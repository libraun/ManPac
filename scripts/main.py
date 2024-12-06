import pygame as pg

from game import Game
from defs import *

from state_memory import StateMemory
from cnn_model import CNNModel
from agent import Agent

def draw_map():

    global screen, game_env
    # Reset the screen by filling it with black pixels.
    screen.fill((0,0,0))
    for i, row in enumerate(game_env.map):
        for j, cell in enumerate(row):
            
            # Create even-length rectangles, coloring them black if they represent a wall or grey if free space.
            rect = pg.Rect(i*BLOCKSIZE, j*BLOCKSIZE, BLOCKSIZE, BLOCKSIZE)
            rect_color = pg.Color((255,255,255)) if cell.is_wall else pg.Color((200,200,200))

            # Draw the base tile onto the screen first, so that other items can be rendered over it
            pg.draw.rect(screen, rect_color, rect)

            # Draw any "character sprites" (pacman or ghosts) 
            if cell.has_ghost or cell.has_manpac:

                character_color = pg.Color((255,255,0)) if cell.has_manpac else pg.Color((0,255,255))
                pg.draw.ellipse(screen, character_color, rect, 0)
            # At bottom so that we don't render coins over ghosts
            elif cell.has_powerup or cell.has_coin:

                item_color = pg.Color((0,255,0)) if cell.has_coin else pg.Color((0,255,255))
                pg.draw.circle(screen, item_color, ((i*20)+10,(j*20)+10), 5)
    # Finally, update the display to render all changes.
    pg.display.flip()


    
def get_state(grid) -> tuple:
    result = [[[False for _ in range(32)] for _ in range(32)] for __ in range(5)]
    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            for k, val in enumerate(cell.get_repr()):
                result[k][i][j] = val
         
    return tuple(result)

# Enables graphics (using Pygame) if true
DEBUG_ON = False

if __name__ == "__main__":

    game_env = Game()

    model = CNNModel(in_features=5, out_features=4, hidden_dim=128)
    agent = Agent(model=model,state_memory=StateMemory())

    pg.init()

    if DEBUG_ON:
        screen = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        clock = pg.time.Clock()

    running = True

    top_score = 0
    current_score = 0
    while running:

        if DEBUG_ON:
            draw_map()
            clock.tick(50)

        last_state = get_state(game_env.map)

        action = agent.get_action(last_state)
        target_direction = DIRECTIONS[action.index(1)]

        game_complete, reward = game_env.play_step(target_direction)
        if reward > 0:
            current_score += reward

        final_state = get_state(game_env.map)
            
        agent.train_step(last_state,final_state,action,reward,game_complete)
        
        agent.state_memory.push(last_state,final_state,action,reward,game_complete)
        if game_complete:

            agent.train()
            agent.n_games += 1

            print(agent.total_loss / agent.n_games, current_score)
            if current_score > top_score:
                top_score = current_score
                print("New High Score:", top_score)

            current_score = 0
            game_env.reset()

    exit(0)
