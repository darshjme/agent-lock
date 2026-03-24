"""Tests for @locked decorator."""

import time
import threading
import pytest
from agent_lock import LockRegistry, LockTimeoutError, locked


def test_locked_decorator_basic():
    reg = LockRegistry()
    results = []

    @locked(reg, "resource")
    def write(val):
        results.append(val)

    write("hello")
    assert results == ["hello"]


def test_locked_decorator_releases_after_call():
    reg = LockRegistry()

    @locked(reg, "res")
    def do_work():
        pass

    do_work()
    assert not reg.is_locked("res")


def test_locked_decorator_releases_after_exception():
    reg = LockRegistry()

    @locked(reg, "res")
    def failing():
        raise ValueError("fail")

    with pytest.raises(ValueError):
        failing()

    assert not reg.is_locked("res")


def test_locked_decorator_raises_on_timeout():
    reg = LockRegistry()
    holding = threading.Event()
    released = threading.Event()

    @locked(reg, "shared", timeout=0.05)
    def quick_work():
        pass

    def holder():
        # Acquire directly inside this thread so main thread cannot re-enter
        reg.acquire("shared", timeout=5.0)
        holding.set()
        released.wait(timeout=2.0)
        reg.release("shared")

    t = threading.Thread(target=holder)
    t.start()
    holding.wait(timeout=2.0)  # Wait until lock is held by the other thread

    with pytest.raises(LockTimeoutError):
        quick_work()

    released.set()
    t.join()


def test_locked_decorator_preserves_function_name():
    reg = LockRegistry()

    @locked(reg, "res")
    def my_function():
        """Docstring."""
        pass

    assert my_function.__name__ == "my_function"
    assert my_function.__doc__ == "Docstring."


def test_locked_decorator_concurrent_serialization():
    reg = LockRegistry()
    counter = [0]
    errors = []

    @locked(reg, "counter-res", timeout=5.0)
    def increment():
        val = counter[0]
        time.sleep(0.002)
        new_val = val + 1
        if counter[0] != val:
            errors.append("Race condition!")
        counter[0] = new_val

    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert counter[0] == 10
