# rl/loader.py
import torch
import numpy as np
from rl.mapoca_model import Actor
from rl.mapoca_env import ACTIONS

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OBS_DIM = 14

def load_actors(actor_h_path="rl_models/actor_h.pth", actor_p_path="rl_models/actor_p.pth"):
    actor_h = Actor(OBS_DIM).to(device); actor_p = Actor(OBS_DIM).to(device)
    actor_h.load_state_dict(torch.load(actor_h_path, map_location=device))
    actor_p.load_state_dict(torch.load(actor_p_path, map_location=device))
    actor_h.eval(); actor_p.eval()
    return actor_h, actor_p

def actor_action(actor, obs_np):
    import torch
    obs_t = torch.tensor(obs_np, dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        logits = actor(obs_t)
        action = int(torch.argmax(logits, dim=-1).item())
    return action  # integer index into ACTIONS
