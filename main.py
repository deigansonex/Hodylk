import pygame
from utils.settings import *
from game.player import Player
from game.maze import Maze
from game.collectibles import CollectibleManager

def start_new_game():
    """Функция для сброса и начала новой игры"""
    maze = Maze(width=33, height=25, cell_size=24)
    player = Player(maze, start_cell=(1, 1))
    collectibles = CollectibleManager(maze, count=10, visual_fraction=0.6)
    start_ticks = pygame.time.get_ticks()
    return maze, player, collectibles, start_ticks


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Maze Collision Demo")
clock = pygame.time.Clock()

# --- Первая инициализация ---
maze, player, collectibles, start_ticks = start_new_game()
TOTAL_TIME = 60  # секунд
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 96)

game_over = False
win = False
fade_alpha = 0

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if not game_over:
        # --- ДВИЖЕНИЕ И ПРОВЕРКИ ---
        player.handle_input(maze)
        player.update_trails()
        player_rect = player.rect

        collectibles.check_collection(player_rect)

        # Проверка победы
        if collectibles.all_collected():
            win = True
            game_over = True
            end_message = "🎉 Победа! Все предметы собраны!"

        # Проверка времени
        seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
        time_left = max(0, TOTAL_TIME - seconds_passed)
        if time_left <= 0:
            win = False
            game_over = True
            end_message = "⏰ Время вышло! Поражение!"

        # --- ОТРИСОВКА ---
        screen.fill((0, 0, 0))
        maze.draw(screen)
        collectibles.draw(screen)
        player.draw(screen)

        # Таймер
        timer_text = font.render(f"Time: {int(time_left)}", True, (227, 34, 60))
        screen.blit(timer_text, (10, 10))

    else:
        # --- ЭКРАН КОНЦА ИГРЫ ---
        fade_alpha = min(fade_alpha + 5, 180)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(fade_alpha)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        text_color = (80, 255, 80) if win else (255, 80, 80)
        text = large_font.render("ПОБЕДА!" if win else "ПОРАЖЕНИЕ!", True, text_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(text, text_rect)

        sub_text = font.render("Нажмите R, чтобы сыграть снова", True, (220, 220, 220))
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        screen.blit(sub_text, sub_rect)

        # Нажатие ESC для выхода
        if keys[pygame.K_ESCAPE]:
            running = False

        # Нажатие R для перезапуска
        if keys[pygame.K_r]:
            maze, player, collectibles, start_ticks = start_new_game()
            game_over = False
            fade_alpha = 0
            win = False

    pygame.display.flip()

pygame.quit()
