# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

### 📊 Summary of Weekly Activity (May 30, 2026 – June 06, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **ironclaw** | 12,396 | 1,445 | `main` | 2026-06-05 | **166** | 2 | 1 | 221.2 | `ironclaw-v0.29.1` (2026-06-04) | `ironclaw-git` @ `ironclaw.v0.29.0.r5.g749f584-1` | 976 | **Highly Active** |
| **librefang** | 285 | 54 | `main` | 2026-06-05 | **62** | 0 | 2 | 166.0 | `v2026.5.31-beta.16`, `v2026.5.30-beta.15` | `librefang-git` @ `2026.5.31beta.16.r33.gfd46c5f9e-1` | 4 | **Highly Active** |
| **zeroclaw** | 31,780 | 4,695 | `master` | 2026-06-06 | **82** | 0 | 1 | 71.7 | `v0.8.0-beta-2` (2026-06-03) | `zeroclaw-git` @ `0.8.0.beta.2.r11.g40be7738f-1` | 29 | **Highly Active** |
| **moltis** | 2,722 | 323 | `main` | 2026-06-05 | **26** | 0 | 6 | 34.5 | `20260603.01`, `20260602.05` | `moltis-git` @ `20260602.05.r1.gdbd58d83b-1` | 10 | **Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 183,194 | 31,424 | `main` | 2026-06-05 | **681** | 54 | 1 | 712.7 | `v2026.6.5` (2026-06-05) | — | — | **Highly Active** |
| **nanobot** | 43,735 | 7,733 | `main` | 2026-06-05 | **112** | 0 | 1 | 109.0 | `v0.2.1` (2026-06-01) | — | — | **Highly Active** |
| **picoclaw** | 29,294 | 4,198 | `main` | 2026-06-05 | **41** | 36 | 0 | 32.2 | `v0.2.9` (2026-05-22) | `picoclaw-git` @ `0.2.9.nightly.20260603.a502aa7f-1` | 26 | **Active** |
| **nanoclaw** | 29,711 | 12,916 | `main` | 2026-06-05 | **13** | 3 | 0 | 31.0 | `v2.0.76` (2026-06-05) | `nanoclaw-git` @ `r1694.b9141218a-1` | 10 | **Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (62 commits, 2 releases in the last week). **4 commits since installed 2026.5.31beta.16 (r33.gfd46c5f9e).**
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: assign approved workshop skill to the creating agent; redact images for text-only models via catalog `supports_vision`; tolerate `<think>` preamble in `history_fold` summary parsing; stop scanning the workflow's own comments to prevent false-positive issues in `todo-to-issue` CI; creator_match filter for TaskClaimed / TaskCompleted triggers; opt-in safe_bins_skip_approval for shell_exec; propagate per-sidecar account_id for multi-bot isolation; ignore skill scaffolder template TODOs.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (82 commits, 1 release in the last week). **29 commits since installed v0.8.0-beta-2 (r11.g40be7738f).**
* **Recent Focus**: support relative after schedules in cron; robustly resolve embedded firmware paths via `CARGO_MANIFEST_DIR`; pass defaulted temperature as option for Ollama; surface pin_devices and description in `hardware_capabilities` tool; share allowlist matching via `crate::allowlist` for WhatsApp Web; treat replies to bot as mentions in WhatsApp Web; setup FreeBSD guide + installable jail files; restore audio attachment transcription in QQ; cover ApprovalBanner in `translate="no"` guard; scrub stale "zeroclaw onboard" references; rename "Scheduled Jobs" tab to "Automations" in WebUI; migrate Agent::turn `load_context` to `MemoryStrategy`.

### Moltis (`moltis-org/moltis`)
* **Status**: Active (26 commits, 6 releases in the last week). **10 commits since installed 20260602.05 (r1.gdbd58d83b).**
* **Recent Focus**: separate Telegram progress stream from final replies; show Polyphony in workflow slide; update deploy templates and releases to 20260603.01; retry empty Fireworks Kimi final turn; expand AI engineering deck examples and fix PDF presentation export; add NFC Summit AI engineering deck; retry transient ZAI catalog probes; restore Gemini tool signature replay.

### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (166 commits, 1 release in the last week). **976 commits since installed ironclaw.v0.29.0 (r5.g749f584).**
* **Recent Focus**: third-party extension hook activation via hook-only projection (`HOOKS_THIRD_PARTY_ENABLED`); activate hook framework in production behind `HOOKS_ENABLED` flag; LibSql/Postgres PredicateStateBackend in own crate; cross-backend adversarial parity suite; prevent cross-tenant leakage, replay, and provider spoofing in event-triggered hooks; drive `arguments_digest` snapshot through `invoke_capability`; add NEAR onboarding setup menu and reborn startup guide.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (681 commits, 54 merges, 1 release in the last week).
* **Recent Focus**: clean force-send of queued messages in TUI; integrate arrow history with the message queue on desktop; arrow up/down to navigate previous user messages; reliable composer message queue; repair macOS updater helper; add `/version` slash command across CLI, gateway, TUI, and desktop; cover IME-composed send-button visibility (Chinese/Japanese/Korean) on desktop; release v0.16.0 (`v2026.6.5`); make rg/grep search error guard reachable and preserve partial matches.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (112 commits, 1 release in the last week).
* **Recent Focus**: route and document `/skill` command to list enabled skills; persist user messages for refresh in WebUI; fix pairing for Weixin and Telegram DMs; support custom image generation provider; allow punctuation after Feishu mention placeholders and strip leading bot mention before commands.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (41 commits, 36 merges, 0 releases in the last week). **26 commits since installed 0.2.9.nightly.20260603 (a502aa7f).**
* **Recent Focus**: log warning when `LoadAndDelete` type assertion fails; add edge case tests for `toChannelHashes` type assertions; expose history tokens and remove leaked state files; use prefixed chatID for group reply routing in onebot; use sync.Once for thread-safe Stop() in SessionManager; handle space in go env GOVERSION; support `anthropic-sdk-go` v1.46.0; handle json.Marshal errors in exec tool responses.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (13 commits, 3 merges, 0 releases in the last week). **10 commits since installed b9141218a.**
* **Recent Focus**: bump version to 2.0.76; blank the secret_url path instead of `/*`; update token count to 181k tokens (91% of context window); trim the upload-trace not-signed-in message; show OneCLI's own setup URL when HF token is missing; simplify HF token setup.

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
