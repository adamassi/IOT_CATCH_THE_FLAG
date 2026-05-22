import pygame
import config
from screens.base import Screen
from ui.button import Button
from utils.draw import draw_soft_shadow, draw_panel


class LayoutConfigScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        self.panel = pygame.Rect(config.WIDTH // 2 - 330, 240, 660, 320)

        btn_w, btn_h = 240, 75
        gap = 50
        total_w = 2 * btn_w + gap
        start_x = config.WIDTH // 2 - total_w // 2
        y = 380

        self.add_btn = Button(
            "Add",
            (start_x, y, btn_w, btn_h),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=None,
        )

        self.remove_btn = Button(
           "Remove",
            (start_x + btn_w + gap, y, btn_w, btn_h),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("remove_obstacle"),
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
        self.add_btn.handle_event(event)
        self.remove_btn.handle_event(event)

    def draw(self, surface):
        title = self.fonts["title"].render("Layout", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 100)))

        sub = self.fonts["subtitle"].render("Add or remove obstacles", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 150)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.add_btn.draw(surface)
        self.remove_btn.draw(surface)
        self.back_btn.draw(surface)