## CAPTURE THE FLAG Project by :  Firas Hilu, Adam Assi, Jimmy Bittar
  Type It, Robot Builds It!
  The project is a robot that receives a word from the user, detects relevant letter cubes, and places them in the correct order in a designated area.
## Details about the project
   Main Features:
  - Real-time 3D object tracking via OptiTrack
  - Autonomous path planning using RRT* for obstacle avoidance
  - Full spelling pipeline: input, detection, pickup, transport, and placement
  This project demonstrates a flexible robotic framework for real-time
  object handling using motion capture and path planning.

## Hardware used:
  - ESP32 CH9102
  - Car platform PCB
  - L293D driver
  - 4 DC motors
  - Active Buzzer
  - Micro servo
  - 9V / 12V battery
  - LM2596 DC-DC Buck Converter Module
  - Optitrack markers
  * note: in the platform we used, the ENA and ENB of the driver were connected together, so in order to be able to control the speed of each side separately, we didnt use libraries for controlling the speed, but we wrote the code of the ESP for controlling the motors using PWM on th IN1, IN2, IN3, IN4.
    
## Folder description :
* ESP32: source code for the esp
* path_algorithms: files used in planning the algorithm
* Documentation: wiring diagram + poster + 3d printed parts
* Unit Tests: tests for individual hardware components
* PARAMETERS.py: contains the parameters and settings that can be modified in the code - hardcoded parameters.

## ESP32 SDK version used in this project: 
"esp32" SDK version 2.0.17 by Espressif Systems.

## Arduino/ESP32 libraries used in this project:
* WiFi - version 2.0.17 (from esp32 core by Espressif Systems)
* AsyncTCP - version 3.3.2
* ESPAsyncWebServer - version 3.6.0
* ESP32Servo - version 3.0.6

## Connection diagram:
<img width="583" alt="diagram" src="https://github.com/user-attachments/assets/9f422e02-cc05-414c-bb46-fe26ac5644c6" />

## Project Poster:
![Capture_The_Falg_poster](https://github.com/user-attachments/assets/c1fde1a4-9627-4bcd-9c4d-18be69c3ab9f)





This project is part of ICST - The Interdisciplinary Center for Smart Technologies, Taub Faculty of Computer Science, Technion
https://icst.cs.technion.ac.il/

