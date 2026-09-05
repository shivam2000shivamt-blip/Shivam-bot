#!/data/data/com.termux/files/usr/bin/bash
set -e
script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$script_dir"
db_path="${DB_PATH:-$script_dir/shivam_store.sqlite3}"
backup_dir="${BACKUP_DIR:-$script_dir/backups}"
retention_days="${BACKUP_RETENTION_DAYS:-14}"
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
stamp="$(date +%Y%m%d_%H%M%S)"
if [ -f "$db_path" ]; then
  backup_path="$backup_dir/shivam_store_${stamp}.sqlite3"
  DB_PATH="$db_path" BACKUP_PATH="$backup_path" python - <<'PY'
import os, sqlite3
src=os.environ["DB_PATH"]
dst=os.environ["BACKUP_PATH"]
with sqlite3.connect(src, timeout=30) as source, sqlite3.connect(dst) as target:
    source.backup(target)
    target.execute("PRAGMA integrity_check")
    result=target.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise SystemExit(f"Backup integrity check failed: {result}")
PY
  chmod 600 "$backup_path"
  find "$backup_dir" -type f -name 'shivam_store_*.sqlite3' -mtime +"$retention_days" -delete
  echo "Safe SQLite backup saved: $backup_path"
else
  echo "Database not found at: $db_path"
fi
