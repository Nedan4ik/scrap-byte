import pygame
from screen.components.Widget import Widget


class Label(Widget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        text: str = "",
        size: int = 24,
        color: tuple[int, int, int] | str = (255, 255, 255),
        font_name: str | None = None,
    ):
        super().__init__(x, y, width=0, height=0)
        self.text = text
        self.size = size
        self.color = color
        self.font_name = font_name

    def setText(self, text: str):
        self.text = str(text)

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible or not self.text:
            return

        from game.Game import Game
        game = Game.getInstance()

        if game and game.fontManager:
            text_surface = game.fontManager.renderText(
                self.text,
                size=self.size,
                color=self.color,
                font_name=self.font_name,
            )
            self.width = text_surface.get_width()
            self.height = text_surface.get_height()
            screen.blit(text_surface, (self.x, self.y))
