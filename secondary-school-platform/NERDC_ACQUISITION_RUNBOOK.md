# NERDC revised SSEC acquisition and verification runbook

## Official entry points
- Revised Senior Secondary Curriculum landing page: https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
- NERDC e-Curriculum browse portal: https://www.nerdc.org.ng/CurriculumView.aspx
- NERDC e-Curriculum sign-in/subscription: https://www.nerdc.org.ng/Index.aspx
- Teachers' Aid access: https://www.nerdc.org.ng/TeachersAid.aspx
- Revised curriculum press release (3 September 2025): https://nerdc.gov.ng/content_manager/pdf_files/Press%20Release%20On%20New%20FG%20Curriculum.pdf
- Approved-subjects implementation notice: https://nerdc.org.ng/eCurriculum/Doc/NERDC-approved-subjects-notice.pdf

## Scope and cohort rules
Target the revised 2025 senior secondary framework. The first product library is six subjects: English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics. It does not cover every compulsory subject in the national framework. The 2025/26 revised framework includes compulsory subjects outside this six-subject initial product scope. Do not silently map new SSS1 curriculum to existing SS2/SS3 cohorts: NERDC's implementation notice describes staged implementation at the start of each three-year cycle. Store cohort applicability as pending until source-backed confirmation.

## Acquisition procedure
1. Obtain valid teacher/school e-Curriculum access or written permission from NERDC. Do not bypass authentication, paywalls or access controls.
2. Capture only materials permitted by the licence. Record source title, official URL, access date, page/section, class, subject, version, copyright/permission status and source checksum.
3. Capture SSS1, SSS2 and SSS3 separately for each of the six subjects. Preserve the source's exact topic wording and stated learning outcomes.
4. Record term only where the official source explicitly assigns one. Otherwise leave term unassigned; a school scheme of work must be separately labelled and evidenced.
5. Have a qualified subject teacher independently compare every imported topic/outcome to the source and sign the review.
6. Import using CURRICULUM_IMPORT_TEMPLATE.csv and backend/curriculum_import.py in dry-run mode.
7. Resolve every validation issue, verify provenance and rights, then request publication approval through the admin review process.
8. Keep rejected, superseded and corrected records for traceability; never overwrite source evidence.

## Acquisition register
Track 18 class-subject combinations and all official sections, not an assumed 54 term syllabus. For each section record: requested, access granted, captured, checksum recorded, rights checked, imported, teacher-reviewed, approved, published.

## Contact and access
NERDC general contact published on its site: info@nerdc.gov.ng. e-Curriculum subscription support is listed on the portal. Confirm current contacts and fees directly with NERDC before action. No email, subscription or payment is initiated by this repository workflow.

## Exit criteria
All target class/subject content is source-captured, rights-cleared, teacher-reviewed and versioned; cohort applicability is evidenced; no term allocations are guessed; imported rows pass dry-run and publication guards. Until then the live catalogue must show only approved records and must not present sample content as official curriculum.
