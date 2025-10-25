import random
import pygame

class Collectible:
    def __init__(self, grid_x, grid_y, cell_size):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.cell_size = cell_size
        self.collected = False
        self.color = (255, 215, 0)  # золотистый

    def draw(self, surface):
        if not self.collected:
            size = int(self.cell_size * 0.75)
            offset = (self.cell_size - size) // 2
            rect = pygame.Rect(
                self.grid_x * self.cell_size + offset,
                self.grid_y * self.cell_size + offset,
                size,
                size
            )
            pygame.draw.ellipse(surface, self.color, rect)


class CollectibleManager:
    def __init__(self, maze, count=5):
        """Создаёт несколько коллектаблов только в свободных клетках лабиринта"""
        self.maze = maze
        self.cell_size = maze.cell_size
        self.collectibles = []

        # Собираем только свободные клетки (0 — путь)
        free_cells = [
            (x, y)
            for y in range(1, maze.height - 1)
            for x in range(1, maze.width - 1)
            if maze.grid[y][x] == 0
        ]

        # Если свободных клеток меньше, чем нужно — ограничим количество
        count = min(count, len(free_cells))
        random.shuffle(free_cells)

        # Берём случайные координаты из свободных клеток
        for i in range(count):
            gx, gy = free_cells[i]
            self.collectibles.append(Collectible(gx, gy, self.cell_size))

    def draw(self, surface):
        for c in self.collectibles:
            c.draw(surface)

    def check_collection(self, player_rect):
        """Проверяет, подобрал ли игрок предмет"""
        for c in self.collectibles:
            if not c.collected:
                c_rect = pygame.Rect(
                    c.grid_x * c.cell_size,
                    c.grid_y * c.cell_size,
                    c.cell_size,
                    c.cell_size
                )
                if player_rect.colliderect(c_rect):
                    c.collected = True

    def all_collected(self):
        return all(c.collected for c in self.collectibles)
