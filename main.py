import pygame
from utils.settings import *
from game.player import Player
from game.maze import Maze
from game.collectibles import CollectibleManager

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Maze Collision Demo")
clock = pygame.time.Clock()

# --- ИНИЦИАЛИЗАЦИЯ ИГРЫ ---
maze = Maze(width=33, height=25, cell_size=24)
player = Player(maze, start_cell=(1, 1))
collectibles = CollectibleManager(maze, count=10, visual_fraction=0.6)

# --- ТАЙМЕР ---
TOTAL_TIME = 120  # секунд
start_ticks = pygame.time.get_ticks()  # время начала в миллисекундах

font = pygame.font.Font(None, 36)  # шрифт для отображения текста

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- ОБНОВЛЕНИЕ СОСТОЯНИЯ ---
    player.handle_input(maze)
    player.update_trails()
    player_rect = player.rect

    collectibles.check_collection(player_rect)

    # --- ПРОВЕРКА ПОБЕДЫ ---
    if collectibles.all_collected():
        print("🎉 Победа! Все предметы собраны!")
        running = False

    # --- ПРОВЕРКА ВРЕМЕНИ ---
    seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
    time_left = max(0, TOTAL_TIME - seconds_passed)

    if time_left <= 0:
        print("⏰ Время вышло! Поражение!")
        running = False

    # --- ОТРИСОВКА ---
    screen.fill((0, 0, 0))
    maze.draw(screen)
    collectibles.draw(screen)
    player.draw(screen)

    # Текст таймера
    timer_text = font.render(f"Time: {int(time_left)}", True, (227, 34, 60))
    screen.blit(timer_text, (10, 10))

    pygame.display.flip()

pygame.quit()
