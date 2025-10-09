import pygame
from utils.settings import *
from game.player import Player

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Game Prototype")
clock = pygame.time.Clock()

player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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

    player.handle_input()
    player.update()

    screen.fill((30, 30, 30))
    player.draw(screen)
    pygame.display.flip()

pygame.quit()
