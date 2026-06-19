# screens/manual_control.py

import os
import sys
import pygame
import config

from screens.base import Screen
from ui.button import Button
from ui.value_slider import ValueSlider
from utils.draw import draw_soft_shadow, draw_panel


class ManualControlScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if project_root not in sys.path:
            sys.path.append(project_root)

        try:
            from robotCommands import (
                send_servo_request,
                send_go_request,
                send_speed_request,
                send_stop_request,
                send_back_request,
                send_left_request,
                send_right_request,
                send_steer_request,
            )

            self.send_servo_request = send_servo_request
            self.send_go_request = send_go_request
            self.send_speed_request = send_speed_request
            self.send_stop_request = send_stop_request
            self.send_back_request = send_back_request
            self.send_left_request = send_left_request
            self.send_right_request = send_right_request
            self.send_steer_request = send_steer_request

        except Exception as e:
            print("Could not import robotCommands:", e)

            self.send_servo_request = lambda angle=45: None
            self.send_go_request = lambda: None
            self.send_speed_request = lambda speed=250: None
            self.send_stop_request = lambda: None
            self.send_back_request = lambda speed=0: None
            self.send_left_request = lambda: None
            self.send_right_request = lambda: None
            self.send_steer_request = lambda left=0, right=0: None

        self.panel = pygame.Rect(
            180,
            190,
            config.WIDTH - 360,
            config.HEIGHT - 280,
        )

        self.back_btn = Button(
            "Back",
            (40, 40, 140, 55),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=lambda: self.manager.go_to("menu"),
        )

        slider_w = 620
        slider_x = config.WIDTH // 2 - slider_w // 2

        # Angle is now 0 -> 90
        self.angle_slider = ValueSlider(
            rect=(slider_x, self.panel.y + 130, slider_w, 40),
            min_value=0,
            max_value=90,
            initial_value=45,
            font=fonts["subtitle"],
            label="Arm Angle",
            text_color=config.WHITE,
            line_color=config.TEXT_DIM,
            knob_color=config.ACCENT,
            on_change=self.on_angle_changed,
            step=1,
        )

        # Speed is -255 -> 255
        self.speed_slider = ValueSlider(
            rect=(slider_x, self.panel.y + 270, slider_w, 40),
            min_value=-255,
            max_value=255,
            initial_value=0,
            font=fonts["subtitle"],
            label="Speed",
            text_color=config.WHITE,
            line_color=config.TEXT_DIM,
            knob_color=config.ACCENT,
            on_change=self.on_speed_changed,
            step=5,
        )

        # -------------------------------------------------
        # Direction buttons — spaced so they do not overlap
        # -------------------------------------------------

        center_x = config.WIDTH // 2
        base_y = self.panel.y + 410

        btn_w = 170
        btn_h = 60
        gap = 35

        self.forward_btn = Button(
            "Forward",
            (center_x - btn_w // 2, base_y, btn_w, btn_h),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.forward,
        )

        row_y = base_y + btn_h + gap

        self.left_btn = Button(
            "Left",
            (center_x - int(1.5 * btn_w) - gap, row_y, btn_w, btn_h),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=self.left,
        )

        self.stop_btn = Button(
            "Stop",
            (center_x - btn_w // 2, row_y, btn_w, btn_h),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=self.stop,
        )

        self.right_btn = Button(
            "Right",
            (center_x + btn_w // 2 + gap, row_y, btn_w, btn_h),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=self.right,
        )

        self.backward_btn = Button(
            "Backward",
            (center_x - btn_w // 2, row_y + btn_h + gap, btn_w, btn_h),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=self.backward,
        )

        self.buttons = [
            self.forward_btn,
            self.left_btn,
            self.stop_btn,
            self.right_btn,
            self.backward_btn,
        ]

        self.status_message = "Manual control ready"

    def on_angle_changed(self, angle):
        self.send_servo_request(angle)
        self.status_message = f"Arm angle set to {angle}°"

    def on_speed_changed(self, speed):
        speed = int(speed)
        self.send_speed_request(speed)
        if speed == 0:
            self.status_message = "Speed set to 0 — stopped"
        elif speed > 0:
            self.status_message = f"Moving forward at speed {speed}"
        else:
            self.status_message = f"Moving backward at speed {abs(speed)}"

    def forward(self):
        self.send_go_request()
        self.status_message = "Forward command sent"

    def backward(self):
        try:
            self.send_back_request(abs(self.speed_slider.value))
        except TypeError:
            self.send_back_request()

        self.status_message = "Backward command sent"

    def stop(self):
        self.speed_slider.value = 0
        self.send_stop_request()
        self.status_message = "Stop command sent"

    def left(self):
        self.send_left_request()
        self.status_message = "Left command sent"

    def right(self):
        self.send_right_request()
        self.status_message = "Right command sent"

    def handle_event(self, event):
        self.back_btn.handle_event(event)

        self.angle_slider.handle_event(event)
        self.speed_slider.handle_event(event)

        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt):
        pass

    def draw(self, surface):
        title = self.fonts["title"].render("Manual Control", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 90)))

        sub = self.fonts["subtitle"].render(
            "Control the robot car manually",
            True,
            config.TEXT_DIM,
        )
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        draw_soft_shadow(surface, self.panel, spread=18, alpha=65)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        self.angle_slider.draw(surface)
        self.speed_slider.draw(surface)

        for button in self.buttons:
            button.draw(surface)

        status = self.fonts["subtitle"].render(
            self.status_message,
            True,
            config.TEXT_DIM,
        )
        surface.blit(
            status,
            status.get_rect(center=(config.WIDTH // 2, self.panel.bottom - 35)),
        )

        self.back_btn.draw(surface)