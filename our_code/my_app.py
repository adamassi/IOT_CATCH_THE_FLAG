# import streamlit as st
# import subprocess

# # Title of the app
# st.title('Run Python Code with Streamlit')

# # Button to run the script
# if st.button('Run my Python script'):
#     # Use subprocess to run the Python file
#     result = subprocess.run(['python', 'our_code/my_script.py'], capture_output=True, text=True)
#     st.write('Script executed!')
#     # Display the output from the script
#     st.write(result.stdout)
#     st.write('done')
#     st.write(result)


# import streamlit as st
# import subprocess

# # Title of the app
# st.title('Real-time Python Script Output')

# # Placeholder for real-time output
# output_placeholder = st.empty()

# # Button to run the script
# if st.button('Run my Python script'):
#     # Run the script with subprocess.Popen for continuous output
#     process = subprocess.Popen(['python', 'our_code/my_script.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

#     # Continuously read the output and display it in real-time
#     for line in process.stdout:
#         output_placeholder.text(line.strip())  # Show each new line of output

#     # Check if there were any errors
#     stderr = process.stderr.read()
#     if stderr:
#         output_placeholder.text(f"Error: {stderr}")








# import streamlit as st
# import subprocess

# # Title of the app
# st.title('Real-time Python Script Output')

# # Placeholder for real-time output
# output_placeholder = st.empty()

# # Button to run the script
# if st.button('Run my Python script'):
#     # Run the script with subprocess.Popen for continuous output
#     process = subprocess.Popen(
#         ['python', 'our_code/my_script.py'],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         bufsize=1,  # Line-buffered output
#         universal_newlines=True
#     )

#     # Continuously read the output and display it in real-time
#     for line in process.stdout:
#         output_placeholder.text(line.strip())  # Show each new line of output

#     # Check if there were any errors
#     stderr = process.stderr.read()
#     if stderr:
#         output_placeholder.text(f"Error: {stderr}")



import streamlit as st
import subprocess
from PIL import Image

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
    st.session_state.clicked_submit = True
if "output_placeholder" not in st.session_state:
    st.session_state.output_placeholder = None
if "error_placeholder" not in st.session_state:
    st.session_state.error_placeholder = None

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

# Title
st.title('Simple Streamlit Example')

# Display current assembled word

st.write("Current assembled word:")
st.info(f'{st.session_state.word}')
image = Image.open("./map-RRT1.png")
# Buttons to assemble the word
left, middle, right = st.columns(3)
left.button("I", on_click=click_i, disabled=st.session_state.clicked_i, use_container_width=True)
middle.button("O", on_click=click_o, disabled=st.session_state.clicked_o, use_container_width=True)
right.button("T", on_click=click_t, disabled=st.session_state.clicked_t, use_container_width=True)

st.session_state.clicked_submit = not (st.session_state.clicked_i and st.session_state.clicked_o and st.session_state.clicked_t)
# Submit and Reset buttons
submit_col, reset_col = st.columns(2)
if submit_col.button("Submit", disabled=st.session_state.clicked_submit):
    if are_permutations(st.session_state.word):
        st.success(f'Assembling the word: {st.session_state.word}!')
        process = subprocess.Popen(
            ['python', 'our_code/my_script.py', st.session_state.word],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered output
            universal_newlines=True
        )
    
        for line in process.stdout:
            st.session_state.output_placeholder = line.strip() # Show each new line of output
            if st.session_state.output_placeholder:
                st.image(st.session_state.output_placeholder, caption="This is my picture")
        # Check if there were any errors
        stderr = process.stderr.read()
        if stderr:
            st.session_state.error_placeholder.text(f"Error: {stderr}")

    else:
        st.error("The robot can't assemble such a word.")

reset_col.button("Reset", on_click=reset_all)

# Optional: Give hint when nothing is submitted
if not st.session_state.word:
    st.info("Hello! Please enter your word by picking the letters.")
