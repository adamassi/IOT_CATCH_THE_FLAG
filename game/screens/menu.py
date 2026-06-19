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

        self.panel = pygame.Rect(
            config.WIDTH // 2 - 300,
            190,
            600,
            470,
        )

        btn_w = 360
        btn_h = 62
        gap = 24

        btn_x = config.WIDTH // 2 - btn_w // 2
        btn_y0 = 285

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
                (btn_x, btn_y0 + 1 * (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.BTN,
                config.BTN_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("configure"),
            ),
            Button(
                "Manual Control",
                (btn_x, btn_y0 + 2 * (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.BTN,
                config.BTN_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("manual_control"),
            ),
            Button(
                "Exit",
                (btn_x, btn_y0 + 3 * (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.DANGER,
                config.DANGER_HOVER,
                config.WHITE,
                on_click=self.quit_game,
            ),
        ]

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        title = self.fonts["title"].render(
            "Capture The Flag",
            True,
            config.WHITE,
        )
        surface.blit(
            title,
            title.get_rect(center=(config.WIDTH // 2, 95)),
        )

        sub = self.fonts["subtitle"].render(
            "Main Menu",
            True,
            config.TEXT_DIM,
        )
        surface.blit(
            sub,
            sub.get_rect(center=(config.WIDTH // 2, 145)),
        )

        draw_soft_shadow(
            surface,
            self.panel,
            spread=12,
            alpha=55,
            radius=26,
        )

        draw_panel(
            surface,
            self.panel,
            config.PANEL_FILL,
            config.PANEL_BORDER,
            radius=26,
        )

        for button in self.buttons:
            button.draw(surface)