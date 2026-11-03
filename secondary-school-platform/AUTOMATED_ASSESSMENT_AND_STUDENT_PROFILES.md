# Student accounts, profiles and automated assessment specification

## Product decision
The platform should operate without the owner manually marking student work, calculating marks or sending individual scores. Assessment delivery, objective grading, score calculation, result release and notifications are automated services.

## Student account and profile
Provide a modern learner account with:
- Email address and verified email sign-in/recovery.
- Unique username/handle and display name.
- SS1, SS2 or SS3 class selection.
- Optional profile photo, uploaded to private object storage and served through controlled URLs.
- Optional short bio (maximum 240 characters).
- Learning dashboard, purchased topics, saved lessons, lesson progress, assessment history, certificates/badges where earned, and notification preferences.
- Profile visibility private by default. Public/classmate visibility must be an explicit opt-in and disabled for minors unless safeguarding/legal review approves it.
- No public directory, direct messaging, follower graph or social feed in the initial release. A social-style profile must not expose a minor's email, phone, exact birth date, home address or school location.

## Data minimisation and reuse
Collect only what is needed for account security, class placement, learning, payment fulfilment and safeguarding. Do not collect full date of birth, home address, phone number or school name unless a documented feature requires it.
Guardian contact/consent should be captured only where required by the age and legal assessment. Do not assume a student's consent is sufficient for every minor's processing.
Student information must not silently become a marketing list or be reused for unrelated future products. Any optional marketing or external reuse must be separate, specific, unbundled, revocable consent. The default is no external reuse. Publish a privacy notice, retention schedule, export/correction/deletion process and breach-response plan before launch. Confirm Nigerian privacy and child-data requirements with qualified counsel.

## Automated assessment behaviour
1. Teachers/admins author question sets and answer keys in the CMS. The answer key is private server-side data and is never returned to student clients.
2. Only reviewed/published assessment versions are made available to students.
3. Students start an attempt; the server enforces attempt limits and, when configured, timing.
4. Answers are submitted to the server. The server grades them using the stored answer key, not browser JavaScript or a client-supplied score.
5. The system calculates awarded points, percentage, pass/fail, attempt number and feedback.
6. The result is released automatically after submission (or according to the configured release rule), saved to the student's assessment history and shown in the dashboard.
7. In-app/email notification is queued and delivered by background workers with retries and idempotency.
8. Analytics update automatically: class/subject/topic performance, question difficulty, completion, average score and common misconceptions.
9. Students can review explanations and, where enabled, request a recheck/report a faulty question. Disputed/faulty items go to a review queue; this is an exception workflow, not routine marking.

## Safe auto-grading scope
Fully automatic deterministic grading is suitable initially for:
- Single-choice MCQ.
- Multiple-select with explicit scoring rules.
- True/false.
- Numeric answers with defined tolerance, units and accepted formats.
- Short exact-answer text with carefully defined normalisation/accepted alternatives.

Do not promise reliable automatic marking of essays, long-form explanations, handwritten work, diagrams or open-ended proofs in the first release. Those require a separately validated rubric-based AI assessment service, bias/accuracy testing, student disclosure and an appeal route. Keep them out of automatically graded high-stakes results until validated. The first release can be fully automated for objective quizzes and practice tests.

## Reliability and integrity
- Server-side grading and score calculation only.
- Use immutable assessment versions; do not change an answer key for an attempt already started.
- Store per-question answers and awarded points for auditability.
- Enforce ownership checks so students can access only their own attempts/results.
- Prevent duplicate submission and duplicate notification.
- Handle timeouts, reconnects and interrupted attempts safely.
- Use rate limits, question/option shuffling and reasonable anti-cheating controls; do not claim these prevent all cheating.
- Keep a full audit trail for admin changes to questions, answer keys, scores and overrides.
- Automated grading should be deterministic and explainable for objective question types.

## Owner operations
The owner gets a management dashboard, not a manual marking queue:
- Automated enrolment, assessment, grading and result notifications.
- Exception alerts for failed email delivery, suspected question defects, payment reconciliation and technical errors.
- Aggregated analytics and exportable reports.
- Admin review only for disputes, flagged questions, abuse, safeguarding and operational exceptions.

## Cost and implementation approach
Start with a low-cost architecture: static frontend hosting, managed PostgreSQL free tier where suitable, small Flask API service, private object storage, and background jobs using a free/low-cost queue or scheduled worker. Free tiers may sleep, pause, have storage/egress limits or no uptime guarantees; test actual provider limits before launch. Keep the app portable and avoid proprietary lock-in. Do not purchase paid services or deploy production without owner approval.

## Acceptance tests
- Student can create and verify account, upload/remove profile image, edit bio and change privacy settings.
- Student can only view/edit their own profile and own results.
- A published objective assessment can be started, submitted, graded server-side and released without admin action.
- Correct, incorrect, partial-credit and unanswered responses produce expected marks.
- Repeated submission does not create duplicate attempts/results.
- Answer keys never appear in student API payloads or browser source.
- Notifications retry safely and do not duplicate.
- Student can see score, percentage, pass/fail, explanations and attempt history.
- Student can report a suspected faulty question.
- Owner analytics aggregate automatically without exposing unnecessary student personal data.
- Privacy consent is separate from optional marketing/external reuse.
