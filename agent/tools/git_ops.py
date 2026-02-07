from __future__ import annotations

import subprocess
from typing import Optional, List

from .base import BaseTool


class GitTool(BaseTool):
    def run(self, args: Optional[List[str]] = None) -> dict:
        if not args:
            return {"status": "skipped", "stdout": "", "stderr": "no git args provided"}
        try:
            proc = subprocess.run(["git", *args], capture_output=True, text=True)
            status = "ok" if proc.returncode == 0 else f"failed(code={proc.returncode})"
            return {"status": status, "stdout": proc.stdout, "stderr": proc.stderr}
        except Exception as e:
            return {"status": "failed(exception)", "stdout": "", "stderr": str(e)}