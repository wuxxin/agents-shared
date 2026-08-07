#!/usr/bin/env python3
"""Automate Gemini Deep Research via Playwright, download YAML code blocks,
and merge them into a single output file.

Exit codes:
    0  — Success (download blocks retrieved).
    1  — Setup error (CLI args, prompt file, browser spawn/connect).
    2  — Pre-research error (navigation, input box, prompt entry, Deep Research
         toggle, query submission).
    3  — Plan error (waiting for / clicking plan confirmation).
    4  — Generation timeout with no data blocks at all.
"""

import argparse
import os
import random
import re
import socket
import subprocess
import sys
import time

import yaml
from playwright.sync_api import sync_playwright

#
# Exit codes
#
EXIT_OK = 0
EXIT_SETUP = 1
EXIT_PRE_RESEARCH = 2
EXIT_PLAN = 3
EXIT_NO_DATA = 4

#
# CSS selectors (element attributes, ids, structure)
#
SEL_INPUT_BOX = "div[contenteditable='true']"
SEL_INPUT_BOX_FALLBACK = "textarea"
SEL_DOWNLOAD_ICON = "button:has(mat-icon[fonticon='arrow_circle_down'])"
SEL_PLUS_MENU = "simplified-input-menu button, .leading-actions-wrapper button"
#
# Locator button texts (most robust — survives UI reshuffles)
# Both German (DE) and English (EN) variants are listed.
#
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

#
# Timeout configuration (seconds unless noted)
#
TIMEOUT_PLAN_WAIT_S = 90
TIMEOUT_DOM_IDLE_S = 120
TIMEOUT_TOTAL_GENERATION_S = 900  # 15 minutes
POLL_INTERVAL_S = 10
TIMEOUT_DOWNLOAD_MS = 20000
TIMEOUT_INPUT_WAIT_MS = 3000
TIMEOUT_SELECTOR_MS = 3000
MAX_RELOADS = 5

#
# MutationObserver JS snippet (best-effort DOM change tracking)
#
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


#
# Logging helpers — errors/warnings → stderr, info → stdout
#
def log_info(msg: str) -> None:
    print(msg, flush=True)


def log_error(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def log_warn(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr, flush=True)


#
# Session ID extraction helper
#
def check_session_id(page, current_sid: str | None) -> str | None:
    if current_sid is not None:
        return current_sid
    try:
        url = page.url
        match = re.search(r"gemini\.google\.com/app/([a-zA-Z0-9_-]+)", url)
        if match:
            sid = match.group(1)
            if sid and sid.lower() not in ["app", "live"]:
                log_info(f"Gemini Session ID: {sid}")
                return sid
    except Exception:
        pass
    return None


#
# Locator helpers
#
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
    counts = []
    for locator in (loc, aria, icon):
        try:
            counts.append(locator.count())
        except Exception:
            counts.append(0)
    return max(counts) if counts else 0


def download_blocks(page, count: int) -> list[str]:
    """Click each download button and return the file contents."""
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


#
# DOM change detection (best-effort)
#
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
        return result
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


#
# Profile / browser helpers
#
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


#
# Prompt parsing
#
def parse_prompt(file_path: str) -> str:
    if not os.path.exists(file_path):
        log_error(f"Error: Prompt file not found at {file_path}")
        sys.exit(EXIT_SETUP)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    prompt_text = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            prompt_text = parts[2].strip()

    return prompt_text


def search_and_replace(prompt_text: str, search_val: str, replace_val: str) -> str:
    """Replace occurrences of search_val with replace_val in prompt_text."""
    if not search_val:
        return prompt_text

    if search_val in prompt_text:
        log_info(
            f"Replacing search string '{search_val}' with '{replace_val}' in prompt."
        )
        return prompt_text.replace(search_val, replace_val)

    try:
        regex = re.compile(search_val)
        if regex.search(prompt_text):
            log_info(
                f"Replacing regex pattern '{search_val}' with '{replace_val}' in prompt."
            )
            return regex.sub(replace_val, prompt_text)
    except Exception:
        pass

    log_warn(f"Search string/pattern '{search_val}' not found in prompt text.")
    return prompt_text


#
# Interactive browser session
#
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


#
# Main automation flow
#
def run_automation(
    prompt_file: str,
    output_yaml: str,
    profile_name: str,
    search_val: str,
    replace_val: str,
    mode: str,
) -> None:
    is_headless = mode.lower() != "headed"
    profile_dir = get_profile_dir(profile_name)

    prompt_text = parse_prompt(prompt_file)
    prompt_text = search_and_replace(prompt_text, search_val, replace_val)

    log_info(
        f"Starting automation in {'headless' if is_headless else 'headed'} mode "
        f"using profile: {profile_dir}"
    )

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
    current_sid: str | None = None

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
                current_sid = check_session_id(page, current_sid)
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
                page.keyboard.press("Enter")
                log_info("Used Enter key fallback to submit.")

            current_sid = check_session_id(page, current_sid)

            # --- Wait for plan confirmation ---
            log_info("Waiting for Deep Research plan confirmation...")
            confirmed = False
            for _ in range(TIMEOUT_PLAN_WAIT_S):
                current_sid = check_session_id(page, current_sid)
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

            current_sid = check_session_id(page, current_sid)

            # --- Generation phase: wait for download blocks ---
            log_info("Waiting for Deep Research blocks generation...")

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
            generation_done = False
            reloads_triggered = 0

            while not generation_done:
                current_sid = check_session_id(page, current_sid)
                current_time = time.time()
                elapsed = current_time - plan_confirmed_time

                if elapsed > TIMEOUT_TOTAL_GENERATION_S:
                    log_warn(
                        f"Total generation timeout ({TIMEOUT_TOTAL_GENERATION_S}s) "
                        "reached."
                    )
                    break

                # Check for "Open" button
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
                        current_sid = check_session_id(page, current_sid)
                    except Exception as e:
                        log_error(f"Failed to click 'Open' button: {e}")

                block_count = count_download_buttons(page)
                ts = time.strftime("%H:%M:%S")
                log_info(f"[{ts}] Code blocks found: {block_count}")

                if block_count > 0:
                    log_info(
                        f"Found downloadable code block(s) ({block_count}). "
                        "Waiting 5 seconds before downloading all blocks..."
                    )
                    time.sleep(5)
                    final_count = count_download_buttons(page)
                    log_info(f"Downloading all {final_count} code block(s)...")
                    data_blocks = download_blocks(page, final_count)
                    exit_code = EXIT_OK
                    generation_done = True
                    break

                should_reload = False
                reload_reason = ""
                if check_connection_error(page):
                    should_reload = True
                    reload_reason = "Connection aborted/reload error message detected"
                else:
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
                            last_activity_time = time.time()
                            continue
                        except Exception as e:
                            log_error(f"Failed to reload page: {e}")
                    else:
                        log_error(f"Max reloads ({MAX_RELOADS}) reached. Aborting.")
                        exit_code = EXIT_NO_DATA
                        generation_done = True
                        break

                if dom_observer_active:
                    ms_idle = ms_since_last_dom_change(page)
                    if ms_idle is not None and ms_idle < POLL_INTERVAL_S * 1000:
                        last_activity_time = current_time

                time.sleep(POLL_INTERVAL_S)

            if not data_blocks:
                final_count = count_download_buttons(page)
                if final_count > 0:
                    log_warn(
                        f"Found {final_count} blocks at timeout. Downloading available blocks."
                    )
                    data_blocks = download_blocks(page, final_count)
                    exit_code = EXIT_OK

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
        log_error("Error: Generation completed with no data blocks.")
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


#
# Download command for finished research
#
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
    current_sid: str | None = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            log_info(f"Navigating to: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("domcontentloaded")
                current_sid = check_session_id(page, current_sid)
            except Exception as e:
                log_error(f"Error: Failed to navigate to {url}: {e}")
                sys.exit(EXIT_PRE_RESEARCH)

            log_info(
                "Waiting for 'Open'/'Öffnen' button or download blocks to appear..."
            )
            open_btn = None
            for _ in range(30):
                current_sid = check_session_id(page, current_sid)
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
                    current_sid = check_session_id(page, current_sid)
                except Exception as e:
                    log_error(f"Error clicking 'Open' button: {e}")
                    sys.exit(EXIT_PRE_RESEARCH)

            log_info("Waiting for download blocks to appear...")
            block_count = 0
            for _ in range(30):
                current_sid = check_session_id(page, current_sid)
                block_count = count_download_buttons(page)
                if block_count > 0:
                    break
                time.sleep(1)

            if block_count > 0:
                log_info(
                    f"Found downloadable code block(s) ({block_count}). "
                    "Waiting 5 seconds before downloading all blocks..."
                )
                time.sleep(5)
                block_count = count_download_buttons(page)

            if block_count == 0:
                log_error("Error: No download blocks found on the results page.")
                sys.exit(EXIT_NO_DATA)

            log_info(f"Found {block_count} download block(s). Downloading...")
            data_blocks = download_blocks(page, block_count)
            exit_code = EXIT_OK

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


#
# CLI entry point
#
USAGE = """
Usage:

deep-research-to-yaml.py
  browser [<profile_name>]
    Open an interactive Chromium window to log in to Gemini

  research <prompt_file> [--search "<str>"] [--replace "<str>"] [--profile <name>] [--output <path>] [--headed|--headless]
    Run automated Deep Research and download YAML blocks.

  download <url> [--profile <name>] [--output <path>] [--headed|--headless]
    Navigate to a finished research session, click Open, and download results.

Exit codes:
  0   Success — download blocks retrieved.
  1   Setup error (CLI, prompt file, browser spawn/connect).  [retryable]
  2   Pre-research error (navigation, input, Deep Research toggle, submit).  [retryable]
  3   Plan error (confirmation wait/click).  [do NOT retry]
  4   Generation timeout — no data blocks found. [do NOT retry]
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automate Gemini Deep Research via Playwright, download YAML code blocks, and merge them."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # browser command
    parser_browser = subparsers.add_parser(
        "browser", help="Open an interactive Chromium window to log in to Gemini"
    )
    parser_browser.add_argument(
        "profile",
        nargs="?",
        default="default",
        help="Profile name (default: default)",
    )

    # research command
    parser_research = subparsers.add_parser(
        "research", help="Run automated Deep Research and download YAML blocks"
    )
    parser_research.add_argument("prompt_file", help="Path to prompt file")
    parser_research.add_argument(
        "--search", default="", help="String or pattern to search in prompt"
    )
    parser_research.add_argument(
        "--replace", default="", help="Replacement string for search match"
    )
    parser_research.add_argument(
        "--profile", default="default", help="Profile name (default: default)"
    )
    parser_research.add_argument("--output", default=None, help="Output YAML file path")
    res_mode = parser_research.add_mutually_exclusive_group()
    res_mode.add_argument(
        "--headed", action="store_true", help="Run browser in headed mode"
    )
    res_mode.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode (default)"
    )

    # download command
    parser_download = subparsers.add_parser(
        "download", help="Download results from finished research URL"
    )
    parser_download.add_argument("url", help="Finished research conversation URL")
    parser_download.add_argument(
        "--profile", default="default", help="Profile name (default: default)"
    )
    parser_download.add_argument("--output", default=None, help="Output YAML file path")
    dl_mode = parser_download.add_mutually_exclusive_group()
    dl_mode.add_argument(
        "--headed", action="store_true", help="Run browser in headed mode"
    )
    dl_mode.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode (default)"
    )

    args = parser.parse_args()

    if args.command == "browser":
        run_interactive(args.profile)
    elif args.command == "research":
        prompt_file = args.prompt_file
        output_yaml = args.output
        if not output_yaml:
            base = os.path.splitext(os.path.basename(prompt_file))[0]
            output_yaml = f"{base}.yaml"
        mode = "headed" if args.headed else "headless"
        run_automation(
            prompt_file,
            output_yaml,
            args.profile,
            args.search,
            args.replace,
            mode,
        )
    elif args.command == "download":
        url = args.url
        output_yaml = args.output
        if not output_yaml:
            match = re.search(r"/app/([a-zA-Z0-9_-]+)", url)
            chat_id = match.group(1) if match else "results"
            output_yaml = f"{chat_id}.yaml"
        mode = "headed" if args.headed else "headless"
        run_download(url, output_yaml, args.profile, mode)


if __name__ == "__main__":
    main()
