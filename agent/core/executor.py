from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

from ..tools.shell import ShellTool
from ..tools.http_client import HttpTool
from ..tools.git_ops import GitTool
from .planner import PlanStep


@dataclass
class ExecutionResult:
    description: str
    command: str
    status: str
    stdout: str
    stderr: str
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "command": self.command,
            "status": self.status,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "meta": self.meta,
        }


class ToolExecutor:
    def __init__(self, ticket_id: Optional[str] = None, audit_log: Optional[str] = None):
        self.shell = ShellTool(ticket_id=ticket_id, audit_log=audit_log)
        self.http = HttpTool(ticket_id=ticket_id, audit_log=audit_log)
        self.git = GitTool(ticket_id=ticket_id, audit_log=audit_log)

    def execute(self, steps: List[PlanStep]) -> List[ExecutionResult]:
        executed: List[ExecutionResult] = []
        for s in steps:
            cmd = s.command
            if not cmd:
                executed.append(ExecutionResult(s.description, cmd, "skipped", "", "non-executable step"))
                continue
            try:
                if cmd == "shell":
                    res = self.shell.run(s.args)
                elif cmd == "http":
                    res = self.http.request(method=s.method or "GET", url=s.url, data=s.args)
                elif cmd == "git":
                    res = self.git.run(s.args)
                else:
                    res = {"status": "skipped", "stdout": "", "stderr": f"Unknown command: {cmd}"}
            except Exception as e:
                res = {"status": "failed(exception)", "stdout": "", "stderr": str(e)}
            executed.append(ExecutionResult(
                s.description,
                cmd,
                res.get("status", "skipped"),
                res.get("stdout", ""),
                res.get("stderr", ""),
                res.get("meta")
            ))
        return executed