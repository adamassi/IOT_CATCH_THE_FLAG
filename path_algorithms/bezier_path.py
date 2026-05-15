"""Bézier path smoothing utilities for RRT/RRT* waypoint plans.

The planner still creates a collision-free polyline path. This module only
replaces sharp corners with short quadratic Bézier arcs, and it validates the
smoothed result before returning it.
"""

import numpy as np


def _as_2d_plan(plan):
    plan = np.asarray(plan, dtype=float)
    if plan.ndim != 2 or plan.shape[1] != 2:
        raise ValueError("plan must be an Nx2 array/list of [x, y] states")
    return plan


def quadratic_bezier(p0, p1, p2, num_points=8):
    """Return samples on a quadratic Bézier curve from p0 to p2 using p1 as control."""
    p0 = np.asarray(p0, dtype=float)
    p1 = np.asarray(p1, dtype=float)
    p2 = np.asarray(p2, dtype=float)
    t_values = np.linspace(0.0, 1.0, int(num_points))
    return np.array([
        ((1 - t) ** 2) * p0 + 2 * (1 - t) * t * p1 + (t ** 2) * p2
        for t in t_values
    ])


def smooth_path_with_bezier(plan, samples_per_corner=8, corner_cut=0.35):
    """Smooth an RRT/RRT* waypoint path with local quadratic Bézier curves.

    Args:
        plan: Nx2 numpy array/list from the planner.
        samples_per_corner: number of sampled points per rounded corner.
        corner_cut: fraction of the shorter adjacent segment to cut before/after
            each waypoint. Keep this below ~0.5 to avoid large shortcuts.

    Returns:
        Nx2 numpy array containing a smoothed path. The first and last points are
        preserved exactly.
    """
    plan = _as_2d_plan(plan)
    if len(plan) < 3:
        return plan.copy()

    smoothed = [plan[0]]

    for i in range(1, len(plan) - 1):
        prev_p = plan[i - 1]
        curr_p = plan[i]
        next_p = plan[i + 1]

        v_in = curr_p - prev_p
        v_out = next_p - curr_p
        len_in = np.linalg.norm(v_in)
        len_out = np.linalg.norm(v_out)

        if len_in < 1e-9 or len_out < 1e-9:
            continue

        cut_dist = min(len_in, len_out) * corner_cut
        curve_start = curr_p - (v_in / len_in) * cut_dist
        curve_end = curr_p + (v_out / len_out) * cut_dist

        # Avoid duplicating the previous point by dropping the first curve sample.
        curve = quadratic_bezier(curve_start, curr_p, curve_end, samples_per_corner)
        smoothed.extend(curve[1:])

    smoothed.append(plan[-1])
    return np.asarray(smoothed)


def path_is_collision_free(path, planning_env):
    """Validate a path using the same state/edge checkers as the planner."""
    path = _as_2d_plan(path)
    for state in path:
        if not planning_env.state_validity_checker(state):
            return False
    for i in range(len(path) - 1):
        if not planning_env.edge_validity_checker(path[i], path[i + 1]):
            return False
    return True


def safe_bezier_smooth_path(plan, planning_env, samples_per_corner=8, corner_cut=0.35):
    """Return a Bézier-smoothed path, or the original path if smoothing collides."""
    original = _as_2d_plan(plan)
    smoothed = smooth_path_with_bezier(
        original,
        samples_per_corner=samples_per_corner,
        corner_cut=corner_cut,
    )

    if path_is_collision_free(smoothed, planning_env):
        print(f"Bézier smoothing accepted: {len(original)} -> {len(smoothed)} points")
        return smoothed

    print("Bézier smoothing rejected because it collides; using original RRT* path")
    return original
