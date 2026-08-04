#!/usr/bin/env python3
"""MCP tool server for OMP Cron and Task Scheduling."""

import json
import os
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cron-scheduler")

CRON_DIR = os.path.expanduser("~/.omp/cron")
CRON_FILE = os.path.join(CRON_DIR, "schedule.json")


def _ensure_storage() -> dict[str, Any]:
    """Ensure storage directory and schedule json file exist."""
    os.makedirs(CRON_DIR, exist_ok=True)
    if not os.path.exists(CRON_FILE):
        data = {"jobs": {}}
        with open(CRON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data
    try:
        with open(CRON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"jobs": {}}


def _save_storage(data: dict[str, Any]) -> None:
    """Save updated schedules to json storage file."""
    os.makedirs(CRON_DIR, exist_ok=True)
    with open(CRON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@mcp.tool()
def cron_schedule(
    name: str, cron_expression: str, prompt: str, target_channel: str = "signal"
) -> dict[str, Any]:
    """Schedule a recurring or one-shot prompt execution using standard cron syntax (e.g. '0 8 * * *')."""
    data = _ensure_storage()
    job_id = str(uuid.uuid4())[:8]
    job = {
        "id": job_id,
        "name": name,
        "schedule": cron_expression,
        "prompt": prompt,
        "target_channel": target_channel,
        "enabled": True,
    }
    data.setdefault("jobs", {})[job_id] = job
    _save_storage(data)
    return {"status": "scheduled", "job": job}


@mcp.tool()
def cron_list() -> list[dict[str, Any]]:
    """List all currently scheduled active cron tasks."""
    data = _ensure_storage()
    jobs = data.get("jobs", {})
    return list(jobs.values())


@mcp.tool()
def cron_cancel(job_id: str) -> dict[str, Any]:
    """Cancel and delete a scheduled cron task by ID."""
    data = _ensure_storage()
    jobs = data.get("jobs", {})
    if job_id in jobs:
        removed = jobs.pop(job_id)
        _save_storage(data)
        return {"status": "cancelled", "job": removed}
    return {"error": f"Job ID '{job_id}' not found."}


if __name__ == "__main__":
    mcp.run(transport="stdio")
