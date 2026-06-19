from __future__ import annotations

import os
import sys
import signal
import time
import queue
import threading
import subprocess
from pathlib import Path
from dataclasses import dataclass, field


# ------------------------------------------------------------
# Fix import path
# ------------------------------------------------------------
# This file is probably inside a sub-folder, while robotCommands.py
# is located in the project root.
#
# Path(__file__).resolve() gives the full path of this file.
# parents[2] goes two folders up to reach the project root.
ROOT_DIR = Path(__file__).resolve().parents[2]

# Add project root to Python import path if it is not already there.
# This allows us to import robotCommands.py.
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# Import robot command functions:
# send_stop_request(), send_go_request(), send_servo_request(), etc.
from robotCommands import *


# ------------------------------------------------------------
# Optional Windows support
# ------------------------------------------------------------
# On Linux/macOS we can pause/resume a process using signals:
# SIGSTOP and SIGCONT.
#
# On Windows, Python does not support SIGSTOP/SIGCONT in the same way,
# so we use psutil if it is installed.
try:
    import psutil  # type: ignore
except Exception:
    psutil = None


@dataclass
class ProcessState:
    """
    Stores the current state of the external process.

    This object is useful for the GUI because pygame can read it
    every frame and update buttons/status/logs accordingly.
    """

    # True while the subprocess is actively running
    running: bool = False

    # True if the process is currently paused
    paused: bool = False

    # True after the process finished or was stopped
    finished: bool = False

    # Process exit code.
    # None means the process has not finished yet.
    returncode: int | None = None

    # Time when the process started.
    # Used to calculate elapsed running time.
    start_time: float | None = None

    # Stores the last error message, if something failed
    last_error: str | None = None

    # Stores recent stdout/stderr lines from the subprocess
    stdout_lines: list[str] = field(default_factory=list)


class ProcessRunner:
    """
    Starts and manages an external Python script.

    Main purpose:
    - Run the robot logic script in the background.
    - Keep pygame responsive.
    - Read stdout/stderr live.
    - Support start, stop, pause, and resume.
    """

    def __init__(
        self,
        script_path: str,
        workdir: str | None = None,
        max_lines: int = 600
    ):
        """
        Initialize the process runner.

        Args:
            script_path:
                Path to the Python script we want to run.

            workdir:
                Optional working directory for the subprocess.
                If None, it uses the current working directory.

            max_lines:
                Maximum number of log lines to keep in memory.
                This prevents the GUI from storing unlimited logs.
        """

        self.script_path = script_path
        self.workdir = workdir
        self.max_lines = max_lines

        # Public state object used by the GUI
        self.state = ProcessState()

        # The actual subprocess object.
        # It is None before start() is called.
        self._proc: subprocess.Popen[str] | None = None

        # Queue used to safely pass stdout lines from the reader thread
        # to the pygame/main thread.
        self._stdout_q: queue.Queue[str] = queue.Queue()

        # Background thread that reads stdout from the subprocess.
        self._reader_thread: threading.Thread | None = None

    def start(self, word: str) -> None:
        """
        Start the external Python script.

        Args:
            word:
                The word passed to the script as a command-line argument.

        Example command:
            python main.py OIT
        """

        # If a process is already running, do not start another one.
        if self.state.running and not self.state.finished:
            return

        # Reset state before starting
        self.state = ProcessState(
            running=True,
            paused=False,
            finished=False,
            start_time=time.time()
        )

        # Build the command:
        # sys.executable means use the same Python interpreter
        # that is currently running this GUI.
        cmd = [sys.executable, self.script_path, word]

        # Start subprocess.
        #
        # stdout=subprocess.PIPE:
        #   Allows us to read the output.
        #
        # stderr=subprocess.STDOUT:
        #   Merges errors into stdout, so we only read from one stream.
        #
        # text=True:
        #   Output is read as strings instead of bytes.
        #
        # bufsize=1:
        #   Line-buffered output, useful for live logs.
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=self.workdir or None,
        )

        def _read_stdout():
            """
            Runs in a background thread.

            Reads output lines from the subprocess and pushes them into a queue.
            We use a separate thread because reading stdout directly could block
            the pygame loop.
            """

            assert self._proc is not None
            assert self._proc.stdout is not None

            try:
                # Read lines until the process ends and stdout closes.
                for line in iter(self._proc.stdout.readline, ""):
                    self._stdout_q.put(line)
            finally:
                # Close stdout safely when done.
                try:
                    self._proc.stdout.close()
                except Exception:
                    pass

        # Start the stdout reader thread.
        # daemon=True means it will not prevent the program from exiting.
        self._reader_thread = threading.Thread(
            target=_read_stdout,
            daemon=True
        )
        self._reader_thread.start()

    def poll(self) -> None:
        """
        Update process state.

        This should be called every frame from the pygame loop.

        Responsibilities:
        - Pull new stdout lines from the queue.
        - Store them in state.stdout_lines.
        - Check whether the subprocess finished.
        """

        # No process started yet
        if not self._proc:
            return

        # Drain all available stdout lines from the queue.
        # get_nowait() prevents blocking the pygame loop.
        while True:
            try:
                line = self._stdout_q.get_nowait()
            except queue.Empty:
                break

            # Remove newline at the end before storing
            self.state.stdout_lines.append(line.rstrip("\n"))

            # Keep only the last max_lines lines.
            # This avoids memory growing forever.
            if len(self.state.stdout_lines) > self.max_lines:
                self.state.stdout_lines = self.state.stdout_lines[-self.max_lines:]

        # Check if the process has finished.
        # poll() returns:
        # - None if still running
        # - return code if finished
        rc = self._proc.poll()

        if rc is not None and not self.state.finished:
            self.state.finished = True
            self.state.running = False
            self.state.returncode = rc

    def elapsed_seconds(self) -> float:
        """
        Return how many seconds passed since the process started.
        """

        if not self.state.start_time:
            return 0.0

        return time.time() - self.state.start_time

    def stop(self) -> None:
        """
        Stop the subprocess and stop the robot.

        This does two things:
        1. Terminates the external Python script.
        2. Sends a stop command to the robot, so it does not keep moving.
        """

        if not self._proc:
            return

        try:
            # Ask the subprocess to terminate.
            # This is a graceful stop, not a force kill.
            self._proc.terminate()
        except Exception as e:
            self.state.last_error = str(e)

        # Important safety command:
        # Even if the script stops, the robot may still be moving,
        # so we explicitly send a stop request.
        send_stop_request()

        # Update internal state
        self.state.paused = False
        self.state.running = False
        self.state.finished = True

    def toggle_pause(self) -> None:
        """
        Pause or resume the subprocess.

        Behavior:
        - If currently running, pause it.
        - If currently paused, resume it.

        """
        # Nothing to pause if no process exists or it already finished
        if not self._proc or self.state.finished:
            return

        if not self.state.paused:
            # --- Pause ---
            try:
                if sys.platform == "win32":
                    if psutil is None:
                        self.state.last_error = (
                            "Pause requires psutil on Windows. "
                            "Install it with: pip install psutil"
                        )
                        send_stop_request()
                        return
                    psutil.Process(self._proc.pid).suspend()
                else:
                    os.kill(self._proc.pid, signal.SIGSTOP)

                # Stop the robot physically now that the script is frozen
                send_stop_request()

                self.state.paused = True
                self.state.running = True
                self.state.finished = False

            except Exception as e:
                self.state.last_error = str(e)
                # Safety fallback: stop the robot even if pause failed
                try:
                    send_stop_request()
                except Exception:
                    pass

        else:
            # --- Resume ---
            try:
                if sys.platform == "win32":
                    if psutil is None:
                        self.state.last_error = (
                            "Resume requires psutil on Windows. "
                            "Install it with: pip install psutil"
                        )
                        return
                    psutil.Process(self._proc.pid).resume()
                else:
                    os.kill(self._proc.pid, signal.SIGCONT)

                self.state.paused = False
                self.state.running = True
                self.state.finished = False

            except Exception as e:
                self.state.last_error = str(e)