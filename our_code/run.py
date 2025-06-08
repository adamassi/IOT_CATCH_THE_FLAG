from path_algorithms.RCSPlanner import RCSPlanner
from path_algorithms.MapEnvironment import MapEnvironment

# Provide the correct path to map1.json
json_file_path = "our_code/path_algorithms/map1.json"

# Pass the path to the MapEnvironment
planning_env = MapEnvironment(json_file=json_file_path)
planner = RCSPlanner(planning_env=planning_env)
# execute plan
plan = planner.plan()
planner.planning_env.visualize_map(plan=plan, expanded_nodes=planner.get_expanded_nodes())