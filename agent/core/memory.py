from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any

AGENT_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = AGENT_DIR / "sessions"


@dataclass
class ConversationTurn:
    role: str
    content: str
    time: str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")


class SessionMemory:
    def __init__(self, ticket_id: Optional[str] = None):
        self.ticket_id = ticket_id or "default"
        self.root = SESSIONS_DIR / self.ticket_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.turns: List[ConversationTurn] = []

    def record_turn(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)

    def record_plan(self, plan: Any) -> None:
        (self.root / "plan.json").write_text(json.dumps({"title": getattr(plan, "title", ""), "steps": [s.to_dict() for s in getattr(plan, "steps", [])]}, indent=2), encoding="utf-8")

    def persist_summary(self, summary: dict) -> None:
        (self.root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (self.root / "turns.json").write_text(json.dumps([t.__dict__ for t in self.turns], indent=2), encoding="utf-8")