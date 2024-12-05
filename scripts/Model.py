import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):

    def __init__(self, in_features: int, 
                 out_features: int, 
                 hidden_dim: int):
        
        super(Model, self).__init__()
    
        self.conv1 = nn.Conv2d(in_channels=5, out_channels=16, kernel_size=3, stride=1,padding=1)
        # Convolutional layer (output channels = 32)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1,padding=1)
        # Fully connected layer (after flattening the feature map)
        self.fc1 = nn.Linear(32 * 32 * 32, hidden_dim)

        self.fc2 = nn.Linear(hidden_dim, out_features)  # Adjust size based on your H and W

        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))

        x = self.fc1(x.view(x.size(0),-1))
        x = self.fc2(F.sigmoid(x))

        return x