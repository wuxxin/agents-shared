# AGENTS.md - Guidelines for Agents Working in This Repository

## Overview

- Shell and Python scripts for general agent management.

## Repository Structure

- `README.md`:

Overall Readme and Instructions on how to use the Agents and Scripts

- `assistants/`:

Houses lifecycle management control wrappers (`*-ctl`) and configuration documentation for running various agents (Hermes, LibreFang, Moltis, NanoBot, NanoClaw, PicoClaw, ZeroClaw) and core local services (Inference, Speech-to-Text, and Signal gateways).

- `scripts/`:

Helper utilities for caching/throughput benchmarking, token counting and token speed simulation.

- `research/`:

Documentation about the assistants git repository activity, llm adapter research and other research findings.

- `scratch/`:

Safe workspace directory for configuration testing, source code cloning, and developmental research.

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
# Format (requires -i 4 to enforce the 4-space indentation style)
shfmt -i 4 -w scripts/*.sh
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
- update documentation whenever any changes are made to scripts, `README.md`  for overall structure and `assistants/*-ctl.md`  for individual agent documentation, same for `scripts/`.
- always use `scratch/` for temporary files and other testings.
- always check configuration changes by verify with the source code in `scratch/*-sources`.
- always check with `[ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ]` if you are bwrapped yourself.
  - if bwrapped, do not use systemd to start/stop or otherwise introspect running systemd services.
  - if bwrapped, expect hat the real $HOME of the $USER eg. ~/.local is not available to you, you have a bwrapped ~/.local 

