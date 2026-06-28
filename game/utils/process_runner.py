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

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from robotCommands import *

try:
    import psutil  # type: ignore
except Exception:
    psutil = None


@dataclass
class ProcessState:
    running: bool = False
    paused: bool = False
    finished: bool = False
    returncode: int | None = None
    start_time: float | None = None
    last_error: str | None = None
    stdout_lines: list[str] = field(default_factory=list)


class ProcessRunner:
    def __init__(
        self,
        script_path: str,
        workdir: str | None = None,
        max_lines: int = 600,
        on_error=None,
    ):
        self.script_path = script_path
        self.workdir = workdir
        self.max_lines = max_lines
        self.on_error = on_error

        self.state = ProcessState()
        self._proc: subprocess.Popen[str] | None = None
        self._stdout_q: queue.Queue[str] = queue.Queue()
        self._reader_thread: threading.Thread | None = None

    def _notify_error(self, message: str):
        self.state.last_error = str(message)
        if self.on_error:
            self.on_error(str(message))

    def _safe_robot_command(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._notify_error(f"Robot command failed: {e}")
            return None

    def start(self, word: str) -> None:
        if self.state.running and not self.state.finished:
            return

        self.state = ProcessState(
            running=True,
            paused=False,
            finished=False,
            start_time=time.time(),
        )

        cmd = [sys.executable, "-u", self.script_path, word]

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=self.workdir or None,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        except Exception as e:
            self.state.running = False
            self.state.finished = True
            self._notify_error(f"Failed to start program: {e}")
            return

        def _read_stdout():
            assert self._proc is not None
            assert self._proc.stdout is not None

            try:
                for line in iter(self._proc.stdout.readline, ""):
                    self._stdout_q.put(line)
            except Exception as e:
                self._stdout_q.put(f"[stdout reader error] {e}")
                self._notify_error(f"Failed reading program output: {e}")
            finally:
                try:
                    self._proc.stdout.close()
                except Exception:
                    pass

        self._reader_thread = threading.Thread(
            target=_read_stdout,
            daemon=True,
        )
        self._reader_thread.start()

    def poll(self) -> None:
        if not self._proc:
            return

        while True:
            try:
                line = self._stdout_q.get_nowait()
            except queue.Empty:
                break

            clean_line = line.rstrip("\n")
            self.state.stdout_lines.append(clean_line)

            if len(self.state.stdout_lines) > self.max_lines:
                self.state.stdout_lines = self.state.stdout_lines[-self.max_lines:]

        rc = self._proc.poll()

        if rc is not None and not self.state.finished:
            self.state.finished = True
            self.state.running = False
            self.state.returncode = rc

            if rc != 0:
                self._notify_error(f"Program exited with error code {rc}")

    def elapsed_seconds(self) -> float:
        if not self.state.start_time:
            return 0.0

        return time.time() - self.state.start_time

    def stop(self) -> None:
        if not self._proc:
            return

        try:
            self._proc.terminate()
        except Exception as e:
            self._notify_error(f"Failed to terminate program: {e}")

        self._safe_robot_command(send_stop_request)
        self._safe_robot_command(send_stop_beeping_request)

        self.state.paused = False
        self.state.running = False
        self.state.finished = True

    def toggle_pause(self) -> None:
        if not self._proc or self.state.finished:
            return

        if not self.state.paused:
            try:
                if sys.platform == "win32":
                    if psutil is None:
                        self._notify_error(
                            "Pause requires psutil on Windows. Install it with: pip install psutil"
                        )
                        self._safe_robot_command(send_stop_request)
                        self._safe_robot_command(send_stop_beeping_request)
                        return

                    psutil.Process(self._proc.pid).suspend()
                else:
                    os.kill(self._proc.pid, signal.SIGSTOP)

                self._safe_robot_command(send_stop_request)
                self._safe_robot_command(send_stop_beeping_request)

                self.state.paused = True
                self.state.running = True
                self.state.finished = False

            except Exception as e:
                self._notify_error(f"Failed to pause program: {e}")
                self._safe_robot_command(send_stop_request)

        else:
            try:
                if sys.platform == "win32":
                    if psutil is None:
                        self._notify_error(
                            "Resume requires psutil on Windows. Install it with: pip install psutil"
                        )
                        return

                    psutil.Process(self._proc.pid).resume()
                else:
                    os.kill(self._proc.pid, signal.SIGCONT)

                self.state.paused = False
                self.state.running = True
                self.state.finished = False

            except Exception as e:
                self._notify_error(f"Failed to resume program: {e}")