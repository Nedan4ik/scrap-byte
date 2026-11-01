from __future__ import annotations
import pygame
from screen.Screen import Screen
from levels.Level import Level
from levels.Trash import Trash
from coding.Interpretator import Interpretator
from coding.Renderer import Renderer
from coding.ExecutionResult import ExecutionResult


class GameScreen(Screen):
    def __init__(self, level_index: int = 1, restart: bool = False):
        super().__init__()

        self.level_index = level_index
        saved = None
        if self.game and hasattr(self.game, "saveManager") and self.game.saveManager:
            saved = self.game.saveManager.load_level(self.level_index)

        from levels.Levels import Levels
        self.level = Levels.get(self.level_index)
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().play_ambient()
        self.last_screen_size: tuple[int, int] = (0, 0)
        self._notified_completion: bool = False
        self._level_completed: bool = bool(saved and saved.get("completed", False))

        if saved and "camera" in saved and not restart:
            cam = saved["camera"]
            if isinstance(cam, dict) and "x" in cam and "y" in cam:
                self.level.camera_x = float(cam["x"])
                self.level.camera_y = float(cam["y"])
                self.level.camera_initialized = True

        self.interpretator = Interpretator(context={"game": self.game, "level": self.level, "drone": self.level.drone}, level_index=self.level_index)
        self._pending_restart_timer: float | None = None
        self.code_editor = self.addWidget(
            Renderer(
                x=400,
                y=20,
                width=380,
                height=560,
                interpretator=self.interpretator,
                level=self.level,
                on_run=self._handle_run_started,
                on_layout_change=lambda *args: self.save_progress(),
                on_execution_finish=self._handle_execution_finished,
            )
        )

        if saved and "editor" in saved:
            self.code_editor.load_dict(saved["editor"])

        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.4
        self.max_zoom = 2.5

        self.is_dragging = False
        self.drag_button = 0
        self.drag_start_mouse = (0, 0)
        self.drag_start_cam = (0.0, 0.0)
        self.drag_moved = False

        self.is_panning = False
        self.target_camera_x = 0.0
        self.target_camera_y = 0.0

    def mouseScrolled(self, mouseX: int, mouseY: int, scrollY: int):
        if self.code_editor.visible and self.code_editor.isHovered(mouseX, mouseY):
            super().mouseScrolled(mouseX, mouseY, scrollY)
            return

        if scrollY > 0:
            self.target_zoom = min(self.max_zoom, self.target_zoom * 1.15)
        elif scrollY < 0:
            self.target_zoom = max(self.min_zoom, self.target_zoom / 1.15)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int):
        if self.code_editor.visible and self.code_editor.isHovered(mouseX, mouseY):
            super().mouseClicked(mouseX, mouseY, button)
            return

        if self.code_editor.is_focused:
            self.code_editor.is_focused = False

        if button in (1, 2, 3):
            self.is_dragging = True
            self.is_panning = False
            self.drag_button = button
            self.drag_start_mouse = (mouseX, mouseY)
            self.drag_start_cam = (self.level.camera_x, self.level.camera_y)
            self.drag_moved = False
        super().mouseClicked(mouseX, mouseY, button)

    def mouseReleased(self, mouseX: int, mouseY: int, button: int):
        if self.is_dragging and button == self.drag_button:
            self.is_dragging = False
            if not self.drag_moved:
                w = self.game.window.width if self.game and self.game.window else 800
                h = self.game.window.height if self.game and self.game.window else 600
                self.target_camera_x = self.level.camera_x + (mouseX - w / 2.0) / self.zoom
                self.target_camera_y = self.level.camera_y + (mouseY - h / 2.0) / self.zoom
                self.is_panning = True
        super().mouseReleased(mouseX, mouseY, button)

    def keyPressed(self, keyCode: int):
        if self.code_editor.visible and self.code_editor.is_focused:
            if keyCode == pygame.K_ESCAPE:
                if self.code_editor.info_open:
                    self.code_editor.info_open = False
                else:
                    self.code_editor.is_focused = False
                return
            super().keyPressed(keyCode)
            return

        if keyCode == pygame.K_ESCAPE:
            if self.interpretator:
                self.interpretator.stop()
            self.save_progress()
            from screen.impl.MainMenuScreen import MainMenuScreen
            if self.game:
                self.game.openScreen(MainMenuScreen())
            return

        super().keyPressed(keyCode)

    def load_level(self, index: int):
        from levels.Levels import Levels
        self.level_index = max(1, min(Levels.COUNT, index))
        saved = None
        if self.game and hasattr(self.game, "saveManager") and self.game.saveManager:
            saved = self.game.saveManager.load_level(self.level_index)

        self.level = Levels.get(self.level_index)
        self._level_completed = bool(saved and saved.get("completed", False))
        self.interpretator.set_context(level=self.level, drone=self.level.drone)
        self.interpretator.set_level_restrictions(self.level_index)
        self.code_editor.level = self.level
        if saved and "editor" in saved:
            self.code_editor.load_dict(saved["editor"])
        for tab in self.code_editor.tabs:
            if tab.title == "Информация о уровне":
                tab.set_text(self.level.get_level_info())
        self.level.camera_initialized = False
        self._notified_completion = False
        w = self.game.window.width if self.game and self.game.window else 800
        h = self.game.window.height if self.game and self.game.window else 600
        self.level.center_on_drone(w, h, self.zoom)
        self.save_progress()

    def restart_level(self):
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().stop_drone_move()
        self.load_level(self.level_index)
        self.code_editor.set_status("Уровень перезапущен. Попробуй еще раз!", (180, 190, 210))
        if self.game and hasattr(self.game, "openScreen") and getattr(self.game, "window", None) and getattr(self.game.window, "window", None):
            new_screen = GameScreen(level_index=self.level_index, restart=True)
            new_screen.code_editor.show_console = True
            new_screen.code_editor.console_logs = list(self.code_editor.console_logs)
            new_screen.code_editor.set_status("Уровень перезапущен. Попробуй еще раз!", (180, 190, 210))
            self.game.openScreen(new_screen, use_transition=True)

    def _handle_run_started(self, code: str):
        self._pending_restart_timer = None

    def _handle_execution_finished(self, result: ExecutionResult | None = None):
        all_collected = bool(not self.level.trashItems or all(t.collected for t in self.level.trashItems))
        if not all_collected:
            self.code_editor.console_logs.append(("⚠ [Собран не весь мусор. Перезапуск уровня...]", (245, 160, 60)))
            self.code_editor.set_status("Не весь мусор собран. Перезапуск...", (245, 160, 60))
            self._pending_restart_timer = 0.6
        else:
            self._level_completed = True
            self.save_progress()
            from sound.SoundManager import SoundManager
            SoundManager.get_instance().play_level_win()
            self.code_editor.console_logs.append(("★ [Превосходно! Весь мусор собран!]", (78, 201, 176)))
            self.code_editor.set_status(f"Сектор {self.level_index} зачищен!", (78, 201, 176))

    def save_progress(self):
        if self.game and hasattr(self.game, "saveManager") and self.game.saveManager:
            data = self.level.to_dict()
            all_collected = bool(self.level.trashItems and all(t.collected for t in self.level.trashItems))
            data["completed"] = all_collected or getattr(self, "_level_completed", False)
            if hasattr(self, "code_editor") and self.code_editor:
                data["editor"] = self.code_editor.to_dict()
            self.game.saveManager.save(data)
            self.game.saveManager.save_level(self.level_index, data)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        dt = 0.016
        w, h = screen.get_size()

        if (w, h) != self.last_screen_size:
            self.last_screen_size = (w, h)
            if not getattr(self.code_editor, "custom_layout", False):
                ed_w = min(420, max(330, int(w * 0.44)))
                self.code_editor.setPosition(w - ed_w - 15, 15)
                self.code_editor.setSize(ed_w, h - 30)
            else:
                nx = max(0, min(self.code_editor.x, max(0, w - 80)))
                ny = max(0, min(self.code_editor.y, max(0, h - 80)))
                nw = max(300, min(self.code_editor.width, w))
                nh = max(200, min(self.code_editor.height, h))
                self.code_editor.setPosition(nx, ny)
                self.code_editor.setSize(nw, nh)

        old_zoom = self.zoom
        self.zoom += (self.target_zoom - self.zoom) * min(1.0, 16.0 * dt)
        if abs(self.target_zoom - self.zoom) < 0.001:
            self.zoom = self.target_zoom

        if old_zoom != self.zoom:
            cur_mx, cur_my = pygame.mouse.get_pos()
            world_x = self.level.camera_x + cur_mx / old_zoom
            world_y = self.level.camera_y + cur_my / old_zoom
            self.level.camera_x = world_x - cur_mx / self.zoom
            self.level.camera_y = world_y - cur_my / self.zoom

        if self.is_dragging:
            pressed = pygame.mouse.get_pressed()
            btn_idx = self.drag_button - 1
            if btn_idx < 0 or btn_idx >= len(pressed) or not pressed[btn_idx]:
                self.is_dragging = False
            else:
                cur_mx, cur_my = pygame.mouse.get_pos()
                dx = (cur_mx - self.drag_start_mouse[0]) / self.zoom
                dy = (cur_my - self.drag_start_mouse[1]) / self.zoom
                if abs(cur_mx - self.drag_start_mouse[0]) > 3 or abs(cur_my - self.drag_start_mouse[1]) > 3:
                    self.drag_moved = True
                self.level.camera_x = self.drag_start_cam[0] - dx
                self.level.camera_y = self.drag_start_cam[1] - dy
        elif self.is_panning:
            pan_speed = min(1.0, 12.0 * dt)
            self.level.camera_x += (self.target_camera_x - self.level.camera_x) * pan_speed
            self.level.camera_y += (self.target_camera_y - self.level.camera_y) * pan_speed
            if abs(self.target_camera_x - self.level.camera_x) < 0.5 and abs(self.target_camera_y - self.level.camera_y) < 0.5:
                self.level.camera_x = self.target_camera_x
                self.level.camera_y = self.target_camera_y
                self.is_panning = False

        self.level.update(dt, screen_w=w, screen_h=h, zoom=self.zoom)
        self.level.render(screen, zoom=self.zoom)

        all_collected = bool(self.level.trashItems and all(t.collected for t in self.level.trashItems))
        if all_collected and not self._notified_completion:
            self._notified_completion = True
            nxt = 2 if self.level_index == 1 else 1
            self.code_editor.set_status(f"Сектор {self.level_index} зачищен! Нажмите N для Сектора {nxt}", (78, 201, 176))

        if self._pending_restart_timer is not None:
            self._pending_restart_timer -= dt
            if self._pending_restart_timer <= 0:
                self._pending_restart_timer = None
                self.restart_level()

        super().render(screen, mouseX, mouseY)
