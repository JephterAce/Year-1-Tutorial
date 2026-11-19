# Build and release roadmap

## Phase 0 — repository and product foundation
- Isolate new work from the legacy Year 1 bot.
- Keep secrets, databases and audio out of Git.
- Maintain product specification, data model and UI prototypes.
- Exit: branch and files reviewed; legacy service remains unchanged.

## Phase 1 — validated experience and curriculum
- Validate each class/subject/term topic sequence against current NERDC curriculum and sample school schemes.
- Finalise visual system, responsive navigation, catalogue, topic detail, player, checkout and account flows.
- Conduct student/teacher usability review.
- Exit: approved content map and tested designs.

## Phase 2 — secure application backend
- Choose maintained Python API framework and supported deployment.
- Add authentication, role-based admin access and PostgreSQL migrations.
- Add student profiles, catalogue, topic entitlements and audit log.
- Add automated tests and database access controls.
- Exit: authentication and student data isolation tests pass.

## Phase 3 — payments and content delivery
- Implement Paystack initialization and server verification.
- Verify webhook signatures, idempotency, amount/currency/reference and refund/reversal events.
- Use private object storage and short-lived media access URLs.
- Enforce entitlements on the server for every asset request.
- Exit: payment, duplicate webhook, underpayment, revoked access and media access tests pass.

## Phase 4 — Telegram and learning features
- Add a new secondary-school Telegram bot; retain the Year 1 bot separately.
- Link accounts using expiring, one-time tokens; never rely on Telegram username as identity.
- Add optional reminders, receipts and support notifications.
- Add audio resume, quiz attempts, notes and progress.
- Exit: account-linking and notification security tests pass.

## Phase 5 — AI content studio
- Build a repeatable workflow for lesson scripts, teacher narration and two-presenter dialogue.
- Human subject review for factual accuracy and curriculum alignment.
- Test maths/science pronunciation, symbols, units and equations.
- Store versioned approved audio; generate assets once and reuse.
- Exit: sample lessons across all five subjects approved by reviewers.

## Phase 6 — pilot and production
- Deploy staging; run end-to-end tests on Android and low-bandwidth connections.
- Verify privacy notice, terms, refund policy, guardian/safeguarding process and support route.
- Test backup restoration and incident recovery.
- Launch a controlled pilot; measure real storage, bandwidth, API and payment costs.
- Scale only after usage and unit economics are understood.

## Cost guardrails
- Use GitHub Free for source control; avoid storing media in Git or using Actions for heavy audio generation.
- Static frontend can use a free static host.
- Use free managed database only for development/pilot if pause, storage and backup limits are acceptable.
- Keep media storage separate from application hosting; compare egress charges before publishing large audio libraries.
- Avoid always-on free web hosts that sleep or ephemeral disks for payment or student records.
- Do not activate a paid plan or create a new cloud project without checking current account billing and getting owner approval.
- Track monthly fixed cost, variable audio generation cost, storage, egress and payment fees.

## Owner-only inputs needed later
- Brand name/logo and final public contact/support details.
- Approved curriculum/school schemes or permission to use official public sources.
- Paystack live-mode approval and credentials (entered directly into hosting secrets; never sent in chat or committed).
- Telegram bot token for the new secondary-school bot (entered directly into hosting secrets).
- Final approval of lesson prices, refund terms, privacy notice and public launch.
