import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 20
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Initialize screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Capture The Flag - Pygame Interface")
clock = pygame.time.Clock()

# Obstacles, car, and destination
obstacles = [(5, 5), (6, 5), (7, 5), (8, 5)]  # Example obstacles
car_position = [2, 2]  # Starting position
path = []  # Path taken by the car
destination = (15, 15)

def draw_grid():
    """Draw the grid on the screen."""
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WINDOW_WIDTH, y))

def draw_obstacles():
    """Draw obstacles on the grid."""
    for obstacle in obstacles:
        rect = pygame.Rect(obstacle[0] * GRID_SIZE, obstacle[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect)

def draw_car():
    """Draw the car on the grid."""
    rect = pygame.Rect(car_position[0] * GRID_SIZE, car_position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, BLUE, rect)

def draw_destination():
    """Draw the destination on the grid."""
    rect = pygame.Rect(destination[0] * GRID_SIZE, destination[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, GREEN, rect)

def draw_path():
    """Draw the path taken by the car."""
    for pos in path:
        rect = pygame.Rect(pos[0] * GRID_SIZE + GRID_SIZE // 4, pos[1] * GRID_SIZE + GRID_SIZE // 4, GRID_SIZE // 2, GRID_SIZE // 2)
        pygame.draw.rect(screen, BLUE, rect)

# Main loop
running = True
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_obstacles()
    draw_path()
    draw_car()
    draw_destination()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Example movement logic (move in a curve toward destination)
    if car_position != list(destination):
        path.append(tuple(car_position))
        dx = destination[0] - car_position[0]
        dy = destination[1] - car_position[1]
        angle = math.atan2(dy, dx)
        car_position[0] += round(math.cos(angle) * 1)  # Adjusted to round for visible movement
        car_position[1] += round(math.sin(angle) * 1)  # Adjusted to round for visible movement

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()