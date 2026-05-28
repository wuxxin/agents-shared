# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 22, 2026 – May 28, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 276 | 54 | `main` | 2026-05-28 | **224** | 0 | 2 | 272.2 | `v2026.5.25-beta.13` | `librefang-cli-git` @ HEAD | 37 | **Highly Active** |
| **moltis** | 2,709 | 318 | `main` | 2026-05-26 | **48** | 0 | 5 | 73.0 | `20260526.03`, `20260525.01` | `moltis-git` @ HEAD | 0 | **Highly Active** |
| **zeroclaw** | 31,617 | 4,661 | `master` | 2026-05-28 | **80** | 0 | 0 | 70.2 | `v0.8.0-beta-1` (2026-05-21) | `zeroclaw-git` @ HEAD | 23 | **Highly Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 170,913 | 28,608 | `main` | 2026-05-25 | **608** | 15 | 0 | 747.7 | `v2026.5.16` (2026-05-16) | — | — | **Highly Active** |
| **nanobot** | 43,300 | 7,642 | `main` | 2026-05-28 | **56** | 4 | 0 | 101.2 | `v0.2.0` (2026-05-16) | — | — | **Highly Active** |
| **nanoclaw** | 29,488 | 12,883 | `main` | 2026-05-25 | **19** | 20 | 0 | 73.0 | `v2.0.70` (2026-05-25) | `nanoclaw-git` @ HEAD | 0 | **Highly Active** |
| **picoclaw** | 29,202 | 4,182 | `main` | 2026-05-26 | **15** | 10 | 1 | 32.5 | `v0.2.9` (2026-05-22) | `picoclaw` v0.2.8 | **189** | **Highly Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (224 commits, 2 releases in the last week).
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Implemented `describe_image()` for media and wired image descriptions via channel adapters; refactored `tool_runner` dispatching and tools to use the new `ToolError` type; added strict input validation, SSRF checks, and safety/PII sanitization across tool runner stubs; resolved cross-chat image leaks by isolating attachment pre-injection per session; introduced a per-agent channel allowlist; fixed Windows-specific issues such as CI Instant subtraction panics and relative path formatting in content responses; and seeded Feishu/Lark configuration forms when the Python SDK is absent.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (48 commits, 5 releases in the last week).
* **Recent Focus**: Gated release workflows on provider tests and integration testing; supported agents as capability boundaries (MCP, sandbox, skills) with per-agent runtime limits, nonblocking spawn agents, and per-turn tool controls; made sub-agent presets editable; exposed Moltis version to prompts and local docs; fixed Docker build failures; and stabilized UI command palette focus.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (80 commits, 0 releases in the last week).
* **Recent Focus**: Tightened Canvas iframe sandboxing to prevent token theft via XSS (GHSA-f385-f6h2-3gqj); preserved `reasoning_content` in native tool requests; declared minimum browser floor and added unsupported-browser fallback banner in Web UI; generalized the `#[secret]` attribute via `SecretField` trait; suppressed verbose INFO logs in agent interactive CLI mode; kept Discord gateway preflight 429 retries retryable; added `file_upload` tool for HTTP multipart uploads; restored legacy channel startup fallback when bindings are empty; and verified self-update downloads against SHA256SUMS.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (608 commits, 15 merges in the last week).
* **Recent Focus**: Enhanced security by rejecting non-regular tar members in auto-installers and android `psutil` compatibility installer, and requiring source CIDR allowlisting for msgraph webhook bindings and `API_SERVER_KEY` for API server dispatches; fixed Kanban layout column wrapping and vertical overflows; normalized Nous Portal entitlement checks for paid/free tiers; synced manual device_code Codex pool entries on re-authorization; fixed xAI OAuth timeout manual fallback; implemented host contracts for external context engines; and pulled full ClawHub catalog into the skills index.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (56 commits, 4 merges in the last week).
* **Recent Focus**: Added Discord model slash command; unified CLI apps and MCP; added Telegram webhook support with an ordered message queue; enhanced OpenAI provider configuration with `extraBody` support, `apiType` validation, and preserved tool call IDs; added Step Plan support; honored `NANOBOT_STREAM_IDLE_TIMEOUT_S` and handled blank Codex transport errors; and stabilized the agent loop by making goal continuation independent and propagating `maxConcurrentSubagents`.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Highly Active (19 commits, 20 merges in the last week).
* **Recent Focus**: Documented context window scaling up to 179k tokens (89% capacity); improved agent runner error handling by exiting on persistent `inbound.db` corruption, honoring zero/negative transcript rotate-age overrides, and rotating oversized/old sessions before resuming; corrected Photon URL to `photon.codes`; loaded per-group `CLAUDE.local.md` setting sources; mapped CLI credential names to Teams app env keys; and fixed `signal-cli` 0.13+ account listings.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Highly Active (15 commits, 10 merges, 1 release in the last week). **189 commits since installed v0.2.8.**
* **Recent Focus**: Supported per-message `created_at` timestamps and normalized session history; added line numbers and wrap toggle for Web UI code blocks; implemented request-scoped context policies and DeepSeek thinking field mapping; added `gpt4free` OpenAI-compatible provider; resolved cron job missing action args and Discord attachment downloads for vision pipeline; and bumped dependency versions to fix security alerts (e.g. `golang.org/x/net`).

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
  
  # Fetch latest updates from remote to avoid stale statistics
  git fetch origin &>/dev/null
  
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

- Modified the Step 4 batch script to run `git fetch origin` directly inside the loop to ensure stats are calculated against the most up-to-date remote state.
