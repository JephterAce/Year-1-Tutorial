"""One-time, explicit bootstrap for the first Learnwise owner admin.

Run from the backend directory in a trusted environment with DATABASE_URL set.
The password is read only from the process environment and is never printed.
"""
import os

from database import connection
from identity_policy import hash_password, normalise_email

CONFIRMATION = "CREATE_OWNER_ADMIN"
BOOTSTRAP_LOCK_KEY = "thinktank-first-owner-admin-bootstrap"


def main():
    if os.environ.get("LEARNWISE_BOOTSTRAP_CONFIRM") != CONFIRMATION:
        raise SystemExit(
            "Refusing to run: set LEARNWISE_BOOTSTRAP_CONFIRM=CREATE_OWNER_ADMIN explicitly."
        )
    if not os.environ.get("DATABASE_URL", "").strip():
        raise SystemExit("DATABASE_URL is required.")

    email = normalise_email(os.environ.get("LEARNWISE_ADMIN_EMAIL", ""))
    password = os.environ.get("LEARNWISE_ADMIN_PASSWORD", "")
    # Validate and hash before opening the transaction; never log the password.
    password_hash = hash_password(password)

    with connection() as conn:
        # Serialise concurrent invocations so two different emails cannot both
        # observe an empty admin table and create two owner accounts.
        conn.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            (BOOTSTRAP_LOCK_KEY,),
        )
        admin_count = conn.execute(
            "SELECT count(*) AS admin_count FROM admin_users"
        ).fetchone()["admin_count"]
        if admin_count:
            raise SystemExit(
                "An administrator account already exists. The owner bootstrap is one-time; "
                "no changes made."
            )

        row = conn.execute(
            """INSERT INTO admin_users(email,password_hash,role,is_active)
               VALUES (%s,%s,'owner',true) RETURNING id""",
            (email, password_hash),
        ).fetchone()
        from psycopg.types.json import Jsonb
        conn.execute(
            """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
               VALUES (%s,'admin.bootstrap.created','admin_user',%s,%s)""",
            (
                row["id"],
                str(row["id"]),
                Jsonb({"role": "owner", "method": "one_time_bootstrap"}),
            ),
        )

    print(
        "Initial Learnwise owner administrator created. "
        "Remove the bootstrap environment variables now."
    )


if __name__ == "__main__":
    main()
