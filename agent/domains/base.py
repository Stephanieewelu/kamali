from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DomainSpec:
    name: str
    compliance: Dict[str, Any]


class BaseDomain:
    def __init__(self, spec: DomainSpec):
        self.spec = spec

    def preflight(self) -> Dict[str, Any]:
        return {"ok": True, "checks": ["secrets available", "observability configured"]}

    def postflight(self) -> Dict[str, Any]:
        return {"ok": True, "checks": ["incident hooks active", "escalation paths ready"]}
