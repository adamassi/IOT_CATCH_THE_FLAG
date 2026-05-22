import json
import os

from shapely.geometry import Polygon  # For creating geometric shapes
import numpy as np  # For mathematical operations like cosine and sine
from path_algorithms.map_json_utils import write_cubes_json, append_obstacle_to_json

def is_within_boundaries(env, points):
    """
    Check if all points of an obstacle are within the map boundaries.
    Args:
        env (MapEnvironment): The planning environment object.
        points (list): List of [x, z] coordinates of the obstacle.
    Returns:
        bool: True if all points are within boundaries, False otherwise.
    """
    for x, z in points:
        if x < env.xlimit[0] or x > env.xlimit[1] or z < env.ylimit[0] or z > env.ylimit[1]:
            return False
    return True

def clear_dynamic_cubes():
    """
    Clears the dynamic cubes file, preparing for a new batch of cubes.
    Call this before starting to add a new set of dynamic obstacles.
    """
    cubes_path = os.path.join(os.getcwd(), "path_algorithms/cubes.json")
    write_cubes_json(cubes_path, [])

def add_circle_obstacle(env, circle_pos, radius=0.09):
    """
    Adds a circular obstacle to the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        circle_pos (list): The [x, y, z] position of the circle (only x and z used).
        radius (float): The radius of the circle in meters.
    """
    cx, cz = circle_pos[0], circle_pos[2]
    obstacle_points = [(cx + radius * np.cos(theta), cz + radius * np.sin(theta)) for theta in np.linspace(0, 2 * np.pi, 100)]
    
    if not is_within_boundaries(env, obstacle_points):
        # print(f"Error: {e}")
        raise ValueError(f"Circle obstacle at position {circle_pos} with radius {radius}m is outside the map boundaries.")
    
    obstacle = Polygon(obstacle_points)
    env.obstacles.append(obstacle)
    # print(f"Added circle obstacle at position {circle_pos} with radius {radius}m.")

def add_cube_obstacle(env, cube_pos, size=0.23):
    """
    Adds a square obstacle representing a cube to the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        cube_pos (list): The [x, y, z] position of the cube (only x and z used).
        size (float): The size of the cube (side length in meters).
    """
    cx, cz = cube_pos[0], cube_pos[2]
    half = size / 2
    obstacle_points = [
        [cx - half, cz - half],
        [cx + half, cz - half],
        [cx + half, cz + half],
        [cx - half, cz + half],
        [cx - half, cz - half]
    ]
    
    if not is_within_boundaries(env, obstacle_points):
        # print(f"Error: Cube obstacle at position {cube_pos} with size {size}m is outside the map boundaries.")
        raise ValueError(f"Cube obstacle at position {cube_pos} with size {size}m is outside the map boundaries.")
    
    obstacle = Polygon(obstacle_points)
    env.obstacles.append(obstacle)

    # Append cube to cubes.json
    cubes_path = os.path.join(os.getcwd(), "path_algorithms/cubes.json")
    append_obstacle_to_json(cubes_path, 'CUBES', obstacle_points)
    # print(f"Added cube obstacle at position {cube_pos} with size {size}m.")
def remove_cube_obstacle(env, number_of_cubes_to_remove):
    """
    Removes the most recently added cube obstacles from the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        number_of_cubes_to_remove (int): The number of cube obstacles to remove.
    """
    # Remove the last 'number_of_cubes_to_remove' obstacles from the environment
    for _ in range(number_of_cubes_to_remove):
        if env.obstacles:
            removed_obstacle = env.obstacles.pop()
            # print(f"Removed cube obstacle: {removed_obstacle}")
        else:
            # print("No more obstacles to remove.")
            break
        
def add_rectangle_obstacle(env, center_pos, width=0.25, height=0.7):
    """
    Adds a rectangular obstacle to the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        center_pos (list): The [x, y, z] position of the rectangle's center (only x and z used).
        width (float): The width of the rectangle along the x-axis.
        height (float): The height of the rectangle along the z-axis.
    """
    cx, cz = center_pos[0], center_pos[2]
    half_w, half_h = width / 2, height / 2
    obstacle_points = [
        [cx - half_w, cz - half_h],
        [cx + half_w, cz - half_h],
        [cx + half_w, cz + half_h],
        [cx - half_w, cz + half_h],
        [cx - half_w, cz - half_h]  # Close the loop
    ]
    
    if not is_within_boundaries(env, obstacle_points):
        raise ValueError(f"Rectangle obstacle at position {center_pos} with width {width}m and height {height}m is outside the map boundaries.")
    
    obstacle = Polygon(obstacle_points)
    env.obstacles.append(obstacle)
    print("********************************************************************************************")
    print(f"Added rectangle obstacle at position {center_pos} with width {width}m and height {height}m.")
    print("********************************************************************************************")




