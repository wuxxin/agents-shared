#!/usr/bin/env python3
"""Automate Gemini Deep Research via Playwright, download YAML code blocks,
and merge them into a single output file.

Exit codes:
    0  — Success (all expected blocks downloaded).
    1  — Setup error (CLI args, prompt file, browser spawn/connect).
    2  — Pre-research error (navigation, input box, prompt entry, Deep Research
         toggle, query submission).
    3  — Plan error (waiting for / clicking plan confirmation).
    4  — Generation timeout with no data blocks at all.
   10  — Partial data: some blocks downloaded but fewer than expected.
"""

import os
import random
import re
import socket
import subprocess
import sys
import time

import yaml
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Exit codes
# ---------------------------------------------------------------------------
EXIT_OK = 0
EXIT_SETUP = 1
EXIT_PRE_RESEARCH = 2
EXIT_PLAN = 3
EXIT_NO_DATA = 4
EXIT_PARTIAL = 10

# ---------------------------------------------------------------------------
# CSS selectors (element attributes, ids, structure)
# ---------------------------------------------------------------------------
SEL_INPUT_BOX = "div[contenteditable='true']"
SEL_INPUT_BOX_FALLBACK = "textarea"
SEL_DOWNLOAD_ICON = "button:has(mat-icon[fonticon='arrow_circle_down'])"
SEL_PLUS_MENU = "simplified-input-menu button, .leading-actions-wrapper button"
# ---------------------------------------------------------------------------
# Locator button texts (most robust — survives UI reshuffles)
# Both German (DE) and English (EN) variants are listed.
# ---------------------------------------------------------------------------
LOC_PLUS_MENU_ARIA = ["Uploads&nbsp;&amp; Tools", "Uploads & Tools"]
LOC_DEEP_RESEARCH_TEXTS = ["Deep Research"]
LOC_SEND_TEXTS = ["Send message", "Nachricht senden"]
LOC_SEND_ARIA = ["Send message", "Nachricht senden"]
LOC_PLAN_CONFIRM_TEXTS = [
    "Start research",
    "Recherche starten",
    "Confirm plan",
    "Plan bestätigen",
]
LOC_DOWNLOAD_TEXTS = ["Download code", "Code herunterladen"]
LOC_DOWNLOAD_ARIA = ["Download code", "Code herunterladen"]
LOC_OPEN_RESEARCH_TEXTS = ["Open", "Öffnen", "Open report", "Bericht öffnen"]

# ---------------------------------------------------------------------------
# Timeout configuration (seconds unless noted)
# ---------------------------------------------------------------------------
TIMEOUT_PLAN_WAIT_S = 90
TIMEOUT_DOM_IDLE_S = 120
TIMEOUT_TOTAL_GENERATION_S = 900  # 15 minutes
TIMEOUT_PARTIAL_GRACE_S = 30
POLL_INTERVAL_S = 10
TIMEOUT_DOWNLOAD_MS = 20000
TIMEOUT_INPUT_WAIT_MS = 3000
TIMEOUT_SELECTOR_MS = 3000
MAX_RELOADS = 5

# ---------------------------------------------------------------------------
# MutationObserver JS snippet (best-effort DOM change tracking)
# ---------------------------------------------------------------------------
_MUTATION_OBSERVER_INIT_JS = """
() => {
    if (window.__drLastChange !== undefined) return true;
    window.__drLastChange = Date.now();
    try {
        const target = document.querySelector(
            'main, [role="main"], .conversation-container, body'
        );
        if (!target) return false;
        const obs = new MutationObserver(() => {
            window.__drLastChange = Date.now();
        });
        obs.observe(target, {childList: true, subtree: true, characterData: true});
        return true;
    } catch(e) {
        return false;
    }
}
"""

_MUTATION_OBSERVER_QUERY_JS = """
() => {
    if (window.__drLastChange === undefined) return null;
    return Date.now() - window.__drLastChange;
}
"""


# ---------------------------------------------------------------------------
# Logging helpers — errors/warnings → stderr, info → stdout
# ---------------------------------------------------------------------------
def log_info(msg: str) -> None:
    print(msg, flush=True)


def log_error(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def log_warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Locator helpers
# ---------------------------------------------------------------------------
def _build_text_locator(page, texts: list[str], tag: str = "button"):
    """Return a Playwright Locator matching the first visible element whose
    text content matches one of *texts*.  Tries each text in order."""
    parts = [f"{tag}:has-text('{t}')" for t in texts]
    return page.locator(", ".join(parts))


def _build_aria_locator(page, labels: list[str], tag: str = "button"):
    """Return a Playwright Locator matching aria-label variants."""
    parts = [f"{tag}[aria-label='{label}']" for label in labels]
    return page.locator(", ".join(parts))


def find_button(
    page,
    *,
    texts: list[str] | None = None,
    aria_labels: list[str] | None = None,
    extra_selector: str | None = None,
):
    """Try to find a button using multiple strategies, most-robust first.

    Priority: button text → aria-label → extra CSS selector.
    Returns the first Locator with count() > 0, or ``None``.
    """
    strategies: list = []
    if texts:
        strategies.append(_build_text_locator(page, texts))
    if aria_labels:
        strategies.append(_build_aria_locator(page, aria_labels))
    if extra_selector:
        strategies.append(page.locator(extra_selector))

    for loc in strategies:
        try:
            if loc.first.count() > 0:
                return loc.first
        except Exception:
            continue
    return None


def count_download_buttons(page) -> int:
    """Return the number of visible code-download buttons on the page."""
    loc = _build_text_locator(page, LOC_DOWNLOAD_TEXTS)
    aria = _build_aria_locator(page, LOC_DOWNLOAD_ARIA)
    icon = page.locator(SEL_DOWNLOAD_ICON)
    # Take the highest count across strategies
    counts = []
    for locator in (loc, aria, icon):
        try:
            counts.append(locator.count())
        except Exception:
            counts.append(0)
    return max(counts) if counts else 0


def download_blocks(page, count: int) -> list[str]:
    """Click each download button and return the file contents."""
    # Build a composite locator and prefer whichever strategy found them
    loc = _build_text_locator(page, LOC_DOWNLOAD_TEXTS)
    aria = _build_aria_locator(page, LOC_DOWNLOAD_ARIA)
    icon = page.locator(SEL_DOWNLOAD_ICON)

    best_loc = loc
    best_count = 0
    for locator in (loc, aria, icon):
        try:
            c = locator.count()
            if c > best_count:
                best_count = c
                best_loc = locator
        except Exception:
            pass

    blocks: list[str] = []
    for i in range(min(count, best_count)):
        btn = best_loc.nth(i)
        try:
            with page.expect_download(timeout=TIMEOUT_DOWNLOAD_MS) as dl_info:
                btn.click()
            download = dl_info.value
            yaml_path = download.path()
            with open(yaml_path, "r", encoding="utf-8") as f:
                blocks.append(f.read())
            log_info(f"Block {i + 1} downloaded successfully.")
        except Exception as e:
            log_error(f"Block {i + 1} download failed: {e}")
    return blocks


# ---------------------------------------------------------------------------
# DOM change detection (best-effort)
# ---------------------------------------------------------------------------
def init_dom_observer(page) -> bool:
    """Inject a MutationObserver. Returns True on success."""
    try:
        return bool(page.evaluate(_MUTATION_OBSERVER_INIT_JS))
    except Exception:
        return False


def ms_since_last_dom_change(page) -> int | None:
    """Milliseconds since the last DOM mutation, or None if observer not active."""
    try:
        result = page.evaluate(_MUTATION_OBSERVER_QUERY_JS)
        return result  # int or None
    except Exception:
        return None


def check_connection_error(page) -> bool:
    """Check if the page is showing a connection error or reload suggestion."""
    try:
        body_text = page.locator("body").text_content() or ""
        err_phrases = [
            "connection aborted",
            "verbindung abgebrochen",
            "verbindung unterbrochen",
            "reload page",
            "seite neu laden",
        ]
        body_lower = body_text.lower()
        for phrase in err_phrases:
            if phrase in body_lower:
                return True
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Profile / browser helpers
# ---------------------------------------------------------------------------
def get_profile_dir(profile_name: str) -> str:
    if os.path.isabs(profile_name) or "/" in profile_name:
        return os.path.abspath(profile_name)
    base_dir = os.path.expanduser("~/.config/deep-research-profiles")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, profile_name)


def get_chromium_binary() -> str | None:
    for binary in ["chromium", "google-chrome", "chromium-browser"]:
        try:
            subprocess.run(
                [binary, "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return binary
        except FileNotFoundError:
            continue
    return None


def get_free_port() -> int:
    while True:
        port = random.randint(9000, 9999)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue


# ---------------------------------------------------------------------------
# Prompt parsing
# ---------------------------------------------------------------------------
def parse_prompt(file_path: str) -> tuple[dict, str]:
    if not os.path.exists(file_path):
        log_error(f"Error: Prompt file not found at {file_path}")
        sys.exit(EXIT_SETUP)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter: dict = {}
    prompt_text = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                prompt_text = parts[2].strip()
            except Exception as e:
                log_error(f"Error parsing frontmatter: {e}")

    return frontmatter, prompt_text


def search_and_replace(frontmatter: dict, prompt_text: str, search_value: str) -> str:
    """Replace the first line matching ``search_identifier`` with *search_value*.

    The ``search_identifier`` frontmatter key is treated as a regex.  This is
    intentionally generic so it can be used for date injection, region swaps,
    or any other dynamic prompt substitution.
    """
    identifier = frontmatter.get("search_identifier")
    if not identifier or not search_value:
        return prompt_text

    try:
        regex = re.compile(identifier)
    except Exception as e:
        log_error(f"Error compiling search_identifier regex '{identifier}': {e}")
        regex = None

    lines = prompt_text.splitlines()
    for idx, line in enumerate(lines):
        if (regex and regex.search(line)) or (not regex and identifier in line):
            lines[idx] = search_value
            log_info(f"Replaced criteria line: '{line}' -> '{lines[idx]}'")
            break

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Interactive browser session
# ---------------------------------------------------------------------------
def run_interactive(profile_name: str) -> None:
    """Launch a headed Chromium window for manual Gemini login.

    We spawn a *real* Chromium process (not Playwright's bundled browser) with
    ``--user-data-dir`` pointing at a persistent profile directory.  This is
    necessary because:

    1. Gemini requires a Google login which typically involves MFA/2FA prompts
       that cannot be automated.
    2. The ``--user-data-dir`` flag stores cookies, localStorage, and session
       tokens on disk so they survive between runs.
    3. The later ``research`` command re-uses the *same* ``--user-data-dir``
       so the saved login session carries over to the headless automation run
       without requiring a fresh login.
    """
    profile_dir = get_profile_dir(profile_name)
    log_info(
        f"Opening interactive browser window using profile directory: {profile_dir}"
    )
    log_info(
        "Please log in to Gemini and then close the browser window to save the session."
    )

    binary = get_chromium_binary()
    if not binary:
        log_error(
            "Error: 'chromium', 'google-chrome', or 'chromium-browser' not found "
            "on PATH. Please ensure Chromium or Google Chrome is installed."
        )
        sys.exit(EXIT_SETUP)

    cmd = [
        binary,
        "--app=https://gemini.google.com/",
        f"--user-data-dir={profile_dir}",
    ]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        log_info("\nSession saved.")


# ---------------------------------------------------------------------------
# Main automation flow
# ---------------------------------------------------------------------------
def run_automation(
    prompt_file: str,
    output_yaml: str,
    profile_name: str,
    search_value: str,
    mode: str,
) -> None:
    is_headless = mode.lower() != "headed"
    profile_dir = get_profile_dir(profile_name)

    frontmatter, prompt_text = parse_prompt(prompt_file)
    prompt_text = search_and_replace(frontmatter, prompt_text, search_value)

    expected_blocks = frontmatter.get("data_blocks", 1)

    log_info(
        f"Starting automation in {'headless' if is_headless else 'headed'} mode "
        f"using profile: {profile_dir}"
    )
    log_info(f"Expecting {expected_blocks} data blocks.")

    # --- Spawn browser ---
    # We spawn a real Chromium process with --user-data-dir pointing at the
    # same profile directory used by the interactive ``browser`` command.
    # This re-uses the saved Google login session (cookies, localStorage).
    # Playwright connects to it over CDP (Chrome DevTools Protocol) via
    # --remote-debugging-port rather than launching its own browser, which
    # would not have the login session.
    binary = get_chromium_binary()
    if not binary:
        log_error(
            "Error: 'chromium', 'google-chrome', or 'chromium-browser' not found "
            "on PATH."
        )
        sys.exit(EXIT_SETUP)

    port = get_free_port()
    cmd = [
        binary,
        "--app=https://gemini.google.com/",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
    ]
    if is_headless:
        cmd.append("--headless=new")
    else:
        cmd.extend(["--no-first-run", "--no-default-browser-check"])

    log_info(f"Spawning browser on port {port}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Wait for debugging port
    connected = False
    for _ in range(50):
        if proc.poll() is not None:
            break
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            try:
                s.connect(("127.0.0.1", port))
                connected = True
                break
            except OSError:
                time.sleep(0.1)

    if not connected:
        log_error("Error: Failed to start Chromium with remote debugging enabled.")
        proc.terminate()
        sys.exit(EXIT_SETUP)

    data_blocks: list[str] = []
    exit_code = EXIT_NO_DATA

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            # --- Navigate to Gemini ---
            log_info("Navigating to Gemini...")
            try:
                page.goto("https://gemini.google.com/app")
                page.wait_for_load_state("domcontentloaded")
            except Exception as e:
                log_error(f"Error: Failed to navigate to Gemini: {e}")
                sys.exit(EXIT_PRE_RESEARCH)

            # --- Find input box ---
            input_box = None
            for sel in [SEL_INPUT_BOX, SEL_INPUT_BOX_FALLBACK]:
                try:
                    el = page.wait_for_selector(sel, timeout=TIMEOUT_INPUT_WAIT_MS)
                    if el:
                        input_box = el
                        break
                except Exception:
                    continue

            if not input_box:
                log_error(
                    "Error: Could not find Gemini's input box. "
                    "Ensure you are logged in using browser mode."
                )
                sys.exit(EXIT_PRE_RESEARCH)

            # --- Type prompt ---
            log_info("Clearing and typing the prompt...")
            try:
                input_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                input_box.fill(prompt_text)
            except Exception as e:
                log_error(f"Error: Failed to type prompt: {e}")
                sys.exit(EXIT_PRE_RESEARCH)

            # --- Enable Deep Research ---
            log_info("Enabling Deep Research...")
            activated = False
            try:
                log_info("Clicking '+' Button")
                plus_btn = find_button(
                    page,
                    extra_selector=SEL_PLUS_MENU,
                    aria_labels=LOC_PLUS_MENU_ARIA,
                )
                if plus_btn:
                    plus_btn.click()
                    time.sleep(1)

                    log_info("Clicking Deep-Research Button")
                    dr_opt = find_button(
                        page,
                        texts=LOC_DEEP_RESEARCH_TEXTS,
                    )
                    if not dr_opt:
                        # Also try span/list-item text matches
                        dr_opt = page.locator(
                            ", ".join(
                                f"span:has-text('{t}')" for t in LOC_DEEP_RESEARCH_TEXTS
                            )
                        ).first
                        if dr_opt.count() == 0:
                            dr_opt = None

                    if dr_opt:
                        dr_opt.click()
                        activated = True
                        log_info("Successfully activated Deep Research!")
                    else:
                        # Close menu if DR option not found
                        plus_btn.click()
            except Exception as e:
                log_error(f"Error activating Deep Research: {e}")

            if not activated:
                log_error(
                    "Error: Failed to activate Deep Research. "
                    "Make sure you are logged in and it is available for your account."
                )
                sys.exit(EXIT_PRE_RESEARCH)

            # --- Submit query ---
            log_info("Submitting query...")
            submitted = False
            send_btn = find_button(
                page,
                texts=LOC_SEND_TEXTS,
                aria_labels=LOC_SEND_ARIA,
            )
            if send_btn:
                try:
                    if send_btn.is_enabled():
                        send_btn.click()
                        submitted = True
                except Exception:
                    pass

            if not submitted:
                # Fallback: press Enter
                page.keyboard.press("Enter")
                log_info("Used Enter key fallback to submit.")

            # --- Wait for plan confirmation ---
            log_info("Waiting for Deep Research plan confirmation...")
            confirmed = False
            for _ in range(TIMEOUT_PLAN_WAIT_S):
                confirm_btn = find_button(page, texts=LOC_PLAN_CONFIRM_TEXTS)
                if confirm_btn:
                    log_info("Clicking plan confirmation...")
                    try:
                        confirm_btn.click()
                        confirmed = True
                        break
                    except Exception as e:
                        log_error(f"Plan confirmation click failed: {e}")
                time.sleep(1)

            if not confirmed:
                log_error(
                    "Error: Plan confirmation button did not appear within "
                    f"{TIMEOUT_PLAN_WAIT_S}s. Aborting."
                )
                sys.exit(EXIT_PLAN)

            # --- Generation phase: wait for download blocks ---
            log_info("Waiting for Deep Research blocks generation...")

            # Initialize DOM observer (best-effort)
            dom_observer_active = init_dom_observer(page)
            if dom_observer_active:
                log_info("DOM change observer initialized.")
            else:
                log_warn(
                    "DOM change observer could not be initialized. "
                    "Falling back to total timeout."
                )

            plan_confirmed_time = time.time()
            last_activity_time = time.time()
            last_block_count = 0
            generation_done = False
            have_partial = False
            reloads_triggered = 0

            while not generation_done:
                current_time = time.time()
                elapsed = current_time - plan_confirmed_time

                # --- Total timeout (15 min) ---
                if elapsed > TIMEOUT_TOTAL_GENERATION_S:
                    log_warn(
                        f"Total generation timeout ({TIMEOUT_TOTAL_GENERATION_S}s) "
                        "reached."
                    )
                    break

                # --- Check for "Open" button if we are not in results view yet ---
                open_btn = find_button(page, texts=LOC_OPEN_RESEARCH_TEXTS)
                if open_btn:
                    log_info(
                        "Found 'Open' research button. Clicking it to access results view..."
                    )
                    try:
                        new_page = None
                        try:
                            with context.expect_page(timeout=3000) as new_page_info:
                                open_btn.click()
                            new_page = new_page_info.value
                            log_info("Opened research results in a new tab.")
                        except Exception:
                            pass

                        if new_page:
                            page = new_page
                            page.wait_for_load_state("domcontentloaded")
                        else:
                            time.sleep(3)

                        dom_observer_active = init_dom_observer(page)
                        last_activity_time = time.time()
                    except Exception as e:
                        log_error(f"Failed to click 'Open' button: {e}")

                # --- Count download blocks ---
                block_count = count_download_buttons(page)
                ts = time.strftime("%H:%M:%S")
                log_info(f"[{ts}] Code blocks found: {block_count}/{expected_blocks}")

                # --- Check for connection error or DOM idle reload ---
                should_reload = False
                reload_reason = ""
                if check_connection_error(page):
                    should_reload = True
                    reload_reason = "Connection aborted/reload error message detected"
                elif block_count == 0:
                    idle_s = current_time - last_activity_time
                    if dom_observer_active and idle_s > TIMEOUT_DOM_IDLE_S:
                        should_reload = True
                        reload_reason = (
                            f"No download blocks and DOM idle for {idle_s:.0f}s"
                        )

                if should_reload:
                    if reloads_triggered < MAX_RELOADS:
                        reloads_triggered += 1
                        log_warn(
                            f"{reload_reason}. Triggering page reload ({reloads_triggered}/{MAX_RELOADS})..."
                        )
                        try:
                            page.reload()
                            page.wait_for_load_state("domcontentloaded")
                            time.sleep(3)
                            dom_observer_active = init_dom_observer(page)
                            if dom_observer_active:
                                log_info(
                                    "DOM change observer re-initialized after reload."
                                )
                            last_activity_time = time.time()
                            continue
                        except Exception as e:
                            log_error(f"Failed to reload page: {e}")
                    else:
                        log_error(f"Max reloads ({MAX_RELOADS}) reached. Aborting.")
                        exit_code = EXIT_NO_DATA
                        generation_done = True
                        break

                # Track activity: new blocks = activity
                if block_count != last_block_count:
                    last_activity_time = current_time
                    last_block_count = block_count

                # Track activity: DOM changes
                if dom_observer_active:
                    ms_idle = ms_since_last_dom_change(page)
                    if ms_idle is not None and ms_idle < POLL_INTERVAL_S * 1000:
                        last_activity_time = current_time

                # --- All expected blocks found → immediate download ---
                if block_count >= expected_blocks:
                    log_info(
                        f"All {expected_blocks} blocks found. Commencing download..."
                    )
                    data_blocks = download_blocks(page, expected_blocks)
                    exit_code = EXIT_OK
                    generation_done = True
                    break

                # --- Have some blocks: check partial grace ---
                if block_count > 0:
                    idle_s = current_time - last_activity_time

                    if dom_observer_active:
                        # Use DOM idle for grace
                        if idle_s > TIMEOUT_PARTIAL_GRACE_S:
                            log_warn(
                                f"Only {block_count}/{expected_blocks} blocks found "
                                f"and {idle_s:.0f}s idle. "
                                "Downloading available blocks."
                            )
                            data_blocks = download_blocks(page, block_count)
                            exit_code = EXIT_PARTIAL
                            have_partial = True
                            generation_done = True
                            break
                    else:
                        # No DOM observer: use time since last new block
                        if idle_s > TIMEOUT_PARTIAL_GRACE_S:
                            log_warn(
                                f"Only {block_count}/{expected_blocks} blocks found "
                                f"and {idle_s:.0f}s since last new block. "
                                "Downloading available blocks."
                            )
                            data_blocks = download_blocks(page, block_count)
                            exit_code = EXIT_PARTIAL
                            have_partial = True
                            generation_done = True
                            break

                else:
                    # No blocks yet: check DOM idle timeout
                    idle_s = current_time - last_activity_time
                    if dom_observer_active:
                        if idle_s > TIMEOUT_DOM_IDLE_S:
                            log_error(
                                f"No download blocks found and DOM idle for "
                                f"{idle_s:.0f}s. Aborting."
                            )
                            exit_code = EXIT_NO_DATA
                            generation_done = True
                            break
                    # Without DOM observer: just keep waiting until total timeout

                time.sleep(POLL_INTERVAL_S)

            # If we exited the loop without downloading anything
            if not data_blocks and not have_partial:
                # One last check for blocks
                final_count = count_download_buttons(page)
                if final_count > 0:
                    log_warn(
                        f"Found {final_count} blocks at timeout. "
                        "Downloading available blocks."
                    )
                    data_blocks = download_blocks(page, final_count)
                    exit_code = (
                        EXIT_OK if final_count >= expected_blocks else EXIT_PARTIAL
                    )

    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    # --- No data at all ---
    if not data_blocks:
        log_error("Error: Generation completed with no data blocks.")
        sys.exit(EXIT_NO_DATA)

    # --- Concatenate data blocks ---
    # Blocks are simply appended as raw text, separated by newlines.  No YAML
    # parsing or structural merging is performed.  This keeps the script
    # format-agnostic: it works as long as the prompt instructs Gemini to
    # emit blocks whose content can be concatenated (e.g. YAML dicts with
    # non-overlapping top-level keys like ``report:``, ``data_01:``,
    # ``data_02:``).  The caller is responsible for designing prompts
    # accordingly.
    log_info(f"Concatenating {len(data_blocks)} data blocks...")
    parts: list[str] = []
    for block in data_blocks:
        text = block if block.endswith("\n") else block + "\n"
        parts.append(text)
    combined = "".join(parts)

    with open(output_yaml, "w", encoding="utf-8") as f:
        f.write(combined)

    log_info(f"Successfully saved combined output to: {output_yaml}")

    if exit_code == EXIT_PARTIAL:
        log_warn(
            f"Only {len(data_blocks)}/{expected_blocks} blocks were downloaded. "
            "Some data may be missing."
        )

    sys.exit(exit_code)


# ---------------------------------------------------------------------------
# Download command for finished research
# ---------------------------------------------------------------------------
def run_download(
    url: str,
    output_yaml: str,
    profile_name: str,
    mode: str,
) -> None:
    """Navigate to a finished research session, click Open, and download results."""
    is_headless = mode.lower() != "headed"
    profile_dir = get_profile_dir(profile_name)

    log_info(
        f"Starting download automation in {'headless' if is_headless else 'headed'} mode "
        f"using profile: {profile_dir}"
    )
    log_info(f"Target URL: {url}")

    binary = get_chromium_binary()
    if not binary:
        log_error(
            "Error: 'chromium', 'google-chrome', or 'chromium-browser' not found on PATH."
        )
        sys.exit(EXIT_SETUP)

    port = get_free_port()
    cmd = [
        binary,
        f"--app={url}",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
    ]
    if is_headless:
        cmd.append("--headless=new")
    else:
        cmd.extend(["--no-first-run", "--no-default-browser-check"])

    log_info(f"Spawning browser on port {port}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    connected = False
    for _ in range(50):
        if proc.poll() is not None:
            break
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            try:
                s.connect(("127.0.0.1", port))
                connected = True
                break
            except OSError:
                time.sleep(0.1)

    if not connected:
        log_error("Error: Failed to start Chromium with remote debugging enabled.")
        proc.terminate()
        sys.exit(EXIT_SETUP)

    data_blocks: list[str] = []
    exit_code = EXIT_NO_DATA

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            log_info(f"Navigating to: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
            except Exception as e:
                log_error(f"Error: Failed to navigate to {url}: {e}")
                sys.exit(EXIT_PRE_RESEARCH)

            # Wait for "Open" button or download buttons
            log_info(
                "Waiting for 'Open'/'Öffnen' button or download blocks to appear..."
            )
            open_btn = None
            for _ in range(30):
                if count_download_buttons(page) > 0:
                    log_info(
                        "Download blocks are already visible, skipping 'Open' button click."
                    )
                    break
                open_btn = find_button(page, texts=LOC_OPEN_RESEARCH_TEXTS)
                if open_btn:
                    break
                time.sleep(1)

            if open_btn:
                log_info("Found 'Open' research button. Clicking it...")
                try:
                    new_page = None
                    try:
                        with context.expect_page(timeout=3000) as new_page_info:
                            open_btn.click()
                        new_page = new_page_info.value
                        log_info("Opened research results in a new tab.")
                    except Exception:
                        pass

                    if new_page:
                        page = new_page
                        page.wait_for_load_state("domcontentloaded")
                    else:
                        time.sleep(3)
                except Exception as e:
                    log_error(f"Error clicking 'Open' button: {e}")
                    sys.exit(EXIT_PRE_RESEARCH)

            # Now wait for download blocks
            log_info("Waiting for download blocks to appear...")
            block_count = 0
            for _ in range(30):
                block_count = count_download_buttons(page)
                if block_count > 0:
                    break
                time.sleep(1)

            if block_count > 0:
                time.sleep(2)  # Let any other buttons render
                block_count = count_download_buttons(page)

            if block_count == 0:
                log_error("Error: No download blocks found on the results page.")
                sys.exit(EXIT_NO_DATA)

            log_info(f"Found {block_count} download block(s). Downloading...")
            data_blocks = download_blocks(page, block_count)
            if len(data_blocks) == block_count:
                exit_code = EXIT_OK
            else:
                exit_code = EXIT_PARTIAL

    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    if not data_blocks:
        log_error("Error: Download completed with no data blocks.")
        sys.exit(EXIT_NO_DATA)

    log_info(f"Concatenating {len(data_blocks)} data blocks...")
    parts: list[str] = []
    for block in data_blocks:
        text = block if block.endswith("\n") else block + "\n"
        parts.append(text)
    combined = "".join(parts)

    with open(output_yaml, "w", encoding="utf-8") as f:
        f.write(combined)

    log_info(f"Successfully saved combined output to: {output_yaml}")
    sys.exit(exit_code)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
USAGE = """
Usage:

deep-research-to-yaml.py
  browser [<profile_name>]
    Open an interactive Chromium window to log in to Gemini

  research <prompt_file> [search="..."] [profile=...] [output=...] [headed|headless]
    Run automated Deep Research and download YAML blocks.

  download <url> [profile=...] [output=...] [headed|headless]
    Navigate to a finished research session, click Open, and download results.

Exit codes:
  0   Success — all expected blocks downloaded.
  1   Setup error (CLI, prompt file, browser spawn/connect).  [retryable]
  2   Pre-research error (navigation, input, Deep Research toggle, submit).  [retryable]
  3   Plan error (confirmation wait/click).  [do NOT retry]
  4   Generation timeout — no data blocks found. [do NOT retry]
  10  Partial data — some blocks downloaded but fewer than expected.  [do NOT retry]

Retry guidance for automated callers:
  Exit 1-2  may be analysed and retried (no quota consumed).
  Exit >= 3 must NEVER be retried automatically.
  Exit 3    may indicate the current session is blocked for deep-research by Google.
  Exit 4    Deep Research quota has been consumed or other Deep Research error while researching (eg.abort,timeout)
  Exit 10   partial output is written; inform the user about missing data.
"""


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1].lower() in [
        "help",
        "[help]",
        "-h",
        "--help",
    ]:
        print(USAGE)
        sys.exit(EXIT_OK)

    cmd = sys.argv[1].lower()

    if cmd == "browser":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else "default"
        run_interactive(profile_name)
    elif cmd == "research":
        if len(sys.argv) < 3:
            log_error("Error: Missing prompt file for research command.")
            print(USAGE)
            sys.exit(EXIT_SETUP)
        prompt_file = sys.argv[2]

        kwargs: dict[str, str] = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, val = arg.split("=", 1)
                kwargs[key.strip().lower()] = val.strip()
            else:
                val = arg.strip().lower()
                if val in ["headed", "headless"]:
                    kwargs["mode"] = val

        search_value = kwargs.get("search", "")
        profile_name = kwargs.get("profile", "default")
        output_yaml = kwargs.get("output")
        if not output_yaml:
            base = os.path.splitext(os.path.basename(prompt_file))[0]
            output_yaml = f"{base}.yaml"

        mode = kwargs.get("mode", "headless")
        run_automation(prompt_file, output_yaml, profile_name, search_value, mode)

    elif cmd == "download":
        if len(sys.argv) < 3:
            log_error("Error: Missing URL for download command.")
            print(USAGE)
            sys.exit(EXIT_SETUP)
        url = sys.argv[2]

        kwargs: dict[str, str] = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, val = arg.split("=", 1)
                kwargs[key.strip().lower()] = val.strip()
            else:
                val = arg.strip().lower()
                if val in ["headed", "headless"]:
                    kwargs["mode"] = val

        profile_name = kwargs.get("profile", "default")
        output_yaml = kwargs.get("output")
        if not output_yaml:
            match = re.search(r"/app/([a-zA-Z0-9_-]+)", url)
            chat_id = match.group(1) if match else "results"
            output_yaml = f"{chat_id}.yaml"

        mode = kwargs.get("mode", "headless")
        run_download(url, output_yaml, profile_name, mode)

    else:
        log_error(f"Error: Unknown command: {cmd}")
        sys.exit(EXIT_SETUP)


if __name__ == "__main__":
    main()
