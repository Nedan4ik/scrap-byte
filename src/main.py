import argparse
import pygame

from game.Game import Game

# TODO
# Может быть сделать циклы во втором уровне

if __name__ == '__main__':
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument(
        '--debug',
        action='store_true',
        help='Запуск игры в режиме отладки'
    )

    argumentParser.add_argument(
        '-width',
        type=int,
        default=1080,
        help='Ширина окна игры'
    )

    argumentParser.add_argument(
        '-height',
        type=int,
        default=600,
        help='Высота окна игры'
    )

    argumentParser.add_argument(
        '-maxFps',
        type=int,
        default=60,
        help='Максимальная частота кадров'
    )

    args = argumentParser.parse_args()

    pygame.init()
    game = Game(debug=args.debug, width=args.width, height=args.height, maxFps=args.maxFps)
    game.run()