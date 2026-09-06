import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

import tr2016_autorecover_watchdog as wd

LOG_PATH = Path("tr2016_autonomous_runner.log")
STATE_PATH = Path("tr2016_autonomous_runner_state.json")


def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    line = f"[{now_str()}] {msg}"
    print(line, flush=True)
    existing = LOG_PATH.read_text(encoding="utf-8") if LOG_PATH.exists() else ""
    LOG_PATH.write_text(existing + line + "\n", encoding="utf-8")


def write_state(payload: dict) -> None:
    p = dict(payload)
    p["updated_at"] = now_str()
    STATE_PATH.write_text(json.dumps(p, indent=2), encoding="utf-8")


def get_health() -> dict:
    client = wd.connect()
    try:
        return wd.get_dataset_health(client)
    finally:
        client.close()


def run_watchdog(interval_sec: int, max_restarts: int) -> int:
    cmd = [
        sys.executable,
        "tr2016_autorecover_watchdog.py",
        "--interval-sec",
        str(interval_sec),
        "--max-restarts",
        str(max_restarts),
    ]
    log(f"Starting watchdog: {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous TR2016 watcher + launcher")
    parser.add_argument("--interval-sec", type=int, default=300,
                        help="Seconds between dataset checks when waiting")
    parser.add_argument("--watchdog-interval-sec", type=int, default=120,
                        help="Seconds between checks inside watchdog")
    parser.add_argument("--watchdog-max-restarts", type=int, default=8,
                        help="Max restarts for watchdog")
    parser.add_argument("--once", action="store_true",
                        help="Check once and exit (do not loop)")
    args = parser.parse_args()

    log("Autonomous TR2016 runner started.")

    while True:
        try:
            health = get_health()
        except Exception as ex:
            log(f"Dataset health check failed: {ex}")
            write_state({
                "status": "health_check_error",
                "error": str(ex),
            })
            if args.once:
                return
            time.sleep(args.interval_sec)
            continue

        if health.get("has_real_data"):
            missing = health.get("missing_or_empty_langs", [])
            if missing:
                log(f"Partial data detected but incomplete languages remain: {missing}")
            else:
                log("Real TR2016 data detected for all required languages. Launching watchdog.")

            write_state({
                "status": "launching_watchdog",
                "dataset_health": health,
            })
            rc = run_watchdog(
                interval_sec=args.watchdog_interval_sec,
                max_restarts=args.watchdog_max_restarts,
            )
            log(f"Watchdog exited with return code {rc}.")

            watchdog_state = {}
            wd_state_path = Path("tr2016_watchdog_state.json")
            if wd_state_path.exists():
                try:
                    watchdog_state = json.loads(wd_state_path.read_text(encoding="utf-8"))
                except Exception as ex:
                    watchdog_state = {"parse_error": str(ex)}

            status = watchdog_state.get("status", "unknown")
            write_state({
                "status": "watchdog_exited",
                "watchdog_return_code": rc,
                "watchdog_status": status,
                "watchdog_state": watchdog_state,
            })

            if status == "completed":
                log("TR2016 watchdog reports completed. Autonomous runner exiting.")
                return

            if args.once:
                return

            log("Watchdog did not complete successfully. Returning to wait mode.")
            time.sleep(args.interval_sec)
            continue

        missing = health.get("missing_or_empty_langs", ["de", "es", "fr", "it"])
        log(f"Waiting for real TR2016 data. Missing/empty languages: {missing}")
        write_state({
            "status": "waiting_for_dataset",
            "dataset_health": health,
        })

        if args.once:
            return

        time.sleep(args.interval_sec)


if __name__ == "__main__":
    main()
