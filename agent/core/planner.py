from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PlanStep:
    description: str
    command: Optional[str] = None
    args: Optional[object] = None
    method: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> dict:
        out = {"description": self.description}
        if self.command: out["command"] = self.command
        if self.args is not None: out["args"] = self.args
        if self.method: out["method"] = self.method
        if self.url: out["url"] = self.url
        return out


@dataclass
class TaskPlan:
    title: str
    steps: List[PlanStep]


class FDEPlanner:
    def decompose(self, task: str, domain: Optional[str] = None) -> TaskPlan:
        t = task.lower()
        # Simple heuristic: provide an executable plan for patient record sync
        if ("sync patient records" in t) or ("patient sync" in t):
            steps = [
                PlanStep("Start sync banner", command="shell", args="echo Starting patient record sync"),
                PlanStep("Fetch API health (viz as placeholder)", command="http", method="GET", url="http://127.0.0.1:8000/index.html"),
                PlanStep("Check repo status", command="git", args=["status"]),
                PlanStep("Finalize sync", command="shell", args="echo Sync finalized"),
                PlanStep("Validation: confirm sync outcomes via health endpoint", command="http", method="GET", url="http://127.0.0.1:8000/index.html"),
            ]
            return TaskPlan(title="Patient Records Sync", steps=steps)
        # Default non-executable planning
        steps = [
            PlanStep("Discovery: confirm goals, success criteria, constraints, timeline"),
            PlanStep("Approvals: prepare change request with validation and rollback"),
            PlanStep("Delivery: execute in staging first; capture artifacts and logs"),
            PlanStep("Validation: explicit checks tied to success criteria; record results"),
            PlanStep("Handoff: provide runbooks, monitoring guidance, and escalation path"),
        ]
        return TaskPlan(title="General Delivery", steps=steps)
