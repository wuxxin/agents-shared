# AGENTS.md

## Repository Structure

- `README.md` — Agent/script instructions, default ports, and isolation requirements.
- `assistants/` — Lifecycle control scripts (`*-ctl`) and documentation (`*-ctl.md`) for:
  - Agents: Hermes, LibreFang, NanoBot, NanoClaw, PicoClaw, IronClaw, ZeroClaw
  - Local inference services (chat, embedding, STT, TTS, rerank, image)
  - Signal Messenger Gateway
- `sandbox-templates/` — Config templates for `scripts/sandbox-ctl install --new-config-from <env-path>`.
- `scripts/` — Benchmarking (caching/throughput), token counting, and speed simulation tools.
- `research/` — Development activity reports, LLM adapter research, and notes.
- `scratch/` — Safe workspace for temp files, source checkouts (`scratch/*-sources`), and testing.

## Code Style & Commands

- **Style:** dont use long visual lines for comment sections, eg. "# -----------"

### Shell Scripts (`.sh`)

- **Style:** `#!/usr/bin/env bash`, 4-space indent, `set -euo pipefail`, quote `"$var"`, use `$(...)`, `lowercase_vars`, `UPPERCASE_CONSTANTS`.
- **Lint & Format:**
  ```bash
  shellcheck scripts/*.sh && shfmt -i 4 -w scripts/*.sh
  ```

### Python Scripts (`.py`)
- **Style:** `#!/usr/bin/env python3`, 4-space indent, type hints, `snake_case` (functions/vars), `PascalCase` (classes), triple-quote docstrings, explicit exception handling.
- **Lint, Test & Utility Commands:**
  ```bash
  ruff check scripts/*.py scripts/test/*.py
  ruff format scripts/*.py scripts/test/*.py
  mypy scripts/*.py scripts/test/*.py
  pytest tests/test_file.py::test_function -v

  # Benchmarks & Activity Updates
  python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --mock
  python3 scripts/run-local-benchmark.py --configs hip,vulkan,cpu --services all --report scratch/test.md --data scratch/test.json
  python3 scripts/update-activity.py [--write]  # Updates research/weekly-devel-activity.md
  ```

## Operating Guidelines

### Workspace & Documentation
- **Workspace Isolation:** Use `scratch/` in repo root for temporary files, research, and git checkouts (`scratch/*-sources`).
- **Docs Maintenance:** Update `README.md`, `assistants/*-ctl.md`, and `scripts/` whenever script behaviors or ports change. Update the "## Sandboxing Architecture" section if isolation profiles change.
- **Sandbox Templates:**
  - **OpenCode:** Keep `sandbox-templates/opencode/opencode.json` and `~/.config/opencode/opencode.json` synced. Run `~/.config/opencode/copy-config-to-target.sh` to save running configs back to the repo.
  - **OMP:** Templates reside in `sandbox-templates/omp/`.

### Benchmarking Rules
- **Script Sync:** Update `scripts/run-local-benchmark.py` whenever local service outputs, performance formats, or env variable prefixes (`LLM_` -> `LCHAT_`, `EMBED_` -> `LMBD_`) change.
- **Report Protection:** Running `--mock` auto-redirects outputs to `scratch/local-benchmark-mock.*`. For custom tests, explicitly pass `--report scratch/test.md --data scratch/test.json` to prevent overwriting production reports in `assistants/`.

### Sandboxing & Bubblewrap (`bwrap`) Discipline
Check if running inside a bwrap sandbox:
```bash
[ -S "${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/systemd/private" ] || echo "bwrapped"
```
**If bwrapped (systemd socket unavailable):**
- **Restriction:** Do **NOT** execute systemd service management commands (`systemctl start/stop/restart/status`).
- **Introspection:** Inspect active processes and logs using `journalctl` (`--user`), `ps`, `/proc`, and `pgrep`.
- **Debugging Control Wrappers:**
  - Test config generation: `./assistants/<name>-ctl install --no-start --new-config`
  - Inspect generated systemd/env files (e.g. `~/.config/systemd/user/<name>-gateway.env`) to verify path specifier expansions (`%h`, `~`).
  - Test CLI routing: `./assistants/<name>-ctl exec --help`
  - Cleanup test installs: `./assistants/<name>-ctl uninstall`

### Upstream Schema Discovery
Discover configuration schemas and features by inspecting checked-out sources in `scratch/*-sources`:
- **ZeroClaw:** `crates/zeroclaw-config/src/schema.rs`, `crates/zeroclaw-memory/`
- **IronClaw:** `.env.example`, `FEATURE_PARITY.md`
- **Hermes:** `hermes_constants.py`, `agent/context_compressor.py`, `acp_adapter/`
- **NanoBot:** `nanobot/config/schema.py`, `nanobot/agent/memory.py`
- **LibreFang:** `librefang.toml.example`, `.env.example`, `crates/librefang-types/src/config/types.rs`
- **NanoClaw:** `.env.example`, `src/config.ts`, `src/env.ts`
- **PicoClaw:** `.env.example`, `config/config.example.json`, `pkg/config/config.go`

## Agent Delegation Rules

### Specialist Roles

Map `@rolename` references to your harness's available sub-agents according to these specialization profiles:

- `@orchestrator`: Workflow planning, delegation, context tracking, final review.
- `@explorer`: Read-only codebase search, symbol mapping, file and pattern discovery.
- `@oracle`: Deep architecture design, root-cause debugging, strategic decisions.
- `@librarian`: External web docs, API references, library research.
- `@designer`: UI/UX, CSS styling, layout structure, frontend components.
- `@fixer`: Code edits, refactoring, bug fixes, multi-file feature implementations.
- `@council`: Multi-perspective peer review, risk assessment and consensus validation before execution.
- `@observer`: Visual UI inspection, render validation, screenshot analysis.
- `@janitor`: Tech debt cleanup, dead code removal, doc alignment.

### Rules

- Orchestrator Limits: Direct edits allowed only for single-file trivial tweaks, doc updates, and synthesis.
- Delegate Execution: Multi-file edits or complex tasks go to `@fixer`. If reaching for `edit`/`write`/`bash` to write code, **stop and delegate**.
- Research: Use `@explorer` for codebase searches (no manual grep/glob) and `@librarian` for web/docs.
- Escalations: Route to `@oracle` for complex bugs or after 2 failed fix attempts. Route to `@council` before risky breaking changes.

