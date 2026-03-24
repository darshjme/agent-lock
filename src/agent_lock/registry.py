"""Registry for managing named locks."""

import threading
from typing import Optional
from .lock import Lock


class LockRegistry:
    """Manages a collection of named Lock instances.

    Thread-safe. Creates locks on demand.
    """

    def __init__(self, default_timeout: float = 10.0):
        self._default_timeout = default_timeout
        self._locks: dict[str, Lock] = {}
        self._meta_lock = threading.Lock()

    def get(self, name: str) -> Lock:
        """Get or create a named lock."""
        with self._meta_lock:
            if name not in self._locks:
                self._locks[name] = Lock(name, self._default_timeout)
            return self._locks[name]

    def acquire(self, name: str, timeout: Optional[float] = None) -> bool:
        """Acquire a named lock. Returns False if timeout exceeded."""
        return self.get(name).acquire(timeout=timeout)

    def release(self, name: str) -> None:
        """Release a named lock."""
        self.get(name).release()

    def is_locked(self, name: str) -> bool:
        """Check if a named lock is currently held."""
        with self._meta_lock:
            if name not in self._locks:
                return False
        return self._locks[name].is_locked

    def locked_names(self) -> list[str]:
        """Return list of names of currently held locks."""
        with self._meta_lock:
            snapshot = list(self._locks.items())
        return [name for name, lock in snapshot if lock.is_locked]

    def __repr__(self) -> str:
        locked = self.locked_names()
        return f"LockRegistry(default_timeout={self._default_timeout}, locked={locked})"
