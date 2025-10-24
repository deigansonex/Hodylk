import pygame
from utils.settings import *

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = (0, 200, 255)
        self.trails = []

    def handle_input(self, maze):
        keys = pygame.key.get_pressed()

        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = PLAYER_SPEED

        # проверяем столкновения по X
        new_rect_x = self.rect.move(dx, 0)
        if not self._collides_with_walls(new_rect_x, maze):
            self.rect = new_rect_x

        # проверяем столкновения по Y
        new_rect_y = self.rect.move(0, dy)
        if not self._collides_with_walls(new_rect_y, maze):
            self.rect = new_rect_y

    def _collides_with_walls(self, rect, maze):
        """Проверяем, пересекается ли прямоугольник игрока со стенами лабиринта."""
        # Проверим четыре угла прямоугольника
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
        self.trails.append([self.rect.centerx, self.rect.centery, TRAIL_LIFETIME])
        for t in self.trails:
            t[2] -= 1
        self.trails = [t for t in self.trails if t[2] > 0]

    def draw(self, screen):
        # следы
        for x, y, lifetime in self.trails:
            alpha = int(255 * (lifetime / TRAIL_LIFETIME))
            color = (TRAIL_COLOR[0], TRAIL_COLOR[1], TRAIL_COLOR[2], alpha)
            surf = pygame.Surface((TRAIL_RADIUS * 2, TRAIL_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (TRAIL_RADIUS, TRAIL_RADIUS), TRAIL_RADIUS)
            screen.blit(surf, (x - TRAIL_RADIUS, y - TRAIL_RADIUS))
        # игрок
        pygame.draw.rect(screen, self.color, self.rect)
