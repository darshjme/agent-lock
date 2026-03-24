# Contributing to agent-lock

Thank you for your interest in contributing!

## Getting Started

```bash
git clone https://github.com/darshjme-codes/agent-lock
cd agent-lock
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Submit a pull request with a clear description

## Code Style

- Python 3.10+ type hints required
- Docstrings for all public classes and methods
- No external dependencies (stdlib only)
- Thread-safety is non-negotiable — test with `threading`

## Reporting Bugs

Open an issue with:
- Python version
- OS and architecture
- Minimal reproduction case
- Expected vs actual behavior
