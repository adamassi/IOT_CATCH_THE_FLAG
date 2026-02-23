from __future__ import annotations
import os
import sys
import time
import queue
import threading
import subprocess
from dataclasses import dataclass, field

# Optional: only used for Windows pause/resume
try:
    import psutil  # type: ignore
except Exception:
    psutil = None

# Optional hardware stop helpers (same ones used in your Streamlit app)
try:
    from stam import send_stop_request, send_stop_beeping_request  # type: ignore
except Exception:
    send_stop_request = None
    send_stop_beeping_request = None


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
    """
    Starts an external python script and streams stdout lines without blocking the pygame loop.
    """
    def __init__(self, script_path: str, workdir: str | None = None, max_lines: int = 600):
        self.script_path = script_path
        self.workdir = workdir
        self.max_lines = max_lines

        self.state = ProcessState()
        self._proc: subprocess.Popen[str] | None = None
        self._stdout_q: queue.Queue[str] = queue.Queue()
        self._reader_thread: threading.Thread | None = None

    def start(self, word: str) -> None:
        if self.state.running and not self.state.finished:
            return  # already running

        self.state = ProcessState(running=True, paused=False, finished=False, start_time=time.time())

        cmd = [sys.executable, self.script_path, word]

        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # merge stderr into stdout for a single live log
            text=True,
            bufsize=1,
            cwd=self.workdir or None,
        )

        def _read_stdout():
            assert self._proc is not None
            assert self._proc.stdout is not None
            try:
                for line in iter(self._proc.stdout.readline, ""):
                    self._stdout_q.put(line)
            finally:
                try:
                    self._proc.stdout.close()
                except Exception:
                    pass

        self._reader_thread = threading.Thread(target=_read_stdout, daemon=True)
        self._reader_thread.start()

    def poll(self) -> None:
        """
        Call every frame from pygame. Pulls new stdout lines and updates finished state.
        """
        if not self._proc:
            return

        # Drain queue
        while True:
            try:
                line = self._stdout_q.get_nowait()
            except queue.Empty:
                break

            self.state.stdout_lines.append(line.rstrip("\n"))
            # keep log bounded
            if len(self.state.stdout_lines) > self.max_lines:
                self.state.stdout_lines = self.state.stdout_lines[-self.max_lines :]

        rc = self._proc.poll()
        if rc is not None and not self.state.finished:
            self.state.finished = True
            self.state.running = False
            self.state.returncode = rc

    def elapsed_seconds(self) -> float:
        if not self.state.start_time:
            return 0.0
        return time.time() - self.state.start_time

    def stop(self) -> None:
        """
        Terminates the process and (optionally) stops robot actions (same as Streamlit version).
        """
        if not self._proc:
            return

        try:
            self._proc.terminate()
        except Exception as e:
            self.state.last_error = str(e)

        # Optional: hardware stop (mirrors your Streamlit stop behavior) :contentReference[oaicite:2]{index=2}
        try:
            if send_stop_request:
                send_stop_request()
            if send_stop_beeping_request:
                send_stop_beeping_request()
        except Exception:
            pass

        self.state.paused = False
        self.state.running = False
        self.state.finished = True

    def toggle_pause(self) -> None:
        """
        Attempts to pause/resume the subprocess.
        - POSIX: SIGSTOP/SIGCONT
        - Windows: requires psutil for suspend/resume
        """
        if not self._proc:
            return

        pid = self._proc.pid
        if pid is None:
            return

        if os.name == "posix":
            import signal
            try:
                if not self.state.paused:
                    os.kill(pid, signal.SIGSTOP)
                    self.state.paused = True
                else:
                    os.kill(pid, signal.SIGCONT)
                    self.state.paused = False
            except Exception as e:
                self.state.last_error = f"Pause/resume failed: {e}"
            return

        # Windows
        if psutil is None:
            self.state.last_error = "Pause/resume on Windows requires 'psutil' (pip install psutil)."
            return

        try:
            p = psutil.Process(pid)
            if not self.state.paused:
                p.suspend()
                self.state.paused = True
            else:
                p.resume()
                self.state.paused = False
        except Exception as e:
            self.state.last_error = f"Pause/resume failed: {e}"