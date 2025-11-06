# Параметры окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Размер ячейки (одна клетка лабиринта)
TILE_SIZE = 40
MAZE_COLS = SCREEN_WIDTH // TILE_SIZE
MAZE_ROWS = SCREEN_HEIGHT // TILE_SIZE

# Игрок
PLAYER_SIZE = 30
PLAYER_SPEED = 2

# Следы
TRAIL_COLOR = (0, 200, 255)
TRAIL_LIFETIME = 180      # сколько кадров живёт след (~3 секунды при 60 FPS)
TRAIL_RADIUS = 5

# Цвета
COLOR_WALL = (50, 50, 50)
COLOR_PATH = (200, 200, 200)