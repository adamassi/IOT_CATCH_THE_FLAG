
from natnet import DataDescriptions, DataFrame, NatNetClient
from robotCommands import *
from PARAMETERS import *




c_pos, c_rot, c_rad = [0,0,0], 0, 0
t_pos1, t_rot1, t_rad1 = [0,0,0], 0, 0
t_pos2, t_rot2, t_rad2 = [0,0,0], 0, 0
t_pos3, t_rot3, t_rad3 = [0,0,0], 0, 0
t_pos, t_rot, t_rad = [0,0,0], 0, 0





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

streaming_client = NatNetClient(
    server_ip_address = OptiTrackConfig.SERVER_IP, #"132.68.35.255",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)


streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)
