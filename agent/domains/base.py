from dataclasses import dataclass
from typing import Protocol


@dataclass
class DomainChecklist:
    name: str
    items: list[str]


class DomainModule(Protocol):
    domain: str

    def get_checklist(self) -> DomainChecklist:
        ...
