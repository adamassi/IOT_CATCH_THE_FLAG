import requests
import time
import math


# Replace with the actual IP address of your ESP device
ESP_IP = "http://192.168.0.101"  # This is typically the default for ESP AP mode

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
def send_back_request():
    try:
        response = requests.get(f"{ESP_IP}/back")
        print("BACK request sent. Response:", response.text)
    except Exception as e:
        print("Error sending BACK request:", e)
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
def send_steer_request(left=250, right = 250):
    try:
        response = requests.get(f"{ESP_IP}/steer?left="+str(left)+"&right="+str(right))
        print("STEER request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STEER request:", e)
def send_beep_request(duration=500):
    try:
        response = requests.get(f"{ESP_IP}/beep?duration="+str(duration), timeout=0.1)
        print("BEEP request sent. Response:", response.text)
    except Exception as e:
        print("Error sending BEEP request:", e)
def send_start_beeping_request(on=300, off=300):
    try:
        response = requests.get(f"{ESP_IP}/start_beeping?on="+str(on)+"&off="+str(off))
        print("START BEEPING request sent. Response:", response.text)
    except Exception as e:
        print("Error sending START BEEPING request:", e)
def send_stop_beeping_request():
    try:
        response = requests.get(f"{ESP_IP}/stop_beeping")
        print("STOP BEEPING request sent. Response:", response.text)
    except Exception as e:
        print("Error sending STOP BEEPING request:", e)


# def angle_between_points(p1, p2):
    
#     return math.atan2(p2[2] - p1[2], p2[0] - p1[0])
    
    
# send_beep_request(50)
# time.sleep(0.1)  # Wait for the beep to finish
# send_beep_request(50)
# time.sleep(0.1)  # Wait for the beep to finish
# send_beep_request(500)

# Example usage
# send_go_request()
# send_left_request
# time.sleep(100)  # optionally wait before stopping
# send_stop_request()

# send_right_request(70)
# time.sleep(3)
# send_right_request(250)
# send_steer(250, 250)
# print("Steering command sent. left: 250, right: 250")
# time.sleep(3)
# send_steer(250, 100)
# print("Steering command sent. left: 250, right: 100")

# #send steer commands, try speeds from 0 to 250 with steps of 10
# for i in range(0, 250, 10):
#     send_steer(250, i)
#     time.sleep(0.1)  # small delay to observe the change in steering
#     print(f"Steering command sent. left: 250, right: {i}")
# # send steer commands, try speeds from 0 to 250 with steps of 1
# for i in range(0, 250, 10):
#     send_steer(i, 250)
#     time.sleep(0.1)  # small delay to observe the change in steering
#     print(f"Steering command sent. left: {i}, right: 250")

# send_stop_request()

send_start_beeping_request(300, 300)
time.sleep(5)  # Beep for 5 seconds
send_stop_beeping_request()