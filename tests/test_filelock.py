"""Tests for FileLock class."""

import os
import time
import threading
import pytest
from agent_lock import FileLock, LockTimeoutError


def test_filelock_acquire_creates_lockfile(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target), timeout_seconds=5.0)
    assert fl.acquire()
    assert os.path.exists(str(target) + ".lock")
    fl.release()


def test_filelock_release_removes_lockfile(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    fl.acquire()
    fl.release()
    assert not os.path.exists(str(target) + ".lock")


def test_filelock_is_locked_true_when_held(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    fl.acquire()
    assert fl.is_locked
    fl.release()


def test_filelock_is_locked_false_when_free(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    assert not fl.is_locked


def test_filelock_context_manager(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    with fl:
        assert fl.is_locked
    assert not fl.is_locked


def test_filelock_context_manager_raises_on_timeout(tmp_path):
    target = tmp_path / "resource.db"
    fl1 = FileLock(str(target), timeout_seconds=5.0)
    fl2 = FileLock(str(target), timeout_seconds=0.05)
    fl1.acquire()

    with pytest.raises(LockTimeoutError):
        with fl2:
            pass

    fl1.release()


def test_filelock_timeout_returns_false(tmp_path):
    target = tmp_path / "resource.db"
    fl1 = FileLock(str(target), timeout_seconds=5.0)
    fl2 = FileLock(str(target), timeout_seconds=0.1)
    fl1.acquire()

    result = fl2.acquire(timeout=0.05)
    assert result is False
    fl1.release()


def test_filelock_stale_lock_detection(tmp_path):
    """A lockfile with a dead PID should be cleared and re-acquired."""
    target = tmp_path / "resource.db"
    lockpath = str(target) + ".lock"

    # Write a fake lockfile with a PID that doesn't exist
    dead_pid = 999999  # Very unlikely to be alive
    with open(lockpath, "w") as f:
        f.write(str(dead_pid))

    fl = FileLock(str(target), timeout_seconds=2.0)
    acquired = fl.acquire()
    assert acquired, "Should clear stale lock and acquire"
    fl.release()


def test_filelock_lockfile_contains_pid(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    fl.acquire()
    lockpath = str(target) + ".lock"
    with open(lockpath) as f:
        pid = int(f.read().strip())
    assert pid == os.getpid()
    fl.release()


def test_filelock_released_after_exception_in_context(tmp_path):
    target = tmp_path / "resource.db"
    fl = FileLock(str(target))
    with pytest.raises(RuntimeError):
        with fl:
            raise RuntimeError("boom")
    assert not fl.is_locked
    assert not os.path.exists(str(target) + ".lock")
