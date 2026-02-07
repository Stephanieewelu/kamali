# Playbook: Incident Response

## Objective
Restore service safely while minimizing impact and capturing a clear record.

## Steps
1. **Triage**
   - Define impact, scope, and severity.
   - Identify recent changes and suspected components.
2. **Stabilize**
   - Apply safe mitigations (feature flag off, scaling, traffic shifting).
3. **Diagnose**
   - Collect logs, metrics, and error traces.
   - Hypothesize and validate root cause.
4. **Remediate**
   - Apply fix with validation checks.
   - Confirm recovery with metrics.
5. **Communicate**
   - Provide status updates to stakeholders on an agreed cadence.
6. **Postmortem**
   - Document root cause, timeline, and action items.

## Required outputs
- Incident timeline
- Root cause analysis
- Mitigation and prevention plan
- Stakeholder communications log
