from __future__ import annotations

from enum import Enum


class DeploymentState(Enum):
    Idle = 0
    Planning = 1
    Executing = 2
    Validated = 3
    Failed = 4


class DeploymentStateMachine:
    def __init__(self) -> None:
        self.current_state = DeploymentState.Idle

    def set_state(self, new_state: DeploymentState) -> None:
        self.current_state = new_state