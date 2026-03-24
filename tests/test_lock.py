"""Tests for Lock class."""

import threading
import time
import pytest
from agent_lock import Lock, LockTimeoutError


def test_lock_basic_acquire_release():
    lock = Lock("test")
    assert not lock.is_locked
    assert lock.acquire()
    assert lock.is_locked
    lock.release()
    assert not lock.is_locked


def test_lock_owner_is_current_thread():
    lock = Lock("test")
    lock.acquire()
    assert lock.owner == threading.current_thread().ident
    lock.release()
    assert lock.owner is None


def test_lock_reentrant_same_thread():
    lock = Lock("reentrant")
    assert lock.acquire()
    assert lock.acquire()  # Same thread — should succeed
    lock.release()
    assert lock.is_locked  # Still locked (count=1)
    lock.release()
    assert not lock.is_locked


def test_lock_timeout_returns_false():
    lock = Lock("timeout-test", timeout_seconds=0.1)
    results = []

    def holder():
        lock.acquire()
        time.sleep(0.5)
        lock.release()

    t = threading.Thread(target=holder)
    t.start()
    time.sleep(0.02)  # Let holder grab the lock

    result = lock.acquire(timeout=0.05)
    assert result is False
    t.join()


def test_lock_context_manager_success():
    lock = Lock("ctx")
    with lock:
        assert lock.is_locked
    assert not lock.is_locked


def test_lock_context_manager_raises_on_timeout():
    lock = Lock("ctx-timeout", timeout_seconds=0.05)
    results = []

    def holder():
        lock.acquire()
        time.sleep(0.3)
        lock.release()

    t = threading.Thread(target=holder)
    t.start()
    time.sleep(0.02)

    with pytest.raises(LockTimeoutError) as exc_info:
        with lock:
            pass

    assert "ctx-timeout" in str(exc_info.value)
    t.join()


def test_lock_release_by_wrong_thread_raises():
    lock = Lock("wrong-thread")
    errors = []

    def acquirer():
        lock.acquire()
        time.sleep(0.5)
        lock.release()

    t = threading.Thread(target=acquirer)
    t.start()
    time.sleep(0.05)

    with pytest.raises(RuntimeError):
        lock.release()  # Wrong thread

    t.join()


def test_lock_released_after_exception_in_context():
    lock = Lock("exception-test")
    with pytest.raises(ValueError):
        with lock:
            raise ValueError("oops")
    assert not lock.is_locked


def test_lock_concurrent_only_one_holder():
    lock = Lock("concurrent", timeout_seconds=5.0)
    holder_count = [0]
    max_holders = [0]
    errors = []
    n = 10

    def worker():
        if lock.acquire(timeout=5.0):
            holder_count[0] += 1
            if holder_count[0] > 1:
                errors.append("Multiple simultaneous holders!")
            max_holders[0] = max(max_holders[0], holder_count[0])
            time.sleep(0.01)
            holder_count[0] -= 1
            lock.release()

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, errors
    assert max_holders[0] == 1
