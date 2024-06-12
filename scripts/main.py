import pygame as pg
import random

from Game import Game
from defs import EXIT_FAILURE, EXIT_SUCCESS, CoordinatePair,Tiles

WINDOW_WIDTH = 620  
WINDOW_HEIGHT = 620

BLOCKSIZE = 20

COLORS = (
    pg.Color((255,255,255)),
    pg.Color((200,200,200)),
    pg.Color((0,0,255)), 
    pg.Color((0,255,0)),
    pg.Color((255,0,0)),
    pg.Color((255,255,0)),
    pg.Color((0,255,0)),
    pg.Color((0,255,255)),
    pg.Color((255,0,0)),
    pg.Color((255,0,0)),
)

def draw_map():
    global SCREEN,ENV
    SCREEN.fill((0,0,0))
    for x in range(WINDOW_WIDTH, BLOCKSIZE):
        for y in range(WINDOW_HEIGHT, BLOCKSIZE):

            rect = pg.Rect(x, y, BLOCKSIZE, BLOCKSIZE)
            pg.draw.rect(SCREEN, pg.Color((200,200,200)), rect,1)
    
    ## TODO: Tidy this up...
    for i, row in enumerate(ENV.get_map().T):
        for j, cell_value in enumerate(row):
            rect = pg.Rect(i*BLOCKSIZE, j*BLOCKSIZE, \
                           BLOCKSIZE, BLOCKSIZE)
            if cell_value == Tiles.POWERUP or cell_value == Tiles.POINT:
                pg.draw.rect(SCREEN, COLORS[1], rect)
                if cell_value == Tiles.POWERUP:
                    pg.draw.ellipse(SCREEN, COLORS[7], rect, 0)
                else:
                    pg.draw.circle(SCREEN,COLORS[6],((i * 20) + 10,(j * 20) + 10) , 5)
            elif cell_value == Tiles.MANPAC:
                pg.draw.rect(SCREEN, COLORS[1], rect)
                pg.draw.ellipse(SCREEN, COLORS[5], rect, 0)
            else:
                pg.draw.rect(SCREEN, COLORS[cell_value], rect)
    pg.display.flip()

DIRECTIONS = (
    CoordinatePair(1, 0),
    CoordinatePair(-1, 0),
    CoordinatePair(0, 1),
    CoordinatePair(0, -1),
)

if __name__ == "__main__":

    ENV = Game()
    running = True

    pg.init()

    SCREEN = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    clock = pg.time.Clock()

    draw_map()
    while running:

      #  direction = random.choice(DIRECTIONS)

        result = ENV.play_step(CoordinatePair(1, 0),)
        draw_map()

        clock.tick(5)

    exit(EXIT_SUCCESS)
