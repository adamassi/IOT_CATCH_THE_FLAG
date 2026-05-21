import pygame


class OptionSlider:
    def __init__(self, rect, options, font, text_color, knob_color, line_color):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.font = font
        self.text_color = text_color
        self.knob_color = knob_color
        self.line_color = line_color
        self.index = 0

    @property
    def value(self):
        return self.options[self.index]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._set_from_x(event.pos[0])

        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(event.pos):
                    self._set_from_x(event.pos[0])

    def _set_from_x(self, x):
        relative = (x - self.rect.x) / max(1, self.rect.w)
        relative = max(0, min(1, relative))
        self.index = round(relative * (len(self.options) - 1))

    def draw(self, surface):
        y = self.rect.centery

        pygame.draw.line(
            surface,
            self.line_color,
            (self.rect.x, y),
            (self.rect.right, y),
            5,
        )

        for i, option in enumerate(self.options):
            x = self.rect.x + int((self.rect.w * i) / (len(self.options) - 1))

            pygame.draw.circle(surface, self.line_color, (x, y), 10)

            label = self.font.render(option, True, self.text_color)
            surface.blit(label, label.get_rect(center=(x, y + 35)))

        knob_x = self.rect.x + int((self.rect.w * self.index) / (len(self.options) - 1))
        pygame.draw.circle(surface, self.knob_color, (knob_x, y), 17)