---
name: deep-research
description: "Executes automated search on Google Gemini using Playwright, extracts structured data blocks, and merges them into a single YAML file."
version: 1.0.0
author: Developer
license: MIT
platforms: [linux, macos]
metadata:
  openclaw:
    tags: [Deep-Research, Browser-Automation, Playwright, Gemini, YAML]
    related_skills: []
---

# Deep Research Agent Skill

This skill automates Gemini Deep Research via Playwright to fetch web information and compile structured, type-agnostically merged YAML data blocks.

## When to Use
- You need to search for current events or run a deep web research query using Google Gemini.
- You want to extract information into structured YAML format across multiple output blocks without hitting token limits.
- You need to automatically run deep research, download code blocks, and merge them into a single target file.

## CLI Usage

### 1. Browser/Interactive Session Setup (headed)
The User must use this command once to log into the Gemini account and establish a session state:
```bash
./deep-research-to-yaml.py browser [profile_name]
```

### 2. Running Research (headless)
Execute the automated deep research:
```bash
./deep-research-to-yaml.py research <prompt_file> [search="<query_string>"] [profile=<profile_name>] [output=<output_path.yaml>] [headed|headless]
```
## Agent Rules & Guidelines
1. **German Interface Handling**: The target browser window/Gemini DOM will likely be in German. Selectors are hardcoded to match both English and German tags (e.g. `button:has-text('Recherche starten')` and `button[aria-label='Nachricht senden']`). Keep these selectors intact.
2. **Double-Submit Prevention**: Never press `Enter` while clicking the send button, as it halts Gemini's input submission. The script is configured to safely click the send button.
3. **Plan Confirmation Gate**: Gemini Deep Research prompts a plan verification screen before searching. The script automatically handles clicking `Recherche starten` or `Start research`.
4. **Block Counting**: Completion tracking is based on the count of rendered download buttons (`download_btn.count() >= data_blocks`). Make sure the target prompt configures `data_blocks` in its YAML frontmatter.
5. **Custom Prompt Schema**: Custom deep research prompts must have frontmatter indicating the number of expected output `data_blocks`, and structure their prompt instructions to make Gemini emit exactly that many consecutive YAML blocks. A comprehensive generic prompt template is available in the [deep-research README.md](README.md#designing-a-custom-research-prompt).
