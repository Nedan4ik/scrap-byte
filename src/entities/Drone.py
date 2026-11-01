from __future__ import annotations
import math
from pathlib import Path
import pygame
from textures.SpriteSheet import SpriteSheet, AnimatedSprite


class Drone:
    DIR_OFFSETS = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    def __init__(
        self,
        col: int = 9,
        row: int = 9,
        x: float = 0.0,
        y: float = 0.0,
        xml_path: str | Path = "assets/drone.xml",
    ):
        self.col = col
        self.row = row
        self.x = x
        self.y = y

        self.target_col = col
        self.target_row = row
        self.start_x = x
        self.start_y = y
        self.target_x = x
        self.target_y = y

        self.is_moving = False
        self.move_progress = 1.0
        self.move_duration = 0.7
        self.move_speed = 1.0 / self.move_duration

        self.is_turning = False
        self.turn_progress = 1.0
        self.turn_duration = self.move_duration
        self.turn_speed = 1.0 / self.turn_duration
        self.start_angle = 0.0

        self.heading = 0
        self.angle = 0.0
        self.target_angle = 0.0

        self.time = 0.0
        self.is_busy = False

        self.spritesheet = SpriteSheet(xml_path)
        self.sprite = AnimatedSprite(self.spritesheet, default_anim="idle", fps=8.0)

    @staticmethod
    def ease_back_out(t: float) -> float:
        c1 = 1.35
        c3 = c1 + 1.0
        u = math.pow(t, 2.7)
        return 1.0 + c3 * math.pow(u - 1.0, 3) + c1 * math.pow(u - 1.0, 2)

    def idle(self):
        if not self.is_busy and self.sprite.current_anim != "idle":
            self.sprite.play("idle", loop=True, fps=6.0)

    def turn_left(self):
        if self.is_busy:
            return
        self.heading = (self.heading - 1) % 4
        self.start_angle = self.angle
        self.target_angle += 90.0
        self.turn_progress = 0.0
        self.is_turning = True
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().play_drone_turn()

    def turn_right(self):
        if self.is_busy:
            return
        self.heading = (self.heading + 1) % 4
        self.start_angle = self.angle
        self.target_angle -= 90.0
        self.turn_progress = 0.0
        self.is_turning = True
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().play_drone_turn()

    def move_forward(self, level) -> bool:
        if self.is_busy or self.is_moving:
            return False

        dcol, drow = self.DIR_OFFSETS[self.heading]
        nxt_c = self.col + dcol
        nxt_r = self.row + drow

        if level.is_air(nxt_c, nxt_r) or getattr(level, "is_obstacle", lambda c, r: False)(nxt_c, nxt_r):
            from sound.SoundManager import SoundManager
            SoundManager.get_instance().play_obstacle_hit()
            return False

        self.start_move(nxt_c, nxt_r, level)
        from sound.SoundManager import SoundManager
        SoundManager.get_instance().play_drone_move()
        return True

    def start_move(self, target_col: int, target_row: int, level):
        self.is_moving = True
        self.target_col = target_col
        self.target_row = target_row
        self.start_x = self.x
        self.start_y = self.y
        tx, ty = level.get_block_center(target_col, target_row)
        self.target_x = tx
        self.target_y = ty
        self.move_progress = 0.0
        self.move_speed = 1.0 / self.move_duration
        self.sprite.play("move_forward", loop=True, fps=12.0)

    def pickup(self, on_complete=None):
        self.is_busy = True

        def _finish():
            self.is_busy = False
            self.idle()
            if on_complete:
                on_complete()

        self.sprite.play("pickup", loop=False, fps=8.0, on_finish=_finish)

    def update(self, dt: float = 0.016):
        self.time += dt

        if self.is_turning:
            self.turn_speed = 1.0 / self.move_duration
            self.turn_progress += dt * self.turn_speed
            t = min(1.0, self.turn_progress)
            ease = self.ease_back_out(t)
            self.angle = self.start_angle + (self.target_angle - self.start_angle) * ease

            if not self.is_busy and not self.is_moving:
                if self.target_angle > self.start_angle:
                    self.sprite.play("turn_left", loop=False, fps=10.0)
                else:
                    self.sprite.play("turn_right", loop=False, fps=10.0)

            if t >= 1.0:
                self.angle = self.target_angle
                self.is_turning = False
                if not self.is_moving and not self.is_busy:
                    self.idle()

        if self.is_moving:
            if not self.is_busy and self.sprite.current_anim != "move_forward":
                self.sprite.play("move_forward", loop=True, fps=12.0)
            self.move_speed = 1.0 / self.move_duration
            self.move_progress += dt * self.move_speed
            t = min(1.0, self.move_progress)
            ease = self.ease_back_out(t)
            self.x = self.start_x + (self.target_x - self.start_x) * ease
            self.y = self.start_y + (self.target_y - self.start_y) * ease

            if t >= 1.0:
                self.col = self.target_col
                self.row = self.target_row
                self.x = self.target_x
                self.y = self.target_y
                self.is_moving = False
                from sound.SoundManager import SoundManager
                SoundManager.get_instance().stop_drone_move()
                if not self.is_turning and not self.is_busy:
                    self.idle()
        elif not self.is_turning and not self.is_moving and not self.is_busy:
            if self.sprite.current_anim not in ("idle",):
                self.idle()

        self.sprite.update(dt)

    def render(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0):
        hover_damping = 0.2 if self.is_moving else 1.0
        hover_y = math.sin(self.time * 3.2) * 1.6 * hover_damping
        hover_x = math.cos(self.time * 1.8) * 0.8 * hover_damping

        draw_x = int((self.x + hover_x - offset_x) * zoom)
        draw_y = int((self.y + hover_y - offset_y) * zoom)

        drone_scale = 1.05 * zoom
        self.sprite.render(screen, draw_x, draw_y, angle=self.angle, scale=drone_scale)
