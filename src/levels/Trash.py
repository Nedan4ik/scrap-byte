from __future__ import annotations
import pygame


class Trash:
    TYPES = {
        "chip": {"color": (46, 204, 113), "border": (180, 255, 200), "val": 15, "name": "Микросхема"},
        "board": {"color": (52, 152, 219), "border": (180, 220, 255), "val": 35, "name": "Плата"},
        "core": {"color": (241, 196, 15), "border": (255, 240, 180), "val": 75, "name": "Ядро процессора"},
        "hazardous": {"color": (231, 76, 60), "border": (255, 180, 180), "val": 50, "name": "Токсичный лом"},
    }

    def __init__(
        self,
        x: float,
        y: float,
        trash_type: str = "chip",
        collected: bool = False,
    ):
        self.x = x
        self.y = y
        self.trash_type = trash_type if trash_type in self.TYPES else "chip"
        self.collected = collected

        info = self.TYPES[self.trash_type]
        self.color = info["color"]
        self.border_color = info["border"]
        self.value = info["val"]
        self.name = info["name"]
        self.size = 14

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size,
            self.size,
        )

    def render(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0):
        if self.collected:
            return

        draw_x = int((self.x - offset_x) * zoom)
        draw_y = int((self.y - offset_y) * zoom)

        sw, sh = screen.get_size()
        size = max(4, int(self.size * zoom))
        if draw_x < -size or draw_x > sw + size or draw_y < -size or draw_y > sh + size:
            return

        rect = pygame.Rect(draw_x - size // 2, draw_y - size // 2, size, size)
        pygame.draw.rect(screen, (15, 18, 24), (rect.x - 2, rect.y - 2, rect.w + 4, rect.h + 4), border_radius=max(1, int(4 * zoom)))
        pygame.draw.rect(screen, self.color, rect, border_radius=max(1, int(3 * zoom)))
        pygame.draw.rect(screen, self.border_color, rect, width=1, border_radius=max(1, int(3 * zoom)))

        dot = max(2, int(4 * zoom))
        if self.trash_type == "chip":
            pygame.draw.rect(screen, (255, 255, 255), (draw_x - dot // 2, draw_y - dot // 2, dot, dot))
        elif self.trash_type == "board":
            pygame.draw.line(screen, (240, 240, 100), (rect.x + 3, draw_y), (rect.right - 3, draw_y), 1)
        elif self.trash_type == "core":
            pygame.draw.circle(screen, (255, 255, 255), (draw_x, draw_y), max(1, int(3 * zoom)))
        elif self.trash_type == "hazardous":
            pygame.draw.line(screen, (255, 255, 255), (rect.x + 2, rect.y + 2), (rect.right - 2, rect.bottom - 2), max(1, int(2 * zoom)))

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "type": self.trash_type,
            "collected": self.collected,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Trash:
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            trash_type=data.get("type", "chip"),
            collected=data.get("collected", False),
        )
