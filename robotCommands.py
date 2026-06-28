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
        response = requests.get(f"{ESPConfig.ESP_IP}/servo?value="+str(angle), timeout=2)
        # print("SERVO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending SERVO request:", e)
        raise e

def send_go_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/go")
        # print("GO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending GO request:", e)
        raise e

def send_speed_request(speed=250):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/slider?value="+str(speed), timeout=2)
        # print("SPEED request sent. Response:", response.text)
    except Exception as e:
        print("Error sending SPEED request:", e)
        raise e

def send_stop_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/stop", timeout=2)
        # print("STOP request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STOP request:", e)
        raise e

def send_back_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/back", timeout=2)
        # print("BACK request sent. Response:", response.text)
    except Exception as e:
        print("Error sending BACK request:", e)
        raise e

# left with i we use 
def send_lift_request(speed=45):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/left?value="+str(speed), timeout=2)
        # print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)
        raise e

def send_right_request(speed=45):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/right?value="+str(speed), timeout=2)
        # print("RIGHT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending RIGHT request:", e)
        raise e

def send_left_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/left", timeout=2)
        # print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)
        raise e

def send_steer_request(left=250, right = 250):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/steer?left="+str(left)+"&right="+str(right), timeout=2)
        # print("STEER request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STEER request:", e)
        raise e
    
def send_lights_color_request(color):
    try:
        red, green, blue = color
        requests.get(
            f"{ESPConfig.ESP_IP}/lights_color?red={red}&green={green}&blue={blue}", timeout=2
        )
    except Exception as e:
        print("Error sending LIGHTS COLOR request:", e)
        raise e

def send_lights_peach_request():
    """Turn the robot RGB LEDs to peach."""
    try:
        requests.get(f"{ESPConfig.ESP_IP}/lights_peach", timeout=2)
    except Exception as e:
        print("Error sending LIGHTS PEACH request:", e)
        raise e


def _send_start_beeping_request_raw(on=300, off=300):
    try:
        requests.get(
            f"{ESPConfig.ESP_IP}/start_beeping?on=" + str(on) + "&off=" + str(off),
            timeout=2
        )
    except Exception as e:
        print("Error sending START BEEPING request:", e)
        raise e


def _send_stop_beeping_request_raw():
    try:
        requests.get(f"{ESPConfig.ESP_IP}/stop_beeping", timeout=2)
    except Exception as e:
        print("Error sending STOP BEEPING request:", e)
        raise e


def send_beep_request(duration=500):
    if is_robot_muted():
        return

    try:
        requests.get(f"{ESPConfig.ESP_IP}/beep?duration=" + str(duration), timeout=2)
    except Exception as e:
        print("Error sending BEEP request:", e)
        raise e


def send_start_beeping_request(on=300, off=300):
    _set_beeping_active(True)

    if is_robot_muted():
        return

    _send_start_beeping_request_raw(on, off)


def send_stop_beeping_request():
    _set_beeping_active(False)
    _send_stop_beeping_request_raw()