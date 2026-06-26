#!/usr/bin/env python
# test_visibility_graph.py
import time
import sys
from pathlib import Path
import numpy as np

# Ensure the repository root is on sys.path when this file is run directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PARAMETERS import *
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.AStarPlanner import AStarPlanner
from path_algorithms.RRTStarPlanner import RRTStarPlanner

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
def main():
    planning_env = MapEnvironment("path_algorithms/map1.json")
    startTime = time.time()
    # visibility_graph = env.generate_visibility_graph()
    planner = RRTStarPlanner(planning_env=planning_env, ext_mode=PlannerConfig.EXTENSION_MODE, goal_prob=PlannerConfig.GOAL_PROBABILITY, k=PlannerConfig.K_NEAREST)
    # planner = AStarPlanner(planning_env)
    plan = planner.plan()
    smooth_plan = bezier_smooth_plan(
        plan,
        samples_per_segment=30,
        tension=0.20
        )
    print(f"Planning time: {time.time() - startTime:.4f} seconds")
    count = 0
    planner.planning_env.visualize_map(plan=smooth_plan, tree_edges=planner.tree.get_edges_as_states(), name='RRTForLive'+str(count))
    count +=1
    for i in range(1,len(plan)):
        planner.planning_env.visualize_map( name='RRTForLive'+str(i),car_pos=plan[i])
    
    
    # planner.planning_env.visualize_map(plan=smooth_plan, visibility_graph=planner.graph, name='ForLIve')


if __name__ == "__main__":
    main()