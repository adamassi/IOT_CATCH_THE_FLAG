import requests
import time
import math


# Replace with the actual IP address of your ESP device
ESP_IP = "http://192.168.0.102"  # This is typically the default for ESP AP mode

def send_servo_request(angle=10):
    try:
        response = requests.get(f"{ESP_IP}/servo?value="+str(angle))
        print("SERVO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending SERVO request:", e)
def send_go_request():
    try:
        response = requests.get(f"{ESP_IP}/go")
        print("GO request sent. Response:", response.text)
    except Exception as e:
        print("Error sending GO request:", e)

def send_stop_request():
    try:
        response = requests.get(f"{ESP_IP}/stop")
        print("STOP request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STOP request:", e)
def send_lift_request(speed=45):
    try:
        response = requests.get(f"{ESP_IP}/left?value="+str(speed))
        print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)
def send_right_request(speed=45):
    try:
        response = requests.get(f"{ESP_IP}/right?value="+str(speed))
        print("RIGHT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending RIGHT request:", e)
def send_left_request():
    try:
        response = requests.get(f"{ESP_IP}/left")
        print("LEFT request sent. Response:", response.text)
    except Exception as e:
        print("Error sending LEFT request:", e)
def angle_between_points(p1, p2):
    
    return math.atan2(p2[2] - p1[2], p2[0] - p1[0])
    

# Example usage
# send_go_request()
# send_left_request
# time.sleep(100)  # optionally wait before stopping
# send_stop_request()

# send_right_request(70)
# time.sleep(3)
# send_right_request(250)
