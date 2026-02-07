from __future__ import annotations

from typing import Optional


class DomainRegistry:
    def detect(self, task: str) -> Optional[str]:
        t = task.lower()
        if any(k in t for k in ["patient", "hipaa", "fhir", "hl7"]):
            return "healthcare"
        if any(k in t for k in ["pci", "sox", "finance", "payment", "card"]):
            return "fintech"
        if any(k in t for k in ["fedramp", "fisma", "itar", "government"]):
            return "government"
        if any(k in t for k in ["store", "cart", "checkout", "ecommerce"]):
            return "ecommerce"
        if any(k in t for k in ["saas", "soc2", "iso 27001"]):
            return "saas"
        return "general"