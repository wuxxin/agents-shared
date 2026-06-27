# Deep Research to YAML

This directory implements a Playwright-based browser automation to run Gemini Deep Research and return structured yaml as output.

## Files

- **`deep-research-to-yaml.py`**: Python script using Playwright to control a persistent Chrome instance via CDP, drive Gemini Deep Research, wait for generation with timeout-based completion detection, download output code blocks, and concatenate them into a single output file.

---

## Setup and Usage

### 1. Install Playwright Dependencies
Ensure Playwright and Chromium are installed:
```bash
playwright install chromium
```

### 2. Establish Session State
Since Gemini requires a Google Login which often triggers MFA/2FA, run the browser tool in headed mode to log in once:
```bash
./deep-research-to-yaml.py browser [default]
```
This launches a real Chromium process with `--user-data-dir` pointing at a persistent profile directory (`~/.config/deep-research-profiles/default`).  Log in to your Google Account, navigate to `gemini.google.com`, verify all works, and close the browser.

The `research` command later re-uses the *same* `--user-data-dir` and connects to the browser over CDP (Chrome DevTools Protocol) via `--remote-debugging-port`.  This is the only reliable way to carry over the saved login session to headless automation, because Playwright's own browser launcher would start a fresh profile without the login cookies.

### 3. Running Research (headless)
Execute the automated deep research:
```bash
./deep-research-to-yaml.py research <prompt_file> [search="<query_string>"] [profile=<profile_name>] [output=<output_path.yaml>] [headed|headless]
```

### 4. Downloading Finished Research Results (headed/headless)
Download YAML data blocks from a finished Gemini conversation URL:
```bash
./deep-research-to-yaml.py download <url> [profile=<profile_name>] [output=<output_path.yaml>] [headed|headless]
```
If `output` is omitted, the script automatically extracts the conversation ID from the URL and saves the output to `<chat_id>.yaml`.

---

## Implementing a new custom deep search


### Gemini Output Token Limits (8k limit) and split YAML blocks.

Gemini has a hard output token ceiling of 8K. To prevent output truncations, the prompt must force Gemini to emit the response split across separate YAML blocks. The script tracks progress by count of available download buttons matching the `data_blocks` frontmatter key.

### Data Block Concatenation

Downloaded code blocks are **concatenated as raw text** with newline separators — no YAML parsing or structural merging is performed.  This keeps the script format-agnostic: it works as long as the prompt instructs Gemini to emit blocks whose content can be simply appended.

For example, YAML dicts with non-overlapping top-level keys (`report:`, `data_01:`, `data_02:`) concatenate into a valid multi-document or single-document YAML file.  The caller is responsible for designing prompts so that blocks are self-contained and appendable.

### Example Research Prompt

```markdown
---
data_blocks: 3
search_identifier: "^Target Dates:.+"
---

# Role & Goal
You are a precise, objective research assistant. 
Your task is to find, verify, and compile [Domain] information in [Target Region] for the requested dates,
and output it in the structured format required.
Write in a factual, dry, and professional tone. 
Avoid superlatives, advertising catchphrases, or hype.

## Search Details
Target Dates: [Dynamically replaced by script] ; Today's Date: [Current Date].

- Specific Date Range: [Date formatting guidelines]
- Region: [Target Region]

## Sources & Websites
Perform a general web search, but prioritize and consult these specific domains:
- [Source A URL]
- [Source B URL]

## Filters & Preferences
### Preferred:
- [e.g., ItemA, public Item Z]
- [e.g., ItemC or ItemG]
### Exclusions & Restrictions:
- Exclude: [e.g., itemZ, Item with blue V]

## Data Integrity & Token Optimization
- **Verification**: Cross-reference dates to prevent US/DE format confusion. 
    Provide Google search URLs or direct source links for verification.
- **Aggregation**: Group multiple listings under the same host venue or event organizer to save output tokens.
- **Count**: Target at least [X] high-quality entries for daytime events 
    and [Y] entries for nighttime/special events.

## Output Format

A brief introduction, followed by exactly three separate, consecutive YAML code blocks.
Do not add any other text outside these blocks.

### 1. First YAML Block (Report)
Under the key `report:`, output the detailed Markdown summary:
\`\`\`yaml
report: |
  # [Region] [Domain] Report
  
  ## Venue Summary
  [Table of venues, locations, and summaries...]
  
  ## Accessibility & Cost
  [Table of free vs paid entries, accessibility factors...]
  
  ## Highlights: [Date]
  [Detailed, objective highlights for the day...]
\`\`\`

### 2. Second YAML Block (Data Block 1)
Under the key `data_01:`, output the structured items for the first data block:
\`\`\`yaml
data_01:
  - title: "Item Title"
    org: "Organizer Name"
    type: "item_type"
    loc: "Location Name"
    addr: "Location Address"
    event_url: "https://example.com/details"
    src_url: "https://example.com/source"
    date: "YYYY-MM-DD"
    time_start: "HH:MM"
    time_end: "HH:MM"
    price: "Free / Entry Fee"
    notes: "Brief description of the item."
    tags:
      - "Tag1"
\`\`\`

### 3. Third YAML Block (Data Block 2)
Under the key `data_02:`, output the structured items for the second data block using the exact same schema:
\`\`\`yaml
data_02:
  - title: "Another Item"
    # ... (same schema as data_01)
\`\`\`
```

