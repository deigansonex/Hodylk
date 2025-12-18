import pygame
import math
import random
import torch
import torch.nn as nn
import os

# =====================================================
# НАСТРОЙКИ
# =====================================================
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 600
CELL_SIZE = 40
GRID_W, GRID_H = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE

MODEL_FILE = "hunter.pth"
TIME_LIMIT = 60
NUM_ITEMS = 5
VIEW_RADIUS = 2

# =====================================================
# ИНИЦИАЛИЗАЦИЯ
# =====================================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Охотник и Жертва")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# =====================================================
# ЗАГРУЗКА ИЗОБРАЖЕНИЙ
# =====================================================
menu_bg = pygame.image.load("assets/menu_bg.png").convert()
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

player_img = pygame.image.load("assets/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (CELL_SIZE, CELL_SIZE))

hunter_img = pygame.image.load("assets/hunter.png").convert_alpha()
hunter_img = pygame.transform.scale(hunter_img, (CELL_SIZE, CELL_SIZE))

item_img = pygame.image.load("assets/item.png").convert_alpha()
item_img = pygame.transform.scale(item_img, (CELL_SIZE, CELL_SIZE))

# =====================================================
# ЛАБИРИНТ
# =====================================================
maze = [[0]*GRID_W for _ in range(GRID_H)]
for i in range(GRID_W):
    maze[i][0] = maze[i][-1] = maze[0][i] = maze[-1][i] = 1
for i in range(3, 12):
    maze[5][i] = 1
    maze[9][i] = 1

# =====================================================
# BOT
# =====================================================
class Bot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
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
            gx, gy = new_rect.x // CELL_SIZE, new_rect.y // CELL_SIZE
            if maze[gy][gx] == 0:
                self.rect = new_rect
            else:
                self.hit_wall = True
        else:
            self.hit_wall = True

# =====================================================
# Q-NET И АГЕНТ
# =====================================================
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

class Agent:
    def __init__(self, state_size):
        self.q = QNet(state_size)
        self.q.load_state_dict(torch.load(MODEL_FILE))
        self.q.eval()

    def get_action(self, state):
        with torch.no_grad():
            return torch.argmax(self.q(torch.FloatTensor(state))).item()

# =====================================================
# СОСТОЯНИЕ ИИ
# =====================================================
def get_state(hunter, player):
    gx, gy = hunter.rect.x // CELL_SIZE, hunter.rect.y // CELL_SIZE
    state = []

    for dy in range(-VIEW_RADIUS, VIEW_RADIUS+1):
        for dx in range(-VIEW_RADIUS, VIEW_RADIUS+1):
            x, y = gx+dx, gy+dy
            if 0 <= x < GRID_W and 0 <= y < GRID_H:
                state.append(maze[y][x])
            else:
                state.append(1)

    state.append((player.rect.x - hunter.rect.x) / SCREEN_WIDTH)
    state.append((player.rect.y - hunter.rect.y) / SCREEN_HEIGHT)
    state.append(1 if hunter.hit_wall else 0)
    return state

# =====================================================
# КНОПКИ
# =====================================================
def draw_button(text, rect):
    pygame.draw.rect(screen, (40,40,40), rect)
    pygame.draw.rect(screen, (200,200,200), rect, 2)
    txt = font.render(text, True, (255,255,255))
    screen.blit(txt, txt.get_rect(center=rect.center))

# =====================================================
# МЕНЮ
# =====================================================
def main_menu():
    start_btn = pygame.Rect(200, 260, 200, 60)
    exit_btn = pygame.Rect(200, 340, 200, 60)

    while True:
        screen.blit(menu_bg, (0,0))
        draw_button("Начать игру", start_btn)
        draw_button("Выход", exit_btn)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn.collidepoint(event.pos):
                    return
                if exit_btn.collidepoint(event.pos):
                    pygame.quit(); exit()

        pygame.display.flip()
        clock.tick(30)

# =====================================================
# ЭКРАН КОНЦА
# =====================================================
def end_screen(result):
    menu_btn = pygame.Rect(200, 300, 200, 60)
    exit_btn = pygame.Rect(200, 380, 200, 60)

    while True:
        screen.fill((0,0,0))

        title = "ПОБЕДА!" if result == "win" else "ПОРАЖЕНИЕ"
        color = (0,255,0) if result == "win" else (255,0,0)
        text = font.render(title, True, color)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH//2, 200)))

        draw_button("В меню", menu_btn)
        draw_button("Выход", exit_btn)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    return
                if exit_btn.collidepoint(event.pos):
                    pygame.quit(); exit()

        pygame.display.flip()
        clock.tick(30)

# =====================================================
# ИГРА
# =====================================================
def game_loop():
    hunter = Bot(40, 40)
    player = Bot(520, 520)
    agent = Agent((2*VIEW_RADIUS+1)**2 + 3)

    items = []
    while len(items) < NUM_ITEMS:
        x, y = random.randint(1, GRID_W-2), random.randint(1, GRID_H-2)
        if maze[y][x] == 0:
            items.append(pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    start_time = pygame.time.get_ticks()

    while True:
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        time_left = max(TIME_LIMIT - elapsed, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()

        keys = pygame.key.get_pressed()
        action = 0
        if keys[pygame.K_w]: action = 1
        if keys[pygame.K_s]: action = 2
        if keys[pygame.K_a]: action = 3
        if keys[pygame.K_d]: action = 4
        player.move(action)

        hunter.move(agent.get_action(get_state(hunter, player)))

        if math.dist(hunter.rect.center, player.rect.center) < 20:
            return "lose"

        for item in items[:]:
            if player.rect.colliderect(item):
                items.remove(item)

        if not items:
            return "win"

        if time_left == 0:
            return "lose"

        screen.fill((0,0,0))
        for y,row in enumerate(maze):
            for x,val in enumerate(row):
                if val == 1:
                    pygame.draw.rect(screen, (90,90,90),
                        (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for item in items:
            screen.blit(item_img, item)

        screen.blit(player_img, player.rect)
        screen.blit(hunter_img, hunter.rect)

        timer = font.render(f"Time: {time_left}", True, (255,255,255))
        screen.blit(timer, (10,10))

        pygame.display.flip()
        clock.tick(10)

# =====================================================
# ЗАПУСК
# =====================================================
while True:
    main_menu()
    result = game_loop()
    end_screen(result)
