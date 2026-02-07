import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional


@dataclass
class ConversationTurn:
    role: str
    content: str
    timestamp: str
    metadata: dict


@dataclass
class SessionState:
    session_id: str
    domain: str
    environment: str
    client: Optional[str]
    turns: list[ConversationTurn]
    artifacts: list[str]
    current_phase: str
    executed_commands: list[dict]


class SessionMemory:
    def __init__(self, storage_path: Path = Path("agent/sessions")) -> None:
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[SessionState] = None

    def start_session(self, session_id: str, domain: str, environment: str = "staging") -> SessionState:
        self.current_session = SessionState(
            session_id=session_id,
            domain=domain,
            environment=environment,
            client=None,
            turns=[],
            artifacts=[],
            current_phase="Discovery",
            executed_commands=[],
        )
        return self.current_session

    def add_turn(self, role: str, content: str, metadata: Optional[dict] = None) -> None:
        if not self.current_session:
            raise RuntimeError("No active session")
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(UTC).isoformat(),
            metadata=metadata or {},
        )
        self.current_session.turns.append(turn)

    def get_context_window(self, max_turns: int = 10) -> list[dict]:
        if not self.current_session:
            return []
        recent = self.current_session.turns[-max_turns:]
        return [{"role": turn.role, "content": turn.content} for turn in recent]

    def save_session(self) -> None:
        if not self.current_session:
            raise RuntimeError("No active session")
        filepath = self.storage_path / f"{self.current_session.session_id}.json"
        with open(filepath, "w", encoding="utf-8") as handle:
            session_dict = asdict(self.current_session)
            json.dump(session_dict, handle, indent=2, default=str)

    def load_session(self, session_id: str) -> Optional[SessionState]:
        filepath = self.storage_path / f"{session_id}.json"
        if filepath.exists():
            with open(filepath, encoding="utf-8") as handle:
                data = json.load(handle)
                self.current_session = SessionState(**data)
                return self.current_session
        return None
