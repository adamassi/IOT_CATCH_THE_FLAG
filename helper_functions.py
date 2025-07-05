import math


def angle_between_points(p1, p2):
    return math.atan2(p2[2] - p1[2], p2[0] - p1[0])

    