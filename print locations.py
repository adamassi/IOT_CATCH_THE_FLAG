import time
import socket
from natnet import DataDescriptions, DataFrame, NatNetClient
import numpy as np
import math
from datetime import datetime
import optitrack_data_handling
from helper_functions import dist, angle_between_points, is_out_of_board 
# import algorithms as al
import matplotlib.pyplot as plt
# from commands import send_led_error_command
import requests
# from stam import send_servo_request, send_go_request, send_stop_request, send_lift_request, send_right_request ,angle_between_points, send_beep_request, send_steer_request
from robotCommands import *
from conversion import normalize_angle



c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0


base_pos = [4.13, 0.09, 0.26]
# Define car_positions globally
car_positions = []
ctf_positions = []

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
    global car_positions  # Declare car_positions as global
    global ctf_positions  # Declare ctf_positions as global



    for ms in data_frame.rigid_bodies:
            
            if ms.id_num == 605:
                # Handle the chaser's data
                c_pos, c_rot, c_rad = optitrack_data_handling.handle_frame(ms)
                # Append the current position of the car to car_positions
                car_positions.append([c_pos[0], c_pos[2]])
                #print(f"Chaser rad: {c_rad}")
                #print(f"Type of c_pos600: {type(c_pos)}")
            # if ms.id_num == 604:
            #     # Handle the target's data
            #     t_pos, t_rot, t_rad = chaser_data_handling.handle_frame(ms, "ctf_cube")
            if ms.id_num == 606:
                # Handle the target's data
                t_pos, t_rot, t_rad = optitrack_data_handling.handle_frame(ms)
                print(f"Target rad: {t_rad}, Target pos: {t_pos}, Target rot: {t_rot}")
                ctf_positions.append([t_pos[0], t_pos[2]])
                
                
    
    #print("received new frame")














streaming_client = NatNetClient(
    server_ip_address="132.68.35.2",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    
    use_multicast=False  # Use unicast instead of multicast for communication
)




streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)


try:
    
    
    with streaming_client:
        streaming_client.request_modeldef()
        # for _ in range(500):
        #     streaming_client.update_sync()
        #     update_live_plot(chaser_plot, target_plot, arrow_artist, car_positions, [t_pos[0], t_pos[2]], c_rad)

        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        #time.sleep(0.1)  # Allow some time for the client to start and receive data
        print("Streaming started. Waiting for data...")
        #GoToTarget(False, [0, 0, 0])
        # turnToTarget()
        # turnToTarget()
        # GoToTarget()
        print("Chaser is facing the target.")
    
    #     send_servo_request(80)
    #     send_beep_request(50)
    #     time.sleep(0.1)
    #     send_beep_request(50)
    #     # time.sleep(1)
    #     turnToTarget(False, base_pos)
    #     turnToTarget(False, base_pos)
    #     GoToTarget(False, base_pos)


        
    # send_servo_request(30)
    # send_beep_request(50)
    # send_beep_request(50)
    # time.sleep(0.1)
    # send_beep_request(50)
    # while True:
    #     # print("c_pos: ", c_pos, "c_rot: ", c_rot, "c_rad: ", c_rad)
    #     print("t_pos: ", , "t_rot: ", t_rot, "t_rad: ", t_rad)
    #      streaming_client.update_sync()
    #     time.sleep(1)
    #print(car_positions)
    #plot_positions(car_positions, [[t_pos[0], t_pos[2]]])
    while True:
        streaming_client.update_sync()
        time.sleep(0.1)  # Adjust the sleep duration as needed to control the update rate
    








# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

