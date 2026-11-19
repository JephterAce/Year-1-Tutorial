#!/usr/bin/env bash
set -euo pipefail

: "${SOURCE_DATABASE_URL:?Set SOURCE_DATABASE_URL to the source database}"
: "${RESTORE_DATABASE_URL:?Set RESTORE_DATABASE_URL to a local restore database}"
: "${CONFIRM_RESTORE_TARGET:?Set CONFIRM_RESTORE_TARGET=thinktank_restore_rehearsal}"

if [[ "$CONFIRM_RESTORE_TARGET" != "thinktank_restore_rehearsal" ]]; then
  echo "Refusing restore: explicit target confirmation did not match." >&2
  exit 2
fi

read -r source_host source_db restore_host restore_db < <(
  python - "$SOURCE_DATABASE_URL" "$RESTORE_DATABASE_URL" <<'PY'
import sys
from urllib.parse import urlparse
source, restore = map(urlparse, sys.argv[1:])
print(source.hostname or "", (source.path or "").lstrip("/"),
      restore.hostname or "", (restore.path or "").lstrip("/"))
PY
)

case "$restore_host" in
  localhost|127.0.0.1|::1) ;;
  *)
    echo "Refusing restore: destination must be local, not $restore_host." >&2
    exit 2
    ;;
esac

if [[ "$restore_db" != "thinktank_restore_rehearsal" ]]; then
  echo "Refusing restore: destination database must be thinktank_restore_rehearsal." >&2
  exit 2
fi

if [[ "$source_host" == "$restore_host" && "$source_db" == "$restore_db" ]]; then
  echo "Refusing restore: source and destination are the same database." >&2
  exit 2
fi

dump_file="$(mktemp "${TMPDIR:-/tmp}/thinktank-backup-XXXXXX.dump")"
trap 'rm -f "$dump_file"' EXIT

echo "Creating a logical backup; source is read-only."
pg_dump --format=custom --no-owner --no-acl --file "$dump_file" "$SOURCE_DATABASE_URL"

echo "Restoring only into the explicitly named local rehearsal database."
pg_restore --exit-on-error --clean --if-exists --no-owner --no-acl \
  --dbname "$RESTORE_DATABASE_URL" "$dump_file"

echo "Checking restored database identity and schema."
psql "$RESTORE_DATABASE_URL" -v ON_ERROR_STOP=1 -Atc \
  "SELECT current_database() || '|' || current_setting('server_version')"

echo "Backup/restore rehearsal completed. Temporary dump removed."
