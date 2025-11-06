import pygame
from rl_training import ACTION_TO_DELTA

class Bot:
    def __init__(self, agent, color=(255, 80, 80)):
        self.agent = agent
        self.color = color
        self.cell_size = agent.maze.cell_size
        self.rect = pygame.Rect(
            agent.position[0] * self.cell_size,
            agent.position[1] * self.cell_size,
            self.cell_size - 4,
            self.cell_size - 4
        )

    def update_position(self, other_bot):
        """Обновляет положение в соответствии с Q-таблицей"""
        state = self.agent.get_state(other_bot.agent.position)
        action = self.agent.choose_action(state)
        self.agent.step(action)
        self.rect.topleft = (
            self.agent.position[0] * self.cell_size,
            self.agent.position[1] * self.cell_size
        )

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
