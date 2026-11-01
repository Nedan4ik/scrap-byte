from __future__ import annotations
import sys
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from screen.Screen import Screen

from resources.ResourceLoader import ResourceLoader
from textures.TextureManager import TextureManager
from fonts.FontManager import FontManager
from game.SaveManager import SaveManager
from sound.SoundManager import SoundManager

from game.Window import Window
from game.Keyboard import Keyboard
from game.Mouse import Mouse


class Game:
    _instance = None

    def __init__(self, debug: bool = False, width: int = 800, height: int = 600, maxFps=60):
        if Game._instance is None:
            Game._instance = self
        else:
            raise Exception("Разрешено создавать только один экземпляр игры!")

        self._running = True
        self.debug = debug
        self._currentScreen: Screen | None = None
        self.maxFps = maxFps
        self.transition = None

        if self.debug:
            print("Запускаю игру в режиме отладки.")

        self.saveManager = SaveManager("save.bin")
        self.soundManager = SoundManager.get_instance()
        self.soundManager.play_ambient()
        self.resourceLoader = ResourceLoader(self, lambda resource: self._resourceLoaded(resource))
        self.textureManager = TextureManager()
        self.fontManager = FontManager()

        self.window = Window(self, width, height)
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(300, 30)

        self.mouse.add_button_down_listener(
            lambda btn, x, y: self._currentScreen.mouseClicked(x, y, btn) if self._currentScreen and self.transition is None else None
        )
        self.mouse.add_button_up_listener(
            lambda btn, x, y: self._currentScreen.mouseReleased(x, y, btn) if self._currentScreen and self.transition is None else None
        )
        self.mouse.add_scroll_listener(
            lambda scroll_y, x, y: self._currentScreen.mouseScrolled(x, y, scroll_y) if self._currentScreen and self.transition is None else None
        )
        self.keyboard.add_key_down_listener(
            lambda key: self._currentScreen.keyPressed(key) if self._currentScreen and self.transition is None else None
        )
        self.keyboard.add_key_up_listener(
            lambda key: self._currentScreen.keyReleased(key) if self._currentScreen and self.transition is None else None
        )

        from screen.impl.MainMenuScreen import MainMenuScreen
        self.openScreen(MainMenuScreen(), use_transition=False)

    def run(self):
        while self._running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.close()
                    elif self.transition is None:
                        self.keyboard.handleEvent(event)
                        self.mouse.handleEvent(event)
                        self.window.handleEvent(event)
                    else:
                        self.window.handleEvent(event)

                self.tick()
                self.window.clear()

                if self.transition:
                    self.transition.update(0.016)
                    self.transition.render(self.window.window)
                    if self.transition.finished:
                        self.transition = None
                else:
                    self.render(self.window.window)

                pygame.display.flip()
                self.clock.tick(self.maxFps)
            except Exception as e:
                print(f"Ошибка в главном цикле игры: {e}")
                self.close()

        pygame.quit()
        sys.exit()

    def tick(self):
        pass

    def render(self, matrix=None):
        if self._currentScreen:
            self._currentScreen.render(matrix, self.mouse.mouseX, self.mouse.mouseY)

        if self.debug:
            current_fps = self.getFps()
            fps_text = self.fontManager.renderText(f"FPS: {current_fps}", size=18, color=(0, 0, 0), font_name="Arial")
            self.window.window.blit(fps_text, (10, 10))

    @property
    def currentScreen(self) -> Screen | None:
        return self._currentScreen

    def openScreen(self, screen: Screen, use_transition: bool = True):
        from screen.Screen import Screen

        if screen is not None and not isinstance(screen, Screen):
            raise TypeError(
                f"currentScreen должен быть Screen, а передан {type(screen).__name__}"
            )

        if use_transition and self._currentScreen is not None and self.window and self.window.window:
            from screen.transition.SwirlTransition import SwirlTransition
            self.transition = SwirlTransition(self, self.window.window.copy(), screen)
        else:
            self._currentScreen = screen

    def close(self):
        if self._currentScreen and hasattr(self._currentScreen, "save_progress"):
            self._currentScreen.save_progress()
        if hasattr(self, "soundManager") and self.soundManager:
            self.soundManager.stop_all()
        self._running = False

    def getFps(self) -> int:
        return int(self.clock.get_fps())

    def _resourceLoaded(self, resource):
        if self.debug:
            print(f"Ресурс загружен: {resource.name} ({resource.size} байт, расширение: {resource.extension})")

    @staticmethod
    def getInstance():
        return Game._instance
