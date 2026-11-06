"""Create two-presenter podcast script drafts from approved lesson content."""
from database import connection


class PodcastProductionError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def _clean(value, limit=2500):
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())[:limit]


def build_podcast_script(topic_title, subject, content):
    """Create an original, source-bounded dialogue; never invent new lesson facts."""
    title = _clean(topic_title, 160)
    subject = _clean(subject, 100)
    if not title or not isinstance(content, dict):
        raise PodcastProductionError("content_unavailable", "Approved lesson content is required.", 404)
    lines = [
        f"HOST 1: Welcome to Think Tank Learning. Today we are exploring {title} in {subject}.",
        "HOST 2: This episode follows the reviewed lesson notes. Keep your notebook nearby and pause whenever you need time to think.",
    ]
    intro = _clean(content.get("intro"))
    if intro:
        lines.append(f"HOST 1: {intro}")
    objectives = content.get("learning_objectives", [])
    if isinstance(objectives, list) and objectives:
        lines.append("HOST 2: By the end of this lesson, you should be able to:")
        for objective in objectives[:8]:
            item = _clean(objective, 400)
            if item:
                lines.append(f"HOST 2: {item}")
    sections = content.get("sections", [])
    if isinstance(sections, list):
        for section in sections[:12]:
            if not isinstance(section, dict):
                continue
            heading = _clean(section.get("heading"), 180)
            body = _clean(section.get("body"), 2500)
            if heading and body:
                lines.append(f"HOST 1: Let us look at {heading}. {body}")
                lines.append("HOST 2: Pause here and explain that idea in your own words before continuing.")
    terms = content.get("key_terms", [])
    if isinstance(terms, list) and terms:
        lines.append("HOST 1: Here are the key terms to remember.")
        for term in terms[:12]:
            if isinstance(term, dict):
                name, definition = _clean(term.get("term"), 120), _clean(term.get("definition"), 500)
                if name and definition:
                    lines.append(f"HOST 2: {name}. {definition}")
    examples = content.get("worked_examples", [])
    if isinstance(examples, list):
        for example in examples[:8]:
            if not isinstance(example, dict):
                continue
            heading = _clean(example.get("title"), 180)
            problem = _clean(example.get("problem"), 500)
            steps = example.get("steps", [])
            answer = _clean(example.get("answer"), 500)
            if heading and problem:
                lines.append(f"HOST 1: Worked example: {heading}. {problem}")
                if isinstance(steps, list):
                    for index, step in enumerate(steps[:10], 1):
                        item = _clean(step, 500)
                        if item:
                            lines.append(f"HOST 2: Step {index}. {item}")
                if answer:
                    lines.append(f"HOST 1: The final answer is {answer}")
    lines.extend([
        "HOST 2: Before we finish, review the learning objectives and try the practice questions attached to this lesson.",
        "HOST 1: Summarise the main idea without looking at your notes. If you cannot explain it yet, revisit that section and ask your teacher for help.",
        "HOST 2: Thank you for learning with Think Tank. See you in the next episode.",
    ])
    script = "\n\n".join(lines)
    if len(script) > 20000:
        raise PodcastProductionError("script_too_long", "The lesson is too large for one podcast episode.")
    return script


def create_podcast_script(topic_id, admin_id):
    with connection() as conn:
        row = conn.execute(
            """SELECT t.title,s.name AS subject,c.id AS content_id,c.content_json
               FROM topics t JOIN subjects s ON s.id=t.subject_id
               JOIN topic_lesson_content c ON c.topic_id=t.id
               WHERE t.id=%s AND t.status IN ('draft','review')
                 AND c.review_status='approved'
               ORDER BY c.version DESC LIMIT 1""",
            (topic_id,),
        ).fetchone()
        if not row:
            raise PodcastProductionError("approved_lesson_required",
                "A teacher-approved lesson and a non-published topic are required before a podcast script can be drafted.", 409)
        script = build_podcast_script(row["title"], row["subject"], row["content_json"])
        version = conn.execute(
            "SELECT COALESCE(MAX(version),0)+1 AS next_version FROM podcast_scripts WHERE topic_id=%s",
            (topic_id,),
        ).fetchone()["next_version"]
        created = conn.execute(
            """INSERT INTO podcast_scripts
                 (topic_id,lesson_content_id,version,title,script_text,status,generated_by_admin)
               VALUES (%s,%s,%s,%s,%s,'draft',%s)
               RETURNING id,version,title,status,created_at""",
            (topic_id,row["content_id"],version,row["title"],script,admin_id),
        ).fetchone()
    return {
        "id": str(created["id"]), "version": created["version"],
        "title": created["title"], "status": created["status"],
        "script_text": script, "created_at": created["created_at"].isoformat(),
    }
