"""File-system-backed lock for cross-process coordination."""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional
from .lock import LockTimeoutError


class FileLock:
    """File-system lock using atomic file creation for cross-process safety.

    Uses PID-based lockfiles with stale lock detection.
    """

    def __init__(self, filepath: str, timeout_seconds: float = 10.0):
        self._lockpath = str(filepath) + ".lock"
        self._timeout_seconds = timeout_seconds
        self._held = False

    def _write_lockfile_atomic(self) -> bool:
        """Atomically create lockfile with current PID. Returns True if successful."""
        pid = os.getpid()
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(self._lockpath) or ".",
            prefix=".tmp_lock_"
        )
        try:
            os.write(tmp_fd, str(pid).encode())
            os.close(tmp_fd)
            # Atomic rename — only succeeds if dest doesn't exist on POSIX
            try:
                os.link(tmp_path, self._lockpath)
                return True
            except (FileExistsError, OSError):
                return False
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _read_lockfile_pid(self) -> Optional[int]:
        """Read PID from existing lockfile. Returns None if unreadable."""
        try:
            with open(self._lockpath, "r") as f:
                return int(f.read().strip())
        except (OSError, ValueError):
            return None

    def _is_pid_alive(self, pid: int) -> bool:
        """Check if a process with given PID is alive."""
        try:
            os.kill(pid, 0)  # Signal 0 — just checks existence
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True  # Process exists, we just can't signal it

    def _clear_stale_lock(self) -> bool:
        """Remove lockfile if the owning PID is dead. Returns True if cleared."""
        pid = self._read_lockfile_pid()
        if pid is None:
            return False
        if not self._is_pid_alive(pid):
            try:
                os.unlink(self._lockpath)
                return True
            except OSError:
                pass
        return False

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire the file lock. Polls until acquired or timeout."""
        timeout = timeout if timeout is not None else self._timeout_seconds
        deadline = time.monotonic() + timeout
        poll_interval = 0.02  # 20ms

        while True:
            # Clear stale locks first
            self._clear_stale_lock()

            if self._write_lockfile_atomic():
                self._held = True
                return True

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(poll_interval, remaining))

    def release(self) -> None:
        """Release the file lock by removing the lockfile."""
        if self._held:
            try:
                os.unlink(self._lockpath)
            except OSError:
                pass
            self._held = False

    @property
    def is_locked(self) -> bool:
        """True if a live process holds the lock (including this process)."""
        if not os.path.exists(self._lockpath):
            return False
        pid = self._read_lockfile_pid()
        if pid is None:
            return False
        return self._is_pid_alive(pid)

    def __enter__(self) -> "FileLock":
        if not self.acquire():
            raise LockTimeoutError(self._lockpath, self._timeout_seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def __repr__(self) -> str:
        return f"FileLock(path={self._lockpath!r}, held={self._held})"
