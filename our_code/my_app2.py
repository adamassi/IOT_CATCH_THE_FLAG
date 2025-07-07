import streamlit as st
import subprocess
import time
import threading
from PIL import Image
import os
from stam import *
import select
import queue

def display_image(image_placeholder, image_path, target_width=400):
    """Display an image with a specified target width."""
    if os.path.exists(image_path):
        try:
            image = Image.open(image_path)
            image.load()  # Force load now, to catch incomplete files
            width_percent = (target_width / float(image.width))
            target_height = int(float(image.height) * width_percent)
            resized_image = image.resize((target_width, target_height), Image.LANCZOS)
            image_placeholder.image(resized_image, caption="Live Map Output")
        except Exception as e:
            pass
    return None

event = threading.Event()
# Initialize session state
if "word" not in st.session_state:
    st.session_state.word = ""
if "clicked_i" not in st.session_state:
    st.session_state.clicked_i = False
if "clicked_o" not in st.session_state:
    st.session_state.clicked_o = False
if "clicked_t" not in st.session_state:
    st.session_state.clicked_t = False
if "clicked_submit" not in st.session_state:
    st.session_state.clicked_submit = False
if "enable_submit" not in st.session_state:
    st.session_state.enable_submit = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None
# if "output_placeholder" not in st.session_state:
#     st.session_state.output_placeholder = None
# if "error_placeholder" not in st.session_state:
#     st.session_state.error_placeholder = None

# Callback functions for each letter
def click_i():
    st.session_state.word += 'I'
    st.session_state.clicked_i = True

def click_o():
    st.session_state.word += 'O'
    st.session_state.clicked_o = True

def click_t():
    st.session_state.word += 'T'
    st.session_state.clicked_t = True

# Reset everything
def reset_all():
    if not st.session_state.clicked_submit:
        st.session_state.word = ""
        st.session_state.clicked_i = False
        st.session_state.clicked_o = False
        st.session_state.clicked_t = False
        st.session_state.clicked_submit = False
        st.session_state.enable_submit = False
    else:
        print("You cannot reset while the algorithm is running. Please stop it first.")



# Title
st.title('Simple Streamlit Example')

# def run_script(output_dict, word):
#     # result = subprocess.run(["python", "./4_main_for_web.py", word], capture_output=True, text=True, timeout=40)
#     process = subprocess.Popen(["python", "./4_main_for_web.py", word], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
#     # time.sleep(10)
#     # process.terminate()  # Terminate the process after 10 seconds
#     # send_stop_request()
#     stdout_lines = []
#     stderr_lines = []

#     while process.poll() == None:
#         if event.is_set():
#             process.kill()
#             send_stop_request()
#             print("Process terminated by event")
#             output_dict["returncode"] = 0
#             output_dict["stdout"] = process.stdout
#             output_dict["stderr"] = process.stderr
#             output_dict["finished"] = True
#             break
#         stdout_lines += process.stdout.readlines()
#         stderr_lines += process.stderr.readlines()
#         output_dict["stdout"] = stdout_lines
        
        
#     print("Process finished")

#     output_dict["returncode"] = process.returncode
#     output_dict["stdout"] = stdout_lines
#     output_dict["stderr"] = stderr_lines
#     output_dict["finished"] = True
#     print("Output:")
#     # for line in output_dict["stdout"]:
#     #     print(line)
#     # print("Error:", output_dict["stderr"])
#     # print("Return code:", output_dict["returncode"])

def enqueue_output(pipe, q):
    for line in iter(pipe.readline, ''):
        q.put(line)
    pipe.close()

def run_script(output_dict, word):
    process = subprocess.Popen(
        ["python", "./4_main_for_web.py", word],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # Line buffered
    )

    stdout_q = queue.Queue()
    stderr_q = queue.Queue()

    t_out = threading.Thread(target=enqueue_output, args=(process.stdout, stdout_q))
    t_err = threading.Thread(target=enqueue_output, args=(process.stderr, stderr_q))
    t_out.daemon = True
    t_err.daemon = True
    t_out.start()
    t_err.start()

    stdout_lines = []
    stderr_lines = []

    try:
        while True:
            # Check for stop
            if event.is_set():
                process.terminate()
                send_stop_request()
                send_stop_beeping_request()
                output_dict["stdout"] = stdout_lines
                output_dict["stderr"] = ["Process terminated by user."]
                output_dict["returncode"] = -1
                output_dict["finished"] = True
                return

            # Get any new stdout lines
            while not stdout_q.empty():
                line = stdout_q.get()
                stdout_lines.append(line)
                output["stdout"].append(line)

            # Get any new stderr lines
            while not stderr_q.empty():
                line = stderr_q.get()
                stderr_lines.append(line)

            if process.poll() is not None:
                break

            time.sleep(0.1)

        # Final drain
        while not stdout_q.empty():
            stdout_lines.append(stdout_q.get())
        while not stderr_q.empty():
            stderr_lines.append(stderr_q.get())

    except Exception as e:
        output_dict["stdout"] = stdout_lines
        output_dict["stderr"] = [f"Exception: {str(e)}"]
        output_dict["returncode"] = -2
        output_dict["finished"] = True
        return

    output_dict["stdout"] = stdout_lines
    output_dict["stderr"] = stderr_lines
    output_dict["returncode"] = process.returncode
    output_dict["finished"] = True

# stop everything
def stop_all():
    event.set()  # Set the event to signal the thread to stop


st.write("Current assembled word:")
st.info(f'{st.session_state.word}')
output = {"finished": False, "returncode": None, "stdout": [], "stderr": []}

# Buttons to assemble the word
left, middle, right = st.columns(3)
left.button("I", on_click=click_i, disabled=st.session_state.clicked_i, use_container_width=True)
middle.button("O", on_click=click_o, disabled=st.session_state.clicked_o, use_container_width=True)
right.button("T", on_click=click_t, disabled=st.session_state.clicked_t, use_container_width=True)

st.session_state.enable_submit = not (st.session_state.clicked_i and st.session_state.clicked_o and st.session_state.clicked_t)
# Submit and Reset buttons
submit_col, stop_col, reset_col = st.columns(3)

timer_placeholder = st.empty()
image_placeholder = st.empty()
output_log = st.empty()

def submit_button():
    st.success(f'Assembling the word: {st.session_state.word}!')
    st.session_state.clicked_submit = True
    st.session_state.is_image = True
     # Dictionary to share output state
    size = len(output["stdout"])
    # Start algorithm in a thread
    thread = threading.Thread(target=run_script, args=(output,st.session_state.word))
    thread.start()
    
    st.session_state.start_time = time.time()
    live_output = ""  # Store visible output text
    # Keep updating timer and image
    while not output["finished"]:
        elapsed = time.time() - st.session_state.start_time
        timer_placeholder.write(f"Time elapsed: {elapsed:.1f} seconds")
        # Reload and display the image safely
        display_image(image_placeholder, "./map-RRTfor_web.png")
         # Print new lines in real-time
        while len(output["stdout"]) > size:
            new_line = output["stdout"][size]
            size += 1
            live_output += new_line
            output_log.text("Output:\n" + live_output)
        time.sleep(0.1)  # Update every 0.3 seconds
    elapsed = time.time() - st.session_state.start_time
    timer_placeholder.write(f"Finished in {elapsed:.1f} seconds")
    # print("Output:", output["stdout"])
    output_log.text("Output:\n" + live_output) 
    # Optionally show success/failure only
    if output["stderr"] == []:
        elapsed = time.time() - st.session_state.start_time
        st.success(f"Algorithm finished successfully! Finished in {elapsed:.1f} seconds!")
        image_placeholder2 = st.empty()
        display_image(image_placeholder2, "./map-RRTfor_web.png")
        st.code("Output:\n" + live_output, height=200)
        print(f"Algorithm finished successfully! Finished in {elapsed:.1f} seconds!")
    else:
        st.error("There was an error running the algorithm.")
        st.error(f"{output['stderr'][0]}")


if submit_col.button("Submit", disabled=st.session_state.enable_submit, on_click=submit_button):
    st.session_state.clicked_submit = True

    

reset_col.button("Reset", on_click=reset_all)

if stop_col.button("Stop", on_click=stop_all):
    if not st.session_state.clicked_submit:
        st.error("The algorithm is not running yet. Please submit your word first.")
    else:
        timer_placeholder = st.empty()
        elapsed = time.time() - st.session_state.start_time
        timer_placeholder.write(f"Finished in {elapsed:.1f} seconds")

# Optional: Give hint when nothing is submitted
if not st.session_state.word:
    st.info("Hello! Please enter your word by picking the letters.")
