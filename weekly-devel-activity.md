# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 20, 2026 – May 27, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **librefang** | 275 | 54 | `main` | 2026-05-26 | **247** | 0 | 1 | 283.8 | `v2026.5.25-beta.13` | **Highly Active** |
| **moltis** | 2,707 | 318 | `main` | 2026-05-26 | **50** | 0 | 5 | 76.8 | `20260526.03`, `20260525.01` | **Highly Active** |
| **zeroclaw** | 31,594 | 4,656 | `master` | 2026-05-25 | **62** | 0 | 1 | 70.5 | `v0.8.0-beta-1` (2026-05-20) | **Highly Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: |
| **hermes-agent** | 168,630 | 27,996 | `main` | 2026-05-26 | **512** | 10 | 0 | 758.2 | `v2026.5.16` (2026-05-16) | **Highly Active** |
| **nanobot** | 43,199 | 7,617 | `main` | 2026-05-26 | **107** | 7 | 0 | 105.2 | `v0.2.0` (2026-05-16) | **Highly Active** |
| **nanoclaw** | 29,433 | 12,874 | `main` | 2026-05-25 | **21** | 20 | 0 | 81.2 | `v2.0.64` (2026-05-18) | **Highly Active** |
| **picoclaw** | 29,191 | 4,180 | `main` | 2026-05-26 | **22** | 11 | 1 | 35.0 | `v0.2.9` (2026-05-22) | **Highly Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (247 commits, 1 release in the last week).
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Exposed per-provider budget caps surface in API and dashboard; propagated kernel-attested caller context to MCP servers; added bot_token fingerprinting for WeChat sidecar; integrated ESLint jsx-no-target-blank guard; and resolved nix flake source filter and API migrate path containment bugs.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (50 commits, 5 releases in the last week).
* **Recent Focus**: Supported agents as capability boundaries (MCP, sandbox, skills) with per-agent runtime limits and per-turn tool controls; implemented editable presets and nonblocking spawn agents; added vault password sync and option to disable encryption at rest; improved voice features (wav metadata for Piper, mp3 chat voice); supported arbitrary chat attachments; and added Codex reasoning effort support.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (62 commits, 1 release in the last week).
* **Recent Focus**: Hardened Canvas iframe sandboxing to prevent token theft via XSS (GHSA-f385-f6h2-3gqj); migrated to multi-agent runtime and schema V3; secured bubblewrap sandboxes by conditionally binding /lib and /lib64; improved email channels (HTML body rendering, subject threading, attachment paths); resolved Discord session resumption and Homebrew config detection; and expanded maintainer and setup documentation.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (512 commits, 10 merges in the last week).
* **Recent Focus**: Introduced Nous-approved MCP catalog with interactive picker and tool refresh command; hardened security by restricting markdown link schemes, parsing untrusted WeChat XML with defusedxml, and blocking AGENTS.md outside workspace; added watchdog cron, health checks, and freshness badges to Skills Hub; and stabilized CLI with fallback paste collapse.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (107 commits, 7 merges in the last week).
* **Recent Focus**: Unified CLI apps and MCP; added Telegram webhook support with an ordered message queue; enhanced providers with Step Plan support, OpenAI extraBody support, OpenAI apiType validation, and Novita AI integration; implemented OpenRouter reasoning.effort for thinking models; and hardened the agent loop for sustained goal continuation.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Highly Active (21 commits, 20 merges in the last week).
* **Recent Focus**: Documented context window scaling up to 179k tokens (89% capacity); released versions v2.0.65 through v2.0.70; improved agent runner error handling (exit on persistent database corruption, transcript rotate override); and corrected configuration setting sources for per-group settings.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Highly Active (22 commits, 11 merges, 1 release in the last week).
* **Recent Focus**: Supported per-message created_at timestamps and session history normalization; added line numbers and wrap toggle for Web UI code blocks; implemented request-scoped context policies and DeepSeek thinking field mapping; and bumped dependencies to resolve security advisories (golang.org/x/net to v0.55.0).




---

## 📋 Instruction Guide: Recreating this Analysis

To re-perform this development activity analysis, follow these steps.

- Read this instructions, then follow these steps for a new analysis

### Step 1: Repository Reference Map
Here is the list of active upstream GitHub repositories:
* **LibreFang**: `librefang/librefang`
* **Moltis**: `moltis-org/moltis`
* **ZeroClaw**: `zeroclaw-labs/zeroclaw`
* **Hermes Agent**: `NousResearch/hermes-agent`
* **NanoBot**: `HKUDS/nanobot`
* **NanoClaw**: `nanocoai/nanoclaw`
* **PicoClaw**: `sipeed/picoclaw`

### Step 2: Gather local installed Package Versions
For each assistant check if installed as system package, record version number.

### Step 3: Gathering Data via Local Clone
If you have local checkouts of the repositories under `scratch/`, make sure they are up-to-date by fetching and resetting to the latest origin tracking branches (to prevent stale local statistics):

```bash
# 1. Clone any missing repositories (e.g. hermes-agent or librefang) using shallow clone
git clone --depth 2000 https://github.com/NousResearch/hermes-agent.git scratch/hermes-agent

# 2. Fetch the latest commits for existing checkouts
git fetch --all

# 3. Reset local branches to the remote counterpart
# Note: ZeroClaw uses 'master' as its default branch; all others use 'main'.
git checkout main && git reset --hard origin/main
# (or for zeroclaw: git checkout master && git reset --hard origin/master)
```

Once updated, you can query statistics for each repository:

```bash
# 1. Total commits in the last 7 days
git log --since="7 days ago" --no-merges --oneline | wc -l

# 1.1 and if assistant installed, commits since installed version.
#FIXME implement and update
# 
# 2. Total pull request merges in the last 7 days
git log --since="7 days ago" --merges --oneline | wc -l

# 3. Last commit date
git log -1 --format="%ad" --date=short

# 4. Average weekly commits over the last 4 weeks
# (Total commits divided by 4)
git log --since="28 days ago" --no-merges --oneline | wc -l

# 5. List tags/releases created in the last 7 days
git log --tags --since="7 days ago" --simplify-by-decoration --pretty="format:%d %as"

# 6. Show recent commit subjects to summarize focus areas
git log --since="7 days ago" --no-merges --oneline -n 15

# 6.1 If assistant is installed, show recent commit subjects since installed version
#FIXME implement and update
```

### Step 4: Batch Statistics Helper Script
To gather all required metrics for all repositories at once, run the following script from the root directory of the workspace:

```bash
for d in librefang moltis zeroclaw hermes-agent nanobot nanoclaw picoclaw; do
  echo "=== $d ==="
  cd "scratch/$d" 2>/dev/null || continue
  
  # Ensure the correct default branch is checked out and reset
  branch=$(git branch -r | grep -E 'origin/HEAD|origin/main|origin/master' | head -n 1 | sed 's/.*-> //; s/origin\///')
  git checkout "$branch" &>/dev/null
  git reset --hard "origin/$branch" &>/dev/null
  
  commits=$(git log --since="7 days ago" --no-merges --oneline | wc -l)
  merges=$(git log --since="7 days ago" --merges --oneline | wc -l)
  last_commit=$(git log -1 --format="%ad" --date=short)
  commits_28=$(git log --since="28 days ago" --no-merges --oneline | wc -l)
  avg_commits=$(echo "scale=1; $commits_28 / 4" | bc)
  tags=$(git log --tags --since="7 days ago" --simplify-by-decoration --pretty="format:%d" | tr -d '()' | tr '\n' ',' | sed 's/,$//')
  
  echo "commits=$commits merges=$merges last_commit=$last_commit avg_commits=$avg_commits tags=[$tags]"
  cd - &>/dev/null
done
```


### Step 5: Gathering Data via GitHub API
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

### Step 6: Compiling the Summary
1. Update the dates in the report title and column headers.
2. Query each active repository using the commands above.
3. Populate the weekly commits, commits since systempkg version, merges, releases, and averages into the table.
4. Review the recent commit subjects to write the brief summary of recent focus areas for each repository, also include changes since systempkg version

### Step 7: Update and Cleanup of Instructions

- update and cleanup from lessons learned while executing these steps
