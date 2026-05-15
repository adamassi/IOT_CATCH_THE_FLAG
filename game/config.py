import pygame

# Window
WIDTH, HEIGHT = 1600, 1000
FPS = 60
CAPTION = "Capture The Flag"

# Colors (easy to change in one place)
BG_TOP = (15, 18, 24)
BG_BOTTOM = (32, 40, 52)

WHITE = (245, 245, 245)
TEXT_DIM = (185, 195, 210)

PANEL_FILL = (255, 255, 255, 22)   # rgba
PANEL_BORDER = (255, 255, 255, 55)

BTN = (52, 62, 76)
BTN_HOVER = (70, 84, 102)

ACCENT = (50, 180, 170)       # teal
ACCENT_HOVER = (75, 205, 195)

DANGER = (240, 90, 90)
DANGER_HOVER = (255, 120, 120)


def load_fonts():
    """Call after pygame.init()."""
    return {
        "title": pygame.font.SysFont("arial", 72, bold=True),
        "subtitle": pygame.font.SysFont("arial", 22),
        "button": pygame.font.SysFont("arial", 32, bold=True),
    }