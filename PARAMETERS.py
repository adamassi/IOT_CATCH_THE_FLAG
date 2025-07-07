
# config.py

class OptiTrackConfig:
    SERVER_IP = "132.68.35.2"
    

class ESPConfig:
    ESP_IP = "http://192.168.0.101"
    OPEN_SERVO_ANGLE = 30
    PICKUP_SERVO_ANGLE = 80
    
class PositionConfig:
    POSITION_TOLERANCE = 0.15
    ANGLE_TOLERANCE = 0.07
    BASE_POS_1 = [4.2, 0.14, -0.1] # x = 3.85 for the point before the base
    BASE_POS_2 = [4.2, 0.14, 0.25]
    BASE_POS_3 = [4.2, 0.14, 0.6]
    BASES_POS = [BASE_POS_1, BASE_POS_2, BASE_POS_3]
    BASES_BORDERS = {
        'first': {
            'start': [4.05, 0.14, -0.28],
            'end': [4.33, 0.14, -0.28],
        },
        'second': {
            'start': [4.05, 0.14, 0.07],
            'end': [4.33, 0.14, 0.07],
        },
        'third': {
            'start': [4.05, 0.14, 0.42],
            'end': [4.33, 0.14, 0.42],
        },
        'fourth': {
            'start': [4.05, 0.14, 0.75],
            'end': [4.33, 0.14, 0.75],
        },
    }

class RigidBodyIDs:
    CAR = 605
    CUBE_1 = 604
    CUBE_2 = 606
    CUBE_3 = 607
    CUBES_IDS = [CUBE_1, CUBE_2, CUBE_3]

class PlannerConfig:
    MAP_JSON_PATH = "our_code/path_algorithms/map1.json"
    GOAL_PROBABILITY = 0.40
    EXTENSION_MODE = 'E2'
    K_NEAREST = 10

class PlotConfig:
    X_LIM = (-1.9, 1.97)
    Y_LIM = (-3.33, 4.3)