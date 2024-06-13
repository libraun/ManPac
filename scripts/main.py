from Game import Game
from defs import EXIT_CODES, CoordinatePair, Tiles

from DataViewer import *
from Model import Model

DEBUG_ON = True

if DEBUG_ON:

    import pygame as pg

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
                
                else:
                    pg.draw.rect(SCREEN, COLORS[cell_value], rect)

        manpac_position = ENV.get_manpac_position()
        manpac_rect = pg.Rect(manpac_position.y * BLOCKSIZE,manpac_position.x * BLOCKSIZE,BLOCKSIZE,BLOCKSIZE)

      #  print(env.)
        pg.draw.rect(SCREEN, COLORS[1], rect)
        pg.draw.ellipse(SCREEN, COLORS[5], manpac_rect, 0)
        pg.display.flip()


DIRECTIONS = (
    CoordinatePair(1, 0),
    CoordinatePair(-1, 0),
    CoordinatePair(0, 1),
    CoordinatePair(0, -1),
)


DEBUG_ON = True

if __name__ == "__main__":

    ENV = Game()

    state_viewer = DataViewer(ENV)

    model = Model(in_features=13, out_features=4, hidden_dim=256)
    agent = Agent(model=model,state_memory=StateMemory())

    if DEBUG_ON:
        pg.init()

        SCREEN = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        clock = pg.time.Clock()

        draw_map()

    replay = True
    running = True
    while running:

        last_state = state_viewer.get_state()
        action = agent.get_action(last_state)

        target_direction = DIRECTIONS[action.index(1)]

        game_status,reward = ENV.play_step(target_direction)
        final_state = state_viewer.get_state()
        
        agent.train_step(last_state,final_state,action,reward,game_status)
        
        agent.state_memory.push(last_state,final_state,action,reward,game_status)
        if game_status == GameStatus.GAME_OVER:
            agent.train()
            agent.n_games += 1
            if replay:
                ENV.reset()

        if DEBUG_ON:
            draw_map()
            clock.tick(5)

    exit(EXIT_CODES.EXIT_SUCCESS)
