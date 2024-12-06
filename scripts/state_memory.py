from collections import deque
import random

from defs import *
    

class StateMemory:
    def __init__(self):
        self.memory = deque([], maxlen=MAX_MEMORY)
    
    def push(self,state,next_state,action,reward,done) -> None:
        self.memory.append((state,next_state,action,reward,done))

    def sample(self, batch_size: int):

        if len(self.memory) > batch_size:
            return random.sample(self.memory, batch_size)
        return self.memory