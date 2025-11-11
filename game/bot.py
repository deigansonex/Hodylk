import pygame
import random
from utils.settings import *


class Bot:
    def __init__(self, maze, start_cell=(1, 1), color=(255, 255, 0), visual_frac=0.7):
        self.maze = maze
        self.color = color
        self.cell_size = maze.cell_size
        self.speed = self.cell_size // 4
        self.visual_frac = visual_frac

        # ищем ближайшую свободную клетку
        self.grid_x, self.grid_y = self.find_nearest_free(start_cell)

        # прямоугольник для отрисовки
        self.rect = pygame.Rect(
            self.grid_x * self.cell_size,
            self.grid_y * self.cell_size,
            int(self.cell_size * self.visual_frac),
            int(self.cell_size * self.visual_frac),
        )
        self.update_rect_pos()

    def find_nearest_free(self, start_cell):
        """Ищет ближайшую свободную клетку в лабиринте от заданной"""
        sx, sy = start_cell
        if self.is_free(sx, sy):
            return sx, sy
        # Поиск BFS
        queue = [(sx, sy)]
        visited = set(queue)
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in visited and 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                    if self.is_free(nx, ny):
                        return nx, ny
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return sx, sy  # fallback

    def is_free(self, x, y):
        return 0 <= y < self.maze.height and 0 <= x < self.maze.width and self.maze.grid[y][x] == 0

    def move_direction(self, action):
        """Двигается на 1 клетку в заданном направлении (U/D/L/R/Stay)"""
        dx, dy = 0, 0
        if action == "UP": dy = -1
        elif action == "DOWN": dy = 1
        elif action == "LEFT": dx = -1
        elif action == "RIGHT": dx = 1
        elif action == "STAY": pass

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        # проверка границ и стен
        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height:
            if self.maze.grid[new_y][new_x] == 0:
                self.grid_x, self.grid_y = new_x, new_y
                self.update_rect_pos()

    def update_rect_pos(self):
        """Обновляет положение прямоугольника на экране"""
        px = self.grid_x * self.cell_size + (self.cell_size * (1 - self.visual_frac) / 2)
        py = self.grid_y * self.cell_size + (self.cell_size * (1 - self.visual_frac) / 2)
        self.rect.topleft = (px, py)

    def random_walk(self):
        """Простое случайное движение, если нет RL"""
        direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT", "STAY"])
        self.move_direction(direction)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
