# screens/add_obstacle.py

import os
import json
import math
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

        self.json_path = os.path.join(
            project_root,
            "path_algorithms",
            "map1.json",
        )

        self.selected_type = "rectangle"
        self.popup_message = None
        self._last_map_mtime = 0

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
            json_path=self.json_path,
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
            placeholder="x",
            input_type="float",
        )

        self.y_input = TextInput(
            (right_x + input_w + gap, start_y + 45, input_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            placeholder="y",
            input_type="float",
        )

        self.z_input = TextInput(
            (right_x + 2 * (input_w + gap), start_y + 45, input_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            placeholder="z",
            input_type="float",
        )

        self.width_input = TextInput(
            (right_x, start_y + 145, (right_w - 20) // 2, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            placeholder="width",
            input_type="float",
        )

        self.height_input = TextInput(
            (right_x + (right_w + 20) // 2, start_y + 145, (right_w - 20) // 2, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            placeholder="height",
            input_type="float",
        )

        self.radius_input = TextInput(
            (right_x, start_y + 145, right_w, input_h),
            fonts["subtitle"],
            config.WHITE,
            (0, 0, 0),
            config.ACCENT,
            placeholder="radius",
            input_type="float",
        )

        self.add_btn = Button(
            "Add Obstacle",
            (right_x, self.panel.y + 500, right_w, 65),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.add_obstacle,
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

        self.ok_btn = Button(
            "OK",
            (config.WIDTH // 2 - 80, config.HEIGHT // 2 + 55, 160, 55),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.close_popup,
        )

    def set_type(self, obstacle_type):
        self.selected_type = obstacle_type

    def close_popup(self):
        self.popup_message = None

    def _read_float(self, input_box, name):
        text = input_box.text.strip()

        if text in ("", "-", "."):
            raise ValueError(f"Please enter {name}.")

        return float(text)

    def _load_map_json(self):
        with open(self.json_path, "r") as f:
            return json.load(f)

    def _save_map_json(self, data):
        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4)

    def _next_obstacle_id(self, obstacles):
        existing_ids = [
            obs.get("id", -1)
            for obs in obstacles
            if isinstance(obs.get("id", None), int)
        ]

        return max(existing_ids, default=-1) + 1

    def add_obstacle(self):
        try:
            x = self._read_float(self.x_input, "x")
            y = self._read_float(self.y_input, "y")
            self._read_float(self.z_input, "z")  # accepted for UI, not used in 2D map

            data = self._load_map_json()
            obstacles = data.setdefault("OBSTACLES", [])

            obstacle_id = self._next_obstacle_id(obstacles)

            if self.selected_type == "rectangle":
                width = self._read_float(self.width_input, "width")
                height = self._read_float(self.height_input, "height")

                if width <= 0 or height <= 0:
                    self.popup_message = "Width and height must be positive."
                    return

                half_h = height / 2
                half_w = width / 2

                coordinates = [
                    [x - half_h, y - half_w],
                    [x + half_h, y - half_w],
                    [x + half_h, y + half_w],
                    [x - half_h, y + half_w],
                    [x - half_h, y - half_w],
                ]

                new_obstacle = {
                    "id": obstacle_id,
                    "type": "rectangle",
                    "coordinates": coordinates,
                }

            else:
                radius = self._read_float(self.radius_input, "radius")

                if radius <= 0:
                    self.popup_message = "Radius must be positive."
                    return

                coordinates = []

                for i in range(8):
                    angle = 2 * math.pi * i / 8
                    px = x + radius * math.cos(angle)
                    py = y + radius * math.sin(angle)
                    coordinates.append([round(px, 3), round(py, 3)])

                coordinates.append(coordinates[0])

                new_obstacle = {
                    "id": obstacle_id,
                    "type": "circle",
                    "coordinates": coordinates,
                }

            obstacles.append(new_obstacle)

            self._save_map_json(data)
            self.map_preview.reload()

            self._clear_inputs()
            self.popup_message = f"Obstacle {obstacle_id} added successfully."

        except ValueError as e:
            self.popup_message = str(e)

        except Exception as e:
            self.popup_message = f"Failed to add obstacle: {e}"

    def _clear_inputs(self):
        self.x_input.text = ""
        self.y_input.text = ""
        self.z_input.text = ""
        self.width_input.text = ""
        self.height_input.text = ""
        self.radius_input.text = ""

    def _reload_map_if_file_changed(self):
        if not os.path.exists(self.json_path):
            return

        mtime = os.path.getmtime(self.json_path)

        if mtime != self._last_map_mtime:
            self._last_map_mtime = mtime
            self.map_preview.reload()

    def handle_event(self, event):
        if self.popup_message:
            self.ok_btn.handle_event(event)
            return

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
        self._reload_map_if_file_changed()

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

        if self.popup_message:
            self.draw_popup(surface)

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

    def draw_popup(self, surface):
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(
            config.WIDTH // 2 - 300,
            config.HEIGHT // 2 - 110,
            600,
            220,
        )

        draw_soft_shadow(surface, popup_rect, spread=18, alpha=80)
        draw_panel(surface, popup_rect, config.PANEL_FILL, config.PANEL_BORDER)

        msg = self.fonts["subtitle"].render(
            self.popup_message,
            True,
            config.WHITE,
        )
        surface.blit(msg, msg.get_rect(center=(popup_rect.centerx, popup_rect.y + 75)))

        self.ok_btn.draw(surface)