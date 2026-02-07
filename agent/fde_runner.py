#!/usr/bin/env python3
import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from agent.core.executor import ToolExecutor, ToolPermission
from agent.core.memory import SessionMemory
from agent.core.planner import Domain, FDEPlanner, TaskContext
from agent.core.validator import (
    ValidationEngine,
    hipaa_audit_logging_check,
    hipaa_encryption_check,
)


class FDEAgent:
    def __init__(self) -> None:
        self.planner = FDEPlanner()
        self.executor = ToolExecutor(ToolPermission.READ_ONLY)
        self.memory = SessionMemory()
        self.validator = ValidationEngine()
        self.validator.register_check("hipaa_encryption", hipaa_encryption_check)
        self.validator.register_check("hipaa_audit", hipaa_audit_logging_check)

    def process_task(self, task: str, environment: str = "staging", client: str | None = None) -> dict:
        domain = self.planner.detect_domain(task)
        context = TaskContext(
            task=task,
            domain=domain,
            environment=environment,
            client=client,
        )
        plan = self.planner.generate_plan(context)

        if domain == Domain.HEALTHCARE:
            validation_results = self.validator.run_checks(
                {"domain": domain.value},
                ["hipaa_encryption", "hipaa_audit"],
            )
            plan["validation_results"] = [
                {
                    "check": result.check_name,
                    "status": result.status.value,
                    "message": result.message,
                }
                for result in validation_results
            ]

        if self.memory.current_session:
            self.memory.add_turn("user", task)
            plan["session_context"] = {
                "session_id": self.memory.current_session.session_id,
                "previous_turns": len(self.memory.current_session.turns),
                "current_phase": self.memory.current_session.current_phase,
            }

        return plan

    def start_session(self, session_id: str | None = None) -> str:
        sid = session_id or f"fde_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        self.memory.start_session(sid, "unknown")
        return sid

    def execute_tool(self, tool: str, command: str, dry_run: bool = True):
        result = self.executor.execute(tool, command, dry_run=dry_run)
        if self.memory.current_session:
            self.memory.current_session.executed_commands.append(
                {
                    "tool": result.tool,
                    "command": result.command,
                    "success": result.success,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
        return result


def format_output(result: dict) -> str:
    lines = [
        f"Time: {result.get('time')}",
        f"Agent: {result.get('agent')}",
        f"Domain: {result.get('domain', 'general').upper()}",
        "",
        "## Summary",
        f"- Request: {result['summary']['request']}",
        f"- Environment: {result['summary']['environment']}",
        "",
    ]

    if result.get("compliance_requirements"):
        lines.append("## Compliance Requirements")
        for req in result["compliance_requirements"]:
            lines.append(f"- {req}")
        lines.append("")

    if result.get("validation_results"):
        lines.append("## Validation Results")
        for validation in result["validation_results"]:
            status = validation["status"]
            icon = "✓" if status == "passed" else "⚠" if status == "warning" else "✗"
            lines.append(f"- [{icon}] {validation['check']}: {validation['message']}")
        lines.append("")

    lines.append("## Plan")
    for phase in result.get("plan", []):
        lines.append(f"\n### {phase['phase']}")
        for step in phase.get("steps", []):
            lines.append(f"  - {step}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="FDE Agent")
    parser.add_argument("--task", type=str, help="Task to process")
    parser.add_argument("--session", action="store_true", help="Interactive session mode")
    parser.add_argument("--environment", default="staging", choices=["staging", "production"])
    parser.add_argument("--client", type=str, help="Client identifier")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--execute", type=str, help="Execute a tool command")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--audit-log", type=str, help="Path for audit log")

    args = parser.parse_args()
    agent = FDEAgent()

    if args.session:
        session_id = agent.start_session()
        print(f"FDE Session started: {session_id}")
        print("Type 'exit' to quit, 'exec <command>' to run tools")

        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() == "exit":
                    agent.memory.save_session()
                    print("Session saved. Goodbye!")
                    break

                if user_input.startswith("exec "):
                    cmd = user_input[5:]
                    result = agent.execute_tool("shell", cmd, dry_run=args.dry_run)
                    output = result.output or result.error
                    status = "✓" if result.success else "✗"
                    print(f"[{status}] {output}")
                else:
                    result = agent.process_task(user_input, args.environment, args.client)
                    formatted = json.dumps(result, indent=2) if args.json else format_output(result)
                    print(formatted)

            except KeyboardInterrupt:
                print("\nSession interrupted.")
                break

    elif args.task:
        result = agent.process_task(args.task, args.environment, args.client)
        output = json.dumps(result, indent=2) if args.json else format_output(result)
        print(output)

        if args.audit_log:
            Path(args.audit_log).parent.mkdir(parents=True, exist_ok=True)
            with open(args.audit_log, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(result) + "\n")
            print(f"\n[AUDIT] Logged to: {args.audit_log}")

    elif args.execute:
        result = agent.execute_tool("shell", args.execute, dry_run=args.dry_run)
        output = result.output or result.error
        status = "✓" if result.success else "✗"
        print(f"[{status}] {output}")


if __name__ == "__main__":
    main()
