from __future__ import annotations
import random
from pathlib import Path
import pygame
from textures.SpriteSheet import SpriteSheet, AnimatedSprite


class Trash:
    TYPES = {
        "chip": {"color": (46, 204, 113), "border": (180, 255, 200), "val": 15, "name": "Микросхема"},
        "board": {"color": (52, 152, 219), "border": (180, 220, 255), "val": 35, "name": "Плата"},
        "core": {"color": (241, 196, 15), "border": (255, 240, 180), "val": 75, "name": "Ядро процессора"},
        "valuable": {"color": (46, 204, 113), "border": (180, 255, 200), "val": 25, "name": "Ценный лом"},
        "hazardous": {"color": (231, 76, 60), "border": (255, 180, 180), "val": 50, "name": "Токсичный лом"},
        "bin": {"color": (52, 73, 94), "border": (120, 180, 200), "val": 0, "name": "Утилизатор"},
        "trash_bin": {"color": (52, 73, 94), "border": (120, 180, 200), "val": 0, "name": "Утилизатор"},
        "basket": {"color": (41, 128, 185), "border": (100, 200, 255), "val": 0, "name": "Корзина для лома"},
        "trash_basket": {"color": (41, 128, 185), "border": (100, 200, 255), "val": 0, "name": "Корзина для лома"},
    }

    VALUABLE_VISUALS = ["scrap_chip", "scrap_board", "scrap_core", "scrap_crystal"]
    HAZARDOUS_VISUALS = ["hazard_barrel", "hazard_battery", "hazard_plasma"]
    BIN_VISUALS = ["trash_bin", "trash_basket"]
    BASKET_VISUALS = ["trash_basket", "basket"]
    ALL_VISUALS = VALUABLE_VISUALS + HAZARDOUS_VISUALS + ["trash_bin", "trash_basket", "basket"]

    _spritesheet: SpriteSheet | None = None
    _spritesheet_attempted: bool = False

    @classmethod
    def get_spritesheet(cls) -> SpriteSheet | None:
        if not cls._spritesheet_attempted:
            cls._spritesheet_attempted = True
            candidates = [
                Path("assets/trash/trash.xml"),
                Path(__file__).resolve().parent.parent.parent / "assets" / "trash" / "trash.xml",
            ]
            for p in candidates:
                if p.exists():
                    try:
                        cls._spritesheet = SpriteSheet(p)
                        break
                    except Exception as e:
                        pass
        return cls._spritesheet

    def __init__(
        self,
        x: float,
        y: float,
        trash_type: str = "chip",
        collected: bool = False,
        visual_variant: str | None = None,
    ):
        self.x = x
        self.y = y

        if trash_type in self.TYPES:
            self.trash_type = trash_type
        elif trash_type in self.ALL_VISUALS:
            if trash_type.startswith("hazard_"):
                self.trash_type = "hazardous"
            elif trash_type in ("trash_bin", "bin"):
                self.trash_type = "trash_bin"
            elif trash_type in ("trash_basket", "basket"):
                self.trash_type = "trash_basket"
            else:
                self.trash_type = "chip"
        else:
            self.trash_type = "chip"

        self.collected = collected

        info = self.TYPES.get(self.trash_type, self.TYPES["chip"])
        self.color = info["color"]
        self.border_color = info["border"]
        self.value = info["val"]
        self.name = info["name"]
        self.size = 14

        # Randomize visual variant if not explicitly supplied
        if visual_variant and visual_variant in self.ALL_VISUALS:
            self.visual_variant = visual_variant
        elif self.trash_type in ("chip", "board", "core", "valuable"):
            self.visual_variant = random.choice(self.VALUABLE_VISUALS)
        elif self.trash_type == "hazardous":
            self.visual_variant = random.choice(self.HAZARDOUS_VISUALS)
        elif self.trash_type in ("bin", "trash_bin"):
            self.visual_variant = "trash_bin"
        elif self.trash_type in ("basket", "trash_basket"):
            self.visual_variant = "trash_basket"
        elif self.trash_type in self.ALL_VISUALS:
            self.visual_variant = self.trash_type
        else:
            self.visual_variant = random.choice(self.VALUABLE_VISUALS)

        # Setup animated sprite
        self.spritesheet = self.get_spritesheet()
        self.sprite: AnimatedSprite | None = None
        if self.spritesheet and self.visual_variant in self.spritesheet.animations:
            self.sprite = AnimatedSprite(self.spritesheet, default_anim=self.visual_variant, fps=6.0)
            frames = self.spritesheet.get_animation(self.visual_variant)
            if frames:
                # Randomize initial frame index to desynchronize animations
                self.sprite.frame_index = random.uniform(0.0, float(len(frames)))

    def update(self, dt: float = 0.016):
        if self.sprite:
            self.sprite.update(dt)

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
        margin = int(48 * zoom)
        if draw_x < -margin or draw_x > sw + margin or draw_y < -margin or draw_y > sh + margin:
            return

        # Dynamic floor contact shadow rendered on the platform beneath the trash item
        shadow_w = max(6, int(34 * zoom))
        shadow_h = max(3, int(12 * zoom))
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        # Soft outer shadow
        pygame.draw.ellipse(shadow_surf, (5, 7, 12, 110), (0, 0, shadow_w, shadow_h))
        # Dense inner core shadow
        core_w = max(2, int(shadow_w * 0.65))
        core_h = max(2, int(shadow_h * 0.65))
        pygame.draw.ellipse(
            shadow_surf,
            (2, 3, 6, 80),
            ((shadow_w - core_w) // 2, (shadow_h - core_h) // 2, core_w, core_h),
        )
        shadow_y = draw_y + int(14 * zoom)
        screen.blit(shadow_surf, (draw_x - shadow_w // 2, shadow_y - shadow_h // 2))

        rendered = False
        if self.sprite and self.sprite.get_current_surface() is not None:
            # 64x64 sprite scaled at 0.75 * zoom fits nicely in the 56px tile (48px size)
            scale = 0.75 * zoom
            self.sprite.render(screen, draw_x, draw_y, scale=scale)
            rendered = True

        if not rendered:
            size = max(4, int(self.size * zoom))
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
            elif self.trash_type in ("bin", "trash_bin", "basket", "trash_basket"):
                pygame.draw.rect(screen, (80, 200, 240), (rect.x + 2, rect.y + 2, rect.w - 4, rect.h - 4), width=1)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "type": self.trash_type,
            "collected": self.collected,
            "visual_variant": self.visual_variant,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Trash:
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            trash_type=data.get("type", "chip"),
            collected=data.get("collected", False),
            visual_variant=data.get("visual_variant"),
        )
