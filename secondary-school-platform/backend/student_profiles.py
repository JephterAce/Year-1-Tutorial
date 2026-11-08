"""Private student profile read/update operations."""
import re
from database import connection


class ProfileError(ValueError):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status


def get_profile(student_id):
    with connection() as conn:
        row = conn.execute(
            """SELECT id,email,display_name,username,class_level,bio,
                      profile_visibility,profile_photo_key,created_at
               FROM students WHERE id=%s AND is_synthetic_qa=false""", (student_id,)
        ).fetchone()
    if not row:
        raise ProfileError("not_found", "Student profile not found.", 404)
    return {key: (str(value) if key == "id" else value)
            for key, value in row.items()}


def update_profile(student_id, changes):
    if not isinstance(changes, dict) or not changes:
        raise ProfileError("invalid_profile", "Provide at least one profile field.")
    allowed = {"display_name", "username", "bio"}
    if set(changes) - allowed:
        raise ProfileError("unsupported_field", "One or more profile fields cannot be changed here.")
    values = {}
    if "display_name" in changes:
        value = changes["display_name"]
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 80:
            raise ProfileError("invalid_display_name", "Display name must be 1–80 characters.")
        values["display_name"] = value.strip()
    if "username" in changes:
        value = changes["username"]
        if value is not None:
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_]{3,24}", value):
                raise ProfileError("invalid_username", "Username must be 3–24 letters, numbers or underscores.")
            value = value.lower()
        values["username"] = value
    if "bio" in changes:
        value = changes["bio"]
        if value is not None and (not isinstance(value, str) or len(value) > 240):
            raise ProfileError("invalid_bio", "Bio must be 240 characters or fewer.")
        values["bio"] = value.strip() if isinstance(value, str) else None
    with connection() as conn:
        if "username" in values and values["username"]:
            duplicate = conn.execute(
                "SELECT 1 FROM students WHERE lower(username)=lower(%s) AND id<>%s",
                (values["username"], student_id)
            ).fetchone()
            if duplicate:
                raise ProfileError("username_taken", "That username is already in use.", 409)
        assignments = ", ".join(f"{column}=%s" for column in values)
        params = list(values.values()) + [student_id]
        row = conn.execute(
            f"""UPDATE students SET {assignments},updated_at=now()
                WHERE id=%s AND is_synthetic_qa=false RETURNING id,email,display_name,username,class_level,bio,
                profile_visibility,profile_photo_key,created_at""", params
        ).fetchone()
        if not row:
            raise ProfileError("not_found", "Student profile not found.", 404)
    return {key: (str(value) if key == "id" else value)
            for key, value in row.items()}
