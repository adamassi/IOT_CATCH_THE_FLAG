# screens/word_bank_config.py

import os
import json
import pygame
import config

from screens.base import Screen
from ui.button import Button
from ui.text_input import TextInput
from utils.draw import draw_soft_shadow, draw_panel


class WordBankConfigScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.json_path = os.path.join(project_root, "path_algorithms/cube_bank.json")

        self.panel = pygame.Rect(120, 180, config.WIDTH - 240, config.HEIGHT - 260)

        self.cubes = []
        self.reload_cubes()

        left_x = self.panel.x + 50
        right_x = self.panel.centerx + 40
        box_w = self.panel.w // 2 - 90

        self.list_rect = pygame.Rect(left_x, self.panel.y + 80, box_w, self.panel.h - 140)
        self.controls_rect = pygame.Rect(right_x, self.panel.y + 80, box_w, self.panel.h - 140)

        self.id_input = TextInput(
            rect=(right_x + 30, self.controls_rect.y + 95, box_w - 60, 55),
            font=fonts["subtitle"],
            text_color=config.WHITE,
            bg_color=(0, 0, 0),
            border_color=config.ACCENT,
            placeholder="Cube ID",
            input_type="int",
        )

        self.letter_input = TextInput(
            rect=(right_x + 30, self.controls_rect.y + 185, box_w - 60, 55),
            font=fonts["subtitle"],
            text_color=config.WHITE,
            bg_color=(0, 0, 0),
            border_color=config.ACCENT,
            placeholder="Letter",
            input_type="text",
            max_length=1,
        )

        self.add_btn = Button(
            "Add Cube",
            (right_x + 30, self.controls_rect.y + 275, box_w - 60, 60),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.add_cube,
        )

        self.remove_btn = Button(
            "Remove Cube",
            (right_x + 30, self.controls_rect.y + 355, box_w - 60, 60),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=self.remove_cube,
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

        self.popup_message = None

        self.ok_btn = Button(
            "OK",
            (config.WIDTH // 2 - 80, config.HEIGHT // 2 + 55, 160, 55),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.close_popup,
        )

    def close_popup(self):
        self.popup_message = None

    def ensure_json_exists(self):
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                json.dump({"CUBES": []}, f, indent=4)

    def reload_cubes(self):
        self.ensure_json_exists()

        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)

            self.cubes = data.get("CUBES", [])

        except Exception:
            self.cubes = []

    def save_cubes(self):
        with open(self.json_path, "w") as f:
            json.dump({"CUBES": self.cubes}, f, indent=4)

    def add_cube(self):
        cube_id_text = self.id_input.text.strip()
        letter = self.letter_input.text.strip().upper()

        if not cube_id_text:
            self.popup_message = "Please enter a cube ID."
            return

        if not letter:
            self.popup_message = "Please enter a letter."
            return

        cube_id = int(cube_id_text)

        for cube in self.cubes:
            if cube.get("cube_ID") == cube_id:
                self.popup_message = f"Cube ID {cube_id} already exists."
                return

        self.cubes.append(
            {
                "cube_ID": cube_id,
                "letter": letter,
            }
        )

        self.save_cubes()
        self.reload_cubes()

        self.id_input.text = ""
        self.letter_input.text = ""

        self.popup_message = f"Cube {cube_id} added."

    def remove_cube(self):
        cube_id_text = self.id_input.text.strip()

        if not cube_id_text:
            self.popup_message = "Please enter the cube ID to remove."
            return

        cube_id = int(cube_id_text)

        old_count = len(self.cubes)

        self.cubes = [
            cube for cube in self.cubes
            if cube.get("cube_ID") != cube_id
        ]

        if len(self.cubes) == old_count:
            self.popup_message = f"No cube with ID {cube_id} exists."
            return

        self.save_cubes()
        self.reload_cubes()

        self.id_input.text = ""
        self.popup_message = f"Cube {cube_id} removed."

    def handle_event(self, event):
        if self.popup_message:
            self.ok_btn.handle_event(event)
            return

        self.back_btn.handle_event(event)
        self.id_input.handle_event(event)
        self.letter_input.handle_event(event)
        self.add_btn.handle_event(event)
        self.remove_btn.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        title = self.fonts["title"].render("Word Bank", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 90)))

        sub = self.fonts["subtitle"].render(
            "Manage available cubes",
            True,
            config.TEXT_DIM,
        )
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.draw_cube_list(surface)
        self.draw_controls(surface)

        self.back_btn.draw(surface)

        if self.popup_message:
            self.draw_popup(surface)

    def draw_cube_list(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.list_rect, border_radius=18)
        pygame.draw.rect(surface, config.PANEL_BORDER, self.list_rect, 2, border_radius=18)

        header = self.fonts["subtitle"].render("Available Cubes", True, config.TEXT_DIM)
        surface.blit(header, (self.list_rect.x + 25, self.list_rect.y + 20))

        y = self.list_rect.y + 75

        id_header = self.fonts["subtitle"].render("Cube ID", True, config.WHITE)
        letter_header = self.fonts["subtitle"].render("Letter", True, config.WHITE)

        surface.blit(id_header, (self.list_rect.x + 35, y))
        surface.blit(letter_header, (self.list_rect.x + 240, y))

        y += 35
        pygame.draw.line(
            surface,
            config.PANEL_BORDER,
            (self.list_rect.x + 25, y),
            (self.list_rect.right - 25, y),
            1,
        )

        y += 25

        for cube in self.cubes:
            cube_id = cube.get("cube_ID", "")
            letter = cube.get("letter", "")

            id_text = self.fonts["subtitle"].render(str(cube_id), True, config.WHITE)
            letter_text = self.fonts["subtitle"].render(str(letter), True, config.WHITE)

            surface.blit(id_text, (self.list_rect.x + 35, y))
            surface.blit(letter_text, (self.list_rect.x + 250, y))

            y += 40

    def draw_controls(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), self.controls_rect, border_radius=18)
        pygame.draw.rect(surface, config.PANEL_BORDER, self.controls_rect, 2, border_radius=18)

        header = self.fonts["subtitle"].render("Add / Remove Cube", True, config.TEXT_DIM)
        surface.blit(header, (self.controls_rect.x + 30, self.controls_rect.y + 25))

        id_label = self.fonts["subtitle"].render("Cube ID", True, config.TEXT_DIM)
        surface.blit(id_label, (self.controls_rect.x + 30, self.controls_rect.y + 70))

        self.id_input.draw(surface)

        letter_label = self.fonts["subtitle"].render("Letter", True, config.TEXT_DIM)
        surface.blit(letter_label, (self.controls_rect.x + 30, self.controls_rect.y + 160))

        self.letter_input.draw(surface)

        self.add_btn.draw(surface)
        self.remove_btn.draw(surface)

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

        msg = self.fonts["subtitle"].render(self.popup_message, True, config.WHITE)
        surface.blit(msg, msg.get_rect(center=(popup_rect.centerx, popup_rect.y + 75)))

        self.ok_btn.draw(surface)