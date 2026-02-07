from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Optional


class Domain(Enum):
    HEALTHCARE = "healthcare"
    FINTECH = "fintech"
    GENERAL = "general"


@dataclass
class TaskContext:
    task: str
    domain: Domain
    environment: str
    client: Optional[str] = None
    constraints: Optional[list[str]] = None

    def __post_init__(self) -> None:
        self.constraints = self.constraints or []
        self.timestamp = datetime.now(UTC).isoformat()


class FDEPlanner:
    DOMAIN_KEYWORDS = {
        Domain.HEALTHCARE: ["hipaa", "phi", "hl7", "fhir", "healthcare", "medical", "patient"],
        Domain.FINTECH: ["pci", "payment", "financial", "banking", "transaction"],
    }

    DOMAIN_REQUIREMENTS = {
        Domain.HEALTHCARE: [
            "HIPAA compliance validation required",
            "PHI data handling audit",
            "BAA verification with third parties",
            "Encryption at rest and in transit (AES-256, TLS 1.3)",
            "Access logging for all PHI touchpoints",
            "Minimum necessary access principle",
        ],
        Domain.FINTECH: [
            "PCI-DSS scope assessment",
            "SOC2 control mapping",
            "Transaction integrity validation",
            "Encryption key rotation plan",
        ],
        Domain.GENERAL: [
            "Standard security review",
            "Access control validation",
        ],
    }

    def detect_domain(self, task: str) -> Domain:
        task_lower = task.lower()
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in task_lower for keyword in keywords):
                return domain
        return Domain.GENERAL

    def generate_plan(self, context: TaskContext) -> dict:
        base_plan = self._base_plan(context)
        domain_reqs = self.DOMAIN_REQUIREMENTS.get(context.domain, [])
        base_plan["compliance_requirements"] = domain_reqs
        base_plan["domain"] = context.domain.value
        base_plan["plan"] = self._adapt_plan_to_domain(base_plan["plan"], context.domain)
        return base_plan

    def _base_plan(self, context: TaskContext) -> dict:
        return {
            "time": context.timestamp,
            "agent": "Forward Deployed Engineer (FDE)",
            "summary": {
                "request": context.task,
                "environment": context.environment,
                "client": context.client,
            },
            "plan": [
                {"phase": "Discovery", "steps": [], "artifacts": []},
                {"phase": "Validation", "steps": [], "artifacts": []},
                {"phase": "Execution", "steps": [], "artifacts": []},
                {"phase": "Verification", "steps": [], "artifacts": []},
                {"phase": "Handoff", "steps": [], "artifacts": []},
            ],
            "risks": [],
            "rollback": {},
        }

    def _adapt_plan_to_domain(self, plan: list[dict], domain: Domain) -> list[dict]:
        adaptations = {
            Domain.HEALTHCARE: {
                "Discovery": ["Identify all PHI data flows", "Map BAA requirements"],
                "Validation": ["HIPAA Security Rule checklist", "Verify audit logging"],
                "Execution": ["Enable PHI access logging", "Configure encryption"],
                "Verification": ["PHI access audit test", "Penetration test scoping"],
                "Handoff": ["HIPAA compliance documentation", "Incident response runbook"],
            }
        }

        if domain in adaptations:
            for phase in plan:
                phase["steps"].extend(adaptations[domain].get(phase["phase"], []))

        return plan
