import pygame
from utils.settings import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Game Prototype")
clock = pygame.time.Clock()

# Игрок — просто квадрат
player = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PLAYER_SIZE, PLAYER_SIZE)

# Цвета
BG_COLOR = (30, 30, 30)
PLAYER_COLOR = (0, 200, 255)

# Основной цикл
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        player.y += PLAYER_SPEED
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED

    # Ограничение границ экрана
    player.x = max(0, min(player.x, SCREEN_WIDTH - PLAYER_SIZE))
    player.y = max(0, min(player.y, SCREEN_HEIGHT - PLAYER_SIZE))

    # Отрисовка
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    pygame.display.flip()

pygame.quit()
