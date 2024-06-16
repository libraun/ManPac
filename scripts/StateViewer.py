from collections import deque
import numpy as np
import random
import math

from defs import *
from Game import Game

class DataViewer:

    def __init__(self, game: Game):

        self._env = game
    
    def get_state(self) -> tuple:
        player_position = self._env._manpac_position
        adjacent_cells = self._env._get_adjacent_cells(player_position.x,player_position.y)

        wall_left = adjacent_cells[0][1] == Tiles.WALL
        wall_right = adjacent_cells[1][1] == Tiles.WALL
        wall_up = adjacent_cells[2][1] == Tiles.WALL
        try:
            wall_down = adjacent_cells[3][1] == Tiles.WALL
        except:
            wall_down = False

        coin_left = adjacent_cells[0][1] == Tiles.POINT
        coin_right = adjacent_cells[1][1] == Tiles.POINT
        coin_up = adjacent_cells[2][1] == Tiles.POINT
        try:
            coin_down = adjacent_cells[3][1] == Tiles.POINT
        except:
            coin_down = False

        ghost_left = self.get_ghost_left(player_position)
        ghost_right = self.get_ghost_right(player_position)
        ghost_up = self.get_ghost_up(player_position)
        try:
            ghost_down = self.get_ghost_down(player_position)
        except:
            ghost_down = False
        powerup_up = self.get_powerup_up(player_position)
        powerup_down = self.get_powerup_down(player_position)
        powerup_left = self.get_powerup_left(player_position)
        powerup_right = self.get_powerup_right(player_position)

        player_direction = self._env._manpac_direction
        direction_idx = DIRECTIONS.index(player_direction)

        direction_left = direction_idx == 0
        direction_right = direction_idx == 1
        direction_up = direction_idx == 2
        direction_down = direction_idx == 3

        player_is_invincible = self._env._invincible_pac
        ghost_is_near = False
        for ghost in self._env._ghosts:
            if math.dist(player_position,ghost.get_position()) < 5:
                ghost_is_near = True
                break
        state = np.array([
            wall_left, wall_right, wall_up, wall_down,
            coin_left, coin_right, coin_up, coin_down,
            ghost_left, ghost_right, ghost_up, ghost_down,
            powerup_left,powerup_right,powerup_up,powerup_down,
            direction_left, direction_right, direction_up, direction_down,
            player_is_invincible, ghost_is_near
        ],dtype=float)
        return state
        
    
    ## Utility Functions ##
    
    def get_ghost_right(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer.T
        col = grid[coordinate.y]

        if Tiles.GHOST not in col:
            return False
        
        i, = np.where(col >= Tiles.GHOST)
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i > j).any()
    
    def get_ghost_left(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer.T
        col = grid[coordinate.y]

        if Tiles.GHOST not in col:
            return False
        
        i, = np.where(col >= Tiles.GHOST)
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i < j).any()
        
    def get_ghost_up(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer
        col = grid[coordinate.x]

        if Tiles.GHOST not in col:
            return False
        
        i, = np.where(col >= Tiles.GHOST)
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i > j).any()
    
    def get_ghost_down(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer
        col = grid[coordinate.x]

        if Tiles.GHOST not in col:
            return False
        
        i, = np.where(col >= Tiles.GHOST)
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i < j).any()
    
    def get_powerup_up(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer.T
        col = grid[coordinate.y]

        if Tiles.GHOST not in col:
            return False
        
        
        i, = np.where(col == (Tiles.POWERUP | Tiles.GHOST_PLUS_POWERUP))
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        
        return (i > j).any()
    def get_powerup_down(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer.T
        col = grid[coordinate.y]

        if Tiles.GHOST not in col:
            return False
        
        
        i, = np.where(col == (Tiles.POWERUP | Tiles.GHOST_PLUS_POWERUP))
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i > j).any()
    
    def get_powerup_left(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer
        col = grid[coordinate.y]

        if Tiles.POWERUP not in col:
            return False
        
        i, = np.where(col == (Tiles.POWERUP | Tiles.GHOST_PLUS_POWERUP))
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i > j).any()
    def get_powerup_right(self, coordinate: CoordinatePair) -> bool:
        grid = self._env._ghost_layer
        col = grid[coordinate.y]

        if Tiles.POWERUP not in col:
            return False
        

        i, = np.where(col == (Tiles.POWERUP | Tiles.GHOST_PLUS_POWERUP))
        j, = np.where(col == Tiles.MANPAC)

        if i.size == 0 or j.size == 0:
            return False
        return (i < j).any()
    
    

class StateMemory:
    def __init__(self):
        self.memory = deque([], maxlen=MAX_MEMORY)
    
    def push(self,state,next_state,action,reward,done) -> None:
        self.memory.append((state,next_state,action,reward,done))

    def sample(self, batch_size: int):

        if len(self.memory) > batch_size:
            return random.sample(self.memory, batch_size)
        return self.memory