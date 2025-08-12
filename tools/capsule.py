#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return os.environ.get("GITHUB_SHA", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Emit a deterministic evaluation capsule JSON")
    parser.add_argument("--config", required=True, help="Path to config file (any format)")
    parser.add_argument("--metrics", required=True, help="Path to metrics/results JSON file")
    parser.add_argument("--out", required=True, help="Output path for capsule JSON")
    args = parser.parse_args()

    # Compute file hashes (raw bytes; we don't assume specific formats)
    config_sha = sha256_of_file(args.config)
    metrics_sha = sha256_of_file(args.metrics)

    # Base metadata
    capsule = {
        "git_commit": git_commit_sha(),
        "utc_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "py_version": sys.version.split(" (", 1)[0],
        "os": platform.platform(),
        "ci_job": os.environ.get("GITHUB_JOB", ""),
        "config_sha256": config_sha,
        "metrics_sha256": metrics_sha,
        "config_path": os.path.relpath(args.config),
        "metrics_path": os.path.relpath(args.metrics),
    }

    # Optionally inline a tiny subset of metrics for convenience (best-effort)
    try:
        with open(args.metrics, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        # Only copy well-known safe fields if present to avoid bloating
        for k in ("metrics", "threshold", "skipped"):
            if k in metrics:
                capsule[k] = metrics[k]
    except Exception:
        # If metrics isn't valid JSON, we still emit the capsule
        pass

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(capsule, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()

