import shlex
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Callable


class ToolPermission(Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    DESTRUCTIVE = "destructive"


@dataclass
class ToolResult:
    tool: str
    command: str
    success: bool
    output: str
    error: str = ""
    duration_ms: int = 0


class ToolExecutor:
    SAFE_COMMANDS = {
        "ls",
        "cat",
        "head",
        "tail",
        "grep",
        "find",
        "echo",
        "pwd",
        "kubectl get",
        "kubectl describe",
        "docker ps",
        "docker logs",
        "git status",
        "git log",
        "git diff",
        "curl -I",
        "ping -c",
    }

    BLOCKED_PATTERNS = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        "> /dev/",
        "chmod 777",
        "curl | bash",
        "wget | sh",
    ]

    def __init__(self, permission_level: ToolPermission = ToolPermission.READ_ONLY) -> None:
        self.permission = permission_level
        self.execution_log: list[ToolResult] = []
        self.require_approval: Callable[[str], bool] = lambda command: True

    def execute(self, tool: str, command: str, dry_run: bool = False) -> ToolResult:
        if not self._is_safe(command):
            return ToolResult(
                tool=tool,
                command=command,
                success=False,
                output="",
                error="Command blocked by security policy",
            )

        if dry_run:
            return ToolResult(
                tool=tool,
                command=command,
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
            )

        if self.permission != ToolPermission.READ_ONLY:
            if not self.require_approval(command):
                return ToolResult(
                    tool=tool,
                    command=command,
                    success=False,
                    output="",
                    error="Command rejected by approval gate",
                )

        result = self._execute_shell(command)
        self.execution_log.append(result)
        return result

    def _is_safe(self, command: str) -> bool:
        for blocked in self.BLOCKED_PATTERNS:
            if blocked in command:
                return False
        return True

    def _execute_shell(self, command: str) -> ToolResult:
        import time

        start = time.time()
        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=None,
            )
            return ToolResult(
                tool="shell",
                command=command,
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                duration_ms=int((time.time() - start) * 1000),
            )
        except Exception as exc:
            return ToolResult(
                tool="shell",
                command=command,
                success=False,
                output="",
                error=str(exc),
            )
