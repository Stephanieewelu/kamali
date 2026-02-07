from __future__ import annotations

import subprocess
from typing import Optional

from .base import BaseTool


class ShellTool(BaseTool):
    def run(self, command: Optional[str] = None) -> dict:
        if not command:
            return {"status": "skipped", "stdout": "", "stderr": "no command provided"}
        try:
            proc = subprocess.run(command, shell=True, capture_output=True, text=True)
            status = "ok" if proc.returncode == 0 else f"failed(code={proc.returncode})"
            return {"status": status, "stdout": proc.stdout, "stderr": proc.stderr}
        except Exception as e:
            return {"status": "failed(exception)", "stdout": "", "stderr": str(e)}
