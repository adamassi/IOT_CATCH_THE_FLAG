class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Location:
    def __init__(self, position, rotation, radius):
        self.position = Position(*position)  # Position object
        self.rotation = rotation  # Rotation in degrees (0-360)
        self.radius = radius  # Radius of the location

    def get_x(self):
        return self.position.x
    
    def get_y(self):
        return self.position.y
    
    def get_z(self):
        return self.position.z
    
    def get_position(self):
        return [self.position.x, self.position.y, self.position.z]
    
    def get_rotation_x(self):
        return self.rotation[0]
    
    def get_rotation_y(self):
        return self.rotation[1]

    def get_radius(self):
        return self.radius