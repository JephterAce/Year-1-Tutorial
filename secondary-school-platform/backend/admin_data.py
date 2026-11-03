"""Read-only, role-gated admin operational views."""
from flask import Blueprint, jsonify, request
from database import connection
from admin_policy import require
from psycopg.types.json import Jsonb

admin_data = Blueprint("admin_data", __name__)

def _session():
    from admin_auth import authenticate_admin
    return authenticate_admin(request.cookies.get("learnwise_admin_session"))

def _denied(capability):
    session = _session()
    if not session:
        return None, (jsonify({"error":"unauthenticated"}),401)
    try:
        require(session["principal"], capability)
    except PermissionError:
        return None, (jsonify({"error":"forbidden"}),403)
    return session, None

def _audit(conn, session, event, entity, count):
    conn.execute(
        """INSERT INTO audit_events(actor_admin_id,event_type,entity_type,entity_id,details)
           VALUES (%s,%s,%s,'list-view',%s)""",
        (session["admin_id"], event, entity, Jsonb({"returned_count": count}))
    )

@admin_data.get("/api/v1/admin/overview")
def overview():
    session, error = _denied("curriculum.read")
    if error: return error
    try:
        with connection() as conn:
            counts = conn.execute("""SELECT
              (SELECT count(*) FROM students) AS students,
              (SELECT count(*) FROM payment_transactions) AS payments,
              (SELECT count(*) FROM topics WHERE status='published' AND curriculum_status='published') AS published_topics,
              (SELECT count(*) FROM assessment_issue_reports WHERE status IN ('submitted','under_review')) AS open_reports""").fetchone()
            _audit(conn, session, "admin.overview.viewed", "platform_metrics", 1)
        return jsonify({"counts": {k:int(v) for k,v in counts.items()}}), 200
    except Exception:
        return jsonify({"error":"admin_overview_unavailable"}),503

@admin_data.get("/api/v1/admin/students")
def students():
    session, error = _denied("student.read_private")
    if error: return error
    try:
        limit=max(1,min(int(request.args.get("limit","50")),100))
        with connection() as conn:
            rows=conn.execute("""SELECT id,display_name,email,class_level,account_status,created_at
              FROM students ORDER BY created_at DESC LIMIT %s""",(limit,)).fetchall()
            _audit(conn,session,"admin.student_records.viewed","students",len(rows))
        return jsonify({"items":[{"id":str(r["id"]),"display_name":r["display_name"],
          "email":r["email"],"class_level":r["class_level"],"account_status":r["account_status"],
          "created_at":r["created_at"].isoformat()} for r in rows]}),200
    except (ValueError,TypeError):
        return jsonify({"error":"invalid_limit"}),400
    except Exception:
        return jsonify({"error":"admin_students_unavailable"}),503

@admin_data.get("/api/v1/admin/payments")
def payments():
    session, error = _denied("payment.read")
    if error: return error
    try:
        limit=max(1,min(int(request.args.get("limit","50")),100))
        with connection() as conn:
            rows=conn.execute("""SELECT id,provider_reference,amount_kobo,currency,status,created_at,verified_at
              FROM payment_transactions ORDER BY created_at DESC LIMIT %s""",(limit,)).fetchall()
            _audit(conn,session,"admin.payment_records.viewed","payment_transactions",len(rows))
        return jsonify({"items":[{"id":str(r["id"]),"reference":r["provider_reference"],
          "amount_kobo":int(r["amount_kobo"]),"currency":r["currency"].strip(),
          "status":r["status"],"created_at":r["created_at"].isoformat(),
          "verified_at":r["verified_at"].isoformat() if r["verified_at"] else None} for r in rows]}),200
    except (ValueError,TypeError):
        return jsonify({"error":"invalid_limit"}),400
    except Exception:
        return jsonify({"error":"admin_payments_unavailable"}),503

@admin_data.get("/api/v1/admin/curriculum-sources")
def curriculum_sources():
    session, error = _denied("curriculum.read")
    if error: return error
    try:
        limit=max(1,min(int(request.args.get("limit","100")),200))
        with connection() as conn:
            rows=conn.execute("""SELECT c.id,c.class_level,c.source_title,c.source_url,c.source_version,
              c.source_section,c.source_kind,c.verification_status,c.licence_status,c.reviewed_by,c.reviewed_at,
              s.name AS subject
              FROM curriculum_source_records c JOIN subjects s ON s.id=c.subject_id
              ORDER BY c.created_at DESC LIMIT %s""",(limit,)).fetchall()
            _audit(conn,session,"admin.curriculum_sources.viewed","curriculum_source_records",len(rows))
        return jsonify({"items":[{"id":str(r["id"]),"class_level":r["class_level"],
          "subject":r["subject"],"source_title":r["source_title"],"source_url":r["source_url"],
          "source_version":r["source_version"],"source_section":r["source_section"],
          "source_kind":r["source_kind"],"verification_status":r["verification_status"],
          "licence_status":r["licence_status"],"reviewed_by":r["reviewed_by"],
          "reviewed_at":r["reviewed_at"].isoformat() if r["reviewed_at"] else None} for r in rows]}),200
    except (ValueError,TypeError):
        return jsonify({"error":"invalid_limit"}),400
    except Exception:
        return jsonify({"error":"admin_curriculum_unavailable"}),503
