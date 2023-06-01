import pygame as pg

pg.init()
pg.font.init()

from Src.SpaceGame import SpaceGame


def main():
    '''
        lazy start
    '''
    game = SpaceGame()
    game.start()


if __name__ == "__main__":
    main()
