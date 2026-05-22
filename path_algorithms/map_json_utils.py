import json
from datetime import datetime
import os


def append_obstacle_to_json(json_path, field_key, obstacle_points, extra_fields=None):
    """
    Appends an obstacle to a JSON file's specified field with auto-incremented ID.
    
    Args:
        json_path (str): Path to the JSON file (e.g., cubes.json, map1.json)
        field_key (str): The key in JSON file to append to ('CUBES', 'OBSTACLES', 'GOALS')
        obstacle_points (list): Coordinate points of the obstacle polygon.
        extra_fields (dict, optional): Additional metadata to store with the obstacle.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
    
    field = json_dict.get(field_key, [])
    next_id = 0 if not field else max(item.get('id', -1) for item in field) + 1
    
    obstacle_entry = {
        'id': next_id,
        'coordinates': obstacle_points,
    }
    if extra_fields:
        obstacle_entry.update(extra_fields)
    
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
            if isinstance(item, dict):
                file_obj.write(
                    f'        {json.dumps(item, separators=(",", ":"))}{comma}\n'
                )
            else:
                coords = json.dumps(item, separators=(',', ':'))
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


def remove_obstacle_by_id(obstacle_id, json_file="path_algorithms/map1.json"):
    """
    Remove an obstacle from the OBSTACLES section and move it to HISTORY.
    Only non-negative IDs (obstacles) can be removed. GOALS cannot be removed.
    
    Args:
        obstacle_id (int): The ID of the obstacle to remove (must be non-negative)
        json_file (str): The path to the JSON file
        
    Returns:
        bool: True if removal was successful, False otherwise
    """
    # Only allow removal of non-negative IDs (OBSTACLES)
    if obstacle_id < 0:
        print(f"Error: Cannot remove obstacle with ID {obstacle_id}. Only non-negative IDs (OBSTACLES) can be removed. GOALS are protected.")
        return False
    
    json_path = os.path.join(os.getcwd(), json_file)
    
    try:
        with open(json_path) as f:
            json_dict = json.load(f)
        
        # Find and remove the obstacle from OBSTACLES
        obstacle_to_remove = None
        
        for obs in json_dict.get('OBSTACLES', []):
            if obs.get('id') == obstacle_id:
                obstacle_to_remove = obs
                break
        
        if obstacle_to_remove is None:
            print(f"Obstacle with ID {obstacle_id} not found in OBSTACLES section")
            return False
        
        # Remove from OBSTACLES
        json_dict['OBSTACLES'] = [
            obs for obs in json_dict['OBSTACLES']
            if obs.get('id') != obstacle_id
        ]
        
        # Add to HISTORY with timestamp
        if 'HISTORY' not in json_dict:
            json_dict['HISTORY'] = []
        
        removed_entry = dict(obstacle_to_remove)
        removed_entry["removed_at"] = datetime.now().isoformat()
        json_dict['HISTORY'].append(removed_entry)
        
        # Write back to file while keeping coordinate arrays compact
        write_map_json_compact(json_path, json_dict)
        
        print(f"Obstacle with ID {obstacle_id} successfully removed and added to HISTORY")
        return True
    
    except Exception as e:
        print(f"Error removing obstacle: {e}")
        return False


def undo_remove_obstacle(json_file="path_algorithms/map1.json"):
    """
    Undo the last removed obstacle by restoring it from HISTORY to OBSTACLES.
    
    Args:
        json_file (str): The path to the JSON file
        
    Returns:
        bool: True if undo was successful, False otherwise
    """
    json_path = os.path.join(os.getcwd(), json_file)
    
    try:
        with open(json_path) as f:
            json_dict = json.load(f)
        
        # Check if HISTORY is not empty
        history = json_dict.get('HISTORY', [])
        if not history:
            print("Error: HISTORY is empty. Nothing to undo.")
            return False
        
        # Get the last removed obstacle from HISTORY
        last_removed = history.pop()
        
        # Remove the 'removed_at' timestamp (it's not part of the original obstacle metadata)
        last_removed.pop('removed_at', None)
        
        # Add it back to OBSTACLES
        if 'OBSTACLES' not in json_dict:
            json_dict['OBSTACLES'] = []
        
        json_dict['OBSTACLES'].append(last_removed)
        json_dict['HISTORY'] = history
        
        # Write back to file while keeping coordinate arrays compact
        write_map_json_compact(json_path, json_dict)
        
        print(f"Obstacle with ID {last_removed.get('id')} successfully restored from HISTORY to OBSTACLES")
        return True
    
    except Exception as e:
        print(f"Error undoing removal: {e}")
        return False