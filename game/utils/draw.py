import pygame

def vertical_gradient(surface, top_color, bottom_color):
    w, h = surface.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))


def draw_soft_shadow(surface, rect, spread=10, alpha=55, radius=26):
    shadow = pygame.Surface((rect.w + spread * 2, rect.h + spread * 2), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, (rect.x - spread, rect.y - spread))


def draw_panel(surface, rect, fill_rgba, border_rgba, radius=26):
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill_rgba, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_rgba, panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)