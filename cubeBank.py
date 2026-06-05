import json


class Cube:
    def __init__(self, cube_id, letter, position=None):
        self.cube_id = cube_id
        self.letter = letter
        self.position = position  # position should be a list or tuple of (x, y, z) coordinates


class CubeBank:
    def __init__(self):
        self.cubes = {}  # Dictionary to store cubes with cube_id as key

    def load_cubes_from_json(self, json_file_path):
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for cube_data in data.get("CUBES", []):
                cube_id = cube_data.get("cube_ID")
                letter = cube_data.get("letter")
                if cube_id is not None and letter is not None:
                    self.cubes[cube_id] = Cube(cube_id, letter)
                else:
                    print(f"Warning: Invalid cube data in JSON: {cube_data}")

    def update_cube(self, cube_id, position):
        if cube_id in self.cubes:
            letter = self.cubes[cube_id].letter 
            self.cubes[cube_id] = Cube(cube_id, letter, position)
            return True
        else:
            print(f"Cube with ID {cube_id} does not exist.")
            return False

    def add_cube(self, cube_id, letter):
        if cube_id in self.cubes:
            return False

        self.cubes[cube_id] = Cube(cube_id, letter)
        return True

    def remove_cube(self, cube_id):
        if cube_id in self.cubes:
            del self.cubes[cube_id]
            return True
        else:
            print(f"Cube with ID {cube_id} does not exist.")
            return False

    def get_cube_position(self, cube_id):
        if cube_id in self.cubes:
            return self.cubes[cube_id].position
        else:
            print(f"Cube with ID {cube_id} does not exist.")
            return None

    def get_all_cubes(self):
        return list(self.cubes.values())