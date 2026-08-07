---
name: deep-research
description: "Executes automated research using Playwright, extracts structured data blocks, and merges them into a single file."
version: 1.2.0
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
- You need to automatically run deep research, download resulting research code blocks, and merge them into a single target file for further processing.

## CLI Usage

### 1. Browser/Interactive Session Setup (headed)
The User must use this command once to log into the Gemini account and establish a session state:
```bash
./deep-research-to-yaml.py browser [profile_name]
```

### 2. Running Research (headless)
Execute the automated deep research:
```bash
./deep-research-to-yaml.py research <prompt_file> [--search "<search_str>"] [--replace "<replace_str>"] [--profile <profile_name>] [--output <output_path.yaml>] [--headed|--headless]
```

### 3. ReDownload a Finished Research Result
Download YAML data blocks from a finished conversation URL:
```bash
./deep-research-to-yaml.py download <url> [--profile <profile_name>] [--output <output_path.yaml>] [--headed|--headless]
```

## Data Block Handling

Downloaded blocks are concatenated as raw text (separated by newlines), **not** parsed or structurally merged. This keeps the script format-agnostic. When downloadable code blocks (>0) are detected during generation or download, the script waits 5 seconds, re-counts all available blocks, and downloads them all.

## Session ID Extraction

During execution, the script monitors the browser URL for the Gemini session ID (`https://gemini.google.com/app/<session_id>`) and outputs it once upon detection (e.g., `Gemini Session ID: a84638e1b8935b00`).

## Browser Session Architecture

The `browser` command launches a real Chromium process with `--user-data-dir` to persist login state (cookies, localStorage, session tokens). Gemini requires Google login with MFA/2FA, which cannot be automated. The `research` and `download` commands re-use the same `--user-data-dir` and connect via CDP (Chrome DevTools Protocol) so the saved session carries over without re-authentication.

## Exit Codes

| Code | Phase | Meaning | Retry |
|------|-------|---------|-------|
| `0`  | — | Success: download blocks retrieved and concatenated. | — |
| `1`  | Setup | CLI argument errors, prompt file not found, browser spawn or connect failure. | May analyse and retry. |
| `2`  | Pre-research | Navigation failure, input box not found, prompt entry error, Deep Research toggle failure, query submission failure. | May analyse and retry. |
| `3`  | Plan | Plan confirmation button did not appear or could not be clicked. | **Do NOT retry** — may indicate deep-research session block, or high load abort/timeout. |
| `4`  | Generation | Generation timed out with no download blocks found. | **Do NOT retry** — quota consumed, or high load abort/timeout |

## Agent Rules & Guidelines
1. **Bilingual Selector Support**: Selectors use button text matching for both English and German (e.g. `Start research` / `Recherche starten`). All locator texts are declared as constants at the top of the script.
2. **Double-Submit Prevention**: Never press `Enter` while clicking the send button, as it halts its input submission. The script safely clicks the send button first, falling back to Enter only if the button is not found.
3. **Plan Confirmation Gate**: Deep Research prompts a plan verification screen before searching. The script automatically handles clicking the confirmation button (tries both DE and EN text variants).
4. **Block Download Logic**: As soon as downloadable code blocks (>0) are detected, the script waits for 5 seconds, counts all download buttons, and downloads all of them.
5. **Block Concatenation**: Downloaded blocks are concatenated as raw text with newline separators.
6. **Exit Code Semantics**: Errors before plan confirmation (exit 1–2) are cheap (no Deep Research quota consumed). Errors on or after plan confirmation (exit 3–4) indicate quota was consumed or high load.
