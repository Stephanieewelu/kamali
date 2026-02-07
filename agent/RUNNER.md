# FDE Agent CLI Runner

This runner produces a structured response from the Forward Deployed Engineer (FDE) agent blueprint using the system prompt, tooling contract, and available artifacts.

## Prerequisites
- Python 3.9+

## One-off run
Generate a structured response and optionally write an audit log.

```powershell
python agent\fde_runner.py --task "Plan integration delivery for customer staging" --audit-log agent\logs\session.md
```

- JSON output:
```powershell
python agent\fde_runner.py --task "Plan observability setup for staging" --json --audit-log agent\logs\session.json
```

## Interactive session
Start a multi-turn session. Type `exit` to quit.

```powershell
python agent\fde_runner.py --session --audit-log agent\logs\session.md
```

- JSON mode in session:
```powershell
python agent\fde_runner.py --session --json --audit-log agent\logs\session.json
```

## What it does
- Loads `agent/system_prompt.md` and `agent/tools/tooling_contract.json`.
- Chooses relevant references from playbooks/runbooks/templates/checklists based on your input.
- Produces a response with Summary, Plan, Status, Risks, Next Steps, and References.
- Writes audit logs (text or JSON) to `agent/logs/` when specified.

## Notes
- This is a blueprint runner; it does not call an LLM or execute external tools.
- Use the artifacts to drive real delivery: playbooks, runbooks, and templates.
- For a UI view, open the visualization by running in `agent/visualization`:
  - `python -m http.server 8000` then visit `http://localhost:8000/`.