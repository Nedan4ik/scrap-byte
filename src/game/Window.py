from __future__ import annotations
import pygame


class Window:
    def __init__(self, game, width: int, height: int):
        self.game = game
        self.width = width
        self.height = height
        self.is_fullscreen: bool = False
        self.saved_size: tuple[int, int] = (width, height)

        self.window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.updateTitle("Scrap Byte")

    def updateTitle(self, title: str):
        if self.window:
            pygame.display.set_caption(title)

    def toggle_fullscreen(self) -> bool:
        self.is_fullscreen = not self.is_fullscreen
        try:
            from pygame._sdl2 import video
            win = video.Window.from_display_module()
            if self.is_fullscreen:
                self.saved_size = (self.width, self.height)
                win.set_fullscreen(desktop=True)
            else:
                win.set_windowed()
            self.window = pygame.display.get_surface()
            self.width, self.height = self.window.get_size()
        except Exception:
            if self.is_fullscreen:
                self.saved_size = (self.width, self.height)
                info = pygame.display.Info()
                self.width, self.height = info.current_w, info.current_h
                self.window = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME)
            else:
                self.width, self.height = self.saved_size
                self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        return self.is_fullscreen

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11 or (event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)):
                self.toggle_fullscreen()
        elif event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.size
            if not self.is_fullscreen:
                self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            else:
                self.window = pygame.display.get_surface()

    def clear(self, color=(0, 0, 0)):
        if self.window:
            self.window.fill(color)
