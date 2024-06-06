import pygame as pg

from Game import Game
from defs import EXIT_FAILURE, EXIT_SUCCESS, Tiles

DEBUG=True

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

def drawGrid():
    global SCREEN,ENV
    SCREEN.fill((0,0,0))
    blockSize = 20 #Set the size of the grid block
    for x in range(0, WINDOW_WIDTH, blockSize):
        for y in range(0, WINDOW_HEIGHT, blockSize):
            rect = pg.Rect(x, y, blockSize, blockSize)
            pg.draw.rect(SCREEN, pg.Color((200,200,200)) , rect,1)
    for j, t in enumerate(ENV._map.transpose()):
        for l, i in enumerate(t):
            rect = pg.Rect(j * 20, l * 20,20,20)
            if i == 1:
                
                
                pg.draw.rect(SCREEN, pg.Color((255,255,255)) , rect)
            elif i == 2:
                pg.draw.rect(SCREEN,pg.Color((200,200,200)),rect)
            elif i == 3:
                pg.draw.rect(SCREEN,pg.Color((0,0,255)),rect)
            elif i == 4:
                pg.draw.rect(SCREEN,pg.Color((0,255,0)),rect)



if __name__ == "__main__":

    ENV = Game()
    running = True

    pg.init()
    SCREEN = pg.display.set_mode((500,500))
    clock = pg.time.Clock()

    drawGrid()
    pg.display.update()
    while running:



        result = ENV.play_step((1, 0))
        drawGrid()

        pg.display.flip()
        clock.tick(1)

    # Check if game is running
    print(result)

    exit(EXIT_SUCCESS)
