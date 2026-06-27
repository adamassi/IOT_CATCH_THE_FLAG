import os
import re
import pygame
import config

from screens.base import Screen
from ui.button import Button
from ui.slider import OptionSlider
from utils.draw import draw_soft_shadow, draw_panel


class RobotConfigScreen(Screen):
    UI_TO_CONFIG = {
        "RRT": "RRT_STAR",
        "A*": "ASTAR",
        "RCS": "RCS",
    }

    CONFIG_TO_UI = {
        "RRT_STAR": "RRT",
        "ASTAR": "A*",
        "RCS": "RCS",
    }

    DESCRIPTIONS = {
        "RRT": "RRT*: Good for exploring continuous spaces and complex maps.",
        "A*": "A*: Finds an efficient path on a known graph/map.",
        "RCS": "RCS: Custom planner for the cube retrieval strategy.",
    }

    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.parameters_path = os.path.join(project_root, "PARAMETERS.py")

        self.panel = pygame.Rect(config.WIDTH // 2 - 420, 210, 840, 500)

        self.algorithm_slider = OptionSlider(
            rect=(config.WIDTH // 2 - 300, 560, 600, 80),
            options=["RRT", "A*", "RCS"],
            font=fonts["subtitle"],
            text_color=config.WHITE,
            knob_color=config.ACCENT,
            line_color=config.TEXT_DIM,
        )

        self._load_current_algorithm()
        self.message = f"Current planner: {self.algorithm_slider.value}"

        self.back_btn = Button(
            "Back",
            (40, 40, 140, 55),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("configure"),
        )

    def _load_current_algorithm(self):
        try:
            with open(self.parameters_path, "r") as f:
                content = f.read()

            match = re.search(r'ALGORITHM\s*=\s*["\']([^"\']+)["\']', content)
            if not match:
                return

            config_value = match.group(1)
            ui_value = self.CONFIG_TO_UI.get(config_value, "RRT")

            if ui_value in self.algorithm_slider.options:
                self.algorithm_slider.index = self.algorithm_slider.options.index(ui_value)

        except Exception as e:
            print("Could not load PlannerConfig.ALGORITHM:", e)

    def _save_algorithm(self, ui_value):
        config_value = self.UI_TO_CONFIG[ui_value]

        try:
            with open(self.parameters_path, "r") as f:
                content = f.read()

            new_content = re.sub(
                r'ALGORITHM\s*=\s*["\'][^"\']+["\']',
                f'ALGORITHM = "{config_value}"',
                content,
                count=1,
            )

            with open(self.parameters_path, "w") as f:
                f.write(new_content)

            self.message = f"Planner changed to {ui_value} ({config_value})"

        except Exception as e:
            self.message = "Failed to update PARAMETERS.py"
            print("Error updating PlannerConfig.ALGORITHM:", e)

    def handle_event(self, event):
        self.back_btn.handle_event(event)

        old_value = self.algorithm_slider.value
        self.algorithm_slider.handle_event(event)
        new_value = self.algorithm_slider.value

        if new_value != old_value:
            self._save_algorithm(new_value)

    def update(self, dt):
        pass

    def draw(self, surface):
        title = self.fonts["title"].render("Robot Configuration", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 100)))

        sub = self.fonts["subtitle"].render("Choose robot settings", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 150)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        label = self.fonts["subtitle"].render(
            f"Algorithm: {self.algorithm_slider.value}",
            True,
            config.TEXT_DIM,
        )
        surface.blit(label, label.get_rect(center=(config.WIDTH // 2, 370)))

        desc = self.DESCRIPTIONS.get(self.algorithm_slider.value, "")
        desc_surface = self.fonts["subtitle"].render(desc, True, config.TEXT_DIM)
        surface.blit(desc_surface, desc_surface.get_rect(center=(config.WIDTH // 2, 430)))

        self.algorithm_slider.draw(surface)

        msg = self.fonts["subtitle"].render(self.message, True, config.TEXT_DIM)
        surface.blit(msg, msg.get_rect(center=(config.WIDTH // 2, 675)))

        self.back_btn.draw(surface)