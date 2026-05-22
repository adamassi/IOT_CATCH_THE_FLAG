import pygame


class MapPreview:
    """
    Simple pygame map preview.
    Coordinates follow your matplotlib map idea:
    X axis vertical: -5 to 5
    Y axis horizontal: -2 to 2
    """

    def __init__(self, rect, font):
        self.rect = pygame.Rect(rect)
        self.font = font

        # Example objects for UI preview only
        self.obstacles = [
            {"id": 101, "rect": (-1.5, 3.0, 0.4, 1.2)},
            {"id": 102, "rect": (0.2, 2.2, 0.3, 1.4)},
            {"id": 103, "rect": (-0.8, -0.5, 0.5, 0.8)},
            {"id": 104, "rect": (0.9, -3.2, 0.4, 1.0)},
        ]

        self.goals = [
            {"label": "G1", "pos": (-1.2, 4.0)},
            {"label": "G2", "pos": (1.0, 3.5)},
        ]

        self.cubes = [
            {"label": "C1", "pos": (-0.5, 1.4)},
            {"label": "C2", "pos": (0.7, -1.0)},
        ]

        self.robot = {"label": "R", "pos": (0.0, 0.0)}

    def world_to_screen(self, y_pos, x_pos):
        """
        y_pos: horizontal coordinate, range [-2, 2]
        x_pos: vertical coordinate, range [-5, 5]
        """
        sx = self.rect.x + int(((y_pos + 2) / 4) * self.rect.w)
        sy = self.rect.bottom - int(((x_pos + 5) / 10) * self.rect.h)
        return sx, sy

    def draw(self, surface):
        pygame.draw.rect(surface, (5, 5, 5), self.rect, border_radius=18)
        pygame.draw.rect(surface, (240, 240, 240), self.rect, 2, border_radius=18)

        self._draw_grid(surface)
        self._draw_obstacles(surface)
        self._draw_goals(surface)
        self._draw_cubes(surface)
        self._draw_robot(surface)

    def _draw_grid(self, surface):
        grid_color = (45, 45, 45)

        for i in range(5):
            x = self.rect.x + int(i * self.rect.w / 4)
            pygame.draw.line(surface, grid_color, (x, self.rect.y), (x, self.rect.bottom), 1)

        for i in range(11):
            y = self.rect.y + int(i * self.rect.h / 10)
            pygame.draw.line(surface, grid_color, (self.rect.x, y), (self.rect.right, y), 1)

    def _draw_obstacles(self, surface):
        for obs in self.obstacles:
            y, x, w, h = obs["rect"]

            top_left = self.world_to_screen(y, x + h)
            bottom_right = self.world_to_screen(y + w, x)

            rect = pygame.Rect(
                top_left[0],
                top_left[1],
                bottom_right[0] - top_left[0],
                bottom_right[1] - top_left[1],
            )

            pygame.draw.rect(surface, (210, 190, 30), rect)
            pygame.draw.rect(surface, (255, 240, 120), rect, 2)

            label = self.font.render(str(obs["id"]), True, (255, 255, 255))
            surface.blit(label, label.get_rect(center=rect.center))

    def _draw_goals(self, surface):
        for goal in self.goals:
            sx, sy = self.world_to_screen(*goal["pos"])
            pygame.draw.circle(surface, (0, 220, 80), (sx, sy), 12)
            label = self.font.render(goal["label"], True, (255, 255, 255))
            surface.blit(label, (sx + 14, sy - 10))

    def _draw_cubes(self, surface):
        for cube in self.cubes:
            sx, sy = self.world_to_screen(*cube["pos"])
            rect = pygame.Rect(sx - 9, sy - 9, 18, 18)
            pygame.draw.rect(surface, (80, 160, 255), rect)
            label = self.font.render(cube["label"], True, (255, 255, 255))
            surface.blit(label, (sx + 12, sy - 10))

    def _draw_robot(self, surface):
        sx, sy = self.world_to_screen(*self.robot["pos"])
        pygame.draw.circle(surface, (240, 70, 70), (sx, sy), 14)
        label = self.font.render("Robot", True, (255, 255, 255))
        surface.blit(label, (sx + 16, sy - 10))