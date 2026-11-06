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


@admin_data.get("/api/v1/admin/audio-assets")
def list_audio_assets():
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    can_review=False
    try:
        require(session["principal"],"audio.upload")
    except PermissionError:
        try:
            require(session["principal"],"audio.review")
            can_review=True
        except PermissionError:
            return jsonify({"error":"forbidden"}),403
    try:
        with connection() as conn:
            rows=conn.execute("""SELECT a.id,a.topic_id,t.title AS topic_title,a.asset_type,
              a.mime_type,a.duration_seconds,a.version,a.review_status,a.created_at
              FROM lesson_assets a JOIN topics t ON t.id=a.topic_id
              WHERE a.asset_type IN ('teacher_audio','podcast_audio')
              ORDER BY a.created_at DESC LIMIT 100""").fetchall()
            _audit(conn,session,"admin.audio_assets.viewed","lesson_assets",len(rows))
        return jsonify({"can_review":can_review or session["role"]=="owner","items":[{"id":str(r["id"]),"topic_id":str(r["topic_id"]),
          "topic_title":r["topic_title"],"asset_type":r["asset_type"],"mime_type":r["mime_type"],
          "duration_seconds":r["duration_seconds"],"version":r["version"],
          "review_status":r["review_status"],"created_at":r["created_at"].isoformat()} for r in rows]}),200
    except Exception:
        return jsonify({"error":"admin_audio_assets_unavailable"}),503

@admin_data.post("/api/v1/admin/audio-assets")
def upload_audio_asset():
    from uuid import UUID, uuid4
    from admin_auth import validate_admin_csrf
    from audio_storage import put_private_audio_object, delete_private_audio_object, AudioStorageError
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"audio.upload")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        topic_id=str(UUID(request.form.get("topic_id","")))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_topic_id"}),400
    asset_type=request.form.get("asset_type","")
    if asset_type not in {"teacher_audio","podcast_audio"}:
        return jsonify({"error":"invalid_asset_type"}),400
    uploaded=request.files.get("file")
    if not uploaded or not uploaded.filename:
        return jsonify({"error":"audio_file_required"}),400
    allowed={"audio/mpeg":".mp3","audio/mp4":".m4a","audio/wav":".wav",
             "audio/ogg":".ogg","audio/webm":".webm"}
    content_type=(uploaded.mimetype or "").lower()
    if content_type not in allowed:
        return jsonify({"error":"unsupported_audio_type"}),400
    try:
        uploaded.stream.seek(0,2)
        size=uploaded.stream.tell()
        uploaded.stream.seek(0)
        signature=uploaded.stream.read(16)
        uploaded.stream.seek(0)
        valid=(content_type=="audio/mpeg" and (signature.startswith(b"ID3") or (len(signature)>1 and signature[0]==0xFF and signature[1]&0xE0==0xE0))) or (content_type=="audio/wav" and signature.startswith(b"RIFF") and signature[8:12]==b"WAVE") or (content_type=="audio/ogg" and signature.startswith(b"OggS")) or (content_type=="audio/webm" and signature.startswith(bytes.fromhex("1a45dfa3"))) or (content_type=="audio/mp4" and len(signature)>=8 and signature[4:8]==b"ftyp")
        if not valid or not 1 <= size <= 100*1024*1024:
            return jsonify({"error":"invalid_audio_file_or_size"}),400
    except Exception:
        return jsonify({"error":"invalid_audio_upload"}),400
    try:
        with connection() as conn:
            topic=conn.execute("SELECT id,status FROM topics WHERE id=%s",(topic_id,)).fetchone()
            if not topic: return jsonify({"error":"topic_not_found"}),404
            if topic["status"] not in {"draft","review"}:
                return jsonify({"error":"published_topic_locked"}),409
            version=conn.execute("SELECT COALESCE(MAX(version),0)+1 AS next_version FROM lesson_assets WHERE topic_id=%s AND asset_type=%s",(topic_id,asset_type)).fetchone()["next_version"]
        object_key=f"topics/{topic_id}/{asset_type}/{uuid4().hex}{allowed[content_type]}"
        etag=put_private_audio_object(object_key,uploaded.stream,content_type,size)
        try:
            with connection() as conn:
                row=conn.execute("""INSERT INTO lesson_assets(topic_id,asset_type,storage_key,mime_type,version,review_status)
                  VALUES (%s,%s,%s,%s,%s,'pending') RETURNING id,created_at""",
                  (topic_id,asset_type,object_key,content_type,version)).fetchone()
                _audit(conn,session,"admin.audio_asset.uploaded","lesson_asset",1)
        except Exception:
            delete_private_audio_object(object_key)
            raise
        return jsonify({"asset":{"id":str(row["id"]),"topic_id":topic_id,"asset_type":asset_type,
          "version":version,"review_status":"pending","created_at":row["created_at"].isoformat()},
          "message":"Uploaded to private storage and queued for review."}),201
    except AudioStorageError:
        return jsonify({"error":"private_audio_storage_unavailable"}),503
    except Exception:
        return jsonify({"error":"audio_asset_save_failed"}),503

@admin_data.post("/api/v1/admin/audio-assets/<asset_id>/review")
def review_audio_asset(asset_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"audio.review")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        asset_id=str(UUID(asset_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_asset_id"}),400
    status=(request.get_json(silent=True) or {}).get("review_status")
    if status not in {"approved","rejected"}:
        return jsonify({"error":"invalid_review_status"}),400
    try:
        with connection() as conn:
            row=conn.execute("""UPDATE lesson_assets SET review_status=%s
              WHERE id=%s AND asset_type IN ('teacher_audio','podcast_audio')
              RETURNING id,review_status""",(status,asset_id)).fetchone()
            if not row: return jsonify({"error":"asset_not_found"}),404
            _audit(conn,session,"admin.audio_asset.reviewed","lesson_asset",1)
        return jsonify({"asset":{"id":str(row["id"]),"review_status":row["review_status"]}}),200
    except Exception:
        return jsonify({"error":"audio_review_unavailable"}),503


@admin_data.post("/api/v1/admin/podcast-scripts")
def create_podcast_script_draft():
    from admin_auth import validate_admin_csrf
    from podcast_production import create_podcast_script, PodcastProductionError
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"audio.upload")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    data=request.get_json(silent=True) or {}
    try:
        result=create_podcast_script(data.get("topic_id"),session["admin_id"])
        with connection() as conn:
            _audit(conn,session,"admin.podcast_script.created","podcast_script",1)
        return jsonify({"script":result}),201
    except PodcastProductionError as exc:
        return jsonify({"error":exc.code,"message":str(exc)}),exc.status
    except Exception:
        return jsonify({"error":"podcast_script_unavailable"}),503


@admin_data.get("/api/v1/admin/podcast-scripts")
def list_podcast_scripts():
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    try:
        require(session["principal"],"audio.upload")
    except PermissionError:
        try:
            require(session["principal"],"audio.review")
        except PermissionError:
            return jsonify({"error":"forbidden"}),403
    try:
        with connection() as conn:
            rows=conn.execute(
                """SELECT p.id,p.topic_id,t.title AS topic_title,p.version,p.title,
                          p.status,p.script_text,p.audio_asset_id,p.created_at,
                          a.review_status AS audio_review_status
                   FROM podcast_scripts p JOIN topics t ON t.id=p.topic_id
                   LEFT JOIN lesson_assets a ON a.id=p.audio_asset_id
                   ORDER BY p.created_at DESC LIMIT 100"""
            ).fetchall()
            _audit(conn,session,"admin.podcast_scripts.viewed","podcast_scripts",len(rows))
        return jsonify({"items":[{
            "id":str(r["id"]),"topic_id":str(r["topic_id"]),
            "topic_title":r["topic_title"],"version":r["version"],
            "title":r["title"],"status":r["status"],"script_text":r["script_text"],
            "audio_asset_id":str(r["audio_asset_id"]) if r["audio_asset_id"] else None,
            "audio_review_status":r["audio_review_status"],
            "created_at":r["created_at"].isoformat()
        } for r in rows]}),200
    except Exception:
        return jsonify({"error":"podcast_script_list_unavailable"}),503


@admin_data.post("/api/v1/admin/podcast-scripts/<script_id>/attach-audio")
def attach_podcast_audio(script_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"audio.upload")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        script_id=str(UUID(script_id))
        asset_id=str(UUID((request.get_json(silent=True) or {}).get("asset_id","")))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_identifier"}),400
    try:
        with connection() as conn:
            row=conn.execute(
                """UPDATE podcast_scripts p SET audio_asset_id=a.id,status='teacher_review'
                   FROM lesson_assets a
                   WHERE p.id=%s AND a.id=%s AND a.topic_id=p.topic_id
                     AND a.asset_type='podcast_audio' AND a.review_status='pending'
                     AND p.status IN ('draft','teacher_review')
                   RETURNING p.id,p.audio_asset_id,p.status""",
                (script_id,asset_id),
            ).fetchone()
            if not row: return jsonify({"error":"matching_pending_podcast_audio_required"}),409
            _audit(conn,session,"admin.podcast_audio.attached","podcast_script",1)
        return jsonify({"script":{"id":str(row["id"]),"audio_asset_id":str(row["audio_asset_id"]),
                                  "status":row["status"]}}),200
    except Exception:
        return jsonify({"error":"podcast_audio_attach_unavailable"}),503


@admin_data.post("/api/v1/admin/podcast-scripts/<script_id>/review")
def review_podcast_script(script_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"audio.review")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        script_id=str(UUID(script_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_script_id"}),400
    status=(request.get_json(silent=True) or {}).get("status")
    if status not in {"approved","rejected"}:
        return jsonify({"error":"invalid_review_status"}),400
    try:
        with connection() as conn:
            if status=="approved":
                row=conn.execute(
                    """UPDATE podcast_scripts p SET status='approved',reviewed_by=%s,reviewed_at=now()
                       WHERE p.id=%s AND p.audio_asset_id IS NOT NULL
                         AND EXISTS (SELECT 1 FROM lesson_assets a WHERE a.id=p.audio_asset_id
                           AND a.topic_id=p.topic_id AND a.asset_type='podcast_audio'
                           AND a.review_status='approved')
                       RETURNING p.id,p.status,p.reviewed_at""",
                    (session["email"],script_id),
                ).fetchone()
            else:
                row=conn.execute(
                    """UPDATE podcast_scripts SET status='rejected',reviewed_by=%s,reviewed_at=now()
                       WHERE id=%s AND status IN ('draft','teacher_review')
                       RETURNING id,status,reviewed_at""",
                    (session["email"],script_id),
                ).fetchone()
            if not row: return jsonify({"error":"approved_audio_and_script_required"}),409
            _audit(conn,session,"admin.podcast_script.reviewed","podcast_script",1)
        return jsonify({"script":{"id":str(row["id"]),"status":row["status"],
                                  "reviewed_at":row["reviewed_at"].isoformat()}}),200
    except Exception:
        return jsonify({"error":"podcast_script_review_unavailable"}),503


@admin_data.post("/api/v1/admin/topics/<topic_id>/lesson-content")
def create_lesson_content_draft(topic_id):
    from uuid import UUID
    from psycopg.types.json import Jsonb
    from admin_auth import validate_admin_csrf
    import json
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.edit")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        topic_id=str(UUID(topic_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_topic_id"}),400
    data=request.get_json(silent=True) or {}
    content=data.get("content")
    questions=data.get("practice_questions",[])
    if not isinstance(content,dict) or not isinstance(questions,list) or len(questions)>100:
        return jsonify({"error":"invalid_lesson_payload"}),400
    if len(json.dumps(content,ensure_ascii=False))>60000:
        return jsonify({"error":"lesson_content_too_large"}),413
    for key in ("sections","learning_objectives","key_terms","worked_examples"):
        if key in content and not isinstance(content[key],list):
            return jsonify({"error":"invalid_lesson_structure","field":key}),400
    if not isinstance(content.get("sections",[]),list) or len(content.get("sections",[]))>30:
        return jsonify({"error":"invalid_lesson_sections"}),400
    for q in questions:
        if not isinstance(q,dict) or q.get("question_type") not in {"single_choice","true_false","numeric"}:
            return jsonify({"error":"invalid_practice_question"}),400
        if not isinstance(q.get("prompt"),str) or not q["prompt"].strip() or len(q["prompt"])>2000:
            return jsonify({"error":"invalid_practice_prompt"}),400
        if not isinstance(q.get("answer_key"),dict) or "value" not in q["answer_key"]:
            return jsonify({"error":"practice_answer_key_required"}),400
        if not isinstance(q.get("explanation"),str) or not q["explanation"].strip() or len(q["explanation"])>4000:
            return jsonify({"error":"practice_explanation_required"}),400
        if q["question_type"]=="single_choice":
            options=q.get("options")
            if not isinstance(options,list) or not 2<=len(options)<=8:
                return jsonify({"error":"invalid_practice_options"}),400
            option_ids={x.get("id") for x in options if isinstance(x,dict)}
            if len(option_ids)!=len(options) or q["answer_key"]["value"] not in option_ids:
                return jsonify({"error":"invalid_practice_answer_key"}),400
        elif q.get("options") not in (None,[]):
            return jsonify({"error":"options_not_allowed"}),400
    try:
        with connection() as conn:
            topic=conn.execute("SELECT id,status FROM topics WHERE id=%s",(topic_id,)).fetchone()
            if not topic: return jsonify({"error":"topic_not_found"}),404
            if topic["status"] in {"published","archived"}:
                return jsonify({"error":"published_topic_locked"}),409
            version=conn.execute(
                "SELECT COALESCE(MAX(version),0)+1 AS next_version FROM topic_lesson_content WHERE topic_id=%s",
                (topic_id,)
            ).fetchone()["next_version"]
            row=conn.execute(
                """INSERT INTO topic_lesson_content
                     (topic_id,version,content_json,review_status,created_by)
                   VALUES (%s,%s,%s,'draft',%s)
                   RETURNING id,version,created_at""",
                (topic_id,version,Jsonb(content),session["email"]),
            ).fetchone()
            for index,q in enumerate(questions,1):
                conn.execute(
                    """INSERT INTO lesson_practice_questions
                         (topic_id,lesson_content_id,question_type,prompt,options,answer_key,
                          explanation,sort_order,review_status)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'draft')""",
                    (topic_id,row["id"],q["question_type"],q["prompt"],
                     Jsonb(q["options"]) if q.get("options") else None,
                     Jsonb(q["answer_key"]),q["explanation"],q.get("sort_order",index)),
                )
            _audit(conn,session,"admin.lesson_content.created","topic_lesson_content",1)
        return jsonify({"content_id":str(row["id"]),"version":row["version"],
                        "practice_question_count":len(questions),"review_status":"draft"}),201
    except Exception:
        return jsonify({"error":"lesson_content_save_failed"}),503


@admin_data.post("/api/v1/admin/lesson-content/<content_id>/review")
def review_lesson_content_draft(content_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.publish")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        content_id=str(UUID(content_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_content_id"}),400
    data=request.get_json(silent=True) or {}
    status=data.get("review_status")
    teacher_reviewer=(data.get("teacher_reviewer_name") or "").strip()
    if status not in {"approved","rejected"}:
        return jsonify({"error":"invalid_review_status"}),400
    if status=="approved" and not 2<=len(teacher_reviewer)<=120:
        return jsonify({"error":"teacher_reviewer_required"}),400
    try:
        with connection() as conn:
            if status=="approved":
                row=conn.execute(
                    """UPDATE topic_lesson_content SET review_status='approved',
                         approved_by=%s,approved_at=now()
                       WHERE id=%s AND review_status IN ('draft','teacher_review')
                       RETURNING id,topic_id,version,review_status""",
                    (teacher_reviewer,content_id),
                ).fetchone()
                if row:
                    conn.execute(
                        """UPDATE lesson_practice_questions SET review_status='approved'
                           WHERE lesson_content_id=%s AND review_status IN ('draft','teacher_review')""",
                        (content_id,),
                    )
            else:
                row=conn.execute(
                    """UPDATE topic_lesson_content SET review_status='rejected'
                       WHERE id=%s AND review_status IN ('draft','teacher_review')
                       RETURNING id,topic_id,version,review_status""",
                    (content_id,),
                ).fetchone()
                if row:
                    conn.execute(
                        "UPDATE lesson_practice_questions SET review_status='rejected' WHERE lesson_content_id=%s",
                        (content_id,),
                    )
            if not row: return jsonify({"error":"draft_not_found_or_already_reviewed"}),409
            _audit(conn,session,"admin.lesson_content.reviewed","topic_lesson_content",1)
        return jsonify({"content_id":str(row["id"]),"topic_id":str(row["topic_id"]),
                        "version":row["version"],"review_status":row["review_status"]}),200
    except Exception:
        return jsonify({"error":"lesson_content_review_unavailable"}),503


@admin_data.get("/api/v1/admin/topics")
def list_curriculum_topics():
    session,error=_denied("curriculum.read")
    if error: return error
    class_level=request.args.get("class_level")
    subject_slug=request.args.get("subject")
    if class_level and class_level not in {"SS1","SS2","SS3"}:
        return jsonify({"error":"invalid_class_level"}),400
    try:
        with connection() as conn:
            rows=conn.execute(
                """SELECT t.id,t.slug,t.title,t.class_level,t.status,t.curriculum_status,
                          t.term_mapping_status,t.term_id,t.curriculum_source_record_id,
                          s.slug AS subject_slug,s.name AS subject
                   FROM topics t JOIN subjects s ON s.id=t.subject_id
                   WHERE (%s IS NULL OR t.class_level=%s)
                     AND (%s IS NULL OR s.slug=%s)
                   ORDER BY t.class_level,s.sort_order,t.title LIMIT 500""",
                (class_level,class_level,subject_slug,subject_slug),
            ).fetchall()
            _audit(conn,session,"admin.curriculum_topics.viewed","topics",len(rows))
        return jsonify({"items":[{
            "id":str(r["id"]),"slug":r["slug"],"title":r["title"],
            "class_level":r["class_level"],"subject_slug":r["subject_slug"],
            "subject":r["subject"],"status":r["status"],
            "curriculum_status":r["curriculum_status"],
            "term_mapping_status":r["term_mapping_status"],
            "term_id":str(r["term_id"]) if r["term_id"] else None,
            "source_id":str(r["curriculum_source_record_id"]) if r["curriculum_source_record_id"] else None
        } for r in rows]}),200
    except Exception:
        return jsonify({"error":"admin_topics_unavailable"}),503


@admin_data.post("/api/v1/admin/curriculum-sources")
def create_curriculum_source_record():
    from uuid import UUID
    from urllib.parse import urlparse
    from admin_auth import validate_admin_csrf
    from psycopg.types.json import Jsonb
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.edit")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    data=request.get_json(silent=True) or {}
    class_level=data.get("class_level")
    subject_slug=data.get("subject_slug")
    title=(data.get("source_title") or "").strip()
    url=(data.get("source_url") or "").strip()
    section=(data.get("source_section") or "").strip()
    source_kind=data.get("source_kind","official_nerdc")
    licence_status=data.get("licence_status","metadata_only")
    parsed=urlparse(url)
    if class_level not in {"SS1","SS2","SS3"} or not isinstance(subject_slug,str):
        return jsonify({"error":"invalid_class_or_subject"}),400
    if not 5<=len(title)<=240 or not section or len(section)>500:
        return jsonify({"error":"source_title_and_section_required"}),400
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        return jsonify({"error":"https_source_url_required"}),400
    if source_kind not in {"official_nerdc","school_scheme","teacher_reference","other"}:
        return jsonify({"error":"invalid_source_kind"}),400
    if licence_status not in {"metadata_only","permission_requested","permission_granted","restricted","unknown"}:
        return jsonify({"error":"invalid_licence_status"}),400
    try:
        with connection() as conn:
            subject=conn.execute("SELECT id FROM subjects WHERE slug=%s AND is_active=true",(subject_slug,)).fetchone()
            version=conn.execute("SELECT id FROM curriculum_versions WHERE version_code='nerdc_ssec_2025' AND status='active'").fetchone()
            if not subject or not version:
                return jsonify({"error":"subject_or_curriculum_version_unavailable"}),404
            row=conn.execute(
                """INSERT INTO curriculum_source_records
                     (subject_id,class_level,source_title,source_url,source_version,source_date,
                      source_section,notes,verification_status,curriculum_version_id,source_kind,
                      licence_status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'source_captured',%s,%s,%s)
                   RETURNING id,created_at""",
                (subject["id"],class_level,title,url,data.get("source_version"),
                 data.get("source_date") or None,section,(data.get("notes") or "")[:2000],
                 version["id"],source_kind,licence_status),
            ).fetchone()
            _audit(conn,session,"admin.curriculum_source.captured","curriculum_source_record",1)
        return jsonify({"source_id":str(row["id"]),"verification_status":"source_captured",
                        "created_at":row["created_at"].isoformat()}),201
    except Exception:
        return jsonify({"error":"curriculum_source_save_failed"}),503


@admin_data.post("/api/v1/admin/topics")
def create_curriculum_topic_draft():
    from uuid import UUID
    import re
    from psycopg.types.json import Jsonb
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.edit")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    data=request.get_json(silent=True) or {}
    class_level=data.get("class_level")
    subject_slug=data.get("subject_slug")
    source_id=data.get("source_id")
    slug=(data.get("slug") or "").strip().lower()
    title=(data.get("title") or "").strip()
    objectives=data.get("learning_objectives",[])
    if class_level not in {"SS1","SS2","SS3"} or not isinstance(subject_slug,str):
        return jsonify({"error":"invalid_class_or_subject"}),400
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+){0,7}",slug):
        return jsonify({"error":"invalid_topic_slug"}),400
    if not 3<=len(title)<=180 or not isinstance(objectives,list) or len(objectives)>20:
        return jsonify({"error":"invalid_topic_metadata"}),400
    if any(not isinstance(x,str) or not x.strip() or len(x)>400 for x in objectives):
        return jsonify({"error":"invalid_learning_objectives"}),400
    try:
        source_id=str(UUID(source_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_source_id"}),400
    try:
        with connection() as conn:
            source=conn.execute(
                """SELECT c.id,c.subject_id,c.class_level,c.source_url,c.source_version,
                          c.source_section,c.curriculum_version_id,s.slug AS subject_slug
                   FROM curriculum_source_records c JOIN subjects s ON s.id=c.subject_id
                   WHERE c.id=%s AND c.class_level=%s AND s.slug=%s
                     AND c.verification_status IN ('source_captured','mapped','teacher_review','approved')""",
                (source_id,class_level,subject_slug),
            ).fetchone()
            if not source: return jsonify({"error":"matching_curriculum_source_required"}),409
            row=conn.execute(
                """INSERT INTO topics
                     (subject_id,class_level,term_id,slug,title,summary,learning_objectives,
                      price_kobo,currency,status,curriculum_version_id,curriculum_source_record_id,
                      curriculum_status,curriculum_theme,curriculum_subtopic,curriculum_source_url,
                      curriculum_source_version,curriculum_source_section,curriculum_evidence_note,
                      term_mapping_status)
                   VALUES (%s,%s,NULL,%s,%s,%s,%s,%s,'NGN','draft',%s,%s,'source_captured',
                      %s,%s,%s,%s,%s,%s,'not_assigned')
                   RETURNING id,created_at""",
                (source["subject_id"],class_level,slug,title,(data.get("summary") or "")[:2000],
                 Jsonb(objectives),max(100000,int(data.get("price_kobo",100000))),
                 source["curriculum_version_id"],source_id,(data.get("curriculum_theme") or "")[:180],
                 (data.get("curriculum_subtopic") or "")[:180],source["source_url"],
                 source["source_version"],source["source_section"],
                 (data.get("curriculum_evidence_note") or "")[:2000]),
            ).fetchone()
            _audit(conn,session,"admin.curriculum_topic.created","topic",1)
        return jsonify({"topic_id":str(row["id"]),"status":"draft",
                        "curriculum_status":"source_captured",
                        "term_mapping_status":"not_assigned"}),201
    except (ValueError,TypeError):
        return jsonify({"error":"invalid_topic_metadata"}),400
    except Exception:
        return jsonify({"error":"curriculum_topic_save_failed"}),503


@admin_data.post("/api/v1/admin/curriculum-sources/<source_id>/review")
def review_curriculum_source_record(source_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.publish")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        source_id=str(UUID(source_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_source_id"}),400
    data=request.get_json(silent=True) or {}
    status=data.get("verification_status")
    reviewer=(data.get("reviewer_name") or "").strip()
    if status not in {"approved","superseded"} or not 2<=len(reviewer)<=120:
        return jsonify({"error":"review_status_and_reviewer_required"}),400
    try:
        with connection() as conn:
            row=conn.execute(
                """UPDATE curriculum_source_records SET verification_status=%s,
                     reviewed_by=%s,reviewed_at=now()
                   WHERE id=%s AND verification_status IN ('source_captured','mapped','teacher_review')
                     AND COALESCE(trim(source_section),'')<>''
                   RETURNING id,verification_status,reviewed_at""",
                (status,reviewer,source_id),
            ).fetchone()
            if not row: return jsonify({"error":"source_not_reviewable"}),409
            _audit(conn,session,"admin.curriculum_source.reviewed","curriculum_source_record",1)
        return jsonify({"source_id":str(row["id"]),"verification_status":row["verification_status"],
                        "reviewed_at":row["reviewed_at"].isoformat()}),200
    except Exception:
        return jsonify({"error":"curriculum_source_review_unavailable"}),503


@admin_data.post("/api/v1/admin/topics/<topic_id>/publish")
def publish_curriculum_topic(topic_id):
    from uuid import UUID
    from admin_auth import validate_admin_csrf
    session=_session()
    if not session: return jsonify({"error":"unauthenticated"}),401
    if not validate_admin_csrf(session,request.headers.get("X-CSRF-Token","")):
        return jsonify({"error":"csrf_failed"}),401
    try:
        require(session["principal"],"curriculum.publish")
    except PermissionError:
        return jsonify({"error":"forbidden"}),403
    try:
        topic_id=str(UUID(topic_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_topic_id"}),400
    data=request.get_json(silent=True) or {}
    reviewer=(data.get("teacher_reviewer_name") or "").strip()
    evidence=(data.get("curriculum_evidence_note") or "").strip()
    mapping=data.get("term_mapping_status","not_assigned")
    term_number=data.get("term_number")
    scheme=(data.get("school_scheme_name") or "").strip()
    if not 2<=len(reviewer)<=120 or not 10<=len(evidence)<=2000:
        return jsonify({"error":"teacher_review_and_evidence_required"}),400
    if mapping not in {"official_term_allocation","school_scheme_verified","school_scheme_required","not_assigned","not_applicable"}:
        return jsonify({"error":"invalid_term_mapping_status"}),400
    if mapping=="school_scheme_verified" and not 2<=len(scheme)<=180:
        return jsonify({"error":"school_scheme_name_required"}),400
    if mapping in {"official_term_allocation","school_scheme_verified"} and term_number not in {1,2,3}:
        return jsonify({"error":"valid_term_number_required"}),400
    if mapping in {"school_scheme_required","not_assigned","not_applicable"} and term_number is not None:
        return jsonify({"error":"unverified_term_must_not_be_assigned"}),400
    try:
        with connection() as conn:
            row=conn.execute(
                """SELECT t.id,t.subject_id,t.class_level,t.curriculum_source_record_id,
                          c.source_kind,c.verification_status,c.licence_status,c.curriculum_version_id,
                          v.version_code,v.status AS version_status,
                          EXISTS (SELECT 1 FROM topic_lesson_content lc
                                  WHERE lc.topic_id=t.id AND lc.review_status='approved') AS has_approved_content
                   FROM topics t
                   JOIN curriculum_source_records c ON c.id=t.curriculum_source_record_id
                   JOIN curriculum_versions v ON v.id=t.curriculum_version_id
                   WHERE t.id=%s AND t.status IN ('draft','review')""",
                (topic_id,),
            ).fetchone()
            if not row: return jsonify({"error":"draft_topic_with_source_required"}),409
            if not row["has_approved_content"]:
                return jsonify({"error":"teacher_approved_lesson_content_required"}),409
            if row["verification_status"]!="approved" or row["version_code"]!="nerdc_ssec_2025" or row["version_status"]!="active":
                return jsonify({"error":"approved_active_curriculum_source_required"}),409
            if row["licence_status"] not in {"metadata_only","permission_granted"}:
                return jsonify({"error":"source_rights_review_required"}),409
            if mapping=="official_term_allocation" and row["source_kind"]!="official_nerdc":
                return jsonify({"error":"official_term_mapping_requires_official_source"}),409
            if mapping=="school_scheme_verified" and row["source_kind"]!="school_scheme":
                return jsonify({"error":"school_scheme_mapping_requires_school_source"}),409
            term_id=None
            if term_number is not None:
                term=conn.execute("SELECT id FROM terms WHERE term_number=%s",(term_number,)).fetchone()
                if not term:return jsonify({"error":"term_not_found"}),404
                term_id=term["id"]
            published=conn.execute(
                """UPDATE topics SET status='published',curriculum_status='published',
                     curriculum_evidence_note=%s,curriculum_approved_by=%s,
                     curriculum_approved_at=now(),term_mapping_status=%s,
                     term_id=%s,school_scheme_name=%s
                   WHERE id=%s AND status IN ('draft','review')
                   RETURNING id,status,curriculum_status,term_mapping_status""",
                (evidence,reviewer,mapping,term_id,scheme or None,topic_id),
            ).fetchone()
            if not published:return jsonify({"error":"topic_state_changed"}),409
            _audit(conn,session,"admin.curriculum_topic.published","topic",1)
        return jsonify({"topic_id":str(published["id"]),"status":published["status"],
                        "curriculum_status":published["curriculum_status"],
                        "term_mapping_status":published["term_mapping_status"]}),200
    except Exception:
        return jsonify({"error":"curriculum_topic_publish_failed"}),503


@admin_data.get("/api/v1/admin/topics/<topic_id>/lesson-content")
def list_admin_lesson_content(topic_id):
    from uuid import UUID
    session,error=_denied("curriculum.read")
    if error: return error
    try:
        topic_id=str(UUID(topic_id))
    except (TypeError,ValueError,AttributeError):
        return jsonify({"error":"invalid_topic_id"}),400
    try:
        with connection() as conn:
            rows=conn.execute(
                """SELECT id,version,content_json,review_status,created_by,approved_by,
                          approved_at,created_at
                   FROM topic_lesson_content WHERE topic_id=%s
                   ORDER BY version DESC LIMIT 20""",
                (topic_id,),
            ).fetchall()
            _audit(conn,session,"admin.lesson_content.viewed","topic_lesson_content",len(rows))
        return jsonify({"items":[{
            "id":str(r["id"]),"version":r["version"],"content":r["content_json"],
            "review_status":r["review_status"],"created_by":r["created_by"],
            "approved_by":r["approved_by"],
            "approved_at":r["approved_at"].isoformat() if r["approved_at"] else None,
            "created_at":r["created_at"].isoformat()
        } for r in rows]}),200
    except Exception:
        return jsonify({"error":"admin_lesson_content_unavailable"}),503
