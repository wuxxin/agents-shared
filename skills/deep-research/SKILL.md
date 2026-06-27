---
name: deep-research
description: "Executes automated research using Playwright, extracts structured data blocks, and merges them into a single file."
version: 1.1.0
author: wuxxin
license: MIT
platforms: [linux, macos]
metadata:
  openclaw:
    tags: [Deep-Research, Browser-Automation, Playwright, YAML]
    related_skills: []
---

# Deep Research Agent Skill

This skill automates Gemini Deep Research via Playwright to fetch web information and compile structured, type-agnostically merged YAML data blocks.

## When to Use
- You need to search for current events or run a deep web research query.
- You want to extract information into structured YAML format across multiple output blocks without hitting token limits.
- You need to automatically run deep research, download resulting research code blocks, and merge them into a single target file for further processing

## CLI Usage

### 1. Browser/Interactive Session Setup (headed)
The User must use this command once to log into the Gemini account and establish a session state:
```bash
./deep-research-to-yaml.py browser [profile_name]
```

### Running Research (headless)
Execute the automated deep research:
```bash
./deep-research-to-yaml.py research <prompt_file> [search="<query_string>"] [profile=<profile_name>] [output=<output_path.yaml>] [headed|headless]
```

### ReDownload a Finished Research Result
Download YAML data blocks from a finished conversation URL:
```bash
./deep-research-to-yaml.py download <url> [profile=<profile_name>] [output=<output_path.yaml>] [headed|headless]
```

## Data Block Handling

Downloaded blocks are concatenated as raw text (separated by newlines), **not** parsed or structurally merged.  This keeps the script format-agnostic.  It works as long as the prompt instructs deep research to emit blocks whose content can be simply appended — for example, YAML dicts with non-overlapping top-level keys (``report:``, ``data_01:``, ``data_02:``).  The caller is responsible for designing prompts accordingly.

## Browser Session Architecture

The ``browser`` command launches a real Chromium process with ``--user-data-dir`` to persist login state (cookies, localStorage, session tokens).  Gemini requires Google login with MFA/2FA, which cannot be automated.  The ``research`` and ``download`` commands re-use the same ``--user-data-dir`` and connect via CDP (Chrome DevTools Protocol) so the saved session carries over without re-authentication.

## Exit Codes

| Code | Phase | Meaning | Retry |
|------|-------|---------|-------|
| `0`  | — | Success: all expected blocks downloaded and concatenated. | — |
| `1`  | Setup | CLI argument errors, prompt file not found, browser spawn or connect failure. | May analyse and retry. |
| `2`  | Pre-research | Navigation failure, input box not found, prompt entry error, Deep Research toggle failure, query submission failure. | May analyse and retry. |
| `3`  | Plan | Plan confirmation button did not appear or could not be clicked. | **Do NOT retry** — may indicate deep-research session block, or high load abort/timeout. |
| `4`  | Generation | Generation timed out with no download blocks found. | **Do NOT retry** — quota consumed, or high load abort/timeout |
| `10` | Generation | Partial data: fewer blocks than expected were downloaded. Output file is written with available data. | **Do NOT retry** — inform user. |

For exit 10, (partial output is available) — inform the user about missing data.


## Timeout & Page Reload Behavior

- **Connection Error / Aborted Error Message:** If a "connection aborted, reload page" or German equivalent is detected on the page, a reload is immediately triggered (up to 5 times).
- **DOM idle timeout (120s):** If a DOM MutationObserver is active and no page changes are detected for 120 seconds with zero blocks, a page reload is triggered (up to 5 times). If reloads are exhausted and the idle timeout occurs again, the script aborts (exit 4).
- **DOM observer fallback:** If the MutationObserver cannot be injected (e.g. Shadow DOM), the script waits the full 15-minute total timeout or until download blocks appear.
- **Total timeout (15 min):** Hard limit for research timeout
- **Partial data grace (30s):** Once ≥1 block is found, if no new blocks appear within 30 seconds and the DOM is idle, available blocks are downloaded and the script exits 10.


## Agent Rules & Guidelines
1. **Bilingual Selector Support**: Selectors use button text matching for both English and German (e.g. `Start research` / `Recherche starten`). All locator texts are declared as constants at the top of the script.
2. **Double-Submit Prevention**: Never press `Enter` while clicking the send button, as it halts its input submission. The script safely clicks the send button first, falling back to Enter only if the button is not found.
3. **Plan Confirmation Gate**: Deep Research prompts a plan verification screen before searching. The script automatically handles clicking the confirmation button (tries both DE and EN text variants).
4. **Block Counting**: Completion tracking is based on the count of rendered download buttons. The `data_blocks` frontmatter key specifies the expected count.
5. **Block Concatenation**: Downloaded blocks are concatenated as raw text with newline separators. The prompt must ensure blocks can be simply appended (e.g. YAML dicts with non-overlapping top-level keys).
6. **Exit Code Semantics**: Errors before plan confirmation (exit 1–2) are cheap (no Deep Research quota consumed). Errors on or after plan confirmation (exit 3–4, 10) indicate quota was consumed or high load. Callers should handle exit 10 (partial data) as usable but incomplete output.
7. **Custom Prompt Schema**: Custom deep research prompts must have frontmatter indicating the number of expected output `data_blocks`, and structure their prompt instructions to make Deep Researh emit exactly that many consecutive YAML blocks. A comprehensive generic prompt template is available in the [deep-research README.md](README.md#implementing-a-new-custom-deep-search).
