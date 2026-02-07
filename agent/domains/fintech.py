from dataclasses import dataclass
from typing import List


@dataclass
class FintechControlMapping:
    control_id: str
    description: str
    validation_steps: List[str]


FINTECH_SECURITY_CONTROLS = [
    FintechControlMapping(
        control_id="PCI-DSS-3.2.1",
        description="Protect stored cardholder data",
        validation_steps=[
            "Verify encryption at rest for cardholder data",
            "Confirm key management rotation schedule",
        ],
    ),
    FintechControlMapping(
        control_id="SOC2-CC6.1",
        description="Logical and physical access controls",
        validation_steps=[
            "Review access reviews and approvals",
            "Validate least-privilege roles",
        ],
    ),
]


def get_fintech_checklist() -> List[dict]:
    return [
        {
            "control_id": control.control_id,
            "description": control.description,
            "steps": control.validation_steps,
        }
        for control in FINTECH_SECURITY_CONTROLS
    ]
