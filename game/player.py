import pygame
from utils.settings import *
from game.trail import Trail

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.color = (0, 200, 255)
        self.trail = Trail()  # объект управления следами

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Ограничение по экрану
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - PLAYER_SIZE))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - PLAYER_SIZE))

    def update(self):
        # Добавляем точку следа в центр игрока и обновляем следы
        cx, cy = self.rect.centerx, self.rect.centery
        self.trail.add_point(cx, cy)
        self.trail.update()

    def draw(self, screen):
        # Рисуем следы, затем игрока поверх
        self.trail.draw(screen)
        pygame.draw.rect(screen, self.color, self.rect)
