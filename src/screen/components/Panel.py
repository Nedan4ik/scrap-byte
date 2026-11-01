import pygame
from screen.components.Widget import Widget


class Panel(Widget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 200,
        height: int = 200,
        bg_color: tuple[int, int, int] = (40, 40, 45),
        border_color: tuple[int, int, int] | None = (70, 70, 80),
        border_radius: int = 10,
        border_width: int = 2,
    ):
        super().__init__(x, y, width, height)
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_radius = border_radius
        self.border_width = border_width

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        if not self.visible:
            return

        rect = self.getRect()

        if self.bg_color:
            pygame.draw.rect(screen, self.bg_color, rect, border_radius=self.border_radius)

        if self.border_color and self.border_width > 0:
            pygame.draw.rect(
                screen,
                self.border_color,
                rect,
                width=self.border_width,
                border_radius=self.border_radius,
            )
