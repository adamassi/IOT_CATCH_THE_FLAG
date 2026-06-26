from robotCommands import *
from PARAMETERS import *

import time

# send_lights_peach_request()

# send_lights_color_request(ColorBank.PEACH)
send_lights_color_request(ColorBank.OFF)
start_time = time.time()
duration=5
while time.time() - start_time < duration:
        for color in [ColorBank.RED, ColorBank.GREEN, ColorBank.BLUE]:
            send_lights_color_request(color)
            time.sleep(0.15)
send_lights_color_request(ColorBank.OFF)