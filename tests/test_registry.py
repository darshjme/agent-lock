"""Tests for LockRegistry class."""

import threading
import time
import pytest
from agent_lock import LockRegistry, LockTimeoutError


def test_registry_get_creates_lock():
    reg = LockRegistry()
    lock = reg.get("resource-a")
    assert lock is not None
    assert lock.name == "resource-a"


def test_registry_get_returns_same_instance():
    reg = LockRegistry()
    lock1 = reg.get("x")
    lock2 = reg.get("x")
    assert lock1 is lock2


def test_registry_acquire_and_release():
    reg = LockRegistry()
    assert reg.acquire("db-row")
    assert reg.is_locked("db-row")
    reg.release("db-row")
    assert not reg.is_locked("db-row")


def test_registry_is_locked_false_for_unknown():
    reg = LockRegistry()
    assert not reg.is_locked("never-used")


def test_registry_locked_names_empty():
    reg = LockRegistry()
    assert reg.locked_names() == []


def test_registry_locked_names_populated():
    reg = LockRegistry()
    reg.acquire("alpha")
    reg.acquire("beta")
    names = reg.locked_names()
    assert "alpha" in names
    assert "beta" in names
    reg.release("alpha")
    reg.release("beta")


def test_registry_locked_names_updates_on_release():
    reg = LockRegistry()
    reg.acquire("gamma")
    assert "gamma" in reg.locked_names()
    reg.release("gamma")
    assert "gamma" not in reg.locked_names()


def test_registry_acquire_timeout():
    reg = LockRegistry(default_timeout=0.1)
    results = []

    def holder():
        reg.acquire("shared")
        time.sleep(0.3)
        reg.release("shared")

    t = threading.Thread(target=holder)
    t.start()
    time.sleep(0.02)

    result = reg.acquire("shared", timeout=0.05)
    assert result is False
    t.join()


def test_registry_default_timeout_used():
    reg = LockRegistry(default_timeout=0.05)
    results = []

    def holder():
        reg.acquire("res")
        time.sleep(0.3)
        reg.release("res")

    t = threading.Thread(target=holder)
    t.start()
    time.sleep(0.01)

    result = reg.acquire("res")
    assert result is False
    t.join()
