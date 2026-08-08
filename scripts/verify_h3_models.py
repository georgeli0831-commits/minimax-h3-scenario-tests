#!/usr/bin/env python3
"""Verify the exact five MiniMax H3 safetensors files without loading weights."""

from __future__ import annotations

import argparse
import json
import pathlib
from safetensors import safe_open


EXPECTED = {
    "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors": 20_970_379_616,
    "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors": 20_970_379_616,
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors": 15_687_142_551,
    "vae/minimax_h3_video_vae_fp16.safetensors": 5_207_808_496,
    "vae/minimax_h3_audio_vae_fp32.safetensors": 605_254_808,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("models_root", type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path, required=True)
    args = parser.parse_args()

    files = []
    failures = []
    for relative, expected_bytes in EXPECTED.items():
        path = args.models_root / relative
        entry = {"path": relative, "expected_bytes": expected_bytes, "actual_bytes": None, "tensor_count": None}
        try:
            entry["actual_bytes"] = path.stat().st_size
            if entry["actual_bytes"] != expected_bytes:
                raise ValueError(f"size {entry['actual_bytes']} != {expected_bytes}")
            # safe_open parses only the safetensors header / metadata; it does
            # not materialize the multi-gigabyte tensor values in CPU memory.
            with safe_open(path, framework="pt", device="cpu") as handle:
                entry["tensor_count"] = len(list(handle.keys()))
                entry["metadata"] = handle.metadata()
            entry["status"] = "PASS"
        except Exception as exc:  # include bad headers and missing files in report
            entry["status"] = "FAIL"
            entry["error"] = str(exc)
            failures.append(relative)
        files.append(entry)

    report = {"status": "PASS" if not failures else "FAIL", "files": files}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MODEL_VERIFICATION={report['status']}")
    for entry in files:
        print(f"{entry['status']} {entry['path']} bytes={entry['actual_bytes']}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
