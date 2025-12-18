import pygame
import random
import math
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import os

# Параметры игры
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
CELL_SIZE = 40
GRID_W, GRID_H = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE
EPISODES = 3000
MAX_STEPS = 200
MODEL_FILE = "hunter.pth"
VIEW_RADIUS = 2  # радиус видимости охотника (5x5 клеток)

# Лабиринт
maze = [[0]*GRID_W for _ in range(GRID_H)]
for i in range(GRID_W):
    maze[i][0] = maze[i][-1] = maze[0][i] = maze[-1][i] = 1
for i in range(3, 12):
    maze[5][i] = 1
    maze[9][i] = 1

# Bot
class Bot:
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.color = color
        self.hit_wall = False

    def move(self, action):
        dx, dy = 0, 0
        if action == 1: dy = -CELL_SIZE
        if action == 2: dy = CELL_SIZE
        if action == 3: dx = -CELL_SIZE
        if action == 4: dx = CELL_SIZE

        new_rect = self.rect.move(dx, dy)
        self.hit_wall = False
        if 0 <= new_rect.x < SCREEN_WIDTH and 0 <= new_rect.y < SCREEN_HEIGHT:
            gx, gy = new_rect.x//CELL_SIZE, new_rect.y//CELL_SIZE
            if maze[gy][gx] == 0:
                self.rect = new_rect
            else:
                self.hit_wall = True
        else:
            self.hit_wall = True

# Q-сеть
class QNet(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.out = nn.Linear(128, 5)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.out(x)

# Агент
class Agent:
    def __init__(self, state_size):
        self.q = QNet(state_size)
        self.target = QNet(state_size)
        self.target.load_state_dict(self.q.state_dict())
        self.mem = deque(maxlen=5000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.optimizer = optim.Adam(self.q.parameters(), lr=0.001)
        self.batch_size = 128

        if os.path.exists(MODEL_FILE):
            self.q.load_state_dict(torch.load(MODEL_FILE))
            self.q.eval()
            self.target.load_state_dict(self.q.state_dict())
            print("Модель загружена, продолжаем обучение...")

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0,4)
        with torch.no_grad():
            return torch.argmax(self.q(torch.FloatTensor(state))).item()

    def train(self):
        if len(self.mem) < self.batch_size:
            return
        batch = random.sample(self.mem, self.batch_size)
        states = torch.FloatTensor([b[0] for b in batch])
        actions = torch.LongTensor([b[1] for b in batch]).unsqueeze(1)
        rewards = torch.FloatTensor([b[2] for b in batch])
        next_states = torch.FloatTensor([b[3] for b in batch])
        dones = torch.FloatTensor([b[4] for b in batch])

        q_vals = self.q(states).gather(1, actions).squeeze()
        with torch.no_grad():
            target_q = rewards + (1 - dones) * self.gamma * torch.max(self.target(next_states), 1)[0]
        loss = nn.MSELoss()(q_vals, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        self.epsilon *= self.epsilon_decay

# Получение состояния (локальная карта + dx/dy + столкновение)
def get_state(hunter, prey):
    gx, gy = hunter.rect.x // CELL_SIZE, hunter.rect.y // CELL_SIZE
    state = []
    for dy in range(-VIEW_RADIUS, VIEW_RADIUS+1):
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS+1):
            x, y = gx+dx, gy+dy
            if 0 <= x < GRID_W and 0 <= y < GRID_H:
                state.append(maze[y][x])
            else:
                state.append(1)
    state.append((prey.rect.x - hunter.rect.x)/SCREEN_WIDTH)
    state.append((prey.rect.y - hunter.rect.y)/SCREEN_HEIGHT)
    state.append(1 if hunter.hit_wall else 0)
    return state

# Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

state_size = (2*VIEW_RADIUS+1)**2 + 3
agent = Agent(state_size)

# Основной цикл обучения
for episode in range(1, EPISODES+1):
    hunter = Bot(40, 40, (255,0,0))
    prey = Bot(520, 520, (0,255,0))
    done = False
    steps = 0
    prev_dist = math.dist(hunter.rect.center, prey.rect.center)

    while not done and steps < MAX_STEPS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        state = get_state(hunter, prey)
        action = agent.get_action(state)
        hunter.move(action)

        # Жертва случайная
        prey.move(random.randint(0,4))

        # Награда
        dist = math.dist(hunter.rect.center, prey.rect.center)
        reward = prev_dist - dist  # приближение к цели
        if hunter.hit_wall:
            reward -= 1  # штраф за столкновение
        if dist < 20:
            reward += 10
            done = True
        prev_dist = dist

        next_state = get_state(hunter, prey)
        agent.mem.append((state, action, reward, next_state, done))
        agent.train()

        # Отрисовка
        screen.fill((0,0,0))
        for y,row in enumerate(maze):
            for x,val in enumerate(row):
                if val==1:
                    pygame.draw.rect(screen, (100,100,100),(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, hunter.color, hunter.rect)
        pygame.draw.rect(screen, prey.color, prey.rect)
        ep_text = font.render(f"Episode: {episode}", True, (255,255,255))
        step_text = font.render(f"Step: {steps}", True, (255,255,255))
        screen.blit(ep_text,(10,10))
        screen.blit(step_text,(10,30))
        pygame.display.flip()
        clock.tick(30)
        steps += 1

    # Обновление target-сети каждые 20 эпизодов
    if episode % 20 == 0:
        agent.target.load_state_dict(agent.q.state_dict())

    # Сохраняем модель каждый эпизод
    torch.save(agent.q.state_dict(), MODEL_FILE)
