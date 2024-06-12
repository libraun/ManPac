import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class Model(nn.Module):

    def __init__(self, in_features: int, 
                 out_features: int, 
                 hidden_dim: int, 
                 dropout: float = 0.1):
        
        super(Model, self).__init__()

        self.layer1 = nn.Linear(in_features, hidden_dim)
        self.layer2 = nn.Linear(hidden_dim, out_features)

        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x):

        x = self.layer1(x)
        x = self.dropout(x)
        x = self.layer2(F.relu(x))

        return x