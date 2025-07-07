import time
import socket
from natnet_client import DataDescriptions, DataFrame, NatNetClient
import numpy as np
import math
from datetime import datetime
import chaser_data_handling
from helperFunc import dist, is_out_of_board 
import algorithms as al

from commands import send_led_error_command

from stam import *
# from stam import send_servo_request, send_go_request, send_stop_request, send_lift_request, send_right_request ,angle_between_points, send_steer_request,send_back_request
from conversion import normalize_angle
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTStarPlanner import RRTStarPlanner
from shapely.geometry import Polygon  # Ensure this is imported
import sys

word = sys.argv[1]
arr=[]





c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos1, t_rot1, t_rad1 = [0,0,0], 0, 0
t_pos2, t_rot2, t_rad2 = [0,0,0], 0, 0
t_pos3, t_rot3, t_rad3 = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0
base_pos = [3.9, 0.09, 0.28]
base_pos2 = [3.9, 0.09, -0.09]  # Define a second base position for the second cube
z = 1  # Initialize a global variable for iteration count
w=1
y=606
def extract_order(word):
    """
    Extracts the order of characters from the input word.
    
    """
    for c in word:
        if c=='I':
            arr.append(604)
        elif c=='O':
            arr.append(606)
        elif c=='T':
            arr.append(607)


def receive_new_desc(desc: DataDescriptions):
    # This function is triggered when new data descriptions are received from the OptiTrack system.
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
    global t_pos2, t_rot2, t_rad2  # Add variables for ctf_cube2
    global t_pos1, t_rot1, t_rad1  # Add variables for ctf_cube1
    global t_pos3, t_rot3, t_rad3  # Add variables for ctf_cube3
    for ms in data_frame.rigid_bodies:
        if ms.id_num == 605:
            # Handle the chaser's data
            c_pos, c_rot, c_rad = chaser_data_handling.handle_frame(ms)
        if ms.id_num == y:
            # Handle the target's data (ctf_cube)
            t_pos, t_rot, t_rad = chaser_data_handling.handle_frame(ms)
        if ms.id_num == 604:
            # Handle the second cube's data (ctf_cube2)
            t_pos1, t_rot1, t_rad1 = chaser_data_handling.handle_frame(ms)
        if ms.id_num == 606:
            # Handle the second cube's data (ctf_cube2)
            t_pos2, t_rot2, t_rad2 = chaser_data_handling.handle_frame(ms)
        if ms.id_num == 607:
            # Handle the third cube's data (ctf_cube3)
            t_pos3, t_rot3, t_rad3 = chaser_data_handling.handle_frame(ms)
    #print("received new frame")














streaming_client = NatNetClient(
    server_ip_address="132.68.35.2",  # IP address of the OptiTrack server
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
        else:
            if not turning_state == right:
                turning_state = right
                send_right_request(60)
    # time.sleep(1)

def GoToTarget(is_cube = True, curr_t_pos = t_pos):
    if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) >= 0.15:
        send_go_request()
        while True:
            streaming_client.update_sync()
            if is_cube:
                curr_t_pos = t_pos
            if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) < 0.15:
                send_stop_request()
                break
            angle = angle_between_points(c_pos, curr_t_pos)
            normalized_angle = normalize_angle(angle - c_rad)
            if abs(normalized_angle) > 0.5:
                #send_stop_request()
                turnToTarget(is_cube, curr_t_pos)
                send_go_request()
def GoBack( ):
    # TODO check the tut of the car or y
    if c_pos[0] >= 3.9:
        send_back_request()
        send_start_beeping_request()
        while True:
            
            streaming_client.update_sync()
            if c_pos[0] < 3.9:
                send_stop_request()
                break
        send_stop_beeping_request()
            

    # time.sleep(1)



def add_cube_obstacle(env, cube_pos, size=0.2):
    """
    Adds a square obstacle representing a cube to the environment.

    Args:
        env (MapEnvironment): The planning environment object.
        cube_pos (list): The [x, y, z] position of the cube (only x and z used).
        size (float): The size of the cube (side length in meters).
    """
    cx, cz = cube_pos[0], cube_pos[2]
    half = size / 2
    obstacle = [
        [cx - half, cz - half],
        [cx + half, cz - half],
        [cx + half, cz + half],
        [cx - half, cz + half],
        [cx - half, cz - half]
    ]
    env.obstacles.append(Polygon(obstacle))


# Function get data where the  robot car and where the cube is and calculate the path to the cube
def get_path_to_goal(start_pos, goal_pos, cube_obstacles=[]):
    global z  # Use the global variable z
    json_file_path = "our_code/path_algorithms/map1.json"
    planning_env = MapEnvironment(json_file=json_file_path)
    # Initialize the map environment with the JSON file path
    planning_env.start = np.array([start_pos[0], start_pos[2]])  # Use x and y coordinates for the start position
    planning_env.goal = np.array([goal_pos[0], goal_pos[2]])  # Use x and y coordinates for the goal position

    # Add dynamic obstacles (e.g., cubes detected in the environment)
    for cube_pos in cube_obstacles:
        if cube_pos != goal_pos:  # Skip if cube_pos matches goal_pos
            print(f"Adding cube obstacle at position {cube_pos}.")
            add_cube_obstacle(planning_env, cube_pos)

    # Create an instance of the RCSPlanner with the planning environment
    planner = RRTStarPlanner(planning_env=planning_env, ext_mode='E2', goal_prob=0.40, k=10)
    print(f"Planning path from {planning_env.start} to {planning_env.goal}...")
    # Execute the planning algorithm to get the path
    plan = planner.plan()

    # Visualize the map with the computed plan and expanded nodes
    planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states(), name='for_web')  # Convert z to string
    print('Successfully planned path')
    z += 1  # Increment the global variable z
    return plan
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
            go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]
            print("Current position:", go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)
            if(dist(t_pos1[0], cur_t_pos1[0], t_pos1[2], cur_t_pos1[2]) > 0.1 and y!=604) or( dist(t_pos2[0], cur_t_pos2[0], t_pos2[2], cur_t_pos2[2]) > 0.1 and y!=606) or dist(t_pos3[0], cur_t_pos3[0], t_pos3[2], cur_t_pos3[2]) > 0.1:
                print("continue")
                finshed = False
                break
    return plan  # Return the planned path for further use or analysis
# Function to get the path to the target position, considering t_pos2 as a dynamic obstacle



def get_path_to_target():
    # plan = []
        # GoBack()
    finshed = False
    while not finshed:
        streaming_client.update_sync()
        cur_t_pos2 = t_pos2  # Use the current position of t_pos2
        cur_t_pos1 = t_pos1  # Use the current position of t_pos1
        cur_t_pos3 = t_pos3  # Use the current position of t_pos3
        plan = get_path_to_goal(c_pos, t_pos, [t_pos1,t_pos2,t_pos3])  # Pass t_pos1 as a dynamic obstacle
        finshed = True
        for i in range(len(plan) - 1):
           
            go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]  # Add an extra element (e.g., 0) to go_to_pos
            print("Current position:", go_to_pos)
            # turnToTarget(False, go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)
            if dist(t_pos2[0], cur_t_pos2[0], t_pos2[2], cur_t_pos2[2]) > 0.1 or dist(t_pos1[0], cur_t_pos1[0], t_pos1[2], cur_t_pos1[2]) > 0.1 or dist(t_pos3[0], cur_t_pos3[0], t_pos3[2], cur_t_pos3[2]) > 0.1:    
                print("continue")
                finshed = False
                break
        print(f"{finshed}AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
          

try:
    send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(1)  # Allow some time for the client to start and receive data
        print("Streaming started. Waiting for data...")
        plan = []
        # GoBack()
        for i in range(1):
            extract_order(word)
            y = arr[i]  # Get the current target ID from the array
            print("Current target ID:", y)
            get_path_to_target()  # Get the path to the target position
            send_servo_request(80)
            plan = go_to_goal(base_pos)  # Move to the base position first
            turnToTarget(False, [plan[-1][0]+0.3,0.09, 0.28])
            GoToTarget(False, [plan[-1][0]+0.3,0.09, 0.28])  # Move slightly forward after reaching the target
            send_servo_request(30)
            GoBack()
        
        
    # send_servo_request(30)
    print("c_pos: ", c_pos, "c_rot: ", c_rot, "c_rad: ", c_rad)
    print("t_pos: ", t_pos, "t_rot: ", t_rot, "t_rad: ", t_rad)








# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

