import time
from robotCommands import *

def test_thread_control():
    print("Starting thread control test...")
    for i in range(5):
        print(f"Iteration {i+1}: Sending servo request")
        send_go_request()
        time.sleep(5)  # Simulate some delay between requests
        send_start_beeping_request()
        send_back_request()
        time.sleep(5)  # Simulate some delay between requests
        send_stop_beeping_request()

    print("Thread control test completed.")


test_thread_control()