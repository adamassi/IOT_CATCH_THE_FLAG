# my_script.py
import time
import sys

def run_code():
    for i in range(10):
        print(f"Processing step {i + 1}...")
        sys.stdout.flush()  # Ensure the output is flushed to the terminal
        time.sleep(1)  # Simulating a time-consuming task

run_code()