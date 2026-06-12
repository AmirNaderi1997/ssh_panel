#!/bin/bash

# Exit on any error
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}      SSH Manager Pro Auto-Installer      ${NC}"
echo -e "${GREEN}==========================================${NC}"

# 1. Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install git.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Installing docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose plugin.${NC}"
    exit 1
fi

# 2. Ask for GitHub Repository URL
# Check if running interactively (TTY). If not (e.g. curl | bash), use default URL.
if [ -t 0 ]; then
    read -p "Enter your GitHub repository URL [default: https://github.com/AmirNaderi1997/ssh_panel.git]: " REPO_INPUT
    REPO_URL=${REPO_INPUT:-"https://github.com/AmirNaderi1997/ssh_panel.git"}
else
    REPO_URL="https://github.com/AmirNaderi1997/ssh_panel.git"
fi

INSTALL_DIR="/opt/ssh_manager_pro"

# 3. Clone or Update Repository
echo -e "${YELLOW}Cloning repository to $INSTALL_DIR...${NC}"
sudo mkdir -p "$INSTALL_DIR"
CODE_RETRIEVED=false

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${YELLOW}Directory $INSTALL_DIR already exists as a Git repository. Fetching latest changes...${NC}"
    cd "$INSTALL_DIR"
    if timeout 15 sudo GIT_CONFIG_NOSYSTEM=1 HOME=/tmp git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=10 fetch --all && \
       timeout 15 sudo GIT_CONFIG_NOSYSTEM=1 HOME=/tmp git reset --hard origin/main && \
       timeout 15 sudo GIT_CONFIG_NOSYSTEM=1 HOME=/tmp git pull; then
        CODE_RETRIEVED=true
    else
        echo -e "${YELLOW}Git update failed or timed out. Falling back to tarball download...${NC}"
    fi
else
    # Try direct clone with a low speed timeout first, isolating git configuration to bypass any insteadOf rewrites
    echo -e "${YELLOW}Trying to clone from GitHub directly (with timeout)...${NC}"
    if timeout 15 sudo GIT_CONFIG_NOSYSTEM=1 HOME=/tmp git -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=10 clone --depth 1 "$REPO_URL" "$INSTALL_DIR"; then
        CODE_RETRIEVED=true
    else
        echo -e "${YELLOW}Git clone failed or timed out. Falling back to tarball download...${NC}"
    fi
fi

# Fallback: Download via curl + extract via tar
if [ "$CODE_RETRIEVED" = false ]; then
    echo -e "${YELLOW}Downloading repository tarball from GitHub...${NC}"
    TARBALL_URL="https://github.com/AmirNaderi1997/ssh_panel/archive/refs/heads/main.tar.gz"
    if sudo curl -fsSL -m 30 "$TARBALL_URL" -o /tmp/ssh_panel.tar.gz; then
        echo -e "${YELLOW}Extracting repository contents...${NC}"
        sudo tar -xzf /tmp/ssh_panel.tar.gz -C "$INSTALL_DIR" --strip-components=1
        sudo rm -f /tmp/ssh_panel.tar.gz
        echo -e "${GREEN}Codebase retrieved successfully via tarball!${NC}"
        CODE_RETRIEVED=true
    else
        echo -e "${RED}Failed to download repository tarball. Please check your internet connection and DNS settings.${NC}"
        exit 1
    fi
fi

cd "$INSTALL_DIR"

# 4. Generate Environment Variables
echo -e "${YELLOW}Configuring environment variables...${NC}"

# Generate 32-byte url-safe base64 key for Fernet
if command -v python3 &> /dev/null; then
    # Try to use python's cryptography if installed, otherwise fallback to openssl base64
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || openssl rand -base64 32)
else
    ENCRYPTION_KEY=$(openssl rand -base64 32)
fi

SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
AGENT_SECRET=$(openssl rand -hex 24)

# Create the .env file in the docker directory
sudo mkdir -p "$INSTALL_DIR/docker"
sudo bash -c "cat > $INSTALL_DIR/docker/.env <<EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=ssh_manager
SECRET_KEY=${SECRET_KEY}
ENCRYPTION_KEY=${ENCRYPTION_KEY}
AGENT_SHARED_SECRET=${AGENT_SECRET}
EOF"

# 5. Build and Deploy
echo -e "${YELLOW}Building and starting services...${NC}"
cd "$INSTALL_DIR/docker"

# Check if using docker compose (v2) or docker-compose (v1)
if docker compose version &> /dev/null; then
    sudo docker compose up -d --build
else
    sudo docker-compose up -d --build
fi

# 6. Final Instructions
SERVER_IP=$(curl -s ifconfig.me || echo "YOUR_SERVER_IP")

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "Web Panel URL: http://${SERVER_IP}"
echo -e "Default Admin: admin / adminpassword123 (Please change after logging in)"
echo -e "Install Directory: ${INSTALL_DIR}"
echo -e "${GREEN}==========================================${NC}"
