# ui/mute_button.py

import pygame
import config
from utils.robot_audio import is_muted, toggle_mute


class MuteButton:
    def __init__(self, rect, font=None):
        self.rect = pygame.Rect(rect)

        # Windows emoji font. Falls back if unavailable.
        self.font = pygame.font.SysFont("Segoe UI Emoji", 30)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                toggle_mute()

    def draw(self, surface):
        muted = is_muted()

        color = config.DANGER if muted else config.BTN
        hover = config.DANGER_HOVER if muted else config.BTN_HOVER

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            color = hover

        pygame.draw.rect(surface, color, self.rect, border_radius=16)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=16)

        icon = "🔇" if muted else "🔊"
        label = self.font.render(icon, True, config.WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))