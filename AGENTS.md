# AGENTS.md - Guidelines for Agents Working in This Repository

## Overview

- Shell and Python scripts for general agent management.

## Repository Structure

- `README.md`:

Overall Readme and Instructions on how to use the Agents and Scripts

- `assistants/`:

Houses lifecycle management control wrappers (`*-ctl`) and configuration documentation for:
  - running various agents (Hermes, LibreFang, NanoBot, NanoClaw, PicoClaw, IronClaw, ZeroClaw)
  - running local inference services (chat,embedding,stt,tts,rerank,image) 
  - running a Signal gateway).

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
# Run local benchmark in mock/test mode (does not overwrite production reports)
python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --mock
# Run local benchmark with custom temporary paths (does not overwrite production reports)
python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --report scratch/test.md --data scratch/test.json
# Regenerate the Weekly Development Activity report (updates research/weekly-devel-activity.md)
python3 scripts/update-activity.py --write
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
- update documentation whenever any changes are made to scripts, `README.md`  for overall structure and `assistants/*-ctl.md`  for individual agent documentation, same for `scripts/`, if any assistant introduces new hardware or namespace isolation requirements, update the "## Sandboxing Architecture" profiles accordingly.
- always use `scratch/` for temporary files, git checkout of sourcecode for research and other testings.
- check configuration changes for packages by verifying it with the source code of the package checkedout and updated in `scratch/*-sources`.
- always check with `[ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ]` if you are bwrapped yourself.
  - if bwrapped, do not use systemd to start/stop or otherwise introspect running systemd services.
  - if bwrapped, expect hat the real $HOME of the $USER eg. ~/.local is not available to you, you have a bwrapped ~/.local 
- whenever you change the output or performance output of a `local-*` script, you must adapt `run-local-benchmark.py`. In addition, `run-local-benchmark.py` must be updated with any environment variable name or prefix changes (e.g., `LLM_` to `LCHAT_`, `EMBED_` to `LMBD_`) so it can spawn the exec server with the correct matching overrides.
- When running `run-local-benchmark.py` for testing or validation (e.g., in `--mock` mode), make sure you do not overwrite the production report/JSON files in `assistants/`. The benchmark script automatically redirects outputs to `scratch/local-benchmark-mock.md` and `scratch/local-benchmark-mock.json` when the `--mock` flag is set. If running other custom test scenarios, explicitly supply temporary paths via `--report scratch/test.md --data scratch/test.json`.
- Discover updates of and new configuration features and schemas, by inspecting configuration source code directories:
  - for ZeroClaw: check crates/zeroclaw-config/src/schema.rs and crates/zeroclaw-memory/
  - for IronClaw: check .env.example and FEATURE_PARITY.md
  - for Hermes: check hermes_constants.py, agent/context_compressor.py, and acp_adapter/
  - for NanoBot: check nanobot/config/schema.py and nanobot/agent/memory.py
  - FIXME: update hints for missing agents here
