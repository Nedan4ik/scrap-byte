from __future__ import annotations
import time
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
            editor_data = {k: v for k, v in saved["editor"].items() if k not in ("tabs", "active_tab")}
            self.code_editor.load_dict(editor_data)

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

        self.time: float = 0.0
        self._last_time_stamp: float | None = None
        self._hud_font: pygame.font.Font | None = None
        self._hud_small_font: pygame.font.Font | None = None
        self._hud_title_font: pygame.font.Font | None = None

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

        if 16 <= mouseX <= 310 and 16 <= mouseY <= 110:
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
        mods = pygame.key.get_mods()
        ctrl_pressed = bool(mods & pygame.KMOD_CTRL)

        if self.code_editor.visible and self.code_editor.is_focused:
            if ctrl_pressed and keyCode == pygame.K_r:
                self.restart_level()
                return

            if keyCode == pygame.K_ESCAPE:
                if self.code_editor.info_open:
                    self.code_editor.info_open = False
                else:
                    self.code_editor.is_focused = False
                return
            super().keyPressed(keyCode)
            return

        if keyCode == pygame.K_r:
            self.restart_level()
            return

        if keyCode == pygame.K_n:
            from levels.Levels import Levels
            nxt = self.level_index + 1 if self.level_index < Levels.COUNT else 1
            if self.interpretator:
                self.interpretator.stop()
            self.save_progress()
            self.load_level(nxt)
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
        self.time = 0.0
        self._last_time_stamp = None
        self._pending_restart_timer = None
        saved = None
        if self.game and hasattr(self.game, "saveManager") and self.game.saveManager:
            saved = self.game.saveManager.load_level(self.level_index)

        self.level = Levels.get(self.level_index)
        self._level_completed = bool(saved and saved.get("completed", False))
        self.interpretator.set_context(level=self.level, drone=self.level.drone)
        self.interpretator.set_level_restrictions(self.level_index)
        self.code_editor.level = self.level
        if saved and "editor" in saved:
            editor_data = {k: v for k, v in saved["editor"].items() if k not in ("tabs", "active_tab")}
            self.code_editor.load_dict(editor_data)
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
        self._pending_restart_timer = None
        self.time = 0.0
        self._last_time_stamp = None
        if self.interpretator:
            self.interpretator.stop()
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().stop_drone_move()
        self.load_level(self.level_index)
        self.code_editor.set_status("Уровень перезапущен. Попробуй еще раз!", (180, 190, 210))
        if self.game and hasattr(self.game, "openScreen") and getattr(self.game, "window", None) and getattr(self.game.window, "window", None):
            new_screen = GameScreen(level_index=self.level_index, restart=True)
            new_screen.code_editor.show_console = True
            new_screen.code_editor.console_logs = list(self.code_editor.console_logs)
            if hasattr(self, "code_editor") and getattr(self.code_editor, "tabs", None):
                from coding.Renderer import CodeTab
                new_screen.code_editor.tabs = [CodeTab(title=t.title, content=t.getText()) for t in self.code_editor.tabs]
                new_screen.code_editor.active_tab_index = min(self.code_editor.active_tab_index, len(new_screen.code_editor.tabs) - 1)
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
                data["editor"] = {
                    "x": int(self.code_editor.x),
                    "y": int(self.code_editor.y),
                    "w": int(self.code_editor.width),
                    "h": int(self.code_editor.height),
                    "custom_layout": getattr(self.code_editor, "custom_layout", False),
                }
            self.game.saveManager.save(data)
            self.game.saveManager.save_level(self.level_index, data)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        now = time.time()
        if self._last_time_stamp is None:
            dt = 0.016
        else:
            dt = min(0.1, max(0.001, now - self._last_time_stamp))
        self._last_time_stamp = now
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

        if not self.level.camera_initialized:
            arena_w = self.code_editor.x if (self.code_editor and self.code_editor.visible) else w
            fit_zoom = max(self.min_zoom, min(0.85, min((arena_w - 70) / max(1, self.level.cols * self.level.tile_size), (h - 70) / max(1, self.level.rows * self.level.tile_size))))
            self.zoom = fit_zoom
            self.target_zoom = fit_zoom
            self.level.camera_x = -(arena_w / 2.0) / self.zoom
            self.level.camera_y = -(h / 2.0) / self.zoom
            self.level.camera_initialized = True

        self.level.update(dt, screen_w=w, screen_h=h, zoom=self.zoom)
        self.level.render(screen, zoom=self.zoom)

        all_collected = bool(self.level.trashItems and all(t.collected for t in self.level.trashItems))
        if all_collected and not self._notified_completion:
            self._notified_completion = True
            from levels.Levels import Levels
            nxt = self.level_index + 1 if self.level_index < Levels.COUNT else 1
            self.code_editor.set_status(f"Сектор {self.level_index} зачищен! Нажмите N для Сектора {nxt}", (78, 201, 176))

        if self._pending_restart_timer is not None:
            self._pending_restart_timer -= dt
            if self._pending_restart_timer <= 0:
                self._pending_restart_timer = None
                self.restart_level()

        is_timed = (
            self.level.max_time != 'inf'
            and self.level.max_time is not None
            and isinstance(self.level.max_time, (int, float))
            and self.level.max_time > 0
            and self.level.max_time != float('inf')
        )

        if is_timed and not self._level_completed and self._pending_restart_timer is None:
            self.time += dt
            if self.time >= self.level.max_time:
                self.time = float(self.level.max_time)
                if self.interpretator:
                    self.interpretator.stop()
                from sound.SoundManager import SoundManager
                sm = SoundManager.get_instance()
                if sm:
                    sm.stop_drone_move()
                    sm.play_obstacle_hit()
                self.code_editor.show_console = True
                self.code_editor.console_logs.append(("⏱ [Время вышло! Уровень перезапускается...]", (244, 75, 86)))
                self.code_editor.set_status("Время вышло! Перезапуск...", (244, 75, 86))
                self._pending_restart_timer = 1.2

        if is_timed and not self._level_completed:
            rem = max(0.0, float(self.level.max_time) - self.time)
            if rem <= 45.0:
                self._render_danger_overlay(screen, rem, float(self.level.max_time))

        self._render_hud(screen, is_timed)
        super().render(screen, mouseX, mouseY)

    def _render_danger_overlay(self, screen: pygame.Surface, rem: float, max_t: float):
        import math
        w, h = screen.get_size()
        ed_x = self.code_editor.x if (self.code_editor and self.code_editor.visible) else w
        arena_w = max(200, ed_x)

        danger_ratio = max(0.0, min(1.0, (45.0 - rem) / 45.0))
        pulse_freq = 4.0 + 5.0 * danger_ratio
        pulse = (math.sin(self.time * pulse_freq) + 1.0) * 0.5

        # 1. Soft red tint across the playable arena
        overlay_alpha = int(14 * danger_ratio + 36 * danger_ratio * pulse)
        if overlay_alpha > 0:
            red_surf = pygame.Surface((arena_w, h), pygame.SRCALPHA)
            red_surf.fill((220, 20, 30, overlay_alpha))
            screen.blit(red_surf, (0, 0))

        # 2. Glowing perimeter borders on arena edges
        border_thickness = int(6 + 14 * danger_ratio)
        border_alpha = int(40 * danger_ratio + 70 * danger_ratio * pulse)
        if border_alpha > 0:
            edge_surf = pygame.Surface((arena_w, h), pygame.SRCALPHA)
            edge_col = (255, 30, 40, border_alpha)
            pygame.draw.rect(edge_surf, edge_col, (0, 0, arena_w, border_thickness))
            pygame.draw.rect(edge_surf, edge_col, (0, h - border_thickness, arena_w, border_thickness))
            pygame.draw.rect(edge_surf, edge_col, (0, 0, border_thickness, h))
            pygame.draw.rect(edge_surf, edge_col, (arena_w - border_thickness, 0, border_thickness, h))
            screen.blit(edge_surf, (0, 0))

        # 3. Flashing warning banner (placed safely below HUD at y=114)
        if rem <= 30.0:
            font = self._hud_title_font or pygame.font.SysFont("Consolas", 13, bold=True)
            warn_color = (255, 75, 75) if pulse > 0.4 else (205, 35, 35)
            warn_text = f"⚠ ТРЕВОГА: ВРЕМЯ НА ИСХОДЕ ({int(rem)}с) ⚠"
            warn_surf = font.render(warn_text, True, warn_color)
            warn_x = (arena_w - warn_surf.get_width()) // 2
            warn_y = 114
            pill_w = warn_surf.get_width() + 20
            pill_h = warn_surf.get_height() + 8
            pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pill_surf.fill((22, 6, 8, int(190 + 65 * pulse)))
            screen.blit(pill_surf, (warn_x - 10, warn_y - 4))
            pygame.draw.rect(screen, (220, 35, 45), (warn_x - 10, warn_y - 4, pill_w, pill_h), width=1, border_radius=6)
            screen.blit(warn_surf, (warn_x, warn_y))

    def _render_hud(self, screen: pygame.Surface, is_timed: bool):
        if self._hud_font is None:
            self._hud_font = pygame.font.SysFont("Consolas", 20, bold=True)
            self._hud_small_font = pygame.font.SysFont("Consolas", 11)
            self._hud_title_font = pygame.font.SysFont("Consolas", 13, bold=True)
            self._hud_hint_font = pygame.font.SysFont("Consolas", 10)

        hud_x, hud_y = 18, 16
        hud_w, hud_h = 290, 92

        # Sleek glassmorphism card
        hud_surf = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud_surf.fill((14, 18, 26, 235))
        screen.blit(hud_surf, (hud_x, hud_y))

        # Thin tech border
        border_col = (48, 58, 78)
        pygame.draw.rect(screen, border_col, (hud_x, hud_y, hud_w, hud_h), width=1, border_radius=10)

        # Header: Sector name and trash progress
        from levels.Levels import Levels
        sec_title = f"СЕКТОР {self.level_index} // {Levels.get_title(self.level_index).upper()}"
        title_surf = self._hud_title_font.render(sec_title, True, (150, 175, 230))
        screen.blit(title_surf, (hud_x + 12, hud_y + 9))

        collected = sum(1 for t in self.level.trashItems if t.collected)
        total = len(self.level.trashItems)
        trash_col = (78, 220, 180) if (total > 0 and collected == total) else (180, 195, 215)
        trash_surf = self._hud_small_font.render(f"ЛОМ: {collected}/{total}", True, trash_col)
        screen.blit(trash_surf, (hud_x + hud_w - trash_surf.get_width() - 12, hud_y + 10))

        if is_timed:
            max_t = float(self.level.max_time)
            rem = max(0.0, max_t - self.time)
            mins = int(rem) // 60
            secs = int(rem) % 60

            if rem > 60.0:
                timer_col = (78, 220, 180)
            elif rem > 30.0:
                timer_col = (255, 185, 50)
            else:
                is_flash = int(self.time * 5) % 2 == 0
                timer_col = (255, 80, 90) if is_flash else (220, 45, 55)

            if self._level_completed:
                timer_text = "★ СЕКТОР ЗАЧИЩЕН"
                timer_col = (78, 220, 180)
                time_surf = self._hud_font.render(timer_text, True, timer_col)
                screen.blit(time_surf, (hud_x + 12, hud_y + 32))
            else:
                if rem <= 10.0:
                    tenths = int((rem - int(rem)) * 10)
                    timer_text = f"⏱ {mins:02d}:{secs:02d}.{tenths}"
                else:
                    timer_text = f"⏱ {mins:02d}:{secs:02d}"

                time_surf = self._hud_font.render(timer_text, True, timer_col)
                screen.blit(time_surf, (hud_x + 12, hud_y + 30))

                limit_str = f"/ {int(max_t)//60:02d}:{int(max_t)%60:02d}"
                limit_surf = self._hud_small_font.render(limit_str, True, (120, 135, 155))
                screen.blit(limit_surf, (hud_x + 12 + time_surf.get_width() + 6, hud_y + 36))

            # Progress bar
            bar_x = hud_x + 12
            bar_y = hud_y + 60
            bar_w = hud_w - 24
            bar_h = 6
            pygame.draw.rect(screen, (24, 30, 44), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            fill_ratio = max(0.0, min(1.0, rem / max_t))
            fill_w = int(bar_w * fill_ratio)
            if fill_w > 0:
                pygame.draw.rect(screen, timer_col, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

            # Shortcut hints
            hint_surf = self._hud_hint_font.render("R - рестарт  |  Ctrl+Z - отмена  |  ▶ - запуск", True, (95, 110, 130))
            screen.blit(hint_surf, (hud_x + 12, hud_y + 72))
        else:
            mins = int(self.time) // 60
            secs = int(self.time) % 60
            if self._level_completed:
                timer_text = "★ СЕКТОР ЗАЧИЩЕН"
                timer_col = (78, 220, 180)
            else:
                timer_text = f"⏱ {mins:02d}:{secs:02d}"
                timer_col = (180, 195, 220)
            time_surf = self._hud_font.render(timer_text, True, timer_col)
            screen.blit(time_surf, (hud_x + 12, hud_y + 30))

            no_limit_surf = self._hud_small_font.render("[ БЕЗ ЛИМИТА ]", True, (100, 140, 185))
            screen.blit(no_limit_surf, (hud_x + 12 + time_surf.get_width() + 8, hud_y + 36))

            hint_surf = self._hud_hint_font.render("R - рестарт  |  Ctrl+Z - отмена  |  ▶ - запуск", True, (95, 110, 130))
            screen.blit(hint_surf, (hud_x + 12, hud_y + 64))
