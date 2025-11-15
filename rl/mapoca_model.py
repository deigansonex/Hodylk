# rl/mapoca_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class Actor(nn.Module):
    def __init__(self, obs_dim, hidden=128, n_actions=5):
        super().__init__()
        self.fc1 = nn.Linear(obs_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.logits = nn.Linear(hidden, n_actions)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.logits(x)

class CentralizedCritic(nn.Module):
    def __init__(self, total_obs_dim, hidden=256):
        super().__init__()
        self.fc1 = nn.Linear(total_obs_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.v   = nn.Linear(hidden, 1)

    def forward(self, joint_obs):
        x = F.relu(self.fc1(joint_obs))
        x = F.relu(self.fc2(x))
        return self.v(x).squeeze(-1)
