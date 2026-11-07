# Student data isolation, extraction and bulk export

Status: required architecture and implementation specification. The export workflow is not yet a live feature.

## Data model: separate identity, shared secured storage

Each learner has one immutable internal student UUID. Every student-owned record must carry a `student_id` foreign key, directly or through a parent record whose ownership is checked in the same transaction. This includes profile data, progress, entitlements, payment references, assessment attempts and answers, notifications, consent records and relevant support/audit events.

Use a centrally managed PostgreSQL database with strict row ownership checks and indexes by `student_id`. Do not create a separate physical database per learner by default: it adds operational cost and makes backups, migrations and reporting harder without automatically providing better isolation. Separate database/schema tenancy can be reconsidered only for a genuine enterprise requirement.

Student-facing queries must derive the student identity from the authenticated session, never from a caller-supplied student ID alone. Cross-student access tests are mandatory. Admin access must be role-authorised and audited.

## Individual extraction

An authorised administrator can request one student's export. The package should include, where applicable:
- profile and account preferences;
- learning progress and completion history;
- assessment definitions/versions referenced by the learner's attempts, learner answers, scores, feedback and submission timestamps;
- entitlements and payment transaction references/statuses (never payment secrets or unnecessary provider payloads);
- notifications and consent/privacy-notice history;
- user-owned uploaded assets and a manifest of included files.

Do not export password hashes, session tokens, reset/verification tokens, private answer keys, internal security secrets, other learners' data, or unnecessary sensitive payment payloads.

## Bulk extraction

Administrators with a dedicated export permission may request:
- all eligible student records;
- one or more class levels (SS1, SS2, SS3);
- selected subjects or a defined date range where supported.

Bulk exports must use stable pagination/snapshots, deterministic column names, UTF-8 encoding and a manifest that states the scope, generation time, schema/export version, record counts and checksum. CSV is for tabular datasets; JSON is the canonical structured format for nested relationships. Related files are delivered separately in a controlled archive with a manifest. Do not create one huge in-memory export.

## Security and operational workflow

1. Authenticate the requester and enforce a dedicated role/permission; require step-up authentication for bulk export.
2. Validate scope and filters; record the request before queueing work.
3. A background worker reads a consistent database snapshot, applies ownership and scope filters, streams records to a private encrypted object-storage location, and calculates a SHA-256 checksum.
4. Mark completion only after storage confirms the object. Create a short-lived, single-purpose signed download URL only after re-authorising the requester.
5. Log request, authorisation, start, completion, download, failure, expiry and cancellation events. Never put exported data or signed URLs in logs.
6. Expire export objects automatically after a short configured retention period (default target: 24 hours); allow earlier deletion and retry failed jobs safely.
7. Rate-limit and cap bulk exports; alert on unusual volume. Do not email exports as attachments.
8. Use encryption in transit and at rest, least-privilege worker credentials, private buckets, object versioning controls and deletion verification.
9. A student's lawful access/export request must have a separate privacy workflow that can verify the requester and return only that student's data; admin bulk-export permissions are not a substitute.
10. Data correction/deletion requests, statutory retention exceptions, payment/accounting obligations and backup expiry must be handled under the approved retention schedule and legal review.

## Database and repository boundary

The Git repository stores application source, migrations, tests and documentation only. It must never store real student records, export archives, production database dumps, uploaded student files or secrets. Production learner data belongs in the secured database and private object storage. Backups must be encrypted, access-controlled and independently restorable.

## Acceptance tests before release

- A student can export only their own permitted data.
- Supplying another student's UUID cannot bypass session ownership.
- An individual export contains no other learner's records.
- A bulk export includes exactly the authorised filter scope and no records outside it.
- Unauthorised roles cannot request, download, or enumerate exports.
- Repeated requests and worker retries do not duplicate or corrupt export jobs.
- CSV and JSON are valid, deterministic, UTF-8 and include a manifest/checksum.
- Expired/revoked URLs cannot retrieve objects; objects are deleted after expiry.
- Audit records capture every lifecycle event without leaking content or signed URLs.
- Export generation streams large datasets and does not exhaust application memory.
- Password hashes, tokens, private answer keys and unrelated sensitive fields are excluded.
- No real student data or export files appear in Git history, CI artifacts or application logs.

## Implementation status — 7 November 2026

- Migration `005_student_data_exports.sql` still defines administrator bulk-export job/audit metadata; the asynchronous worker, private archive storage, checksum manifest, signed-download lifecycle and bulk-export role are not implemented.
- A separate student self-service JSON export endpoint now returns only the authenticated student's own profile, consent, learning progress, lesson practice, assessment attempts/answers, payment ledger, entitlements, saved lessons and data-rights request records.
- The student export projection does not select password hashes, session/reset/verification tokens, provider payloads or assessment answer keys. The download is private/no-store and audited.
- Migration `019_student_data_rights_requests.sql` provides student access/export, correction, deletion and restriction request intake, student request history/withdrawal, and a role-gated administrator triage queue.
- Deletion requests are intake-only. The system does not automatically erase accounts or records. Fulfilment, statutory retention exceptions, guardian identity verification and appeal handling remain subject to approved legal policy and human review.
- Disposable PostgreSQL CI replays the migration and runs authenticated browser tests with synthetic fixtures. No managed staging data or real student account is used.

**Still not complete:** bulk export worker, private archive storage, streamed large exports, file manifests/checksums, signed URL expiry/revocation, export lifecycle background jobs, formal guardian/age verification and legally approved retention/deletion execution. Do not describe statutory data-rights compliance as complete until legal sign-off and all acceptance criteria above pass.
