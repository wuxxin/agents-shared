#!/usr/bin/env python3
"""Bunker Infrastructure Monitor.

Probes local OMP infrastructure endpoints (Local Router, Hindsight,
Nanobot Signal, STT, TTS), returns structured health dictionaries,
and logs service status transitions.
"""

from datetime import datetime, timezone
import json
import logging
import os
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("bunker_monitor")

DEFAULT_SERVICES: Dict[str, Dict[str, Any]] = {
    "Local Router": {
        "port": 51080,
        "url": os.getenv("LOCAL_ROUTER_URL", "http://localhost:51080/v1/models"),
        "fallback_path": "/v1/models",
    },
    "Hindsight Memory": {
        "port": 8888,
        "url": os.getenv("HINDSIGHT_API_URL", "http://localhost:8888/v1/default/banks"),
        "fallback_path": "/health",
    },
    "Nanobot Signal Gateway": {
        "port": 50889,
        "url": os.getenv("SIGNAL_HTTP_URL", "http://localhost:50889/health"),
        "fallback_path": "/v1/receive",
    },
    "Speech-to-Text (STT)": {
        "port": 50090,
        "url": os.getenv("STT_BASE_URL", "http://localhost:50090/v1/models"),
        "fallback_path": "/v1/models",
    },
    "Text-to-Speech (TTS)": {
        "port": 50095,
        "url": os.getenv("TTS_BASE_URL", "http://localhost:50095/v1/models"),
        "fallback_path": "/v1/models",
    },
}


class BunkerMonitor:
    """Monitors health and status transitions for local OMP services."""

    def __init__(self, services: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize BunkerMonitor with service target definitions."""
        self.services = services or DEFAULT_SERVICES.copy()
        self.service_states: Dict[str, str] = {}
        self.transition_history: List[Dict[str, Any]] = []

    def probe_tcp_port(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Probe if a TCP port is accepting connections."""
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, socket.timeout):
            return False

    def probe_service(
        self, name: str, config: Dict[str, Any], timeout: float = 3.0
    ) -> Dict[str, Any]:
        """Probe a single service endpoint and return structured health details."""
        url: str = config.get("url", "")
        port: int = config.get("port", 0)
        start_time = time.perf_counter()

        healthy = False
        status = "DOWN"
        http_code: Optional[int] = None
        detail = "Connection failed"
        error: Optional[str] = None

        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "BunkerMonitor/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                http_code = response.getcode()
                healthy = True
                status = "LIVE"
                detail = f"HTTP {http_code} OK"
        except urllib.error.HTTPError as err:
            http_code = err.code
            if http_code in (401, 403, 404, 405):
                healthy = True
                status = "DEGRADED"
                detail = f"HTTP {http_code} (Service active, path notice)"
            else:
                healthy = False
                status = "DEGRADED"
                detail = f"HTTP {http_code} {err.reason}"
            error = f"HTTP {http_code}"
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            port_open = self.probe_tcp_port("localhost", port, timeout=1.5)
            if port_open:
                healthy = True
                status = "DEGRADED"
                detail = f"Port {port} open (HTTP probe failed: {err})"
            else:
                healthy = False
                status = "DOWN"
                detail = f"Port {port} unreachable: {err}"
                error = str(err)
        except Exception as err:
            healthy = False
            status = "DOWN"
            detail = f"Unexpected error: {err}"
            error = str(err)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        now_iso = datetime.now(timezone.utc).isoformat()

        # Log and store state transition if status changed
        prev_state = self.service_states.get(name, "UNKNOWN")
        if prev_state != status:
            transition_entry = {
                "service": name,
                "from_state": prev_state,
                "to_state": status,
                "timestamp": now_iso,
                "detail": detail,
            }
            self.transition_history.append(transition_entry)
            self.service_states[name] = status

            if prev_state != "UNKNOWN":
                logger.warning(
                    "[Bunker Monitor] Transition for '%s': %s -> %s (%s)",
                    name,
                    prev_state,
                    status,
                    detail,
                )
            else:
                logger.info(
                    "[Bunker Monitor] Initial state for '%s': %s (%s)",
                    name,
                    status,
                    detail,
                )

        return {
            "name": name,
            "port": port,
            "url": url,
            "healthy": healthy,
            "status": status,
            "http_code": http_code,
            "latency_ms": latency_ms,
            "detail": detail,
            "error": error,
            "timestamp": now_iso,
        }

    def probe_all(self, timeout: float = 3.0) -> Dict[str, Any]:
        """Probe all registered services and return structured dictionary report."""
        now_iso = datetime.now(timezone.utc).isoformat()
        results: Dict[str, Dict[str, Any]] = {}
        healthy_count = 0
        live_count = 0
        degraded_count = 0
        down_count = 0

        for name, config in self.services.items():
            res = self.probe_service(name, config, timeout=timeout)
            results[name] = res
            if res["healthy"]:
                healthy_count += 1
            if res["status"] == "LIVE":
                live_count += 1
            elif res["status"] == "DEGRADED":
                degraded_count += 1
            else:
                down_count += 1

        total_count = len(self.services)
        overall_healthy = down_count == 0

        report = {
            "timestamp": now_iso,
            "overall_healthy": overall_healthy,
            "summary": {
                "total": total_count,
                "healthy": healthy_count,
                "live": live_count,
                "degraded": degraded_count,
                "down": down_count,
            },
            "services": results,
            "transitions": list(self.transition_history),
        }
        return report


def run_bunker_health_check() -> Dict[str, Any]:
    """Execute a single health check sweep across bunker infrastructure services."""
    monitor = BunkerMonitor()
    return monitor.probe_all()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    report = run_bunker_health_check()
    print(json.dumps(report, indent=2))
