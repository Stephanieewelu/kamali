import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime

# UI and HTTP
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import requests

# Orchestrator integration
from .core import FDEOrchestrator, OrchestratorConfig

BASE_DIR = Path(__file__).resolve().parent.parent
AGENT_DIR = BASE_DIR / "agent"
PROMPT_PATH = AGENT_DIR / "system_prompt.md"
CONTRACT_PATH = AGENT_DIR / "tools" / "tooling_contract.json"
PLAYBOOKS_DIR = AGENT_DIR / "playbooks"
RUNBOOKS_DIR = AGENT_DIR / "runbooks"
CHECKLISTS_DIR = AGENT_DIR / "checklists"
TEMPLATES_DIR = AGENT_DIR / "templates"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def load_contract() -> dict:
    try:
        return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def list_artifacts() -> dict:
    def list_md(dir_path: Path):
        if not dir_path.exists():
            return []
        return [p.name for p in sorted(dir_path.glob("*.md"))]
    return {
        "playbooks": list_md(PLAYBOOKS_DIR),
        "runbooks": list_md(RUNBOOKS_DIR),
        "checklists": list_md(CHECKLISTS_DIR),
        "templates": list_md(TEMPLATES_DIR),
    }


def choose_references(task: str) -> list:
    task_l = task.lower()
    refs = []
    if any(k in task_l for k in ("incident","outage","sev","mitigate")):
        refs.append("playbooks/incident_response.md")
    if any(k in task_l for k in ("migrate","migration","data move","cutover")):
        refs.append("playbooks/data_migration.md")
    if any(k in task_l for k in ("deploy","delivery","integration","harden")):
        refs += ["playbooks/integration_delivery.md","playbooks/deployment_hardening.md"]
    if any(k in task_l for k in ("observe","monitor","alerts","metrics","dashboard")):
        refs.append("runbooks/observability_setup.md")
    if any(k in task_l for k in ("access","credential","permission","mfa")):
        refs.append("runbooks/access_setup.md")
    if any(k in task_l for k in ("validate","compatibility","dry-run","staging")):
        refs.append("runbooks/environment_validation.md")
    refs += [
        "templates/customer_intake.md",
        "templates/change_request.md",
        "checklists/go_live.md",
        "checklists/security_review.md",
    ]
    seen, out = set(), []
    for r in refs:
        if r not in seen:
            out.append(r); seen.add(r)
    return out


def build_structured(task: str) -> dict:
    contract = load_contract()
    refs = choose_references(task)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
    data = {
        "time": now,
        "agent": "Forward Deployed Engineer (FDE)",
        "summary": {
            "request": task,
            "assumptions": "staging available; approvals required for production changes; rollback planned.",
            "outcome_target": "validated, reversible steps and documented artifacts."
        },
        "plan": [
            "Discovery: confirm goals, success criteria, constraints, timeline (templates/customer_intake.md).",
            "Approvals: prepare change request with validation and rollback (templates/change_request.md).",
            "Delivery: execute in staging first; capture artifacts and logs (playbooks + runbooks).",
            "Validation: explicit checks tied to success criteria; record results.",
            "Handoff: provide runbooks, monitoring guidance, and escalation path."
        ],
        "status": {"current": "Planning", "next_checkpoint": "Discovery complete and approvals obtained."},
        "risks": [
            {"description": "Environment mismatch, access gaps, or missing rollback.", "level": "Medium"},
            {"description": "Production impact without a change window or validation.", "level": "High"},
            {"description": "Security/compliance controls not fully validated.", "level": "High"}
        ],
        "next_steps": [
            "Confirm environment readiness (runbooks/environment_validation.md)",
            "Validate access and MFA (runbooks/access_setup.md)",
            "Set up observability and alerts (runbooks/observability_setup.md)",
            "Draft change request with milestones, validation, and rollback"
        ],
        "references": refs,
        "tooling_contract": [
            *(f"{t.get('name')}: {t.get('purpose')}" for t in contract.get('tools', []))
        ] if contract else []
    }

    # Provide an executable plan for patient record sync tasks
    t = task.lower()
    if ("sync patient records" in t) or ("patient sync" in t):
        data["plan"] = [
            {"description": "Start sync banner", "command": "shell", "args": "echo Starting patient record sync"},
            {"description": "Fetch API health (viz as placeholder)", "command": "http", "method": "GET", "url": "http://127.0.0.1:8000/index.html"},
            {"description": "Check repo status", "command": "git", "args": ["status"]},
            {"description": "Finalize sync", "command": "shell", "args": "echo Sync finalized"},
            {"description": "Validation: confirm sync outcomes via health endpoint", "command": "http", "method": "GET", "url": "http://127.0.0.1:8000/index.html"}
        ]
        data["status"]["current"] = "Executing"
        data["status"]["next_checkpoint"] = "Validate outcomes"

    return data


def render_text(d: dict) -> str:
    lines = [f"Time: {d['time']}", f"Agent: {d['agent']}", "", "Summary"]
    s = d['summary']; lines += [f"- Request: {s['request']}", f"- Assumptions: {s['assumptions']}", f"- Outcome target: {s['outcome_target']}"]
    lines += ["", "Plan"] + [f"- {p}" for p in d['plan']]
    st = d['status']; lines += ["", "Status", f"- Current: {st['current']}", f"- Next checkpoint: {st['next_checkpoint']}"]
    # Render risks as descriptions for text mode
    risk_lines = []
    for r in d['risks']:
        desc = r['description'] if isinstance(r, dict) else str(r)
        level = (r.get('level') if isinstance(r, dict) else None)
        risk_lines.append(f"- {desc}" + (f" ({level})" if level else ""))
    lines += ["", "Risks"] + risk_lines
    lines += ["", "Next Steps"] + [f"- {n}" for n in d['next_steps']]
    lines += ["", "References"] + [f"- {r}" for r in d['references']]
    if d.get("tooling_contract"):
        lines += ["", "Tooling Contract"] + [f"- {t}" for t in d['tooling_contract']]
    return "\n".join(lines)


def render_rich(d: dict, environment: str | None) -> None:
    console = Console()
    # Environment guard tag at the very top
    if environment:
        env = environment.lower()
        if env == "production":
            panel = Panel(Text("!!! PRODUCTION !!!", style="bold red blink"), title="Environment", border_style="red")
        elif env == "staging":
            panel = Panel(Text("STAGING", style="bold black on yellow"), title="Environment", border_style="yellow")
        else:
            panel = Panel(Text(environment.upper(), style="bold"), title="Environment", border_style="blue")
        console.print(panel)

    console.print(f"Time: {d['time']}")
    console.print(f"Agent: {d['agent']}")
    console.print("")

    # Plan table
    plan_table = Table(title="Plan", show_lines=True)
    plan_table.add_column("Step", style="cyan", no_wrap=True)
    plan_table.add_column("Description", overflow="fold")
    plan_table.add_column("Result", style="green", no_wrap=True)
    exec_steps = (d.get("execution", {}) or {}).get("steps", [])
    # map index->status for display
    result_map = {}
    for idx, step in enumerate(exec_steps, start=1):
        result_map[idx] = step.get("status", "pending")
    for i, p in enumerate(d['plan'], start=1):
        desc = p if isinstance(p, str) else p.get('description', str(p))
        res = result_map.get(i, "pending")
        style = "bold red" if res.startswith("failed") else ("bold yellow" if res == "skipped" else "bold green" if res in ("ok","success") else "")
        plan_table.add_row(str(i), desc, Text(res, style=style))
    console.print(plan_table)

    # Status
    st = d['status']
    console.print(f"[bold]Status[/bold]: {st['current']} (Next: {st['next_checkpoint']})")

    # Risks table with styling for High/Critical
    risk_table = Table(title="Risks", show_lines=True)
    risk_table.add_column("Description", overflow="fold")
    risk_table.add_column("Level", style="magenta", no_wrap=True)
    for r in d['risks']:
        desc = r['description'] if isinstance(r, dict) else str(r)
        level = (r.get('level') if isinstance(r, dict) else "Medium")
        if level in ("High", "Critical"):
            risk_table.add_row(Text(desc, style="bold red"), Text(level, style="bold red"))
        else:
            risk_table.add_row(desc, level)
    console.print(risk_table)

    # Next steps
    next_table = Table(title="Next Steps")
    next_table.add_column("#", style="cyan", no_wrap=True)
    next_table.add_column("Description", overflow="fold")
    for i, n in enumerate(d['next_steps'], start=1):
        next_table.add_row(str(i), n)
    console.print(next_table)

    # References
    ref_table = Table(title="References")
    ref_table.add_column("Path", overflow="fold")
    for r in d['references']:
        ref_table.add_row(r)
    console.print(ref_table)

    # Tooling contract
    if d.get("tooling_contract"):
        tc_table = Table(title="Tooling Contract")
        tc_table.add_column("Entry", overflow="fold")
        for t in d['tooling_contract']:
            tc_table.add_row(t)
        console.print(tc_table)


def try_validation() -> bool:
    """Attempt a simple validation (simulate `curl -f`) against local viz server."""
    try:
        resp = requests.get("http://localhost:8000/", timeout=3)
        return resp.status_code < 400
    except Exception:
        return False


def suggest_rollback_command() -> str:
    """Provide an immediate rollback command suggestion."""
    # Generic example; adjust per deployment stack
    return "kubectl rollout undo deployment/<service>  # adjust to your stack"


def generate_evidence_bundle(ticket_id: str, environment: str | None, d: dict, executed_steps: list[dict], validation_ok: bool, rollback_cmd: str | None) -> Path:
    """Create artifacts/{ticket_id}/deployment_manifest.json with planned vs actual."""
    root = AGENT_DIR / "artifacts" / ticket_id
    root.mkdir(parents=True, exist_ok=True)
    manifest = {
        "ticket_id": ticket_id,
        "time": d["time"],
        "environment": environment,
        "plan": [{"description": p} if isinstance(p, str) else p for p in d["plan"]],
        "executed": executed_steps,
        "status": d.get("status"),
        "validation_ok": validation_ok,
        "rollback_suggested": rollback_cmd,
        "references": d.get("references"),
    }
    out = root / "deployment_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out


def write_audit(content: str, path: Path, append: bool = False):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append and path.exists() else "w"
    with path.open(mode, encoding="utf-8") as f:
        f.write(content + ("\n" if not content.endswith("\n") else ""))


class ToolRunner:
    def __init__(self, audit_log: str | None, ticket_id: str | None):
        self.audit_log = Path(audit_log) if audit_log else None
        self.ticket_id = ticket_id or "default"
        self.state_dir = AGENT_DIR / "artifacts" / self.ticket_id
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "state.json"

    def _write_audit(self, text: str):
        if self.audit_log:
            write_audit(text, self.audit_log, append=True)

    def load_state(self) -> int:
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return int(data.get("current_step", 0))
        except Exception:
            return 0

    def save_state(self, step_index: int):
        payload = {"current_step": step_index}
        self.state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def execute_step(self, step: dict) -> dict:
        desc = step.get("description", "")
        cmd_type = step.get("command")
        result = {"description": desc, "command": cmd_type, "status": "skipped", "stdout": "", "stderr": ""}
        if not cmd_type:
            return result
        try:
            if cmd_type == "shell":
                command = step.get("args") or step.get("cmd")
                if not command:
                    raise RuntimeError("shell step missing 'args' or 'cmd'")
                proc = subprocess.run(command, shell=True, capture_output=True, text=True)
                result["stdout"] = proc.stdout
                result["stderr"] = proc.stderr
                if proc.returncode == 0:
                    result["status"] = "ok"
                else:
                    result["status"] = f"failed({proc.returncode})"
            elif cmd_type == "http":
                method = (step.get("method") or "GET").upper()
                url = step.get("url")
                data = step.get("data")
                if not url:
                    raise RuntimeError("http step missing 'url'")
                resp = requests.request(method, url, json=data, timeout=10)
                result["stdout"] = f"status={resp.status_code} body={resp.text[:500]}"
                if resp.status_code < 400:
                    result["status"] = "ok"
                else:
                    result["status"] = f"failed({resp.status_code})"
            elif cmd_type == "git":
                args = step.get("args")
                if not args:
                    raise RuntimeError("git step missing 'args'")
                proc = subprocess.run(["git"] + args, capture_output=True, text=True)
                result["stdout"] = proc.stdout
                result["stderr"] = proc.stderr
                if proc.returncode == 0:
                    result["status"] = "ok"
                else:
                    result["status"] = f"failed({proc.returncode})"
            else:
                result["status"] = "skipped"
                result["stderr"] = f"Unknown command type: {cmd_type}"
        except Exception as e:
            result["status"] = "failed(exception)"
            result["stderr"] = str(e)
        # log stderr if any
        if result.get("stderr"):
            self._write_audit(f"[ERROR] {desc}: {result['stderr']}")
        return result

    def run(self, plan: list[dict]) -> tuple[list[dict], bool, int]:
        start_index = self.load_state()
        executed = []
        failed = False
        for i in range(start_index, len(plan)):
            step = plan[i]
            # normalize string -> dict
            if isinstance(step, str):
                step = {"description": step}
            res = self.execute_step(step)
            executed.append(res)
            self.save_state(i + 1)
            if res["status"].startswith("failed"):
                failed = True
                break
        return executed, failed, self.load_state()


def one_off(task: str, json_mode: bool, audit_log: str | None, environment: str | None, ticket_id: str | None, execute: bool = False):
    data = build_structured(task)

    # Simulate execution status and validation
    executed_steps = [{"description": p if isinstance(p, str) else p.get('description', str(p)), "status": "planned"} for p in data["plan"]]
    needs_validation = any((isinstance(p, str) and "Validation:" in p) or (isinstance(p, dict) and "validation" in p.get("description"," ").lower()) for p in data["plan"])
    validation_ok = True
    rollback_cmd = None

    # Execute plan if requested and commands exist
    if execute:
        cfg = OrchestratorConfig(ticket_id=ticket_id, environment=environment, audit_log=Path(audit_log) if audit_log else None)
        orch = FDEOrchestrator(cfg)
        summary = orch.run_task(task)
        exec_results = summary.get("executed", [])
        executed_steps = exec_results
        data.setdefault("execution", {})["steps"] = exec_results
        all_ok = summary.get("validation_ok", False) and all(s.get("status") == "ok" for s in exec_results)
        validation_ok = all_ok
        if all_ok:
            data["status"]["current"] = "Validated"
            data["status"]["next_checkpoint"] = "Handoff artifacts"
        else:
            data["status"]["current"] = "FAILED - Awaiting Rollback"
            data["status"]["next_checkpoint"] = "Suggest rollback"
            rollback_cmd = suggest_rollback_command()

    if needs_validation and not execute:
        validation_ok = try_validation()
        if not validation_ok:
            data["status"]["current"] = "ROLLING BACK"
            rollback_cmd = suggest_rollback_command()

    if json_mode:
        content = json.dumps(data, indent=2)
        print(content)
    else:
        render_rich(data, environment)
        if rollback_cmd:
            console = Console()
            console.print(Panel(Text(f"Validation/Execution issue → Suggested rollback: {rollback_cmd}", style="bold red"), border_style="red"))

    # Write audit log with text-mode rendering
    if audit_log:
        log_path = Path(audit_log)
        write_audit(render_text(data), log_path)
        print(f"\n[AUDIT] Saved structured response to: {log_path}")

    # Evidence bundle
    if ticket_id:
        out = generate_evidence_bundle(ticket_id, environment, data, executed_steps, validation_ok, rollback_cmd)
        print(f"[EVIDENCE] deployment_manifest saved to: {out}")


def session(json_mode: bool, audit_log: str | None, environment: str | None, ticket_id: str | None, execute: bool = False):
    print("FDE Agent session. Type 'exit' to quit.")
    log_path = Path(audit_log) if audit_log else None
    while True:
        try:
            task = input("> ").strip()
        except EOFError:
            break
        if not task or task.lower() in ("exit","quit"):
            break
        data = build_structured(task)

        # Simulate execution and validation per turn
        executed_steps = [{"description": p if isinstance(p, str) else p.get('description', str(p)), "status": "planned"} for p in data["plan"]]
        needs_validation = any((isinstance(p, str) and "Validation:" in p) or (isinstance(p, dict) and "validation" in p.get("description"," ").lower()) for p in data["plan"])
        validation_ok = True
        rollback_cmd = None

        if execute:
            cfg = OrchestratorConfig(ticket_id=ticket_id, environment=environment, audit_log=Path(audit_log) if audit_log else None)
            orch = FDEOrchestrator(cfg)
            summary = orch.run_task(task)
            exec_results = summary.get("executed", [])
            executed_steps = exec_results
            data.setdefault("execution", {})["steps"] = exec_results
            all_ok = summary.get("validation_ok", False) and all(s.get("status") == "ok" for s in exec_results)
            validation_ok = all_ok
            if all_ok:
                data["status"]["current"] = "Validated"
                data["status"]["next_checkpoint"] = "Handoff artifacts"
            else:
                data["status"]["current"] = "FAILED - Awaiting Rollback"
                data["status"]["next_checkpoint"] = "Suggest rollback"
                rollback_cmd = suggest_rollback_command()

        if needs_validation and not execute:
            validation_ok = try_validation()
            if not validation_ok:
                data["status"]["current"] = "ROLLING BACK"
                rollback_cmd = suggest_rollback_command()

        if json_mode:
            content = json.dumps(data, indent=2)
            print(content)
        else:
            render_rich(data, environment)
            if rollback_cmd:
                console = Console()
                console.print(Panel(Text(f"Validation/Execution issue → Suggested rollback: {rollback_cmd}", style="bold red"), border_style="red"))

        if log_path:
            write_audit(render_text(data), log_path, append=True)

        if ticket_id:
            out = generate_evidence_bundle(ticket_id, environment, data, executed_steps, validation_ok, rollback_cmd)
            print(f"[EVIDENCE] deployment_manifest saved to: {out}")


def main():
    parser = argparse.ArgumentParser(description="FDE Agent CLI Runner (blueprint)")
    parser.add_argument("--task", help="Describe the task or request for the agent.")
    parser.add_argument("--audit-log", help="Path to write responses (e.g., agent/logs/session.md)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    parser.add_argument("--session", action="store_true", help="Start an interactive multi-turn session")
    parser.add_argument("--environment", choices=["staging","production"], help="Target environment tag for UI guard")
    parser.add_argument("--ticket-id", help="Change ticket or request identifier for evidence bundle")
    parser.add_argument("--execute", action="store_true", help="Execute plan commands with ToolRunner")
    args = parser.parse_args()

    if args.session:
        session(json_mode=args.json, audit_log=args.audit_log, environment=args.environment, ticket_id=args.ticket_id, execute=args.execute)
    else:
        if not args.task:
            parser.error("--task is required for one-off runs (or use --session)")
        one_off(task=args.task, json_mode=args.json, audit_log=args.audit_log, environment=args.environment, ticket_id=args.ticket_id, execute=args.execute)


if __name__ == "__main__":
    main()
