"""In-process reentrant lock with timeout support."""

import threading
import time
from typing import Optional


class LockTimeoutError(Exception):
    """Raised when a lock cannot be acquired within the timeout period."""

    def __init__(self, name: str, timeout: float):
        self.name = name
        self.timeout = timeout
        super().__init__(f"Could not acquire lock '{name}' within {timeout}s timeout")


class Lock:
    """Reentrant in-process lock with timeout.

    Thread-safe, supports context manager protocol.
    Reentrant: same thread can acquire multiple times.
    """

    def __init__(self, name: str, timeout_seconds: float = 10.0):
        self.name = name
        self._timeout_seconds = timeout_seconds
        self._lock = threading.RLock()
        self._condition = threading.Condition(threading.Lock())
        self._owner_ident: Optional[int] = None
        self._acquire_count: int = 0
        self._state_lock = threading.Lock()

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire the lock. Returns False if timeout exceeded."""
        timeout = timeout if timeout is not None else self._timeout_seconds
        deadline = time.monotonic() + timeout

        current_ident = threading.current_thread().ident

        # Poll-based acquire with timeout
        poll_interval = 0.005  # 5ms
        while True:
            with self._state_lock:
                if self._owner_ident is None or self._owner_ident == current_ident:
                    self._owner_ident = current_ident
                    self._acquire_count += 1
                    return True

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(poll_interval, remaining))

    def release(self):
        """Release the lock."""
        current_ident = threading.current_thread().ident
        with self._state_lock:
            if self._owner_ident != current_ident:
                raise RuntimeError(
                    f"Lock '{self.name}' released by non-owner thread "
                    f"(owner={self._owner_ident}, caller={current_ident})"
                )
            self._acquire_count -= 1
            if self._acquire_count == 0:
                self._owner_ident = None

    @property
    def is_locked(self) -> bool:
        """True if the lock is currently held."""
        with self._state_lock:
            return self._owner_ident is not None

    @property
    def owner(self) -> Optional[int]:
        """Thread ident of current holder, or None."""
        with self._state_lock:
            return self._owner_ident

    def __enter__(self) -> "Lock":
        if not self.acquire():
            raise LockTimeoutError(self.name, self._timeout_seconds)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False

    def __repr__(self) -> str:
        return f"Lock(name={self.name!r}, locked={self.is_locked}, owner={self.owner})"
