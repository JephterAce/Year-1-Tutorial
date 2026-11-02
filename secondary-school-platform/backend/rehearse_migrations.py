"""Safe, repeatable PostgreSQL migration rehearsal runner."""
import hashlib, os, re, sys
from pathlib import Path
from urllib.parse import urlparse
import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE_SCHEMA = ROOT / "DATABASE_SCHEMA.sql"
MIGRATIONS = Path(__file__).resolve().parent / "migrations"
NAME = re.compile(r"^\d{3}_[a-z0-9_]+\.sql$")

def rehearsal_dsn():
    dsn = os.environ.get("LEARNWISE_REHEARSAL_DATABASE_URL", "")
    if not dsn:
        raise RuntimeError("Set LEARNWISE_REHEARSAL_DATABASE_URL to a disposable rehearsal DB.")
    parsed = urlparse(dsn)
    if (parsed.hostname or "").lower() not in {"localhost", "127.0.0.1", "::1", "postgres"}:
        raise RuntimeError("Refusing non-local database host; production rehearsals are prohibited.")
    if not parsed.path or parsed.path in {"/", "/postgres", "/learnwise"}:
        raise RuntimeError("Use a dedicated disposable database name.")
    return dsn

def migration_files():
    files = sorted(p for p in MIGRATIONS.iterdir() if NAME.match(p.name))
    numbers = [int(p.name[:3]) for p in files]
    if not files or numbers != list(range(1, len(numbers)+1)):
        raise RuntimeError(f"Migration sequence has a gap or duplicate: {numbers}")
    return files

def rehearse(dsn=None):
    dsn = dsn or rehearsal_dsn()
    applied = []
    with psycopg.connect(dsn, autocommit=False) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS learnwise_schema_migrations (
            version TEXT PRIMARY KEY, sha256 CHAR(64) NOT NULL,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
        conn.commit()
        baseline_sql = BASE_SCHEMA.read_text(encoding="utf-8")
        baseline_digest = hashlib.sha256(baseline_sql.encode()).hexdigest()
        with conn.transaction():
            baseline = conn.execute(
                "SELECT sha256 FROM learnwise_schema_migrations WHERE version='000_DATABASE_SCHEMA.sql'"
            ).fetchone()
            if baseline:
                if baseline[0].strip() != baseline_digest:
                    raise RuntimeError("Initial schema checksum changed; create a reviewed forward migration.")
            else:
                conn.execute(baseline_sql)
                conn.execute(
                    "INSERT INTO learnwise_schema_migrations(version,sha256) VALUES ('000_DATABASE_SCHEMA.sql',%s)",
                    (baseline_digest,),
                )
                applied.append("000_DATABASE_SCHEMA.sql")
        for path in migration_files():
            sql = path.read_text(encoding="utf-8")
            digest = hashlib.sha256(sql.encode()).hexdigest()
            with conn.transaction():
                prior = conn.execute("SELECT sha256 FROM learnwise_schema_migrations WHERE version=%s",
                                     (path.name,)).fetchone()
                if prior:
                    if prior[0].strip() != digest:
                        raise RuntimeError(f"Historical migration checksum changed: {path.name}")
                    continue
                conn.execute(sql)
                conn.execute("INSERT INTO learnwise_schema_migrations(version,sha256) VALUES (%s,%s)",
                             (path.name, digest))
                applied.append(path.name)
        conn.execute("SELECT 1")
    return applied

if __name__ == "__main__":
    try:
        done = rehearse()
        print("Applied:", ", ".join(done) if done else "no new migrations")
        print("Migration rehearsal completed.")
    except Exception as exc:
        print(f"Migration rehearsal failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
