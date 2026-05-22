# ui/text_input.py

import pygame


class TextInput:
    def __init__(self, rect, font, text_color, bg_color, border_color, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.placeholder = placeholder

        self.text = ""
        self.active = False

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:

            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            elif event.key == pygame.K_RETURN:
                self.active = False

            else:
                # ONLY allow non-negative integer IDs
                if event.unicode.isdigit() and len(self.text) < 20:
                    self.text += event.unicode

    def draw(self, surface):

        pygame.draw.rect(
            surface,
            self.bg_color,
            self.rect,
            border_radius=12,
        )

        border_width = 3 if self.active else 2

        pygame.draw.rect(
            surface,
            self.border_color,
            self.rect,
            border_width,
            border_radius=12,
        )

        display_text = self.text if self.text else self.placeholder

        color = (
            self.text_color
            if self.text
            else (150, 150, 150)
        )

        text_surface = self.font.render(
            display_text,
            True,
            color,
        )

        surface.blit(
            text_surface,
            (self.rect.x + 15, self.rect.y + 14),
        )