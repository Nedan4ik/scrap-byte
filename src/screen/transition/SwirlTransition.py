from __future__ import annotations
import math
import pygame


class SwirlTransition:
    def __init__(
        self,
        game,
        old_surface: pygame.Surface,
        target_screen,
        tile_size: int = 48,
    ):
        self.game = game
        self.target_screen = target_screen
        self.w, self.h = old_surface.get_size()
        self.tile_size = tile_size

        self.cols = math.ceil(self.w / tile_size)
        self.rows = math.ceil(self.h / tile_size)

        self.old_tiles = self._slice_surface(old_surface)
        self.new_tiles = []

        self.phase = 1
        self.timer = 0.0

        self.close_duration = 0.60
        self.hold_duration = 0.10
        self.open_duration = 0.95
        self.finished = False

    def _slice_surface(self, surface: pygame.Surface) -> list[tuple]:
        tiles = []
        cx = self.cols / 2.0
        cy = self.rows / 2.0
        max_dist = max(1.0, math.hypot(cx, cy))

        for gy in range(self.rows):
            for gx in range(self.cols):
                rx = gx * self.tile_size
                ry = gy * self.tile_size
                rw = min(self.tile_size, self.w - rx)
                rh = min(self.tile_size, self.h - ry)

                tile_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                tile_surf.blit(surface, (0, 0), pygame.Rect(rx, ry, rw, rh))

                dx = gx - cx
                dy = gy - cy
                dist = math.hypot(dx, dy) / max_dist
                angle_ratio = (math.atan2(dy, dx) + math.pi) / (2.0 * math.pi)

                center_x = rx + self.tile_size / 2.0
                center_y = ry + self.tile_size / 2.0

                tiles.append((tile_surf, center_x, center_y, dist, angle_ratio))
        return tiles

    def update(self, dt: float = 0.016):
        self.timer += dt

        if self.phase == 1:
            if self.timer >= self.close_duration:
                self.phase = 2
                self.timer = 0.0

                self.game._currentScreen = self.target_screen

                temp_surf = pygame.Surface((self.w, self.h))
                self.target_screen.render(temp_surf, self.game.mouse.mouseX, self.game.mouse.mouseY)
                self.new_tiles = self._slice_surface(temp_surf)

        elif self.phase == 2:
            if self.timer >= self.hold_duration:
                self.phase = 3
                self.timer = 0.0

        elif self.phase == 3:
            if self.timer >= self.open_duration:
                self.finished = True

    def render(self, screen: pygame.Surface):
        screen.fill((16, 18, 24))

        if self.phase == 2:
            return

        is_closing = (self.phase == 1)
        tiles = self.old_tiles if is_closing else self.new_tiles
        if not tiles:
            return

        current_duration = self.close_duration if is_closing else self.open_duration
        active_window = max(0.001, current_duration - 0.38)

        for tile_surf, cx, cy, dist, angle_ratio in tiles:
            if is_closing:
                stagger = dist * 0.28 + angle_ratio * 0.10
            else:
                stagger = (1.0 - dist) * 0.28 + (1.0 - angle_ratio) * 0.10

            raw_t = (self.timer - stagger) / active_window
            clamped_t = max(0.0, min(1.0, raw_t))

            ease = clamped_t * clamped_t * (3.0 - 2.0 * clamped_t)

            if is_closing:
                scale = max(0.001, 1.0 - ease)
                angle = ease * 180.0
            else:
                scale = max(0.001, ease)
                angle = (1.0 - ease) * -180.0

            if scale > 0.02:
                tw = max(1, int(self.tile_size * scale))
                th = max(1, int(self.tile_size * scale))
                scaled = pygame.transform.scale(tile_surf, (tw, th))
                rotated = pygame.transform.rotate(scaled, angle)
                rot_rect = rotated.get_rect(center=(int(cx), int(cy)))
                screen.blit(rotated, rot_rect)
