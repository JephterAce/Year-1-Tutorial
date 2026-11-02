# Learnwise curriculum acquisition and publication workflow

## Target standard

Learnwise targets the NERDC Revised Senior Secondary Education Curriculum (2025 framework) for all three classes and the six selected subjects:

- English Language
- General Mathematics
- Further Mathematics
- Biology
- Chemistry
- Physics

The version key used by the platform is `nerdc_ssec_2025`. This is a platform target, not a claim that every class/cohort transition rule has been confirmed. Cohort applicability is stored separately and remains `pending_official_confirmation` until supported by a direct NERDC source or written confirmation.

Official starting points:

- Revised SSS curriculum landing page: https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
- NERDC e-Curriculum browse page: https://www.nerdc.org.ng/CurriculumView.aspx
- 2025 curriculum implementation press release: https://nerdc.gov.ng/content_manager/pdf_files/Press%20Release%20On%20New%20FG%20Curriculum.pdf
- Approved-subject implementation notice: https://nerdc.org.ng/eCurriculum/Doc/NERDC-approved-subjects-notice.pdf
- Teachers' Aid / institutional access: https://www.nerdc.org.ng/TeachersAid.aspx

Do not bypass portal login, subscriptions, access controls or copyright restrictions. Publicly visible metadata can be used as a discovery aid; full curriculum content requires authorised access and rights review.

## Acquisition order

1. Capture official NERDC source records for each class and each of the six subjects. Record the exact page, section, document version/date, retrieval date, source URL and source checksum where practical.
2. Request authorised SSS1–SSS3 materials and digital reuse permission from NERDC. The public portal may expose only part of the curriculum.
3. Ask partner schools for their current approved term schemes. Store them as school-specific evidence; do not relabel them as universal NERDC term allocations.
4. Have a qualified Nigerian subject teacher validate each topic, subtopic and learning outcome against the source.
5. Create original lesson explanations, examples, questions and media. Do not copy textbook or curriculum prose wholesale without permission.

## Import and review

Use `CURRICULUM_IMPORT_TEMPLATE.csv` and `backend/curriculum_import.py`. The `parse_csv_import()` and `validate_csv_import()` helpers support a no-write dry run before any database integration. The validator checks:

- class and subject scope;
- target curriculum version;
- HTTPS source and source type;
- evidence section and learning-outcome shape;
- whether a term assignment is genuinely official or school-scheme-based;
- teacher approval and rights status before publication.

A row with `school_scheme_required` or `not_assigned` is not a term-specific lesson. Do not guess a term. A row cannot be published until its source is traceable, a named reviewer has approved it, and rights status is known. Official term allocation requires an official NERDC source. School term mapping requires a named school scheme.

## Cohort transition

The platform defaults to the revised 2025 framework as the intended target for SS1, SS2 and SS3. It does not silently declare every current cohort eligible for that framework. The 2025 implementation notice identifies a cycle-based rollout; capture the exact applicability for each intake from authoritative evidence before assigning students. The schema supports multiple versions and cohort-specific applicability without forcing an unsupported assumption.

The database publication guard in migration 010 independently enforces the source/class/subject/version match, reviewer metadata, evidence note, rights status and term mapping rules. This protects against an admin tool or API accidentally bypassing the import validator.\n\n## What remains intentionally empty

Until source capture and teacher review are completed, the class/subject topic catalogue remains empty rather than being populated with guessed topics or guessed term order. Any illustrative UI samples must remain explicitly marked as demo data and must never be represented as official curriculum content.
