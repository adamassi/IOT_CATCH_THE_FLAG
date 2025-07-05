import os
import time
from datetime import datetime
import json
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
from matplotlib import patches as pat
from matplotlib import collections as coll
from numpy.core.fromnumeric import size
from shapely.geometry import Point, LineString, Polygon
import imageio
import sys
# 2.71, 0.14, 1.06
# add circle obstacles function
def add_circle_obstacle(env, circle_pos, radius=0.09):
    """
    Adds a circular obstacle to the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        circle_pos (list): The [x, y, z] position of the circle (only x and z used).
        radius (float): The radius of the circle in meters.
    """
    cx, cz = circle_pos[0], circle_pos[2]
    obstacle = Polygon([(cx + radius * np.cos(theta), cz + radius * np.sin(theta)) for theta in np.linspace(0, 2 * np.pi, 100)])
    env.obstacles.append(obstacle)
    print(f"Added circle obstacle at position {circle_pos} with radius {radius}m.")
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
    obstacle = [
        [cx - half, cz - half],
        [cx + half, cz - half],
        [cx + half, cz + half],
        [cx - half, cz + half],
        [cx - half, cz - half]
    ]
    env.obstacles.append(Polygon(obstacle))

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
    obstacle = [
        [cx - half_w, cz - half_h],
        [cx + half_w, cz - half_h],
        [cx + half_w, cz + half_h],
        [cx - half_w, cz + half_h],
        [cx - half_w, cz - half_h]  # Close the loop
    ]
    print(f"Adding rectangle obstacle at position {center_pos} with width {width}m and height {height}m.")
    print(obstacle)
    env.obstacles.append(Polygon(obstacle))


class MapEnvironment(object):
    
    def __init__(self, json_file):

        # check if json file exists and load
        json_path = os.path.join(os.getcwd(), json_file)
        print(f'Loading map from {json_path}...')
        if not os.path.isfile(json_path):
            raise ValueError('Json file does not exist!');
        with open(json_path) as f:
            json_dict = json.load(f)

        # obtain boundary limits, start and inspection points
        self.xlimit = [-4.0, json_dict['WIDTH']]
        self.ylimit = [-2, json_dict['HEIGHT']]
        # print(f'World limits: x={self.xlimit}, y={self.ylimit}')
        # print(f'Start point: {json_dict["START"]}, Goal point: {json_dict["GOAL"]}')
        self.start = np.array(json_dict['START'])
        self.goal = np.array(json_dict['GOAL'])
        self.load_obstacles(obstacles=json_dict['OBSTACLES'])
        # add circle obstacles in the map in  [2.71, 1.06]
        add_circle_obstacle(self, [2.71, 0.14, 1.06])
        # add_cube_obstacle(self, [2.71, 0.14, 1.06])

        add_rectangle_obstacle(self, [1.6, 0.24, 0.06], width=0.25, height=0.7)
        # adding pyramid obstacle
        add_rectangle_obstacle(self, [1.97, 0.12, 0.40], width=0.6, height=0.25)



        # test ithe valueError
        add_cube_obstacle(self, [-4.14, 0.14, 1.06])
        # check that the start location is within limits and collision free
        if not self.state_validity_checker(state=self.start):
            
            raise ValueError('Start state must be within the map limits');

        # check that the goal location is within limits and collision free
        if not self.state_validity_checker(state=self.goal):
            raise ValueError('Goal state must be within the map limits');

        # if you want to - you can display starting map here
        #self.visualize_map()

    def load_obstacles(self, obstacles):
        '''
        A function to load and verify scene obstacles.
        @param obstacles A list of lists of obstacles points.
        '''
        # iterate over all obstacles
        self.obstacles, self.obstacles_edges = [], []
        for obstacle in obstacles:
            non_applicable_vertices = [x[0] < self.xlimit[0] or x[0] > self.xlimit[1] or x[1] < self.ylimit[0] or x[1] > self.ylimit[1] for x in obstacle]
            if any(non_applicable_vertices):
                # Raise an error if any obstacle overlaps with the map boundaries, ensuring all obstacles are within valid limits.
                # print(f'OOOOObstacle {obstacle} overlaps with the map boundaries: {self.xlimit}, {self.ylimit}')
                print('An obstacle coincides with the maps boundaries!', file=sys.stderr)
                raise ValueError('An obstacle coincides with the maps boundaries!')
            
            # make sure that the obstacle is a closed form
            if obstacle[0] != obstacle[-1]:
                obstacle.append(obstacle[0])
                self.obstacles_edges.append([LineString([Point(x[0],x[1]),Point(y[0],y[1])]) for (x,y) in zip(obstacle[:-1], obstacle[1:])])
            self.obstacles.append(Polygon(obstacle))

    def compute_distance(self, start_state, end_state):
        '''
        Return the Euclidean distance between two states.
        @param start_state The starting state (position) of the robot.
        @param end_state The target state (position) of the robot.
        '''
        return np.linalg.norm(np.array(end_state) - np.array(start_state))

    def state_validity_checker(self, state):
        '''
        Verify that the state is in the world boundaries, and is not inside an obstacle.
        Return false if the state is not applicable, and true otherwise.
        @param state The given position of the robot.
        '''

        # make sure robot state is a numpy array
        if not isinstance(state, np.ndarray):
            state = np.array(state)

        # verify that the robot position is between world boundaries
        if state[0] < self.xlimit[0] or state[1] < self.ylimit[0] or state[0] > self.xlimit[1] or state[1] > self.ylimit[1]:
            return False

        # verify that the robot is not positioned inside an obstacle
        for obstacle in self.obstacles:
            if obstacle.intersects(Point(state[0], state[1])):
                return False

        return True

    def edge_validity_checker(self, state1, state2):
        '''
        A function to check if the edge between two states is free from collisions. The function will return False if the edge intersects another obstacle.
        @param state1 The source state of the robot.
        @param state2 The destination state of the robot.
        '''

        # # define undirected edge
        # given_edge = LineString([state1, state2])

        # # verify that the robot does not crossing any obstacle
        # for obstacle in self.obstacles:
        #     if given_edge.intersects(obstacle):
        #         return False
        # Define undirected edge
        edge = LineString([state1, state2])
        
        # Create a buffer around the edge to simulate the robot's footprint during movement
        edge_buffer = edge.buffer(0.07)  # cap_style=2 for flat ends

        # Check for intersection with any obstacle
        for obstacle in self.obstacles:
            if edge_buffer.intersects(obstacle):
                return False
        half_side = 0.07  # half the side length of the cube
        x, y = state2[0], state2[1]
        square_at_state2 = Polygon([
            [x - half_side, y - half_side],
            [x + half_side, y - half_side],
            [x + half_side, y + half_side],
            [x - half_side, y + half_side],
            [x - half_side, y - half_side]
        ])

        # Check collision with obstacles
        for obstacle in self.obstacles:
            if square_at_state2.intersects(obstacle):
                return False
        # # Check collision of a circle around state2
        # circle_at_state2 = Point(state2[0], state2[1]).buffer(0.07)  # Circle with radius  around state2
        # for obstacle in self.obstacles:
        #     if circle_at_state2.intersects(obstacle):
        #         return False

        return True

    def compute_heuristic(self, state):
        '''
        #NOT RELEVANT FOR THIS ASSIGNMENT
        Return the heuristic function
        @param state The state (position) of the robot.
        '''

        pass

    # ------------------------#
    # Visualization Functions
    # ------------------------#

    # def visualize_map(self, show_map=False, plan=None, tree_edges=None, expanded_nodes=None,name=""):
    #     '''
    #     Visualize map with current state of robot and obstacles in the map.
    #     @param show_map If to show the map or save it.
    #     @param plan A given plan to draw for the robot.
    #     @param tree_edges A set of tree edges to draw.
    #     @param expanded_nodes A set of expanded nodes to draw.
    #     '''
    #     # create empty background
    #     plt = self.create_map_visualization()

    #     # add obstacles
    #     plt = self.visualize_obstacles(plt=plt)

    #     # add plan if given
    #     if plan is not None:
    #         plt = self.visualize_plan(plt=plt, plan=plan, color='navy')

    #     # add tree edges if given
    #     if tree_edges is not None:
    #         plt = self.visualize_tree_edges(plt=plt, tree_edges=tree_edges, color='lightgrey')

    #     # add expanded nodes if given
    #     if expanded_nodes is not None:
    #         plt = self.visualize_expanded_nodes(plt=plt, expanded_nodes=expanded_nodes, color='lightgrey')

    #     # add start
    #     plt = self.visualize_point_location(plt=plt, state=self.start, color='r')

    #     # add goal or inspection points
    #     plt = self.visualize_point_location(plt=plt, state=self.goal, color='g')

    #     # show map
    #     if show_map:
    #         plt.show()
    #     else:
    #         plt.savefig('map-RRT'+name+'.png')

    #     return plt
# firas 
    def visualize_map(self, show_map=False, plan=None, tree_edges=None, expanded_nodes=None, name=""):
        """
        Visualize the map with current state of robot and obstacles in the map (X is vertical, Y is horizontal).
        @param show_map If to show the map or save it.
        @param plan A given plan to draw for the robot.
        @param tree_edges A set of tree edges to draw.
        @param expanded_nodes A set of expanded nodes to draw.
        """
        plt.figure(figsize=(6, 10))  # Adjusted to match your preferred dimensions

        # Draw background
        back_img = np.zeros((self.ylimit[1] + 1, self.xlimit[1] + 1))
        plt.imshow(
            back_img.T,  # Transposed to reflect axis swap
            origin='lower',
            extent=(self.ylimit[0], self.ylimit[1], self.xlimit[0], self.xlimit[1]),
            zorder=0
        )

        # Draw obstacles (with axis swap)
        for obstacle in self.obstacles:
            coords = list(obstacle.exterior.coords)
            swapped = [(y, x) for x, y in coords]  # Swap X and Y
            xs, ys = zip(*swapped)
            plt.fill(xs, ys, "y", zorder=5)

        # Plot the plan if given
        if plan is not None:
            for i in range(len(plan) - 1):
                x0, y0 = plan[i][1], plan[i][0]
                x1, y1 = plan[i+1][1], plan[i+1][0]
                plt.plot([x0, x1], [y0, y1], color='navy', linewidth=1, zorder=20)

        # Plot tree edges if given
        if tree_edges is not None:
            for edge in tree_edges:
                x0, y0 = edge[0][1], edge[0][0]
                x1, y1 = edge[1][1], edge[1][0]
                plt.plot([x0, x1], [y0, y1], color='lightgrey', zorder=10)

        # Plot expanded nodes if given
        if expanded_nodes is not None:
            for node in expanded_nodes:
                cx, cy = node[1], node[0]
                point_circ = plt.Circle((cx, cy), radius=0.1, color='lightgrey', zorder=10)
                plt.gca().add_patch(point_circ)

        # Plot start and goal
        for state, color in [(self.start, 'r'), (self.goal, 'g')]:
            cx, cy = state[1], state[0]
            point_circ = plt.Circle((cx, cy), radius=0.1, color=color, zorder=30)
            plt.gca().add_patch(point_circ)

        # Set labels and limits
        plt.xlabel('Y Position →')
        plt.ylabel('X Position →')
        plt.xlim(-2, 2)
        plt.ylim(-3.33, 4.5)
        #plt.gca().set_aspect('auto')
        plt.gca().set_aspect('equal', adjustable='box')

        if show_map:
            plt.show()
        else:
            plt.savefig(f'map-RRT{name}.png')

        return plt

    def create_map_visualization(self):
        '''
        Prepare the plot of the scene for visualization.
        '''
        # create figure and add background
        plt.figure()
        back_img = np.zeros((self.ylimit[1]+1, self.xlimit[1]+1))
        plt.imshow(back_img, origin='lower', zorder=0,
                   extent=(self.xlimit[0], self.xlimit[1], self.ylimit[0], self.ylimit[1]))

        return plt

    def visualize_obstacles(self, plt):
        '''
        Draw the scene's obstacles on top of the given frame.
        @param plt Plot of a frame of the environment.
        '''
        # plot obstacles
        for obstacle in self.obstacles:
            obstacle_xs, obstacle_ys = zip(*list(obstacle.exterior.coords))
            plt.fill(obstacle_xs, obstacle_ys, "y", zorder=5)

        return plt

    def visualize_plan(self, plt, plan, color):
        '''
        Draw a given plan on top of the given frame.
        @param plt Plot of a frame of the environment.
        @param plan The requested sequence of steps.
        @param color The requested color for the plan.
        '''
        # add plan edges to the plt
        for i in range(0, len(plan)-1):
            plt.plot([plan[i,0],plan[i+1,0]], [plan[i,1],plan[i+1,1]], color=color, linewidth=1, zorder=20)

        return plt 

    def visualize_tree_edges(self, plt, tree_edges, color):
        '''
        Draw the set of the given tree edges on top of the given frame.
        @param plt Plot of a frame of the environment.
        @param tree_edges The requested set of edges.
        @param color The requested color for the plan.
        '''
        # add plan edges to the plt
        for tree_edge in tree_edges:
            plt.plot([tree_edge[0][0],tree_edge[1][0]], [tree_edge[0][1],tree_edge[1][1]], color=color, zorder=10)

        return plt

    def visualize_expanded_nodes(self, plt, expanded_nodes, color):
        '''
        Draw the set of the given expanded nodes on top of the given frame.
        @param plt Plot of a frame of the environment.
        @param expanded_nodes The requested set of expanded states.
        @param color The requested color for the plan.
        '''
        # add plan edges to the plt
        point_radius = 0.05
        for expanded_node in expanded_nodes:
            point_circ = plt.Circle(expanded_node, radius=point_radius, color=color, zorder=10)
            plt.gca().add_patch(point_circ)

        return plt

    def visualize_point_location(self, plt, state, color):
        '''
        Draw a point of start/goal on top of the given frame.
        @param plt Plot of a frame of the environment.
        @param state The requested state.
        @param color The requested color for the point.
        '''

        # draw the circle
        point_radius = 0.1
        point_circ = plt.Circle(state, radius=point_radius, color=color, zorder=30)
        plt.gca().add_patch(point_circ)
    
        return plt