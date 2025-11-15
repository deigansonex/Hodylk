# rl/mapoca_env.py
import numpy as np
import random
from collections import deque
from game.maze import Maze
from game.bot import Bot

ACTIONS = ["STAY", "UP", "DOWN", "LEFT", "RIGHT"]

class MapocaEnv:
    def __init__(self, width=33, height=25, cell_size=24, trail_len=20, max_steps=500):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.maze = Maze(width=width, height=height, cell_size=cell_size)
        # hunter in bottom-right, prey in top-left by default
        self.hunter = Bot(self.maze, start_cell=(width-2, height-2), color=(255,80,80), visual_frac=0.6)
        self.prey = Bot(self.maze, start_cell=(1,1), color=(50,180,255), visual_frac=0.6)
        self.trail_len = trail_len
        self.trails = deque(maxlen=trail_len)
        self.timestep = 0
        self.max_steps = max_steps

    def reset(self):
        self.maze = Maze(width=self.width, height=self.height, cell_size=self.cell_size)
        self.hunter = Bot(self.maze, start_cell=(self.width-2, self.height-2), visual_frac=0.6)
        self.prey = Bot(self.maze, start_cell=(1,1), visual_frac=0.6)
        self.trails.clear()
        self.timestep = 0
        return self.get_obs()

    def step(self, actions):
        """
        actions: tuple/list (ah_index, ap_index) -> indices in ACTIONS
        returns: (obs_h, obs_p), (rew_h, rew_p), done, info
        """
        self.timestep += 1
        ah = ACTIONS[int(actions[0])]
        ap = ACTIONS[int(actions[1])]

        self.hunter.apply_action(ah)
        self.prey.apply_action(ap)
        # prey leaves a trail
        self.trails.append((self.prey.rect.centerx, self.prey.rect.centery, self.timestep))

        # compute reward (simple zero-sum shaping)
        hx = self.hunter.rect.centerx / self.cell_size
        hy = self.hunter.rect.centery / self.cell_size
        px = self.prey.rect.centerx / self.cell_size
        py = self.prey.rect.centery / self.cell_size
        dist = abs(hx - px) + abs(hy - py)

        done = False
        if self.hunter.rect.colliderect(self.prey.rect):
            reward_h = +10.0
            reward_p = -10.0
            done = True
        else:
            # shaping: smaller dist => hunter better
            reward_h = -0.01 * dist
            reward_p = +0.01 * dist

        if self.timestep >= self.max_steps:
            done = True
            reward_h -= 5.0
            reward_p += 5.0

        obs = self.get_obs()
        info = {"timestep": self.timestep}
        return obs, (reward_h, reward_p), done, info

    def _raycast(self, x_px, y_px, angle_rad, max_dist=None):
        if max_dist is None:
            max_dist = max(self.width, self.height) * self.cell_size
        step = max(1.0, self.cell_size * 0.2)
        total = 0.0
        cx, cy = x_px, y_px
        while total < max_dist:
            cx += step * np.cos(angle_rad)
            cy += step * np.sin(angle_rad)
            total += step
            if self.maze.is_wall(int(cx), int(cy)):
                return total / max_dist
        return 1.0

    def _get_obs_agent(self, agent, other_agent):
        norm = max(self.width, self.height)
        dx_cells = (other_agent.rect.centerx - agent.rect.centerx) / self.cell_size
        dy_cells = (other_agent.rect.centery - agent.rect.centery) / self.cell_size
        rel = np.array([dx_cells / norm, dy_cells / norm], dtype=np.float32)

        angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
        rc = [self._raycast(agent.rect.centerx, agent.rect.centery, a) for a in angles]
        rc = np.array(rc, dtype=np.float32)

        trail_feats = np.zeros(4, dtype=np.float32)
        if len(self.trails) > 0:
            recent = list(self.trails)[-4:]
            for i, (tx, ty, t) in enumerate(recent):
                relx = (tx - agent.rect.centerx) / (self.cell_size * norm)
                rely = (ty - agent.rect.centery) / (self.cell_size * norm)
                trail_feats[i] = np.hypot(relx, rely)
        obs = np.concatenate([rel, rc, trail_feats]).astype(np.float32)
        return obs

    def get_obs(self):
        return (self._get_obs_agent(self.hunter, self.prey),
                self._get_obs_agent(self.prey, self.hunter))

    def sample_action(self):
        return (random.randrange(len(ACTIONS)), random.randrange(len(ACTIONS)))
