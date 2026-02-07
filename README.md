# Forward Deployed Engineer Agent

A production-ready, forward deployed engineer (FDE) agent blueprint designed for customer environments. It standardizes discovery, delivery, incident response, and operational handoff with clear guardrails and auditability.

## What this provides
- **System prompt** tuned for FDE work: discovery, integration, delivery, and escalation.
- **Operational playbooks** for integration delivery, incidents, deployment hardening, and data migration.
- **Runbooks** for environment validation, access setup, observability, and rollback.
- **Checklists** for launch readiness and security review.
- **Templates** for customer intake, change requests, postmortems, and weekly updates.
- **Tooling contract** that defines safe usage of shell, HTTP, and Git.
- **Evaluation rubric** for quality, safety, and customer impact.
- **Visualization** to demonstrate the deployment flow at a glance.

## Quick start
1. Review the system prompt: `agent/system_prompt.md`
2. Configure tools: `agent/tools/tooling_contract.json`
3. Capture customer context with `agent/templates/customer_intake.md`
4. Use playbooks/runbooks during delivery and operations.
5. Open `agent/visualization/index.html` to visualize the deployment flow.

## Repository layout
```
agent/
  system_prompt.md
  capabilities.md
  agent_profile.yaml
  tools/
    tooling_contract.json
  playbooks/
    integration_delivery.md
    incident_response.md
    deployment_hardening.md
    data_migration.md
  runbooks/
    environment_validation.md
    access_setup.md
    observability_setup.md
    rollback.md
  checklists/
    go_live.md
    security_review.md
  templates/
    customer_intake.md
    change_request.md
    incident_postmortem.md
    launch_readiness.md
    weekly_update.md
  visualization/
    index.html
    styles.css
  evaluation_rubric.md
```

## Usage guidance
This blueprint is framework-agnostic. Embed `system_prompt.md` into your agent runner, load the playbooks/runbooks as tools or memory, and use the templates for human-facing communication and approvals.
