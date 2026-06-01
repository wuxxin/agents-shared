# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 26, 2026 – June 1, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 280 | 54 | `main` | 2026-06-01 | **144** | 0 | 6 | 196.0 | `v2026.5.31-beta.16`, `v2026.5.30-beta.15` | `librefang-git` @ `2026.5.31beta.16.r6.g23e4fe214-1` | 0 | **Highly Active** |
| **zeroclaw** | 31,655 | 4,663 | `master` | 2026-05-31 | **67** | 0 | 0 | 68.2 | `v0.8.0-beta-1` (2026-05-21) | `zeroclaw-git` @ `0.8.0.beta.1.r117.g0690456f9-1` | 0 | **Highly Active** |
| **moltis** | 2,714 | 320 | `main` | 2026-05-29 | **27** | 0 | 5 | 50.0 | `20260529.02`, `20260529.01` | `moltis-git` @ `20260529.02.r0.g6de135a28-1` | 0 | **Highly Active** |
| **ironclaw** | 12,376 | 1,446 | `main` | 2026-05-28 | **6** | 0 | 1 | 21.2 | `ironclaw-v0.29.0` (2026-05-26) | `ironclaw-git` @ `ironclaw.v0.29.0.r5.g749f584-1` | 0 | **Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 174,143 | 29,525 | `main` | 2026-06-01 | **623** | 19 | 2 | 743.5 | `v2026.5.29`, `v2026.5.28` | — | — | **Highly Active** |
| **nanobot** | 43,419 | 7,669 | `main` | 2026-06-01 | **67** | 0 | 1 | 102.5 | `v0.2.1` (2026-06-01) | — | — | **Highly Active** |
| **picoclaw** | 29,230 | 4,194 | `main` | 2026-06-01 | **17** | 13 | 0 | 35.5 | `v0.2.9` (2026-05-22) | `picoclaw-git` @ `0.2.9.nightly.20260601.ba806592-1` | 4 | **Active** |
| **nanoclaw** | 29,551 | 12,889 | `main` | 2026-05-31 | **5** | 2 | 0 | 54.0 | `v2.0.71` (2026-05-28), `v2.0.70` (2026-05-25) | `nanoclaw-git` @ `r1694.b9141218a-1` | 0 | **Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (144 commits, 6 releases in the last week). **0 commits since installed 2026.5.31beta.16 (r6.g23e4fe214).**
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Externalized template routing rules to an overridable TOML; ensured full suite runs on merge_group so a queue can gate before main; fixed Cargo.lock changes from busting the rust-cache; enabled faster docker dev iteration with mold linker; and enforced required-status-checks for CI Gate.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (67 commits, 0 releases in the last week). **0 commits since installed v0.8.0-beta-1 (r117.g0690456f9).**
* **Recent Focus**: Inlined image data for vision in channels/media-pipeline; matched LID bot mentions in whatsapp-web channel; documented web_dist_dir setting and supported env-var override; removed marketplace sync workflow from release automation; and wired transcription_provider alias for inbound voice in Telegram.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (27 commits, 5 releases in the last week). **0 commits since installed 20260529.02 (r0.g6de135a28).**
* **Recent Focus**: Prepared release 20260529.02 and 20260529.01; hardened request metadata schemas for OpenAI-compatible LLM providers; propagated bundled skill test errors to improve diagnostics; and stabilized command palette UI focus and navigation.

### IronClaw (`nearai/ironclaw`)
* **Status**: Active (6 commits, 1 release in the last week). **0 commits since installed ironclaw.v0.29.0 (r5.g749f584).**
* **Recent Focus**: Scoped id-token: write to nearai-bench CI jobs; granted id-token: write to unblock reusable workflow; tracked nearai/benchmarks @main instead of pinning; plumbed temperature through Responses API; and added WeCom release artifacts.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (623 commits, 19 merges, 2 releases in the last week).
* **Recent Focus**: Mapped Subway2023 for PR salvage; paired terminal-side gate for ~/.hermes/config.yaml writes and blocked agent writes to it to prevent silent approval bypass; stopped reporting broken streams as output-length truncation; and added full administration panel to dashboard for MCP, pairing, webhooks, credentials, memory, gateway, and ops.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (67 commits, 0 merges, 1 release in the last week).
* **Recent Focus**: Updated README with release notes for v0.2.1; released v0.2.1; archived actual idle compact drops in session; corrected last_consolidated tracking in non-contiguous retention; and prevented duplicate archive and message loss in enforce_file_cap.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (17 commits, 13 merges, 0 releases in the last week). **4 commits since installed 0.2.9.nightly.20260601 (ba806592).**
* **Recent Focus**: Flattened if-else chains in cron refactoring; dropped temperature for models that deprecate it in Bedrock; restricted list/get/update to accessible jobs per channel in cron tool; added get and update actions to cron tool; and formatted long lines to satisfy golines.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (5 commits, 2 merges in the last week). **0 commits since installed r1694.b9141218a.**
* **Recent Focus**: Updated token count to 181k tokens; bumped version to 2.0.72; added /upload-trace command to upload session trace to Hugging Face; bumped version to 2.0.71; and bumped claude-code to 2.1.154 and claude-agent-sdk to 0.3.154.


---

## 📋 Instruction Guide: Recreating this Analysis

To re-perform this development activity analysis, follow these steps.

- Read this instructions, then follow these steps for a new analysis

### Step 1: Repository Reference Map
Here is the list of active upstream GitHub repositories and their corresponding system package names (if installed):

| Assistant | GitHub Repo | System Package | Pkg Type |
| :--- | :--- | :--- | :--- |
| **LibreFang** | `librefang/librefang` | `librefang-git` | AUR `-git` |
| **ZeroClaw** | `zeroclaw-labs/zeroclaw` | `zeroclaw-git` | AUR `-git` |
| **Moltis** | `moltis-org/moltis` | `moltis-git` | AUR `-git` |
| **IronClaw** | `nearai/ironclaw` | `ironclaw-git` | AUR `-git` |
| **Hermes Agent** | `NousResearch/hermes-agent` | — | not installed |
| **NanoBot** | `HKUDS/nanobot` | — | not installed |
| **PicoClaw** | `sipeed/picoclaw` | `picoclaw-git` | AUR `-git` |
| **NanoClaw** | `nanocoai/nanoclaw` | `nanoclaw-git` | AUR `-git` |

### Step 2: Gather local installed Package Versions
For each assistant check if installed as a system package and record the version. On Arch Linux, use `pacman -Q`:

```bash
# Probe all known package names and print installed versions
for pkg in librefang-git moltis-git zeroclaw-git ironclaw-git nanoclaw-git picoclaw-git; do
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
  # Fallback: format <tag>.nightly.<date>.<hash> (release/nightly packages)
  if [ -z "$installed_ref" ]; then
    installed_ref=$(echo "$pkg_ver" | grep -oP 'nightly\.[0-9]+\.\K[0-9a-f]+')
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
  [librefang]=librefang-git
  [zeroclaw]=zeroclaw-git
  [moltis]=moltis-git
  [ironclaw]=ironclaw-git
  [hermes-agent]=""
  [nanobot]=""
  [picoclaw]=picoclaw-git
  [nanoclaw]=nanoclaw-git
)

for d in librefang moltis zeroclaw ironclaw hermes-agent nanobot nanoclaw picoclaw; do
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
      # Fallback: format <tag>.nightly.<date>.<hash> (release/nightly packages)
      if [ -z "$installed_ref" ]; then
        installed_ref=$(echo "$pkg_ver" | grep -oP 'nightly\.[0-9]+\.\K[0-9a-f]+')
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
