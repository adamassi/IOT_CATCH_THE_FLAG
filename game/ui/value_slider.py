# ui/value_slider.py

import pygame


class ValueSlider:
    def __init__(
        self,
        rect,
        min_value,
        max_value,
        initial_value,
        font,
        label,
        text_color,
        line_color,
        knob_color,
        on_change=None,
        step=1,
    ):
        self.rect = pygame.Rect(rect)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.font = font
        self.label = label
        self.text_color = text_color
        self.line_color = line_color
        self.knob_color = knob_color
        self.on_change = on_change
        self.step = step
        self.dragging = False
        self._last_sent_value = initial_value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._set_from_x(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                self._emit_change(force=True)

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_x(event.pos[0])

    def _set_from_x(self, x):
        relative = (x - self.rect.x) / max(1, self.rect.w)
        relative = max(0, min(1, relative))

        raw = self.min_value + relative * (self.max_value - self.min_value)
        stepped = round(raw / self.step) * self.step

        self.value = int(max(self.min_value, min(self.max_value, stepped)))
        self._emit_change()

    def _emit_change(self, force=False):
        if self.on_change is None:
            return

        if force or self.value != self._last_sent_value:
            self._last_sent_value = self.value
            self.on_change(self.value)

    def draw(self, surface):
        label = self.font.render(f"{self.label}: {self.value}", True, self.text_color)
        surface.blit(label, label.get_rect(center=(self.rect.centerx, self.rect.y - 35)))

        y = self.rect.centery

        pygame.draw.line(
            surface,
            self.line_color,
            (self.rect.x, y),
            (self.rect.right, y),
            8,
        )

        zero_x = self._value_to_x(0)
        if self.min_value < 0 < self.max_value:
            pygame.draw.circle(surface, self.text_color, (zero_x, y), 7)

        knob_x = self._value_to_x(self.value)

        pygame.draw.circle(surface, self.knob_color, (knob_x, y), 18)
        pygame.draw.circle(surface, self.text_color, (knob_x, y), 18, 2)

    def _value_to_x(self, value):
        relative = (value - self.min_value) / (self.max_value - self.min_value)
        return self.rect.x + int(relative * self.rect.w)