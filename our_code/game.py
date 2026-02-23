import sys
import pygame

pygame.init()

# -----------------------------
# Window
# -----------------------------
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Capture The Flag")
clock = pygame.time.Clock()

# -----------------------------
# New color palette (neutral + teal)
# -----------------------------
BG_TOP = (12, 16, 20)       # near-black
BG_BOTTOM = (28, 36, 44)    # dark slate

WHITE = (245, 245, 245)
TEXT_DIM = (180, 190, 200)

PANEL_FILL = (255, 255, 255, 26)   # translucent
PANEL_BORDER = (255, 255, 255, 60)

BTN = (45, 55, 65)          # neutral button
BTN_HOVER = (62, 74, 88)

ACCENT = (46, 196, 182)     # teal
ACCENT_HOVER = (70, 220, 206)

DANGER = (240, 84, 84)      # soft red
DANGER_HOVER = (255, 110, 110)

# -----------------------------
# Fonts
# -----------------------------
title_font = pygame.font.SysFont("arial", 74, bold=True)
subtitle_font = pygame.font.SysFont("arial", 22)
button_font = pygame.font.SysFont("arial", 32, bold=True)

# -----------------------------
# Helpers
# -----------------------------
def vertical_gradient(surface, top_color, bottom_color):
    w, h = surface.get_size()
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

def draw_rounded_panel(surface, rect, fill_rgba, border_rgba, radius=26):
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, fill_rgba, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, border_rgba, panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)

def draw_soft_shadow(surface, rect, spread=10, alpha=40):
    shadow = pygame.Surface((rect.w + spread*2, rect.h + spread*2), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, alpha), shadow.get_rect(), border_radius=28)
    surface.blit(shadow, (rect.x - spread, rect.y - spread))

# -----------------------------
# Button
# -----------------------------
class Button:
    def __init__(self, text, rect, base_color, hover_color, text_color=WHITE, border_color=(0, 0, 0)):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.hover_color if hovered else self.base_color

        # shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 6
        draw_soft_shadow(surface, shadow_rect, spread=8, alpha=35)

        pygame.draw.rect(surface, color, self.rect, border_radius=18)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, width=2, border_radius=18)

        text_surf = button_font.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def clicked(self, event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

# -----------------------------
# Pages / States
# -----------------------------
MENU = "menu"
GAME = "game"
state = MENU

# -----------------------------
# Layouts
# -----------------------------
# Menu panel (same idea, centered)
menu_panel = pygame.Rect(WIDTH//2 - 280, 185, 560, 380)

btn_w, btn_h = 340, 66
btn_x = WIDTH//2 - btn_w//2
btn_y0 = 290
gap = 22

btn_start = Button("Start", (btn_x, btn_y0, btn_w, btn_h), ACCENT, ACCENT_HOVER)
btn_config = Button("Configure", (btn_x, btn_y0 + (btn_h + gap), btn_w, btn_h), BTN, BTN_HOVER)
btn_exit = Button("Exit", (btn_x, btn_y0 + 2*(btn_h + gap), btn_w, btn_h), DANGER, DANGER_HOVER)

# Bigger game "screen" panel so buttons fit inside
game_panel = pygame.Rect(WIDTH//2 - 380, 170, 760, 420)

# Game buttons INSIDE panel
g_btn_w, g_btn_h = 210, 62
g_gap = 20
g_total_w = 3*g_btn_w + 2*g_gap
g_start_x = game_panel.centerx - g_total_w//2
g_y = game_panel.bottom - 95  # inside the panel near bottom

btn_run = Button("Run", (g_start_x, g_y, g_btn_w, g_btn_h), ACCENT, ACCENT_HOVER)
btn_pause = Button("Pause", (g_start_x + (g_btn_w + g_gap), g_y, g_btn_w, g_btn_h), BTN, BTN_HOVER)
btn_stop = Button("Stop", (g_start_x + 2*(g_btn_w + g_gap), g_y, g_btn_w, g_btn_h), DANGER, DANGER_HOVER)

btn_back = Button("Back", (35, 35, 130, 48), BTN, BTN_HOVER, text_color=WHITE)

# -----------------------------
# Draw Functions
# -----------------------------
def draw_title(surface, main_text, sub_text=None):
    title = title_font.render(main_text, True, WHITE)
    surface.blit(title, title.get_rect(center=(WIDTH//2, 92)))

    if sub_text:
        sub = subtitle_font.render(sub_text, True, TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(WIDTH//2, 140)))

def draw_menu(surface):
    draw_title(surface, "Capture The Flag", "Main Menu")

    draw_soft_shadow(surface, menu_panel, spread=12, alpha=55)
    draw_rounded_panel(surface, menu_panel, PANEL_FILL, PANEL_BORDER)

    btn_start.draw(surface)
    btn_config.draw(surface)
    btn_exit.draw(surface)

def draw_game(surface):
    draw_title(surface, "Capture The Flag", "Game Screen (controls are placeholders)")

    draw_soft_shadow(surface, game_panel, spread=14, alpha=60)
    draw_rounded_panel(surface, game_panel, PANEL_FILL, PANEL_BORDER)

    # Some placeholder text inside panel
    hint = subtitle_font.render("Your game will be drawn here later.", True, TEXT_DIM)
    surface.blit(hint, hint.get_rect(center=(game_panel.centerx, game_panel.y + 110)))

    btn_run.draw(surface)
    btn_pause.draw(surface)
    btn_stop.draw(surface)

    btn_back.draw(surface)

# -----------------------------
# Main Loop
# -----------------------------
running = True
while running:
    clock.tick(60)

    vertical_gradient(screen, BG_TOP, BG_BOTTOM)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if btn_start.clicked(event):
                state = GAME
            elif btn_config.clicked(event):
                pass
            elif btn_exit.clicked(event):
                running = False

        elif state == GAME:
            if btn_back.clicked(event):
                state = MENU

            # placeholders (do nothing)
            if btn_run.clicked(event):
                pass
            if btn_pause.clicked(event):
                pass
            if btn_stop.clicked(event):
                pass

    if state == MENU:
        draw_menu(screen)
    else:
        draw_game(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()