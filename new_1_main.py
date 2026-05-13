import time
import socket
from natnet import DataDescriptions, DataFrame, NatNetClient
import numpy as np
import optitrack_data_handling
#from helperFunc import dist, is_out_of_board 
# from helper_functions import dist, angle_between_points ,out_limits, is_flipped
from robotCommands import *
from conversion import normalize_angle
from helper_functions import *
# from shapely.geometry import Polygon  # Ensure this is imported
from PARAMETERS import *
from path_algorithms.create_obstacles import add_cube_obstacle  # Import the function to add cube obstacles
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTStarPlanner import RRTStarPlanner
# import #sys

# check_esp_http()
# for web
# word = #sys.argv[1]
word = "OIT"  # Example word to extract order from
arr=[]
c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos1, t_rot1, t_rad1 = [0,0,0], 0, 0
t_pos2, t_rot2, t_rad2 = [0,0,0], 0, 0
t_pos3, t_rot3, t_rad3 = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0
base_pos2 = [3.7, 0.09, 0.28]
base_pos3 = [3.7, 0.09, -0.15]  # Define a second base position for the second cube
base_pos1 = [3.7, 0.09, 0.67]  # Define a third base position for the third cube
bases=[base_pos3, base_pos2,  base_pos1]  # List of base positions for the cubes
y_base = [-0.15, 0.28, 0.67]  # List of base positions for the cubes
z = 1  # Initialize a global variable for iteration count
y=604
def extract_order(word):
    """
    Extracts the order of characters from the input word.
    
    """
    for c in word:
        if c=='T':
            arr.append(607)
        elif c=='O':
            arr.append(606)
        elif c=='I':
            arr.append(604)


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
    global c_pos, c_rot, c_rad
    global t_pos, t_rot, t_rad
    global t_pos1, t_rot1, t_rad1  # Add variables for ctf_cube1
    global t_pos2, t_rot2, t_rad2  # Add variables for ctf_cube2
    global t_pos3, t_rot3, t_rad3

    for ms in data_frame.rigid_bodies:
        if ms.id_num == 605:
            # Handle the chaser's data
            c_pos, c_rot, c_rad = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == y:
            # Handle the target's data (ctf_cube)
            t_pos, t_rot, t_rad = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == 604:
            # Handle the first cube's data (ctf_cube2)
            t_pos1, t_rot1, t_rad1 = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == 606:
            # Handle the second cube's data (ctf_cube2)
            t_pos2, t_rot2, t_rad2 = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == 607:
            # Handle the third cube's data (ctf_cube3)
            t_pos3, t_rot3, t_rad3 = optitrack_data_handling.handle_frame(ms)   
    #print("received new frame")














streaming_client = NatNetClient(
    server_ip_address = OptiTrackConfig.SERVER_IP, #"132.68.35.255",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)




streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)

def turnToTarget(is_cube = True, curr_t_pos = t_pos):
    left, right, stop = 1, 2, 3
    turning_state = stop
    while True:
        streaming_client.update_sync()
        curr_c_pos, curr_c_rad = c_pos, c_rad
        if is_cube:
            curr_t_pos = t_pos
        angle = angle_between_points(curr_c_pos, curr_t_pos)
        normalized_angle = normalize_angle(angle - curr_c_rad)
        if abs(normalized_angle) < 0.07:
            send_stop_request()
            break
        elif normalized_angle < 0:
            if not turning_state == left:
                turning_state = left
                send_lift_request(60)
                # send_steer_request(left=15, right = 250)
        
        else:
            if not turning_state == right:
                turning_state = right
                send_right_request(60)
                # send_steer_request(left=250, right = 15)
    # time.sleep(1)

def GoToTarget(is_cube = True, curr_t_pos = t_pos):
    """Drive the chaser toward a target position until close.

    Args:
        is_cube (bool): If True, use the tracked global `t_pos` as the
            current target; otherwise use the provided `curr_t_pos`.
        curr_t_pos (list): [x, y, z] fallback target position when
            `is_cube` is False.

    Behavior:
        - If the distance to the target is >= 0.16 m, start moving forward.
        - Continuously update streaming data and check distance.
        - If within 0.14 m, stop and return.
        - If heading error is large (> 0.5 rad), call `turnToTarget`
          to re-orient before continuing forward.
    """

    # Only start driving if we're not already close to the target
    if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) >= 0.16:
        send_go_request()
        while True:
            # Keep optitrack data fresh
            streaming_client.update_sync()

            # If tracking a cube, always use the live global `t_pos`
            if is_cube:
                curr_t_pos = t_pos

            # If we got close enough, stop and exit
            if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) < 0.14:
                send_stop_request() #the problem if we remove this line is harder to catch the target 
                #1/3/2026
                break

            # Compute heading error and optionally re-orient
            angle = angle_between_points(c_pos, curr_t_pos)
            normalized_angle = normalize_angle(angle - c_rad)
            if abs(normalized_angle) > 0.5:
                # Large heading error: turn toward the target, then resume
                turnToTarget(is_cube, curr_t_pos)
                send_go_request()

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
            
            










# def pure_pursuit(plan, lookahead_dist=0.35, base_speed=200, wheelbase=0.12):
#     """
#     Follow a path plan using Pure Pursuit — smooth turning while driving.
    
#     Args:
#         plan: numpy array of [x, z] waypoints from RRT*
#         lookahead_dist: how far ahead to aim (meters). Larger = smoother but cuts corners more
#         base_speed: base PWM speed (0-255)
#         wheelbase: distance between wheels (meters) — measure your robot
#     """
#     print(f"Robot position: x={c_pos[0]:.2f}, z={c_pos[2]:.2f}")
#     print(f"Plan start: {plan[0]}")
#     print(f"Plan end: {plan[-1]}")
#     print(f"Plan length: {len(plan)} points")
    
#     first_lookahead = find_lookahead_point(plan, c_pos, lookahead_dist)
#     print(f"First lookahead point: {first_lookahead}")
    
#     angle_to_target = angle_between_points(c_pos, [first_lookahead[0], 0, first_lookahead[1]])
#     print(f"Robot heading (c_rad): {c_rad:.2f}")
#     print(f"Angle to lookahead: {angle_to_target:.2f}")
#     print(f"Heading error: {normalize_angle(angle_to_target - c_rad):.2f}")


#     goal = [plan[-1][0], 0, plan[-1][1]]  # Final destination in 3D coords
    
#     while True:
#         streaming_client.update_sync()
        
#         # Check if we've reached the final goal
#         if dist(c_pos[0], goal[0], c_pos[2], goal[2]) < 0.14:
#             send_stop_request()
#             break
        
#         # --- Find the lookahead point on the path ---
#         lookahead_point = find_lookahead_point(plan, c_pos, lookahead_dist)
        
#         # --- Compute heading error to lookahead point ---
#         angle_to_target = angle_between_points(c_pos, 
#                                                [lookahead_point[0], 0, lookahead_point[1]])
#         heading_error = normalize_angle(angle_to_target - c_rad)
        
#         # --- Pure Pursuit curvature formula ---
#         # κ = 2 * sin(α) / L
#         curvature = 2.0 * math.sin(heading_error) / lookahead_dist
        
#         # --- Convert curvature to differential drive speeds ---
#         # v_right = v * (1 + κ * W/2)
#         # v_left  = v * (1 - κ * W/2)
#         right_speed = base_speed * (1.0 + curvature * wheelbase / 2.0)
#         left_speed  = base_speed * (1.0 - curvature * wheelbase / 2.0)
        
#         # Clamp to valid PWM range [0, 255]
#         # Negative = going backward on that wheel, which helps tight turns
#         right_speed = int(max(-255, min(255, right_speed)))
#         left_speed  = int(max(-255, min(255, left_speed)))
        
#         send_steer_request(left=left_speed, right=right_speed)


def pure_pursuit(plan, lookahead_dist=0.7, base_speed=180, wheelbase=0.12):
    
    # === NEW: coarse alignment before starting ===
    first_lookahead = find_lookahead_point(plan, c_pos, lookahead_dist)
    angle_to_target = angle_between_points(c_pos, [first_lookahead[0], 0, first_lookahead[1]])
    initial_error = abs(normalize_angle(angle_to_target - c_rad))
    
    if initial_error > 0.3:  # more than ~17 degrees off -> turn first
        print(f"Initial heading error {initial_error:.2f} rad, turning first...")
        turnToTarget(False, [first_lookahead[0], 0, first_lookahead[1]])
    # === end new part ===

    goal = [plan[-1][0], 0, plan[-1][1]]

    while True:
        streaming_client.update_sync()

        if dist(c_pos[0], goal[0], c_pos[2], goal[2]) < 0.14:
            send_stop_request()
            break

        lookahead_point = find_lookahead_point(plan, c_pos, lookahead_dist)
        angle_to_target = angle_between_points(c_pos, [lookahead_point[0], 0, lookahead_point[1]])
        heading_error = normalize_angle(angle_to_target - c_rad)

        # === NEW: also recover mid-path if we get very lost ===
        if abs(heading_error) > 1.2:
            send_stop_request()
            turnToTarget(False, [lookahead_point[0], 0, lookahead_point[1]])
            continue
        # === end new part ===

        curvature = 2.0 * math.sin(heading_error) / lookahead_dist
        # right_speed = int(max(0, min(255, base_speed * (1.0 + curvature * wheelbase / 2.0))))
        # left_speed  = int(max(0, min(255, base_speed * (1.0 - curvature * wheelbase / 2.0))))

        # send_steer_request(left=left_speed, right=right_speed)
        # AFTER - both wheels always move forward, just at different speeds
        min_speed = 20  # minimum forward speed, tune this

        right_speed = base_speed * (1.0 + curvature * wheelbase / 2.0)
        left_speed  = base_speed * (1.0 - curvature * wheelbase / 2.0)

        # Scale down if either exceeds 255
        max_val = max(abs(right_speed), abs(left_speed))
        if max_val > 255:
            right_speed = right_speed * 255 / max_val
            left_speed  = left_speed  * 255 / max_val

        # Lift the slower wheel up to min_speed without changing the faster one
        min_val = min(right_speed, left_speed)
        if min_val < min_speed:
            diff = min_speed - min_val
            right_speed += diff
            left_speed  += diff

        right_speed = int(min(255, right_speed))
        left_speed  = int(min(255, left_speed))

        send_steer_request(left=left_speed, right=right_speed)





def find_lookahead_point(plan, robot_pos, lookahead_dist):
    """
    Find the point on the path that is lookahead_dist ahead of the robot.
    Walks along path segments and finds where the circle of radius 
    lookahead_dist intersects the path.
    """
    # Find the closest point on the path first
    closest_idx = 0
    min_dist = float('inf')
    for i, point in enumerate(plan):
        d = dist(robot_pos[0], point[0], robot_pos[2], point[1])
        if d < min_dist:
            min_dist = d
            closest_idx = i
    
    # Walk forward from closest point until we exceed lookahead distance
    for i in range(closest_idx, len(plan) - 1):
        d = dist(robot_pos[0], plan[i][0], robot_pos[2], plan[i][1])
        if d >= lookahead_dist:
            return plan[i]
    
    # If no point found at that distance, return the last point
    return plan[-1]


def smooth_path(plan, iterations=100, alpha=0.5, beta=0.3):
    """
    Gradient descent path smoothing (keeps endpoints fixed).
    alpha: how much to pull toward original path
    beta: how much to pull toward neighbors (smoothness)
    """
    smoothed = np.copy(plan)
    for _ in range(iterations):
        for i in range(1, len(smoothed) - 1):
            smoothed[i] += alpha * (plan[i] - smoothed[i])
            smoothed[i] += beta * (smoothed[i-1] + smoothed[i+1] - 2 * smoothed[i])
    return smoothed


















   


# TODO CHECK IF I CAN TO DELETE THIS FUNCTION
# def add_cube_obstacle(env, cube_pos, size=0.2):
#     """
#     Adds a square obstacle representing a cube to the environment.

#     Args:
#         env (MapEnvironment): The planning environment object.
#         cube_pos (list): The [x, y, z] position of the cube (only x and z used).
#         size (float): The size of the cube (side length in meters).
#     """
#     cx, cz = cube_pos[0], cube_pos[2]
#     half = size / 2
#     obstacle = [
#         [cx - half, cz - half],
#         [cx + half, cz - half],
#         [cx + half, cz + half],
#         [cx - half, cz + half],
#         [cx - half, cz - half]
#     ]
#     env.obstacles.append(Polygon(obstacle))

# TODO MOVE TO ANOTHER FILE 
# Function get data where the  robot car and where the cube is and calculate the path to the cube
def get_path_to_goal(start_pos, goal_pos, cube_obstacles=[]):
    global z  # Use the global variable z
    json_file_path = "path_algorithms/map1.json"
    planning_env = MapEnvironment(json_file=json_file_path)
    # Initialize the map environment with the JSON file path
    planning_env.start = np.array([start_pos[0], start_pos[2]])  # Use x and y coordinates for the start position
    planning_env.goal = np.array([goal_pos[0], goal_pos[2]])  # Use x and y coordinates for the goal position

    # Add dynamic obstacles (e.g., cubes detected in the environment)
    for cube_pos in cube_obstacles:
        if cube_pos != goal_pos:  # Skip if cube_pos matches goal_pos
            print(f"Adding cube obstacle NOT GOAL at position {cube_pos}.")
            add_cube_obstacle(planning_env, cube_pos)

    # Create an instance of the RCSPlanner with the planning environment
    print("Creating RRT* planner...")
    planner = RRTStarPlanner(planning_env=planning_env, ext_mode='E2', goal_prob=0.40, k=10)
    print(f"Planning path from {planning_env.start} to {planning_env.goal}...")
    # Execute the planning algorithm to get the path
    plan = planner.plan()

    # for-web
    # planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(), name='for_web')
    # Visualize the map with the computed plan and expanded nodes
    print("Visualizing the map with the computed plan and expanded nodes...")
    planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(), name='4main'+str(y))  # Convert z to string
    # print('Successfully planned path')
    z += 1  # Increment the global variable z
    return plan
# use it to go to the base position
def go_to_goal(goal_pos):

    finshed = False
    while not finshed:
        streaming_client.update_sync()
        cur_t_pos1 = t_pos1
        cur_t_pos2 = t_pos2  # Use the current position of t_pos2
        cur_t_pos3 = t_pos3  # Use the current position of t_pos3
        obsticles = [t_pos1, t_pos2, t_pos3]  # List of dynamic obstacles (cubes)
        if y == 606:
            obsticles.remove(t_pos2)
        elif y == 604:
            obsticles.remove(t_pos1) 
        elif y == 607:
            obsticles.remove(t_pos3)
        plan = get_path_to_goal(c_pos, goal_pos,obsticles)
        finshed = True
        for i in range(len(plan) - 1):
            
        #     is_flipped([t_rot1, t_rot2, t_rot3])
        #     # out_limits(c_pos, t_pos)
        #     # print("2")
        #     go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]
        #     # print("Current position:", go_to_pos)
        #     turnToTarget(False, go_to_pos)
        #     GoToTarget(False, go_to_pos)
        #     if(dist(t_pos1[0], cur_t_pos1[0], t_pos1[2], cur_t_pos1[2]) > 0.1 and y!=604) or( dist(t_pos2[0], cur_t_pos2[0], t_pos2[2], cur_t_pos2[2]) > 0.1 and y!=606) or (dist(t_pos3[0], cur_t_pos3[0], t_pos3[2], cur_t_pos3[2])> 0.1 and y!=607) :
        #         # print("continue")
        #         finshed = False
        #         break
        #     if dist(c_pos[0], t_pos[0], c_pos[2], t_pos[2]) > 0.15:
        #         send_servo_request(30)
        #         return []
            pure_pursuit(plan, lookahead_dist=0.35, base_speed=180)
    
    # plan = smooth_path(plan)
                
    return plan  # Return the planned path for further use or analysis



def get_path_to_target():
    finshed = False
    while not finshed:
        streaming_client.update_sync()
        cur_t_pos2 = t_pos2  # Use the current position of t_pos2
        cur_t_pos1 = t_pos1  # Use the current position of t_pos1
        cur_t_pos3 = t_pos3  # Use the current position of t_pos3
        plan = get_path_to_goal(c_pos, t_pos, [t_pos1,t_pos2,t_pos3])  # Pass t_pos1 as a dynamic obstacle
        finshed = True
        for i in range(len(plan) - 1):
            is_flipped([t_rot1, t_rot2, t_rot3])
            out_limits(c_pos, t_pos)
            go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]  # Add an extra element (e.g., 0) to go_to_pos
            # print("Current position:", go_to_pos)
            # turnToTarget(False, go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)
            if dist(t_pos2[0], cur_t_pos2[0], t_pos2[2], cur_t_pos2[2]) > 0.1 or dist(t_pos1[0], cur_t_pos1[0], t_pos1[2], cur_t_pos1[2]) > 0.1 or dist(t_pos3[0], cur_t_pos3[0], t_pos3[2], cur_t_pos3[2]) > 0.1:    
                print("continue")
                finshed = False
                break
         
try:
    extract_order(word) 
    print(arr)
    y= arr[0]  # Get the first target ID from the array
    send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(1)  # Allow some time for the client to start and receive data

        #sys.stdout.flush()  # Ensure that the output is flushed immediately
        print("Streaming started. Waiting for data...", flush=True)
        
        # TODO
        # GoBack()
       
        #sys.stdout.flush()  # Ensure that the output is flushed immediately
        for i in range(3):
            print(i)
            y = arr[i]  # Get the current target ID from the array
            
            # while for 1 sec
            # start_time = time.time()
            # while time.time() - start_time >= 1.0:
            #     continue
            out_limits(c_pos, t_pos)
            is_flipped([t_rot1, t_rot2, t_rot3])
            # print("Current target ID:", y)
            #sys.stdout.flush()  # Ensure that the output is flushed immediately
            # y=607
            # print(f"cccccccccccccheck correct slot {t_pos}")
            if not correct_slot(i,t_pos):
                # TODO PRINT
                plan = []
                while len(plan) == 0:
                    get_path_to_target()  # Get the path to the target position
                    send_servo_request(80) # close the servo
                    plan = go_to_goal(bases[i])  # Move to the base position first
                turnToTarget(False, [plan[-1][0]+0.4,0.09, y_base[i]])
                #sys.stdout.flush()  # Ensure that the output is flushed immediately
                GoToTarget(False, [plan[-1][0]+0.4,0.09, y_base[i]])  # Move slightly forward after reaching the target
                send_servo_request(30)
                #sys.stdout.flush()  # Ensure that the output is flushed immediately
                GoBack()
            
        
        
    # send_servo_request(30)
    # print("c_pos: ", c_pos, "c_rot: ", c_rot, "c_rad: ", c_rad)
    # print("t_pos: ", t_pos, "t_rot: ", t_rot, "t_rad: ", t_rad)
    #sys.stdout.flush()  # Ensure that the output is flushed immediately
    # exit()


# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack #system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    # print(f"An unexpected error occurred: {e}", file=#sys.stderr)
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

