# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 27, 2026 – June 03, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 283 | 54 | `main` | 2026-06-03 | **170** | 0 | 6 | 180.7 | `v2026.5.31-beta.16`, `v2026.5.30-beta.15` | `librefang-git` @ `2026.5.31beta.16.r33.gfd46c5f9e-1` | 0 | **Highly Active** |
| **zeroclaw** | 31,695 | 4,669 | `master` | 2026-06-03 | **81** | 0 | 1 | 70.5 | `v0.8.0-beta-2` (2026-06-03) | `zeroclaw-git` @ `0.8.0.beta.2.r11.g40be7738f-1` | 0 | **Highly Active** |
| **moltis** | 2,716 | 321 | `main` | 2026-06-03 | **28** | 0 | 5 | 43.5 | `20260602.05`, `20260602.04` | `moltis-git` @ `20260602.05.r1.gdbd58d83b-1` | 0 | **Highly Active** |
| **ironclaw** | 12,384 | 1,446 | `main` | 2026-05-28 | **4** | 0 | 0 | 15.7 | `ironclaw-v0.29.0` (2026-05-26) | `ironclaw-git` @ `ironclaw.v0.29.0.r5.g749f584-1` | 0 | **Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 175,968 | 30,014 | `main` | 2026-06-03 | **665** | 36 | 2 | 720.0 | `v2026.5.29`, `v2026.5.28` | — | — | **Highly Active** |
| **nanobot** | 43,484 | 7,689 | `main` | 2026-06-03 | **105** | 0 | 1 | 111.0 | `v0.2.1` (2026-06-01) | — | — | **Highly Active** |
| **picoclaw** | 29,258 | 4,191 | `main` | 2026-06-03 | **20** | 27 | 0 | 34.5 | `v0.2.9` (2026-05-22) | `picoclaw-git` @ `0.2.9.nightly.20260603.a502aa7f-1` | 1 | **Active** |
| **nanoclaw** | 29,614 | 12,901 | `main` | 2026-05-31 | **5** | 2 | 0 | 44.5 | `v2.0.72` (2026-05-31), `v2.0.71` (2026-05-28) | `nanoclaw-git` @ `r1694.b9141218a-1` | 0 | **Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (170 commits, 6 releases in the last week). **0 commits since installed 2026.5.31beta.16 (r33.gfd46c5f9e).**
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: creator_match filter for TaskClaimed / TaskCompleted triggers; opt-in safe_bins_skip_approval for shell_exec; propagate per-sidecar account_id for multi-bot isolation; ignore skill scaffolder template TODOs; update contributors and star history; remote marketplace install for Hands; memory/wiki ACL denials degrade gracefully instead of killing the turn; auto-commit regenerated codegen on same-repo PRs; split routes/config.rs, routes/skills.rs, routes/workflows.rs, routes/agents.rs into per-concern modules; wire RL rollout export producer into AgentLoopEnd hook; activated parallel tool-call dispatch behind config flag; persisted goal runs and recovered stale runs at boot.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (81 commits, 1 release in the last week). **0 commits since installed v0.8.0-beta-2 (r11.g40be7738f).**
* **Recent Focus**: versioned documentation deployment and version selector; transcode to OGG/Opus for voice notes (Telegram + WhatsApp); deliver WhatsApp replies for LID JIDs and empty sanitization; enforce per-agent tool allowlist in start_channels; bind TTS manager to the channel-owning agent; flag web_dist_dir paths using tilde or $VAR expansion; add dev-sim feature with /tmp/zc-sim-* serial allowlist; add smartroom named-device tools (set_device / read_device) + peripheral wiring support; add http_request private-host allowlist; static output_modality preference on peer groups; honor webhook Retry-After dates; add Spanish and Chinese runtime and zerocode locales (released in `v0.8.0-beta-2`); optional base64 encoding for file_read / file_write; introduce zerocode TUI, RPC socket transport, DenyWithEdit approval, and beta-2 integration; reskinned mdBook to match the web dashboard.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (28 commits, 5 releases in the last week). **0 commits since installed 20260602.05 (r1.gdbd58d83b).**
* **Recent Focus**: update deploy templates and releases to 20260602.05; restore Gemini tool signature replay; default Alibaba Coding live test endpoint; skip blocked live release gates; propagate registry test errors; use explicit OpenAI capabilities; split OpenAI Codex catalog; add NEAR AI Cloud provider; and handle OpenAI Codex final tool-call arguments.

### IronClaw (`nearai/ironclaw`)
* **Status**: Active (4 commits, 0 releases in the last week). **0 commits since installed ironclaw.v0.29.0 (r5.g749f584).**
* **Recent Focus**: Scoped id-token: write to nearai-bench CI jobs; granted id-token: write to unblock reusable workflow; tracked nearai/benchmarks @main instead of pinning; plumbed temperature through Responses API.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (665 commits, 36 merges, 2 releases in the last week).
* **Recent Focus**: Bump npmDepsHash for refreshed lockfile in Nix; regenerate lockfile and map vladkvlchk for salvaged PR; add @testing-library/dom as explicit dev dependency for desktop; include desktop.log in hermes debug share / /debug / hermes logs; fix banner to show 'disabled' instead of 'failed' for enabled:false servers in MCP; make Desktop App remote-backend docs self-contained; add remote-backend section to Desktop App page and explain remote-gateway session token; pass live backend PID to in-app update so its own dashboard is spared; exclude desktop-managed backend from stale-dashboard kill; make matrix bang-command resolution robust, fix dead skill-command branch, and support bang command aliases.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (105 commits, 0 merges, 1 release in the last week).
* **Recent Focus**: Restore top-level import order; cover progress message suppression in email tests; skip progress messages to prevent empty emails after tool calls; reject non-integer consolidated offsets in sessions; reset out-of-range last_consolidated to recover hidden history; replace two-phase Dream class with simple cron + process_direct; bound outbound attachment handling and cover agent-initiated attachments in outbound messages; attach media files to outbound SMTP messages; bound startup fetch waits; split WebUI gateway dependencies; check static token as fallback for handler token issue; remove gateway-specific kwargs from WebSocketChannel; and inject GatewayHTTPHandler in ChannelManager.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (20 commits, 27 merges, 0 releases in the last week). **1 commit since installed 0.2.9.nightly.20260603 (a502aa7f).**
* **Recent Focus**: Bump go from 1.25.10 to 1.25.11 (GO-2026-5039); logs detection; complete picoclaw-agent skill documentation; use sync.Once for thread-safe Stop() in SessionManager; retry transient LLM HTTP errors using provider error classifier; add Zhipu API error code 1210 to format error patterns; add Stop() to SessionManager to prevent goroutine leak; flatten if-else chains and suppress dupl lint; drop temperature for models that deprecate it; restrict list/get/update to accessible jobs per channel; and add get and update actions to cron tool.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (5 commits, 2 merges, 0 releases in the last week). **0 commits since installed b9141218a.**
* **Recent Focus**: Update token count to 181k tokens (91% of context window); bump version to 2.0.72; add /upload-trace command to upload session trace to Hugging Face; bump version to 2.0.71; and bump claude-code to 2.1.154 and claude-agent-sdk to 0.3.154.


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
