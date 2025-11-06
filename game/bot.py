import pygame
import math
import random
from utils.settings import *

class Bot:
    def __init__(self, maze, start_cell=(1, 1)):
        self.maze = maze
        self.cell_size = maze.cell_size
        self.color = (255, 80, 80)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED * 0.8  # немного медленнее игрока
        self.rect = pygame.Rect(start_cell[0] * self.cell_size, start_cell[1] * self.cell_size, self.size, self.size)
        self.target = None

    def update(self, maze, player):
        """Двигается к игроку, используя его следы"""
        self._choose_target(player)

        if self.target:
            tx, ty = self.target
        else:
            # fallback: идёт к текущему положению игрока
            tx, ty = player.rect.center

        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist

        # Попытка сдвига
        new_rect = self.rect.move(dx * self.speed, dy * self.speed)
        if not self._collides_with_walls(new_rect, maze):
            self.rect = new_rect
        else:
            # если упёрся — слегка меняет направление
            self.rect = self.rect.move(random.choice([-1, 1]) * self.speed, random.choice([-1, 1]) * self.speed)

    def _choose_target(self, player):
        """Выбирает ближайший свежий след"""
        visible_trails = [t for t in player.trails if t[2] > TRAIL_LIFETIME * 0.3]
        if visible_trails:
            visible_trails.sort(key=lambda t: t[2])  # идёт к самому свежему
            self.target = (visible_trails[0][0], visible_trails[0][1])
        else:
            self.target = player.rect.center

    def _collides_with_walls(self, rect, maze):
        points = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
        for (x, y) in points:
            if maze.is_wall(x, y):
                return True
        return False

    def caught_player(self, player):
        """Проверяет, догнал ли игрока"""
        return self.rect.colliderect(player.rect)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
