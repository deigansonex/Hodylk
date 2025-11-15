import pygame
import random

class Bot:
    def __init__(self, maze, start_cell, color=(255, 0, 0), speed=1.3, visual_frac=0.6):
        self.maze = maze
        self.cell_size = maze.cell_size
        self.color = color
        self.speed = speed

        self.size = int(self.cell_size * visual_frac)

        gx, gy = start_cell
        x = gx * self.cell_size + (self.cell_size - self.size) // 2
        y = gy * self.cell_size + (self.cell_size - self.size) // 2

        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.target_dx = 0
        self.target_dy = 0
        self.change_dir_timer = 0

    # ---------------------------------------------------------

    def _collides(self, rect):
        points = [
            rect.topleft,
            rect.topright,
            rect.bottomleft,
            rect.bottomright
        ]
        for x, y in points:
            if self.maze.is_wall(x, y):
                return True
        return False

    # ---------------------------------------------------------

    def random_walk(self):
        if self.change_dir_timer <= 0:
            self.change_dir_timer = random.randint(20, 40)
            dirs = [(1,0), (-1,0), (0,1), (0,-1), (0,0)]
            self.target_dx, self.target_dy = random.choice(dirs)

        self.change_dir_timer -= 1

        dx = self.target_dx * self.speed
        dy = self.target_dy * self.speed

        new_x = self.rect.move(dx, 0)
        if not self._collides(new_x):
            self.rect = new_x

        new_y = self.rect.move(0, dy)
        if not self._collides(new_y):
            self.rect = new_y

    # ---------------------------------------------------------

    def apply_action(self, action):
        """
        0 — стоять
        1 — вверх
        2 — вниз
        3 — влево
        4 — вправо
        """
        if action == 0:
            dx = 0; dy = 0
        elif action == 1:
            dx = 0; dy = -self.speed
        elif action == 2:
            dx = 0; dy = self.speed
        elif action == 3:
            dx = -self.speed; dy = 0
        elif action == 4:
            dx = self.speed; dy = 0
        else:
            return

        new_x = self.rect.move(dx, 0)
        if not self._collides(new_x):
            self.rect = new_x

        new_y = self.rect.move(0, dy)
        if not self._collides(new_y):
            self.rect = new_y

    # ---------------------------------------------------------

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
