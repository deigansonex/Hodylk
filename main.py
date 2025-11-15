# main.py  (заменяет твой прежний main.py)
import pygame, os
from utils.settings import *
from game.player import Player
from rl.mapoca_env import MapocaEnv, ACTIONS
from rl.loader import load_actors, actor_action

pygame.init()

# небольшая проверка: если нет сохранённых моделей — треним быстро или используем random
MODEL_DIR = "rl_models"
have_models = os.path.exists(os.path.join(MODEL_DIR, "actor_h.pth")) and os.path.exists(os.path.join(MODEL_DIR, "actor_p.pth"))

# сделаем env (и будем рисовать env.maze + env.hunter/env.prey)
env = MapocaEnv(width=33, height=25, cell_size=24)
maze = env.maze
screen = pygame.display.set_mode((maze.width * maze.cell_size, maze.height * maze.cell_size))
pygame.display.set_caption("MA-POCA demo")
clock = pygame.time.Clock()

player = Player(maze, start_cell=(1,1))  # human player
collectibles = None  # (optional) you can reuse your CollectibleManager if you want player to collect items

# load actors if available
if have_models:
    actor_h, actor_p = load_actors()
else:
    actor_h = actor_p = None

TOTAL_TIME = 60
font = pygame.font.Font(None, 36)

game_over = False
win = False
start_ticks = pygame.time.get_ticks()

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        # handle human movement
        player.handle_input(maze)
        player.update_trails()

        # get current obs for agents
        obs_h, obs_p = env.get_obs()

        # choose actions (from model if exists, otherwise random)
        if actor_h is not None:
            ah = actor_action(actor_h, obs_h)
            ap = actor_action(actor_p, obs_p)
        else:
            ah = env.sample_action()[0]
            ap = env.sample_action()[1]

        # apply actions (smooth movement via Bot.apply_action inside env.step)
        (obs_h2, obs_p2), (rh, rp), done, info = env.step((ah, ap))

        # draw everything
        screen.fill((0,0,0))
        maze.draw(screen)
        # optionally draw player and trails
        player.draw(screen)
        env.prey.draw(screen)
        env.hunter.draw(screen)

        # timer
        seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
        time_left = max(0, TOTAL_TIME - seconds_passed)
        timer_text = font.render(f"Time: {int(time_left)}", True, (255,255,255))
        screen.blit(timer_text, (10,10))

        # win/lose checks
        if env.hunter.rect.colliderect(env.prey.rect):
            win = False
            game_over = True
            end_message = "😈 Охотник поймал жертву!"
        if time_left <= 0:
            win = True
            game_over = True
            end_message = "⏰ Время вышло — жертва спаслась!"

        pygame.display.flip()

    else:
        # end screen (simple)
        screen.fill((0,0,0))
        msg = "ПОБЕДА!" if win else "ПОРАЖЕНИЕ!"
        txt = font.render(msg, True, (255,255,255))
        screen.blit(txt, (20,20))
        sub = font.render("R - restart, ESC - quit", True, (200,200,200))
        screen.blit(sub, (20,60))
        pygame.display.flip()
        if keys[pygame.K_ESCAPE]:
            running = False
        if keys[pygame.K_r]:
            env.reset()
            start_ticks = pygame.time.get_ticks()
            game_over = False
            win = False

pygame.quit()
