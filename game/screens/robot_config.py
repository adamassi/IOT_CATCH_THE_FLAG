import pygame
import config
from screens.base import Screen
from ui.button import Button
from ui.slider import OptionSlider
from utils.draw import draw_soft_shadow, draw_panel


class RobotConfigScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        self.panel = pygame.Rect(config.WIDTH // 2 - 420, 230, 840, 390)

        self.word_bank_btn = Button(
            "Change Word Bank",
            (config.WIDTH // 2 - 220, 315, 440, 70),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=None,
        )

        self.algorithm_slider = OptionSlider(
            rect=(config.WIDTH // 2 - 300, 485, 600, 80),
            options=["RRT", "A*", "CRS"],
            font=fonts["subtitle"],
            text_color=config.WHITE,
            knob_color=config.ACCENT,
            line_color=config.TEXT_DIM,
        )

        self.back_btn = Button(
            "Back",
            (40, 40, 140, 55),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("configure"),
        )

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.word_bank_btn.handle_event(event)
        self.algorithm_slider.handle_event(event)

    def draw(self, surface):
        title = self.fonts["title"].render("Robot Configuration", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 100)))

        sub = self.fonts["subtitle"].render("Choose robot settings", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 150)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.word_bank_btn.draw(surface)

        label = self.fonts["subtitle"].render(
            f"Algorithm: {self.algorithm_slider.value}",
            True,
            config.TEXT_DIM,
        )
        surface.blit(label, label.get_rect(center=(config.WIDTH // 2, 440)))

        self.algorithm_slider.draw(surface)
        self.back_btn.draw(surface)