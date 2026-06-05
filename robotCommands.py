import requests
import socket
from PARAMETERS import ESPConfig


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
def send_beep_request(duration=500):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/beep?duration="+str(duration))
        # print("BEEP request sent. Response:", response.text)
    except Exception as e:
        print("Error sending BEEP request:", e)
def send_start_beeping_request(on=300, off=300):
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/start_beeping?on="+str(on)+"&off="+str(off))
        # print("START BEEPING request sent. Response:", response.text)
    except Exception as e:
        print("Error sending START BEEPING request:", e)
def send_stop_beeping_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/stop_beeping")
        # print("STOP BEEPING request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STOP BEEPING request:", e)
def send_led_blue_request():
    try:
        response = requests.get(f"{ESPConfig.ESP_IP}/blue")
        # print("LED BLUE request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LED BLUE request:", e)

