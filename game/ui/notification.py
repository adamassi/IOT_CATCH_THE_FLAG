# ui/notification.py

import pygame
import config


class NotificationManager:
    def __init__(self, fonts):
        self.fonts = fonts
        self.message = None
        self.is_error = False
        self.duration = 0.0

    def show(self, message, is_error=True, duration=4.0):
        self.message = str(message)
        self.is_error = is_error
        self.duration = duration

    def update(self, dt):
        if self.message:
            self.duration -= dt
            if self.duration <= 0:
                self.message = None

    def draw(self, surface):
        if not self.message:
            return

        color = config.DANGER if self.is_error else config.ACCENT

        rect = pygame.Rect(
            config.WIDTH // 2 - 360,
            25,
            720,
            60,
        )

        pygame.draw.rect(surface, color, rect, border_radius=16)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=16)

        text = self.fonts["subtitle"].render(self.message[:90], True, config.WHITE)
        surface.blit(text, text.get_rect(center=rect.center))