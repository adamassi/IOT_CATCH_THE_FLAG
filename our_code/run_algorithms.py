from path_algorithms.RCSPlanner import RCSPlanner
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTStarPlanner import RRTStarPlanner

# Provide the correct path to map1.json
json_file_path = "our_code/path_algorithms/map1.json"

# Pass the path to the MapEnvironment
planning_env = MapEnvironment(json_file=json_file_path)
 # Create an instance of the RCSPlanner with the planning environment
planner = RRTStarPlanner(planning_env=planning_env,ext_mode='E2',goal_prob=0.05,k=10)

# Execute the planning algorithm to get the path
plan = planner.plan()

# Visualize the map with the computed plan and expanded nodes
planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states())




# planner = RCSPlanner(planning_env=planning_env)
# # execute plan
# plan = planner.plan()
# planner.planning_env.visualize_map(plan=plan, expanded_nodes=planner.get_expanded_nodes())