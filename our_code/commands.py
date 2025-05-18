import requests

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



def send_motion_command(ip_address, port, left_direction, left_pwm, right_direction, right_pwm, angle):
    """
    Sends a motion command to the robot car via HTTP GET request.

    Parameters:
    - ip_address (str): The IP address of the robot car's HTTP server.
    - port (int): The port number of the robot car's HTTP server.
    - left_direction (str): The direction of the left motor ('F' for forward, 'B' for backward).
    - left_pwm (int): The PWM speed of the left motor (0-255).
    - right_direction (str): The direction of the right motor ('F' for forward, 'B' for backward).
    - right_pwm (int): The PWM speed of the right motor (0-255).
    - angle (int): The angle of the front steering wheels (60-120).

    Returns:
    - response (requests.Response): The response object from the HTTP GET request.
    """
    # Ensure PWM values are within valid range (0-255)
    left_pwm = max(0, min(255, left_pwm))
    right_pwm = max(0, min(255, right_pwm))

    # Ensure angle is within valid range (60-120)
    angle = max(60, min(120, angle))

    # Format PWM values and angle to 3 digits
    left_pwm_str = f"{left_pwm:03d}"
    right_pwm_str = f"{right_pwm:03d}"
    angle_str = f"{angle:03d}"

    # Construct the command string
    command = f"{left_direction}{left_pwm_str}{right_direction}{right_pwm_str}A{angle_str}A"

    # Construct the URL
    url = f"http://{ip_address}:{port}/{command}"
    print("sending request: ")
    # Send the GET request
    response = requests.get(url)
    print(response)
    print("request sent!")
    return response


def send_led_error_command(ip_address, port, led, state):
    url = None
    if state == 'low':
        url = f"http://{ip_address}:{port}/L{led}"
    if state == 'high':
        url = f"http://{ip_address}:{port}/H{led}"
        response = requests.get(url)
        print(response)
        print("request sent!")
        url = f"http://{ip_address}:{port}/L2"
        response = requests.get(url)
    # Send the GET request
    response = requests.get(url)

    return response
