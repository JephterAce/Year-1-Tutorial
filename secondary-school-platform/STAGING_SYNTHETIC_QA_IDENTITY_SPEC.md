# Staging Synthetic QA Identity Lifecycle

**Status:** Design and implementation contract; not yet implemented or deployed.  
**Scope:** Staging only. This document does not authorise public registration, production changes, real learner onboarding, or guardian-consent processing.

## Why a separate lifecycle is required

The existing student registration path is not suitable for creating a QA identity. It is feature-gated by `STUDENT_REGISTRATION_ENABLED`, creates a pending row in `students`, creates a verification token, and writes privacy-notice and terms acceptance records. Those records must not be reused to imply guardian consent or approval of draft legal documents. Public registration must remain disabled.

## Required design

1. **Staging-only activation**
   - A dedicated `STAGING_QA_IDENTITY_ENABLED` flag must be required in addition to `APP_ENV=staging`.
   - The route must return not-found when either condition is false.
   - No public registration flag may be enabled as a side effect.

2. **Owner-authorised provisioning**
   - Provisioning must require an authenticated admin session, valid CSRF token, and the narrowest available admin permission (or a new explicit `qa.identity.manage` permission).
   - Only an explicitly configured, owner-controlled QA mailbox may receive the invitation. Do not accept an arbitrary recipient from the request body.
   - Enforce a small fixed maximum number of active QA identities and an issuance rate limit.
   - Record an audit event containing only the synthetic account ID, actor, action, expiry and outcome. Never log passwords, tokens, cookies or message contents.

3. **Explicit synthetic identity marker**
   - A database-level marker must distinguish synthetic QA identities from real learners.
   - The marker must be immutable through ordinary student profile routes.
   - QA identities must be excluded from all learner counts, exports, payments, analytics, guardian/consent reports, and production data migration paths by default.
   - No guardian-consent row may be created, inferred, or marked granted by QA provisioning.

4. **Verification and authentication**
   - Generate a cryptographically random, single-use, hashed verification token with a short expiry and revocation support.
   - Deliver the invitation only to the configured QA mailbox using the existing email delivery service.
   - Require verification before login; never return the raw token from an API response.
   - Use the existing password hashing, session hashing, secure-cookie and CSRF mechanisms.
   - Expiry, revocation, duplicate invitation, repeated issuance and failed delivery must fail closed.

5. **Constrained QA access**
   - A synthetic session must be explicitly marked in the authenticated principal.
   - It must not access or mutate real learner records, assessments, progress, tutoring, payments, exports, privacy requests, or private audio.
   - It may access only a minimal identity/session endpoint and a clearly labelled QA landing shell, plus read-only readiness checks specifically designed for synthetic QA.
   - Any endpoint not explicitly allow-listed must deny synthetic sessions by default. Do not rely on a list of routes that happen to remember to block QA users.

6. **Expiry and cleanup**
   - Give each synthetic identity a short maximum lifetime (default 24 hours, configurable only within a strict upper bound).
   - Provide owner-only revoke/cleanup with CSRF and audit logging.
   - Cleanup must revoke sessions and outstanding tokens before deleting the synthetic identity; it must never cascade into non-synthetic records.
   - Expired identities must be rejected at authentication even if cleanup has not yet run.

## Required implementation and acceptance tests

- Feature flags off in development, production and default staging configuration: route unavailable.
- Wrong environment or missing flag: route unavailable.
- Anonymous, non-admin, wrong-permission and missing/invalid-CSRF requests denied.
- Request cannot choose recipient, class, role, consent, expiry or arbitrary account attributes.
- Only the configured QA mailbox can receive an invitation.
- Stored verification token is a digest; raw token never appears in response, database, logs or audit metadata.
- Expired, consumed, revoked and malformed tokens cannot verify.
- Verification does not create or alter guardian-consent records or privacy/terms acceptance records.
- Synthetic marker is visible to authentication middleware and cannot be removed through profile updates.
- Synthetic identity can authenticate only after verification; session and CSRF cookies retain existing security properties.
- Synthetic session is denied by default on every learner-data and write endpoint; allow-listed QA shell and identity checks work.
- Real learner identity and normal authentication behavior are unchanged.
- Expiry, revocation, cleanup, audit trail, rate limits, duplicate-email and concurrent issuance are tested against disposable PostgreSQL.
- Browser acceptance runs against disposable synthetic fixtures in CI first. Live staging acceptance is a separate later gate and must not create real learner records.

## Deployment sequence

1. Implement migration, service, narrow admin route, middleware allow-list, cleanup path and tests on `secondary-school-platform-foundation`.
2. Run full unit/security, migration replay/idempotency, PostgreSQL integration and browser CI.
3. Review the migration and route diff for consent isolation and default-deny access.
4. Obtain explicit staging-promotion approval before applying the migration or deploying the code to Render.
5. Provision one synthetic identity through the owner-only flow, verify invitation delivery, perform read-only authenticated browser acceptance, then revoke and confirm cleanup.
6. Keep public student registration disabled throughout. Production remains blocked pending all independent safeguarding, legal, curriculum, security and operational approvals.

## Current blockers

- No synthetic marker, provisioning route, verification purpose, expiry/revocation lifecycle or synthetic-session access boundary exists yet.
- The current registration function writes privacy-notice and terms acceptance records, so it must not be called by a QA provisioning route.
- Staging currently has no student rows. No synthetic identity has been created.
- Authenticated browser acceptance against live staging remains blocked until this design is implemented, CI-tested, approved for staging, and exercised through the owner-only lifecycle.
