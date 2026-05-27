# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 21, 2026 – May 27, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 276 | 54 | `main` | 2026-05-26 | **220** | 0 | 2 | 270.0 | `v2026.5.25-beta.13` | `librefang-cli-git` @ HEAD | 0 | **Highly Active** |
| **moltis** | 2,709 | 319 | `main` | 2026-05-26 | **50** | 0 | 5 | 76.8 | `20260526.03`, `20260525.01` | `moltis-git` @ HEAD | 0 | **Highly Active** |
| **zeroclaw** | 31,605 | 4,660 | `master` | 2026-05-25 | **61** | 0 | 1 | 64.7 | `v0.8.0-beta-1` (2026-05-21) | `zeroclaw-git` @ HEAD | 0 | **Highly Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 169,810 | 28,311 | `main` | 2026-05-26 | **582** | 17 | 0 | 756.7 | `v2026.5.16` (2026-05-16) | — | — | **Highly Active** |
| **nanobot** | 43,252 | 7,630 | `main` | 2026-05-27 | **96** | 7 | 0 | 102.2 | `v0.2.0` (2026-05-16) | — | — | **Highly Active** |
| **nanoclaw** | 29,461 | 12,876 | `main` | 2026-05-25 | **20** | 20 | 0 | 78.0 | `v2.0.70` (2026-05-25) | `nanoclaw-git` @ HEAD | 0 | **Highly Active** |
| **picoclaw** | 29,201 | 4,181 | `main` | 2026-05-26 | **19** | 11 | 1 | 34.2 | `v0.2.9` (2026-05-22) | `picoclaw` v0.2.8 | **189** | **Highly Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (220 commits, 2 releases in the last week).
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Exposed per-provider budget caps surface in API and dashboard; propagated kernel-attested caller context to MCP servers; added per-agent proactive memory with extraction_model field for multi-provider setups; plugged agent-loop data leaks and restored lost state; hardened runtime chat-template leak detection; added bot_token fingerprinting for WeChat sidecar; integrated ESLint jsx-no-target-blank guard; multi-bot isolation via /commands account_id filtering; and resolved nix flake source filter and API migrate path containment bugs.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (50 commits, 5 releases in the last week).
* **Recent Focus**: Supported agents as capability boundaries (MCP, sandbox, skills) with per-agent runtime limits and per-turn tool controls; implemented editable presets and nonblocking spawn agents; exposed Moltis version to agent prompts and local docs; added vault password sync and option to disable encryption at rest; improved voice features (wav metadata for Piper, mp3 chat voice); supported arbitrary chat attachments; fixed Docker builds and sandbox media file reads; and added Codex reasoning effort support.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (61 commits, 1 release in the last week).
* **Recent Focus**: Hardened Canvas iframe sandboxing to prevent token theft via XSS (GHSA-f385-f6h2-3gqj); secured bubblewrap sandboxes by conditionally binding /lib and /lib64; added native extended thinking support for Anthropic and Bedrock providers; implemented Lark/Feishu request_approval channel; improved email channels (HTML body rendering, subject threading, attachment paths); resolved Discord session resumption and Homebrew config detection; and expanded maintainer, skills, and setup documentation.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (582 commits, 17 merges in the last week).
* **Recent Focus**: Built full dashboard OAuth authentication system (Nous plugin, PKCE flow, SPA auth widget, WS ticket auth, session cookies, audit logging, /login redesign); hardened xAI OAuth by gating slash-enum strip on model name; fixed Telegram gateway (heartbeat editing, start ping filtering, compaction noise, Codex 429 rate-limit classification); stabilized Codex adapter (foreign-issuer reasoning drop, transient replay state cleanup); improved Docker tagging and Chromium discovery; and recovered Windows Discord voice opus decoding.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (96 commits, 7 merges in the last week).
* **Recent Focus**: Unified CLI apps and MCP; added Telegram webhook support with an ordered message queue; enhanced providers with Step Plan support, OpenAI extraBody support, and apiType validation; hardened agent loop for sustained goal continuation with maxConcurrentSubagents propagation; updated Kagi search API integration; enabled WebUI ESLint; and improved slash command actions and activity display.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Highly Active (20 commits, 20 merges in the last week).
* **Recent Focus**: Documented context window scaling up to 179k tokens (89% capacity); released versions v2.0.65 through v2.0.70; improved agent runner error handling (exit on persistent database corruption, transcript rotate override, oversized session rotation before resume); added add-rtk skill for token-efficient CLI proxy; corrected Photon URL and configuration setting sources for per-group settings; and fixed signal-cli 0.13+ account listing.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Highly Active (19 commits, 11 merges, 1 release in the last week). **189 commits since installed v0.2.8.**
* **Recent Focus**: Supported per-message created_at timestamps and session history normalization; added line numbers and wrap toggle for Web UI code blocks; implemented request-scoped context policies and DeepSeek thinking field mapping; added gpt4free OpenAI-compatible provider; fixed cron job execution missing 'action' arg and Discord attachment downloads for vision pipeline; and bumped dependencies to resolve security advisories (golang.org/x/net to v0.55.0).




---

## 📋 Instruction Guide: Recreating this Analysis

To re-perform this development activity analysis, follow these steps.

- Read this instructions, then follow these steps for a new analysis

### Step 1: Repository Reference Map
Here is the list of active upstream GitHub repositories and their corresponding system package names (if installed):

| Assistant | GitHub Repo | System Package | Pkg Type |
| :--- | :--- | :--- | :--- |
| **LibreFang** | `librefang/librefang` | `librefang-cli-git` | AUR `-git` |
| **Moltis** | `moltis-org/moltis` | `moltis-git` | AUR `-git` |
| **ZeroClaw** | `zeroclaw-labs/zeroclaw` | `zeroclaw-git` | AUR `-git` |
| **Hermes Agent** | `NousResearch/hermes-agent` | — | not installed |
| **NanoBot** | `HKUDS/nanobot` | — | not installed |
| **NanoClaw** | `nanocoai/nanoclaw` | `nanoclaw-git` | AUR `-git` |
| **PicoClaw** | `sipeed/picoclaw` | `picoclaw` | AUR release |

### Step 2: Gather local installed Package Versions
For each assistant check if installed as a system package and record the version. On Arch Linux, use `pacman -Q`:

```bash
# Probe all known package names and print installed versions
for pkg in librefang-cli-git moltis-git zeroclaw-git nanoclaw-git picoclaw; do
  ver=$(pacman -Q "$pkg" 2>/dev/null | awk '{print $2}')
  if [ -n "$ver" ]; then
    echo "$pkg: $ver"
  else
    echo "$pkg: not installed"
  fi
done
```

**Version format notes** (Arch `-git` packages follow `pkgver-pkgrel`):
* `-git` packages with a tag base embed the git hash after `g`: e.g. `2026.5.25beta.13.r1.gd4adc14f8-1`
  * Extract the commit hash after the last `g`: `echo "$ver" | grep -oP 'g\K[0-9a-f]+'`
  * The `rN` part is the number of commits *past* the last tag.
* `-git` packages without tags use `r<revcount>.<hash>`: e.g. `r1687.24922593e-1`
  * Extract with: `echo "$ver" | grep -oP 'r[0-9]+\.\K[0-9a-f]+'`
* Release packages use the upstream tag directly: e.g. `0.2.8-1` → git tag `v0.2.8`.

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

# 1.1 Commits since installed package version.
#     For -git packages: extract the embedded commit hash from pacman version.
#     For release packages: map version to a git tag (e.g. 0.2.8 -> v0.2.8).
pkg_ver=$(pacman -Q "$PKG_NAME" 2>/dev/null | awk '{print $2}')
if [ -n "$pkg_ver" ]; then
  # Try to extract git hash: format <tag>.rN.g<hash> (most -git packages)
  installed_ref=$(echo "$pkg_ver" | grep -oP 'g\K[0-9a-f]+')
  # Fallback: format r<revcount>.<hash> (no-tag -git packages like nanoclaw)
  if [ -z "$installed_ref" ]; then
    installed_ref=$(echo "$pkg_ver" | grep -oP 'r[0-9]+\.\K[0-9a-f]+')
  fi
  if [ -z "$installed_ref" ]; then
    # Release package: strip pkgrel suffix and prepend 'v'
    installed_ref="v$(echo "$pkg_ver" | sed 's/-[0-9]*$//')"
  fi
  echo "Commits since installed ($installed_ref):"
  git log --no-merges --oneline "${installed_ref}..HEAD" | wc -l
fi

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

# 6.1 If assistant is installed, show commit subjects since installed version
if [ -n "$pkg_ver" ]; then
  echo "--- commits since installed ($installed_ref) ---"
  git log --no-merges --oneline "${installed_ref}..HEAD" -n 25
fi
```

### Step 4: Batch Statistics Helper Script
To gather all required metrics for all repositories at once, run the following script from the root directory of the workspace:

```bash
# Map: directory_name -> pacman package name (empty = not installed)
declare -A PKG_MAP=(
  [librefang]=librefang-cli-git
  [moltis]=moltis-git
  [zeroclaw]=zeroclaw-git
  [hermes-agent]=""
  [nanobot]=""
  [nanoclaw]=nanoclaw-git
  [picoclaw]=picoclaw
)

for d in librefang moltis zeroclaw hermes-agent nanobot nanoclaw picoclaw; do
  echo "=== $d ==="
  cd "scratch/$d" 2>/dev/null || continue
  
  # Ensure the correct default branch is checked out and reset
  branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
  if [ -z "$branch" ]; then
    branch=$(git branch -r | grep -E 'origin/main|origin/master' | head -n 1 | sed 's/.*origin\///')
  fi
  git checkout "$branch" &>/dev/null
  git reset --hard "origin/$branch" &>/dev/null
  
  commits=$(git log --since="7 days ago" --no-merges --oneline | wc -l)
  merges=$(git log --since="7 days ago" --merges --oneline | wc -l)
  last_commit=$(git log -1 --format="%ad" --date=short)
  commits_28=$(git log --since="28 days ago" --no-merges --oneline | wc -l)
  avg_commits=$(echo "scale=1; $commits_28 / 4" | bc)
  tags=$(git log --tags --since="7 days ago" --simplify-by-decoration --pretty="format:%d" | tr -d '()' | tr '\n' ',' | sed 's/,$//')
  
  # Installed package version and commits since
  pkg="${PKG_MAP[$d]}"
  pkg_info="not installed" since_commits="-"
  if [ -n "$pkg" ]; then
    pkg_ver=$(pacman -Q "$pkg" 2>/dev/null | awk '{print $2}')
    if [ -n "$pkg_ver" ]; then
      # Extract git hash: format <tag>.rN.g<hash> (most -git packages)
      installed_ref=$(echo "$pkg_ver" | grep -oP 'g\K[0-9a-f]+')
      # Fallback: format r<revcount>.<hash> (no-tag -git packages like nanoclaw)
      if [ -z "$installed_ref" ]; then
        installed_ref=$(echo "$pkg_ver" | grep -oP 'r[0-9]+\.\K[0-9a-f]+')
      fi
      if [ -z "$installed_ref" ]; then
        # Release package: strip pkgrel suffix and prepend 'v'
        installed_ref="v$(echo "$pkg_ver" | sed 's/-[0-9]*$//')"
      fi
      since_commits=$(git log --no-merges --oneline "${installed_ref}..HEAD" 2>/dev/null | wc -l)
      pkg_info="$pkg_ver (ref=$installed_ref)"
    fi
  fi
  
  echo "commits=$commits merges=$merges last_commit=$last_commit avg_commits=$avg_commits tags=[$tags]"
  echo "pkg=$pkg_info since_installed=$since_commits"
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
