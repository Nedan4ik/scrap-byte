from __future__ import annotations
import math
from entities.Drone import Drone
from levels.Block import Block
from levels.Level import Level
from levels.Trash import Trash


class Levels:
    COUNT = 2
    LEVEL_TITLES = {
        1: "Первый вылет",
        2: "Условия IF",
    }
    LEVEL_SUBTITLES = {
        1: "Основы навигации и обход барьеров",
        2: "Сенсоры препятствий и ветвление",
    }

    @classmethod
    def get_title(cls, index: int) -> str:
        return cls.LEVEL_TITLES.get(index, f"Сектор {index}")

    @classmethod
    def get_subtitle(cls, index: int) -> str:
        return cls.LEVEL_SUBTITLES.get(index, "Спецоперация")

    @classmethod
    def get(cls, index: int) -> Level:
        if index == 2:
            return cls.create_level_2()
        return cls.create_level_1()

    @staticmethod
    def create_level_1() -> Level:
        rows, cols = 16, 16
        grid: list[list[Block]] = []
        obstacles = {
            (8, 7), (7, 7), (9, 7),
            (5, 10), (11, 10),
            (6, 4), (10, 4),
        }

        for r in range(rows):
            row_blocks: list[Block] = []
            for c in range(cols):
                air = (
                    r < 2 or r >= rows - 2 or c < 2 or c >= cols - 2
                    or (r in (2, 3, rows - 3, rows - 4) and (c <= 3 or c >= cols - 4))
                )
                if air:
                    row_blocks.append(Block(isAir=True))
                elif (c, r) in obstacles:
                    row_blocks.append(Block(isAir=False, is_obstacle=True))
                else:
                    dist = abs(r - rows / 2 + 0.5) + abs(c - cols / 2 + 0.5)
                    col = (58, 70, 92) if dist <= 2.5 else ((46, 54, 70) if (r + c) % 2 == 0 else (42, 50, 64))
                    row_blocks.append(Block(isAir=False, color=col))
            grid.append(row_blocks)

        init_col, init_row = 8, 10
        lvl = Level(blocks=grid, level_index=1)
        cx, cy = lvl.get_block_center(init_col, init_row)
        lvl.drone = Drone(col=init_col, row=init_row, x=cx, y=cy)
        lvl.drone.heading = 0
        lvl.drone.angle = 0.0
        lvl.drone.target_angle = 0.0

        trash_coords = [
            (8, 5, "chip"),
            (11, 8, "board"),
            (5, 8, "core"),
        ]
        items = []
        for c, r, ttype in trash_coords:
            bx, by = lvl.get_block_center(c, r)
            items.append(Trash(bx, by, ttype))
        lvl.trashItems = items

        lvl.info = (
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
        return lvl

    @staticmethod
    def create_level_2() -> Level:
        rows, cols = 16, 16
        grid: list[list[Block]] = []
        obstacles = {
            (4, 9), (5, 9),
            (7, 7), (8, 7),
            (4, 5), (5, 5),
            (10, 8), (10, 9),
            (8, 11), (9, 11),
        }

        for r in range(rows):
            row_blocks: list[Block] = []
            for c in range(cols):
                air = (
                    r < 2 or r >= rows - 2 or c < 2 or c >= cols - 2
                    or (r in (2, 3, rows - 3, rows - 4) and (c <= 3 or c >= cols - 4))
                )
                if air:
                    row_blocks.append(Block(isAir=True))
                elif (c, r) in obstacles:
                    row_blocks.append(Block(isAir=False, is_obstacle=True))
                else:
                    dist = abs(r - rows / 2 + 0.5) + abs(c - cols / 2 + 0.5)
                    col = (54, 68, 88) if dist <= 3.0 else ((44, 52, 68) if (r + c) % 2 == 0 else (40, 48, 62))
                    row_blocks.append(Block(isAir=False, color=col))
            grid.append(row_blocks)

        init_col, init_row = 4, 12
        lvl = Level(blocks=grid, level_index=2)
        cx, cy = lvl.get_block_center(init_col, init_row)
        lvl.drone = Drone(col=init_col, row=init_row, x=cx, y=cy)
        lvl.drone.heading = 0
        lvl.drone.angle = 0.0
        lvl.drone.target_angle = 0.0

        trash_coords = [
            (4, 10, "chip"),
            (7, 9, "board"),
            (7, 5, "core"),
            (10, 6, "hazardous"),
        ]
        items = []
        for c, r, ttype in trash_coords:
            bx, by = lvl.get_block_center(c, r)
            items.append(Trash(bx, by, ttype))
        lvl.trashItems = items

        lvl.info = (
            "СЕКТОР 2: СЕНСОРЫ И УСЛОВИЯ (IF)\n"
            "================================\n\n"
            "Привет, пилот! Поздравляем с переходом в Сектор 2.\n\n"
            "Инженерный отдел активировал сенсорные сканеры дрона и разблокировал оператор «if»!\n"
            "В этом секторе установлены защитные лабиринты с автоматическими перегородками.\n\n"
            "Теперь ты можешь анализировать пространство перед дроном с помощью логических условий:\n"
            "  can_forward()       - возвращает True, если путь впереди свободен (нет обрыва и препятствий)\n"
            "  front_is_obstacle() - возвращает True, если прямо перед дроном стоит блок-препятствие\n"
            "  front_is_air()      - возвращает True, если впереди пропасть\n"
            "  can_pickup()        - возвращает True, если прямо под дроном лежит ценный лом\n\n"
            "Базовые команды дрона:\n"
            "  forward()    - пролететь на 1 клетку вперед\n"
            "  turn_left()  - повернуться налево на 90°\n"
            "  turn_right() - повернуться направо на 90°\n"
            "  pickup()     - подобрать деталь под дроном\n\n"
            "Пример использования условий в коде:\n"
            "  if can_forward():\n"
            "      forward()\n"
            "  else:\n"
            "      turn_right()\n"
            "      forward()\n\n"
            "  if can_pickup():\n"
            "      pickup()\n\n"
            "Используй оператор «if», чтобы безопасно провести дрон мимо препятствий и собрать все платы!"
        )
        return lvl