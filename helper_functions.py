import math


def angle_between_points(p1, p2):
    return math.atan2(p2[2] - p1[2], p2[0] - p1[0])


limit_X = 4.5
limit_Y = 1.9
def is_flipped(cube_ror=[[0, 0, 0]]):
    for i in range(len(cube_ror)):
        if abs(cube_ror[i][0]) > 60.0 or abs(cube_ror[i][1]) > 60:
            print("The robot is flipped. Please check the position.")
            raise ValueError("The robot is flipped. Please check the position.")
def out_limits(car :float, target :float):
    """
    Check if the car is within the defined limits of the board.

    Args:
        car (list): The [x, y, z] position of the car.
        target (list): The [x, y, z] position of the target.

    Returns:
        bool: True if both car and target are within limits, False otherwise.
    """
    if is_out_of_board(car[0], car[2]) or is_out_of_board(target[0], target[2]):
        print("The robot is out of the board limits. Please check the position.")
        exit()
    


    # return is_out_of_board(car[0], car[2]) or is_out_of_board(target[0], target[2])
    
#if True : The robot out of the borders of the board
#if False : The robot in the borders of the board
def is_out_of_board(cord_x :float, cord_y :float):
    """
    Check if the robot is out of the board boundaries.

    Args:
        cord_x (float): x-coordinate of the robot.
        cord_y (float): y-coordinate of the robot.

    Returns:
        bool: True if the robot is out of the board boundaries, False otherwise.
    """
    return abs(cord_x) > limit_X or abs(cord_y) > limit_Y


def get_speed(steering_degree):
    if steering_degree > 0:
        right = 250 - int(70 / 30 * abs(steering_degree))
        left = 250
    else:
        right = 250
        left = 250 - int(70 / 30 * abs(steering_degree))

    print(right, left)
    return right, left

def dist(x1, x2, y1, y2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2).

    Args:
        x1 (float): x-coordinate of the first point.
        y1 (float): y-coordinate of the first point.
        x2 (float): x-coordinate of the second point.
        y2 (float): y-coordinate of the second point.

    Returns:
        float: The Euclidean distance between the two points.
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def correct_slot(cube,pos):
    "first slot [[3.9, -0.05], [3.9, 0.00], [4.5, 0.00], [4.5, -0.40], [3.9, -0.40], [3.9, -0.45], [4.4, -0.45], [4.5, -0.45], [4.5, -0.40], [4.4, -0.40], [4.4, -0.05]]"
    "2:[[3.9,0.4],[3.9,0.45],[4.5,0.45] ,[4.5,0.05],[3.9,0.05],[3.9,0.0],[4.4,0.0],[4.5, 0.0], [4.5, 0.05], [4.4, 0.05],[4.4,0.4]],"
    if pos[0]> 3.9:
        print("The target is in the correct slot")
        if cube==0:
            # print(pos)
            if (pos[2]> -0.40 and pos[2]< -0.05):
                # print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
                return True
        elif cube==1:
            # print(pos)
            # print("AAAAAAAAAAAAAAAAAAA")
            if (pos[2]< 0.40 and pos[2]> 0.0):
                return True
        elif cube==2:
            if (pos[2]> 0.45 and pos[2]< 0.8):
                return True
    
    return False

