import pygame
from utils.settings import *
from game.player import Player
from game.maze import Maze
from game.collectibles import CollectibleManager


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Maze Collision Demo")
clock = pygame.time.Clock()

maze = Maze(width=31, height=31, cell_size=20)
collectibles = CollectibleManager(maze, count=7)
player = Player(TILE_SIZE, TILE_SIZE)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.handle_input(maze)
    player.update_trails()

    player_rect = player.rect


    # Проверка сбора предметов
    collectibles.check_collection(player_rect)

    # Проверка победы
    if collectibles.all_collected():
        print("🎉 Победа! Все предметы собраны!")
        running = False

    screen.fill((0, 0, 0))
    maze.draw(screen)


    # debug: нарисовать точки в центрах всех свободных ячеек
    def debug_draw_free_cells(surface, maze):
        for y in range(maze.height):
            for x in range(maze.width):
                if maze.grid[y][x] == 0:
                    cx = x * maze.cell_size + maze.cell_size // 2
                    cy = y * maze.cell_size + maze.cell_size // 2
                    pygame.draw.circle(surface, (0, 255, 0), (cx, cy), 3)


    # в основном цикле отрисовки (после maze.draw(screen))
    debug_draw_free_cells(screen, maze)

    collectibles.draw(screen)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
