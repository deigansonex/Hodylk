import pygame
from utils.settings import TRAIL_COLOR, TRAIL_LIFETIME, TRAIL_RADIUS

class Trail:
    """
    Хранит и рисует следы: точки с временем жизни.
    Предоставляет API для доступа к координатам следов (для ИИ).
    """
    def __init__(self, lifetime=TRAIL_LIFETIME, radius=TRAIL_RADIUS, color=TRAIL_COLOR):
        self.points = []  # каждый элемент: [x, y, remaining_life]
        self.lifetime = lifetime
        self.radius = radius
        self.color = color

    def add_point(self, x, y):
        """Добавить след в позицию (x,y) с полным временем жизни."""
        self.points.append([x, y, self.lifetime])

    def update(self):
        """Уменьшить life всех следов и удалить истёкшие."""
        for p in self.points:
            p[2] -= 1
        # Оставляем только живые следы
        self.points = [p for p in self.points if p[2] > 0]

    def draw(self, screen):
        """Отрисовать все следы (полупрозрачные кружки)."""
        for x, y, life in self.points:
            alpha = int(255 * (life / self.lifetime))
            surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            rgba = (self.color[0], self.color[1], self.color[2], alpha)
            pygame.draw.circle(surf, rgba, (self.radius, self.radius), self.radius)
            screen.blit(surf, (int(x) - self.radius, int(y) - self.radius))

    def get_positions(self, recent_n=None):
        """
        Вернуть список координат следов.
        Если recent_n задан, вернуть последние recent_n точек (от старых к новым).
        """
        pts = [(p[0], p[1]) for p in self.points]
        return pts[-recent_n:] if recent_n is not None else pts

    def clear(self):
        """Очистить все следы (удобно при ресете уровня)."""
        self.points = []
