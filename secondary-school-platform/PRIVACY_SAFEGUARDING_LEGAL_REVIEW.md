# Privacy, safeguarding and legal release review

This is an engineering control register, not legal advice or a claim of compliance. Obtain review from a Nigerian data-protection practitioner and qualified counsel before collecting real student data.

## Data protection and minors
- Confirm controller/processor roles, lawful bases, purpose limitation and retention for every field.
- Determine age bands and whether parental/guardian authorisation and age-appropriate notices are required.
- Complete a Data Protection Impact Assessment before processing minors' profiles, learning analytics, payments or integrity signals at scale.
- Provide access, correction, export, deletion and complaint channels.
- Keep profiles private by default; no public directory, private adult-to-minor messaging, behavioural advertising or unrelated reuse.
- Optional communications consent must be separate, specific, revocable and off by default.
- Define retention for identity, assessment, integrity, payment, support, logs and backups.
- Document processor agreements, hosting locations, international transfers and subprocessors.
- Establish incident triage, breach assessment, notification decisions and evidence preservation.
- Integrity signals are not misconduct findings; provide human review and appeal.

## Safeguarding
- No unsupervised adult-to-minor private messaging in the initial release.
- Publish a monitored safeguarding contact and escalation process before enrolment.
- Minimise staff access; use named accounts, MFA, least privilege and audit logs.
- Train and appropriately vet staff who can access student records.
- Define reporting, response times and emergency escalation for abuse disclosures.
- Avoid precise location, sensitive documents and unnecessary family information.
- Provide accessibility accommodations for assessment and integrity controls.

## Nigerian legal review topics
Counsel should assess the Nigeria Data Protection Act 2023 and current NDPC guidance, applicable child-protection obligations, consumer/e-commerce terms, payment-provider obligations, intellectual-property licensing, tax/accounting records, accessibility and marketing rules.
Official starting points: https://ndpc.gov.ng/ and https://nerdc.gov.ng/

## Release-blocking evidence
Approved privacy notice, terms and retention schedule; completed DPIA and signed legal review; child safeguarding policy and named lead; processor agreements and hosting/data residency assessment; tested access/correction/export/deletion and incident response; independent security test and remediation sign-off. Do not release while unresolved.


## Engineering update — 7 November 2026

The following technical foundations now exist:
- Student profile privacy defaults and explicit terms/privacy consent capture remain in the account flow.
- Authenticated students can download a scoped JSON copy of their own account, consent, progress, practice, assessment, payment-ledger, entitlement, saved-lesson and rights-request data.
- Migration 019 tracks student access/export, correction, deletion and restriction requests. Students can view and withdraw open requests; authorised support/owner administrators can triage and record a reasoned response.
- A deletion request records intent only. No automatic account or record deletion is performed.
- Authenticated administrator data-rights triage and student self-service controls are included in disposable-fixture browser acceptance.

These controls do **not** establish legal compliance. The export is not yet a streamed/bulk archive workflow; guardian identity/age verification, formal correction/deletion fulfilment, retention schedules, processor contracts, cross-border transfer assessment, DPIA and safeguarding policy approvals remain outstanding. The guardian consent field is not proof of verified guardian consent. Obtain counsel and safeguarding-lead sign-off before enabling real student registration.
