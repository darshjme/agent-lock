"""agent-lock: Distributed locking for shared resource access."""

from .lock import Lock, LockTimeoutError
from .registry import LockRegistry
from .filelock import FileLock
from .decorator import locked

__all__ = ["Lock", "LockTimeoutError", "LockRegistry", "FileLock", "locked"]
__version__ = "1.0.0"
