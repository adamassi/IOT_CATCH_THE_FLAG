from location import Location

limit_X = 4.5
limit_Y = 1.9
def is_flipped(rot_x, rot_y):
    if abs(rot_x) > 60.0 or abs(rot_y) > 60.0:
            print("The robot is flipped. Please check the position.")
            raise ValueError("The robot is flipped. Please check the position.")

def is_robot_off_limits(cord_x :float, cord_y :float):
    """
    Check if the car is within the defined limits of the board.

    Args:
        car (list): The [x, y, z] position of the car.
        target (list): The [x, y, z] position of the target.

    Returns:
        bool: True if both car and target are within limits, False otherwise.
    """
    if is_out_of_board(cord_x, cord_y):
        return True
    else:
        return False
    


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

def correct_slot(idx,pos):
    "first slot [[3.9, -0.05], [3.9, 0.00], [4.5, 0.00], [4.5, -0.40], [3.9, -0.40], [3.9, -0.45], [4.4, -0.45], [4.5, -0.45], [4.5, -0.40], [4.4, -0.40], [4.4, -0.05]]"
    "2:[[3.9,0.4],[3.9,0.45],[4.5,0.45] ,[4.5,0.05],[3.9,0.05],[3.9,0.0],[4.4,0.0],[4.5, 0.0], [4.5, 0.05], [4.4, 0.05],[4.4,0.4]],"
    if pos[0] > 3.9:
        print("The target is in the correct slot")
        if idx==0:
            # print(pos)
            if (pos[2] > -0.40 and pos[2] < -0.05):
                # print("AAAAAAAAAAAAAAAAAAAAAAAAAA")
                return True
        elif idx==1:
            # print(pos)
            # print("AAAAAAAAAAAAAAAAAAA")
            if (pos[2] < 0.40 and pos[2] > 0.0):
                return True
        elif idx==2:
            if (pos[2] > 0.45 and pos[2] < 0.8):
                return True
    
    return False

