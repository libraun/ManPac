from collections import deque
import random

from defs import *
from Game import Game

import torch
import torch.nn as nn
import torch.optim as optim

import numpy

class DataViewer:

    def __init__(self, game: Game):

        self._env = game
    
    def get_state(self) -> tuple:
        player_position = self._env._manpac_position
        adjacent_cells = self._env._get_adjacent_cells(player_position)

        wall_left = adjacent_cells[0][1] == Tiles.WALL
        wall_right = adjacent_cells[1][1] == Tiles.WALL
        wall_up = adjacent_cells[2][1] == Tiles.WALL
        wall_down = adjacent_cells[3][1] == Tiles.WALL

        coin_left = adjacent_cells[0][1] == Tiles.POINT
        coin_right = adjacent_cells[1][1] == Tiles.POINT
        coin_up = adjacent_cells[2][1] == Tiles.POINT
        coin_down = adjacent_cells[3][1] == Tiles.POINT

        ghost_left = adjacent_cells[0][1] >= Tiles.GHOST
        ghost_right = adjacent_cells[1][1] >= Tiles.GHOST
        ghost_up = adjacent_cells[2][1] >= Tiles.GHOST
        ghost_down = adjacent_cells[3][1] == Tiles.GHOST

        player_is_invincible = self._env._invincible_pac
        state = [
            wall_left, wall_right, wall_up, wall_down,
            coin_left, coin_right, coin_up, coin_down,
            ghost_left, ghost_right, ghost_up, ghost_down,
            player_is_invincible
        ]
        return numpy.array(state,dtype=bool)
        
    
    ## Utility Functions ##
'''
    def get_fruit_right(self) -> bool:
        if self.last_direction[1] != 0:
            column = self.grid.transpose()[self.snake_body[-1][1]]
            if 2 not in column:
                return False
            i, = np.where(column == 3)
            j, = np.where(column == 2)
            if i.size == 0 or j.size == 0:
                return False
            return (i < j).any()
        else:
            row = self.grid[self.snake_body[-1][0]]
            if 2 not in row:
                return False
            i, = np.where(row == 3)
            j, = np.where(row == 2)
            if j.size == 0 or j.size == 0:
                return False

            return (i > j).any()
        
    def get_danger_left(self) -> bool:
        if self.last_direction[1] != 0:

            column = self.grid.transpose()[self.snake_body[-1][1]]
            if 2 not in column:
                return False
            i, = np.where(column == 3)
            j, = np.where(column == 2)
            if i.size or j.size:
                return False

            return (i > j).any()
        else:
            row = self.grid[self.snake_body[-1][0]]
            if 2 not in row:
                return False
            i, = np.where(row == 3)
            j, = np.where(row == 2)
            if i.size == 0 or j.size == 0:
                return False

            return (i < j).any()
'''


class StateMemory:
    def __init__(self, lr: float = 0.01):
        self.memory = deque([], maxlen=MAX_MEMORY)
    
    def push(self,state,next_state,action,reward,done) -> None:
        self.memory.append((state,next_state,action,reward,done))

    def sample(self, batch_size: int):

        if len(self.memory) > batch_size:
            return random.sample(self.memory, batch_size)
        return self.memory
    



class Agent:

    def __init__(self, model, state_memory: StateMemory, lr: float=0.01):
        self.state_memory = state_memory
        self.n_games = 0
        self.model = model
        self.gamma = 0.99
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.MSELoss()


    def train(self):
        sample_memory = self.state_memory.sample(batch_size=BATCH_SIZE)
        state,next_state,action,reward,done = zip(*sample_memory)
        self.train_step(state,next_state,action,reward,done)

    def train_step(self,state,next_state,action,reward,done):

        state = torch.tensor(state,dtype=torch.float)
        next_state = torch.tensor(next_state,dtype=torch.float)
        action = torch.tensor(action,dtype=torch.float)
        reward = torch.tensor(reward,dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state,0)
            action = torch.unsqueeze(action,0)
            reward = torch.unsqueeze(reward,0)
            done = (done,)

        pred = self.model(state)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action).item()] = Q_new
        self.optimizer.zero_grad()

        loss = self.criterion(target,pred)
        loss.backward()

        self.optimizer.step()

    def get_action(self, state):
        final_move = [0,0,0,0]
        if random.randint(0,200) < (80 - self.n_games):
            move = random.randint(0,3)
        else:
            state_vec = torch.tensor(state,dtype=torch.float)
            prediction = self.model(state_vec)

            move = torch.argmax(prediction).item()
        final_move[move] = 1
        return final_move
