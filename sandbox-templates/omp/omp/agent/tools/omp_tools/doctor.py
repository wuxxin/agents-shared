#!/usr/bin/env python3
"""OMP Doctor Diagnostic Tool.

Runs comprehensive diagnostic checks across system prerequisites (bun, python3,
signal-cli), sandbox configuration, and local service port accessibility.
Formats a clean capability table with status (LIVE, DEGRADED, DOWN) and fix commands.
"""

from datetime import datetime, timezone
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List

try:
    from omp_tools.bunker_monitor import BunkerMonitor
except ImportError:
    try:
        from bunker_monitor import BunkerMonitor
    except ImportError:
        BunkerMonitor = None  # type: ignore


class OMPDoctor:
    """Diagnostic suite for Oh-My-PI (OMP) environment & infrastructure."""

    def __init__(self) -> None:
        """Initialize OMPDoctor diagnostic runner."""
        self.home_dir = os.path.expanduser("~")
        self.omp_dir = os.path.join(self.home_dir, ".omp")
        self.config_path = os.path.join(self.omp_dir, "agent", "config.yml")

    def check_prerequisite(
        self, binary_name: str, display_name: str, fix_cmd: str
    ) -> Dict[str, Any]:
        """Check availability of a system prerequisite executable."""
        path = shutil.which(binary_name)
        if path:
            version_str = ""
            try:
                out = subprocess.check_output(
                    [path, "--version"], stderr=subprocess.STDOUT, timeout=2.0
                )
                version_str = out.decode("utf-8").strip().split("\n")[0]
            except Exception:
                version_str = "version unknown"

            location_desc = f"{path} ({version_str})" if version_str else path
            return {
                "capability": display_name,
                "category": "Prerequisite",
                "status": "LIVE",
                "location": location_desc,
                "fix_command": "-",
                "detail": f"{binary_name} binary available in PATH",
            }
        else:
            return {
                "capability": display_name,
                "category": "Prerequisite",
                "status": "DOWN",
                "location": f"{binary_name} not found in PATH",
                "fix_command": fix_cmd,
                "detail": f"{binary_name} executable missing",
            }

    def check_sandbox_config(self) -> Dict[str, Any]:
        """Check OMP sandbox profile and configuration files."""
        if os.path.isfile(self.config_path):
            return {
                "capability": "Sandbox Configuration",
                "category": "Configuration",
                "status": "LIVE",
                "location": self.config_path,
                "fix_command": "-",
                "detail": "Agent configuration file present",
            }
        elif os.path.isdir(self.omp_dir):
            return {
                "capability": "Sandbox Configuration",
                "category": "Configuration",
                "status": "DEGRADED",
                "location": self.omp_dir,
                "fix_command": "sandbox-ctl install omp",
                "detail": "OMP home directory exists but agent/config.yml is missing",
            }
        else:
            return {
                "capability": "Sandbox Configuration",
                "category": "Configuration",
                "status": "DOWN",
                "location": "Not installed (~/.omp missing)",
                "fix_command": "sandbox-ctl install omp --no-start",
                "detail": "Sandbox directory structure missing",
            }

    def run_all_checks(self) -> List[Dict[str, Any]]:
        """Run all diagnostic checks across prerequisites, sandbox, and services."""
        checks: List[Dict[str, Any]] = []

        # 1. System Prerequisites
        checks.append(
            self.check_prerequisite(
                "bun", "Bun Runtime", "curl -fsSL https://bun.sh/install | bash"
            )
        )
        checks.append(
            self.check_prerequisite(
                "python3", "Python 3 Interpreter", "sudo pacman -S python"
            )
        )
        checks.append(
            self.check_prerequisite(
                "signal-cli", "Signal CLI", "sandbox-ctl provision signal-cli"
            )
        )

        # 2. Sandbox Configuration
        checks.append(self.check_sandbox_config())

        # 3. Port Accessibility & Services via BunkerMonitor
        service_fix_map = {
            "Local Router": "assistants/local-router.sh start",
            "Hindsight Memory": "bunx hindsight-mcp",
            "Nanobot Signal Gateway": "signal-cli daemon --http 127.0.0.1:50889",
            "Speech-to-Text (STT)": "assistants/local-speech-to-text.sh start",
            "Text-to-Speech (TTS)": "assistants/local-text-to-speech.sh start",
        }

        if BunkerMonitor is not None:
            monitor = BunkerMonitor()
            bunker_report = monitor.probe_all()
            for s_name, s_data in bunker_report.get("services", {}).items():
                s_status = s_data.get("status", "DOWN")
                s_url = s_data.get("url", f"port {s_data.get('port')}")
                s_detail = s_data.get("detail", "")
                fix_cmd = (
                    "-"
                    if s_status == "LIVE"
                    else service_fix_map.get(s_name, "check service logs")
                )

                checks.append(
                    {
                        "capability": s_name,
                        "category": "Service Port",
                        "status": s_status,
                        "location": s_url,
                        "fix_command": fix_cmd,
                        "detail": s_detail,
                    }
                )
        else:
            for s_name, fix_cmd in service_fix_map.items():
                checks.append(
                    {
                        "capability": s_name,
                        "category": "Service Port",
                        "status": "DOWN",
                        "location": "Monitor unavailable",
                        "fix_command": fix_cmd,
                        "detail": "BunkerMonitor module not loaded",
                    }
                )

        return checks

    def format_table(
        self, checks: List[Dict[str, Any]], color: bool = True
    ) -> str:
        """Format clean terminal capability table showing statuses and fix commands."""
        green = "\033[32m" if color else ""
        yellow = "\033[33m" if color else ""
        red = "\033[31m" if color else ""
        cyan = "\033[36m" if color else ""
        bold = "\033[1m" if color else ""
        reset = "\033[0m" if color else ""

        col_cap = 25
        col_cat = 15
        col_stat = 10
        col_loc = 35
        col_fix = 35

        header = (
            f"{'Capability':<{col_cap}} | "
            f"{'Category':<{col_cat}} | "
            f"{'Status':<{col_stat}} | "
            f"{'Endpoint / Location':<{col_loc}} | "
            f"{'Fix Command (if broken)':<{col_fix}}"
        )

        divider_line = (
            f"{'-'*col_cap}-+-{'-'*col_cat}-+-{'-'*col_stat}-+-{'-'*col_loc}-+-{'-'*col_fix}"
        )
        thick_divider = "=" * len(divider_line)

        rows: List[str] = []
        rows.append(thick_divider)
        rows.append(
            f"{bold}{cyan}{'OMP DOCTOR DIAGNOSTIC REPORT':^{len(divider_line)}}{reset}"
        )
        rows.append(thick_divider)
        rows.append(f"{bold}{header}{reset}")
        rows.append(divider_line)

        live_cnt = 0
        degraded_cnt = 0
        down_cnt = 0

        for item in checks:
            cap = item["capability"]
            cat = item["category"]
            stat = item["status"]
            loc = item["location"]
            fix = item["fix_command"]

            cap_str = cap[:col_cap]
            cat_str = cat[:col_cat]
            loc_str = loc[:col_loc]
            fix_str = fix[:col_fix]

            if stat == "LIVE":
                stat_colored = f"{green}{stat:<{col_stat}}{reset}"
                live_cnt += 1
            elif stat == "DEGRADED":
                stat_colored = f"{yellow}{stat:<{col_stat}}{reset}"
                degraded_cnt += 1
            else:
                stat_colored = f"{red}{stat:<{col_stat}}{reset}"
                down_cnt += 1

            row = (
                f"{cap_str:<{col_cap}} | "
                f"{cat_str:<{col_cat}} | "
                f"{stat_colored} | "
                f"{loc_str:<{col_loc}} | "
                f"{fix_str:<{col_fix}}"
            )
            rows.append(row)

        rows.append(thick_divider)
        total = len(checks)
        summary_str = (
            f"Summary: {live_cnt}/{total} capabilities operational. "
            f"[{green}{live_cnt} LIVE{reset}] "
            f"[{yellow}{degraded_cnt} DEGRADED{reset}] "
            f"[{red}{down_cnt} DOWN{reset}]"
        )
        rows.append(summary_str)
        rows.append(thick_divider)

        return "\n".join(rows)


def run_diagnostics(color: bool = True) -> Dict[str, Any]:
    """Run doctor diagnostics and return structured result dictionary and table string."""
    doctor = OMPDoctor()
    checks = doctor.run_all_checks()
    table_output = doctor.format_table(checks, color=color)

    has_down = any(c["status"] == "DOWN" for c in checks)
    has_degraded = any(c["status"] == "DEGRADED" for c in checks)

    if not (has_down or has_degraded):
        overall_status = "HEALTHY"
    elif not has_down:
        overall_status = "DEGRADED"
    else:
        overall_status = "UNHEALTHY"

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "checks": checks,
        "table": table_output,
    }


if __name__ == "__main__":
    use_color = sys.stdout.isatty()
    diag = run_diagnostics(color=use_color)
    print(diag["table"])
    if any(c["status"] == "DOWN" for c in diag["checks"]):
        sys.exit(1)
    sys.exit(0)
