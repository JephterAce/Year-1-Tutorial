-- Track authorised student-data exports without storing exported student records in the app database.
-- Files are written to private object storage by a worker; never to the source repository.
CREATE TABLE student_data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by_admin_id UUID NOT NULL REFERENCES admin_users(id),
    target_student_id UUID REFERENCES students(id),
    export_scope TEXT NOT NULL CHECK (export_scope IN ('individual', 'bulk')),
    export_format TEXT NOT NULL CHECK (export_format IN ('json', 'csv')),
    filters JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'expired', 'cancelled')),
    record_count BIGINT CHECK (record_count IS NULL OR record_count >= 0),
    storage_key TEXT,
    checksum_sha256 CHAR(64),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    failure_code TEXT,
    CONSTRAINT individual_export_requires_student
        CHECK (export_scope <> 'individual' OR target_student_id IS NOT NULL),
    CONSTRAINT bulk_export_has_no_single_target
        CHECK (export_scope <> 'bulk' OR target_student_id IS NULL),
    CONSTRAINT completed_export_requires_storage
        CHECK (status <> 'completed' OR (storage_key IS NOT NULL AND expires_at IS NOT NULL))
);

CREATE INDEX student_data_exports_requester_idx
    ON student_data_exports(requested_by_admin_id, requested_at DESC);
CREATE INDEX student_data_exports_target_idx
    ON student_data_exports(target_student_id, requested_at DESC)
    WHERE target_student_id IS NOT NULL;
CREATE INDEX student_data_exports_status_idx
    ON student_data_exports(status, requested_at)
    WHERE status IN ('queued', 'processing');

-- Explicit export audit trail; do not put student data or download URLs in event details.
CREATE TABLE student_data_export_audit (
    id BIGSERIAL PRIMARY KEY,
    export_id UUID NOT NULL REFERENCES student_data_exports(id),
    actor_admin_id UUID NOT NULL REFERENCES admin_users(id),
    event_type TEXT NOT NULL CHECK (event_type IN (
        'requested', 'authorised', 'started', 'completed',
        'downloaded', 'failed', 'expired', 'cancelled'
    )),
    source_ip INET,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX student_data_export_audit_export_idx
    ON student_data_export_audit(export_id, created_at);
