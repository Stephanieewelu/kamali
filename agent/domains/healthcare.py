from dataclasses import dataclass
from typing import List


@dataclass
class HIPAAControlMapping:
    control_id: str
    description: str
    implementation_spec: str
    validation_steps: List[str]


HIPAA_SECURITY_CONTROLS = [
    HIPAAControlMapping(
        control_id="164.312(a)(1)",
        description="Access Control - Unique User Identification",
        implementation_spec="Assign unique identifier to each user",
        validation_steps=[
            "Verify unique user IDs in identity provider",
            "Check no shared accounts exist",
            "Validate MFA enforcement",
        ],
    ),
    HIPAAControlMapping(
        control_id="164.312(a)(2)(iv)",
        description="Access Control - Encryption and Decryption",
        implementation_spec="Implement encryption for PHI at rest",
        validation_steps=[
            "Verify AES-256 encryption on databases",
            "Check encryption on file storage",
            "Validate key management procedures",
        ],
    ),
    HIPAAControlMapping(
        control_id="164.312(b)",
        description="Audit Controls",
        implementation_spec="Implement audit logging for PHI access",
        validation_steps=[
            "Verify audit logs capture all PHI access",
            "Check log retention meets 6-year requirement",
            "Validate log integrity protection",
        ],
    ),
    HIPAAControlMapping(
        control_id="164.312(e)(1)",
        description="Transmission Security",
        implementation_spec="Protect PHI during transmission",
        validation_steps=[
            "Verify TLS 1.2+ on all endpoints",
            "Check certificate validity",
            "Validate no insecure protocols",
        ],
    ),
]


def get_hipaa_checklist() -> List[dict]:
    return [
        {
            "control_id": control.control_id,
            "description": control.description,
            "steps": control.validation_steps,
        }
        for control in HIPAA_SECURITY_CONTROLS
    ]
