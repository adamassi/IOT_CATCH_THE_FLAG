from path_algorithms.create_obstacles import add_cube_obstacle, remove_cube_obstacle, clear_dynamic_cubes  # Import the function to add and remove cube obstacles
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTStarPlanner import RRTStarPlanner
from path_algorithms.AStarPlanner import AStarPlanner
from PARAMETERS import *
import numpy as np  # Import numpy for array operations


# number_of_run=1
def bezier_smooth_plan(plan, samples_per_segment=25, tension=0.25):
    """
    Smooth a polyline plan using cubic Bézier segments.

    plan: numpy array with shape (N, 2)
    returns: numpy array with many sampled points along the smooth curve
    """
    plan = np.asarray(plan, dtype=float)

    if plan is None or len(plan) < 2:
        return plan

    if len(plan) == 2:
        return plan

    smooth_points = []

    for i in range(len(plan) - 1):
        p0 = plan[i]
        p3 = plan[i + 1]

        # Tangent at p0
        if i == 0:
            tangent0 = plan[i + 1] - plan[i]
        else:
            tangent0 = plan[i + 1] - plan[i - 1]

        # Tangent at p3
        if i == len(plan) - 2:
            tangent1 = plan[i + 1] - plan[i]
        else:
            tangent1 = plan[i + 2] - plan[i]

        p1 = p0 + tension * tangent0
        p2 = p3 - tension * tangent1

        # Avoid duplicating the joint point except on the final segment
        t_values = np.linspace(0, 1, samples_per_segment, endpoint=(i == len(plan) - 2))

        for t in t_values:
            point = (
                (1 - t) ** 3 * p0
                + 3 * (1 - t) ** 2 * t * p1
                + 3 * (1 - t) * t ** 2 * p2
                + t ** 3 * p3
            )
            smooth_points.append(point)

    return np.array(smooth_points)


json_file_path = PlannerConfig.MAP_JSON_PATH  # Get the JSON file path from the configuration
planning_env = MapEnvironment(json_file=json_file_path)


def 
# Function get data where the  robot car and where the cube is and calculate the path to the cube
def get_path_to_goal(start_pos, goal_pos, cube_obstacles=[]):
    # global number_of_run
    
    # Initialize the map environment with the JSON file path
    planning_env.start = np.array([start_pos[0], start_pos[2]])  # Use x and y coordinates for the start position
    planning_env.goal = np.array([goal_pos[0], goal_pos[2]])  # Use x and y coordinates for the goal position
    nember_of_added_obstacles = 0
    # Add dynamic obstacles (e.g., cubes detected in the environment)
    for cube_pos in cube_obstacles:
        if cube_pos != goal_pos:  # Skip if cube_pos matches goal_pos
            print(f"Adding cube obstacle NOT GOAL at position {cube_pos}.")
            add_cube_obstacle(planning_env, cube_pos)
            nember_of_added_obstacles += 1
    

    # Create an instance of the RCSPlanner with the planning environment
    print("Creating A*/RRT* planner...")
    # planner = RRTStarPlanner(planning_env=planning_env, ext_mode='E2', goal_prob=0.40, k=10)
    if PlannerConfig.ALGORITHM == "RRT_STAR":
        planner = RRTStarPlanner(planning_env=planning_env, ext_mode=PlannerConfig.EXTENSION_MODE, goal_prob=PlannerConfig.GOAL_PROBABILITY, k=PlannerConfig.K_NEAREST)
    elif PlannerConfig.ALGORITHM == "ASTAR":
        planner = AStarPlanner(planning_env=planning_env)
    else:
        raise ValueError(f"Unsupported planner algorithm: {PlannerConfig.ALGORITHM}")
    
    print(f"Planning path from {planning_env.start} to {planning_env.goal}...")
    # Execute the planning algorithm to get the path
    plan = planner.plan()

    smooth_plan = bezier_smooth_plan(
        plan,
        samples_per_segment=30,
        tension=0.20
        )
    if PlannerConfig.ALGORITHM == "ASTAR":
        planner.planning_env.visualize_map(plan=smooth_plan, visibility_graph=planner.graph, name='AStarPlan')
    elif PlannerConfig.ALGORITHM == "RRT_STAR":
        planner.planning_env.visualize_map(plan=smooth_plan, tree_edges=planner.tree.get_edges_as_states(), name='RRTStarPlan')
    print("Visualizing the map with the computed plan and expanded nodes...")
    # planner.planning_env.visualize_map( name='beforeRemove')
    clear_dynamic_cubes()  # Clear the dynamic cubes from the environment after planning
    remove_cube_obstacle(planning_env, nember_of_added_obstacles)
    # planner.planning_env.visualize_map( name='afterRemove')
    # planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(), name='4main'+str(y))  # Convert z to string
    # print('Successfully planned path')
    return smooth_plan