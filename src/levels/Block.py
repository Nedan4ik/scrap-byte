from __future__ import annotations
import pygame


class Block:
    def __init__(
        self,
        isAir: bool = False,
        color: tuple[int, int, int] = (44, 52, 66),
        is_obstacle: bool = False,
    ):
        self.isAir = isAir
        self.color = color
        self.is_obstacle = is_obstacle
        self.bevel_color = (int(color[0] * 0.52), int(color[1] * 0.52), int(color[2] * 0.52))
        self.shadow_color = (int(color[0] * 0.3), int(color[1] * 0.3), int(color[2] * 0.3))
        self.border_color = (int(color[0] * 0.72), int(color[1] * 0.72), int(color[2] * 0.72))
        self.hi_color = (min(255, color[0] + 28), min(255, color[1] + 28), min(255, color[2] + 28))
        self.inner_color = (int(color[0] * 0.88), int(color[1] * 0.88), int(color[2] * 0.88))

    def render(self, screen: pygame.Surface, draw_x: int, draw_y: int, size: int):
        if self.isAir:
            return

        if self.is_obstacle:
            obs_depth = max(2, int(round(size * 8.0 / 56.0)))
            obs_top_h = max(2, size - obs_depth)
            base_col = (48, 38, 42)
            top_col = (72, 54, 58)
            pygame.draw.rect(screen, top_col, (draw_x, draw_y, size, obs_top_h))
            pygame.draw.rect(screen, base_col, (draw_x, draw_y + obs_top_h, size, obs_depth))
            pygame.draw.rect(screen, (190, 85, 45), (draw_x, draw_y, size, obs_top_h), width=2)
            pygame.draw.line(screen, (225, 140, 50), (draw_x + 3, draw_y + 3), (draw_x + size - 4, draw_y + obs_top_h - 4), 2)
            pygame.draw.line(screen, (225, 140, 50), (draw_x + size - 4, draw_y + 3), (draw_x + 3, draw_y + obs_top_h - 4), 2)
            pygame.draw.rect(screen, (245, 185, 65), (draw_x + size // 2 - 3, draw_y + obs_top_h // 2 - 3, 6, 6))
            return

        depth = max(1, int(round(size * 5.0 / 56.0)))
        top_h = max(1, size - depth)

        pygame.draw.rect(screen, self.color, (draw_x, draw_y, size, top_h))
        pygame.draw.rect(screen, self.bevel_color, (draw_x, draw_y + top_h, size, depth))
        pygame.draw.line(screen, self.shadow_color, (draw_x, draw_y + size - 1), (draw_x + size - 1, draw_y + size - 1))
        pygame.draw.rect(screen, self.border_color, (draw_x, draw_y, size, top_h), width=1)
        pygame.draw.line(screen, self.hi_color, (draw_x + 1, draw_y + 1), (draw_x + size - 2, draw_y + 1))
        pygame.draw.line(screen, self.hi_color, (draw_x + 1, draw_y + 1), (draw_x + 1, draw_y + top_h - 2))

        inset = depth
        if size > inset * 2 and top_h > inset * 2:
            pygame.draw.rect(
                screen,
                self.inner_color,
                (draw_x + inset, draw_y + inset, size - inset * 2, top_h - inset * 2),
                width=1,
            )

    def to_dict(self) -> dict:
        return {
            "isAir": self.isAir,
            "color": list(self.color),
            "is_obstacle": self.is_obstacle,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Block:
        return cls(
            isAir=bool(data.get("isAir", False)),
            color=tuple(data.get("color", (44, 52, 66))),
            is_obstacle=bool(data.get("is_obstacle", False)),
        )
