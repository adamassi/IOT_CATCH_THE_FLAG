import streamlit as st
import subprocess
import time
import threading
from PIL import Image
import os
from robotCommands import *
from A4_main_as_function import run_all_code

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
if "is_image" not in st.session_state:
    st.session_state.is_image = False
if "output_placeholder" not in st.session_state:
    st.session_state.output_placeholder = None
if "error_placeholder" not in st.session_state:
    st.session_state.error_placeholder = None
if "stop_event" not in st.session_state:
    st.session_state.stop_event = threading.Event()
if "process" not in st.session_state:
    st.session_state.process = None

# Function to check if the word is a permutation of "IOT"
def are_permutations(str2):
    return sorted('IOT') == sorted(str2)

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
    st.session_state.word = ""
    st.session_state.clicked_i = False
    st.session_state.clicked_o = False
    st.session_state.clicked_t = False
    st.session_state.clicked_submit = False



# Title
st.title('Simple Streamlit Example')


def run_script(output_dict, word):
    result = subprocess.run(["python", "our_code/4_main_for_web.py", word], capture_output=True, text=True)
    output_dict["returncode"] = result.returncode
    output_dict["stdout"] = result.stdout
    output_dict["stderr"] = result.stderr
    output_dict["finished"] = True
def run_script_as_function(output_dict, word):
    run_all_code()
    output_dict["finished"] = True

# stop everything
def stop_all():
    return

def submit_botton():
    if are_permutations(st.session_state.word):
        st.session_state.clicked_submit = True
        st.session_state.stop_event.clear()
        st.success(f'Assembling the word: {st.session_state.word}!')
        timer_placeholder = st.empty()
        image_placeholder = st.empty()
        st.session_state.is_image = True
        st.session_state.output_placeholder = st.empty()
        st.session_state.error_placeholder = st.empty()
         # Dictionary to share output state
        output = {"finished": False, "returncode": None, "stdout": "", "stderr": ""}

        # Start algorithm in a thread
        thread = threading.Thread(target=run_script_as_function, args=(output,st.session_state.word))
        thread.start()

        start_time = time.time()
        target_width = 400
        # Keep updating timer and image
        while not output["finished"]:
            elapsed = time.time() - start_time
            timer_placeholder.write(f"Time elapsed: {elapsed:.1f} seconds")
            # Reload and display the image safely
            if os.path.exists("map-RRTfor_web.png"):
                try:
                    if output["stderr"] != "":
                        st.session_state.error_placeholder.text(f"Error: {output['stderr']}")
                    image = Image.open("map-RRTfor_web.png")
                    image.load()  # Force load now, to catch incomplete files
                    width_percent = (target_width / float(image.width))
                    target_height = int(float(image.height) * width_percent)
                    resized_image = image.resize((target_width, target_height), Image.LANCZOS)
                    image_placeholder.image(resized_image, caption="Live Map Output")
                except Exception:
                    pass  # Silently ignore corrupted/incomplete image loads
        time.sleep(0.3)  # Update every 0.3 seconds
        elapsed = time.time() - start_time
        timer_placeholder.write(f"Finished in {elapsed:.1f} seconds")

        # Optionally show success/failure only
        if output["returncode"] == 0:
            st.success("Algorithm finished successfully!")
        else:
            st.error("There was an error running the algorithm.")

    else:
        st.error("The robot can't assemble such a word.")



st.write("Current assembled word:")
st.info(f'{st.session_state.word}')

# Buttons to assemble the word
left, middle, right = st.columns(3)
left.button("I", on_click=click_i, disabled=st.session_state.clicked_i, use_container_width=True)
middle.button("O", on_click=click_o, disabled=st.session_state.clicked_o, use_container_width=True)
right.button("T", on_click=click_t, disabled=st.session_state.clicked_t, use_container_width=True)

st.session_state.enable_submit = not (st.session_state.clicked_i and st.session_state.clicked_o and st.session_state.clicked_t)
# Submit and Reset buttons
submit_col, stop_col, reset_col = st.columns(3)
submit_col.button("Submit", disabled=st.session_state.enable_submit, on_click=submit_botton)

reset_col.button("Reset",  disabled=st.session_state.clicked_submit, on_click=reset_all)
if stop_col.button("Stop", on_click=stop_all): 
    is_Stopped = True

# Optional: Give hint when nothing is submitted
if not st.session_state.word:
    st.info("Hello! Please enter your word by picking the letters.")
