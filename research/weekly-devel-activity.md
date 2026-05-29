# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 23, 2026 – May 29, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 278 | 54 | `main` | 2026-05-29 | **199** | 0 | 2 | 250.7 | `v2026.5.28-beta.14`, `v2026.5.25-beta.13` | `librefang-cli-git` @ HEAD | 83 | **Highly Active** |
| **moltis** | 2,710 | 318 | `main` | 2026-05-28 | **53** | 0 | 5 | 67.0 | `20260526.03`, `20260526.02` | `moltis-git` @ HEAD | 6 | **Highly Active** |
| **zeroclaw** | 31,627 | 4,660 | `master` | 2026-05-28 | **81** | 0 | 0 | 66.0 | `v0.8.0-beta-1` (2026-05-21) | `zeroclaw-git` @ HEAD | 1 | **Highly Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 172,238 | 28,936 | `main` | 2026-05-29 | **690** | 16 | 2 | 734.5 | `v2026.5.29`, `v2026.5.28` | — | — | **Highly Active** |
| **nanobot** | 43,353 | 7,650 | `main` | 2026-05-29 | **64** | 4 | 0 | 105.2 | `v0.2.0` (2026-05-16) | — | — | **Highly Active** |
| **nanoclaw** | 29,522 | 12,883 | `main` | 2026-05-28 | **20** | 21 | 0 | 65.5 | `v2.0.70` (2026-05-25) | `nanoclaw-git` @ HEAD | 2 | **Highly Active** |
| **picoclaw** | 29,212 | 4,186 | `main` | 2026-05-29 | **15** | 13 | 0 | 33.7 | `v0.2.9` (2026-05-22) | `picoclaw` @ HEAD | **8** | **Highly Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (199 commits, 2 releases in the last week).
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Unified the three out-of-process sidecar bridges onto a shared transport crate (`engine = "sidecar"`); completed a comprehensive security audit sweep of the memory subsystem fixing 5 critical and 7 high vulnerabilities (split-brain, RBAC, decay, prompt budget, async consolidation); added a Tools tab with grouped views and source attribution to the dashboard UI; added search filtering to the FangHub skills grid; implemented a Kanban task board page in the dashboard; tightened runtime tool runners (filesystem protection via backslash rejection, canonicalization, and TOCTOU fixes, and Canvas security via XSS escapes and data URI blocking); and routed `auto_evolve` creations through the `skill_workshop` pending queue.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (53 commits, 5 releases in the last week).
* **Recent Focus**: Enforced release gates and isolated `qmd` installs in CI pipelines; stripped user names for the MiniMax provider; preserved host execution targets in cron jobs; supported message forks in the Web UI by including clicked responses; logged silent voice message drops in the Discord channel adapter; and prepared releases up to `20260526.03`.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (81 commits, 0 releases in the last week).
* **Recent Focus**: Added Codex subscription authorization check for the OpenAI provider during onboarding; reconciled channel documentation against schemas and fixed stale CLI references; preserved `reasoning_content` in native tool requests; used platform-agnostic paths in configuration policy tests; replaced flaky wall-clock assertions in tests with deterministic overlap checks; generalized the `#[secret]` attribute via `SecretField` trait; and declared a minimum browser floor with an unsupported-browser fallback banner in the Web UI.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (690 commits, 16 merges, 2 releases in the last week).
* **Recent Focus**: Tightened security by removing vestigial Nous API auth parameters, legacy session key fallbacks, and JWT-shape fallbacks; blocked AWS SDK credentials from leaking into subprocess environments; scoped bridge catalog search and tool dispatching specifically to the current session's toolsets; implemented progressive tool disclosure for MCP and plugin tools; relaxed Codex no-byte TTFB watchdog threshold to 120s to prevent premature timeouts; and added clear diagnostic errors for media rejections at the gateway.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (64 commits, 4 merges in the last week).
* **Recent Focus**: Introduced multi-tenant project workspaces and granular access control policies in the Web UI; added customizable context window settings; isolated signed media serving and added support for video byte-range queries and markdown previews; restructured the agent runner by moving document extraction logic out of the core loop and introducing a toggle to disable extraction; added extension registry source support and registry logos; trusted official MS Teams service hosts; and improved error messaging on billing/quota arrears.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Highly Active (20 commits, 21 merges in the last week).
* **Recent Focus**: Bumped upstream `claude-code` to version 2.1.154 and `claude-agent-sdk` to 0.3.154; updated documented context window utilization metrics up to 179k tokens; added support for reading settings from per-group `CLAUDE.local.md` files; and exited the agent runner cleanly on persistent SQLite `inbound.db` corruption errors.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Highly Active (15 commits, 13 merges, 0 releases in the last week). **8 commits since installed v0.2.9.nightly.20260528.28ec5793.**
* **Recent Focus**: Added auto-detection for Termux SSL certificate paths; preserved `created_at` timestamps across history bootstrap; fixed command job execution failures caused by a missing `action` argument in cron jobs; and bumped dependencies such as `github.com/pion/rtp` and `github.com/caarlos0/env/v11`.

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
