# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 16, 2026 – May 23, 2026)

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **librefang** | 272 | 54 | `main` | 2026-05-22 | **308** | 0 | 2 | 355.2 | `v2026.5.17-beta.12` | **Highly Active** |
| **moltis** | 2,700 | 315 | `main` | 2026-05-22 | **40** | 0 | 5 | 96.2 | `20260519.01`, `20260518.01` | **Highly Active** |
| **zeroclaw** | 31,535 | 4,646 | `master` | 2026-05-22 | **56** | 0 | 1 | 72.0 | `v0.8.0-beta-1` (2026-05-21) | **Highly Active** |
| **hermes-agent** | 163,134 | 26,684 | `main` | 2026-05-22 | **776** | 14 | 1 | 846.5 | `v2026.5.16`, `v2026.5.7` | **Highly Active** |
| **nanobot** | 43,003 | 7,572 | `main` | 2026-05-23 | **155** | 13 | 1 | 125.5 | `v0.2.0` (2026-05-16) | **Highly Active** |
| **nanoclaw** | 29,280 | 12,856 | `main` | 2026-05-22 | **36** | 17 | 1 | 130.8 | `v2.0.64` (2026-05-18) | **Highly Active** |
| **picoclaw** | 29,133 | 4,174 | `main` | 2026-05-22 | **31** | 5 | 2 | 62.2 | `v0.2.9` (2026-05-22) | **Highly Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (308 commits, 2 releases in the last week).
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Shifted WhatsApp integration from in-process Rust adapter to sidecar python-sdk adapter, fixed test fixture drift, and refined config-validation env-var hooks.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (40 commits, 5 releases in the last week).
* **Recent Focus**: Reasoning effort support for OpenAI Codex endpoints, splitting test suites, expanding wav metadata extraction for Piper TTS, and supporting arbitrary chat attachments.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (56 commits, 1 release in the last week).
* **Recent Focus**: OTel tool span enrichment with Semantic Conventions (`gen_ai.tool.*`), onboarding improvements, service templates parameterization, and Discord thread message route bugfixes.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (776 commits, 14 merges in the last week).
* **Recent Focus**: Significant work on mobile/Termux optimization, access token lifecycle management (e.g., Minimax OAuth refactoring), and speedups for bare CLI prompts.
### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (155 commits, 13 merges, 1 release in the last week).
* **Recent Focus**: Windows CI compatibility for CLI Apps, UI localization updates, and safety improvements for fetch preflight streaming.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Highly Active (36 commits, 17 merges, 1 release in the last week).
* **Recent Focus**: WhatsApp message formatting skill, agent runner envelope drops bugfix, and documentation enhancements regarding context window scaling (reaching 177k tokens).

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Highly Active (31 commits, 5 merges, 2 releases in the last week).
* **Recent Focus**: Timestamps for session messages, and critical dependency updates (bumping `golang.org/x/net` to `v0.55.0` to address security advisories).



---

## 📋 Instruction Guide: Recreating this Analysis

To perform this development activity analysis for another week, follow these steps.

### Step 1: Repository Reference Map
Here is the list of active upstream GitHub repositories:
* **LibreFang**: `librefang/librefang`
* **Moltis**: `moltis-org/moltis`
* **ZeroClaw**: `zeroclaw-labs/zeroclaw`
* **Hermes Agent**: `NousResearch/hermes-agent`
* **NanoBot**: `HKUDS/nanobot`
* **NanoClaw**: `nanocoai/nanoclaw`
* **PicoClaw**: `sipeed/picoclaw`

### Step 2: Gathering Data via Local Clone
If you have local checkouts of the repositories, run the following commands inside each repository:

```bash
# 1. Total commits in the last 7 days
git log --since="7 days ago" --no-merges --oneline | wc -l

# 2. Total pull request merges in the last 7 days
git log --since="7 days ago" --merges --oneline | wc -l

# 3. Last commit date
git log -1 --format="%ad" --date=short

# 4. Average weekly commits over the last 4 weeks
# (Total commits divided by 4)
git log --since="28 days ago" --no-merges --oneline | wc -l

# 5. List tags/releases created in the last 7 days
git log --tags --since="7 days ago" --simplify-by-decoration --pretty="format:%d %as"
```

### Step 3: Gathering Data via GitHub API
If you do not have local clones, you can fetch the statistics using `curl` and the GitHub API. 
*Note: Set your `GITHUB_TOKEN` environment variable if you hit rate limits.*

```bash
# Define target repository and date boundaries
REPO="librefang/librefang"
SINCE_DATE="2026-05-16T00:00:00Z"

# 1. Fetch commits since a given date
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/commits?since=$SINCE_DATE" | jq '. | length'

# 2. Fetch releases created since a given date
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO/releases" | jq --arg since "$SINCE_DATE" \
  '.[] | select(.created_at >= $since) | {name: .name, tag_name: .tag_name, date: .created_at}'

# 3. Fetch current stars and forks
curl -s -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO" | jq '{stargazers_count, forks_count}'
```

### Step 4: Compiling the Summary
1. Update the dates in the report title and column headers.
2. Query each active repository using the commands above.
3. Populate the weekly commits, merges, releases, and averages into the table.
4. Review the recent commit subjects (`git log --since="7 days ago" --oneline`) to write the brief summary of recent focus areas for each repository.
