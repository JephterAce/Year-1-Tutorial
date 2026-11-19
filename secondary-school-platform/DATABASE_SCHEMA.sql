-- Initial PostgreSQL schema; deploy only through reviewed migrations.
CREATE TABLE students (
 id UUID PRIMARY KEY, email TEXT UNIQUE, display_name TEXT NOT NULL,
 class_level TEXT NOT NULL CHECK (class_level IN ('SS1','SS2','SS3')),
 telegram_user_id BIGINT UNIQUE, guardian_email TEXT,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE subjects (
 id UUID PRIMARY KEY, slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
 description TEXT, sort_order INTEGER NOT NULL DEFAULT 0, is_active BOOLEAN NOT NULL DEFAULT false
);
CREATE TABLE terms (
 id UUID PRIMARY KEY, term_number SMALLINT NOT NULL UNIQUE CHECK (term_number BETWEEN 1 AND 3),
 label TEXT NOT NULL
);
CREATE TABLE topics (
 id UUID PRIMARY KEY, subject_id UUID NOT NULL REFERENCES subjects(id),
 class_level TEXT NOT NULL CHECK (class_level IN ('SS1','SS2','SS3')),
 term_id UUID NOT NULL REFERENCES terms(id), slug TEXT NOT NULL, title TEXT NOT NULL,
 summary TEXT, learning_objectives JSONB NOT NULL DEFAULT '[]'::jsonb,
 price_kobo BIGINT NOT NULL CHECK (price_kobo >= 100000), currency CHAR(3) NOT NULL DEFAULT 'NGN',
 estimated_minutes INTEGER, sort_order INTEGER NOT NULL DEFAULT 0,
 status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','review','published','archived')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 UNIQUE(subject_id,class_level,term_id,slug)
);
CREATE TABLE lesson_assets (
 id UUID PRIMARY KEY, topic_id UUID NOT NULL REFERENCES topics(id),
 asset_type TEXT NOT NULL CHECK (asset_type IN ('teacher_audio','podcast_audio','transcript','notes','worksheet','cover')),
 storage_key TEXT NOT NULL, mime_type TEXT, duration_seconds INTEGER, version INTEGER NOT NULL DEFAULT 1,
 review_status TEXT NOT NULL DEFAULT 'pending' CHECK (review_status IN ('pending','approved','rejected')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), UNIQUE(topic_id,asset_type,version)
);
CREATE TABLE payment_transactions (
 id UUID PRIMARY KEY, student_id UUID NOT NULL REFERENCES students(id), topic_id UUID NOT NULL REFERENCES topics(id),
 provider TEXT NOT NULL DEFAULT 'paystack', provider_reference TEXT NOT NULL UNIQUE,
 amount_kobo BIGINT NOT NULL CHECK (amount_kobo > 0), currency CHAR(3) NOT NULL DEFAULT 'NGN',
 status TEXT NOT NULL CHECK (status IN ('initialized','pending','successful','failed','refunded','reversed')),
 provider_payload JSONB, verified_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE entitlements (
 id UUID PRIMARY KEY, student_id UUID NOT NULL REFERENCES students(id), topic_id UUID NOT NULL REFERENCES topics(id),
 payment_id UUID REFERENCES payment_transactions(id), grant_reason TEXT NOT NULL DEFAULT 'purchase',
 granted_at TIMESTAMPTZ NOT NULL DEFAULT now(), revoked_at TIMESTAMPTZ,
 UNIQUE(student_id,topic_id,payment_id)
);
CREATE TABLE lesson_progress (
 student_id UUID NOT NULL REFERENCES students(id), topic_id UUID NOT NULL REFERENCES topics(id),
 asset_id UUID REFERENCES lesson_assets(id), position_seconds INTEGER NOT NULL DEFAULT 0 CHECK(position_seconds>=0),
 completed_at TIMESTAMPTZ, updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 PRIMARY KEY(student_id,topic_id,asset_id)
);
CREATE TABLE quiz_questions (
 id UUID PRIMARY KEY, topic_id UUID NOT NULL REFERENCES topics(id), question JSONB NOT NULL,
 answer_key JSONB NOT NULL, explanation TEXT, sort_order INTEGER NOT NULL DEFAULT 0,
 is_published BOOLEAN NOT NULL DEFAULT false
);
CREATE TABLE quiz_attempts (
 id UUID PRIMARY KEY, student_id UUID NOT NULL REFERENCES students(id), topic_id UUID NOT NULL REFERENCES topics(id),
 score NUMERIC(5,2), answers JSONB NOT NULL DEFAULT '[]'::jsonb, submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE admin_users (
 id UUID PRIMARY KEY, email TEXT NOT NULL UNIQUE,
 role TEXT NOT NULL CHECK(role IN ('owner','editor','reviewer','support','analyst')),
 is_active BOOLEAN NOT NULL DEFAULT true, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE audit_events (
 id BIGSERIAL PRIMARY KEY, actor_admin_id UUID REFERENCES admin_users(id), student_id UUID REFERENCES students(id),
 event_type TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
 details JSONB NOT NULL DEFAULT '{}'::jsonb, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX topics_catalogue_idx ON topics(class_level,subject_id,term_id,status,sort_order);
CREATE INDEX assets_topic_idx ON lesson_assets(topic_id,asset_type,review_status);
CREATE INDEX payments_student_idx ON payment_transactions(student_id,created_at DESC);
CREATE INDEX entitlements_student_idx ON entitlements(student_id,granted_at DESC);
CREATE INDEX progress_student_idx ON lesson_progress(student_id,updated_at DESC);
-- Enforce entitlement checks server-side / database policies; keep media storage private.
