import pygame
from screen.components.Widget import Widget

class Button(Widget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 160,
        height: int = 45,
        text: str = "Кнопка",
        onClick=None,
        font_size: int = 20,
        font_name: str | None = None,
        bg_color: tuple[int, int, int] = (60, 60, 70),
        hover_color: tuple[int, int, int] = (90, 90, 110),
        text_color: tuple[int, int, int] = (255, 255, 255),
        border_radius: int = 8,
    ):
        super().__init__(x, y, width, height)
        self.text = text
        self.onClick = onClick
        self.font_size = font_size
        self.font_name = font_name
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible:
            return

        hovered = self.isHovered(mouseX, mouseY) and self.enabled
        color = self.hover_color if hovered else self.bg_color

        rect = self.getRect()
        pygame.draw.rect(screen, color, rect, border_radius=self.border_radius)

        border_color = (120, 120, 140) if hovered else (80, 80, 90)
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=self.border_radius)

        if self.text:
            from game.Game import Game
            game = Game.getInstance()
            if game and game.fontManager:
                text_surface = game.fontManager.renderText(
                    self.text,
                    size=self.font_size,
                    color=self.text_color,
                    font_name=self.font_name,
                )
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)

    def mouseClicked(self, mouseX: int, mouseY: int, button: int) -> bool:
        if not self.visible or not self.enabled:
            return False

        if button == 1 and self.isHovered(mouseX, mouseY):
            if self.onClick:
                self.onClick()
            return True

        return False
