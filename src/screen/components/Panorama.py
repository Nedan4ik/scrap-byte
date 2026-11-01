from __future__ import annotations
import math
import random
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.Game import Game


class AmbientParticle:
    def __init__(self, w: int, h: int, random_y: bool = True):
        self.reset(w, h, random_y)

    def reset(self, w: int, h: int, random_y: bool = False):
        self.x = random.uniform(0, max(1, w))
        self.y = random.uniform(0, max(1, h)) if random_y else h + random.uniform(5, 20)
        self.radius = random.uniform(1.2, 2.5)
        self.speed_y = random.uniform(-0.25, -0.7)
        self.speed_x = random.uniform(-0.2, 0.2)
        self.color = random.choice([
            (78, 201, 176),
            (86, 156, 214),
            (220, 220, 220),
            (206, 145, 120),
        ])

    def update(self, w: int, h: int):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.y < -15 or self.x < -20 or self.x > w + 20:
            self.reset(w, h, random_y=False)

    def render(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))


class Panorama:
    def __init__(self, texture_name: str = "background"):
        self.texture_name = texture_name
        self.time: float = 0.0

        self.last_screen_size: tuple[int, int] = (0, 0)
        self.scaled_surface: pygame.Surface | None = None
        self.overlay_surface: pygame.Surface | None = None

        self.particles: list[AmbientParticle] = [
            AmbientParticle(800, 600, random_y=True) for _ in range(30)
        ]

    def _prepare_surfaces(self, screen_w: int, screen_h: int):
        from game.Game import Game
        game = Game.getInstance()

        raw_image = None
        if game and game.textureManager:
            tex = game.textureManager.getTexture(self.texture_name)
            if not tex or not tex.image:
                tex = game.textureManager.getTexture("background") or game.textureManager.getTexture("R")
            if tex and tex.image:
                raw_image = tex.image

        if raw_image:
            img_w, img_h = raw_image.get_size()
            aspect = img_w / img_h

            target_h = int(screen_h * 1.2)
            target_w = int(target_h * aspect)

            if target_w < int(screen_w * 1.2):
                target_w = int(screen_w * 1.2)
                target_h = int(target_w / aspect)

            self.scaled_surface = pygame.transform.smoothscale(raw_image, (target_w, target_h))
        else:
            self.scaled_surface = None

        self.overlay_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        self.overlay_surface.fill((18, 20, 26, 160))

        vignette_h = int(screen_h * 0.22)
        for y in range(vignette_h):
            alpha = int((1.0 - (y / vignette_h)) * 140)
            pygame.draw.line(self.overlay_surface, (10, 12, 16, alpha), (0, y), (screen_w, y))

            bot_alpha = int(((y) / vignette_h) * 160)
            target_y = screen_h - vignette_h + y
            pygame.draw.line(self.overlay_surface, (10, 12, 16, bot_alpha), (0, target_y), (screen_w, target_y))

    def update(self, dt: float = 0.016):
        self.time += dt

    def render(self, screen: pygame.Surface, mouseX: int, mouseY: int):
        w, h = screen.get_size()

        if (w, h) != self.last_screen_size or self.scaled_surface is None:
            self.last_screen_size = (w, h)
            self._prepare_surfaces(w, h)
            self.particles = [AmbientParticle(w, h, random_y=True) for _ in range(30)]

        if self.scaled_surface:
            surf_w, surf_h = self.scaled_surface.get_size()
            max_drift_x = surf_w - w
            max_drift_y = surf_h - h

            auto_x = - (max_drift_x * 0.5) - (math.sin(self.time * 0.1) * (max_drift_x * 0.35))
            auto_y = - (max_drift_y * 0.5) - (math.cos(self.time * 0.08) * (max_drift_y * 0.2))

            parallax_x = (mouseX / w - 0.5) * -35
            parallax_y = (mouseY / h - 0.5) * -20

            draw_x = max(-max_drift_x, min(0, int(auto_x + parallax_x)))
            draw_y = max(-max_drift_y, min(0, int(auto_y + parallax_y)))

            screen.blit(self.scaled_surface, (draw_x, draw_y))
        else:
            screen.fill((18, 20, 26))

        if self.overlay_surface:
            screen.blit(self.overlay_surface, (0, 0))

        for p in self.particles:
            p.update(w, h)
            p.render(screen)
