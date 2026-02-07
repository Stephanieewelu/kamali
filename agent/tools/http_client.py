from __future__ import annotations

import requests
from typing import Optional, Any

from .base import BaseTool


class HttpTool(BaseTool):
    def request(self, method: str = "GET", url: Optional[str] = None, data: Optional[Any] = None) -> dict:
        if not url:
            return {"status": "skipped", "stdout": "", "stderr": "no url provided"}
        try:
            resp = requests.request(method=method, url=url, data=data, timeout=10)
            status = "ok" if resp.status_code < 400 else f"failed(status={resp.status_code})"
            return {"status": status, "stdout": resp.text, "stderr": ""}
        except Exception as e:
            return {"status": "failed(exception)", "stdout": "", "stderr": str(e)}
