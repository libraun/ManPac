import random

import torch
import torch.nn as nn
import torch.optim as optim

from state_viewer import StateMemory
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
        if len(self.state_memory.memory) > 5000:
            mini_sample = random.sample(self.state_memory.memory, 500)
        else:
            mini_sample = self.state_memory.memory
        state,actions,rewards,next_states,done = zip(*mini_sample)
        self.train_step(state,actions,rewards,next_states,done)

    def train_step(self,state,next_state,action,reward,done):
        state = torch.tensor(state, dtype=torch.float32)
        next_state = torch.tensor(next_state, dtype=torch.float32)
                
        action = torch.tensor(action,dtype=torch.float32)
        reward = torch.tensor(reward,dtype=torch.float32)
        if len(action.shape) == 1:
            state = torch.unsqueeze(state, 0)   
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)

            done = (done,)
        self.optimizer.zero_grad()
        pred = self.model(state)
        target = pred.clone().detach()
     #   print(target.shape, done)
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                model_result = self.model(next_state[idx].unsqueeze(0))
                Q_new = reward[idx] + self.gamma * torch.max(model_result)
            target[idx][torch.argmax(action).item()] = Q_new
        loss = self.criterion(target, pred)
        
        loss.backward()

        nn.utils.clip_grad_norm_(self.model.parameters(),1)
        
        self.optimizer.step()
    

    def get_action(self, state):
        final_move = [0,0,0,0]
        if random.randint(0,200) < (80 - self.n_games): 
            move = random.randint(0,3)
        else:
            state_vec = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            prediction = self.model(state_vec)
            move = prediction.argmax().item()

            
        final_move[move] = 1
        return final_move