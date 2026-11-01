from __future__ import annotations
import pygame
from screen.Screen import Screen
from screen.components.Panorama import Panorama
from screen.components.MenuButton import MenuButton
from screen.components.Panel import Panel
from screen.components.Label import Label
from levels.Levels import Levels


class LevelsScreen(Screen):
    def __init__(self):
        super().__init__()
        self.last_screen_size: tuple[int, int] = (0, 0)
        self.status_message: str = ""
        self.status_timer: int = 0

        self.panorama = Panorama(texture_name="background")

        self.panel = self.addWidget(
            Panel(
                x=0,
                y=0,
                width=420,
                height=450,
                bg_color=(20, 23, 30),
                border_color=(45, 50, 64),
                border_radius=14,
                border_width=2,
            )
        )

        self.title_label = self.addWidget(
            Label(x=0, y=0, text="Уровни", size=32, color=(140, 120, 240), font_name="Consolas")
        )

        self.subtitle_label = self.addWidget(
            Label(x=0, y=0, text="ВЫБОР СЕКТОРА ОПЕРАЦИИ", size=13, color=(110, 120, 140), font_name="Consolas")
        )

        self.level_buttons: list[MenuButton] = []
        btn_style = {
            "width": 360,
            "height": 52,
            "font_size": 17,
        }

        sm = self.game.saveManager if self.game and hasattr(self.game, "saveManager") else None

        for idx in range(1, Levels.COUNT + 1):
            unlocked = sm.is_level_unlocked(idx) if sm else (idx == 1)
            completed = sm.is_level_completed(idx) if sm else False
            title = Levels.get_title(idx)

            if not unlocked:
                btn = self.addWidget(
                    MenuButton(
                        text=f"Сектор {idx}: {title}",
                        icon="",
                        accent_color=(105, 115, 130),
                        is_locked=True,
                        onClick=(lambda i=idx: self.show_locked(i)),
                        **btn_style,
                    )
                )
            else:
                tag = " [ПРОЙДЕН]" if completed else ""
                icon = "✔" if completed else "▶"
                accent = (78, 201, 176) if completed else (86, 156, 214)
                btn = self.addWidget(
                    MenuButton(
                        text=f"Сектор {idx}: {title}{tag}",
                        icon=icon,
                        accent_color=accent,
                        is_locked=False,
                        onClick=(lambda i=idx: self.start_level(i)),
                        **btn_style,
                    )
                )
            self.level_buttons.append(btn)

        self.btn_back = self.addWidget(
            MenuButton(
                icon="icon_back",
                text="Назад в меню",
                accent_color=(244, 75, 86),
                onClick=self.on_back,
                width=360,
                height=48,
                font_size=16,
            )
        )

        self.status_label = self.addWidget(
            Label(x=0, y=0, text="", size=13, color=(240, 180, 80), font_name="Consolas")
        )

    def _update_layout(self, w: int, h: int):
        panel_w = 420
        panel_h = 360 + len(self.level_buttons) * 60
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        self.panel.setPosition(panel_x, panel_y)
        self.panel.setSize(panel_w, panel_h)

        font_title = self.game.fontManager.getFont("Consolas", 32)
        title_w, _ = font_title.size(self.title_label.text)
        self.title_label.setPosition(panel_x + (panel_w - title_w) // 2, panel_y + 24)

        font_sub = self.game.fontManager.getFont("Consolas", 13)
        sub_w, _ = font_sub.size(self.subtitle_label.text)
        self.subtitle_label.setPosition(panel_x + (panel_w - sub_w) // 2, panel_y + 64)

        start_y = panel_y + 100
        spacing = 60
        for i, btn in enumerate(self.level_buttons):
            bx = panel_x + (panel_w - btn.width) // 2
            btn.setPosition(bx, start_y + i * spacing)

        back_y = start_y + len(self.level_buttons) * spacing + 12
        self.btn_back.setPosition(panel_x + (panel_w - self.btn_back.width) // 2, back_y)
        self.status_label.setPosition(panel_x + 24, panel_y + panel_h - 34)

    def show_locked(self, idx: int):
        self.show_status(f"Сектор {idx} заблокирован! Пройдите Сектор {idx - 1}.")

    def show_status(self, text: str):
        self.status_message = text
        self.status_label.setText(text)
        self.status_timer = 200

    def start_level(self, idx: int):
        from screen.impl.GameScreen import GameScreen
        self.game.openScreen(GameScreen(level_index=idx))

    def on_back(self):
        from screen.impl.MainMenuScreen import MainMenuScreen
        self.game.openScreen(MainMenuScreen())

    def keyPressed(self, keyCode: int):
        if keyCode == pygame.K_ESCAPE:
            self.on_back()
            return
        super().keyPressed(keyCode)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        w, h = screen.get_size()

        if (w, h) != self.last_screen_size:
            self.last_screen_size = (w, h)
            self._update_layout(w, h)

        self.panorama.update(0.016)
        self.panorama.render(screen, mouseX, mouseY)

        if self.status_timer > 0:
            self.status_timer -= 1
            if self.status_timer == 0:
                self.status_label.setText("")

        super().render(screen, mouseX, mouseY)