import pygame
import config
from screens.base import Screen
from ui.button import Button
from utils.draw import draw_soft_shadow, draw_panel


class ConfigureScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        self.panel = pygame.Rect(config.WIDTH // 2 - 330, 220, 660, 420)

        btn_w, btn_h = 380, 70
        btn_x = config.WIDTH // 2 - btn_w // 2
        btn_y = 310
        gap = 30

        self.buttons = [
            Button(
                "Layout",
                (btn_x, btn_y, btn_w, btn_h),
                fonts["button"],
                config.ACCENT,
                config.ACCENT_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("layout_config"),
            ),
            Button(
                "Robot Configuration",
                (btn_x, btn_y + btn_h + gap, btn_w, btn_h),
                fonts["button"],
                config.BTN,
                config.BTN_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("robot_config"),
            ),
            Button(
                "Word Bank",
                (btn_x, btn_y + 2 * (btn_h + gap), btn_w, btn_h),
                fonts["button"],
                config.BTN,
                config.BTN_HOVER,
                config.WHITE,
                on_click=lambda: self.manager.go_to("word_bank_config"),
            ),
        ]

        self.back_btn = Button(
            "Back",
            (40, 40, 140, 55),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("menu"),
        )

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface):
        title = self.fonts["title"].render("Configure", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 100)))

        sub = self.fonts["subtitle"].render("Choose configuration category", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 150)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        for button in self.buttons:
            button.draw(surface)

        self.back_btn.draw(surface)