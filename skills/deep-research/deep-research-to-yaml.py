#!/usr/bin/env python

import os
import random
import re
import socket
import subprocess
import sys
import time

import yaml
from playwright.sync_api import sync_playwright


def get_profile_dir(profile_name):
    if os.path.isabs(profile_name) or "/" in profile_name:
        return os.path.abspath(profile_name)
    base_dir = os.path.expanduser("~/.config/deep-research-profiles")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, profile_name)


def get_chromium_binary():
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


def get_free_port():
    while True:
        port = random.randint(9000, 9999)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue


def parse_prompt(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Prompt file not found at {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    frontmatter = {}
    prompt_text = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                prompt_text = parts[2].strip()
            except Exception as e:
                print(f"Error parsing frontmatter: {e}")

    return frontmatter, prompt_text


def replace_dates(frontmatter, prompt_text, search_value):
    identifier = frontmatter.get("search_identifier")
    if not identifier or not search_value:
        return prompt_text

    try:
        regex = re.compile(identifier)
    except Exception as e:
        print(f"Error compiling search_identifier regex '{identifier}': {e}")
        regex = None

    lines = prompt_text.splitlines()
    for idx, line in enumerate(lines):
        if (regex and regex.search(line)) or (not regex and identifier in line):
            lines[idx] = search_value
            print(f"Replaced criteria line: '{line}' -> '{lines[idx]}'")
            break

    return "\n".join(lines)


def run_interactive(profile_name):
    profile_dir = get_profile_dir(profile_name)
    print(f"Opening interactive browser window using profile directory: {profile_dir}")
    print(
        "Please log in to Gemini and then close the browser window to save the session."
    )

    binary = get_chromium_binary()
    if not binary:
        print(
            "Error: 'chromium', 'google-chrome', or 'chromium-browser' command not found on PATH. Please ensure Chromium or Google Chrome is installed."
        )
        sys.exit(1)

    cmd = [
        binary,
        "--app=https://gemini.google.com/",
        f"--user-data-dir={profile_dir}",
    ]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nSession saved.")


def run_automation(prompt_file, output_yaml, profile_name, search_value, mode):
    is_headless = mode.lower() != "headed"
    profile_dir = get_profile_dir(profile_name)

    frontmatter, prompt_text = parse_prompt(prompt_file)
    prompt_text = replace_dates(frontmatter, prompt_text, search_value)

    expected_blocks = frontmatter.get("data_blocks", 1)
    report_received = False
    report_aborted = False

    print(
        f"Starting automation in {'headless' if is_headless else 'headed'} mode using profile: {profile_dir}"
    )
    print(f"Expecting {expected_blocks} YAML data blocks.")

    binary = get_chromium_binary()
    if not binary:
        print(
            "Error: 'chromium', 'google-chrome', or 'chromium-browser' command not found on PATH. Please ensure Chromium or Google Chrome is installed."
        )
        sys.exit(1)

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

    # cmd.extend(["--no-sandbox", "--disable-setuid-sandbox"])

    print(f"Spawning browser on port {port}...")
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
        print("Error: Failed to start Chromium with remote debugging enabled.")
        proc.terminate()
        sys.exit(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()

            print("Navigating to Gemini...")
            page.goto("https://gemini.google.com/app")
            page.wait_for_load_state("domcontentloaded")

            # Locate input box
            input_selectors = [
                "div[contenteditable='true']",
                "textarea",
                ".input-area",
                "g-textarea-input",
            ]
            input_box = None
            for sel in input_selectors:
                try:
                    el = page.wait_for_selector(sel, timeout=3000)
                    if el:
                        input_box = el
                        break
                except Exception:
                    continue

            if not input_box:
                print(
                    "Error: Could not find Gemini's input box. Ensure you are logged in using browser mode."
                )
                report_aborted = True

            if not report_aborted:
                print("Clearing and typing the prompt...")
                input_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                input_box.fill(prompt_text)

                # Enable Deep Research toggle
                print("Enabling Deep Research...")
                activated = False
                try:
                    plus_btn = page.locator(
                        "simplified-input-menu button, .leading-actions-wrapper button, button[aria-label*='Add'], button[aria-label*='Hinzufügen']"
                    ).first
                    if plus_btn.count() > 0:
                        plus_btn.click()
                        time.sleep(1)
                        deep_research_opt = page.locator(
                            "span:has-text('Deep Research'), .mat-mdc-list-item-unscoped-content:has-text('Deep Research'), .list-item-title-text:has-text('Deep Research')"
                        ).first
                        if deep_research_opt.count() > 0:
                            deep_research_opt.click()
                            activated = True
                            print("Successfully activated Deep Research!")
                        else:
                            plus_btn.click()
                except Exception as e:
                    print(f"Toggle error: {e}")

                if not activated:
                    print(
                        "Failed to activate Deep Research. Make sure you are logged in, and it is available for your account."
                    )
                    report_aborted = True

            if not report_aborted:
                print("Submitting query...")
                send_btn_selectors = [
                    "button[aria-label='Send message']",
                    "button[aria-label='Nachricht senden']",
                    "button.send-button",
                ]
                submitted = False
                for btn_sel in send_btn_selectors:
                    try:
                        btn = page.locator(btn_sel)
                        if btn.count() > 0 and btn.is_enabled():
                            btn.click()
                            submitted = True
                            break
                    except Exception:
                        pass
                if not submitted:
                    page.keyboard.press("Enter")

                # Wait for plan confirmation
                print("Waiting for Deep Research plan confirmation...")
                confirmed = False
                for _ in range(90):
                    start_btn = page.locator(
                        "button:has-text('Recherche starten'), button:has-text('Start research'), button:has-text('Plan bestätigen'), button:has-text('Confirm plan')"
                    )
                    if start_btn.count() > 0:
                        print("Clicking plan confirmation...")
                        try:
                            start_btn.first.click()
                            confirmed = True
                            break
                        except Exception as e:
                            print(f"Click failed: {e}")
                    time.sleep(1)

                if not confirmed:
                    print("Error: Plan confirmation button did not appear. Aborting.")
                    report_aborted = True

            if not report_aborted:
                # Wait for downloads
                print("Waiting for Deep Research blocks generation...")
                yaml_blocks = []
                while True:
                    download_btn = page.locator(
                        "button[aria-label='Code herunterladen'], button[aria-label='Download code'], button:has(mat-icon[fonticon='arrow_circle_down'])"
                    )
                    count = download_btn.count()
                    print(
                        f"[{time.strftime('%H:%M:%S')}] Code blocks found: {count}/{expected_blocks}"
                    )

                    if count >= expected_blocks:
                        print(
                            f"All {expected_blocks} blocks found. Commencing download..."
                        )
                        for i in range(expected_blocks):
                            btn = download_btn.nth(i)
                            try:
                                with page.expect_download(
                                    timeout=20000
                                ) as download_info:
                                    btn.click()
                                download = download_info.value
                                yaml_path = download.path()
                                with open(yaml_path, "r", encoding="utf-8") as f:
                                    yaml_blocks.append(f.read())
                                print(f"Block {i + 1} downloaded successfully.")
                            except Exception as e:
                                print(f"Block {i + 1} download failed: {e}")
                        report_received = True
                        break

                    generating_indicators = page.locator(
                        ".generating, .progress-bar, button[aria-label='Stop generation'], button[aria-label='Generierung abbrechen']"
                    )
                    if generating_indicators.count() == 0 and count < expected_blocks:
                        if count > 0:
                            print(
                                f"Generation stopped. Only {count} of {expected_blocks} blocks found. Downloading available blocks..."
                            )
                            for i in range(count):
                                btn = download_btn.nth(i)
                                try:
                                    with page.expect_download(
                                        timeout=20000
                                    ) as download_info:
                                        btn.click()
                                    download = download_info.value
                                    yaml_path = download.path()
                                    with open(yaml_path, "r", encoding="utf-8") as f:
                                        yaml_blocks.append(f.read())
                                    print(f"Block {i + 1} downloaded successfully.")
                                except Exception as e:
                                    print(f"Block {i + 1} download failed: {e}")
                            report_received = True
                            break
                        else:
                            print(
                                "Generation stopped and no code blocks were found. Aborting."
                            )
                            break

                    time.sleep(10)

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

    if not report_received:
        print("Error, report not received, abort.")
        sys.exit(1)

    # Merge YAML data
    print("Merging YAML outputs...")
    combined_data = None
    for idx, block in enumerate(yaml_blocks):
        try:
            data = yaml.safe_load(block)
            if data is None:
                continue
            if combined_data is None:
                combined_data = data
                continue

            if isinstance(combined_data, dict) and isinstance(data, dict):
                for k, v in data.items():
                    if k in combined_data:
                        if isinstance(combined_data[k], list) and isinstance(v, list):
                            combined_data[k].extend(v)
                        elif isinstance(combined_data[k], dict) and isinstance(v, dict):
                            combined_data[k].update(v)
                        else:
                            combined_data[k] = v
                    else:
                        combined_data[k] = v
            elif isinstance(combined_data, list) and isinstance(data, list):
                combined_data.extend(data)
            else:
                print(
                    f"Warning: Cannot merge block {idx + 1} due to type mismatch. Overwriting."
                )
                combined_data = data
        except Exception as e:
            print(f"Failed to parse/merge block {idx + 1}: {e}")

        # Write merged yaml
        with open(output_yaml, "w", encoding="utf-8") as f:
            yaml.dump(combined_data, f, allow_unicode=True, default_flow_style=False)

        print(f"Successfully saved combined YAML data to: {output_yaml}")


def main():
    usage_str = """
Usage:
./deep-research-to-yaml.py
    browser [<profile_name>]
    research <prompt_file> [search="..."] [profile=...] [output=...] [headed|headless]
"""
    if len(sys.argv) < 2 or sys.argv[1].lower() in [
        "help",
        "[help]",
        "-h",
        "--help",
    ]:
        print(usage_str)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "browser":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else "default"
        run_interactive(profile_name)
    elif cmd == "research":
        if len(sys.argv) < 3:
            print("Error: Missing prompt file for research command.")
            print(usage_str)
            sys.exit(1)
        prompt_file = sys.argv[2]

        kwargs = {}
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
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
