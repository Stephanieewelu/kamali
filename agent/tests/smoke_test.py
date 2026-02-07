from __future__ import annotations

import json
import os
import sys
import time
import glob
import subprocess
from typing import Any, Dict


def latest_artifact_dir(base: str) -> str | None:
    dirs = [d for d in glob.glob(os.path.join(base, "*")) if os.path.isdir(d)]
    if not dirs:
        return None
    # Sort by modification time desc
    dirs.sort(key=lambda d: os.path.getmtime(d), reverse=True)
    return dirs[0]


def run_one_off(task: str = "Sync patient records") -> None:
    cmd = [sys.executable, "-m", "agent.fde_runner", "--task", task, "--execute"]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    base_artifacts = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    base_artifacts = os.path.abspath(base_artifacts)

    run_one_off()
    time.sleep(0.5)

    latest_dir = latest_artifact_dir(base_artifacts)
    if not latest_dir:
        print("No artifacts directory found.")
        return 1

    manifest_path = os.path.join(latest_dir, "deployment_manifest.json")
    if not os.path.exists(manifest_path):
        print("deployment_manifest.json not found in", latest_dir)
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest: Dict[str, Any] = json.load(f)

    if not manifest.get("validation_ok"):
        print("Validation did not pass in manifest.")
        return 1

    executed = manifest.get("executed", [])
    http_ok = True
    for step in executed:
        if step.get("command") == "http":
            meta = step.get("meta") or {}
            code = meta.get("status_code")
            if code is not None and not (200 <= int(code) < 300):
                http_ok = False
                print("HTTP step failed status_code:", code)
    if not http_ok:
        return 1

    print("Smoke test passed: validation_ok and HTTP steps healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())