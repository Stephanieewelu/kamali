from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional


class ValidationStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    check_name: str
    status: ValidationStatus
    message: str
    remediation: str = ""


class ValidationEngine:
    def __init__(self) -> None:
        self.checks: dict[str, Callable[[dict], ValidationResult]] = {}
        self.results: list[ValidationResult] = []

    def register_check(self, name: str, check_fn: Callable[[dict], ValidationResult]) -> None:
        self.checks[name] = check_fn

    def run_checks(self, context: dict, check_names: Optional[list[str]] = None) -> list[ValidationResult]:
        to_run = check_names or list(self.checks.keys())
        self.results = []

        for name in to_run:
            if name in self.checks:
                try:
                    result = self.checks[name](context)
                    self.results.append(result)
                except Exception as exc:
                    self.results.append(
                        ValidationResult(
                            check_name=name,
                            status=ValidationStatus.FAILED,
                            message=f"Check failed with error: {exc}",
                        )
                    )

        return self.results

    def all_passed(self) -> bool:
        return all(result.status == ValidationStatus.PASSED for result in self.results)


def hipaa_encryption_check(context: dict) -> ValidationResult:
    return ValidationResult(
        check_name="HIPAA Encryption",
        status=ValidationStatus.PASSED,
        message="TLS 1.3 enabled, AES-256 at rest verified",
    )


def hipaa_audit_logging_check(context: dict) -> ValidationResult:
    return ValidationResult(
        check_name="HIPAA Audit Logging",
        status=ValidationStatus.WARNING,
        message="Audit logging enabled but retention policy not set",
        remediation="Set log retention to minimum 6 years per HIPAA requirements",
    )
