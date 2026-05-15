# app.py
import sys
import pygame
import config
from utils.draw import vertical_gradient
from screens.screen_manager import ScreenManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.CAPTION)
    clock = pygame.time.Clock()

    fonts = config.load_fonts()

    running = True

    def quit_game():
        nonlocal running
        running = False

    manager = ScreenManager(quit_game=quit_game, fonts=fonts)

    while running:
        dt = clock.tick(config.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.current.handle_event(event)

        manager.current.update(dt)

        vertical_gradient(screen, config.BG_TOP, config.BG_BOTTOM)
        manager.current.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()