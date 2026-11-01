"""Small PostgreSQL repository layer.

DATABASE_URL is supplied by the deployment environment and must never be committed.
The connection string should use TLS and a least-privilege application database role.
"""
import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


def database_url():
    return os.environ.get("DATABASE_URL")


@contextmanager
def connection():
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not configured")
    with psycopg.connect(url, row_factory=dict_row, connect_timeout=5) as conn:
        yield conn


def database_ready():
    try:
        with connection() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def list_published_topics(class_level=None, subject_slug=None, term_number=None, search=None):
    clauses = ["t.status = 'published'"]
    params = []
    if class_level in ("SS1", "SS2", "SS3"):
        clauses.append("t.class_level = %s")
        params.append(class_level)
    if subject_slug:
        clauses.append("s.slug = %s")
        params.append(subject_slug)
    if term_number in (1, 2, 3):
        clauses.append("tr.term_number = %s")
        params.append(term_number)
    if search:
        clauses.append("(t.title ILIKE %s OR COALESCE(t.summary, '') ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    query = """
        SELECT t.id, t.class_level, s.slug AS subject_slug, s.name AS subject, s.offering_group,
               tr.term_number, tr.label AS term, t.slug, t.title, t.summary,
               t.learning_objectives, t.price_kobo, t.currency, t.estimated_minutes
        FROM topics t
        JOIN subjects s ON s.id = t.subject_id
        JOIN terms tr ON tr.id = t.term_id
        WHERE """ + " AND ".join(clauses) + """
        ORDER BY t.class_level, s.sort_order, tr.term_number, t.sort_order, t.title
        LIMIT 200
    """
    with connection() as conn:
        return conn.execute(query, params).fetchall()
