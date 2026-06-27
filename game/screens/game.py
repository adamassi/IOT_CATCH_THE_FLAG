# game/screens/game.py

import os
import io
import json
import pygame
import config

from screens.base import Screen
from ui.button import Button
from ui.text_input import TextInput
from ui.mute_button import MuteButton
from utils.draw import draw_soft_shadow, draw_panel
from utils.process_runner import ProcessRunner


class GameScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.script_path = os.path.join(project_root, "thread_control_test.py")
        self.image_path = os.path.join(project_root, "map-RRTfor_web.png")
        self.cube_bank_path = os.path.join(project_root, "cube_bank.json")

        self.runner = ProcessRunner(
            script_path=self.script_path,
            workdir=project_root,
            max_lines=2000,
        )

        # ------------------------------------------------------------
        # Buttons above panel
        # ------------------------------------------------------------
        btn_w, btn_h = 220, 70
        gap = 40
        total_w = 3 * btn_w + 2 * gap
        start_x = config.WIDTH // 2 - total_w // 2
        btn_y = 170

        self.btn_run = Button(
            "Run",
            (start_x, btn_y, btn_w, btn_h),
            fonts["button"],
            config.ACCENT,
            config.ACCENT_HOVER,
            config.WHITE,
            on_click=self.on_run,
        )

        self.btn_pause = Button(
            "Pause",
            (start_x + btn_w + gap, btn_y, btn_w, btn_h),
            fonts["button"],
            config.BTN,
            config.BTN_HOVER,
            config.WHITE,
            on_click=self.on_pause,
        )

        self.btn_stop = Button(
            "Stop",
            (start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h),
            fonts["button"],
            config.DANGER,
            config.DANGER_HOVER,
            config.WHITE,
            on_click=self.on_stop,
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

        self.mute_btn = MuteButton(
            (config.WIDTH - 95, 35, 60, 55),
            fonts["button"],
        )

        # ------------------------------------------------------------
        # Main panel
        # ------------------------------------------------------------
        margin_x = 150
        panel_top = 260
        panel_bottom_margin = 90

        self.panel = pygame.Rect(
            margin_x,
            panel_top,
            config.WIDTH - margin_x * 2,
            config.HEIGHT - panel_top - panel_bottom_margin,
        )

        padding = 40

        # ------------------------------------------------------------
        # Word input area
        # ------------------------------------------------------------
        self.word_input = TextInput(
            rect=(self.panel.x + 40, self.panel.y + 50, 320, 55),
            font=fonts["subtitle"],
            text_color=config.WHITE,
            bg_color=(0, 0, 0),
            border_color=config.ACCENT,
            placeholder="Enter word",
            input_type="text",
            max_length=20,
        )

        self.word_message = "Enter a word before running."
        self.available_cubes = []
        self.reload_cube_bank()

        # ------------------------------------------------------------
        # Image and log areas
        # ------------------------------------------------------------
        input_area_height = 145
        img_height = int(self.panel.h * 0.50)

        self.img_rect = pygame.Rect(
            self.panel.x + padding,
            self.panel.y + input_area_height,
            self.panel.w - padding * 2,
            img_height,
        )

        self.log_rect = pygame.Rect(
            self.panel.x + padding,
            self.img_rect.bottom + 20,
            self.panel.w - padding * 2,
            self.panel.bottom - (self.img_rect.bottom + 60),
        )

        self._image = None

        # ------------------------------------------------------------
        # Log scrolling
        # ------------------------------------------------------------
        self.log_scroll_px = 0
        self._line_h = 24
        self._log_padding = 15
        self._auto_follow = True

    # ------------------------------------------------------------
    # Cube bank / word validation
    # ------------------------------------------------------------

    def reload_cube_bank(self):
        try:
            with open(self.cube_bank_path, "r") as f:
                data = json.load(f)

            self.available_cubes = data.get("CUBES", [])

        except Exception:
            self.available_cubes = []

    def get_available_letters(self):
        return [
            cube.get("letter", "").upper()
            for cube in self.available_cubes
        ]

    def can_form_word(self, word):
        available = self.get_available_letters()

        for letter in word.upper():
            if letter not in available:
                return False

            available.remove(letter)

        return True

    # ------------------------------------------------------------
    # Button callbacks
    # ------------------------------------------------------------

    def on_run(self):
        word = self.word_input.text.strip().upper()

        if not word:
            self.word_message = "Please enter a word."
            return

        self.reload_cube_bank()

        if not self.can_form_word(word):
            available = "".join(self.get_available_letters())
            self.word_message = f"Invalid word. Available letters: {available}"
            return

        if not self.runner.state.running:
            self.runner.start(word)
            self.word_message = f"Running word: {word}"

    def on_pause(self):
        self.runner.toggle_pause()

    def on_stop(self):
        self.runner.stop()

    # ------------------------------------------------------------
    # Log scrolling helpers
    # ------------------------------------------------------------

    def _content_height(self) -> int:
        return len(self.runner.state.stdout_lines) * self._line_h

    def _viewport_height(self) -> int:
        return max(0, self.log_rect.h - 2 * self._log_padding)

    def _max_scroll(self) -> int:
        return max(0, self._content_height() - self._viewport_height())

    def _clamp_log_scroll(self) -> None:
        self.log_scroll_px = max(0, min(self.log_scroll_px, self._max_scroll()))

        if self.log_scroll_px >= self._max_scroll() - self._line_h:
            self._auto_follow = True

    # ------------------------------------------------------------
    # Pygame hooks
    # ------------------------------------------------------------

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.btn_run.handle_event(event)
        self.btn_pause.handle_event(event)
        self.btn_stop.handle_event(event)
        self.mute_btn.handle_event(event)

        self.word_input.handle_event(event)

        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()

            if self.log_rect.collidepoint(mx, my):
                self._auto_follow = False
                self.log_scroll_px -= event.y * self._line_h * 3
                self._clamp_log_scroll()

    def update(self, dt):
        self.runner.poll()
        self._try_load_image()

        if self._auto_follow:
            self.log_scroll_px = self._max_scroll()
        else:
            self._clamp_log_scroll()

    def _try_load_image(self):
        now = pygame.time.get_ticks()

        if not hasattr(self, "_last_img_check_ms"):
            self._last_img_check_ms = 0
            self._last_img_mtime = 0.0

        if now - self._last_img_check_ms < 500:
            return

        self._last_img_check_ms = now

        if not os.path.exists(self.image_path):
            return

        try:
            mtime = os.path.getmtime(self.image_path)

            if mtime == self._last_img_mtime:
                return

            with open(self.image_path, "rb") as f:
                data = f.read()

            img = pygame.image.load(io.BytesIO(data))

            iw, ih = img.get_size()
            scale = min(
                self.img_rect.w / max(iw, 1),
                self.img_rect.h / max(ih, 1),
            )

            new_size = (
                max(1, int(iw * scale)),
                max(1, int(ih * scale)),
            )

            self._image = pygame.transform.smoothscale(img, new_size)
            self._last_img_mtime = mtime

        except PermissionError:
            return

        except Exception:
            return

    # ------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------

    def draw(self, surface):
        title = self.fonts["title"].render(
            "Capture The Flag",
            True,
            config.WHITE,
        )
        surface.blit(
            title,
            title.get_rect(center=(config.WIDTH // 2, 90)),
        )

        status = "Idle"

        if self.runner.state.running and not self.runner.state.paused:
            status = "Running"

        elif self.runner.state.paused:
            status = "Paused"

        elif self.runner.state.finished:
            status = "Finished"

        sub = self.fonts["subtitle"].render(
            f"Game Screen — {status}",
            True,
            config.TEXT_DIM,
        )
        surface.blit(
            sub,
            sub.get_rect(center=(config.WIDTH // 2, 140)),
        )

        self.btn_pause.text = "Resume" if self.runner.state.paused else "Pause"

        self.btn_run.draw(surface)
        self.btn_pause.draw(surface)
        self.btn_stop.draw(surface)

        draw_soft_shadow(surface, self.panel, spread=20, alpha=70)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        # Timer
        elapsed = self.runner.elapsed_seconds()
        timer_text = self.fonts["subtitle"].render(
            f"Time: {elapsed:.1f}s",
            True,
            config.TEXT_DIM,
        )
        surface.blit(
            timer_text,
            (self.panel.x + 40, self.panel.y + 10),
        )

        self.word_input.draw(surface)

        # Available cubes
        self.reload_cube_bank()

        cube_text = "Available letters: " + ", ".join(
            cube.get("letter", "?")
            for cube in self.available_cubes
        )

        cubes_label = self.fonts["subtitle"].render(
            cube_text,
            True,
            config.TEXT_DIM,
        )
        surface.blit(
            cubes_label,
            (self.panel.x + 390, self.panel.y + 60),
        )

        # Word validation message
        is_error = (
            self.word_message.startswith("Invalid")
            or self.word_message.startswith("Please")
        )

        msg_color = config.DANGER if is_error else config.TEXT_DIM

        msg = self.fonts["subtitle"].render(
            self.word_message,
            True,
            msg_color,
        )
        surface.blit(
            msg,
            (self.panel.x + 40, self.panel.y + 112),
        )

        # Image box
        pygame.draw.rect(
            surface,
            (0, 0, 0),
            self.img_rect,
            border_radius=20,
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            self.img_rect,
            2,
            border_radius=20,
        )

        if self._image:
            rect = self._image.get_rect(center=self.img_rect.center)
            surface.blit(self._image, rect)

        else:
            waiting = self.fonts["subtitle"].render(
                "Waiting for map-RRTfor_web.png ...",
                True,
                config.TEXT_DIM,
            )
            surface.blit(
                waiting,
                waiting.get_rect(center=self.img_rect.center),
            )

        # Log box
        pygame.draw.rect(
            surface,
            (0, 0, 0),
            self.log_rect,
            border_radius=20,
        )
        pygame.draw.rect(
            surface,
            (255, 255, 255),
            self.log_rect,
            2,
            border_radius=20,
        )

        old_clip = surface.get_clip()
        surface.set_clip(self.log_rect)

        x = self.log_rect.x + self._log_padding
        y = self.log_rect.y + self._log_padding - self.log_scroll_px

        for ln in self.runner.state.stdout_lines:
            txt = self.fonts["subtitle"].render(
                ln[:220],
                True,
                config.WHITE,
            )
            surface.blit(txt, (x, y))
            y += self._line_h

        surface.set_clip(old_clip)

        self.back_btn.draw(surface)
        self.mute_btn.draw(surface)