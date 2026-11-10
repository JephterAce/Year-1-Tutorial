"""Seed synthetic identities and subjects into the disposable CI database only.

Never point this script at managed staging or production. It is called only by
the local PostgreSQL browser-acceptance workflow.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))

os.environ["LEARNWISE_BOOTSTRAP_CONFIRM"] = "CREATE_OWNER_ADMIN"
os.environ.setdefault("LEARNWISE_ADMIN_EMAIL", "ci-owner@thinktank.invalid")
os.environ.setdefault("LEARNWISE_ADMIN_PASSWORD", "Ephemeral-CI-Admin-Password-Only-2026!")
os.environ.setdefault("AUTH_RATE_LIMIT_PEPPER", "ci-only-pepper-not-a-real-secret-000000000000")

from bootstrap_admin import main as bootstrap_owner
from database import connection
from identity_policy import hash_password


def seed():
    bootstrap_owner()
    with connection() as conn:
        subjects = [
            ("ci-chemistry", "CI Chemistry"),
            ("ci-physics", "CI Physics"),
            ("ci-biology", "CI Biology"),
            ("ci-mathematics", "CI Mathematics"),
        ]
        for slug, name in subjects:
            conn.execute(
                """INSERT INTO subjects(slug,name,is_active)
                   VALUES (%s,%s,true) ON CONFLICT(slug) DO UPDATE
                   SET name=EXCLUDED.name,is_active=true""",
                (slug, name),
            )
        student = conn.execute(
            """INSERT INTO students
               (email,display_name,class_level,username,password_hash,email_verified_at,
                account_status,privacy_notice_version,guardian_consent_status,marketing_opt_in)
               VALUES (%s,%s,'SS1',%s,%s,now(),'active','ci-privacy-v1','not_required',false)
               ON CONFLICT (email) DO UPDATE SET account_status='active',
                 email_verified_at=COALESCE(students.email_verified_at,now())
               RETURNING id""",
            ("ci-student@thinktank.invalid","CI Student","ci_student",
             hash_password(os.environ.get("CI_STUDENT_PASSWORD","Ephemeral-CI-Student-Password-Only-2026!"))),
        ).fetchone()
        conn.execute(
            """INSERT INTO student_consent_records
               (student_id,consent_type,policy_version,granted)
               VALUES (%s,'terms_of_service','ci-terms-v1',true),
                      (%s,'privacy_notice','ci-privacy-v1',true)""",
            (student["id"],student["id"]),
        )
    print("Disposable CI fixtures seeded; no external provider was contacted.")


if __name__ == "__main__":
    if not os.environ.get("DATABASE_URL", "").strip():
        raise SystemExit("DATABASE_URL is required.")
    seed()
