import numpy as np
import random

ACTIONS = ['up', 'down', 'left', 'right']
ACTION_TO_DELTA = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}

class QLearningAgent:
    def __init__(self, name, maze, learning_rate=0.1, discount=0.9, epsilon=0.2):
        self.name = name
        self.maze = maze
        self.alpha = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.q_table = {}
        self.position = (1, 1)

    def set_start(self, pos):
        self.position = pos

    def get_state(self, other_pos):
        """Состояние: относительное положение другого агента"""
        dx = np.sign(other_pos[0] - self.position[0])
        dy = np.sign(other_pos[1] - self.position[1])
        return (self.position[0], self.position[1], dx, dy)

    def choose_action(self, state):
        """ε-жадная стратегия"""
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(ACTIONS)
        return max(self.q_table[state], key=self.q_table[state].get)

    def step(self, action):
        """Совершает шаг в лабиринте"""
        dx, dy = ACTION_TO_DELTA[action]
        new_x = self.position[0] + dx
        new_y = self.position[1] + dy
        # если это стена — остаётся на месте
        if self.maze.grid[new_y][new_x] == 1:
            return self.position
        self.position = (new_x, new_y)
        return self.position

    def update_q(self, state, action, reward, next_state):
        """Обновление Q-таблицы"""
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in ACTIONS}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in ACTIONS}

        best_next = max(self.q_table[next_state].values())
        old_value = self.q_table[state][action]
        self.q_table[state][action] = old_value + self.alpha * (reward + self.gamma * best_next - old_value)

def train_zero_sum(maze, episodes=1000, max_steps=200):
    hunter = QLearningAgent("Hunter", maze)
    prey = QLearningAgent("Prey", maze)

    for episode in range(episodes):
        hunter.set_start((maze.width - 2, maze.height - 2))
        prey.set_start((1, 1))

        for step in range(max_steps):
            state_h = hunter.get_state(prey.position)
            state_p = prey.get_state(hunter.position)

            action_h = hunter.choose_action(state_h)
            action_p = prey.choose_action(state_p)

            prev_dist = np.linalg.norm(np.array(hunter.position) - np.array(prey.position))

            hunter.step(action_h)
            prey.step(action_p)

            new_dist = np.linalg.norm(np.array(hunter.position) - np.array(prey.position))

            # награды — zero-sum
            if hunter.position == prey.position:
                reward_h = +10
                reward_p = -10
                done = True
            else:
                reward_h = (prev_dist - new_dist) * 0.5  # бонус за приближение
                reward_p = -reward_h
                done = False

            next_state_h = hunter.get_state(prey.position)
            next_state_p = prey.get_state(hunter.position)

            hunter.update_q(state_h, action_h, reward_h, next_state_h)
            prey.update_q(state_p, action_p, reward_p, next_state_p)

            if done:
                break

        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}: Hunter reward {reward_h:.2f}")

    return hunter, prey

import pickle

def save_agents(hunter, prey, path="rl_models.pkl"):
    with open(path, "wb") as f:
        pickle.dump({"hunter": hunter.q_table, "prey": prey.q_table}, f)
    print("✅ Модели сохранены:", path)

def load_agents(maze, path="rl_models.pkl"):
    with open(path, "rb") as f:
        data = pickle.load(f)
    from rl_training import QLearningAgent
    hunter = QLearningAgent("Hunter", maze)
    prey = QLearningAgent("Prey", maze)
    hunter.q_table = data["hunter"]
    prey.q_table = data["prey"]
    print("🤖 Модели загружены из", path)
    return hunter, prey

