# screens/remove_obstacle.py

import os
import sys
import json
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

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        if project_root not in sys.path:
            sys.path.append(project_root)

        self.json_path = os.path.join(
            project_root,
            "path_algorithms",
            "map1.json",
        )

        self.json_relative_path = "path_algorithms/map1.json"

        from path_algorithms.map_json_utils import (
            remove_obstacle_by_id,
            undo_remove_obstacle,
        )

        self.remove_obstacle_by_id = remove_obstacle_by_id
        self.undo_remove_obstacle = undo_remove_obstacle

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
                int(self.panel.w * 0.42),
                self.panel.h - 100,
            ),
            font=fonts["subtitle"],
            json_path=self.json_path,
        )

        right_x = self.map_preview.rect.right + 50
        right_w = self.panel.right - right_x - 40

        self.input_label_pos = (
            right_x,
            self.panel.y + 90,
        )

        self.obstacle_input = TextInput(
            rect=(
                right_x,
                self.panel.y + 135,
                right_w,
                60,
            ),
            font=fonts["subtitle"],
            text_color=config.WHITE,
            bg_color=(0, 0, 0),
            border_color=config.ACCENT,
            placeholder="Enter obstacle ID",
        )

        self.confirm_btn = Button(
            "Confirm Removal",
            (
                right_x,
                self.panel.y + 225,
                right_w,
                65,
            ),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=self.confirm_removal,
        )

        self.undo_btn = Button(
            "Undo Last Removal",
            (
                right_x,
                self.panel.y + 315,
                right_w,
                65,
            ),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=self.undo_last_removal,
        )

        self.reload_btn = Button(
            "Reload Map",
            (
                right_x,
                self.panel.y + 405,
                right_w,
                65,
            ),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.reload_map,
        )

        self.back_btn = Button(
            "Back",
            (
                40,
                40,
                140,
                55,
            ),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("layout_config"),
        )

        self.popup_message = None

        self.ok_btn = Button(
            "OK",
            (
                config.WIDTH // 2 - 80,
                config.HEIGHT // 2 + 55,
                160,
                55,
            ),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.close_popup,
        )

    # -------------------------------------------------
    # POPUP
    # -------------------------------------------------

    def close_popup(self):
        self.popup_message = None

    # -------------------------------------------------
    # RELOAD MAP
    # -------------------------------------------------

    def reload_map(self):
        self.map_preview.reload()
        self.popup_message = "Map reloaded successfully."

    # -------------------------------------------------
    # UNDO LAST REMOVAL
    # -------------------------------------------------

    def undo_last_removal(self):

        try:
            result = self.undo_remove_obstacle(
                json_file=self.json_relative_path,
            )

        except TypeError:
            result = self.undo_remove_obstacle(
                self.json_relative_path,
            )

        if result is False:
            self.popup_message = "Nothing to undo."
            return

        self.map_preview.reload()

        self.popup_message = "Last removal undone successfully."

    # -------------------------------------------------
    # REMOVE OBSTACLE
    # -------------------------------------------------

    def confirm_removal(self):

        text = self.obstacle_input.text.strip()

        if text == "":
            self.popup_message = "Please enter an obstacle ID."
            return

        obstacle_id = int(text)

        if not self._obstacle_exists(obstacle_id):
            self.popup_message = (
                f"No obstacle with ID {obstacle_id} exists."
            )
            return

        try:
            result = self.remove_obstacle_by_id(
                obstacle_id,
                json_file=self.json_relative_path,
            )

        except TypeError:
            result = self.remove_obstacle_by_id(
                obstacle_id,
                self.json_relative_path,
            )

        if result is False:
            self.popup_message = (
                f"Failed to remove obstacle {obstacle_id}."
            )
            return

        self.obstacle_input.text = ""

        self.map_preview.reload()

        self.popup_message = (
            f"Obstacle {obstacle_id} removed successfully."
        )

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------

    def _obstacle_exists(self, obstacle_id):

        try:
            with open(self.json_path, "r") as f:
                data = json.load(f)

            for obstacle in data.get("OBSTACLES", []):

                if obstacle.get("id") == obstacle_id:
                    return True

        except Exception:
            pass

        return False

    # -------------------------------------------------
    # EVENTS
    # -------------------------------------------------

    def handle_event(self, event):

        if self.popup_message:
            self.ok_btn.handle_event(event)
            return

        self.back_btn.handle_event(event)

        self.obstacle_input.handle_event(event)

        self.confirm_btn.handle_event(event)

        self.undo_btn.handle_event(event)

        self.reload_btn.handle_event(event)

    # -------------------------------------------------

    def update(self, dt):
        pass

    # -------------------------------------------------
    # DRAW
    # -------------------------------------------------

    def draw(self, surface):

        title = self.fonts["title"].render(
            "Remove Obstacles",
            True,
            config.WHITE,
        )

        surface.blit(
            title,
            title.get_rect(
                center=(config.WIDTH // 2, 90)
            ),
        )

        sub = self.fonts["subtitle"].render(
            "Select an obstacle ID to remove from the layout",
            True,
            config.TEXT_DIM,
        )

        surface.blit(
            sub,
            sub.get_rect(
                center=(config.WIDTH // 2, 140)
            ),
        )

        draw_soft_shadow(
            surface,
            self.panel,
            spread=18,
            alpha=65,
        )

        draw_panel(
            surface,
            self.panel,
            config.PANEL_FILL,
            config.PANEL_BORDER,
        )

        self.map_preview.draw(surface)

        label = self.fonts["subtitle"].render(
            "Obstacle ID",
            True,
            config.TEXT_DIM,
        )

        surface.blit(
            label,
            self.input_label_pos,
        )

        self.obstacle_input.draw(surface)

        self.confirm_btn.draw(surface)

        self.undo_btn.draw(surface)

        self.reload_btn.draw(surface)

        self.back_btn.draw(surface)

        if self.popup_message:
            self.draw_popup(surface)

    # -------------------------------------------------
    # POPUP DRAW
    # -------------------------------------------------

    def draw_popup(self, surface):

        overlay = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 150))

        surface.blit(overlay, (0, 0))

        popup_rect = pygame.Rect(
            config.WIDTH // 2 - 300,
            config.HEIGHT // 2 - 110,
            600,
            220,
        )

        draw_soft_shadow(
            surface,
            popup_rect,
            spread=18,
            alpha=80,
        )

        draw_panel(
            surface,
            popup_rect,
            config.PANEL_FILL,
            config.PANEL_BORDER,
        )

        msg = self.fonts["subtitle"].render(
            self.popup_message,
            True,
            config.WHITE,
        )

        surface.blit(
            msg,
            msg.get_rect(
                center=(popup_rect.centerx, popup_rect.y + 75)
            ),
        )

        self.ok_btn.draw(surface)