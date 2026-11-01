# Curriculum source register and validation rules

Last checked: 2026-11-01

## Authoritative starting points

1. NERDC New Revised Senior Secondary Education Curriculum (SSEC) landing page:
   https://nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
   The page links separately to SSS 1, SSS 2 and SSS 3 curriculum portals. Treat each class as its own source; do not assume the same topic order or content across classes.

2. NERDC e-Curriculum browse portal:
   https://www.nerdc.org.ng/CurriculumView.aspx
   The portal exposes class-level selection (SSS 1, SSS 2, SSS 3), subject selection, themes, topics and content details. Use it to record exact class/subject/topic mappings.

3. NERDC revised curriculum approved-subject notice:
   https://nerdc.gov.ng/content_manager/Basic%20and%20Senior%20Secondary%20Education%20Curriculum%20Offerings.pdf
   The published senior-secondary offering identifies General Mathematics as a core compulsory subject and lists Biology, Chemistry, Physics and Further Mathematics under Science.

4. NERDC approved-subject notice (alternate official-hosted copy):
   https://nerdc.org.ng/eCurriculum/Doc/NERDC-approved-subjects-notice.pdf

## Scope selected for the first release

- Classes: SS1, SS2, SS3.
- Subjects: General Mathematics, Further Mathematics, Biology, Chemistry and Physics.
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

## Initial evidence captured

- NERDC's SSEC landing page links separate portals for SSS1, SSS2 and SSS3.
- The official approved-subject notice lists General Mathematics as compulsory and Biology, Chemistry, Physics and Further Mathematics within Science.
- The NERDC e-Curriculum browse portal lists the selected subjects and exposes class-specific topic/content browsing.

## Outstanding research work

The full topic-by-topic capture for all 15 class/subject combinations and verified term allocation for each school scheme is not complete. No curriculum content should be marked approved or published solely on the basis of this register.
