import json


def append_obstacle_to_json(json_path, field_key, obstacle_points):
    """
    Appends an obstacle to a JSON file's specified field with auto-incremented ID.
    
    Args:
        json_path (str): Path to the JSON file (e.g., cubes.json, map1.json)
        field_key (str): The key in JSON file to append to ('CUBES', 'OBSTACLES', 'GOALS')
        obstacle_points (list): Coordinate points of the obstacle polygon
        obstacle_points (list): Coordinate points of the obstacle polygon.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
    
    field = json_dict.get(field_key, [])
    next_id = 0 if not field else max(item.get('id', -1) for item in field) + 1
    
    obstacle_entry = {
        'id': next_id,
        'coordinates': obstacle_points,
    }
    
    field.append(obstacle_entry)
    
    # Write back to file based on which field was modified
    if field_key == 'CUBES':
        write_cubes_json(json_path, field)
    else:
        json_dict[field_key] = field
        write_map_json_compact(json_path, json_dict)


def write_cubes_json(cubes_path, cubes_list):
    '''Write the cubes JSON file with compact coordinate arrays.
    
    Args:
        cubes_path (str): Path to cubes.json file.
        cubes_list (list): List of cube dictionaries with 'id' and 'coordinates' keys.
    '''
    with open(cubes_path, 'w', encoding='utf-8') as f:
        f.write('{\n')
        f.write('    "CUBES": [\n')
        for index, cube in enumerate(cubes_list):
            comma = ',' if index < len(cubes_list) - 1 else ''
            coords = json.dumps(cube.get('coordinates', []), separators=(',', ':'))
            f.write(
                f'        {{"id": {json.dumps(cube["id"])}, "coordinates": {coords}}}{comma}\n'
            )
        f.write('    ]\n')
        f.write('}\n')


def write_map_json_compact(json_path, json_dict):
    '''Write the map JSON file while keeping obstacle coordinate arrays compact.'''

    def write_section(file_obj, key, items):
        file_obj.write(f'    "{key}": [\n')
        for index, item in enumerate(items):
            comma = ',' if index < len(items) - 1 else ''
            coords = json.dumps(item.get('coordinates', []), separators=(',', ':'))
            if isinstance(item, dict) and 'id' in item:
                file_obj.write(
                    f'        {{"id": {json.dumps(item["id"])}, "coordinates": {coords}}}{comma}\n'
                )
            else:
                file_obj.write(f'        {coords}{comma}\n')
        file_obj.write('    ]')

    with open(json_path, 'w', encoding='utf-8') as f:
        f.write('{' + '\n')
        f.write(f'    "HEIGHT": {json.dumps(json_dict.get("HEIGHT"))},\n')
        f.write(f'    "WIDTH": {json.dumps(json_dict.get("WIDTH"))},\n')

        write_section(f, 'GOALS', json_dict.get('GOALS', []))
        f.write(',\n')
        write_section(f, 'OBSTACLES', json_dict.get('OBSTACLES', []))
        f.write(',\n')

        if 'CUBES' in json_dict:
            write_section(f, 'CUBES', json_dict.get('CUBES', []))
            f.write(',\n')

        history = json_dict.get('HISTORY', [])
        f.write(f'    "HISTORY": {json.dumps(history, ensure_ascii=False, separators=(",", ": "))},\n')
        f.write(f'    "START": {json.dumps(json_dict.get("START"))},\n')
        f.write(f'    "GOAL": {json.dumps(json_dict.get("GOAL"))}\n')
        f.write('}\n')