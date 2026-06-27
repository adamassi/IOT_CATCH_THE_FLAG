import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from planner import get_path_to_goal
from PARAMETERS import PlannerConfig

PlannerConfig.ALGORITHM = "RCS"

start_pos = [1.0, 0.0, 1.0]
goal_pos = [3.0, 0.0, -1.0]

plan = get_path_to_goal(start_pos, goal_pos, cube_obstacles=[])

print(plan)
print(f"Plan length: {len(plan)}")