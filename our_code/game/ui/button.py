import pygame
from utils.draw import draw_soft_shadow

class Button:
    def __init__(self, text, rect, font, base_color, hover_color, text_color, on_click=None):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.on_click = on_click  # callable or None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.hover_color if hovered else self.base_color

        # subtle shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        draw_soft_shadow(surface, shadow_rect, spread=8, alpha=35, radius=18)

        pygame.draw.rect(surface, color, self.rect, border_radius=18)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=18)

        text_surf = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))