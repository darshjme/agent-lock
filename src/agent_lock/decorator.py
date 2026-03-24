"""@locked decorator for automatic resource locking."""

import functools
from typing import Callable
from .registry import LockRegistry
from .lock import LockTimeoutError


def locked(registry: LockRegistry, resource: str, timeout: float = 10.0):
    """Decorator that acquires a named lock before calling the function.

    Releases the lock after the function returns, even on exception.
    Raises LockTimeoutError if the lock cannot be acquired.

    Usage:
        registry = LockRegistry()

        @locked(registry, "my_resource", timeout=5.0)
        def write_to_db(data):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            acquired = registry.acquire(resource, timeout=timeout)
            if not acquired:
                raise LockTimeoutError(resource, timeout)
            try:
                return func(*args, **kwargs)
            finally:
                registry.release(resource)
        return wrapper
    return decorator
