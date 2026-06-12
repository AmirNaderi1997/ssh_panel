#!/bin/bash
set -e

BACKUP_DIR="/opt/ssh-manager-pro/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="db_dump_$TIMESTAMP.sql.gz"

echo "Backing up database container..."

# Execute pg_dump inside db container and compress
docker exec -t ssh_manager_db pg_dumpall -c -U postgres | gzip > "$BACKUP_DIR/$FILENAME"

echo "Backup created successfully: $BACKUP_DIR/$FILENAME"
