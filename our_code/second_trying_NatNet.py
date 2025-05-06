import time
import math
import numpy as np
from natnet_client import NatNetClient
import conversion  # Assuming this is your module
import socket

CHASER_ID = 600
TARGET_ID = 601
ANGLE_TOLERANCE = 0.05  # Radians

streaming_client = NatNetClient(
    server_ip_address="132.68.35.255",  # IP address of the OptiTrack server
    local_ip_address=socket.gethostbyname(socket.gethostname()),  # Local IP address
    use_multicast=False  # Use unicast instead of multicast for communication
)
rigid_bodies = {}

def handle_frame(ms, name):
    location_yup = np.array(ms.pos)
    quaternion_yup = np.array(ms.rot)
    location_zup, euler_angles_zup = conversion.convert_yup_to_zup(location_yup, quaternion_yup)
    rad = round(math.radians(euler_angles_zup[2]), 2)
    return conversion.only2(ms.pos), euler_angles_zup, rad

def data_handler(rb_data):
    if rb_data.id_num in [CHASER_ID, TARGET_ID]:
        rigid_bodies[rb_data.id_num] = rb_data

def angle_between_points(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle = math.atan2(dy, dx)
    return round(angle, 2)

def wait_for_both_bodies(timeout=5):
    print("Waiting for CHASER and TARGET data...")
    start = time.time()
    while time.time() - start < timeout:
        if CHASER_ID in rigid_bodies and TARGET_ID in rigid_bodies:
            return True
        time.sleep(0.01)
    return False

def main():
    streaming_client.rigid_body_listener = data_handler

    with streaming_client:
        if not wait_for_both_bodies():
            print("Failed to receive both bodies in time.")
            return

    # Stop receiving
    chaser_pos, _, chaser_rad = handle_frame(rigid_bodies[CHASER_ID], "CHASER")
    target_pos, _, _ = handle_frame(rigid_bodies[TARGET_ID], "TARGET")

    desired_angle = angle_between_points(chaser_pos, target_pos)
    print(f"Calculated desired angle (rad): {desired_angle}")

    # Start receiving again
    def tracking_loop(rb_data):
        if rb_data.id_num == CHASER_ID:
            pos, _, current_angle = handle_frame(rb_data, "CHASER")
            print(f"Current angle: {current_angle}")
            if abs(current_angle - desired_angle) <= ANGLE_TOLERANCE:
                print("🎯 Angle was reached.")
                streaming_client.on_rigid_body_received_event.handlers.clear()

    streaming_client.on_rigid_body_received_event.handlers.clear()
    streaming_client.rigid_body_listener = tracking_loop

    with streaming_client:
        while streaming_client.on_rigid_body_received_event.handlers:
            time.sleep(0.05)

if __name__ == "__main__":
    main()
