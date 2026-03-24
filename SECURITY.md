# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes    |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, email: **darshjme@gmail.com** with subject `[agent-lock] Security Vulnerability`.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours and issue a fix within 7 days for confirmed vulnerabilities.

## Security Considerations

- `FileLock` uses atomic file creation (`os.link`) to prevent race conditions during lock acquisition
- PID-based stale lock detection uses `os.kill(pid, 0)` — no signals are sent
- Lockfiles are created in the same directory as the target file; ensure write permissions
- `Lock` is safe for multithreading but **not** for multiprocessing — use `FileLock` for cross-process locking
