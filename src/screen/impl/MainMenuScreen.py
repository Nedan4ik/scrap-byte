from __future__ import annotations
import pygame
from screen.Screen import Screen
from screen.components.Panorama import Panorama
from screen.components.MenuButton import MenuButton
from screen.components.Panel import Panel
from screen.components.Label import Label


class MainMenuScreen(Screen):
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
                width=360,
                height=490,
                bg_color=(20, 23, 30),
                border_color=(45, 50, 64),
                border_radius=14,
                border_width=2,
            )
        )

        self.title_label = self.addWidget(
            Label(x=0, y=0, text="ScrapByte", size=34, color=(78, 201, 176), font_name="Consolas")
        )

        self.subtitle_label = self.addWidget(
            Label(x=0, y=0, text="DRONE OPS // v0.1.0", size=13, color=(100, 110, 130), font_name="Consolas")
        )

        btn_style = {
            "width": 300,
            "height": 52,
            "font_size": 18,
        }

        self.btn_play = self.addWidget(
            MenuButton(
                icon="icon_play",
                text="Играть",
                accent_color=(78, 201, 176),
                onClick=self.on_play,
                **btn_style,
            )
        )

        self.btn_levels = self.addWidget(
            MenuButton(
                icon="icon_levels",
                text="Уровни",
                accent_color=(140, 120, 240),
                onClick=self.on_levels,
                **btn_style,
            )
        )

        self.btn_settings = self.addWidget(
            MenuButton(
                icon="icon_settings",
                text="Настройки",
                accent_color=(86, 156, 214),
                onClick=self.on_settings,
                **btn_style,
            )
        )

        self.btn_faq = self.addWidget(
            MenuButton(
                icon="icon_faq",
                text="ЧаВо",
                accent_color=(220, 180, 80),
                onClick=self.on_faq,
                **btn_style,
            )
        )

        self.btn_exit = self.addWidget(
            MenuButton(
                icon="icon_exit",
                text="Выход",
                accent_color=(244, 75, 86),
                onClick=self.on_exit,
                **btn_style,
            )
        )

        self.status_label = self.addWidget(
            Label(x=0, y=0, text="", size=14, color=(220, 220, 130), font_name="Consolas")
        )

    def _update_layout(self, w: int, h: int):
        panel_w = 360
        panel_h = 490
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        self.panel.setPosition(panel_x, panel_y)
        self.panel.setSize(panel_w, panel_h)

        font_title = self.game.fontManager.getFont("Consolas", 34)
        title_w, _ = font_title.size(self.title_label.text)
        self.title_label.setPosition(panel_x + (panel_w - title_w) // 2, panel_y + 24)

        font_sub = self.game.fontManager.getFont("Consolas", 13)
        sub_w, _ = font_sub.size(self.subtitle_label.text)
        self.subtitle_label.setPosition(panel_x + (panel_w - sub_w) // 2, panel_y + 64)

        btn_w = 300
        btn_x = panel_x + (panel_w - btn_w) // 2
        start_y = panel_y + 102
        spacing = 58

        self.btn_play.setPosition(btn_x, start_y)
        self.btn_levels.setPosition(btn_x, start_y + spacing)
        self.btn_settings.setPosition(btn_x, start_y + spacing * 2)
        self.btn_faq.setPosition(btn_x, start_y + spacing * 3)
        self.btn_exit.setPosition(btn_x, start_y + spacing * 4)

        self.status_label.setPosition(panel_x + 30, panel_y + panel_h - 34)

    def show_status(self, text: str):
        self.status_message = text
        self.status_label.setText(text)
        self.status_timer = 180

    def on_play(self):
        from screen.impl.GameScreen import GameScreen
        from levels.Levels import Levels
        target_idx = 1
        if self.game and hasattr(self.game, "saveManager") and self.game.saveManager:
            for idx in range(1, Levels.COUNT + 1):
                if not self.game.saveManager.is_level_completed(idx):
                    target_idx = idx
                    break
            else:
                target_idx = Levels.COUNT
        self.game.openScreen(GameScreen(level_index=target_idx))

    def on_levels(self):
        from screen.impl.LevelsScreen import LevelsScreen
        self.game.openScreen(LevelsScreen())

    def on_settings(self):
        from screen.impl.SettingsScreen import SettingsScreen
        self.game.openScreen(SettingsScreen())

    def on_faq(self):
        from screen.impl.FaqScreen import FaqScreen
        self.game.openScreen(FaqScreen())

    def on_about(self):
        self.on_faq()

    def on_exit(self):
        self.game.close()

    def keyPressed(self, keyCode: int):
        if keyCode == pygame.K_ESCAPE:
            self.on_exit()
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
