# Active AI Assistants: Weekly Development Activity

This document tracks repository activity, commit counts, merge frequency, and release cycles for active assistant projects.

---

### 📊 Summary of Weekly Activity (June 02, 2026 – June 09, 2026)

#### Repository Overview & Package Status
| Assistant Repo | Stars | Forks | Main Branch | Last Commit | Installed Pkg | Commits Since Pkg | Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| **ironclaw** | 12,435 | 1,448 | `main` | 2026-06-09 | `ironclaw-git` @ `ironclaw.v0.29.1.r1211.g5364cb3-1` | 46 | **Highly Active** |
| **librefang** | 288 | 55 | `main` | 2026-06-08 | `librefang-git` @ `2026.5.31beta.16.r44.g648356c92-1` | 3 | **Active** |
| **zeroclaw** | 31,838 | 4,710 | `master` | 2026-06-09 | `zeroclaw-git` @ `0.8.0.beta.2.r86.ga486993c9-1` | 31 | **Highly Active** |
| **moltis** | 2,731 | 321 | `main` | 2026-06-05 | `moltis-git` @ `20260603.01.r8.g48c9a4192-1` | 0 | **Active** |
| **hermes-agent** | 188,240 | 32,425 | `main` | 2026-06-09 | — | — | **Highly Active** |
| **nanobot** | 43,941 | 7,778 | `main` | 2026-06-09 | — | — | **Active** |
| **picoclaw** | 29,332 | 4,204 | `main` | 2026-06-09 | `picoclaw-git` @ `0.2.9.nightly.20260607 (7d2b0c2a)` | 19 | **Active** |
| **nanoclaw** | 29,758 | 12,923 | `main` | 2026-06-08 | `nanoclaw-git` @ `r1725.9edb33dd3` | 4 | **Active** |

#### Weekly Activity Metrics (Human vs Bot)
| Assistant Repo | Commits / Week | Lines Added (Human/Bot) | Lines Deleted (Human/Bot) | Merges (Last Wk) | Releases/Tags (Last Wk) | Avg Commits/Wk (4 Wks) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ironclaw** | **155** / 10 | 158.8k / 286 | 19.8k / 216 | 2 | 1 | 196.8 |
| **librefang** | **21** / 6 | 28.1k / 1.1k | 23.5k / 992 | 0 | 0 | 146.8 |
| **zeroclaw** | **123** / 0 | 246.9k / 0 | 194.5k / 0 | 0 | 1 | 82.2 |
| **moltis** | **18** / 2 | 3.3k / 53 | 314 / 10 | 0 | 6 | 30.2 |
| **hermes-agent** | **819** / 1 | 156.0k / 189 | 92.3k / 5 | 66 | 1 | 732.5 |
| **nanobot** | **64** / 1 | 21.5k / 315 | 3.0k / 11 | 0 | 0 | 101.2 |
| **picoclaw** | **45** / 2 | 2.5k / 21 | 307 / 21 | 44 | 0 | 35.2 |
| **nanoclaw** | **21** / 9 | 5.8k / 17 | 4.3k / 17 | 8 | 0 | 22.8 |

---

## 🔍 Repository Breakdown

> [!NOTE]
> The contributor lists and activity metrics for each repository below are compiled according to commits from the last 7 days.

### LibreFang (`librefang/librefang`)
* **Status**: Active (Total: 27 commits [21 H / 6 B], 0 releases in the last week). Lines added/deleted: +28.1k/-23.5k (Human), +1.1k/-992 (Bot). **3 commits since installed 2026.5.31beta.16 (r44.g648356c92).**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 2 Bots):
  - **Top Humans**:
    - `Evan <suzukaze.haduki@gmail.com>` (Human): 18 commits, +27.4k/-23.5k lines
    - `Paco Navarrete <paco.j.navarrete@gmail.com>` (Human): 2 commits, +728/-48 lines
    - `Vignesh Jagadeesh <vignesh.nrfs@gmail.com>` (Human): 1 commit, +6/-1 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 5 commits, +1.1k/-985 lines
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 1 commit, +7/-7 lines
* **Note**: LibreFang is a community fork of the former `RightNow-AI/openfang` repository, which had **17,623 stars** and **2,252 forks** before going stale.
* **Recent Focus**: daemon_json surfaces error-less 4xx instead of silent success; cron enable/disable uses PUT with {enabled} body; loop-guard soft blocking with persistent block degradation; multiple dependency group updates (dashboard, next, cargo, web, docs); guard against editing a re-created worktree on a stale base; preserve tool-result content on history fold omit/parse failure; assign approved workshop skill to the creating agent; redact images for text-only models via catalog supports_vision; tolerate <think> preamble in history_fold summary parsing; stop scanning the workflow's own comments in todo-to-issue CI; creator_match filter for TaskClaimed / TaskCompleted triggers.

### ZeroClaw (`zeroclaw-labs/zeroclaw`)
* **Status**: Highly Active (Total: 123 commits [123 H / 0 B], 1 release in the last week). Lines added/deleted: +246.9k/-194.5k (Human), +0/-0 (Bot). **31 commits since installed v0.8.0-beta-2 (r86.ga486993c9).**
* **Contributors (according to last 7 days commits)** (Total: 33 Humans, 0 Bots):
  - **Top Humans**:
    - `Shane Engelman <contact@shane.gg>` (Human): 26 commits, +230.7k/-192.0k lines
    - `Dan Gilles <dfgilles@uchicago.edu>` (Human): 18 commits, +3.4k/-773 lines
    - `Alix-007 <li.long15@xydigit.com>` (Human): 11 commits, +498/-71 lines
    - `Argenis De La Rosa <theonlyhennygod@gmail.com>` (Human): 9 commits, +2.8k/-111 lines
    - `Cherilyn Buren <88433283+NiuBlibing@users.noreply.github.com>` (Human): 6 commits, +742/-62 lines
    - `Tidux <jon@borg.moe>` (Human): 5 commits, +1.0k/-841 lines
    - `rifuki <rifuki.dev@gmail.com>` (Human): 5 commits, +508/-54 lines
    - `robinDU <drbparadise@gmail.com>` (Human): 5 commits, +387/-19 lines
    - `Jason Perlow <jperlow@gmail.com>` (Human): 4 commits, +1.3k/-30 lines
    - `JordanTheJet <morepencils@gmail.com>` (Human): 4 commits, +390/-43 lines
* **Recent Focus**: update project banner; add languagetool grammar/style plugin; strip XML tool_result blocks from channel responses; isolate session state per Matrix channel alias and repair key backup; guard trim_history against orphan-cascade; preserve markdown fences when splitting Telegram messages; normalize webp images for vision; clean up docs build warnings; scope channel runtime context to the agent workspace; add sd-webui self-hosted image-gen plugin; correct Codex-subscription credential source; omit temperature on wire when unset; allow what unbounded/yolo presets advertise; restore mid-turn input in zerocode for outbound message queue; add 7 OpenAI-compatible providers under schema v3; add Twitch chat channel; print model names in models list.

### Moltis (`moltis-org/moltis`)
* **Status**: Active (Total: 20 commits [18 H / 2 B], 6 releases in the last week). Lines added/deleted: +3.3k/-314 (Human), +53/-10 (Bot). **0 commits since installed 20260603.01 (r8.g48c9a4192).**
* **Contributors (according to last 7 days commits)** (Total: 2 Humans, 1 Bots):
  - **Top Humans**:
    - `Fabien Penso <gpg@pen.so>` (Human): 17 commits, +1.4k/-83 lines
    - `Sergey Salamatov <55296341+s-salamatov@users.noreply.github.com>` (Human): 1 commit, +1.9k/-231 lines
  - **Top Bots**:
    - `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>` (Bot): 2 commits, +53/-10 lines
* **Recent Focus**: [codex] separate Telegram progress stream from final replies; show Polyphony in workflow slide; update deploy templates and releases to 20260603.01 and 20260602.05; retry empty Fireworks Kimi final turn; expand AI engineering deck examples and NFC Summit deck with personal site title additions and PDF presentation export fixes; retry transient ZAI catalog probes; restore Gemini tool signature replay.

### IronClaw (`nearai/ironclaw`)
* **Status**: Highly Active (Total: 165 commits [155 H / 10 B], 1 release in the last week). Lines added/deleted: +158.8k/-19.8k (Human), +286/-216 (Bot). **46 commits since installed ironclaw.v0.29.1 (r1211.g5364cb3).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `firat.sertgoz <firat.sertgoz@near.ai>` (Human): 84 commits, +63.5k/-9.2k lines
    - `Henry Park <henrypark133@gmail.com>` (Human): 37 commits, +44.9k/-5.5k lines
    - `Zaki Manian <zaki@iqlusion.io>` (Human): 9 commits, +18.3k/-2.6k lines
    - `jinxin <106428113+italic-jinxin@users.noreply.github.com>` (Human): 6 commits, +7.0k/-1.1k lines
    - `Robert Yan <46699230+think-in-universe@users.noreply.github.com>` (Human): 5 commits, +5.7k/-426 lines
    - `Daniel Wang <5139554+danielwpz@users.noreply.github.com>` (Human): 5 commits, +5.5k/-353 lines
    - `Coffee <zjchen1234@foxmail.com>` (Human): 3 commits, +8.0k/-290 lines
    - `Benjamin Kurrek <57506486+BenKurrek@users.noreply.github.com>` (Human): 2 commits, +271/-6 lines
    - `Illia Polosukhin <ilblackdragon@gmail.com>` (Human): 2 commits, +5.4k/-275 lines
    - `Josh Ford <thisisjoshford@gmail.com>` (Human): 1 commit, +200/-39 lines
  - **Top Bots**:
    - `IronClaw Agent <agent@ironclaw.com>` (Bot): 10 commits, +286/-216 lines
* **Recent Focus**: route Responses and chat completions through Reborn ProductWorkflow; add Reborn Railway config; fix staged credentials for MCP sessions; soften activity summary failures in codex; add Slack shared outbound targets and channel-neutral outbound target authority status; add automation run history UI and scoped outbound delivery defaults; extend ToolCall with arguments_parse_error field; planner subagent flavor + spawn_subagent schema redesign; default google-calendar list_events timeMin to now; replace outbound delivery plan; persist Slack host-beta workflow state; auto-detect Codex client_version.

### Hermes Agent (`NousResearch/hermes-agent`)
* **Status**: Highly Active (Total: 820 commits [819 H / 1 B], 66 merges, 1 release in the last week). Lines added/deleted: +156.0k/-92.3k (Human), +189/-5 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 126 Humans, 1 Bots):
  - **Top Humans**:
    - `Teknium <127238744+teknium1@users.noreply.github.com>` (Human): 176 commits, +27.0k/-16.8k lines
    - `Brooklyn Nicholson <brooklyn.bb.nicholson@gmail.com>` (Human): 124 commits, +17.4k/-6.3k lines
    - `teknium1 <127238744+teknium1@users.noreply.github.com>` (Human): 96 commits, +20.4k/-14.1k lines
    - `brooklyn! <brooklyn.bb.nicholson@gmail.com>` (Human): 31 commits, +5.8k/-2.3k lines
    - `kshitijk4poor <82637225+kshitijk4poor@users.noreply.github.com>` (Human): 26 commits, +2.5k/-485 lines
    - `xxxigm <tuancanhnguyen706@gmail.com>` (Human): 22 commits, +1.4k/-59 lines
    - `Ben Barclay <ben@nousresearch.com>` (Human): 21 commits, +2.7k/-137 lines
    - `Ben <ben@nousresearch.com>` (Human): 19 commits, +6.8k/-592 lines
    - `underthestars-zhy <zhuhaoyu0909@icloud.com>` (Human): 17 commits, +4.4k/-1.5k lines
    - `ethernet <arilotter@gmail.com>` (Human): 17 commits, +5.4k/-39.1k lines
  - **Top Bots**:
    - `Sol Aitken <solaiagent@gmail.com>` (Bot): 1 commit, +189/-5 lines
* **Recent Focus**: recover from and cover char-based output-cap overflow parsing; consolidate yuanbao media resolution into pipeline middlewares; recover session after sleep/wake desktop gateway restart; record app-server token usage in session accounting; preserve downstream errors in nemo-relay adaptive execution; cap terminal code-block preview in gateway; complete sane PATH entries on POSIX; remote-gateway file attachments via file.attach; persist Nous recommended-models to disk with Portal fallback; add laguna-m.1 and nemotron-3-ultra to curated OpenRouter list.

### NanoBot (`HKUDS/nanobot`)
* **Status**: Active (Total: 65 commits [64 H / 1 B], 0 releases in the last week). Lines added/deleted: +21.5k/-3.0k (Human), +315/-11 (Bot).
* **Contributors (according to last 7 days commits)** (Total: 16 Humans, 1 Bots):
  - **Top Humans**:
    - `chengyongru <chengyongru.ai@gmail.com>` (Human): 20 commits, +2.6k/-431 lines
    - `Xubin Ren <52506698+Re-bin@users.noreply.github.com>` (Human): 10 commits, +13.7k/-1.3k lines
    - `Flávio Veloso Soares <flaviovs@magnux.com>` (Human): 7 commits, +720/-82 lines
    - `axelray-dev <110029405+axelray-dev@users.noreply.github.com>` (Human): 7 commits, +452/-10 lines
    - `chengyongru <2755839590@qq.com>` (Human): 4 commits, +206/-12 lines
    - `Kunal Karmakar <kkdthunlshd@gmail.com>` (Human): 4 commits, +420/-34 lines
    - `chengyongru <61816729+chengyongru@users.noreply.github.com>` (Human): 2 commits, +1.7k/-959 lines
    - `04cb <0x04cb@gmail.com>` (Human): 2 commits, +28/-1 lines
    - `comadreja <comadreja@email.com>` (Human): 1 commit, +780/-113 lines
    - `Ilia Breitburg <ilya.breytburg@gmail.com>` (Human): 1 commit, +319/-18 lines
  - **Top Bots**:
    - `NanoBot <nanobot@local>` (Bot): 1 commit, +315/-11 lines
* **Recent Focus**: introduce and test postActionExpunge option and configurable post-action handling to gate broad IMAP expunge; support IMAP MOVE and UID expunge fallbacks; extract IMAP session helper; render TeX math delimiters in WebUI; improve tool call validation strictness; add AssemblyAI and Xiaomi MiMo ASR (mimo-v2.5-asr) as transcription/STT providers; support configurable STT model and OpenRouter provider.

### PicoClaw (`sipeed/picoclaw`)
* **Status**: Active (Total: 47 commits [45 H / 2 B], 44 merges, 0 releases in the last week). Lines added/deleted: +2.5k/-307 (Human), +21/-21 (Bot). **19 commits since installed 0.2.9.nightly.20260607 (7d2b0c2a).**
* **Contributors (according to last 7 days commits)** (Total: 10 Humans, 1 Bots):
  - **Top Humans**:
    - `程智超0668000959 <cheng.zhichao@xydigit.com>` (Human): 34 commits, +737/-233 lines
    - `Mauro <afjcjsbx@gmail.com>` (Human): 2 commits, +9/-9 lines
    - `afjcjsbx <afjcjsbx@gmail.com>` (Human): 2 commits, +841/-0 lines
    - `Guoguo <i@qwq.trade>` (Human): 1 commit, +0/-0 lines
    - `pancake <pancake@nopcode.org>` (Human): 1 commit, +5/-0 lines
    - `2023478 <2694762037@qq.com>` (Human): 1 commit, +43/-0 lines
    - `jp39 <jp39@gmx.com>` (Human): 1 commit, +675/-13 lines
    - `Sutra Hsing <sutrahsing@163.com>` (Human): 1 commit, +39/-1 lines
    - `Jay Shen <shenjiecode@gmail.com>` (Human): 1 commit, +38/-51 lines
    - `SebastianBoehler <27767932+SebastianBoehler@users.noreply.github.com>` (Human): 1 commit, +110/-0 lines
  - **Top Bots**:
    - `dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>` (Bot): 2 commits, +21/-21 lines
* **Recent Focus**: fix health check always returning not ready; add ok checks for type assertions (in webfetch first-hop host, subagent, spawn tools, context values, startup info, singleflight model probe); handle os.Getwd error in context builder, skills recall, and drafts; handle Telegram location messages; replace log/fmt prints with structured logger; use %w for error wrapping; add native Kagi web search provider; avoid err shadowing in feishu close check; use canonical Anthropic default model ID; check Close() error after io.Copy to writable files.

### NanoClaw (`nanocoai/nanoclaw`)
* **Status**: Active (Total: 30 commits [21 H / 9 B], 8 merges, 0 releases in the last week). Lines added/deleted: +5.8k/-4.3k (Human), +17/-17 (Bot). **4 commits since installed r1725.9edb33dd3.**
* **Contributors (according to last 7 days commits)** (Total: 3 Humans, 1 Bots):
  - **Top Humans**:
    - `gavrielc <gabicohen22@yahoo.com>` (Human): 19 commits, +5.6k/-4.3k lines
    - `Omri Maya <omri@nanoco.ai>` (Human): 1 commit, +157/-2 lines
    - `markbala <22162779+markbala@users.noreply.github.com>` (Human): 1 commit, +74/-0 lines
  - **Top Bots**:
    - `github-actions[bot] <github-actions[bot]@users.noreply.github.com>` (Bot): 9 commits, +17/-17 lines
* **Recent Focus**: bump version to 2.1.1 and release 2.1.0; update token count documentation (183k tokens, 92% context window); opt-in security egress lockdown limiting agent egress via OneCLI; prompt caching for Ollama by filtering cache-busting hash; human-addressed guidance on upgrade tripwire banner; rewrite native-credential-proxy, add-ollama-tool, and migrate-from-openclaw skills for v2; conformance cleanup for MCP-tool, capability, and provider (opencode, codex); channel-family conformance retrofit.

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

### Step 4: Batch Statistics Helper Script (Python)
To gather all required metrics, including contributor breakdowns and lines added/deleted, run the following Python script (`scratch/collect_stats.py`) from the root directory of the workspace:

```python
#!/usr/bin/env python3
"""
Python script to gather weekly development statistics for all assistant repos.
Classifies commits and line changes as Human or Bot, and lists contributor breakdowns.
"""

import subprocess
import os
from typing import Dict, Any

# Map: directory_name -> pacman package name (empty = not installed)
PKG_MAP = {
    "librefang": "librefang-git",
    "zeroclaw": "zeroclaw-git",
    "moltis": "moltis-git",
    "ironclaw": "ironclaw-git",
    "hermes-agent": "",
    "nanobot": "",
    "picoclaw": "picoclaw-git",
    "nanoclaw": "nanoclaw-git",
}

ROOT_DIR = "/home/wuxxin/agent-shared/code/agents-shared"


def is_bot(author_info: str) -> bool:
    """Check if the author is a bot/agent based on name or email patterns."""
    author_lc = author_info.lower()
    bot_patterns = [
        "[bot]",
        "github-actions",
        "dependabot",
        "renovate",
        "nanobot@local",
        "agent@ironclaw.com",
        "agent@",
    ]
    return any(pat in author_lc for pat in bot_patterns)


def format_lines(count: int) -> str:
    """Format large numbers with k/M suffixes for readability in table."""
    if count >= 1000000:
        return f"{count / 1000000:.1f}M"
    elif count >= 1000:
        return f"{count / 1000:.1f}k"
    return str(count)


def get_stats(repo_dir: str) -> Dict[str, Any]:
    """Retrieve commits, merges, line stats, tags, and installed packages."""
    full_path = os.path.join(ROOT_DIR, "scratch", repo_dir)
    if not os.path.exists(full_path):
        return {}

    # Git fetch and reset
    try:
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Get remote branch
        res = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=False,
        )
        branch = res.stdout.strip().replace("refs/remotes/origin/", "")
        if not branch:
            res = subprocess.run(
                ["git", "branch", "-r"],
                cwd=full_path,
                capture_output=True,
                text=True,
                check=False,
            )
            branches = res.stdout.split()
            if any("origin/main" in b for b in branches):
                branch = "main"
            elif any("origin/master" in b for b in branches):
                branch = "master"
            else:
                branch = "main"

        subprocess.run(
            ["git", "checkout", branch],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["git", "reset", "--hard", f"origin/{branch}"],
            cwd=full_path,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Error updating {repo_dir}: {e}")

    # Gather commits and lines
    human_commits = 0
    bot_commits = 0
    human_added = 0
    human_deleted = 0
    bot_added = 0
    bot_deleted = 0

    contributors = {}  # author_info -> {"commits": 0, "added": 0, "deleted": 0, "is_bot": bool}

    # Run git log with numstat
    try:
        cmd = [
            "git",
            "log",
            "--since=7 days ago",
            "--no-merges",
            "--numstat",
            "--pretty=format:AUTHOR: %an <%ae>",
        ]
        res = subprocess.run(
            cmd, cwd=full_path, capture_output=True, text=True, check=True
        )

        current_author = None
        current_author_is_bot = False
        for line in res.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("AUTHOR: "):
                author_info = line[8:]
                current_author = author_info
                current_author_is_bot = is_bot(author_info)
                if current_author not in contributors:
                    contributors[current_author] = {
                        "commits": 0,
                        "added": 0,
                        "deleted": 0,
                        "is_bot": current_author_is_bot,
                    }
                contributors[current_author]["commits"] += 1
                if current_author_is_bot:
                    bot_commits += 1
                else:
                    human_commits += 1
            else:
                # numstat line: added deleted filename
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    added_str, deleted_str = parts[0], parts[1]
                    added = int(added_str) if added_str.isdigit() else 0
                    deleted = int(deleted_str) if deleted_str.isdigit() else 0
                    if current_author:
                        contributors[current_author]["added"] += added
                        contributors[current_author]["deleted"] += deleted
                    if current_author_is_bot:
                        bot_added += added
                        bot_deleted += deleted
                    else:
                        human_added += added
                        human_deleted += deleted
    except Exception as e:
        print(f"Error gathering git log for {repo_dir}: {e}")

    # Merges
    merges = 0
    try:
        res = subprocess.run(
            ["git", "log", "--since=7 days ago", "--merges", "--oneline"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        merges = len(res.stdout.strip().splitlines()) if res.stdout.strip() else 0
    except Exception:
        pass

    # Last Commit Date
    last_commit = "N/A"
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        last_commit = res.stdout.strip()
    except Exception:
        pass

    # Avg Commits (4 weeks)
    avg_commits = 0.0
    try:
        res = subprocess.run(
            ["git", "log", "--since=28 days ago", "--no-merges", "--oneline"],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        count_28 = len(res.stdout.strip().splitlines()) if res.stdout.strip() else 0
        avg_commits = count_28 / 4.0
    except Exception:
        pass

    # Tags
    tags_list = []
    try:
        res = subprocess.run(
            [
                "git",
                "log",
                "--tags",
                "--since=7 days ago",
                "--simplify-by-decoration",
                "--pretty=format:%d %as",
            ],
            cwd=full_path,
            capture_output=True,
            text=True,
            check=True,
        )
        for line in res.stdout.splitlines():
            line = line.strip()
            if line:
                tags_list.append(line)
    except Exception:
        pass

    return {
        "commits": human_commits + bot_commits,
        "human_commits": human_commits,
        "bot_commits": bot_commits,
        "human_added": human_added,
        "human_deleted": human_deleted,
        "bot_added": bot_added,
        "bot_deleted": bot_deleted,
        "merges": merges,
        "last_commit": last_commit,
        "avg_commits": avg_commits,
        "tags": tags_list,
        "contributors": contributors,
    }


def main():
    for repo in PKG_MAP.keys():
        stats = get_stats(repo)
        if not stats:
            continue
        print(f"=== {repo} ===")
        print(
            f"Commits: Total={stats['commits']} (Human={stats['human_commits']}, Bot={stats['bot_commits']})"
        )
        print(
            f"Lines Added: Human={stats['human_added']} ({format_lines(stats['human_added'])}), Bot={stats['bot_added']} ({format_lines(stats['bot_added'])})"
        )
        print(
            f"Lines Deleted: Human={stats['human_deleted']} ({format_lines(stats['human_deleted'])}), Bot={stats['bot_deleted']} ({format_lines(stats['bot_deleted'])})"
        )
        print(
            f"Merges: {stats['merges']}, Last Commit: {stats['last_commit']}, Avg Commits: {stats['avg_commits']:.1f}"
        )
        print(f"Tags: {stats['tags']}")
        print("Contributors (according to last 7 days commits):")
        humans = [
            item
            for item in stats["contributors"].items()
            if not item[1]["is_bot"]
        ]
        bots = [
            item for item in stats["contributors"].items() if item[1]["is_bot"]
        ]

        # Sort descending by commits
        humans_sorted = sorted(
            humans, key=lambda x: x[1]["commits"], reverse=True
        )
        bots_sorted = sorted(bots, key=lambda x: x[1]["commits"], reverse=True)

        print(f"Total: {len(humans)} Humans, {len(bots)} Bots")
        if humans_sorted:
            print("  - Top Humans:")
            for name, info in humans_sorted[:10]:
                print(
                    f"    - `{name}` (Human): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
                )
        if bots_sorted:
            print("  - Top Bots:")
            for name, info in bots_sorted[:3]:
                print(
                    f"    - `{name}` (Bot): {info['commits']} commits, +{format_lines(info['added'])}/-{format_lines(info['deleted'])} lines"
                )
        print()


if __name__ == "__main__":
    main()
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
