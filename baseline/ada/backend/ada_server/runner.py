"""Single-GPU subprocess lifecycle.

The runner spawns exactly one child process per run — ``scripts/run_experiment.py``
— records its PID and return code, and cancellation terminates only the
process belonging to that run.  Blocked configurations never reach this class
(the service refuses before a process exists).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional

SCRIPT_ENTRY = "scripts/run_experiment.py"


class Runner:
    def __init__(self, ada_root: str, python_executable: Optional[str] = None):
        self.ada_root = os.path.abspath(ada_root)
        self.python_executable = python_executable or sys.executable

    def script_path(self) -> str:
        return os.path.join(self.ada_root, SCRIPT_ENTRY)

    def spawn(self, config_path: str, train_dir: str, log_path: str) -> Dict[str, Any]:
        """Launch the experiment subprocess; returns pid + handles."""
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
        log_fh = open(log_path, "w", encoding="utf-8")
        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        proc = subprocess.Popen(
            [
                self.python_executable,
                self.script_path(),
                "--config-path",
                os.path.abspath(config_path),
                "--train-dir",
                os.path.abspath(train_dir),
            ],
            cwd=self.ada_root,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
        return {"pid": proc.pid, "proc": proc, "log_fh": log_fh, "started_at": time.time()}

    def poll(self, proc: subprocess.Popen) -> Optional[int]:
        return proc.poll()

    def cancel(self, proc: subprocess.Popen) -> int:
        """Terminate only this run's own process.

        Uses a best-effort graceful terminate, then kill; on Windows the
        process was spawned in its own process group so Ctrl-break targets
        exactly this child, never other runs' processes.
        """
        if proc.poll() is not None:
            return proc.returncode if proc.returncode is not None else 0
        try:
            if os.name == "nt":
                proc.send_signal(subprocess.signal.CTRL_BREAK_EVENT)
            else:
                proc.terminate()
        except Exception:
            pass
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
            try:
                proc.wait(timeout=5)
            except Exception:
                pass
        return proc.returncode if proc.returncode is not None else -1

    def cleanup(self, handle: Dict[str, Any]) -> None:
        fh = handle.get("log_fh")
        if fh and not fh.closed:
            try:
                fh.close()
            except Exception:
                pass
