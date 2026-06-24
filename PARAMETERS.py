
# config.py

class OptiTrackConfig:
    SERVER_IP = "132.68.35.2"
    

class ESPConfig:
    ESP_IP = "http://192.168.0.105"
    OPEN_SERVO_ANGLE = 30
    PICKUP_SERVO_ANGLE = 80
    
class PositionConfig:
    POSITION_TOLERANCE = 0.15
    ANGLE_TOLERANCE = 0.07
    BASE_POS_1 = [4.2, 0.14, -0.1] # x = 3.85 for the point before the base
    BASE_POS_2 = [4.2, 0.14, 0.25]
    BASE_POS_3 = [4.2, 0.14, 0.6]
    BASES_POS = [BASE_POS_1, BASE_POS_2, BASE_POS_3]
# below are the base positions for the cubes, which are different from the target positions (BASES_POS) where the cubes should be placed. The base positions are where the cubes start before being moved to their target positions.
    base_pos1 = [3.7, 0.09, 0.67]  # Define a third base position for the third cube
    base_pos2 = [3.7, 0.09, 0.28]
    base_pos3 = [3.7, 0.09, -0.15]  # Define a second base position for the second cube
    bases = [base_pos3, base_pos2, base_pos1]  # List of base positions

class RigidBodyIDs:
    CAR = 605
    CUBE_1 = 604
    CUBE_2 = 606
    CUBE_3 = 607
    CUBES_IDS = [CUBE_1, CUBE_2, CUBE_3]

CUBES_BANK_JSON_PATH = "path_algorithms/cube_bank.json"  # Path to the JSON file containing cube information

class PlannerConfig:
    MAP_JSON_PATH = "path_algorithms/map1.json"
    # Choose path planning algorithm:
    # Options: "RRT_STAR", "ASTAR" default is RRT_STAR
    ALGORITHM = "RRT_STAR"
    # ALGORITHM = "ASTAR"
    # RRT* parameters
    GOAL_PROBABILITY = 0.40
    EXTENSION_MODE = 'E2'
    K_NEAREST = 10
    PATH_TIMEOUT_SECONDS = 60
class PlotConfig:
    X_LIM = (-1.9, 1.97)
    Y_LIM = (-3.33, 4.3)

class PlaygroundConfig:
    X_MAX = 3.35
    X_MIN = -4.05
    Y_MAX = 2.1
    Y_MIN = -1.9

class SmoothMotion:
    # Heading error thresholds (radians) — tune after testing
    ANGLE_STEER_ONLY = 0.10   # below this: drive straight, tiny correction only
    ANGLE_SLOW_DOWN  = 0.35   # below this: steer while moving at normal speed
    ANGLE_STOP_TURN  = 0.60   # above this: stop and spin in place

    # Distance thresholds (metres)
    DIST_STOP = 0.14          # arrive / pass-through radius
    DIST_SLOW = 0.35          # slow-down approach zone

    # Motor PWM values (0-255)
    SPEED_NORMAL = 230
    SPEED_SLOW   = 150
    SPEED_MIN    = 80         # minimum per-wheel PWM to keep motors spinning
    SPEED_MAX    = 250

    # Proportional gain for differential steering correction
    STEER_KP = 80.0

    # Rate limiter: minimum seconds between motor commands to the ESP
    CMD_RATE_INTERVAL = 0.15

    # Waypoint thinning at execution time (1 = no thinning, 2 = every 2nd, 3 = every 3rd)
    EXECUTION_WAYPOINT_STEP = 1
