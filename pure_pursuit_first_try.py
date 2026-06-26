"""
path_follower.py
================
Pure-pursuit path follower for a differential-drive robot tracked by OptiTrack.

Pipeline (runs every control tick):
    OptiTrack pose  ->  lookahead point on the Bezier path  ->  steering angle (alpha)
                    ->  desired turn radius  ->  left/right wheel commands

Two things make this work on YOUR setup:
  1. The calibration table you measured (slow-side command -> turn diameter) is
     inverted here, so a desired turn radius maps straight to a wheel command.
  2. calibrate_heading() measures the relationship between the reported heading
     (c_rad) and the direction the robot actually moves, so you never have to
     reason about the y-up/z-up coordinate flip by hand.

UNITS: OptiTrack positions are in METERS. The calibration table is in CM and is
converted internally. Your Bezier `path` MUST also be in METERS (see load_path).

HOW TO USE
  1. Plug your Bezier path into load_path() (list of [x, z] points, meters).
  2. Run once with calibrate_heading() enabled in main() (see the comment there),
     paste the three printed values into the CONFIG block, then comment it out.
  3. Run main() to follow the path.
"""

import time
import socket
import math

import numpy as np

#from natnet_client import DataDescriptions, DataFrame, NatNetClient
from natnet import DataDescriptions, DataFrame, NatNetClient
import optitrack_data_handling
from robotCommands import (
    send_steer_request,
    send_stop_request,
    send_servo_request,
)

# ============================================================================
# CONFIG  -- the three heading values come from calibrate_heading()
# ============================================================================

CHASER_ID = 605                 # rigid-body id of the robot in OptiTrack

# --- heading calibration (PASTE values from calibrate_heading() here) -------
HEADING_SIGN   = 1.0            # +1.0 or -1.0
HEADING_OFFSET = 0.0            # radians
LEFT_SLOW_INCREASES_HEADING = True   # does slowing the LEFT wheel raise heading?

# --- geometry / tuning ------------------------------------------------------
LOOKAHEAD       = 0.25          # Ld in meters. Bigger = smoother, smaller = tighter.
GOAL_TOL        = 0.08          # meters from final point -> stop
ALIGN_TOL       = math.radians(8)    # heading tolerance for initial alignment
STRAIGHT_ALPHA  = math.radians(2)    # below this alpha -> drive straight
HARD_TURN_ALPHA = math.radians(90)   # above this alpha -> command tightest turn
SEARCH_WINDOW   = 60            # points scanned ahead when relocating progress
LOOP_DT         = 0.03          # control period (s), ~33 Hz

# --- wheel commands ---------------------------------------------------------
SPEED_MAX = 250                 # fast side (pinned, matches your calibration)
SPEED_MIN = 70                  # tightest measured slow-side command
ALIGN_OUTER = 130               # outer-wheel speed while pivoting to align
END_CREEP   = 150               # speed cap while creeping into the final point

# --- OptiTrack server -------------------------------------------------------
SERVER_IP = "132.68.35.2"

# ============================================================================
# CALIBRATION TABLE  (right side pinned at 250, left = slow side)
# diameter is in CM -> converted to a turn RADIUS in METERS.
# ============================================================================
# (slow_speed_command, measured_circle_diameter_cm)
_CALIB = [
    (200, 600.0),
    (190, 369.5),
    (180, 258.0),
    (170, 200.0),
    (160, 155.0),
    (150, 120.0),
    (140,  99.5),
    (130,  79.5),
    (120,  66.5),
    (110,  55.5),
    (100,  45.5),
    ( 90,  40.0),
    ( 80,  36.0),
    ( 70,  31.0),
]

# Build monotonic arrays for interpolation: radius_m (increasing) -> slow_speed.
# radius_m = (diameter_cm / 2) / 100
_radius_m = np.array([d / 200.0 for (_, d) in _CALIB])
_slow_spd = np.array([s for (s, _) in _CALIB], dtype=float)
_order = np.argsort(_radius_m)
_radius_m = _radius_m[_order]
_slow_spd = _slow_spd[_order]
# Near-straight anchor: very large radius -> full speed (straight).
_radius_m = np.append(_radius_m, 6.0)
_slow_spd = np.append(_slow_spd, float(SPEED_MAX))


def slow_speed_for_radius(radius_m):
    """Desired (positive) turn radius in meters -> slow-side wheel command."""
    r = max(radius_m, _radius_m[0])             # clamp to tightest measured turn
    spd = float(np.interp(r, _radius_m, _slow_spd))
    return int(round(min(max(spd, SPEED_MIN), SPEED_MAX)))


# ============================================================================
# OptiTrack state (updated by the streaming callback thread)
# ============================================================================
_c_pos = [0.0, 0.0, 0.0]
_c_rad = 0.0
_frames = 0


def receive_new_desc(desc: DataDescriptions):
    pass


def receive_new_frame(data_frame: DataFrame):
    global _c_pos, _c_rad, _frames
    for ms in data_frame.rigid_bodies:
        if ms.id_num == CHASER_ID:
            pos, _euler, rad = optitrack_data_handling.handle_frame(ms)
            _c_pos = pos
            _c_rad = rad
            _frames += 1


# ============================================================================
# Geometry helpers
# ============================================================================
def wrap_angle(a):
    """Wrap to (-pi, pi]."""
    return math.atan2(math.sin(a), math.cos(a))


def _xz(pos):
    """Extract (x, z) ground-plane coords, robust to 2- or 3-length pos."""
    if len(pos) >= 3:
        return pos[0], pos[2]
    return pos[0], pos[1]


def get_raw_pose():
    """(x, z, raw_c_rad) -- used only by calibration."""
    x, z = _xz(_c_pos)
    return x, z, _c_rad


def get_pose():
    """(x, z, heading) with heading corrected into the stored (x, z) frame."""
    x, z = _xz(_c_pos)
    heading = wrap_angle(HEADING_SIGN * _c_rad + HEADING_OFFSET)
    return x, z, heading


def _slow_left(alpha):
    """Which wheel to slow so the robot turns toward the target."""
    return (alpha > 0) == LEFT_SLOW_INCREASES_HEADING


# ============================================================================
# Path tracking
# ============================================================================
def update_progress(path, x, z, idx):
    """Advance the progress index to the nearest point at/after `idx`
    (within a forward window, so it never latches onto an earlier segment)."""
    end = min(len(path), idx + SEARCH_WINDOW)
    best_i, best_d = idx, float("inf")
    for i in range(idx, end):
        dx = path[i][0] - x
        dz = path[i][1] - z
        d = dx * dx + dz * dz
        if d < best_d:
            best_d, best_i = d, i
    return best_i


def find_lookahead(path, x, z, idx, Ld):
    """First point at/after idx that is >= Ld away. Returns (idx, point, near_end)."""
    Ld2 = Ld * Ld
    for i in range(idx, len(path)):
        dx = path[i][0] - x
        dz = path[i][1] - z
        if dx * dx + dz * dz >= Ld2:
            return i, path[i], False
    return len(path) - 1, path[-1], True        # no point Ld away -> end of path


def compute_command(x, z, heading, Lx, Lz):
    """Pure-pursuit -> (left, right) wheel commands."""
    alpha = wrap_angle(math.atan2(Lz - z, Lx - x) - heading)
    a = abs(alpha)

    if a < STRAIGHT_ALPHA:
        return SPEED_MAX, SPEED_MAX

    if a >= HARD_TURN_ALPHA:
        slow = SPEED_MIN                         # target way off to the side
    else:
        R = LOOKAHEAD / (2.0 * math.sin(a))      # pure-pursuit turn radius (m)
        slow = slow_speed_for_radius(R)

    if _slow_left(alpha):
        return slow, SPEED_MAX                   # slow LEFT  -> turn that way
    return SPEED_MAX, slow                        # slow RIGHT -> turn that way


# ============================================================================
# Startup helpers
# ============================================================================
def wait_for_tracking(timeout=5.0):
    t0 = time.time()
    f0 = _frames
    while _frames < f0 + 5:
        if time.time() - t0 > timeout:
            raise RuntimeError(
                "No OptiTrack frames received -- is the system on and streaming?"
            )
        time.sleep(0.05)


def align_to_first(path, timeout=8.0):
    """Pivot in place until the heading roughly points at an early lookahead
    point, so pure pursuit starts from a sane orientation."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        x, z, heading = get_pose()
        _, (Lx, Lz), _ = find_lookahead(path, x, z, 0, LOOKAHEAD)
        alpha = wrap_angle(math.atan2(Lz - z, Lx - x) - heading)
        if abs(alpha) < ALIGN_TOL:
            break
        # pivot: stop the inside wheel, drive the outside one
        if _slow_left(alpha):
            send_steer_request(left=0, right=ALIGN_OUTER)
        else:
            send_steer_request(left=ALIGN_OUTER, right=0)
        time.sleep(LOOP_DT)
    send_stop_request()


# ============================================================================
# Main control loop
# ============================================================================
def follow_path(path, do_align=True):
    if len(path) < 2:
        raise ValueError("Path needs at least 2 points.")

    wait_for_tracking()
    if do_align:
        align_to_first(path)

    idx = 0
    goal = path[-1]
    print("Following path...")
    try:
        while True:
            x, z, heading = get_pose()

            if math.hypot(goal[0] - x, goal[1] - z) < GOAL_TOL:
                break

            idx = update_progress(path, x, z, idx)
            idx, (Lx, Lz), near_end = find_lookahead(path, x, z, idx, LOOKAHEAD)

            left, right = compute_command(x, z, heading, Lx, Lz)

            if near_end:                          # creep gently into the goal
                left = min(left, END_CREEP)
                right = min(right, END_CREEP)

            send_steer_request(left=left, right=right)
            time.sleep(LOOP_DT)
    finally:
        send_stop_request()
    print("Path complete.")


# ============================================================================
# One-time heading calibration
# ============================================================================
def _drive_straight_measure(dist=0.35, speed=200):
    """Drive straight ~`dist` meters; return (travel_direction, heading_while_driving)."""
    x0, z0, r0 = get_raw_pose()
    send_steer_request(left=speed, right=speed)
    x1, z1 = x0, z0
    while math.hypot(x1 - x0, z1 - z0) < dist:
        x1, z1, _ = get_raw_pose()
        time.sleep(LOOP_DT)
    send_stop_request()
    travel_dir = math.atan2(z1 - z0, x1 - x0)
    return travel_dir, r0


def calibrate_heading():
    """Run ONCE. Measures the mapping from reported c_rad to the robot's true
    forward direction (no coordinate-frame assumptions), then prints the three
    values to paste into the CONFIG block above.

    Needs ~1.5 m of clear space ahead.
    """
    wait_for_tracking()

    print("Calibration: straight segment 1...")
    p1, r1 = _drive_straight_measure()
    time.sleep(0.4)

    print("Calibration: re-orienting...")
    send_steer_request(left=120, right=250)       # pivot to a new heading
    time.sleep(1.3)
    send_stop_request()
    time.sleep(0.4)

    print("Calibration: straight segment 2...")
    p2, r2 = _drive_straight_measure()

    # Solve  actual_dir = S * c_rad + O  from the two (heading, travel_dir) pairs.
    dphi = wrap_angle(p1 - p2)
    drad = wrap_angle(r1 - r2)
    if drad == 0:
        S = 1.0
    else:
        S = 1.0 if (dphi * drad) > 0 else -1.0
    O = wrap_angle(p1 - S * r1)

    # Which wheel-slow raises the corrected heading?
    def corrected_heading():
        _, _, raw = get_raw_pose()
        return wrap_angle(S * raw + O)

    time.sleep(0.3)
    h_before = corrected_heading()
    send_steer_request(left=120, right=250)        # slow the LEFT wheel
    time.sleep(1.0)
    send_stop_request()
    h_after = corrected_heading()
    left_slow_increases = wrap_angle(h_after - h_before) > 0

    print("\n==================  PASTE THESE INTO CONFIG  ==================")
    print(f"HEADING_SIGN   = {S:.1f}")
    print(f"HEADING_OFFSET = {O:.4f}")
    print(f"LEFT_SLOW_INCREASES_HEADING = {left_slow_increases}")
    print("===============================================================")
    print("Sanity check after pasting: face the robot at a target slightly to")
    print("its LEFT and confirm it turns left, not right.\n")
    return S, O, left_slow_increases


# ============================================================================
# Path source -- plug in your Bezier output here
# ============================================================================
def load_path():
    """Return the Bezier path as a list of [x, z] points in METERS, ordered
    start -> goal. Replace the body with your own source, e.g.:

        from your_bezier_module import get_smoothed_path
        return get_smoothed_path()

    If your Bezier points are in centimeters, divide each coordinate by 100
    here so the units match the OptiTrack positions.
    """
    raise NotImplementedError("Plug in your Bezier path (list of [x, z], meters).")


# ============================================================================
# Entry point
# ============================================================================
def make_client():
    return NatNetClient(
        server_ip_address=SERVER_IP,
        local_ip_address=socket.gethostbyname(socket.gethostname()),
        use_multicast=False,
    )


def main():
    client = make_client()
    client.on_data_description_received_event.handlers.append(receive_new_desc)
    client.on_data_frame_received_event.handlers.append(receive_new_frame)

    send_servo_request(30)        # set gripper/lift to carry position (optional)

    try:
        with client:
            client.request_modeldef()
            client.run_async()
            time.sleep(0.3)

            # ---- STEP 1: run this ONCE, paste the printed values into CONFIG,
            #      then comment these two lines out. ----
            # calibrate_heading()
            # return

            # ---- STEP 2: normal operation ----
            path = load_path()
            follow_path(path)

    except ConnectionResetError as e:
        print(f"OptiTrack connection failed -- check it is on and streaming.\n{e}")
    except KeyboardInterrupt:
        pass
    finally:
        send_stop_request()

