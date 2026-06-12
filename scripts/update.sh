#!/bin/bash
set -e

echo "Updating SSH Manager Pro..."

cd /opt/ssh-manager-pro

# Pull new docker images if building on hub, or rebuild locally
docker-compose -f docker/docker-compose.yml build
docker-compose -f docker/docker-compose.yml up -d

# Run migrations
docker-compose -f docker/docker-compose.yml exec backend alembic upgrade head

echo "Update successful!"
