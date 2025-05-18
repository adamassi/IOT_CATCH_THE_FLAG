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


# ip_address = None
# try:
#     ip_address = socket.gethostbyname("esp32.local")
#     #TODELETE OR FIX AAAAAAAAAA
#     send_led_error_command(ip_address, 80, 4, "low")
#     send_led_error_command(ip_address, 80, 15, "low")
#     print(f"The IP address of esp32.local is {ip_address}\n\n")
# except socket.gaierror as e:
#     print(f"Dear friend !!\nDNS resolution failed:\nPlease check the following:\n"
#           f"1.The robot chaser is powered on. \n"
#           f"2.The router is working properly. \n"
#           f"3.The battery is full.  \n"
#           f"4.The wifi configuration."
#           f"\n\n\n{e}")
#     #lazem arg3ha
#     #exit()
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")





port = 80

backwards_driving = True
close_break = False
stop = False

# y up -> x,z planar motion. yaw is around the third parameter.
i, num_frames = 0, 0
c_pos, c_rot, c_rad = 0, 0, 0
t_pos, t_rot, t_rad = 0, 0, 0
# Initialize lists to keep track of chaser and target positions
chaser_positions = []
target_positions = []
WB = 0.14
MAX_STEER = np.deg2rad(30.0)  # maximum steering angle [rad]
# initial state
state = 0
# initial yaw compensation
pp = 0
target_pos = 0
steering_angle = 0
prev_target_x = None
prev_target_y = None
prev_time = None
current_time = None
timestamp = None
drive_b = None


ROBOT_STATE = 1 #1 is IDLE, 2 is turning
desired_yaw = 0



def receive_new_desc(desc: DataDescriptions):
    # This function is triggered when new data descriptions are received from the OptiTrack system.
    # It processes the data descriptions and checks for a specific marker set named 'IOT_car'.

    print("Received data descriptions.")  # Notify that data descriptions have been received.

    # Iterate through the marker sets in the data descriptions.
    for ms in desc.marker_sets:
        # Check if the marker set name matches 'IOT_car'.
        if ms.name == 'IOT_car':
            # If a match is found, print the entire data description.
            print(desc)




def receive_new_frame(data_frame: DataFrame):
    global i, num_frames
    # car position and rotation and radius
    global c_pos, c_rot, c_rad
    global t_pos, t_rot, t_rad
    global state, pp
    global target_pos, steering_angle, stop
    global target_v, prev_target_x, prev_target_y
    global chaser_positions, target_positions  # Track positions
    global prev_time
    global WB
    global drive_b
    # Increment frame counter to keep track of the number of frames processed
    num_frames += 1

    # Process every 100th frame to avoid excessive processing
    if (num_frames % 30 == 0):
        # Iterate through the rigid bodies in the data frame to extract positions
        for ms in data_frame.rigid_bodies:
            if ms.id_num == 600:
                # Handle the chaser's data
                c_pos, c_rot, c_rad = chaser_data_handling.handle_frame(ms, "CHASER")
            if ms.id_num == 601:
                # Handle the target's data
                t_pos, t_rot, t_rad = chaser_data_handling.handle_frame(ms, "TARGET")
        #if ROBOT_STATE == 2:
    if dist(c_pos[0], t_pos[0], c_pos[2], t_pos[2]) < 0.25:
            print(f"YEYYYYY \nThe robot chaser got the target.")
    if is_out_of_board(c_pos[0], c_pos[2]):
            print(f"Chaser board limit fail. Check if the chaser robot is on the board.")

    path= []
    path=al.calculate_rrtS(c_pos[0], c_pos[2], t_pos[0], t_pos[2])
    for i in range(len(path)):
        print(path[i])    



streaming_client = NatNetClient(
    server_ip_address="132.68.35.255",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)




streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)


# streaming_client.request_modeldef()
# streaming_client.update_async()



# Request model definitions from the server to trigger a data description packet
try:
    with streaming_client:
        # Request the model definitions from the OptiTrack server
        streaming_client.request_modeldef()

        # Loop to receive and process frames for a specific duration
        for i in range(100):
            # Check if a condition to stop processing is met
            if close_break and stop:
                break

            # Sleep for 1 second before updating
            time.sleep(1)

            # Update the streaming client to process incoming data synchronously
            streaming_client.update_sync()

            # Print the number of frames received
            print(f"Received {num_frames} frames in {i + 1}s")


# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(
        f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

