# Timed Assessments and Test Integrity Specification

Status: approved product requirement; implementation pending.
Applies to Learnwise SS1–SS3 assessments across the six selected subjects.

## 1. Student-selected test length and time calculation

Every assessment session is time-limited. Before starting, the student selects the number of questions from the range the assessment author has made available. The server validates the selection and calculates the time limit; the browser must never be the authority for the deadline.

**Standard rate: 36 seconds per question, with one owner-approved exception: 10 questions receive 7 minutes.**
Formula: `time_limit_seconds = question_count * 36`, except `question_count = 10`, which receives 420 seconds.
Display the result as minutes and seconds. Examples:
- 5 questions = 3 minutes
- 10 questions = 7 minutes (explicit exception)
- 20 questions = 12 minutes
- 50 questions = 30 minutes
- 100 questions = 60 minutes

This preserves the examples you supplied while implementing your explicit instruction that a 10-question test lasts 7 minutes. The exception is centralised in the server-side timing policy, not hard-coded into the student interface. Do not silently vary timing by subject or question type.

The student chooses a count, not an arbitrary time. The server returns the selected count, time limit, assessment rules/version, and a signed/opaque attempt identifier. The countdown starts only after the student has read the briefing and explicitly agreed, then presses **Start test**. The deadline is stored server-side and cannot be extended by refreshing, changing the device clock, editing browser code, or reopening a tab.

Assessment authors configure allowed question-count choices, question pool, pass mark, attempt policy, and availability. The system randomly selects the requested number from the eligible published pool, with controlled topic/difficulty coverage where configured. It must not create more questions than are available. Each attempt receives a shuffled question order and, where safe, shuffled answer options. Questions and answer keys are versioned; an attempt remains tied to the exact immutable version it started with.

## 2. Mandatory pre-test briefing and affirmative agreement

Before **every** test, show a dedicated briefing screen, not a small dismissible tooltip. It must state:
- subject, assessment title, class, selected question count, and calculated time;
- the standard 36-seconds-per-question rule, the 10-question/7-minute exception, and a worked calculation;
- when the timer starts and that it continues while the student changes tabs or loses focus;
- that expiry submits the answers saved by the server automatically;
- whether unanswered questions receive zero and whether negative marking applies;
- whether navigation between questions and answer changes are allowed;
- the number of permitted focus/fullscreen-exit incidents (three; termination occurs on the third);
- the restricted actions and what happens when a warning is triggered;
- that attempts are logged for integrity and technical troubleshooting;
- that no system can guarantee detection of a second device, external camera, or every operating-system/browser behaviour;
- how to report a technical issue or challenge an incorrect integrity flag.

Require an unchecked checkbox labelled **I have read and agree to the test rules**. Keep **Start test** disabled until checked. Record the policy version, student, attempt, timestamp, and affirmative agreement server-side. Agreement is per attempt; it is not a blanket consent for future tests.

## 3. Focus and interface-leaving policy

Use browser-supported signals as deterrence and audit evidence:
- request fullscreen when the test starts where the browser/device supports it;
- listen for Page Visibility changes, fullscreen exit, and window focus loss;
- prevent common in-page copy, cut, paste, context-menu, and text-selection actions on the question/answer area during an active test;
- warn when a focus-loss/visibility/fullscreen incident is detected;
- keep an incident counter on the server and display the current count and remaining allowance;
- on the third qualifying incident, automatically end the attempt and submit answers already persisted on the server.

Do not count every raw browser event as a separate incident. Debounce correlated events from one transition (for example, fullscreen exit and visibility change caused by the same tab switch) into one incident. Define and test a short configurable debounce window. Ignore events during the initial fullscreen request and known internal navigation. Do not count normal movement between questions within the test.

The policy is three incidents total: first and second incidents warn; the third terminates. The timer does not pause during warnings, focus loss, or temporary disconnection. Persist answers as the student works so that a termination or expiry can grade the last safely received answers. Show a clear termination explanation and provide an appeal/report-technical-problem route.

**Fairness safeguard:** browser focus signals are imperfect. Notifications, incoming calls, accessibility tools, device/browser limitations, and accidental taps can cause false positives. Treat the third incident as an automatic test termination, but record the result as **integrity review required**, not a conclusive finding of cheating. Preserve event timestamps and evidence; allow an appeal. Do not automatically impose account bans or academic misconduct penalties based only on client-side signals.

## 4. Honest technical limits

A normal website cannot make questions impossible to copy, photograph, transcribe, search, or send to an AI. Browser controls can block common copy/paste shortcuts and deter casual switching, but cannot prevent screenshots, another phone/computer, browser extensions, developer tools, OS-level capture, or a determined user. Do not advertise this as foolproof anti-cheating.

Use layered deterrence instead:
- question and option randomisation from a sufficiently large question bank;
- per-attempt variants and values where pedagogically valid;
- server-side answer-key isolation and grading;
- no answer keys or grading logic in frontend payloads;
- signed/opaque attempt identifiers and server-enforced deadlines;
- rate limits, idempotent submissions, and audit events;
- question watermarking with a non-sensitive attempt reference where appropriate;
- anomaly flags for unusual answer timing/patterns, for human review only;
- accessible test mode that does not rely on blocking assistive technology.

No hidden surveillance, webcam/microphone recording, device fingerprinting, or invasive collection is authorised by this specification. Any future proctoring feature requires separate privacy, child-safeguarding, accessibility and legal review, explicit notice, and owner approval.

## 5. Server-side state machine and reliability

Recommended attempt states: `briefing`, `in_progress`, `submitted`, `expired`, `terminated_integrity`, `under_review`, `graded`.

- Server creates the attempt and deadline only after valid agreement and start.
- Server validates every answer update against attempt ownership, status, question membership and deadline.
- Use server time (UTC) for all deadlines; never trust client timestamps.
- Auto-save answers with idempotent writes and safe retry behaviour.
- Submission, timeout, and third-incident termination must be atomic and idempotent; only one terminal transition may win.
- A background expiry worker is useful, but the API must also enforce expiry whenever an attempt is read or submitted, so worker delays cannot grant extra time.
- On timeout, grade the persisted answers. Late requests cannot change the attempt.
- If connectivity is lost, show a reconnection warning; the server timer continues. Reconnect should restore the same attempt and remaining server-calculated time, not create a fresh attempt.
- A client-only countdown is display assistance; it is not enforcement.
- Store event types, server receipt times, policy version and concise metadata. Avoid retaining unnecessary device or network data.

## 6. Results and owner workload

For objective question types with authored scoring rules, grade on the server immediately after submission/expiry/termination. Store score, maximum score, percentage, pass/fail, explanations, question-version reference and result-release timestamp. Notify the student in-app and by email when delivery is configured. Routine grading and score sending must not require the owner.

An attempt terminated by the integrity threshold is graded from saved answers but visibly marked **Integrity review required**. Do not hide the score from the student indefinitely; explain the status and provide an appeal route. Owner/admin dashboard should surface exceptions (appeals, suspicious signals, faulty questions, delivery failures), not require routine marking.

Essays, handwriting, diagrams and open-ended proofs remain outside deterministic auto-grading until a separately validated rubric-based system is approved.

## 7. Accessibility, device support and student protection

- Provide clear, keyboard-accessible instructions and controls.
- Do not disable screen readers or essential assistive technologies.
- Explain if fullscreen/focus monitoring is unavailable on a device; use an explicitly defined compatible mode rather than silently pretending it is enforced.
- Test current Android mobile browsers, iOS Safari, desktop Chrome/Firefox/Edge, small screens, low bandwidth and interrupted connectivity.
- A student must be able to report a call/notification/accessibility-triggered false positive.
- Keep integrity data access restricted to authorised administrators and apply a documented retention period.
- Since students may be minors, publish understandable privacy information and complete child-safeguarding/data-protection review before launch.

## 8. Acceptance tests

1. Five, ten, fifty and one hundred questions calculate to 180, 360, 1,800 and 3,600 seconds respectively.
2. A student cannot start until the briefing checkbox is selected.
3. The server stores agreement and policy version for each attempt.
4. Refreshing, changing device clock or reopening a tab does not reset the deadline.
5. Server rejects answer writes after terminal state/deadline.
6. Repeated submission and concurrent timeout requests produce one result only.
7. First and second qualifying focus incidents warn; the third ends the attempt once.
8. Correlated visibility/fullscreen/focus events from one transition count as one incident.
9. Normal question navigation does not count as leaving the test.
10. Answers already saved are graded on expiry or termination.
11. Answer keys never appear in student-facing API responses or HTML.
12. The test remains usable with keyboard and supported assistive technology.
13. Unsupported browser signals are disclosed and do not create false claims of protection.
14. Terminated attempts are labelled for review and have an appeal path.
15. Tests cover mobile, desktop, offline/reconnect, timer race conditions and malicious client-side clock manipulation.
