import requests
import time

# Replace with the actual IP address of your ESP device
ESP_IP = "http://192.168.0.105"  # This is typically the default for ESP AP mode

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

# Example usage
# send_go_request()

# time.sleep(100)  # optionally wait before stopping
# send_stop_request()