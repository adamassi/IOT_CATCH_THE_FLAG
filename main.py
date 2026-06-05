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
from path_algorithms.planner import *
from PARAMETERS import *


word = "OIT"  # Example word to extract order from

c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos1, t_rot1, t_rad1 = [0,0,0], 0, 0
t_pos2, t_rot2, t_rad2 = [0,0,0], 0, 0
t_pos3, t_rot3, t_rad3 = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0
y_base = [-0.15, 0.28, 0.67]  # List of base positions for the cubes
z = 1  # Initialize a global variable for iteration count
current_target_id = 604



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
        if ms.id_num == RigidBodyIDs.CAR:
            # Handle the chaser's data
            c_pos, c_rot, c_rad = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == current_target_id:
            # Handle the target's data (ctf_cube)
            t_pos, t_rot, t_rad = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == RigidBodyIDs.CUBE_1:
            # Handle the first cube's data (ctf_cube1)``
            t_pos1, t_rot1, t_rad1 = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == RigidBodyIDs.CUBE_2:
            # Handle the second cube's data (ctf_cube2)
            t_pos2, t_rot2, t_rad2 = optitrack_data_handling.handle_frame(ms)
        if ms.id_num == RigidBodyIDs.CUBE_3:
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
        else:
            if not turning_state == right:
                turning_state = right
                send_right_request(60)
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
            
            

   





# use it to go to the base position
def go_to_goal(goal_pos):

    finshed = False
    while not finshed:
        streaming_client.update_sync()
        cur_t_pos1 = t_pos1
        cur_t_pos2 = t_pos2  # Use the current position of t_pos2
        cur_t_pos3 = t_pos3  # Use the current position of t_pos3
        obsticles = [t_pos1, t_pos2, t_pos3]  # List of dynamic obstacles (cubes)
        if current_target_id == 606:
            obsticles.remove(t_pos2)
        elif current_target_id == 604:
            obsticles.remove(t_pos1) 
        elif current_target_id == 607:
            obsticles.remove(t_pos3)
        plan = get_path_to_goal(c_pos, goal_pos,obsticles)
        finshed = True
        for i in range(len(plan) - 1):
            
            is_flipped([t_rot1, t_rot2, t_rot3])
           
            go_to_pos = [plan[i+1][0], 0, plan[i+1][1]]
            # print("Current position:", go_to_pos)
            turnToTarget(False, go_to_pos)
            GoToTarget(False, go_to_pos)
            if(dist(t_pos1[0], cur_t_pos1[0], t_pos1[2], cur_t_pos1[2]) > 0.1 and current_target_id!=604) or ( dist(t_pos2[0], cur_t_pos2[0], t_pos2[2], cur_t_pos2[2]) > 0.1 and current_target_id!=606) or (dist(t_pos3[0], cur_t_pos3[0], t_pos3[2], cur_t_pos3[2])> 0.1 and current_target_id!=607) :
                # print("continue")
                finshed = False
                break
            if dist(c_pos[0], t_pos[0], c_pos[2], t_pos[2]) > 0.16:
                send_servo_request(30)
                return []
                
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
    arr = extract_order(word) 
    print(arr)
    current_target_id = arr[0]  # Get the first target ID from the array
    send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(1)  # Allow some time for the client to start and receive data

        #sys.stdout.flush()  # Ensure that the output is flushed immediately
        print("Streaming started. Waiting for data...", flush=True)
        
        
       
        #sys.stdout.flush()  # Ensure that the output is flushed immediately
        for i in range(3):
            print(i)
            current_target_id = arr[i]  # Get the current target ID from the array
            
            
            out_limits(c_pos, t_pos)
            is_flipped([t_rot1, t_rot2, t_rot3])
            if not correct_slot(i,t_pos):
                plan = []
                while len(plan) == 0:
                    get_path_to_target()  # Get the path to the target position and move there
                    send_servo_request(80) # close the servo
                    plan = go_to_goal(PositionConfig.bases[i])  # Move to the base position first
                turnToTarget(False, [plan[-1][0]+0.4,0.09, y_base[i]])
                #sys.stdout.flush()  # Ensure that the output is flushed immediately
                GoToTarget(False, [plan[-1][0]+0.4,0.09, y_base[i]])  # Move slightly forward after reaching the target
                send_servo_request(30)
                #sys.stdout.flush()  # Ensure that the output is flushed immediately
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

