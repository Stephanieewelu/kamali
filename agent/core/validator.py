from __future__ import annotations

from typing import List
from .planner import TaskPlan
from .executor import ExecutionResult


class ValidationEngine:
    """Minimal validation engine with basic HTTP checks.
    Marks success when all executable steps return status 'ok'.
    For HTTP steps, also require an HTTP 200 status code when available.
    """
    def validate(self, plan: TaskPlan, results: List[ExecutionResult]) -> bool:
        if not results:
            return False
        for r in results:
            if r.command:
                if r.status != "ok":
                    return False
                if r.command == "http":
                    code = None
                    if getattr(r, "meta", None):
                        code = r.meta.get("status_code")
                    if code is not None and not (200 <= int(code) < 300):
                        return False
        return True