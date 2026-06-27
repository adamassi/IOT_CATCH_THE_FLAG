# test_visibility_graph.py
import time
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Ensure the repository root is on sys.path when this file is run directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.AStarPlanner import AStarPlanner


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


def is_smoothed_plan_valid(env, smooth_plan):
    """
    Check that every small segment of the Bézier path is collision-free.
    Your MapEnvironment already has edge_validity_checker for obstacle checking.
    """
    for i in range(len(smooth_plan) - 1):
        if not env.edge_validity_checker(smooth_plan[i], smooth_plan[i + 1]):
            return False
    return True


def main():
    env = MapEnvironment("path_algorithms/map1.json")

    startTime = time.time()
    visibility_graph = env.generate_visibility_graph()

    aStar = AStarPlanner(env)
    plan = aStar.plan_path()

    print(f"Planning time: {time.time() - startTime:.4f} seconds")

    smooth_plan = bezier_smooth_plan(
        plan,
        samples_per_segment=30,
        tension=0.20
    )

    if is_smoothed_plan_valid(env, smooth_plan):
        print("Bézier path is valid.")
    else:
        print("Warning: Bézier path collides with an obstacle. Use the original A* plan or lower the tension.")
     


    print(plan)
    print("Smoothed plan:")
    print(smooth_plan)
    # Important: show_map=False first, so we can draw the Bézier curve before plt.show()
    env.visualize_map(
        plan=plan,
        show_map=False,
        visibility_graph=visibility_graph
    )

    # Your map visualization swaps axes: horizontal = y, vertical = x
    plt.plot(
        smooth_plan[:, 1],
        smooth_plan[:, 0],
        color="red",
        linewidth=2.5,
        label="Bézier smoothed plan",
        zorder=40
    )

    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()