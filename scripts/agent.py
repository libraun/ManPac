# Note: This class was adapted from Patrick Loeber's Snake AI Agent.
# The original project can be found at: https://github.com/patrickloeber/snake-ai-pytorch


import random

import torch
import torch.nn as nn
import torch.optim as optim

from state_memory import StateMemory
from defs import BATCH_SIZE

class Agent:

    def __init__(self, model, state_memory: StateMemory, lr: float=0.0001):
        self.state_memory = state_memory
        self.n_games = 0
        self.model = model
        self.gamma = 0.9
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = nn.L1Loss()

        self.total_loss = 0

    def train(self):
        mini_sample = self.state_memory.sample(BATCH_SIZE)

        state, actions, rewards, next_states, done = zip(*mini_sample)
        self.train_step(state,actions,rewards,next_states,done)

    def train_step(self,state,next_state,action,reward,done):
        state = torch.tensor(state, dtype=torch.float32)
        next_state = torch.tensor(next_state, dtype=torch.float32)
                
        action = torch.tensor(action,dtype=torch.float16)
        reward = torch.tensor(reward,dtype=torch.float16)
        if len(state.shape) == 3:
            state = torch.unsqueeze(state, 0)   
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        self.optimizer.zero_grad()
 
        pred = self.model(state)
        target = pred.clone()
        
        for idx in range(len(done)):
            Q_new = reward[idx]
            if done[idx]:
                model_result = self.model(next_state[idx])
                Q_new = reward[idx] + self.gamma * torch.mean(model_result)

            target[idx][torch.argmax(action).item()] = Q_new
        loss = self.criterion(pred, target)
        
        self.total_loss += loss.item()
        
        loss.backward()
        
        self.optimizer.step()
    

    def get_action(self, state):
        final_move = [0,0,0,0]
        if random.randint(0,200) < (300 - self.n_games): 
            move = random.randint(0,3)
        else:
            # Batch the state to be 4D
            state_vec = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            prediction = self.model(state_vec)
            move = prediction.argmax().item()

            
        final_move[move] = 1
        return final_move