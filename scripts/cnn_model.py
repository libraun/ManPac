import torch.nn as nn
import torch.nn.functional as F

class CNNModel(nn.Module):

    def __init__(self, in_features: int, 
                 out_features: int, 
                 hidden_dim: int):
        
        super(CNNModel, self).__init__()

        # Lower output channels for cnn1 tend to work better (32 is arbitrary)
        self.cnn1 = nn.Conv2d(in_channels=in_features, out_channels=32, kernel_size=3, stride=1,padding=1)
        # Want to remove extraneous output channels
        self.cnn2 = nn.Conv2d(in_channels=32, out_channels=1, kernel_size=3, stride=1,padding=1)

        # Input shape for fc1 is height * width
        self.fc1 = nn.Linear(32 * 32, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, out_features)  

        self.activation = nn.Tanh()

    def forward(self, x):
        x = self.activation(self.cnn1(x))
        x = self.activation(self.cnn2(x))
        
        # Remove the batch dimension of CNN output
        x = self.fc1(x.view(x.size(0),-1))
        x = self.fc2(self.activation(x))

        return x