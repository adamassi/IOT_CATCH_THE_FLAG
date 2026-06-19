# utils/robot_audio.py

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from robotCommands import is_robot_muted, set_robot_muted
except Exception as e:
    print("Could not import robot audio commands:", e)

    def is_robot_muted():
        return False

    def set_robot_muted(muted: bool):
        pass


def is_muted():
    return is_robot_muted()


def toggle_mute():
    new_state = not is_robot_muted()
    set_robot_muted(new_state)
    return new_state