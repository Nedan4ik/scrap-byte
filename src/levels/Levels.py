from __future__ import annotations
import math
from entities.Drone import Drone
from levels.Block import Block
from levels.Level import Level
from levels.Trash import Trash


class Levels:
    COUNT = 3
    LEVEL_TITLES = {
        1: "Первый вылет",
        2: "Условия и циклы",
        3: "Гонка со временем",
    }
    LEVEL_SUBTITLES = {
        1: "Основы навигации (без лимита)",
        2: "Сенсоры, IF, WHILE и FOR (без лимита)",
        3: "Скоростная зачистка сектора за 5 минут",
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
        if index == 3:
            return cls.create_level_3()
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
        lvl = Level(blocks=grid, level_index=1, max_time='inf')
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
            "  - На первых секторах лимит времени отключен — учись и экспериментируй!\n"
            "  - Прокладывай маршрут заранее и пиши команды по порядку сверху вниз.\n"
            "  - Облетай барьеры и не подлетай к обрыву платформы!\n"
            "  - Если ошибся, нажми Ctrl+Z для отмены действия в редакторе.\n"
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
        lvl = Level(blocks=grid, level_index=2, max_time='inf')
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
            "СЕКТОР 2: УСЛОВИЯ И ЦИКЛЫ (IF, WHILE, FOR)\n"
            "===========================================\n\n"
            "Привет, пилот! Поздравляем с переходом в Сектор 2.\n\n"
            "Инженерный отдел активировал сенсоры дрона, а также разблокировал оператор «if»\n"
            "и полноценные циклы «while» и «for»!\n"
            "В Секторе 2 время также не ограничено — осваивай новые конструкции спокойно.\n\n"
            "Сенсоры и условия:\n"
            "  can_forward()       - True, если путь впереди свободен (нет обрыва и препятствий)\n"
            "  front_is_obstacle() - True, если прямо перед дроном стоит блок-препятствие\n"
            "  front_is_air()      - True, если впереди пропасть\n"
            "  can_pickup()        - True, если прямо под дроном лежит ценный лом\n\n"
            "Базовые команды дрона:\n"
            "  forward()    - пролететь на 1 клетку вперед\n"
            "  turn_left()  - повернуться налево на 90°\n"
            "  turn_right() - повернуться направо на 90°\n"
            "  pickup()     - подобрать деталь под дроном\n\n"
            "Примеры циклов и условий:\n"
            "  # Цикл for для выполнения заданного числа шагов:\n"
            "  for i in range(3):\n"
            "      forward()\n\n"
            "  # Цикл while для движения пока свободен путь:\n"
            "  while can_forward():\n"
            "      forward()\n\n"
            "  # Проверка наличия детали и её подбор:\n"
            "  if can_pickup():\n"
            "      pickup()\n\n"
            "Используй циклы while и for, чтобы автоматизировать перемещение и собрать все детали!"
        )
        return lvl

    @staticmethod
    def create_level_3() -> Level:
        rows, cols = 16, 16
        grid: list[list[Block]] = []
        obstacles = {
            (5, 5), (6, 5), (7, 5), (8, 5), (9, 5), (10, 5),
            (5, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10),
            (5, 7), (5, 8),
            (10, 7), (10, 8),
            (7, 7), (8, 7), (7, 8), (8, 8),
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
                    col = (56, 64, 86) if dist <= 3.0 else ((42, 48, 64) if (r + c) % 2 == 0 else (38, 44, 58))
                    row_blocks.append(Block(isAir=False, color=col))
            grid.append(row_blocks)

        init_col, init_row = 3, 11
        lvl = Level(blocks=grid, level_index=3, max_time=300)
        cx, cy = lvl.get_block_center(init_col, init_row)
        lvl.drone = Drone(col=init_col, row=init_row, x=cx, y=cy)
        lvl.drone.heading = 0
        lvl.drone.angle = 0.0
        lvl.drone.target_angle = 0.0

        trash_coords = [
            (3, 4, "chip"),
            (12, 4, "board"),
            (12, 11, "core"),
            (7, 6, "hazardous"),
            (8, 9, "hazardous"),
        ]
        items = []
        for c, r, ttype in trash_coords:
            bx, by = lvl.get_block_center(c, r)
            items.append(Trash(bx, by, ttype))
        lvl.trashItems = items

        lvl.info = (
            "СЕКТОР 3: ГОНКА СО ВРЕМЕНЕМ (5 МИНУТ)\n"
            "======================================\n\n"
            "Внимание, пилот! Аварийная тревога!\n"
            "В Секторе 3 обнаружен критический сбой питания платформы.\n"
            "У тебя есть ровно 5 МИНУТ (300 секунд), чтобы написать алгоритм,\n"
            "запустить дрон и собрать все 5 деталей до аварийного отключения!\n\n"
            "Особенности миссии:\n"
            "  • ЛИМИТ ВРЕМЕНИ: 300 секунд (5:00) на решение и выполнение миссии.\n"
            "  • ТРЕВОЖНАЯ СИГНАЛИЗАЦИЯ: когда времени останется мало, включится красная тревога!\n"
            "  • Вставка кода (Ctrl+V) отключена — пиши код вручную во встроенном редакторе.\n"
            "  • Ошибся в коде? Комбинация Ctrl+Z отменит последнее действие!\n"
            "  • Разрешены все команды дрона, операторы if/else и циклы while и for.\n\n"
            "Команды управления дроном:\n"
            "  forward(), turn_left(), turn_right(), pickup()\n"
            "  can_forward(), front_is_obstacle(), front_is_air(), can_pickup()\n\n"
            "Совет диспетчера:\n"
            "  Используй циклы while can_forward(): forward() для быстрого преодоления прямых\n"
            "  и сбора деталей по периметру и в центре площадки!"
        )
        return lvl