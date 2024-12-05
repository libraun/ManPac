from collections import deque
import numpy as np
import random

from defs import *
from game import Game

class DataViewer:

    def __init__(self, game: Game):

        self._env = game
    
    def get_state(self) -> tuple:
        result = [[[False for _ in range(32)] for _ in range(32)] for __ in range(5)]
        for i, row in enumerate(self._env.get_map()):
            for j, cell in enumerate(row):
                for k, val in enumerate(cell.get_repr()):
                    result[k][i][j] = val
         
                    
        return tuple(result)
            
    

class StateMemory:
    def __init__(self):
        self.memory = deque([], maxlen=MAX_MEMORY)
    
    def push(self,state,next_state,action,reward,done) -> None:
        self.memory.append((state,next_state,action,reward,done))

    def sample(self, batch_size: int):

        if len(self.memory) > batch_size:
            return random.sample(self.memory, batch_size)
        return self.memory