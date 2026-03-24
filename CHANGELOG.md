# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-24

### Added
- `Lock` — reentrant in-process lock with configurable timeout
- `LockRegistry` — named lock manager with thread-safe creation
- `FileLock` — file-system-backed cross-process lock with PID tracking and stale lock detection
- `@locked` decorator for automatic resource locking
- `LockTimeoutError` exception for timeout failures
- Full context manager support (`with` statement) for `Lock` and `FileLock`
- Zero external dependencies (stdlib only: `threading`, `os`, `time`, `tempfile`)
- 22+ pytest tests covering concurrency, timeouts, and edge cases
