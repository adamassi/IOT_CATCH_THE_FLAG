import math
# import state_validators
from  state_validators import *
# 
def angle_between_points(p1, p2):
    return math.atan2(p2[2] - p1[2], p2[0] - p1[0])


limit_X = 4.5
limit_Y = 1.9

def extract_order(word):
    """
    Extracts the order of characters from the input word.
    
    """
    arr = []
    for c in word:
        if c=='T':
            arr.append(607)
        elif c=='O':
            arr.append(606)
        elif c=='I':
            arr.append(604)
    return arr



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



