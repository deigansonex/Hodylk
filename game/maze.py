import random
import pygame

COLOR_WALL = (30, 30, 30)
COLOR_PATH = (240, 240, 240)

class Maze:
    def __init__(self, width, height, cell_size):
        """
        width, height — количество клеток
        cell_size — размер клетки в пикселях
        """
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        self._generate_maze()
        self._open_borders()  # 👈 вот здесь магия

    def _generate_maze(self):
        """Генерация лабиринта методом DFS."""
        stack = []
        start_row, start_col = 1, 1
        self.grid[start_row][start_col] = 0
        stack.append((start_row, start_col))

        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        while stack:
            row, col = stack[-1]
            random.shuffle(dirs)
            carved = False
            for dr, dc in dirs:
                new_r, new_c = row + dr, col + dc
                if 1 <= new_r < self.height - 1 and 1 <= new_c < self.width - 1:
                    if self.grid[new_r][new_c] == 1:
                        self.grid[row + dr // 2][col + dc // 2] = 0
                        self.grid[new_r][new_c] = 0
                        stack.append((new_r, new_c))
                        carved = True
                        break
            if not carved:
                stack.pop()

    def _open_borders(self):
        """Делает все клетки по краям проходимыми (0)."""
        for x in range(self.width):
            self.grid[0][x] = 0               # верхняя строка
            self.grid[self.height - 1][x] = 0 # нижняя строка

        for y in range(self.height):
            self.grid[y][0] = 0               # левая колонка
            self.grid[y][self.width - 1] = 0  # правая колонка

    def draw(self, screen):
        """Отрисовывает лабиринт."""
        for row in range(self.height):
            for col in range(self.width):
                x, y = col * self.cell_size, row * self.cell_size
                color = COLOR_WALL if self.grid[row][col] == 1 else COLOR_PATH
                pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))

    def is_wall(self, x, y):
        """Проверяет, является ли клетка стеной по пиксельным координатам."""
        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= row < self.height and 0 <= col < self.width:
            return self.grid[row][col] == 1
        return True  # всё вне лабиринта — стенка

    def get_free_cells(self):
        """Возвращает список координат клеток-проходов (0)."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 0:
                    yield (x, y)
