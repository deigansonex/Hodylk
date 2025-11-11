import random
import pickle
import numpy as np

# --- Действия (влево, вправо, вверх, вниз)
ACTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]
ACTION_TO_DELTA = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


# ===============================
# Q-агент
# ===============================
class QLearningAgent:
    def __init__(self, name, maze, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.name = name
        self.maze = maze
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.position = (1, 1)  # старт по умолчанию

    # Безопасно проверяем границы
    def is_cell_free(self, pos):
        x, y = pos
        if 0 <= y < self.maze.height and 0 <= x < self.maze.width:
            return self.maze.grid[y][x] == 0
        return False

    def set_start(self, pos):
        self.position = pos

    def get_state(self, other_pos):
        """Состояние = относительное положение к другому агенту"""
        dx = other_pos[0] - self.position[0]
        dy = other_pos[1] - self.position[1]
        return (dx, dy)

    def choose_action(self, state):
        """Выбор действия по ε-greedy"""
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        self.q_table.setdefault(state, {a: 0 for a in ACTIONS})
        return max(self.q_table[state], key=self.q_table[state].get)

    def step(self, action):
        """Совершает шаг, если можно"""
        dx, dy = ACTION_TO_DELTA[action]
        new_pos = (self.position[0] + dx, self.position[1] + dy)
        if self.is_cell_free(new_pos):
            self.position = new_pos

    def update(self, state, action, reward, next_state):
        """Обновление Q-таблицы"""
        self.q_table.setdefault(state, {a: 0 for a in ACTIONS})
        self.q_table.setdefault(next_state, {a: 0 for a in ACTIONS})

        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())

        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value


# ===============================
# Обучение в zero-sum формате
# ===============================
def train_zero_sum(maze, episodes=1000, max_steps=500):
    hunter = QLearningAgent("Hunter", maze)
    prey = QLearningAgent("Prey", maze)

    for episode in range(episodes):
        # начальные позиции — гарантированно внутри лабиринта
        hunter.set_start((maze.width - 3, maze.height - 3))
        prey.set_start((2, 2))

        for step in range(max_steps):
            # состояния
            state_h = hunter.get_state(prey.position)
            state_p = prey.get_state(hunter.position)

            # действия
            action_h = hunter.choose_action(state_h)
            action_p = prey.choose_action(state_p)

            # шаги
            hunter.step(action_h)
            prey.step(action_p)

            # новое состояние
            next_state_h = hunter.get_state(prey.position)
            next_state_p = prey.get_state(hunter.position)

            # вознаграждения
            if hunter.position == prey.position:
                reward_h = +10
                reward_p = -10
            else:
                # стимулируем охотника приближаться, а жертву — удаляться
                prev_dist = abs(state_h[0]) + abs(state_h[1])
                new_dist = abs(next_state_h[0]) + abs(next_state_h[1])
                reward_h = (prev_dist - new_dist) * 0.5
                reward_p = -reward_h

            # обновление Q
            hunter.update(state_h, action_h, reward_h, next_state_h)
            prey.update(state_p, action_p, reward_p, next_state_p)

            if hunter.position == prey.position:
                break

        if episode % 100 == 0:
            print(f"Episode {episode}/{episodes}")

    return hunter, prey


# ===============================
# Сохранение / загрузка
# ===============================
def save_agents(hunter, prey, path="rl_models.pkl"):
    with open(path, "wb") as f:
        pickle.dump({"hunter": hunter.q_table, "prey": prey.q_table}, f)
    print("✅ Модели сохранены в", path)


def load_agents(maze, path="rl_models.pkl"):
    with open(path, "rb") as f:
        data = pickle.load(f)

    hunter = QLearningAgent("Hunter", maze)
    prey = QLearningAgent("Prey", maze)
    hunter.q_table = data["hunter"]
    prey.q_table = data["prey"]
    print("🤖 Модели загружены из", path)

    return hunter, prey


# ===============================
# Тест запуска обучения вручную
# ===============================
if __name__ == "__main__":
    from game.maze import Maze
    maze = Maze(width=33, height=25, cell_size=24)
    hunter, prey = train_zero_sum(maze, episodes=2000)
    save_agents(hunter, prey)
