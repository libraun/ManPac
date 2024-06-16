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

        self.input_layer = nn.Linear(in_features, hidden_dim)
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim)
        self.output_layer = nn.Linear(hidden_dim, out_features)

        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x):

        x = self.input_layer(x)
        x = self.hidden_layer(x)

     #   x = self.dropout(x)
        x = self.output_layer(F.relu(x))

        return x