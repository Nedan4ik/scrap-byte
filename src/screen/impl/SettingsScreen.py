from __future__ import annotations
import pygame
from screen.Screen import Screen
from screen.components.Panorama import Panorama
from screen.components.MenuButton import MenuButton
from screen.components.Panel import Panel
from screen.components.Label import Label


class SettingsScreen(Screen):
    def __init__(self):
        super().__init__()
        from sound.SoundManager import SoundManager
        self.last_screen_size: tuple[int, int] = (0, 0)
        self.sound_enabled: bool = SoundManager.get_instance().is_sound_enabled()
        self.fullscreen_enabled: bool = bool(self.game.window.is_fullscreen) if (self.game and self.game.window) else False

        self.panorama = Panorama(texture_name="background")

        self.panel = self.addWidget(
            Panel(
                x=0,
                y=0,
                width=380,
                height=360,
                bg_color=(20, 23, 30),
                border_color=(45, 50, 64),
                border_radius=14,
                border_width=2,
            )
        )

        self.title_label = self.addWidget(
            Label(x=0, y=0, text="Настройки", size=32, color=(86, 156, 214), font_name="Consolas")
        )

        self.subtitle_label = self.addWidget(
            Label(x=0, y=0, text="ПАРАМЕТРЫ СИСТЕМЫ", size=13, color=(100, 110, 130), font_name="Consolas")
        )

        btn_style = {
            "width": 320,
            "height": 50,
            "font_size": 17,
        }

        self.btn_sound = self.addWidget(
            MenuButton(
                icon="icon_sound",
                text=f"Звуки: {'ВКЛ' if self.sound_enabled else 'ВЫКЛ'}",
                accent_color=(86, 156, 214) if self.sound_enabled else (140, 140, 150),
                onClick=self.toggle_sound,
                **btn_style,
            )
        )

        self.btn_fullscreen = self.addWidget(
            MenuButton(
                icon="icon_fullscreen",
                text=f"Экран: {'Полный' if self.fullscreen_enabled else 'Оконный'}",
                accent_color=(78, 201, 176) if self.fullscreen_enabled else (220, 180, 80),
                onClick=self.toggle_fullscreen,
                **btn_style,
            )
        )

        self.btn_back = self.addWidget(
            MenuButton(
                icon="icon_back",
                text="Назад в меню",
                accent_color=(244, 75, 86),
                onClick=self.on_back,
                **btn_style,
            )
        )

    def _update_layout(self, w: int, h: int):
        panel_w = 380
        panel_h = 360
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        self.panel.setPosition(panel_x, panel_y)
        self.panel.setSize(panel_w, panel_h)

        font_title = self.game.fontManager.getFont("Consolas", 32)
        title_w, _ = font_title.size(self.title_label.text)
        self.title_label.setPosition(panel_x + (panel_w - title_w) // 2, panel_y + 26)

        font_sub = self.game.fontManager.getFont("Consolas", 13)
        sub_w, _ = font_sub.size(self.subtitle_label.text)
        self.subtitle_label.setPosition(panel_x + (panel_w - sub_w) // 2, panel_y + 68)

        btn_w = 320
        btn_x = panel_x + (panel_w - btn_w) // 2
        start_y = panel_y + 112
        spacing = 64

        self.btn_sound.setPosition(btn_x, start_y)
        self.btn_fullscreen.setPosition(btn_x, start_y + spacing)
        self.btn_back.setPosition(btn_x, start_y + spacing * 2)

    def toggle_sound(self):
        from sound.SoundManager import SoundManager
        sm = SoundManager.get_instance()
        self.sound_enabled = sm.toggle_sound()
        self.btn_sound.text = f"Звуки: {'ВКЛ' if self.sound_enabled else 'ВЫКЛ'}"
        self.btn_sound.accent_color = (86, 156, 214) if self.sound_enabled else (140, 140, 150)

    def toggle_fullscreen(self):
        if self.game and self.game.window:
            self.fullscreen_enabled = self.game.window.toggle_fullscreen()
        else:
            self.fullscreen_enabled = not self.fullscreen_enabled
        self.btn_fullscreen.text = f"Экран: {'Полный' if self.fullscreen_enabled else 'Оконный'}"
        self.btn_fullscreen.accent_color = (78, 201, 176) if self.fullscreen_enabled else (220, 180, 80)

    def on_back(self):
        from screen.impl.MainMenuScreen import MainMenuScreen
        self.game.openScreen(MainMenuScreen())

    def keyPressed(self, keyCode: int):
        if keyCode == pygame.K_ESCAPE:
            self.on_back()
        super().keyPressed(keyCode)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        w, h = screen.get_size()

        if (w, h) != self.last_screen_size:
            self.last_screen_size = (w, h)
            self._update_layout(w, h)

        if self.game and self.game.window and self.fullscreen_enabled != self.game.window.is_fullscreen:
            self.fullscreen_enabled = self.game.window.is_fullscreen
            self.btn_fullscreen.text = f"Экран: {'Полный' if self.fullscreen_enabled else 'Оконный'}"
            self.btn_fullscreen.accent_color = (78, 201, 176) if self.fullscreen_enabled else (220, 180, 80)

        self.panorama.update(0.016)
        self.panorama.render(screen, mouseX, mouseY)

        super().render(screen, mouseX, mouseY)
