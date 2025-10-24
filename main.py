import pygame
from utils.settings import *
from game.player import Player
from game.maze import Maze

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Maze Collision Demo")
clock = pygame.time.Clock()

maze = Maze()
player = Player(TILE_SIZE, TILE_SIZE)

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.handle_input(maze)
    player.update_trails()

    screen.fill((0, 0, 0))
    maze.draw(screen)
    player.draw(screen)

    pygame.display.flip()

pygame.quit()
