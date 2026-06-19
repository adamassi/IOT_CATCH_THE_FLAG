# game/screens/game.py

import os
import io
import pygame
import config
from screens.base import Screen
from ui.button import Button
from utils.draw import draw_soft_shadow, draw_panel
from utils.process_runner import ProcessRunner


class GameScreen(Screen):
    def __init__(self, manager, fonts):
        self.manager = manager
        self.fonts = fonts

        # ------------------------------------------------------------
        # Paths:
        #  - Your pygame project is inside a "game/" folder
        #  - 4_main_for_web.py is one directory ABOVE "game/"
        # ------------------------------------------------------------
        # __file__ = .../game/screens/game.py
        # go up 2 levels -> .../game
        # go up 1 more     -> project_root (contains 4_main_for_web.py)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        self.script_path = os.path.join(project_root, "thread_control_test.py")
        self.image_path = os.path.join(project_root, "map-RRTfor_web.png")

        self.runner = ProcessRunner(script_path=self.script_path, workdir=project_root, max_lines=2000)

        # ------------------------------------------------------------
        # Layout: buttons ABOVE the panel
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

        # ------------------------------------------------------------
        # Big centered game panel (pushed down under the buttons)
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

        # ------------------------------------------------------------
        # Panel internal layout
        # ------------------------------------------------------------
        padding = 40

        # Image area (top ~60% of panel)
        img_height = int(self.panel.h * 0.6)
        self.img_rect = pygame.Rect(
            self.panel.x + padding,
            self.panel.y + padding,
            self.panel.w - padding * 2,
            img_height - padding,
        )

        # Log area (bottom)
        self.log_rect = pygame.Rect(
            self.panel.x + padding,
            self.img_rect.bottom + 20,
            self.panel.w - padding * 2,
            self.panel.bottom - (self.img_rect.bottom + 60),
        )

        # Cached image
        self._image = None

        # ------------------------------------------------------------
        # Log scrolling
        # ------------------------------------------------------------
        self.log_scroll_px = 0
        self._line_h = 24
        self._log_padding = 15
        self._auto_follow = True  # follow newest output unless user scrolls up

    # -----------------------
    # Button callbacks
    # -----------------------
    def on_run(self):
        print(f"[GAME] on_run  running={self.runner.state.running}  paused={self.runner.state.paused}")
        # Never start a new process while the current one is paused
        if self.runner.state.paused:
            return
        if not self.runner.state.running:
            self.runner.start("IOT")

    def on_pause(self):
        print(f"[GAME] on_pause  running={self.runner.state.running}  paused={self.runner.state.paused}")
        self.runner.toggle_pause()

    def on_stop(self):
        print(f"[GAME] on_stop  running={self.runner.state.running}  paused={self.runner.state.paused}")
        self.runner.stop()

    # -----------------------
    # Scrolling helpers
    # -----------------------
    def _content_height(self) -> int:
        return len(self.runner.state.stdout_lines) * self._line_h

    def _viewport_height(self) -> int:
        return max(0, self.log_rect.h - 2 * self._log_padding)

    def _max_scroll(self) -> int:
        return max(0, self._content_height() - self._viewport_height())

    def _clamp_log_scroll(self) -> None:
        self.log_scroll_px = max(0, min(self.log_scroll_px, self._max_scroll()))
        # If near bottom again, re-enable follow mode
        if self.log_scroll_px >= self._max_scroll() - self._line_h:
            self._auto_follow = True

    # -----------------------
    # Pygame hooks
    # -----------------------
    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.btn_run.handle_event(event)
        self.btn_pause.handle_event(event)
        self.btn_stop.handle_event(event)

        # Mouse wheel scrolling (only when hovering log area)
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.log_rect.collidepoint(mx, my):
                self._auto_follow = False
                self.log_scroll_px -= event.y * self._line_h * 3  # ~3 lines per notch
                self._clamp_log_scroll()

    def update(self, dt):
        self.runner.poll()
        self._try_load_image()

        # Auto-follow: keep pinned to bottom unless user scrolled up
        if self._auto_follow:
            self.log_scroll_px = self._max_scroll()
        else:
            self._clamp_log_scroll()

    def _try_load_image(self):
    # Throttle reload attempts (avoid fighting the writer on Windows)
        now = pygame.time.get_ticks()
        if not hasattr(self, "_last_img_check_ms"):
            self._last_img_check_ms = 0
            self._last_img_mtime = 0.0

        if now - self._last_img_check_ms < 500:  # check at most 2 times/sec
            return
        self._last_img_check_ms = now

        if not os.path.exists(self.image_path):
            return

        try:
            mtime = os.path.getmtime(self.image_path)
            if mtime == self._last_img_mtime:
                return  # no change since last successful load

            # Read bytes quickly and close file immediately
            with open(self.image_path, "rb") as f:
                data = f.read()

            img = pygame.image.load(io.BytesIO(data))
            iw, ih = img.get_size()
            scale = min(self.img_rect.w / max(iw, 1), self.img_rect.h / max(ih, 1))
            new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))

            self._image = pygame.transform.smoothscale(img, new_size)
            self._last_img_mtime = mtime  # mark successful load

        except PermissionError:
            # File is being written right now — try again next tick
            return
        except Exception:
            # Image might be incomplete mid-write — try again later
            return

    def draw(self, surface):
        # Title
        title = self.fonts["title"].render("Capture The Flag", True, config.WHITE)
        surface.blit(title, title.get_rect(center=(config.WIDTH // 2, 90)))

        # Status
        status = "Idle"
        if self.runner.state.running and not self.runner.state.paused:
            status = "Running"
        elif self.runner.state.paused:
            status = "Paused"
        elif self.runner.state.finished:
            status = "Finished"

        sub = self.fonts["subtitle"].render(f"Game Screen — {status}", True, config.TEXT_DIM)
        surface.blit(sub, sub.get_rect(center=(config.WIDTH // 2, 140)))

        # Pause button label
        self.btn_pause.text = "Resume" if self.runner.state.paused else "Pause"

        # Buttons ABOVE panel
        self.btn_run.draw(surface)
        self.btn_pause.draw(surface)
        self.btn_stop.draw(surface)

        # Panel
        draw_soft_shadow(surface, self.panel, spread=20, alpha=70)
        draw_panel(surface, self.panel, config.PANEL_FILL, config.PANEL_BORDER)

        # Timer
        elapsed = self.runner.elapsed_seconds()
        timer_text = self.fonts["subtitle"].render(f"Time: {elapsed:.1f}s", True, config.TEXT_DIM)
        surface.blit(timer_text, (self.panel.x + 40, self.panel.y + 10))

        # Image box
        pygame.draw.rect(surface, (0, 0, 0), self.img_rect, border_radius=20)
        pygame.draw.rect(surface, (255, 255, 255), self.img_rect, 2, border_radius=20)

        if self._image:
            rect = self._image.get_rect(center=self.img_rect.center)
            surface.blit(self._image, rect)
        else:
            msg = self.fonts["subtitle"].render("Waiting for map-RRTfor_web.png ...", True, config.TEXT_DIM)
            surface.blit(msg, msg.get_rect(center=self.img_rect.center))

        # Log box
        pygame.draw.rect(surface, (0, 0, 0), self.log_rect, border_radius=20)
        pygame.draw.rect(surface, (255, 255, 255), self.log_rect, 2, border_radius=20)

        # Clip log rendering so it NEVER draws outside log_rect
        old_clip = surface.get_clip()
        surface.set_clip(self.log_rect)

        x = self.log_rect.x + self._log_padding
        y = self.log_rect.y + self._log_padding - self.log_scroll_px

        for ln in self.runner.state.stdout_lines:
            txt = self.fonts["subtitle"].render(ln[:220], True, config.WHITE)
            surface.blit(txt, (x, y))
            y += self._line_h

        surface.set_clip(old_clip)

        # Back button
        self.back_btn.draw(surface)