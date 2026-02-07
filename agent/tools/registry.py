from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolRegistration:
    name: str
    permission: str
    handler: Callable


class ToolRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, ToolRegistration] = {}

    def register(self, name: str, permission: str, handler: Callable) -> None:
        self._registry[name] = ToolRegistration(name=name, permission=permission, handler=handler)

    def get(self, name: str) -> ToolRegistration:
        return self._registry[name]
