from natnet_client import DataDescriptions, DataFrame, NatNetClient
import optitrack_data_handling
import socket
from robotCommands import *
from helper_functions import angle_between_points, dist
from conversion import normalize_angle
from PARAMETERS import PositionConfig

car_pos, car_rot, car_rad = [0,0,0], 0, 0
# cube_1_pos, cube_1_rot, cube_1_rad = [0,0,0], 0, 0
# cube_2_pos, cube_2_rot, cube_2_rad = [0,0,0], 0, 0
# cube_3_pos, cube_3_rot, cube_3_rad = [0,0,0], 0, 0

class Cube:
    def __init__(self, id_num):
        self.id_num = id_num
        self.pos = [0, 0, 0]
        self.rot = 0
        self.rad = 0

    def update_from_marker(self, marker_data):
        self.pos, self.rot, self.rad = optitrack_data_handling.handle_frame(marker_data)
cube_ids = [604, 606, 607]  # ID numbers from OptiTrack
cubes = [Cube(id_num) for id_num in cube_ids]


def receive_new_frame(data_frame: DataFrame):
    global car_pos, car_rot, car_rad

    for ms in data_frame.rigid_bodies:
        if ms.id_num == 605:
            car_pos, car_rot, car_rad = optitrack_data_handling.handle_frame(ms)
        else:
            for cube in cubes:
                if ms.id_num == cube.id_num:
                    cube.update_from_marker(ms)

###############################
##### OptiTrack functions #####
############################### 
def receive_new_desc(desc: DataDescriptions):
    # This function is triggered when new data descriptions are received from the OptiTrack system.
    # It processes the data descriptions and checks for a specific marker set named '*'.
    print("Received data descriptions.")  # Notify that data descriptions have been received.


# def receive_new_frame(data_frame: DataFrame):
#     global car_pos, car_rot, car_rad
#     global cube_1_pos, cube_1_rot, cube_1_rad
#     global cube_2_pos, cube_2_rot, cube_2_rad
#     global cube_3_pos, cube_3_rot, cube_3_rad

#     for ms in data_frame.rigid_bodies:
#             if ms.id_num == 605:
#                 car_pos, car_rot, car_rad = optitrack_data_handling.handle_frame(ms)
#             elif ms.id_num == 604:
#                 cube_1_pos, cube_1_rot, cube_1_rad = optitrack_data_handling.handle_frame(ms)
#             elif ms.id_num == 606:
#                 cube_2_pos, cube_2_rot, cube_2_rad = optitrack_data_handling.handle_frame(ms)
#             elif ms.id_num == 607:
#                 cube_3_pos, cube_3_rot, cube_3_rad = optitrack_data_handling.handle_frame(ms)


streaming_client = NatNetClient(
    server_ip_address="132.68.35.2",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)


streaming_client.on_data_description_received_event.handlers.append(receive_new_desc)
streaming_client.on_data_frame_received_event.handlers.append(receive_new_frame)






###############################
##### contrling the robot #####
###############################
# def turnToTarget(cube_number, target_pos, is_cube = True):
#     left, right, stop = 1, 2, 3
#     turning_state = stop
#     while True:
#         streaming_client.update_sync()
#         curr_car_pos, curr_car_rad = car_pos, car_rad
#         curr_target_pos = ()
#         if is_cube:
#             curr_t_pos = t_pos
#         angle = angle_between_points(curr_c_pos, curr_t_pos)
#         normalized_angle = normalize_angle(angle - curr_c_rad)
#         if abs(normalized_angle) < 0.07:
#             send_stop_request()
#             break
#         elif normalized_angle < 0:
#             if not turning_state == left:
#                 turning_state = left
#                 send_lift_request(60)
#         else:
#             if not turning_state == right:
#                 turning_state = right
#                 send_right_request(60)
#     # time.sleep(1)

# def GoToTarget(is_cube = True, curr_t_pos = t_pos):
#     if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) >= 0.15:
#         send_go_request()
#         while True:
#             streaming_client.update_sync()
#             if is_cube:
#                 curr_t_pos = t_pos
#             if dist(c_pos[0], curr_t_pos[0], c_pos[2], curr_t_pos[2]) < 0.15:
#                 send_stop_request()
#                 break
#             angle = angle_between_points(c_pos, curr_t_pos)
#             normalized_angle = normalize_angle(angle - c_rad)
#             if abs(normalized_angle) > 0.5:
#                 #send_stop_request()
#                 turnToTarget(is_cube, curr_t_pos)
#                 send_go_request()
# def GoBack( ):
    
#     if c_pos[0] >= 3.9:
#         send_back_request()
#         send_start_beeping_request()
#         while True:
            
#             streaming_client.update_sync()
#             if c_pos[0] < 3.9:
#                 send_stop_request()
#                 break
#         send_stop_beeping_request()
            



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
        # for _ in range(500):
        #     streaming_client.update_sync()
        #     update_live_plot(chaser_plot, target_plot, arrow_artist, car_positions, [t_pos[0], t_pos[2]], c_rad)

        streaming_client.request_modeldef()

        streaming_client.update_sync()
        #streaming_client.run_async()
        time.sleep(0.1)  # Allow some time for the client to start and receive data
        print("Streaming started. Waiting for data...")
        #GoToTarget(False, [0, 0, 0])
        turnToTarget(cube_number=1, is_cube=True)  # Turn to the first cube
        # turnToTarget()
        GoToTarget(cube_number=1, is_cube=True)  # Go to the first cube
        print("Chaser is facing the target.")
    
        send_servo_request(80)
        send_beep_request(50)
        time.sleep(0.1)
        send_beep_request(50)
        # time.sleep(1)
        turnToTarget(target_pos = PositionConfig.BASE_POS_1, is_cube=False)  # Turn to the base position
        # turnToTarget(False, base_pos)
        GoToTarget(target_pos = PositionConfig.BASE_POS_1, is_cube=False)


        
    send_servo_request(30)
    send_beep_request(50)
    time.sleep(0.1)
    send_beep_request(50)
    time.sleep(0.1)
    send_beep_request(50)
    # print("c_pos: ", c_pos, "c_rot: ", c_rot, "c_rad: ", c_rad)
    # print("t_pos: ", t_pos, "t_rot: ", t_rot, "t_rad: ", t_rad)
    #print(car_positions)
    #plot_positions(car_positions, [[t_pos[0], t_pos[2]]])
    








# Handle connection-related errors specifically
except ConnectionResetError as e:
    print(f"Dear friend !!\nOptitrack connection failed:\nPlease check if the Optitrack system is on and streaming.\n\n\n{e}")

    exit()  # Exit the program

# Handle any other unexpected exceptions
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    # Handle other exceptions, possibly with logging or retry logic here


        

