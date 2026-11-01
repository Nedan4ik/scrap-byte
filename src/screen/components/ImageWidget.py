import pygame
from screen.components.Widget import Widget


class ImageWidget(Widget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int | None = None,
        height: int | None = None,
        texture_name: str | None = None,
    ):
        super().__init__(x, y, width or 0, height or 0)
        self.texture_name = texture_name
        self.texture = None

        if texture_name:
            self.loadTexture(texture_name)

    def loadTexture(self, texture_name: str):
        self.texture_name = texture_name
        from game.Game import Game
        game = Game.getInstance()
        if game and game.textureManager:
            self.texture = game.textureManager.getTexture(texture_name)
            if self.texture and (self.width == 0 or self.height == 0):
                self.width = self.texture.width
                self.height = self.texture.height

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible:
            return

        if not self.texture and self.texture_name:
            self.loadTexture(self.texture_name)

        if self.texture:
            self.texture.render(screen, self.x, self.y, self.width, self.height)
