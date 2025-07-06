
# config.py

class OptiTrackConfig:
    SERVER_IP = "132.68.35.2"
    

class ESPConfig:
    ESP_IP = "http://192.168.0.101"
    OPEN_SERVO_ANGLE = 30
    PICKUP_SERVO_ANGLE = 80
    
class PositionConfig:
    BASE_POS_1 = [3.9, 0.09, 0.28]
    BASE_POS_2 = [3.9, 0.09, -0.09]
    BASE_POS_3 = [4.13, 0.09, 0.26]
    POSITION_TOLERANCE = 0.15
    ANGLE_TOLERANCE = 0.07

class RigidBodyIDs:
    CAR = 605
    CUBE_1 = 604
    CUBE_2 = 606
    CUBE_3 = 607

class PlannerConfig:
    MAP_JSON_PATH = "our_code/path_algorithms/map1.json"
    GOAL_PROBABILITY = 0.40
    EXTENSION_MODE = 'E2'
    K_NEAREST = 10

class PlotConfig:
    X_LIM = (-1.9, 1.97)
    Y_LIM = (-3.33, 4.3)