import requests
import socket
from PARAMETERS import ESPConfig
import os

AUDIO_STATE_DIR = os.path.dirname(os.path.abspath(__file__))

MUTE_FLAG_FILE = os.path.join(AUDIO_STATE_DIR, "robot_muted.flag")
BEEPING_FLAG_FILE = os.path.join(AUDIO_STATE_DIR, "robot_beeping_active.flag")


def is_robot_muted():
    return os.path.exists(MUTE_FLAG_FILE)


def is_beeping_active():
    return os.path.exists(BEEPING_FLAG_FILE)


def _set_beeping_active(active: bool):
    if active:
        with open(BEEPING_FLAG_FILE, "w") as f:
            f.write("active")
    else:
        if os.path.exists(BEEPING_FLAG_FILE):
            os.remove(BEEPING_FLAG_FILE)


def set_robot_muted(muted: bool):
    if muted:
        with open(MUTE_FLAG_FILE, "w") as f:
            f.write("muted")

        _send_stop_beeping_request_raw()

    else:
        if os.path.exists(MUTE_FLAG_FILE):
            os.remove(MUTE_FLAG_FILE)

        if is_beeping_active():
            _send_start_beeping_request_raw()

            

def send_servo_request(angle=10):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/servo?value="+str(angle))
        # print("SERVO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending SERVO request:", e)

def send_go_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/go")
        # print("GO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending GO request:", e)

def send_speed_request(speed=250):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/slider?value="+str(speed))
        # print("SPEED request sent. Response:", response.text)
    except Exception as e:
        print("Error sending SPEED request:", e)

def send_stop_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/stop")
        # print("STOP request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STOP request:", e)

def send_back_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/back")
        # print("BACK request sent. Response:", response.text)
    except Exception as e:
        print("Error sending BACK request:", e)

# left with i we use 
def send_lift_request(speed=45):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/left?value="+str(speed))
        # print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)

def send_right_request(speed=45):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/right?value="+str(speed))
        # print("RIGHT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending RIGHT request:", e)

def send_left_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/left")
        # print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)

def send_steer_request(left=250, right = 250):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/steer?left="+str(left)+"&right="+str(right))
        # print("STEER request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STEER request:", e)
def send_lights_color_request(color):
    try:
        red, green, blue = color
        requests.get(
            f"{ESPConfig.ESP_IP}/lights_color?red={red}&green={green}&blue={blue}"
        )
    except Exception as e:
        print("Error sending LIGHTS COLOR request:", e)
               
def send_lights_peach_request():
    """Turn the robot RGB LEDs to peach."""
    try:
        requests.get(f"{ESPConfig.ESP_IP}/lights_peach")
    except Exception as e:
        print("Error sending LIGHTS PEACH request:", e)

def _send_start_beeping_request_raw(on=300, off=300):
    try:
        requests.get(
            f"{ESPConfig.ESP_IP}/start_beeping?on=" + str(on) + "&off=" + str(off)
        )
    except Exception as e:
        print("Error sending START BEEPING request:", e)


def _send_stop_beeping_request_raw():
    try:
        requests.get(f"{ESPConfig.ESP_IP}/stop_beeping")
    except Exception as e:
        print("Error sending STOP BEEPING request:", e)


def send_beep_request(duration=500):
    if is_robot_muted():
        return

    try:
        requests.get(f"{ESPConfig.ESP_IP}/beep?duration=" + str(duration))
    except Exception as e:
        print("Error sending BEEP request:", e)


def send_start_beeping_request(on=300, off=300):
    _set_beeping_active(True)

    if is_robot_muted():
        return

    _send_start_beeping_request_raw(on, off)


def send_stop_beeping_request():
    _set_beeping_active(False)
    _send_stop_beeping_request_raw()