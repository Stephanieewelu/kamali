"""
FDE Agent Orchestrator - The brain of the operation.
Coordinates planning, execution, validation, memory, and state transitions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .planner import FDEPlanner, TaskPlan
from .executor import ToolExecutor, ExecutionResult
from .validator import ValidationEngine
from .memory import SessionMemory, ConversationTurn
from .state_machine import DeploymentStateMachine, DeploymentState
from ..domains.registry import DomainRegistry


@dataclass
class OrchestratorConfig:
    ticket_id: Optional[str] = None
    environment: Optional[str] = None
    audit_log: Optional[Path] = None


class FDEOrchestrator:
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.planner = FDEPlanner()
        self.executor = ToolExecutor(ticket_id=config.ticket_id, audit_log=config.audit_log)
        self.validator = ValidationEngine()
        self.memory = SessionMemory(ticket_id=config.ticket_id)
        self.state = DeploymentStateMachine()
        self.domain_registry = DomainRegistry()

    def run_task(self, task: str) -> dict[str, Any]:
        domain = self.domain_registry.detect(task)
        self.memory.record_turn(ConversationTurn(role="user", content=task))
        self.state.set_state(DeploymentState.Planning)

        plan: TaskPlan = self.planner.decompose(task, domain=domain)
        self.memory.record_plan(plan)
        self.state.set_state(DeploymentState.Executing)

        results: list[ExecutionResult] = self.executor.execute(plan.steps)
        validation_ok = self.validator.validate(plan, results)
        self.state.set_state(DeploymentState.Validated if validation_ok else DeploymentState.Failed)

        summary = {
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"),
            "environment": self.config.environment,
            "ticket_id": self.config.ticket_id,
            "domain": domain,
            "plan": [s.to_dict() for s in plan.steps],
            "executed": [r.to_dict() for r in results],
            "validation_ok": validation_ok,
            "status": self.state.current_state.name,
        }
        self.memory.persist_summary(summary)
        return summary