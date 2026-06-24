import time
import socket
from natnet import DataDescriptions, DataFrame, NatNetClient
import numpy as np
import optitrack_data_handling
from robotCommands import *
from conversion import normalize_angle
from helper_functions import *
from path_algorithms.planner import *
from PARAMETERS import *
from cubeBank import CubeBank, Cube
from location import Location


word = "OIT"  # Example word to extract order from

c_pos, c_rot, c_rad = [0,0,0], 0, 0

y_base = [-0.15, 0.28, 0.67]  # List of base positions for the cubes
current_target_id = 604
current_target_pos = [0,0,0]

# Rate-limiter state for motor commands
_last_cmd_time = 0.0
_last_steer = None  # last (left_int, right_int) sent to /steer

def cube_blocks_target_base(base_pos, threshold=0.18):
    """
    Check if another cube is blocking the target base for the current cube.

    Args:
        base_pos: target base position [x, y, z]
        current_cube_id: ID of the cube we are currently moving
        threshold: distance in meters to consider the base blocked

    Returns:
        blocking_cube_id if blocked, otherwise None
    """
    for cube in cube_bank.get_all_cubes():
        # Do not count the cube we are currently moving
        if cube.cube_id == current_target_id:
            continue

        # Compare only x and z because y is height
        d = dist(cube.position[0], base_pos[0], cube.position[2], base_pos[2])

        if d < threshold:
            print(f"Cube {cube.cube_id} is blocking the target base (distance: {d:.2f} m).")
            return cube.cube_id
    return None


def check_cube_moved(x_curr, x_prev, z_curr, z_prev, threshold=0.1):
    """
    Check if the cube has moved by comparing current and previous positions.

    Args:
        x_curr (float): Current x-coordinate of the cube.
        z_curr (float): Current z-coordinate of the cube.
        x_prev (float): Previous x-coordinate of the cube.
        z_prev (float): Previous z-coordinate of the cube.
        threshold (float): Distance threshold to determine if the cube has moved.

    Returns:
        bool: True if the cube has moved beyond the threshold, False otherwise.
    """
    return dist(x_curr, x_prev, z_curr, z_prev) > threshold

def receive_new_desc(desc: DataDescriptions):
    # This function is triggered when new data descriptions are received from the OptiTrack #system.
    # It processes the data descriptions and checks for a specific marker set named 'IOT_car'.

    print("Received data descriptions.")  # Notify that data descriptions have been received.

    # Iterate through the marker sets in the data descriptions.
    for ms in desc.marker_sets:
        # Check if the marker set name matches 'IOT_car'.
        if ms.name == 'IOT_car':
            # If a match is found, print the entire data description.
            #print(desc)
            x = 1

def receive_new_frame(data_frame: DataFrame):
    # This function is triggered when a new data frame is received from the OptiTrack system.
    # It processes the data frame to extract the positions, rotations, and radii of the chaser and target objects.
    global cube_bank  # Access the global cube bank to update cube positions
    global c_pos, c_rot, c_rad
    global current_target_pos, current_target_id
    for ms in data_frame.rigid_bodies:
        if ms.id_num == RigidBodyIDs.CAR:
            # Handle the chaser's data
            c_pos, c_rot, c_rad = optitrack_data_handling.handle_frame(ms)
        if cube_bank.check_if_cube_in_bank(ms.id_num):
            pos, rot, rad = optitrack_data_handling.handle_frame(ms)
            cube_bank.update_cube(ms.id_num, Location(pos, rot, rad))
            if ms.id_num == current_target_id:
                current_target_pos = cube_bank.get_cube_position_by_id(current_target_id)

def check_board_validity():
    # This function checks if the robot and the cubes are within the defined limits of the board and checks if the robot is flipped.
    # It uses the `is_out_of_board` function to determine if either the chaser or target is out of bounds.

    if is_out_of_board(c_pos[0], c_pos[2]):
        print("The robot is out of the board limits. Please check the position.")
        exit()

    cube_bank.validate_cubes()  # Validate the cubes in the cube bank to ensure they are within limits and not flipped


def turnToTarget(is_cube = True, curr_t_pos = current_target_pos):
    left, right, stop = 1, 2, 3
    turning_state = stop
    while True:
        streaming_client.update_sync()
        curr_c_pos, curr_c_rad = c_pos, c_rad
        if is_cube:
            curr_t_pos = current_target_pos
        angle = angle_between_points(curr_c_pos, curr_t_pos)
        normalized_angle = normalize_angle(angle - curr_c_rad)
        if abs(normalized_angle) < 0.07:
            send_stop_request()
            break
        elif normalized_angle < 0:
            if not turning_state == left:
                turning_state = left
                send_lift_request(60)
        else:
            if not turning_state == right:
                turning_state = right
                send_right_request(60)
    # time.sleep(1)

def heading_error_to(target_pos):
    """Return signed heading error (radians) from current pose to target_pos."""
    angle = angle_between_points(c_pos, target_pos)
    return normalize_angle(angle - c_rad)


def _send_steer_if_changed(left, right):
    """Send /steer only when speeds changed or rate-limit interval elapsed."""
    global _last_cmd_time, _last_steer
    l = int(max(SmoothMotion.SPEED_MIN, min(SmoothMotion.SPEED_MAX, left)))
    r = int(max(SmoothMotion.SPEED_MIN, min(SmoothMotion.SPEED_MAX, right)))
    now = time.time()
    if _last_steer != (l, r) or now - _last_cmd_time >= SmoothMotion.CMD_RATE_INTERVAL:
        send_steer_request(l, r)
        _last_cmd_time = now
        _last_steer = (l, r)


def thin_waypoints(plan, step):
    """Keep every step-th waypoint from plan; always include the last."""
    if step <= 1 or len(plan) <= 2:
        return plan
    indices = list(range(0, len(plan) - 1, step)) + [len(plan) - 1]
    return plan[indices]


def GoToTarget(is_cube = True, curr_t_pos = current_target_pos, stop_at_end = True):
    """Drive toward a target using differential steering; no unnecessary stops.

    is_cube      – True: track live current_target_pos; always stop on arrival.
    stop_at_end  – False: leave motors running when arrive radius reached
                   (use for intermediate path waypoints).

    Heading logic:
      |error| < ANGLE_SLOW_DOWN  → steer at normal speed
      |error| < ANGLE_STOP_TURN  → steer at slow speed
      |error| >= ANGLE_STOP_TURN → stop, spin in place, resume
    """
    global _last_cmd_time, _last_steer

    if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) < SmoothMotion.DIST_STOP:
        if stop_at_end:
            send_stop_request()
            _last_steer = None
        return

    _last_steer = None  # force first steer command through rate-limiter

    while True:
        streaming_client.update_sync()

        if is_cube:
            curr_t_pos = current_target_pos

        d = dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2])

        if d < SmoothMotion.DIST_STOP:
            if stop_at_end:
                send_stop_request()
                _last_steer = None
            break

        heading_err = heading_error_to(curr_t_pos)

        if abs(heading_err) > SmoothMotion.ANGLE_STOP_TURN:
            # Too far off: stop, spin in place, then resume driving
            send_stop_request()
            _last_steer = None
            turnToTarget(is_cube, curr_t_pos)
            _last_steer = None
            continue

        # Choose base speed: slow when close or heading error is moderate
        if d < SmoothMotion.DIST_SLOW or abs(heading_err) > SmoothMotion.ANGLE_SLOW_DOWN:
            base_speed = SmoothMotion.SPEED_SLOW
        else:
            base_speed = SmoothMotion.SPEED_NORMAL

        # Differential steering:
        # heading_err > 0 → need to turn right → left motor faster
        # heading_err < 0 → need to turn left  → right motor faster
        correction = SmoothMotion.STEER_KP * heading_err
        _send_steer_if_changed(base_speed + correction, base_speed - correction)

def GoBack( ):
    
    if c_pos[0] >= 3.85:
        send_start_beeping_request()
        send_back_request()
        
        while True:
            
            streaming_client.update_sync()
            if c_pos[0] < 3.8:
                send_stop_request()
                break
        send_stop_beeping_request()
            


def move_cube_to_base(base_pos):
    plan = []
    start_time = time.time()

    while len(plan) == 0:
        if time.time() - start_time >= PlannerConfig.PATH_TIMEOUT_SECONDS:
            print(f"Path planning timed out after {PlannerConfig.PATH_TIMEOUT_SECONDS} seconds.")
            return np.array([])
        
        get_path_to_target()      # go to the cube
        send_servo_request(80)    # close servo / pick cube
        plan = go_to_goal(base_pos)  # carry cube to base
        # if len(plan) == 0:
        #     blocking_cube_id = cube_blocks_target_base(base_pos, current_target_id)
        #     if blocking_cube_id is not None:
        #         move_cube_blocking_base(blocking_cube_id)  # Move the blocking cube out of the way
        #         print(f"Cube {blocking_cube_id} is blocking the target base.")
    return plan

# use it to go to the base position
def go_to_goal(goal_pos):

    finished = False
    while not finished:
        streaming_client.update_sync()

        cubes_positions = [cube_bank.get_cube_position_by_id(idx) for idx in cubes_order if idx is not current_target_id]
        plan = get_path_to_goal(c_pos, goal_pos, cubes_positions)
        plan = thin_waypoints(plan, SmoothMotion.EXECUTION_WAYPOINT_STEP)
        finished = True
        last_idx = len(plan) - 2  # index of last waypoint step
        for i in range(len(plan) - 1):
            check_board_validity()

            go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]
            is_final = (i == last_idx)
            # Stop only at the last waypoint; keep rolling through intermediate ones
            GoToTarget(False, go_to_pos, stop_at_end=is_final)

            streaming_client.update_sync()
            curr_pos = [cube_bank.get_cube_position_by_id(idx) for idx in cubes_order if idx is not current_target_id]
            if any(check_cube_moved(prev[0], curr[0], prev[2], curr[2]) for (prev, curr) in zip(cubes_positions, curr_pos)):
                print("continue")
                finished = False
                break

            if dist(c_pos[0], current_target_pos[0], c_pos[2], current_target_pos[2]) > 0.16:
                send_servo_request(30)
                return []

    return plan  # Return the planned path for further use or analysis



def get_path_to_target():
    finished = False
    while not finished:
        streaming_client.update_sync()

        cubes_positions = [cube_bank.get_cube_position_by_id(idx) for idx in cubes_order if idx is not current_target_id]
        plan = get_path_to_goal(c_pos, current_target_pos, cubes_positions)
        plan = thin_waypoints(plan, SmoothMotion.EXECUTION_WAYPOINT_STEP)
        finished = True
        last_idx = len(plan) - 2  # index of last waypoint step
        for point in range(len(plan) - 1):
            check_board_validity()

            go_to_pos = [plan[point+1][0], 0, plan[point+1][1]]
            is_final = (point == last_idx)
            if is_final:
                # Final approach: track live cube position, stop for pickup
                GoToTarget(True, go_to_pos, stop_at_end=True)
            else:
                # Intermediate waypoint: steer through without stopping
                GoToTarget(False, go_to_pos, stop_at_end=False)

            streaming_client.update_sync()
            curr_pos = [cube_bank.get_cube_position_by_id(idx) for idx in cubes_order if idx is not current_target_id]
            if any(check_cube_moved(prev[0], curr[0], prev[2], curr[2]) for (prev, curr) in zip(cubes_positions, curr_pos)):
                print("continue")
                finished = False
                break


cube_bank = CubeBank()  # Initialize the cube bank to manage cube information and positions
cube_bank.load_cubes_from_json(CUBES_BANK_JSON_PATH)  # Load cube data from JSON file
#for cube in cube_bank.get_all_cubes():
   # print(f"Cube ID: {cube.cube_id}, Letter: {cube.letter}, Position: {cube.position}")  # Print cube information for verification

# Initialize the NatNet client to connect to the OptiTrack system and set up event handlers for receiving data descriptions and data frames.
streaming_client = NatNetClient(
    server_ip_address = OptiTrackConfig.SERVER_IP, #"132.68.35.255",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)

# Attach the event handlers to the streaming client to process incoming data descriptions and data frames.
streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)


try:
    arr = extract_order(word) 
    print(arr)

    # Initial servo position (e.g., Open Claw)
    send_servo_request(30)
    
    with streaming_client:

        # Request the model definitions from the OptiTrack server to initialize the data stream.
        streaming_client.request_modeldef()

        # Continuously update the streaming client to receive data frames and process them with the defined handlers.
        streaming_client.update_sync()
        
        time.sleep(1)  # Allow some time for the client to start and receive data

        print("Streaming started. Waiting for data...", flush=True)
               
        cubes_order = cube_bank.get_cubes_ordered_by_word(word)  # Get the current cubes from the cube bank
        for idx in range(len(cubes_order)):
            current_target_id = cubes_order[idx]  # Get the current target ID from the array

            check_board_validity()  # Check if the robot and cubes are within the defined limits of the board and check if the robot is flipped

            if not correct_slot(idx,current_target_pos):  # Check if the target position is in the correct slot
                # blocking_cube_id = cube_blocks_target_base(PositionConfig.bases[idx])
                # if blocking_cube_id is not None:
                #     print(f"Cube {blocking_cube_id} is blocking the target base.")
                plan = []
                plan = move_cube_to_base(PositionConfig.bases[idx])  # Move the cube to the base position
                turnToTarget(False, [plan[-1][0]+0.4,0.09, y_base[idx]])
                GoToTarget(False, [plan[-1][0]+0.4,0.09, y_base[idx]], stop_at_end=True)  # Stop before releasing cube
                send_servo_request(30)
                GoBack()

# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack #system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

except ValueError as e:
    print(e)

# Handle any other unexpected exceptions
except Exception as e:
    # print(f"An unexpected error occurred: {e}", file=#sys.stderr)
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

