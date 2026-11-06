# Think Tank curriculum population plan

## Scope

The initial product catalogue contains six subjects across SS1, SS2 and SS3: English Language, General Mathematics, Further Mathematics, Biology, Chemistry and Physics. The 18 subject/class combinations are recorded in `CURRICULUM_SOURCE_REGISTER.csv`.

## Official source entry points

- NERDC revised Senior Secondary Education Curriculum home: https://www.nerdc.gov.ng/content_manager/new_senior_curriculum_home.html
- Revised SSS1 core and compulsory subject listing: https://lmis.nerdcportals.com.ng/s1_core
- Revised SSS1 science subject listing: https://lmis.nerdcportals.com.ng/s1_science
- Revised SSS2 core and compulsory subject listing: https://lmis.nerdcportals.com.ng/s2_core
- Revised SSS2 science subject listing: https://lmis.nerdcportals.com.ng/s2_science
- NERDC e-Curriculum subject/class browse: https://www.nerdc.org.ng/CurriculumView.aspx
- NERDC approved subject offering notice: https://nerdc.gov.ng/content_manager/Basic%20and%20Senior%20Secondary%20Education%20Curriculum%20Offerings.pdf

The SSS1 revised portal lists English Language and General Mathematics under core/compulsory subjects and Further Mathematics, Biology, Chemistry and Physics under science subjects. The source register marks the actual curriculum document and topic capture as outstanding; a subject listing alone is not a syllabus.

## Important cohort/transition control

The Federal Ministry of Education/NERDC announcement dated 3 September 2025 states that the revised curriculum is introduced at the beginning of a three-year education cycle, including SS1. Therefore the platform must not automatically label every SS1, SS2 and SS3 learner as following the same revised 2025 sequence. Confirm the learner cohort and the applicable curriculum version for each class before assigning topics. The revised SSS2 core/science subject listing pages are now accessible and have been added to the register, but their individual subject curriculum PDFs still require capture. NERDC lists SSS3 as a revised curriculum level on its official home page, but a class-specific SSS3 subject page/PDF was not retrievable during this audit; that track remains pending.

## Publication rules

1. Capture the actual subject/class curriculum document and exact section/page/topic reference.
2. Record the source URL, version/date, checksum where possible, and licence/permission status.
3. Map topics to a class and term only where the official document or a verified school scheme supports it.
4. Author original explanatory notes, worked examples, practice and podcast scripts; do not reproduce protected source text wholesale.
5. Obtain qualified subject-teacher review and record reviewer/date.
6. Publish only after source evidence, rights metadata, class mapping, review and QA pass the database publication guard.

## Current status

- Six subject records exist in the staging database; the last verified topic count was zero.
- This register creates a traceable 18-track work queue only. It does not insert topics, claim syllabus completeness, assign term placement or publish student-facing content.
- The curriculum import validator and database publication guard are retained. The new reviewed lesson-content and podcast workflow requires approved content before student access or podcast generation.


## Source capture progress update

The official October 2025 Biology SSS1 curriculum PDF has now been captured and indexed at:

- https://lmis.nerdcportals.com.ng/sss_1/necurrdc/6.pdf

Its overview/table of contents identifies 20 Biology SSS1 topic headings across Biology and Scientific Enquiry, Organization of Life and Biochemical Processes, Society and Environmental Biology, and Health and Diseases. The topic map is in `content/curriculum-drafts/biology/SS1_TOPIC_MAP.md`. One original lesson draft, Laboratory Safety Rules, has been prepared in `content/curriculum-drafts/biology/SS1/laboratory-safety-rules.lesson.json`. Both are drafts; no term allocation is inferred and no student-facing lesson has been published.

The other five subject PDFs and the SS2/SS3 cohort-specific documents still need to be captured and indexed. Do not infer their topic sequences from the Biology file or from an older curriculum edition.
