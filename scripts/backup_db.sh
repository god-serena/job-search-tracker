#!/usr/bin/env bash
set -euo pipefail

RETENTION_COUNT=5

if [ -d "/backups" ] && command -v pg_dump >/dev/null 2>&1; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="jobsearch_backup_${TIMESTAMP}.sql"
    echo "Creating database backup inside container: /backups/${BACKUP_FILE}"
    pg_dump -U "${POSTGRES_USER:-jobsearch}" "${POSTGRES_DB:-jobsearch}" > "/backups/${BACKUP_FILE}"
    echo "Pruning older backups (keeping latest ${RETENTION_COUNT})..."
    cd /backups && ls -tp jobsearch_backup_*.sql 2>/dev/null | grep -v '/$' | tail -n +$((RETENTION_COUNT + 1)) | xargs -I {} rm -f -- {} 2>/dev/null || true
    echo "Done! Backup created at /backups/${BACKUP_FILE}"
else
    echo "Triggering backup in db container via docker compose..."
    docker compose exec -T db sh -c '
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="jobsearch_backup_${TIMESTAMP}.sql"
        pg_dump -U jobsearch jobsearch > "/backups/${BACKUP_FILE}"
        cd /backups && ls -tp jobsearch_backup_*.sql 2>/dev/null | grep -v "/$" | tail -n +6 | xargs -I {} rm -f -- {} 2>/dev/null || true
        echo "Created /backups/${BACKUP_FILE}"
    '
    echo "Backup successfully written to ~/!db_backups/"
fi
