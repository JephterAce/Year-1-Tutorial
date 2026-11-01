# Senior Secondary Audio Learning Platform

A new SS1–SS3 learning product, isolated from the existing Year 1 Telegram subscription bot.

## Product scope
- Classes: SS1, SS2, SS3
- Initial subjects: Mathematics, Further Mathematics, Biology, Chemistry, Physics
- Terms: First, Second, Third
- Lesson formats: teacher-led audio and two-presenter educational podcast
- Student experience: discover, preview, purchase, listen, practise, resume and revise
- Admin experience: curriculum, content, pricing, publishing, support and reporting

## Protection of the existing service
All new work lives under this directory and on `secondary-school-platform-foundation`. The root-level legacy bot and its live configuration are not modified. Do not deploy this prototype over the existing service.

## Current implementation status
- [x] GitHub write access and isolated branch verified
- [x] Product specification and initial relational data model
- [x] Mobile-first student portal prototype
- [ ] Backend authentication and student accounts
- [ ] Curriculum data reviewed against current NERDC and school schemes
- [ ] Paystack server-side checkout, verification and webhook processing
- [ ] Secure audio storage and authenticated playback
- [ ] Telegram account linking and notifications
- [ ] Admin content studio and reporting
- [ ] Automated tests, security review, backups and production deployment

## Run the UI prototype
Open `frontend/index.html` in a browser. It is a static demonstration using sample catalogue data. It does not process payments, authenticate users, store real student records or deliver protected audio.

## Architecture direction
Static frontend on a free static host; Python API; managed PostgreSQL; private object storage/CDN for audio; Paystack for Nigerian payments; Telegram for notifications/account linking. Choose production providers only after validating current free-tier limits, data retention, backups and actual traffic costs.

## Safety and trust
- Never commit API keys, bot tokens, payment secrets, student data or private audio.
- Verify all payment details server-side and make webhook processing idempotent.
- Grant access only to the exact purchased topic.
- Keep storage private; use short-lived authenticated media URLs.
- Many learners may be minors: minimise data and complete privacy/child-safety review before launch.
- Do not claim audio is impossible to record; external recording cannot be fully prevented.
