<div align="center">
<img src="assets/hero.svg" width="100%"/>
</div>

# agent-lock

**Distributed locking for multi-agent shared resource access**

[![PyPI version](https://img.shields.io/pypi/v/agent-lock?color=purple&style=flat-square)](https://pypi.org/project/agent-lock/) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square)](https://python.org) [![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE) [![Tests](https://img.shields.io/badge/tests-passing-brightgreen?style=flat-square)](#)

---

## The Problem

Without distributed locks, concurrent agents race to modify shared state — double-spending tokens, corrupting queues, or triggering duplicate tool calls. Correctness under concurrency is not accidental.

## Installation

```bash
pip install agent-lock
```

## Quick Start

```python
from agent_lock import FileLock, LockTimeoutError, Lock

# Initialise
instance = FileLock(name="my_agent")

# Use
# see API reference below
print(result)
```

## API Reference

### `FileLock`

```python
class FileLock:
    """File-system lock using atomic file creation for cross-process safety.
    def __init__(self, filepath: str, timeout_seconds: float = 10.0):
    def _write_lockfile_atomic(self) -> bool:
        """Atomically create lockfile with current PID. Returns True if successful."""
    def _read_lockfile_pid(self) -> Optional[int]:
        """Read PID from existing lockfile. Returns None if unreadable."""
    def _is_pid_alive(self, pid: int) -> bool:
        """Check if a process with given PID is alive."""
```

### `LockTimeoutError`

```python
class LockTimeoutError(Exception):
    """Raised when a lock cannot be acquired within the timeout period."""
    def __init__(self, name: str, timeout: float):
```

### `Lock`

```python
class LockTimeoutError(Exception):
    """Raised when a lock cannot be acquired within the timeout period."""
    def __init__(self, name: str, timeout: float):
class Lock:
    def __init__(self, name: str, timeout_seconds: float = 10.0):
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire the lock. Returns False if timeout exceeded."""
    def release(self):
        """Release the lock."""
```


## How It Works

### Flow

```mermaid
flowchart LR
    A[User Code] -->|create| B[FileLock]
    B -->|configure| C[LockTimeoutError]
    C -->|execute| D{Success?}
    D -->|yes| E[Return Result]
    D -->|no| F[Error Handler]
    F --> G[Fallback / Retry]
    G --> C
```

### Sequence

```mermaid
sequenceDiagram
    participant App
    participant FileLock
    participant LockTimeoutError

    App->>+FileLock: initialise()
    FileLock->>+LockTimeoutError: configure()
    LockTimeoutError-->>-FileLock: ready
    App->>+FileLock: run(context)
    FileLock->>+LockTimeoutError: execute(context)
    LockTimeoutError-->>-FileLock: result
    FileLock-->>-App: WorkflowResult
```

## Philosophy

> *Ekāgratā* — single-pointed focus — is the lock that prevents distraction from entering the critical section.

---

*Part of the [arsenal](https://github.com/darshjme/arsenal) — production stack for LLM agents.*

*Built by [Darshankumar Joshi](https://github.com/darshjme), Gujarat, India.*
