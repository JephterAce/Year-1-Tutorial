# Private audio delivery

## Required architecture
1. Keep original masters and encoded files in a private object-storage bucket. Disable public ACLs and listing.
2. Keep bucket credentials on the server. Students never receive storage credentials.
3. Authenticate the student; verify the topic is published and an active entitlement exists.
4. Issue a resource-scoped signed token with a maximum five-minute lifetime.
5. An authenticated media gateway validates signature, audience, expiry and resource key, then streams with byte-range support.
6. Restrict CORS to the Learnwise origin; set correct MIME type, nosniff and private cache controls.
7. Log resource ID, pseudonymous student ID, decision and request ID—not token values or media contents.
8. Revoke by removing entitlement or rotating signing keys; tokens expire quickly.

## Implemented foundation
backend/audio_media.py issues and verifies HMAC-SHA256 resource tokens. It does not expose a public bucket or claim to stream media. A production adapter must check entitlements against PostgreSQL at issuance and connect to a private S3-compatible store or equivalent.

## Upload and publication
Validate MIME type, file size, codec, checksum and malware scan. Use immutable object keys; corrections create new versions. Keep transcript, source rights, consent and reviewer approval with the asset metadata. Never place private audio in Git or public frontend directories.
