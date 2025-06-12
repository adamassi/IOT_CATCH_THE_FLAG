import time
import socket
from natnet_client import DataDescriptions, DataFrame, NatNetClient
import numpy as np
import math
from datetime import datetime
import chaser_data_handling
from helperFunc import dist, is_out_of_board 
import algorithms as al
import matplotlib.pyplot as plt
from commands import send_led_error_command
import requests
from stam import send_servo_request, send_go_request, send_stop_request, send_lift_request, send_right_request ,angle_between_points
from conversion import normalize_angle
from path_algorithms.RCSPlanner import RCSPlanner
from path_algorithms.MapEnvironment import MapEnvironment
from path_algorithms.RRTPlanner import RRTPlanner
from path_algorithms.RRTStarPlanner import RRTStarPlanner




c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0
base_pos = [4, 0.09, 0]

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


    for ms in data_frame.rigid_bodies:
            
            if ms.id_num == 605:
                # Handle the chaser's data
                c_pos, c_rot, c_rad = chaser_data_handling.handle_frame(ms, "ctf_car")
                #print(f"Chaser rad: {c_rad}")
                #print(f"Type of c_pos600: {type(c_pos)}")
            if ms.id_num == 604:
                # Handle the target's data
                t_pos, t_rot, t_rad = chaser_data_handling.handle_frame(ms, "ctf_cube")
    
    #print("received new frame")














streaming_client = NatNetClient(
    server_ip_address="132.68.35.255",  # IP address of the OptiTrack server
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
                send_lift_request(150)
        else:
            if not turning_state == right:
                turning_state = right
                send_right_request(150)
    time.sleep(1)

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
            if abs(normalized_angle) > 0.15:
                #send_stop_request()
                turnToTarget(is_cube, curr_t_pos)
                send_go_request()

    time.sleep(1)

# Function get data where the  robot car and where the cube is and calculate the path to the cube
def get_path_to_target(start_pos, goal_pos):
    # Initialize the map environment with the JSON file path
    json_file_path = "our_code/path_algorithms/map1.json"
    planning_env = MapEnvironment(json_file=json_file_path)
    planning_env.start = np.array([start_pos[0], start_pos[2]])  # Use x and y coordinates for the start position
    planning_env.goal = np.array([goal_pos[0], goal_pos[2]])  # Use x and y coordinates for the goal position

    # Create an instance of the RCSPlanner with the planning environment
    planner = RRTStarPlanner(planning_env=planning_env,ext_mode='E2',goal_prob=0.05,k=10)

    # Execute the planning algorithm to get the path
    plan = planner.plan()

    # Visualize the map with the computed plan and expanded nodes
    planner.planning_env.visualize_map(plan=plan, tree_edges=planner.tree.get_edges_as_states())
    return plan
    
try:
    send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(1)  # Allow some time for the client to start and receive data
        print("Streaming started. Waiting for data...")
        plan = []
        plan=get_path_to_target(c_pos, t_pos)

        #iteration nover the plan
        for i in range(len(plan) - 1):
            go_to_pos = [plan[i+1][0],0, plan[i+1][1]]  # Add an extra element (e.g., 0) to go_to_pos
            print("Current position:", go_to_pos)
            turnToTarget(False, go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)

        # turnToTarget()
        # turnToTarget()
        # GoToTarget()
        print("Chaser is facing the target.")
    
        send_servo_request(57)
        plan=get_path_to_target(c_pos, base_pos)
        print("finished planening")
        for i in range(len(plan) - 1):
            go_to_pos = [plan[i+1][0],0, plan[i+1][1]]  # Add an extra element (e.g., 0) to go_to_pos
            print("Current position:", go_to_pos)
            turnToTarget(False, go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)
        
        # turnToTarget(False, base_pos)
        # turnToTarget(False, base_pos)
        # GoToTarget(False, base_pos)
        print("KNOW WE CAN GO TO THE TARGET POSITION")

        
    send_servo_request(30)
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

