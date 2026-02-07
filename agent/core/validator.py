from __future__ import annotations

from typing import List
from .planner import TaskPlan
from .executor import ExecutionResult


class ValidationEngine:
    """Minimal validation engine.
    Marks success when all executable steps return status 'ok'.
    """
    def validate(self, plan: TaskPlan, results: List[ExecutionResult]) -> bool:
        if not results:
            return False
        for r in results:
            if r.command and r.status != "ok":
                return False
        return True