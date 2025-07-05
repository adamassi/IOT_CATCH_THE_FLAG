from path_algorithms.RCSPlanner import RCSPlanner
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTStarPlanner import RRTStarPlanner
from shapely.geometry import Polygon  # Ensure this is imported
import time

def add_cube_obstacle(env, cube_pos, size=0.3):
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
    print(f"AAAAAAAAAAAAAAAAAAAAAAAAdded cube obstacle at position {cube_pos} with size {size}m.")

# Provide the correct path to map1.json
json_file_path = "our_code/path_algorithms/map1.json"


planning_env = MapEnvironment(json_file=json_file_path)
cube_pos = [0., 0., 0.]  
print(f"BBBBBBBBBBAdding cube obstacle at position {cube_pos}.")
add_cube_obstacle(planning_env, cube_pos)
 # Create an instance of the RCSPlanner with the planning environment
planner = RRTStarPlanner(planning_env=planning_env,ext_mode='E2',goal_prob=0.05,k=10)

# Execute the planning algorithm to get the path
plan = planner.plan()

# Visualize the map with the computed plan and expanded nodes
planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(),name='run_algorithms_for_web')

time.sleep(1)  

# Pass the path to the MapEnvironment
planning_env = MapEnvironment(json_file=json_file_path)
cube_pos = [0., 0., 0.]  
print(f"BBBBBBBBBBAdding cube obstacle at position {cube_pos}.")
add_cube_obstacle(planning_env, cube_pos)
 # Create an instance of the RCSPlanner with the planning environment
planner = RRTStarPlanner(planning_env=planning_env,ext_mode='E2',goal_prob=0.05,k=10)

# Execute the planning algorithm to get the path
plan = planner.plan()

# Visualize the map with the computed plan and expanded nodes
planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(),name='run_algorithms_for_web')  # Convert z to string

for i in range(3):
    # Pass the path to the MapEnvironment
    planning_env = MapEnvironment(json_file=json_file_path)
    cube_pos = [i*2, i*2, i*2]  
    print(f"BBBBBBBBBBAdding cube obstacle at position {cube_pos}.")
    add_cube_obstacle(planning_env, cube_pos)
    # Create an instance of the RCSPlanner with the planning environment
    planner = RRTStarPlanner(planning_env=planning_env,ext_mode='E2',goal_prob=0.05,k=10)

    # Execute the planning algorithm to get the path
    plan = planner.plan()

    # Visualize the map with the computed plan and expanded nodes
    planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(),name='run_algorithms_for_web')  # Convert z to string
    time.sleep(1)  # Sleep for 1 second before the next iteration



# planner = RCSPlanner(planning_env=planning_env)
# # execute plan
# plan = planner.plan()
# planner.planning_env.visualize_map(plan=plan, expanded_nodes=planner.get_expanded_nodes())