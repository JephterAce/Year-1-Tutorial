# Think Tank backup, recovery and operational monitoring runbook

## Scope and release status

This runbook defines the operational controls required before student enrolment or production use. It is a procedure, not evidence that a backup or restore has already been completed. No managed database, media object, production service or secret was changed while preparing it.

## Required backup coverage

1. **PostgreSQL:** use Neon point-in-time recovery/branch restore for short-window recovery and scheduled encrypted logical backups for independent recovery. Record backup timestamp, source project/branch, schema migration version, dump checksum and retention expiry.
2. **Private media:** enable object versioning or an equivalent recoverable snapshot policy for the private audio bucket. Record object inventory and checksums without making the bucket public.
3. **Configuration:** maintain a separately controlled inventory of required environment-variable names, owners, rotation dates and restore order. Never include secret values in Git, audit logs, this runbook or backup manifests.
4. **Application source:** retain reviewed Git commits, migration checksums, container build metadata and the release-gate record.

## Recovery objectives requiring owner approval

Before release, the owner must approve numeric Recovery Point Objective (RPO), Recovery Time Objective (RTO), backup retention, storage location, encryption/key custody, restore approvers and incident escalation. Do not infer these values.

## Safe restore rehearsal

The script `ops/backup_restore_rehearsal.sh` is deliberately restricted:
- the source is read-only and may be a managed backup/source URL;
- the destination must be the local database named exactly `thinktank_restore_rehearsal`;
- an explicit confirmation variable is required;
- source and destination cannot be the same database;
- the temporary dump is deleted after the rehearsal.

Example (use only after provisioning a disposable local PostgreSQL restore database):

```bash
export SOURCE_DATABASE_URL='postgresql://...'
export RESTORE_DATABASE_URL='postgresql://localhost:5432/thinktank_restore_rehearsal'
export CONFIRM_RESTORE_TARGET='thinktank_restore_rehearsal'
bash ops/backup_restore_rehearsal.sh
```

The script has not been run against managed staging or production. Do not paste connection strings or credentials into chat.

## Monitoring and incident response

- Configure a real uptime monitor for `GET /health` and assert HTTP 200 plus JSON `status=ok`; record `mode` and `service`.
- Configure Render health-check path only after an approved deployment proves the endpoint is stable.
- Alert on sustained HTTP 5xx, failed/in-progress deployments, instance restarts, CPU/memory saturation, database connection exhaustion, stale payment outbox jobs, SMTP failures and private-media access failures.
- Retain structured logs with request IDs and event metadata; never log passwords, bearer tokens, reset/verification tokens, payment secrets, full payment payloads or private media URLs.
- Maintain a named incident owner, severity matrix, user/guardian notification process and a tested rollback decision tree.
- Test the health monitor, alert delivery and escalation path using synthetic checks that do not create real student records or payments.

## Restore acceptance checklist

- [ ] Restore to an isolated target, never over the source.
- [ ] Verify dump checksum and source timestamp.
- [ ] Verify migration history and schema checksums.
- [ ] Verify expected row counts and referential integrity.
- [ ] Verify student login, assessment history and payment ledger using disposable fixtures.
- [ ] Verify private media objects remain private and can be recovered with correct checksums.
- [ ] Verify audit trail continuity and secrets are supplied separately.
- [ ] Record actual elapsed recovery time and data-loss window against the approved RTO/RPO.
- [ ] Obtain independent reviewer sign-off and owner acceptance.

## Current blockers

- Managed staging has migrations 001–013 only; repository migrations 014–019 are rehearsed in disposable CI, not applied to managed staging.
- No approved RPO/RTO, retention or independent off-site backup destination is recorded.
- No restore rehearsal has been completed against a managed backup.
- Monitoring and alert routing are not independently verified.
- Independent security review and production release approval remain outstanding.
