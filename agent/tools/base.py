from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ToolResult:
    status: str
    stdout: str = ""
    stderr: str = ""


class BaseTool:
    def __init__(self, ticket_id: Optional[str] = None, audit_log: Optional[str] = None):
        self.ticket_id = ticket_id
        self.audit_log = audit_log

    def _record(self, entry: dict[str, Any]) -> None:
        # In production, append to audit log; here it's a no-op
        pass

    def run(self, *args, **kwargs) -> dict:
        raise NotImplementedError