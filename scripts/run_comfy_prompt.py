#!/usr/bin/env python3
"""Submit an already-exported ComfyUI API prompt and record runtime evidence."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess
import threading
import time
import urllib.error
import urllib.request


def request_json(url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


class GpuMonitor:
    def __init__(self, csv_path: pathlib.Path, interval: float) -> None:
        self.csv_path = csv_path
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.peak_memory_mib = 0

    def start(self) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        self.thread.start()

    def stop(self) -> int:
        self.stop_event.set()
        self.thread.join(timeout=self.interval + 3)
        return self.peak_memory_mib

    def _run(self) -> None:
        with self.csv_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["captured_at", "gpu", "memory_used_mib", "memory_total_mib", "utilization_pct", "power_w"])
            while not self.stop_event.is_set():
                captured_at = dt.datetime.now(dt.timezone.utc).isoformat()
                try:
                    result = subprocess.run(
                        [
                            "nvidia-smi",
                            "--query-gpu=index,memory.used,memory.total,utilization.gpu,power.draw",
                            "--format=csv,noheader,nounits",
                        ],
                        check=True,
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    for line in result.stdout.splitlines():
                        fields = [field.strip() for field in line.split(",")]
                        if len(fields) == 5:
                            used = int(float(fields[1]))
                            self.peak_memory_mib = max(self.peak_memory_mib, used)
                            writer.writerow([captured_at, *fields])
                    stream.flush()
                except (OSError, subprocess.SubprocessError, ValueError):
                    writer.writerow([captured_at, "monitor_error", "", "", "", ""])
                    stream.flush()
                self.stop_event.wait(self.interval)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=pathlib.Path, help="JSON from export_h3_t2v_api.py")
    parser.add_argument("--server", default="http://127.0.0.1:8188")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--poll-seconds", type=float, default=3.0)
    parser.add_argument("--monitor-log", type=pathlib.Path, required=True)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    if not isinstance(payload.get("prompt"), dict) or not payload["prompt"]:
        raise SystemExit("payload must contain a non-empty prompt object")

    started = time.monotonic()
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    monitor = GpuMonitor(args.monitor_log, 1.0)
    monitor.start()
    try:
        submitted = request_json(f"{args.server.rstrip('/')}/prompt", payload)
        prompt_id = submitted.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"ComfyUI did not return prompt_id: {submitted}")

        history: dict | None = None
        while time.monotonic() - started < args.timeout:
            result = request_json(f"{args.server.rstrip('/')}/history/{prompt_id}")
            history = result.get(prompt_id)
            if history and history.get("status", {}).get("completed"):
                break
            time.sleep(args.poll_seconds)
        else:
            raise TimeoutError(f"timed out after {args.timeout}s waiting for {prompt_id}")
    finally:
        peak_memory_mib = monitor.stop()

    finished_at = dt.datetime.now(dt.timezone.utc).isoformat()
    elapsed_seconds = round(time.monotonic() - started, 2)
    report = {
        "prompt_id": prompt_id,
        "submitted": submitted,
        "history": history,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": elapsed_seconds,
        "peak_memory_mib": peak_memory_mib,
        "monitor_log": str(args.monitor_log),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    status = history.get("status", {}).get("status_str", "unknown")
    print(f"PROMPT_ID={prompt_id}")
    print(f"STATUS={status}")
    print(f"ELAPSED_SECONDS={elapsed_seconds}")
    print(f"PEAK_MEMORY_MIB={peak_memory_mib}")
    print(f"REPORT={args.report}")
    if status != "success":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
