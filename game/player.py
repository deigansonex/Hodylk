import pygame
from utils.settings import *

class Player:
    def __init__(self, maze, start_cell=(1, 1)):
        """
        maze — объект Maze
        start_cell — координаты клетки (x, y) в сетке, где появится игрок
        """
        self.cell_size = maze.cell_size

        # Размер игрока = 60% от размера клетки, чтобы он помещался
        self.size = int(self.cell_size * 0.6)

        # Центрируем игрока в клетке
        grid_x, grid_y = start_cell
        x = grid_x * self.cell_size + (self.cell_size - self.size) // 2
        y = grid_y * self.cell_size + (self.cell_size - self.size) // 2

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.color = (0, 200, 255)
        self.trails = []
        self.speed = PLAYER_SPEED  # скорость зависит от масштаба

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = self.speed

        # Проверяем столкновения по X
        new_rect_x = self.rect.move(dx, 0)
        if not self._collides_with_walls(new_rect_x, maze):
            self.rect = new_rect_x

        # Проверяем столкновения по Y
        new_rect_y = self.rect.move(0, dy)
        if not self._collides_with_walls(new_rect_y, maze):
            self.rect = new_rect_y

    def _collides_with_walls(self, rect, maze):
        """Проверяем, пересекается ли прямоугольник игрока со стенами лабиринта."""
        points = [
            rect.topleft,
            rect.topright,
            rect.bottomleft,
            rect.bottomright
        ]
        for (x, y) in points:
            if maze.is_wall(x, y):
                return True
        return False

    def update_trails(self):
        """Добавляет и обновляет следы игрока."""
        self.trails.append([self.rect.centerx, self.rect.centery, 60])  # 60 кадров живёт
        for t in self.trails:
            t[2] -= 1
        self.trails = [t for t in self.trails if t[2] > 0]

    def draw(self, screen):
        """Отрисовывает следы и самого игрока."""
        for x, y, lifetime in self.trails:
            alpha = int(255 * (lifetime / 60))
            color = (100, 200, 255, alpha)
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (4, 4), 4)
            screen.blit(surf, (x - 4, y - 4))

        pygame.draw.rect(screen, self.color, self.rect)
