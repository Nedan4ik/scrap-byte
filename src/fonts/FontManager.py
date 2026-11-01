from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.Game import Game


class FontManager:
    def __init__(self):
        self.fonts: dict[tuple[str, int], pygame.font.Font] = {}

        if not pygame.font.get_init():
            pygame.font.init()

    def getFont(self, name: str | None, size: int) -> pygame.font.Font:
        cache_key = (name or "__default__", size)
        if cache_key in self.fonts:
            return self.fonts[cache_key]

        font = self._loadFont(name, size)
        self.fonts[cache_key] = font
        return font

    get_font = getFont

    def _loadFont(self, name: str | None, size: int) -> pygame.font.Font:
        from game.Game import Game
        game = Game.getInstance()

        if not name:
            return pygame.font.Font(None, size)

        if game and game.resourceLoader:
            resource = game.resourceLoader.getResourceByName(name)
            if resource:
                try:
                    return pygame.font.Font(resource.to_stream(), size)
                except Exception as e:
                    if game.debug:
                        print(f"[FontManager] Ошибка при распаковке шрифта '{name}' из ресурсов: {e}")

        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            pass

        if game and game.debug:
            print(f"[FontManager] Шрифт '{name}' не найден. Использован шрифт по умолчанию.")

        return pygame.font.Font(None, size)

    def renderText(
        self,
        text: str,
        size: int = 24,
        color: tuple[int, int, int] | str = (255, 255, 255),
        font_name: str | None = None,
        antialias: bool = True,
    ) -> pygame.Surface:
        font = self.getFont(font_name, size)
        return font.render(str(text), antialias, color)

    render_text = renderText
