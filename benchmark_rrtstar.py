import matplotlib
matplotlib.use('Agg')  # Prevent any display windows from opening

import os
import csv
import time
import numpy as np

# Set algorithm BEFORE calling get_path_to_goal (checked inside the function)
from PARAMETERS import PlannerConfig
PlannerConfig.ALGORITHM = "RRT_STAR"

# Reuse the already-instantiated environment from the planner module
from path_algorithms.planner import get_path_to_goal, planning_env

NUM_RUNS = 100
XLIMIT = [-3.9, 3.9]
YLIMIT = [-1.9, 1.9]
MIN_DISTANCE = 0.5
CSV_FILE = "rrtstar_benchmark_results.csv"
ALGORITHM_NAME = "RRT_STAR"

# The planner saves plots to pics/ — create it if missing
os.makedirs("pics_Comparison", exist_ok=True)


def sample_valid_point(env):
    """Randomly sample [x, y] inside XLIMIT/YLIMIT that is not inside any obstacle."""
    while True:
        x = np.random.uniform(XLIMIT[0], XLIMIT[1])
        y = np.random.uniform(YLIMIT[0], YLIMIT[1])
        if env.state_validity_checker(np.array([x, y])):
            return x, y


def path_length(plan):
    """Total Euclidean distance along the path. Returns 0 for an empty/None path."""
    if plan is None or len(plan) == 0:
        return 0.0
    total = 0.0
    for i in range(len(plan) - 1):
        total += np.linalg.norm(np.array(plan[i + 1]) - np.array(plan[i]))
    return float(total)


def main():
    results = []
    successful_runs = 0
    failed_runs = 0
    total_time = 0.0
    successful_time = 0.0

    print(f"=== Benchmarking {ALGORITHM_NAME} — {NUM_RUNS} runs ===\n")

    for run_idx in range(NUM_RUNS):
        # Sample a valid start/goal pair with at least MIN_DISTANCE separation
        while True:
            start_x, start_y = sample_valid_point(planning_env)
            goal_x, goal_y = sample_valid_point(planning_env)
            if np.hypot(goal_x - start_x, goal_y - start_y) >= MIN_DISTANCE:
                break

        # Planner expects [x, 0.14, z]; internally uses index 0 and 2 as 2D [x, z]
        start_pos = [start_x, 0.14, start_y]
        goal_pos = [goal_x, 0.14, goal_y]

        success = False
        plan_len = 0.0
        elapsed = 0.0

        t_start = time.perf_counter()
        try:
            plan = get_path_to_goal(start_pos, goal_pos, cube_obstacles=[])
            elapsed = time.perf_counter() - t_start

            success = plan is not None and len(plan) > 0
            if success:
                plan_len = path_length(plan)
                successful_runs += 1
                successful_time += elapsed
            else:
                failed_runs += 1
                print(f"  Run {run_idx + 1}: planner returned empty path")

        except Exception as exc:
            elapsed = time.perf_counter() - t_start
            failed_runs += 1
            print(f"  Run {run_idx + 1}: EXCEPTION — {exc}")

        total_time += elapsed

        results.append({
            "run_index": run_idx + 1,
            "start_x": round(start_x, 4),
            "start_y": round(start_y, 4),
            "goal_x": round(goal_x, 4),
            "goal_y": round(goal_y, 4),
            "success": int(success),
            "path_length": round(plan_len, 4),
            "time_seconds": round(elapsed, 6),
        })

        if (run_idx + 1) % 10 == 0:
            print(f"  [{run_idx + 1:3d}/{NUM_RUNS}] success={successful_runs}  failed={failed_runs}  "
                  f"avg_so_far={total_time / (run_idx + 1):.3f}s")

    avg_success = successful_time / successful_runs if successful_runs > 0 else 0.0
    avg_all = total_time / NUM_RUNS

    print(f"\n=== Results: {ALGORITHM_NAME} ===")
    print(f"  Algorithm:                {ALGORITHM_NAME}")
    print(f"  Successful runs:          {successful_runs} / {NUM_RUNS}")
    print(f"  Failed runs:              {failed_runs} / {NUM_RUNS}")
    print(f"  Total time:               {total_time:.3f} s")
    print(f"  Avg time (success only):  {avg_success:.3f} s")
    print(f"  Avg time (all 100 runs):  {avg_all:.3f} s")

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["run_index", "start_x", "start_y", "goal_x", "goal_y",
                        "success", "path_length", "time_seconds"],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to {CSV_FILE}")


if __name__ == "__main__":
    main()
