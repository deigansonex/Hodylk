# rl/mapoca_train.py
import os
import torch
import torch.optim as optim
import numpy as np
from rl.mapoca_env import MapocaEnv, ACTIONS
from rl.mapoca_model import Actor, CentralizedCritic
import torch.nn.functional as F
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

OBS_DIM = 14
TOTAL_OBS = OBS_DIM * 2
N_ACTIONS = len(ACTIONS)

def compute_returns(rewards, gamma=0.99):
    R = 0
    returns = []
    for r in reversed(rewards):
        R = r + gamma * R
        returns.insert(0, R)
    return returns

def train(episodes=500, steps_per_update=64, ppo_epochs=4, lr=3e-4):
    env = MapocaEnv(width=21, height=15, cell_size=12, max_steps=300)
    actor_h = Actor(OBS_DIM).to(device)
    actor_p = Actor(OBS_DIM).to(device)
    critic = CentralizedCritic(TOTAL_OBS).to(device)

    opt_ah = optim.Adam(actor_h.parameters(), lr=lr)
    opt_ap = optim.Adam(actor_p.parameters(), lr=lr)
    opt_cr = optim.Adam(critic.parameters(), lr=lr)

    for ep in range(episodes):
        obs_h, obs_p = env.reset()
        done = False
        ep_steps = 0
        buffer = {"joint_obs": [], "ah": [], "ap": [], "logp_h": [], "logp_p": [], "rew_h": [], "rew_p": [], "vals": [], "masks": []}
        while not done and ep_steps < env.max_steps:
            # collect rollout chunk
            for _ in range(steps_per_update):
                oh_t = torch.tensor(obs_h, dtype=torch.float32, device=device).unsqueeze(0)
                op_t = torch.tensor(obs_p, dtype=torch.float32, device=device).unsqueeze(0)
                logits_h = actor_h(oh_t); probs_h = torch.softmax(logits_h, dim=-1)
                logits_p = actor_p(op_t); probs_p = torch.softmax(logits_p, dim=-1)
                dist_h = torch.distributions.Categorical(probs_h)
                dist_p = torch.distributions.Categorical(probs_p)
                ah = int(dist_h.sample().item()); ap = int(dist_p.sample().item())
                logp_h = float(dist_h.log_prob(torch.tensor(ah, device=device)).item())
                logp_p = float(dist_p.log_prob(torch.tensor(ap, device=device)).item())

                joint_obs = np.concatenate([obs_h, obs_p]).astype(np.float32)
                with torch.no_grad():
                    val = critic(torch.tensor(joint_obs, dtype=torch.float32, device=device).unsqueeze(0)).item()

                (next_oh, next_op), (rh, rp), done, info = env.step((ah, ap))
                buffer["joint_obs"].append(joint_obs)
                buffer["ah"].append(ah); buffer["ap"].append(ap)
                buffer["logp_h"].append(logp_h); buffer["logp_p"].append(logp_p)
                buffer["rew_h"].append(rh); buffer["rew_p"].append(rp)
                buffer["vals"].append(val)
                buffer["masks"].append(0.0 if done else 1.0)

                obs_h, obs_p = next_oh, next_op
                ep_steps += 1
                if done:
                    break

            # compute returns & advantages for hunter (critic predicts hunter returns)
            returns = compute_returns(buffer["rew_h"], gamma=0.99)
            values = buffer["vals"]
            advantages = [r - v for r, v in zip(returns, values)]
            adv = torch.tensor(advantages, dtype=torch.float32, device=device)
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)

            joint_obs_b = torch.tensor(np.array(buffer["joint_obs"]), dtype=torch.float32, device=device)
            actions_h_b = torch.tensor(buffer["ah"], dtype=torch.long, device=device)
            old_logp_h = torch.tensor(buffer["logp_h"], dtype=torch.float32, device=device)

            # PPO-ish update for actor_h
            for _ in range(ppo_epochs):
                logits = actor_h(torch.tensor(np.array([o[:OBS_DIM] for o in buffer["joint_obs"]]), dtype=torch.float32, device=device))
                probs = torch.softmax(logits, dim=-1)
                dist = torch.distributions.Categorical(probs)
                new_logp = dist.log_prob(actions_h_b)
                ratio = torch.exp(new_logp - old_logp_h)
                surr1 = ratio * adv
                surr2 = torch.clamp(ratio, 0.8, 1.2) * adv
                loss_ah = -torch.min(surr1, surr2).mean()
                opt_ah.zero_grad(); loss_ah.backward(); opt_ah.step()

            # Critic update
            returns_t = torch.tensor(returns, dtype=torch.float32, device=device)
            pred_vals = critic(joint_obs_b).squeeze(-1)
            loss_c = F.mse_loss(pred_vals, returns_t)
            opt_cr.zero_grad(); loss_c.backward(); opt_cr.step()

            # For simplicity: update prey actor to maximize negative hunter advantage (zero-sum)
            # compute "prey advantage" as -adv
            adv_p = -adv
            actions_p_b = torch.tensor(buffer["ap"], dtype=torch.long, device=device)
            old_logp_p = torch.tensor(buffer["logp_p"], dtype=torch.float32, device=device)
            for _ in range(ppo_epochs):
                logits_p = actor_p(torch.tensor(np.array([o[OBS_DIM:] for o in buffer["joint_obs"]]), dtype=torch.float32, device=device))
                probs_p = torch.softmax(logits_p, dim=-1)
                dist_p = torch.distributions.Categorical(probs_p)
                new_logp_p = dist_p.log_prob(actions_p_b)
                ratio_p = torch.exp(new_logp_p - old_logp_p)
                surr1_p = ratio_p * adv_p
                surr2_p = torch.clamp(ratio_p, 0.8, 1.2) * adv_p
                loss_ap = -torch.min(surr1_p, surr2_p).mean()
                opt_ap.zero_grad(); loss_ap.backward(); opt_ap.step()

            # clear buffer
            buffer = {k: [] for k in buffer}

        if (ep+1) % 10 == 0:
            print(f"Episode {ep+1}/{episodes} steps {ep_steps}")

    os.makedirs("rl_models", exist_ok=True)
    torch.save(actor_h.state_dict(), "rl_models/actor_h.pth")
    torch.save(actor_p.state_dict(), "rl_models/actor_p.pth")
    torch.save(critic.state_dict(), "rl_models/critic.pth")
    print("Saved models to rl_models/")

train()