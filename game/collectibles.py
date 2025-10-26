# collectibles.py
import random
import pygame

class Collectible:
    """
    Хранит позицию в пикселях (center_x, center_y) и радиус для отрисовки/коллизии.
    Используем пиксельные координаты, чтобы избежать рассинхрона scale.
    """
    def __init__(self, center_x: int, center_y: int, radius: int, grid_coord=None):
        self.cx = int(center_x)
        self.cy = int(center_y)
        self.radius = int(radius)
        self.collected = False
        self.color = (255, 215, 0)  # золотистый
        self.grid_coord = grid_coord  # (gx, gy) — опционально для отладки

    def draw(self, surface):
        if self.collected:
            return
        # рисуем круг в пикселях
        pygame.draw.circle(surface, self.color, (self.cx, self.cy), self.radius)

    def get_bounding_rect(self):
        """Возвращает pygame.Rect вокруг коллектабла (для быстрой коллизии)."""
        return pygame.Rect(self.cx - self.radius, self.cy - self.radius,
                           self.radius * 2, self.radius * 2)


class CollectibleManager:
    """
    Надёжный менеджер коллектаблов.
    - Определяет cell_size автоматически (maze.cell_size или maze.tile_size).
    - Берёт свободные клетки через maze.get_free_cells() если доступно, иначе напрямую из maze.grid.
    - Преобразует координаты ячеек в пиксели при создании, хранит пиксельные позиции.
    """
    def __init__(self, maze, count=8, visual_fraction=0.6):
        """
        maze: объект лабиринта (должен иметь maze.grid и maze.width/maze.height и cell_size/tile_size)
        count: желаемое количество предметов
        visual_fraction: доля клетки, занимаемая предметом (0..1), например 0.6 => 60% ячейки
        """
        self.maze = maze
        # безопасно получить размер клетки (поддержка разных имён)
        self.cell = getattr(maze, "cell_size", None) or getattr(maze, "tile_size", None)
        if not self.cell:
            raise ValueError("Maze must define 'cell_size' or 'tile_size' attribute")

        # получить список свободных клеток (gx,gy). сначала пробуем метод у maze, иначе читаем grid
        if hasattr(maze, "get_free_cells"):
            free_cells = list(maze.get_free_cells())
        else:
            free_cells = [
                (x, y)
                for y in range(1, getattr(maze, "height", len(maze.grid)) - 1)
                for x in range(1, getattr(maze, "width", len(maze.grid[0])) - 1)
                if maze.grid[y][x] == 0
            ]

        if not free_cells:
            raise ValueError("No free cells to spawn collectibles")

        random.shuffle(free_cells)
        count = min(count, len(free_cells))

        # размер предмета в пикселях: визуальная доля от cell
        radius = max(1, int((self.cell * visual_fraction) / 2))

        self.collectibles = []
        for i in range(count):
            gx, gy = free_cells[i]
            # переводим в пиксели: центр клетки
            cx = gx * self.cell + self.cell // 2
            cy = gy * self.cell + self.cell // 2
            c = Collectible(cx, cy, radius, grid_coord=(gx, gy))
            self.collectibles.append(c)

    def draw(self, surface):
        for c in self.collectibles:
            c.draw(surface)

    def check_collection(self, player_rect: pygame.Rect):
        """
        Проверяем пересечение игрока и коллектаблов.
        player_rect — pygame.Rect в пикселях (используй player.rect).
        """
        for c in self.collectibles:
            if c.collected:
                continue
            # быстрая AABB проверка через rect, затем точечная проверка центра (или оставить rect)
            if player_rect.colliderect(c.get_bounding_rect()):
                # пометим как собранный
                c.collected = True

    def all_collected(self) -> bool:
        return all(c.collected for c in self.collectibles)

    def remaining_count(self) -> int:
        return sum(1 for c in self.collectibles if not c.collected)

    def debug_draw_grid_positions(self, surface):
        """
        Для отладки: рисует маленькие крестики в центрах ячеек, куда спавнились предметы,
        и подписывает их grid-координаты (опционально).
        """
        font = pygame.font.get_default_font()
        f = pygame.font.SysFont(font, max(10, self.cell // 4))
        for c in self.collectibles:
            color = (0, 255, 0) if not c.collected else (100, 100, 100)
            pygame.draw.line(surface, color, (c.cx - 3, c.cy), (c.cx + 3, c.cy))
            pygame.draw.line(surface, color, (c.cx, c.cy - 3), (c.cx, c.cy + 3))
            if c.grid_coord:
                gx, gy = c.grid_coord
                txt = f.render(f"{gx},{gy}", True, (150,150,150))
                surface.blit(txt, (c.cx + 6, c.cy - txt.get_height()//2))
