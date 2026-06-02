# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

## 📊 Summary of Weekly Activity (May 26, 2026 – June 02, 2026)

Rust Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **librefang** | 283 | 54 | `main` | 2026-06-02 | **157** | 0 | 6 | 184.5 | `v2026.5.31-beta.16`, `v2026.5.30-beta.15` | `librefang-git` @ `2026.5.31beta.16.r6.g23e4fe214-1` | 14 | **Highly Active** |
| **zeroclaw** | 31,695 | 4,669 | `master` | 2026-06-02 | **67** | 0 | 0 | 68.3 | `v0.8.0-beta-1` (2026-05-21) | `zeroclaw-git` @ `0.8.0.beta.1.r117.g0690456f9-1` | 11 | **Highly Active** |
| **moltis** | 2,716 | 321 | `main` | 2026-06-02 | **20** | 0 | 3 | 46.8 | `20260529.02`, `20260529.01` | `moltis-git` @ `20260529.02.r0.g6de135a28-1` | 6 | **Highly Active** |
| **ironclaw** | 12,384 | 1,446 | `main` | 2026-05-28 | **6** | 0 | 1 | 20.8 | `ironclaw-v0.29.0` (2026-05-26) | `ironclaw-git` @ `ironclaw.v0.29.0.r5.g749f584-1` | 0 | **Active** |

Other Projects:

| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Commits (Last Wk) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) | Recent Tags / Versions | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: | :---: |
| **hermes-agent** | 175,968 | 30,014 | `main` | 2026-06-02 | **659** | 23 | 2 | 732.3 | `v2026.5.29`, `v2026.5.28` | — | — | **Highly Active** |
| **nanobot** | 43,484 | 7,689 | `main` | 2026-06-02 | **101** | 0 | 1 | 112.5 | `v0.2.1` (2026-06-01) | — | — | **Highly Active** |
| **picoclaw** | 29,258 | 4,191 | `main` | 2026-06-02 | **14** | 13 | 1 | 35.5 | `v0.2.9` (2026-05-22) | `picoclaw-git` @ `0.2.9.nightly.20260601.ba806592-1` | 5 | **Active** |
| **nanoclaw** | 29,614 | 12,901 | `main` | 2026-05-31 | **5** | 2 | 0 | 48.8 | `v2.0.72` (2026-05-31), `v2.0.71` (2026-05-28) | `nanoclaw-git` @ `r1694.b9141218a-1` | 0 | **Active** |

---

## 🔍 Repository Breakdown

### LibreFang (`librefang/librefang`)
* **Status**: Highly Active (157 commits, 6 releases in the last week). **14 commits since installed 2026.5.31beta.16 (r6.g23e4fe214).**
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: Activated parallel tool-call dispatch behind config flag; persisted goal runs and recovered stale runs at boot; pre-flight hand role spawns before reactivation teardown; extracted heartbeat de-dup transition into a testable helper; split main.rs into per-command modules; executed WASM hooks in the sandbox as pure-compute; fixed cron day-of-week POSIX convention; gated skill_evolve_* tools on auto_evolve and skill_workshop flags; populated sessions.peer_id on save; derived task_claim retry budget from pool size; split role-trait god-file into per-domain modules; retried past lost CAS race in task_claim; made task_claim an atomic compare-and-swap; shipped MCP caller context via _meta; and externalized template routing rules to an overridable TOML.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (67 commits, 0 releases in the last week). **11 commits since installed v0.8.0-beta-1 (r117.g0690456f9).**
* **Recent Focus**: Reskinned mdBook to match the web dashboard; retried empty completions instead of returning a blank turn; redacted Discord delivery failure targets; fell back before visible stream errors; ignored blank SMTP credential overrides; honored private DNS host allowlist; resolved image_info paths through policy; restored date-only channel prompt context; defined lean default channel bundle; added Jina AI as web_search provider; omitted temperature for kimi-k2 models; inlined image data for vision; matched LID bot mentions in whatsapp-web; documented web_dist_dir setting; and removed marketplace sync workflow.

### Moltis (`moltis-org/moltis`)
* **Status**: Highly Active (20 commits, 3 releases in the last week). **6 commits since installed 20260529.02 (r0.g6de135a28).**
* **Recent Focus**: Propagated registry test errors; used explicit OpenAI capabilities; split OpenAI Codex catalog; added NEAR AI Cloud provider; handled OpenAI Codex final tool-call arguments; bounded live integration runtime; prepared releases 20260529.02 and 20260529.01; hardened OpenAI-compatible request metadata; propagated bundled skill test errors; stabilized command palette navigation; tracked bundled skill disables individually; logged silent voice message drops; isolated qmd install; and enforced provider release gates.

### IronClaw (`nearai/ironclaw`)
* **Status**: Active (6 commits, 1 release in the last week). **0 commits since installed ironclaw.v0.29.0 (r5.g749f584).**
* **Recent Focus**: Scoped id-token: write to nearai-bench CI jobs; granted id-token: write to unblock reusable workflow; tracked nearai/benchmarks @main instead of pinning; plumbed temperature through Responses API; and added WeCom release artifacts.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (659 commits, 23 merges, 2 releases in the last week).
* **Recent Focus**: Implemented per-platform streaming defaults (Telegram on, Discord off) and dashboard toggles; rotated dashboard sessions via refresh token; consolidated skills and tools management into one pane; surfaced gateway streaming block in DEFAULT_CONFIG; implemented structured stream-event protocol and Telegram draft formatting parity; sanitized invisible unicode in vetted skill content; reflected active toolset provider in config panel; set up gateway messaging channel from the browser; installed python3-venv so ensurepip fallback works; asserted M3 stale-cache guard contract; preserved Docker -w workdir in main-wrapper; inherited spawning worker's task workspace in kanban_create; completed admin panel with MCP catalog, toggles, hooks, and stats; used registry-backed build cache for arm64; and extended sandbox-mirror guard to cover inner-container path.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Highly Active (101 commits, 0 merges, 1 release in the last week).
* **Recent Focus**: Bounded outbound attachment handling; covered agent-initiated file attachments in outbound messages; attached media files to outbound SMTP messages; bounded startup fetch waits; split WebUI gateway dependencies; checked static token as fallback for handler token issue; removed gateway-specific kwargs from WebSocketChannel; injected GatewayHTTPHandler in ChannelManager; accepted injected http_handler in WebSocketChannel; updated import paths after ws_http move; moved ws_http.py from channels/ to webui/; extracted GatewayHTTPHandler from WebSocketChannel; prevented read_file offload loop; moved media replay helpers out of websocket channel; and removed useless timezone assignment.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (14 commits, 13 merges, 1 release in the last week). **5 commits since installed 0.2.9.nightly.20260601 (ba806592).**
* **Recent Focus**: Added Zhipu API error code 1210 to format error patterns; flattened if-else chains and suppressed dupl lint in cron; dropped temperature for models that deprecate it in Bedrock; restricted list/get/update to accessible jobs per channel in cron tool; added get and update actions to cron tool; formatted long line in codex_provider_test.go; added Bangla support bn-in; fixed linting; added azure entra id support for azure openai provider; added chat image paste and drag-and-drop upload; preserved streamed output text deltas; updated wechat qrcode; and bumped pion/rtp and caarlos0/env/v11.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (5 commits, 2 merges, 0 tags in the last week). **0 commits since installed b9141218a.**
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
