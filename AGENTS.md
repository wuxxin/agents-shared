# AGENTS.md

## Repository Structure

- `README.md`: Overall Readme and Instructions on how to use the Agents and Scripts
- `assistants/`: Houses lifecycle management control wrappers (`*-ctl`) and configuration documentation (`*-ctl.md`) for:
  - running various agents (hermes, librefang, nanobot, nanoclaw, picoclaw, ironclaw, zeroclaw)
  - running local inference services (chat,embedding,speech-to-text,text-to-speech,rerank,image) 
  - running a `Signal` Messenger Gateway.
- `scripts/`: Helper utilities for caching/throughput benchmarking, token counting and token speed simulation.
- `research/`: Documentation about the assistants git repository activity, llm adapter research and other research findings.
- `scratch/`: Safe workspace directory for configuration testing, source code cloning, and developmental research.

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
# Run local benchmark in mock mode (does not overwrite production reports)
python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --mock
# Run local benchmark with temporary paths output
python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --report scratch/test.md --data scratch/test.json
# if requested by the user: regenerate the Activity of the used Agents Software Sources from github, updates research/weekly-devel-activity.md:
python3 scripts/update-activity.py [--write]
```

### Shell Scripts
```bash
# Lint
shellcheck scripts/*.sh
# Format (requires -i 4 to enforce the 4-space indentation)
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


## Working with This Repository
- document all agent software default ports and isolation requirements in `README.md`
- update documentation whenever any changes are made to scripts, `README.md`  for overall structure and `assistants/*-ctl.md`  for individual agent/service documentation, same for `scripts/`, if any assistant introduces new hardware or namespace isolation requirements, update the "## Sandboxing Architecture" profiles accordingly.
- always use `scratch/` for temporary files, git checkout of sourcecode for research and other testings.
- check configuration changes for packages by verifying it with the source code of the package checkedout and updated in `scratch/*-sources`.
- always check with `[ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ]` if you are bwrapped yourself.
  - if bwrapped, do not use systemd to start/stop or otherwise introspect running systemd services.
  - if bwrapped, expect hat the real $HOME of the $USER eg. ~/.local is not available to you, you have a bwrapped ~/.local 
- whenever you change the output or performance output of a `local-*` script, you must adapt `run-local-benchmark.py`. In addition, it must be updated if any environment variable name or prefix changes (e.g., `LLM_` to `LCHAT_`, `EMBED_` to `LMBD_`) so it can spawn the exec server with the correct matching overrides.
- When running `run-local-benchmark.py` for testing or validation (e.g., in `--mock` mode), make sure you do not overwrite the production report/JSON files in `assistants/`. when used with the `--mock` flag, the script automatically redirects outputs to `scratch/local-benchmark-mock.*`. If running other custom test scenarios, explicitly supply temporary paths via `--report scratch/test.md --data scratch/test.json`.
- Discover updates of and new configuration features and schemas, by inspecting configuration source code directories:
  - ZeroClaw: check crates/zeroclaw-config/src/schema.rs and crates/zeroclaw-memory/
  - IronClaw: check .env.example and FEATURE_PARITY.md
  - Hermes: check hermes_constants.py, agent/context_compressor.py, and acp_adapter/
  - NanoBot: check nanobot/config/schema.py and nanobot/agent/memory.py
  - LibreFang: check librefang.toml.example, .env.example, and crates/librefang-types/src/config/types.rs
  - NanoClaw: check .env.example, src/config.ts, and src/env.ts
  - PicoClaw: check .env.example, config/config.example.json, and pkg/config/config.go
- **Debugging Control Scripts in Sandboxed (bwrapped) Environment**:
  If the agent environment is bwrapped (systemd socket does not exist), you cannot use systemd commands to start/stop/status/restart services. However, you can still test installation, uninstallation, and transient execution. To debug:
  1. Test configuration generation with: `./assistants/<name>-ctl install --no-start --new-config`
  2. Inspect the generated systemd environment file (e.g. `~/.config/systemd/user/<name>-gateway.env`) and verify path specifiers (%h, ~) expand or persist correctly.
  3. Clean up the sandbox with: `./assistants/<name>-ctl uninstall`
  4. Test command line routing and fallback transient execution using: `./assistants/<name>-ctl exec --help`
