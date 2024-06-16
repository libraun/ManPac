import random

import torch
import torch.nn as nn
import torch.optim as optim

from StateViewer import StateMemory
from defs import BATCH_SIZE

class Agent:

    def __init__(self, model, state_memory: StateMemory, lr: float=0.001):
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