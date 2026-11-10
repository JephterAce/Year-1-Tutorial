# Curriculum source register and validation rules

Last checked: 2026-11-02

## Authoritative starting points

1. NERDC New Revised Senior Secondary Education Curriculum (SSEC) landing page:
   https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
   The page links separately to SSS 1, SSS 2 and SSS 3 curriculum portals. Treat each class as its own source; do not assume the same topic order or content across classes.
   - SSS 1: https://lmis.nerdcportals.com.ng/sss_1
   - SSS 2: https://lmis.nerdcportals.com.ng/sss_2
   - SSS 3: https://lmis.nerdcportals.com.ng/sss_3

2. NERDC e-Curriculum browse portal:
   https://www.nerdc.org.ng/CurriculumView.aspx
   The portal exposes class-level selection (SSS 1, SSS 2, SSS 3), subject selection, themes, topics and content details. Use it to record exact class/subject/topic mappings.

3. NERDC revised curriculum approved-subject notice:
   https://nerdc.gov.ng/content_manager/Basic%20and%20Senior%20Secondary%20Education%20Curriculum%20Offerings.pdf
   The published senior-secondary offering identifies English Language and General Mathematics among the five core/compulsory subjects, and lists Biology, Chemistry, Physics and Further Mathematics under Science. The other three core subjects are one trade subject, Citizenship and Heritage Studies, and Digital Technologies. This product is not a complete school subject package.

4. NERDC approved-subject notice (alternate official-hosted copy):
   https://nerdc.org.ng/eCurriculum/Doc/NERDC-approved-subjects-notice.pdf

## Scope selected for the first release

- Classes: SS1, SS2, SS3.
- Subjects: English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics.
- NERDC groups: English Language and General Mathematics are core/compulsory; Biology, Chemistry, Physics and Further Mathematics are in the Science field.
- Term labels in our product: First, Second and Third term.
- Pricing floor: NGN 1,000 per topic. The production database stores NGN amounts in kobo; a minimum of 100,000 kobo represents NGN 1,000.

This is a product scope, not evidence that every topic is taught in the same term by every school.

## Mandatory curriculum mapping process

For every class and subject:

1. Open the official class-specific NERDC SSEC portal.
2. Select the exact subject and capture the theme, topic, subtopic/content detail, learning outcomes and any practical/assessment expectations.
3. Record the source URL, document title/version/date, retrieval date and page/section where available.
4. Map topics to First/Second/Third term only when supported by an official term allocation or a current school scheme of work. Otherwise mark the term allocation `school_scheme_required` and do not publish it as a universal national term sequence.
5. Draft lesson objectives and teaching scripts from the verified learning outcomes. Keep the original curriculum wording in source notes, not as a substitute for an original lesson.
6. Have a qualified subject teacher review accuracy, level, worked examples, experiments/safety, and assessment alignment.
7. Have a second reviewer check maths/science notation, units, equations and audio pronunciation.
8. Publish only after review approval; retain source/version and reviewer audit records.

## Data status vocabulary

- `unresearched`: no official source inspected.
- `source_captured`: official curriculum source and version recorded.
- `mapped`: topics and outcomes mapped to this class/subject.
- `term_pending`: term allocation needs school scheme confirmation.
- `teacher_review`: subject specialist review outstanding.
- `approved`: curriculum and editorial checks passed.
- `published`: released to students.

## Release integrity rules

- Never invent a topic list or claim a topic is NERDC-approved without a traceable source.
- Never infer term placement from a textbook, a different class, an old scheme or another school's sequence.
- Keep General Mathematics distinct from Further Mathematics in catalogues, scripts and prices.
- Record school-specific scheme variants where necessary instead of overwriting the national curriculum mapping.
- Do not ingest or republish copyrighted textbook pages or paid school materials without permission. Use official curriculum outcomes and create original explanations, examples, diagrams and audio.

## Revised curriculum structure confirmed

The Federal Ministry of Education press release dated 3 September 2025 states that the revised senior-secondary structure takes effect in the 2025/26 academic year and retains 8–9 subjects, with five core/compulsory subjects. These include English Language and General Mathematics; the other core subjects are one trade subject, Citizenship and Heritage Studies and Digital Technologies. The Science field includes Biology, Chemistry, Physics and Further Mathematics.

NERDC provides separate revised SSS1, SSS2 and SSS3 curriculum links. The e-Curriculum browser offers class selection and lists all six requested subjects. Its browse page is dynamic; a visible sample topic sequence must not be treated as a complete class-by-class term scheme.

## Initial evidence captured

- NERDC's SSEC landing page links separate portals for SSS1, SSS2 and SSS3.
- The official approved-subject notice lists English Language and General Mathematics among the core/compulsory subjects and Biology, Chemistry, Physics and Further Mathematics within Science.
- The NERDC e-Curriculum browse portal lists the selected subjects and exposes class-specific topic/content browsing.

## Outstanding research work

The full topic-by-topic capture for all 18 class/subject combinations and verified term allocation for each school scheme is not complete. Automated retrieval of the linked SSEC detail pages returned access errors in this research session, so the links are recorded for authorised manual/teacher access rather than pretending the topics have been captured. No curriculum content should be marked approved or published solely on the basis of this register.


## Current official evidence URLs
- Federal Ministry of Education press release (3 September 2025): https://nerdc.gov.ng/content_manager/pdf_files/Press%20Release%20On%20New%20FG%20Curriculum.pdf
- NERDC revised SSEC landing page: https://www.nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
- NERDC e-Curriculum browse page: https://nerdc.org.ng/CurriculumView.aspx


## Public-source verification update — 2026-11-02

Official pages have now been checked directly:

- The NERDC SSEC landing page links to three separate class portals (SSS1, SSS2, SSS3): https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
- The NERDC e-Curriculum browse page exposes SSS1–SSS3 selectors and all six selected subjects. Its rendered page shows a sample General Mathematics theme/topic sequence, but the dynamic page is not a complete export of all class/topic/content records: https://www.nerdc.org.ng/CurriculumView.aspx
- The Federal Ministry of Education's 3 September 2025 press release says the revised curriculum takes effect in 2025/26, SSS students select 8–9 subjects, and identifies five core/compulsory subjects: English Language, General Mathematics, one trade subject, Citizenship and Heritage Studies, and Digital Technologies. Biology, Chemistry, Physics and Further Mathematics are in the Science field: https://nerdc.gov.ng/content_manager/pdf_files/Press%20Release%20On%20New%20FG%20Curriculum.pdf
- NERDC's 8 September 2025 approved-subject notice confirms the revised subject offering and says implementation begins at the start of each three-year cycle, including SS1: https://nerdc.org.ng/eCurriculum/Doc/NERDC-approved-subjects-notice.pdf
- NERDC e-Curriculum explains that full digital access/Teachers' Aid is associated with school access/subscription. Contact shown by NERDC: subscription@nerdc.org.ng and 08069234214. General NERDC site contact: info@nerdc.gov.ng; +2347081361390 / +2348036656492.

### Important transition and product implications

1. The revised 2025/26 senior-secondary framework is now the starting point for new SS1 cohorts. Do not silently apply the revised SS1 structure to all existing SS2/SS3 cohorts; retain cohort/curriculum-version metadata and verify the transition rules for those cohorts with NERDC and the relevant school/state education authority.
2. Learnwise's six-subject learning library remains a valid product scope, but must not be represented as the complete compulsory SSS subject package. Biology, Chemistry, Physics and Further Mathematics are Science-field subjects, not all five compulsory subjects.
3. Curriculum content and school term schemes are different layers. Keep topic coverage separate from First/Second/Third-term placement. Term mapping must cite a school scheme or official term allocation.
4. Next source-acquisition step: request access to the class-specific SSS curriculum and full content details from NERDC; if digital access is subscription-controlled, obtain an authorised school/teacher account or a written official extract/permission. Never bypass login or access controls.
