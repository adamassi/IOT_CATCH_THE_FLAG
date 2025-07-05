# my_script.py
import time
import sys

def run_code():
    word = sys.argv[1]
    for i in range(3):
        print(f"map-RRT{i + 1}.png")
        sys.stdout.flush()  # Ensure the output is flushed to the terminal
        time.sleep(3)  # Simulating a time-consuming task

run_code()