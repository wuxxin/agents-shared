#!/usr/bin/env python3
"""OMP Background Service Heartbeat & Cron Runner.

This script implements an asynchronous background heartbeat daemon and cron runner
for OMP orchestration services. It periodically executes work audit pokes and
triggers Hindsight memory reflection sweeps.
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from typing import Any

import httpx

# Optional import for APScheduler AsyncIOScheduler
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    HAS_APSCHEDULER = True
except ImportError:
    HAS_APSCHEDULER = False


DEFAULT_RPC_URL = os.getenv("OMP_RPC_URL", "http://localhost:51080/v1/rpc")
DEFAULT_HINDSIGHT_URL = os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")
DEFAULT_BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "omp-orchestrator")

# Default intervals: 30 minutes for work sweep, 2 hours for health sync
DEFAULT_SWEEP_INTERVAL_SEC = 1800.0
DEFAULT_HEALTH_INTERVAL_SEC = 7200.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("omp_heartbeat")


async def job_work_sweep(
    client: httpx.AsyncClient | None = None,
    rpc_url: str = DEFAULT_RPC_URL,
) -> dict[str, Any]:
    """Execute periodic work audit poke to the OMP RPC service endpoint.

    Args:
        client: Optional httpx.AsyncClient instance for HTTP calls.
        rpc_url: Target OMP RPC service endpoint URL.

    Returns:
        dict[str, Any]: Execution status dictionary.
    """
    logger.info("Executing job_work_sweep (Work Audit Poke)...")
    payload = {
        "jsonrpc": "2.0",
        "method": "work_sweep",
        "params": {"audit": True, "timestamp": time.time()},
        "id": "work-sweep-job",
    }
    headers = {"Content-Type": "application/json"}

    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=10.0)
        close_client = True

    try:
        response = await client.post(rpc_url, json=payload, headers=headers)
        response.raise_for_status()
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}
        logger.info("job_work_sweep completed successfully (HTTP %d)", response.status_code)
        return {"status": "success", "http_code": response.status_code, "data": data}
    except httpx.HTTPError as exc:
        logger.error("job_work_sweep HTTP error: %s", exc)
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        logger.error("job_work_sweep unexpected error: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        if close_client:
            await client.aclose()


async def job_health_sync(
    client: httpx.AsyncClient | None = None,
    hindsight_url: str = DEFAULT_HINDSIGHT_URL,
    bank_id: str = DEFAULT_BANK_ID,
) -> dict[str, Any]:
    """Execute periodic Hindsight reflection sweep POST /v1/default/banks/{bank_id}/reflect.

    Args:
        client: Optional httpx.AsyncClient instance for HTTP calls.
        hindsight_url: Base URL for Hindsight API.
        bank_id: Hindsight bank identifier.

    Returns:
        dict[str, Any]: Execution status dictionary.
    """
    endpoint = f"{hindsight_url.rstrip('/')}/v1/default/banks/{bank_id}/reflect"
    logger.info("Executing job_health_sync (Hindsight Reflection Sweep to %s)...", endpoint)
    headers = {"Content-Type": "application/json"}
    payload = {
        "query": "Periodic health reflection sweep",
        "reason": "scheduled_health_sync",
        "timestamp": time.time(),
    }

    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=30.0)
        close_client = True

    try:
        response = await client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text}
        logger.info("job_health_sync completed successfully (HTTP %d)", response.status_code)
        return {"status": "success", "http_code": response.status_code, "data": data}
    except httpx.HTTPError as exc:
        logger.error("job_health_sync HTTP error: %s", exc)
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        logger.error("job_health_sync unexpected error: %s", exc)
        return {"status": "error", "error": str(exc)}
    finally:
        if close_client:
            await client.aclose()


async def run_once(
    rpc_url: str,
    hindsight_url: str,
    bank_id: str,
) -> dict[str, Any]:
    """Execute a single pass of all heartbeat jobs.

    Args:
        rpc_url: Target OMP RPC service endpoint URL.
        hindsight_url: Base URL for Hindsight API.
        bank_id: Hindsight bank identifier.

    Returns:
        dict[str, Any]: Combined results of all jobs executed.
    """
    logger.info("Running single pass of heartbeat jobs (--once)...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        work_res = await job_work_sweep(client=client, rpc_url=rpc_url)
        health_res = await job_health_sync(
            client=client, hindsight_url=hindsight_url, bank_id=bank_id
        )
    return {
        "job_work_sweep": work_res,
        "job_health_sync": health_res,
    }


async def run_daemon(
    rpc_url: str,
    hindsight_url: str,
    bank_id: str,
    sweep_interval_sec: float = DEFAULT_SWEEP_INTERVAL_SEC,
    health_interval_sec: float = DEFAULT_HEALTH_INTERVAL_SEC,
) -> None:
    """Run the background heartbeat daemon loop continuously.

    Uses APScheduler AsyncIOScheduler if available, otherwise falls back to
    an asyncio.sleep loop scheduler.

    Args:
        rpc_url: Target OMP RPC service endpoint URL.
        hindsight_url: Base URL for Hindsight API.
        bank_id: Hindsight bank identifier.
        sweep_interval_sec: Interval in seconds for job_work_sweep.
        health_interval_sec: Interval in seconds for job_health_sync.
    """
    logger.info(
        "Starting OMP Heartbeat Daemon (sweep_interval=%.0fs, health_interval=%.0fs)...",
        sweep_interval_sec,
        health_interval_sec,
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        if HAS_APSCHEDULER:
            logger.info("Using APScheduler AsyncIOScheduler backend.")
            scheduler = AsyncIOScheduler()

            async def scheduled_work_sweep() -> None:
                await job_work_sweep(client=client, rpc_url=rpc_url)

            async def scheduled_health_sync() -> None:
                await job_health_sync(client=client, hindsight_url=hindsight_url, bank_id=bank_id)

            scheduler.add_job(
                scheduled_work_sweep,
                trigger=IntervalTrigger(seconds=sweep_interval_sec),
                id="job_work_sweep",
                name="Work Sweep Audit Poke",
                replace_existing=True,
            )
            scheduler.add_job(
                scheduled_health_sync,
                trigger=IntervalTrigger(seconds=health_interval_sec),
                id="job_health_sync",
                name="Health Sync Reflection",
                replace_existing=True,
            )
            scheduler.start()

            # Trigger initial run on daemon startup
            await job_work_sweep(client=client, rpc_url=rpc_url)
            await job_health_sync(client=client, hindsight_url=hindsight_url, bank_id=bank_id)

            try:
                while True:
                    await asyncio.sleep(3600)
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("Stopping APScheduler heartbeat daemon...")
                scheduler.shutdown(wait=False)
        else:
            logger.info(
                "APScheduler unavailable. Falling back to asyncio.sleep loop scheduler."
            )

            async def loop_work_sweep() -> None:
                while True:
                    await job_work_sweep(client=client, rpc_url=rpc_url)
                    await asyncio.sleep(sweep_interval_sec)

            async def loop_health_sync() -> None:
                while True:
                    await job_health_sync(client=client, hindsight_url=hindsight_url, bank_id=bank_id)
                    await asyncio.sleep(health_interval_sec)

            try:
                await asyncio.gather(
                    loop_work_sweep(),
                    loop_health_sync(),
                )
            except (KeyboardInterrupt, asyncio.CancelledError):
                logger.info("Stopping asyncio loop heartbeat daemon...")


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional raw command line arguments.

    Returns:
        argparse.Namespace: Parsed CLI options.
    """
    parser = argparse.ArgumentParser(
        description="OMP Background Service Heartbeat & Cron Runner"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously as background daemon (default action if --once is not passed)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single pass of all heartbeat jobs and exit",
    )
    parser.add_argument(
        "--rpc-url",
        default=DEFAULT_RPC_URL,
        help=f"OMP RPC service endpoint URL (default: {DEFAULT_RPC_URL})",
    )
    parser.add_argument(
        "--hindsight-url",
        default=DEFAULT_HINDSIGHT_URL,
        help=f"Hindsight API base URL (default: {DEFAULT_HINDSIGHT_URL})",
    )
    parser.add_argument(
        "--bank-id",
        default=DEFAULT_BANK_ID,
        help=f"Hindsight Bank ID (default: {DEFAULT_BANK_ID})",
    )
    parser.add_argument(
        "--sweep-interval",
        type=float,
        default=DEFAULT_SWEEP_INTERVAL_SEC,
        help=f"Work sweep interval in seconds (default: {DEFAULT_SWEEP_INTERVAL_SEC})",
    )
    parser.add_argument(
        "--health-interval",
        type=float,
        default=DEFAULT_HEALTH_INTERVAL_SEC,
        help=f"Health sync interval in seconds (default: {DEFAULT_HEALTH_INTERVAL_SEC})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose DEBUG logging",
    )
    return parser.parse_args(args)


async def main_async(cli_args: argparse.Namespace) -> int:
    """Async main entrypoint.

    Args:
        cli_args: Parsed CLI namespace.

    Returns:
        int: Process exit code.
    """
    if cli_args.verbose:
        logger.setLevel(logging.DEBUG)

    if cli_args.once:
        results = await run_once(
            rpc_url=cli_args.rpc_url,
            hindsight_url=cli_args.hindsight_url,
            bank_id=cli_args.bank_id,
        )
        logger.info("Single pass results: %s", results)
        return 0

    await run_daemon(
        rpc_url=cli_args.rpc_url,
        hindsight_url=cli_args.hindsight_url,
        bank_id=cli_args.bank_id,
        sweep_interval_sec=cli_args.sweep_interval,
        health_interval_sec=cli_args.health_interval,
    )
    return 0


def main() -> None:
    """CLI script entrypoint."""
    parsed = parse_args()
    try:
        sys.exit(asyncio.run(main_async(parsed)))
    except KeyboardInterrupt:
        logger.info("Heartbeat process interrupted by user. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
