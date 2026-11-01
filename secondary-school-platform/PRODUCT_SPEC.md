# Product specification

## Audience and promise
A clear, welcoming, low-bandwidth learning environment for Nigerian senior secondary learners in SS1–SS3. A learner should be able to find a topic, understand what is included, pay safely, listen, practise and continue later.

## Catalogue
Class × subject × term × topic. Initial subjects are Mathematics, Further Mathematics, Biology, Chemistry and Physics. The 45 class/subject/term combinations are catalogue containers, not a claim that every school follows the same topic order. Verify each sequence against the current NERDC curriculum and representative school schemes before publication.

## Student journey
1. Select class and create an account.
2. Browse/search subjects, terms and topics.
3. Preview objectives, formats, duration and sample.
4. Buy a topic or clearly described bundle.
5. Verify payment server-side with Paystack.
6. Grant the exact topic entitlement only after verified payment.
7. Listen in an authenticated player; resume progress and access included notes/quizzes.
8. Optionally link Telegram for reminders and service notifications.
9. Review progress, quiz attempts and receipts.

## Content model
Each topic may include teacher narration, two-presenter podcast, transcript, notes, worked examples, worksheet and quiz. Workflow: source material → learning objectives → script → subject review → voice production → technical pronunciation QA → mastering → approval → publication. Maths/science QA must cover equations, units, symbols, chemical notation and factual accuracy. Generate once and reuse; do not regenerate audio per playback.

## Pricing and payments
Configurable topic prices with ₦1,000 minimum. Store NGN amounts as integer kobo. Never trust browser-supplied prices. Unique payment reference tied to student and product; verify status, reference, amount and currency directly with Paystack; validate webhook signatures; process events idempotently; handle failed, pending, refunded and reversed payments. Browser redirect alone never unlocks content.

## UX requirements
Mobile-first, responsive, accessible, fast and low-bandwidth friendly. Search and class/subject/term filters; clear free-preview, locked, purchased and completed states; continue-learning area; player speed/seek/resume; transcript/notes; accessible labels; loading, empty, offline, pending, failed and error states. No fabricated testimonials, ratings, counters or payment-success states.

## Admin
Role-based content editor, curriculum/topic management, script/audio/notes uploads, version history, review/approve/publish, pricing and bundles, payment/refund/entitlement ledger, audited support overrides, analytics and MFA.

## Privacy and safeguarding
Learners may be minors. Minimise collected data; define retention/deletion, guardian contact approach, staff access controls and incident response; review applicable Nigerian privacy and child-data requirements before public launch.

## Launch gates
Curriculum reviewed; subject experts approve scripts/audio; payment duplicate/underpayment/refund tests pass; student entitlement isolation passes; audio storage remains private; backup/restore tested; accessibility/mobile/low-bandwidth QA passes; privacy notice, terms, refund policy and support contact are published.
