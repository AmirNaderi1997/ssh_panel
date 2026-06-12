#!/bin/bash
set -e

echo "=================================================="
echo "          SSH Manager Pro Installation           "
echo "=================================================="

# Check requirements
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error: docker is not installed. Installing docker...' >&2
  curl -fsSL https://get.docker.com | sh
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed. Installing...' >&2
  sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

# Create directory
mkdir -p /opt/ssh-manager-pro
cd /opt/ssh-manager-pro

# In production, we pull repository files here
# For local scaffold setup we copy docker files
echo "Configuring environment variables..."
if [ ! -f docker/.env ]; then
  cp docker/.env.example docker/.env
  # Generate unique random keys
  SECRET_RAND=$(openssl rand -hex 32)
  ENCRYPT_RAND=$(openssl rand -base64 32)
  sed -i "s/SECRET_KEY=supersecretkeychangeinproduction1234567890/SECRET_KEY=$SECRET_RAND/g" docker/.env
  sed -i "s|ENCRYPTION_KEY=32bytekeyforfernetencryption_mustbe32bytes=|ENCRYPTION_KEY=$ENCRYPT_RAND|g" docker/.env
fi

echo "Starting container services via Docker Compose..."
docker-compose -f docker/docker-compose.yml up -d

echo "=================================================="
echo "    Installation Complete! Access Panel on Port 80"
echo "=================================================="
