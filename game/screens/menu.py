# screens/menu.py
import pygame
import config
from screens.base import Screen
from ui.button import Button
from utils.draw import draw_soft_shadow, draw_panel


class MenuScreen(Screen):
    def __init__(self, manager, quit_game, fonts):
        self.manager = manager
        self.quit_game = quit_game
        self.fonts = fonts

        self.panel = pygame.Rect(config.WIDTH // 2 - 280, 185, 560, 380)

        btn_w, btn_h = 340, 66
        btn_x = config.WIDTH // 2 - btn_w // 2
        btn_y0 = 290
        gap = 22

        self.buttons = [
            Button(
                "Start",
                (btn_x, btn_y0, btn_w, btn_h),
                fonts["button"],
                config.ACCENT,
                config.ACCENT_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("game"),
            ),
            Button(
                "Configure",
                (btn_x, btn_y0 + (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.BTN,
                config.BTN_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("configure"),  # does nothing for now
            ),
            Button(
                "Exit",
                (btn_x, btn_y0 + 2 * (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.DANGER,
                config.DANGER_HOVER,
                config.WHITE,
                on_click=self.quit_game,
            ),
        ]

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, surface):
        title = self.fonts["title"].render("Capture The Flag", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 92)))

        sub = self.fonts["subtitle"].render("Main Menu", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        draw_soft_shadow(surface, self.panel, spread=12, alpha=55, radius=26)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER, radius=26)

        for b in self.buttons:
            b.draw(surface)