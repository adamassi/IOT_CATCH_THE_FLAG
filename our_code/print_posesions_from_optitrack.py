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
from stam import send_servo_request, send_go_request, send_stop_request, send_lift_request, send_right_request ,angle_between_points, send_beep_request
from conversion import normalize_angle



c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0


base_pos = [4.13, 0.09, 0.26]
# Define car_positions globally
car_positions = []

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



    for ms in data_frame.rigid_bodies:
            
            if ms.id_num == 605:
                # Handle the chaser's data
                c_pos, c_rot, c_rad = chaser_data_handling.handle_frame(ms, "ctf_car")
                # Append the current position of the car to car_positions
                # car_positions.append((c_pos[0], c_pos[2]))
                #print(f"Chaser rad: {c_rad}")
                #print(f"Type of c_pos600: {type(c_pos)}")
            if ms.id_num == 604:
                # Handle the target's data
                t_pos, t_rot, t_rad = chaser_data_handling.handle_frame(ms, "ctf_cube")
    #print(f"ctf_car:  c_pos: {str(c_pos):<25} c_rot: {str(c_rot):<25} c_rad: {str(c_rad):<10}")
    
    # time.sleep(1)  # Sleep for a short duration to avoid flooding the console with messages
    #print("received new frame")














streaming_client = NatNetClient(
    server_ip_address="132.68.35.2",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    
    use_multicast=False  # Use unicast instead of multicast for communication
)




streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)


def plot_positions(car_positions, ctf_positions):
    """
    Plots the chaser and target positions over time.

    Args:
        car_positions (list of tuples): The tracked chaser positions, each tuple is (x, y).
        ctf_positions (list of tuples): The tracked target positions, each tuple is (x, y).
    """
    plt.figure(figsize=(6, 10))  # Set the figure size to 6x10 inches

    # Unpack chaser and target positions into x and y components
    chaser_x, chaser_y = car_positions[-1]
    target_x, target_y = ctf_positions[-1]

    # Plot chaser path with 'o' markers
    plt.plot(chaser_y, chaser_x, label="Chaser Path", marker='o')

    # Plot target path with 'x' markers
    plt.plot(target_y, target_x, label="Target Path", marker='x')

    # Label the x-axis and y-axis
    plt.xlabel('X Position')
    plt.ylabel('Y Position')

    # Set the plot title
    plt.title('Chaser and Target Paths Over Time')

    # Add legend to the plot for clarity
    plt.legend()

    # Add grid lines to the plot for better readability
    plt.grid(True)

    # Set the x-axis limits from -3 to 3
    plt.xlim(-3, 3)

    # Set the y-axis limits from -5 to 5
    plt.ylim(-5, 5)

    # Adjust the aspect ratio of the plot to fit the specified limits
    plt.gca().set_aspect('auto')

    # Display the plot
    plt.show()





    
try:
    # send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(1)  # Allow some time for the client to start and receive data
        print("Streaming started. Waiting for data...")
        print("ctf_car: c_pos{c_pos}, c_rot: {c_rot}, c_rad: {c_rad}")
        print("ctf_cube: t_pos{t_pos}, t_rot: {t_rot}, t_rad: {t_rad}")
        while True:
            # Continuously receive data frames
            streaming_client.update_sync()
            time.sleep(1)
            print(f"ctf_cube: t_pos: {str(t_pos):<25} t_rot: {str(t_rot):<25} t_rad: {str(t_rad):<10}")


        








# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here

