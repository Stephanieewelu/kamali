# Playbook: Data Migration

## Objective
Move customer data safely with validation, minimal downtime, and clear rollback options.

## Steps
1. **Discovery**
   - Identify data sources, volumes, and required transformations.
   - Confirm data owners, retention policies, and compliance requirements.
2. **Plan**
   - Define migration windows, cutover strategy, and validation checks.
   - Establish rollback and re-run strategy.
3. **Prepare**
   - Provision staging and backups.
   - Dry-run the migration on a sample dataset.
4. **Execute**
   - Run migration with monitoring for throughput and errors.
   - Record logs and checkpoints.
5. **Validate**
   - Compare record counts, checksums, and business KPIs.
6. **Handoff**
   - Document final state and provide operational guidance.

## Deliverables
- Migration plan and cutover checklist
- Validation report and sign-off
- Rollback procedure
