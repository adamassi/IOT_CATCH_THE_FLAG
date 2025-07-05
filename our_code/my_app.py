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

def are_permutations(str2):
    return sorted('iot') == sorted(str2)

# Title of the app
st.title('Simple Streamlit Example')

# Ask for the user's name
# word = st.text_input('Enter a word to assemble:')
word = ""
st.write(f'The assembled word is: {word}')
if st.button('I'):
    word += 'i'
if st.button('O'):
    word += 'o' 
if st.button('T'):  
    word += 't'
# Display a greeting if the user has entered their name
if word:
    if are_permutations(word):
        st.write(f'Hello, {word}! Welcome to Streamlit!')
    else:
        st.write("The robot can't assemble such a word.")
else:
    st.write('Hello! Please enter your name.')