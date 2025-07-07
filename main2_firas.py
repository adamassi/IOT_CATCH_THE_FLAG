from natnet_client import DataDescriptions, DataFrame, NatNetClient
import optitrack_data_handling
import socket
from robotCommands import *
from helper_functions import angle_between_points, dist
from conversion import normalize_angle
from PARAMETERS import PositionConfig, RigidBodyIDs, OptiTrackConfig





class Cube:
    def __init__(self, id_num):
        self.id_num = id_num
        self.pos = [0, 0, 0]
        self.rot = 0
        self.rad = 0

    def update_from_marker(self, marker_data):
        self.pos, self.rot, self.rad = optitrack_data_handling.handle_frame(marker_data)

car_pos, car_rot, car_rad = [0,0,0], 0, 0 # ID numbers from OptiTrack
cubes = [Cube(id_num) for id_num in RigidBodyIDs.CUBES_IDS]



###############################
##### OptiTrack functions #####
############################### 
def receive_new_frame(data_frame: DataFrame):
    global car_pos, car_rot, car_rad ########is it needed to be global?
    global cubes

    for ms in data_frame.rigid_bodies:
        if ms.id_num == 605:
            car_pos, car_rot, car_rad = optitrack_data_handling.handle_frame(ms)
        else:
            for cube in cubes:
                if ms.id_num == cube.id_num:
                    cube.update_from_marker(ms)


def receive_new_desc(desc: DataDescriptions):
    # This function is triggered when new data descriptions are received from the OptiTrack system.
    print("Received data descriptions.")  # Notify that data descriptions have been received.



streaming_client = NatNetClient(
    server_ip_address = OptiTrackConfig.SERVER_IP,  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)

streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)






###############################
##### contrling the robot #####
###############################

def turnToTarget(cube_number=None, target_pos=None, is_cube=True):
    left, right, stop = 1, 2, 3
    turning_state = stop

    while True:
        streaming_client.update_sync()
        curr_car_pos, curr_car_rad = car_pos, car_rad

        if is_cube:
            if cube_number < 1 or cube_number > len(cubes):
                print(f"Invalid cube number: {cube_number}")
                return
            curr_target_pos = cubes[cube_number - 1].pos
        else:
            curr_target_pos = target_pos

        angle = angle_between_points(curr_car_pos, curr_target_pos)
        normalized_angle = normalize_angle(angle - curr_car_rad)

        if abs(normalized_angle) < 0.07:
            if turning_state != stop:
                send_stop_request()
            break
        elif normalized_angle < 0:
            if turning_state != left:
                turning_state = left
                send_lift_request(60)
        else:
            if turning_state != right:
                turning_state = right
                send_right_request(60)



def GoToTarget(cube_number=None, target_pos=None, is_cube=True):
    streaming_client.update_sync()
    curr_car_pos = car_pos
    curr_car_rad = car_rad

    # Get initial target position
    if is_cube:
        if cube_number is None or cube_number < 1 or cube_number > len(cubes):
            print(f"Invalid cube number: {cube_number}")
            return
        curr_target_pos = cubes[cube_number - 1].pos
    else:
        if target_pos is None:
            print("Target position must be provided if not using a cube.")
            return
        curr_target_pos = target_pos

    # Start moving if far enough
    if dist(curr_car_pos[0], curr_target_pos[0], curr_car_pos[2], curr_target_pos[2]) >= 0.15:
        send_go_request()

    while True:
        streaming_client.update_sync()
        curr_car_pos = car_pos
        curr_car_rad = car_rad

        # Update target position if it's a cube (because it may move)
        if is_cube:
            curr_target_pos = cubes[cube_number - 1].pos

        # Stop when close enough
        if dist(curr_car_pos[0], curr_target_pos[0], curr_car_pos[2], curr_target_pos[2]) < 0.2:
            send_stop_request()
            break

        # Check angle and realign if necessary
        angle = angle_between_points(curr_car_pos, curr_target_pos)
        normalized_angle = normalize_angle(angle - curr_car_rad)
        if abs(normalized_angle) > 0.2:
            # send_stop_request()
            turnToTarget(cube_number=cube_number, target_pos=target_pos, is_cube=is_cube)
            send_go_request()







try:
    
    send_servo_request(30)
    with streaming_client:
        streaming_client.request_modeldef()
        streaming_client.update_sync()
        time.sleep(0.1)  # Allow some time for the client to start and receive data

        print("Streaming started. Waiting for data...")
        
        turnToTarget(cube_number=3, is_cube=True)  # Turn to the first cube
        GoToTarget(cube_number=3, is_cube=True)  # Go to the first cube
        # print("Chaser is facing the target.")
    
        send_servo_request(80)
        send_beep_request(50)
        time.sleep(0.1)
        send_beep_request(50)
        
        turnToTarget(target_pos = PositionConfig.BASE_POS_3, is_cube=False)  # Turn to the base position
        GoToTarget(target_pos = PositionConfig.BASE_POS_3, is_cube=False)


        
    send_servo_request(30)
    send_beep_request(50)
    time.sleep(0.1)
    send_beep_request(50)
    time.sleep(0.1)
    send_beep_request(50)

    





# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here


        

