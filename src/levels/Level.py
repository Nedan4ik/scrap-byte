from __future__ import annotations
import math
import pygame
from entities.Drone import Drone
from levels.Block import Block
from levels.Trash import Trash


class Level:
    def __init__(
        self,
        blocks: list[list[Block]] | list[Block] | None = None,
        trashItems: list[Trash] | None = None,
        level_index: int = 1,
        info: str | None = None,
    ):
        self.tile_size: int = 56
        self.level_index: int = level_index

        if blocks is None:
            self.blocks = self._create_default_platform(18, 18)
        elif blocks and isinstance(blocks[0], list):
            self.blocks = blocks
        else:
            side = int(math.isqrt(len(blocks))) if blocks else 0
            self.blocks = [blocks[i * side : (i + 1) * side] for i in range(side)] if side * side == len(blocks) and side > 0 else ([blocks] if blocks else [])

        self.rows: int = len(self.blocks)
        self.cols: int = len(self.blocks[0]) if self.rows > 0 else 0

        self.origin_x: float = -(self.cols * self.tile_size) / 2.0
        self.origin_y: float = -(self.rows * self.tile_size) / 2.0

        self.trashItems: list[Trash] = trashItems if trashItems is not None else []

        init_col = self.cols // 2
        init_row = self.rows // 2
        init_x, init_y = self.get_block_center(init_col, init_row)
        self.drone = Drone(col=init_col, row=init_row, x=init_x, y=init_y)

        self.camera_x: float = 0.0
        self.camera_y: float = 0.0
        self.camera_initialized: bool = False

        if info is not None:
            self.info: str = info
        else:
            self.info: str = (
                "СЕКТОР 1: ПЕРВЫЙ ВЫЛЕТ\n"
                "======================\n\n"
                "Привет, новичок! Рады видеть тебя за пультом дрона.\n\n"
                "Добро пожаловать в Scrap-Byte! Твой дрон-утилизатор только что приземлился\n"
                "на заброшенной платформе Сектора 1. Вокруг полно ценного лома, брошенных чипов и плат.\n\n"
                "Внимание: на платформе установлены защитные блоки-препятствия (с оранжевой разметкой).\n"
                "Они абсолютно непроходимы — дрон не сможет через них пролететь, облетай их стороной!\n\n"
                "Твоя задача — расчистить посадочную площадку и собрать все детали.\n"
                "Пиши команды в редакторе кода и отправляй дрон в путь!\n\n"
                "Команды управления дроном:\n"
                "  forward()    - пролететь на 1 клетку вперед\n"
                "  turn_left()  - повернуть дрон налево на 90 градусов\n"
                "  turn_right() - повернуть дрон направо на 90 градусов\n"
                "  pickup()     - подобрать деталь прямо под дроном\n\n"
                "Советы диспетчера:\n"
                "  - Прокладывай маршрут заранее и пиши команды по порядку сверху вниз.\n"
                "  - Облетай барьеры и не подлетай к обрыву платформы!\n"
                "  - Когда закончишь писать команды, нажми зеленую кнопку запуска (▶).\n\n"
                "Удачи в первом вылете, пилот! Собери весь лом!"
            )

        self.stars: list[tuple[int, int, int, tuple[int, int, int]]] = [
            (
                (i * 137 + 49) % 1600,
                (i * 263 + 83) % 1200,
                1 if i % 3 != 0 else 2,
                (175, 185, 210) if i % 4 == 0 else (95, 105, 130),
            )
            for i in range(120)
        ]

    def get_level_info(self) -> str:
        return self.info

    @staticmethod
    def _create_default_platform(rows: int = 18, cols: int = 18) -> list[list[Block]]:
        grid: list[list[Block]] = []
        obstacle_coords = {(6, 7), (7, 6), (11, 7), (12, 6), (6, 11), (7, 12), (11, 11), (12, 12), (9, 5), (9, 13)}
        for r in range(rows):
            row_blocks: list[Block] = []
            for c in range(cols):
                air = (
                    r < 2 or r >= rows - 2 or c < 2 or c >= cols - 2
                    or (r in (2, 3, rows - 4, rows - 3) and (c <= 3 or c >= cols - 4))
                    or (r in (8, 9) and (c == 2 or c == cols - 3))
                    or (r in (4, 5) and c == 5)
                    or (r in (12, 13) and c == cols - 6)
                )
                if air:
                    row_blocks.append(Block(isAir=True))
                elif (c, r) in obstacle_coords:
                    row_blocks.append(Block(isAir=False, is_obstacle=True))
                else:
                    dist = abs(r - rows / 2 + 0.5) + abs(c - cols / 2 + 0.5)
                    col = (58, 70, 92) if dist <= 2.5 else ((46, 54, 70) if (r + c) % 2 == 0 else (42, 50, 64))
                    row_blocks.append(Block(isAir=False, color=col))
            grid.append(row_blocks)
        return grid

    def is_air(self, col: int, row: int) -> bool:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return True
        return self.blocks[row][col].isAir

    def is_obstacle(self, col: int, row: int) -> bool:
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return bool(getattr(self.blocks[row][col], "is_obstacle", False))

    def is_walkable(self, col: int, row: int) -> bool:
        return (not self.is_air(col, row)) and (not self.is_obstacle(col, row))

    def get_block_center(self, col: int, row: int) -> tuple[float, float]:
        cx = self.origin_x + col * self.tile_size + self.tile_size / 2.0
        cy = self.origin_y + row * self.tile_size + (self.tile_size - 5.0) / 2.0
        return cx, cy

    def world_to_grid(self, x: float, y: float) -> tuple[int, int]:
        col = int(math.floor((x - self.origin_x) / self.tile_size))
        row = int(math.floor((y - self.origin_y) / self.tile_size))
        return col, row

    def center_camera(self, target_x: float, target_y: float, screen_w: int, screen_h: int, zoom: float = 1.0):
        self.camera_x = target_x - (screen_w / 2.0) / zoom
        self.camera_y = target_y - (screen_h / 2.0) / zoom

    def center_on_drone(self, screen_w: int, screen_h: int, zoom: float = 1.0):
        self.center_camera(self.drone.x, self.drone.y, screen_w, screen_h, zoom=zoom)

    def pan_camera(self, dx: float, dy: float):
        self.camera_x += dx
        self.camera_y += dy

    def update(self, dt: float = 0.016, screen_w: int = 800, screen_h: int = 600, zoom: float = 1.0):
        self.drone.update(dt)
        if not self.camera_initialized:
            self.center_camera(self.drone.x, self.drone.y, screen_w, screen_h, zoom=zoom)
            self.camera_initialized = True

    def render(self, screen: pygame.Surface, zoom: float = 1.0):
        sw, sh = screen.get_size()
        screen.fill((10, 12, 18))

        for sx, sy, rad, col in self.stars:
            draw_sx = int((sx - self.camera_x * 0.15 * zoom) % sw)
            draw_sy = int((sy - self.camera_y * 0.15 * zoom) % sh)
            if rad == 1:
                screen.set_at((draw_sx, draw_sy), col)
            else:
                pygame.draw.circle(screen, col, (draw_sx, draw_sy), max(1, int(rad * zoom)))

        tile_px = self.tile_size * zoom
        start_col = max(0, int(math.floor((self.camera_x - self.origin_x) / self.tile_size)))
        end_col = min(self.cols, int(math.ceil((self.camera_x + (sw / zoom) - self.origin_x) / self.tile_size)) + 1)
        start_row = max(0, int(math.floor((self.camera_y - self.origin_y) / self.tile_size)))
        end_row = min(self.rows, int(math.ceil((self.camera_y + (sh / zoom) - self.origin_y) / self.tile_size)) + 1)

        draw_size = max(1, int(math.ceil(tile_px)))
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                block = self.blocks[r][c]
                draw_x = int((self.origin_x + c * self.tile_size - self.camera_x) * zoom)
                draw_y = int((self.origin_y + r * self.tile_size - self.camera_y) * zoom)
                block.render(screen, draw_x, draw_y, draw_size)

        for t in self.trashItems:
            t.render(screen, self.camera_x, self.camera_y, zoom=zoom)

        self.drone.render(screen, offset_x=self.camera_x, offset_y=self.camera_y, zoom=zoom)

    def to_dict(self) -> dict:
        return {
            "drone": {
                "col": self.drone.col,
                "row": self.drone.row,
                "heading": self.drone.heading,
                "angle": self.drone.angle,
            },
            "camera": {
                "x": self.camera_x,
                "y": self.camera_y,
            },
            "trash": [t.to_dict() for t in self.trashItems],
            "info": self.info,
            "level_index": self.level_index,
        }

    def load_state(self, data: dict):
        if "level_index" in data:
            self.level_index = int(data["level_index"])
        d_data = data.get("drone", {})
        if "col" in d_data and "row" in d_data:
            col, row = int(d_data["col"]), int(d_data["row"])
        else:
            col, row = self.world_to_grid(float(d_data.get("x", 0.0)), float(d_data.get("y", 0.0)))

        if self.is_air(col, row):
            col, row = self.cols // 2, self.rows // 2

        cx, cy = self.get_block_center(col, row)
        self.drone.col = self.drone.target_col = col
        self.drone.row = self.drone.target_row = row
        self.drone.x = self.drone.target_x = cx
        self.drone.y = self.drone.target_y = cy
        self.drone.is_moving = False

        heading_angles = (0.0, -90.0, 180.0, 90.0)
        self.drone.heading = int(d_data.get("heading", 0)) % 4
        default_angle = heading_angles[self.drone.heading]
        self.drone.angle = float(d_data.get("angle", default_angle)) if "heading" in d_data else default_angle
        self.drone.target_angle = self.drone.angle
        self.drone.start_angle = self.drone.angle
        self.drone.is_turning = False
        self.drone.turn_progress = 1.0

        cam_data = data.get("camera", {})
        if "x" in cam_data and "y" in cam_data:
            self.camera_x = float(cam_data["x"])
            self.camera_y = float(cam_data["y"])
            self.camera_initialized = True

        t_data = data.get("trash", [])
        if t_data:
            self.trashItems = [Trash.from_dict(td) for td in t_data]

        if "info" in data:
            self.info = str(data["info"])
