# ui/map_preview.py

import json
import math
import os
import pygame


class MapPreview:
    X_MIN, X_MAX = -5, 5
    Y_MIN, Y_MAX = -2, 2

    BG_COLOR = (0, 0, 0)
    GRID_COLOR = (45, 45, 45)
    BORDER_COLOR = (240, 240, 240)

    OBSTACLE_COLOR = (205, 200, 0)
    OBSTACLE_BORDER = (255, 240, 120)

    GOAL_COLOR = (0, 220, 80)
    GOAL_BORDER = (120, 255, 170)

    TEXT_COLOR = (255, 255, 255)

    def __init__(self, rect, font, json_path):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.json_path = json_path
        self.id_font = pygame.font.SysFont("arial", 26, bold=True)

        self.goals = []
        self.obstacles = []
        self.reload()

    def reload(self):
        if not os.path.exists(self.json_path):
            print(f"Map file not found: {self.json_path}")
            return

        with open(self.json_path, "r") as f:
            data = json.load(f)

        self.goals = data.get("GOALS", [])
        self.obstacles = data.get("OBSTACLES", [])

    def world_to_screen(self, x_pos, y_pos):
        sx = self.rect.x + int(((y_pos - self.Y_MIN) / (self.Y_MAX - self.Y_MIN)) * self.rect.w)
        sy = self.rect.bottom - int(((x_pos - self.X_MIN) / (self.X_MAX - self.X_MIN)) * self.rect.h)
        return sx, sy

    def draw(self, surface):
        pygame.draw.rect(surface, self.BG_COLOR, self.rect, border_radius=18)
        pygame.draw.rect(surface, self.BORDER_COLOR, self.rect, 2, border_radius=18)

        self._draw_grid(surface)

        self._draw_items(surface, self.goals, self.GOAL_COLOR, self.GOAL_BORDER, show_ids=False, enlarge=False)
        self._draw_items(surface, self.obstacles, self.OBSTACLE_COLOR, self.OBSTACLE_BORDER, show_ids=True, enlarge=True)

    def _draw_grid(self, surface):
        for i in range(5):
            x = self.rect.x + int(i * self.rect.w / 4)
            pygame.draw.line(surface, self.GRID_COLOR, (x, self.rect.y), (x, self.rect.bottom), 1)

        for i in range(11):
            y = self.rect.y + int(i * self.rect.h / 10)
            pygame.draw.line(surface, self.GRID_COLOR, (self.rect.x, y), (self.rect.right, y), 1)

    def _draw_items(self, surface, items, fill_color, border_color, show_ids=True, enlarge=False):
        for item in items:
            item_id = item.get("id", "")
            item_type = item.get("type", "polygon")
            coords = item.get("coordinates", [])

            if len(coords) < 3:
                continue

            if item_type == "rectangle":
                center = self._draw_rectangle(surface, coords, fill_color, border_color, enlarge)
            elif item_type == "circle":
                center = self._draw_circle(surface, coords, fill_color, border_color, enlarge)
            else:
                center = self._draw_polygon(surface, coords, fill_color, border_color)

            if show_ids:
                self._draw_id(surface, item_id, center)

    def _draw_rectangle(self, surface, coords, fill_color, border_color, enlarge=False):
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        top_left = self.world_to_screen(max_x, min_y)
        bottom_right = self.world_to_screen(min_x, max_y)

        rect = pygame.Rect(
            top_left[0],
            top_left[1],
            bottom_right[0] - top_left[0],
            bottom_right[1] - top_left[1],
        )

        if enlarge:
            rect.inflate_ip(6, 6)

        pygame.draw.rect(surface, fill_color, rect)
        pygame.draw.rect(surface, border_color, rect, 2)

        return rect.center

    def _draw_circle(self, surface, coords, fill_color, border_color, enlarge=False):
        # Estimate center from the polygon points in JSON
        cx = sum(p[0] for p in coords) / len(coords)
        cy = sum(p[1] for p in coords) / len(coords)

        center = self.world_to_screen(cx, cy)

        # Fixed visual radius so it is always a true circle and readable
        radius = 18 if enlarge else 10

        pygame.draw.circle(surface, fill_color, center, radius)
        pygame.draw.circle(surface, border_color, center, radius, 2)

        return center

    def _draw_polygon(self, surface, coords, fill_color, border_color):
        points = [self.world_to_screen(x, y) for x, y in coords]

        pygame.draw.polygon(surface, fill_color, points)
        pygame.draw.polygon(surface, border_color, points, 2)

        avg_x = sum(p[0] for p in points) // len(points)
        avg_y = sum(p[1] for p in points) // len(points)

        return avg_x, avg_y

    def _draw_id(self, surface, item_id, center):
        text = self.id_font.render(str(item_id), True, self.TEXT_COLOR)
        surface.blit(text, text.get_rect(center=center))