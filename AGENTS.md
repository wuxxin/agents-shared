# AGENTS.md - Guidelines for Agents Working in This Repository

## Overview

- Shell and Python scripts for general agent management.

## Repository Structure

```
agents-shared/
├── assistants/           # assistant software control scripts and configuration documentation
├── scripts/              # other utility scripts and their documentation
|__ scratch/              # scratch space for agents work (e.g. cloned assistant source code for configuration research, or testing)
```

## Build/Lint/Test Commands


### Python Scripts
```bash
# Lint
ruff check scripts/*.py
# Format
ruff format scripts/*.py
# Type check
mypy scripts/*.py
# Run a single test
pytest tests/test_file.py::test_function -v
```

### Shell Scripts
```bash
# Lint
shellcheck scripts/*.sh
# Format
shfmt -w scripts/*.sh
```

## Code Style Guidelines

### Shell Scripts
- **Shebang**: `#!/usr/bin/env bash`
- **Indentation**: 4 spaces (no tabs)
- **Variables**: lowercase_with_underscores
- **Constants**: UPPERCASE
- **Error handling**: Use `set -euo pipefail` at script top
- **Quotes**: Always quote variables: `"$var"`
- **Command substitution**: Use `$(...)` not backticks

### Python Scripts
- **Shebang**: `#!/usr/bin/env python3`
- **Imports**: stdlib, third-party, local
- **Indentation**: 4 spaces
- **Types**: Use type hints where practical
- **Naming**: `snake_case` functions/variables, `PascalCase` classes
- **Docstrings**: Triple quotes `"""docstring"""`
- **Error handling**: Use specific exceptions, not bare `except:`

## Common Patterns

### Bubblewrap (bwrap)
- Use `--unshare-all` with `--share-net` for isolation
- Bind mount persistent home directories
- Set DISPLAY, XAUTHORITY, XDG_RUNTIME_DIR

### Agent Software Configuration 

- document all agent software default ports and isolation requirements in `README.md`

