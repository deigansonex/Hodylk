import random
import pygame
from utils.settings import *

class Maze:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self._generate_maze()

    def _generate_maze(self):
        # Алгоритм: DFS
        stack = []
        start_row, start_col = 1, 1
        self.grid[start_row][start_col] = 0
        stack.append((start_row, start_col))

        # Варианты направлений (вверх, вниз, влево, вправо)
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        while stack:
            row, col = stack[-1]
            random.shuffle(dirs)
            carved = False
            for dr, dc in dirs:
                new_r, new_c = row + dr, col + dc
                if 1 <= new_r < MAZE_ROWS - 1 and 1 <= new_c < MAZE_COLS - 1:
                    if self.grid[new_r][new_c] == 1:
                        # Разрушаем стену между текущей и новой клеткой
                        self.grid[row + dr // 2][col + dc // 2] = 0
                        self.grid[new_r][new_c] = 0
                        stack.append((new_r, new_c))
                        carved = True
                        break
            if not carved:
                stack.pop()

    def draw(self, screen):
        for row in range(MAZE_ROWS):
            for col in range(MAZE_COLS):
                x, y = col * TILE_SIZE, row * TILE_SIZE
                color = COLOR_WALL if self.grid[row][col] == 1 else COLOR_PATH
                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    def is_wall(self, x, y):
        """Проверяет, является ли клетка по координатам стеной."""
        col = x // TILE_SIZE
        row = y // TILE_SIZE
        # Проверяем границы массива
        if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
            return self.grid[row][col] == 1
        return True  # всё вне лабиринта — считается стеной
