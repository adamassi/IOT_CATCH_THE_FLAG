# screens/add_obstacle.py

import os
import pygame
import config

from screens.base import Screen
from ui.button import Button
from ui.text_input import TextInput
from ui.map_preview import MapPreview
from utils.draw import draw_soft_shadow, draw_panel


class AddObstacleScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        json_path = os.path.join(project_root, "path_algorithms", "map1.json")

        self.selected_type = "rectangle"

        self.panel = pygame.Rect(
            120,
            180,
            config.WIDTH - 240,
            config.HEIGHT - 260,
        )

        self.map_preview = MapPreview(
            rect=(
                self.panel.x + 40,
                self.panel.y + 50,
                int(self.panel.w * 0.50),
                self.panel.h - 100,
            ),
            font=fonts["subtitle"],
            json_path=self.json_path if hasattr(self, "json_path") else json_path,
        )

        right_x = self.map_preview.rect.right + 35
        right_w = self.panel.right - right_x - 40

        self.right_x = right_x
        self.right_w = right_w

        self.rectangle_btn = Button(
            "Rectangle",
            (right_x, self.panel.y + 70, (right_w - 20) // 2, 60),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=lambda: self.set_type("rectangle"),
        )

        self.circle_btn = Button(
            "Circle",
            (right_x + (right_w + 20) // 2, self.panel.y + 70, (right_w - 20) // 2, 60),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.set_type("circle"),
        )

        input_w = 120
        input_h = 55
        gap = 18
        start_y = self.panel.y + 190

        self.x_input = TextInput(
            (right_x, start_y + 45, input_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "x",
            input_type="float",
        )

        self.y_input = TextInput(
            (right_x + input_w + gap, start_y + 45, input_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "y",
            input_type="float",
        )

        self.z_input = TextInput(
            (right_x + 2 * (input_w + gap), start_y + 45, input_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "z",
            input_type="float",
        )

        self.width_input = TextInput(
            (right_x, start_y + 145, (right_w - 20) // 2, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "width",
            input_type="float",
        )

        self.height_input = TextInput(
            (right_x + (right_w + 20) // 2, start_y + 145, (right_w - 20) // 2, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "height",
            input_type="float",
        )

        self.radius_input = TextInput(
            (right_x, start_y + 145, right_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            "radius",
            input_type="float",
        )

        self.add_btn = Button(
            "Add Obstacle",
            (right_x, self.panel.y + 500, right_w, 65),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
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

    def set_type(self, obstacle_type):
        self.selected_type = obstacle_type

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.rectangle_btn.handle_event(event)
        self.circle_btn.handle_event(event)

        self.x_input.handle_event(event)
        self.y_input.handle_event(event)
        self.z_input.handle_event(event)

        if self.selected_type == "rectangle":
            self.width_input.handle_event(event)
            self.height_input.handle_event(event)
        else:
            self.radius_input.handle_event(event)

        self.add_btn.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        title = self.fonts["title"].render("Add Obstacle", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 90)))

        sub = self.fonts["subtitle"].render(
            "Choose obstacle type and enter its dimensions",
            True,
            config.TEXT_DIM,
        )
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.map_preview.draw(surface)

        self._draw_type_buttons(surface)
        self._draw_inputs(surface)

        self.add_btn.draw(surface)
        self.back_btn.draw(surface)

    def _draw_type_buttons(self, surface):
        self.rectangle_btn.base_color = config.ACCENT if self.selected_type == "rectangle" else config.BTN
        self.rectangle_btn.hover_color = config.ACCENT_HOVER if self.selected_type == "rectangle" else config.BTN_HOVER

        self.circle_btn.base_color = config.ACCENT if self.selected_type == "circle" else config.BTN
        self.circle_btn.hover_color = config.ACCENT_HOVER if self.selected_type == "circle" else config.BTN_HOVER

        label = self.fonts["subtitle"].render("Obstacle Type", True, config.TEXT_DIM)
        surface.blit(label, (self.right_x, self.panel.y + 35))

        self.rectangle_btn.draw(surface)
        self.circle_btn.draw(surface)

    def _draw_inputs(self, surface):
        y = self.panel.y + 190

        label = self.fonts["subtitle"].render("Center Position", True, config.TEXT_DIM)
        surface.blit(label, (self.right_x, y))

        self.x_input.draw(surface)
        self.y_input.draw(surface)
        self.z_input.draw(surface)

        if self.selected_type == "rectangle":
            label = self.fonts["subtitle"].render("Rectangle Size", True, config.TEXT_DIM)
            surface.blit(label, (self.right_x, y + 105))

            self.width_input.draw(surface)
            self.height_input.draw(surface)

        else:
            label = self.fonts["subtitle"].render("Circle Radius", True, config.TEXT_DIM)
            surface.blit(label, (self.right_x, y + 105))

            self.radius_input.draw(surface)