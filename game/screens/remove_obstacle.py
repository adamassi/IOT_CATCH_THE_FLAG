import pygame
import config
from screens.base import Screen
from ui.button import Button
from ui.text_input import TextInput
from ui.map_preview import MapPreview
from utils.draw import draw_soft_shadow, draw_panel


class RemoveObstacleScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        self.panel = pygame.Rect(120, 180, config.WIDTH - 240, config.HEIGHT - 260)

        self.map_preview = MapPreview(
            rect=(self.panel.x + 40, self.panel.y + 50, int(self.panel.w * 0.62), self.panel.h - 100),
            font=fonts["subtitle"],
        )

        right_x = self.map_preview.rect.right + 50
        right_w = self.panel.right - right_x - 40

        self.input_label_pos = (right_x, self.panel.y + 90)

        self.obstacle_input = TextInput(
            rect=(right_x, self.panel.y + 135, right_w, 60),
            font=fonts["subtitle"],
            text_color=config.WHITE,
            bg_color=(0, 0, 0),
            border_color=config.ACCENT,
            placeholder="Enter obstacle ID",
        )

        self.confirm_btn = Button(
            "Confirm Removal",
            (right_x, self.panel.y + 225, right_w, 65),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=None,
        )

        self.undo_btn = Button(
            "Undo Last Removal",
            (right_x, self.panel.y + 315, right_w, 65),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=None,
        )

        self.back_btn = Button(
            "Back",
            (40, 40, 140, 55),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("layout_config"),
        )

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.obstacle_input.handle_event(event)
        self.confirm_btn.handle_event(event)
        self.undo_btn.handle_event(event)

    def draw(self, surface):
        title = self.fonts["title"].render("Remove Obstacles", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 90)))

        sub = self.fonts["subtitle"].render(
            "Select an obstacle ID to remove from the layout",
            True,
            config.TEXT_DIM,
        )
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.map_preview.draw(surface)

        label = self.fonts["subtitle"].render("Obstacle ID", True, config.TEXT_DIM)
        surface.blit(label, self.input_label_pos)

        self.obstacle_input.draw(surface)
        self.confirm_btn.draw(surface)
        self.undo_btn.draw(surface)
        self.back_btn.draw(surface)