class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Location:
    def __init__(self, position, rotation, radius):
        self.position = position  # Position object
        self.rotation = rotation  # Rotation in degrees (0-360)
        self.radius = radius  # Radius of the location