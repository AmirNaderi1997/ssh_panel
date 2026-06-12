#!/bin/bash
set -e

# SSH Manager Remote Agent Installer
# Target: Ubuntu/Debian VPS nodes

echo "=================================================="
echo "      SSH Manager Pro - Remote Agent Installer    "
echo "=================================================="

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run this installation script as root (sudo)."
  exit 1
fi

echo "[1/4] Installing system dependencies..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git iptables

echo "[2/4] Scaffolding agent directory..."
mkdir -p /opt/ssh-agent
cd /opt/ssh-agent

# Create virtual env
python3 -m venv venv
source venv/bin/activate

# Install Python modules
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple || pip install --upgrade pip
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple fastapi uvicorn psutil pydantic-settings || pip install fastapi uvicorn psutil pydantic-settings

# Create config .env
cat << 'EOF' > .env
PORT=8080
SHARED_SECRET=agentsharedsecretforauthandencryption
EOF

# Create main script
mkdir -p agents/agent
cat << 'EOF' > agents/agent/__init__.py
EOF

cat << 'EOF' > agents/agent/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PORT: int = 8080
    SHARED_SECRET: str = "agentsharedsecretforauthandencryption"

agent_settings = AgentSettings()
EOF

cat << 'EOF' > agents/agent/main.py
from fastapi import FastAPI, Depends, Header, HTTPException, status
import psutil
import subprocess
from pydantic import BaseModel
from agents.agent.config import agent_settings

app = FastAPI(title="SSH Manager Remote Agent", version="1.0.0")

async def verify_secret(x_agent_secret: str = Header(..., description="Agent Shared Token")) -> None:
    if x_agent_secret != agent_settings.SHARED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized agent request token"
        )

class LinuxUserCreate(BaseModel):
    username: str
    password: str
    expiry: str  # YYYY-MM-DD

@app.post("/users", dependencies=[Depends(verify_secret)])
def create_linux_user(user: LinuxUserCreate):
    check = subprocess.run(["id", user.username], capture_output=True)
    if check.returncode == 0:
        raise HTTPException(status_code=400, detail="Linux user already exists")
    create_cmd = ["useradd", "-m", "-s", "/usr/sbin/nologin", "-e", user.expiry, user.username]
    res = subprocess.run(create_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {res.stderr}")
    passwd_cmd = subprocess.Popen(["chpasswd"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = passwd_cmd.communicate(input=f"{user.username}:{user.password}")
    if passwd_cmd.returncode != 0:
        subprocess.run(["userdel", "-r", user.username])
        raise HTTPException(status_code=500, detail=f"Failed to set password: {stderr}")
    return {"status": "SUCCESS", "message": f"User {user.username} created"}

@app.delete("/users/{username}", dependencies=[Depends(verify_secret)])
def delete_linux_user(username: str):
    res = subprocess.run(["userdel", "-r", username], capture_output=True, text=True)
    if res.returncode != 0 and "does not exist" not in res.stderr:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {res.stderr}")
    return {"status": "SUCCESS", "message": f"User {username} deleted"}

@app.get("/stats", dependencies=[Depends(verify_secret)])
def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0.1, 0.2, 0.1]
    }
EOF

echo "[3/4] Creating systemd service file..."
cat << 'EOF' > /etc/systemd/system/ssh-agent.service
[Unit]
Description=SSH Manager Pro Remote Agent Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ssh-agent
ExecStart=/opt/ssh-agent/venv/bin/python3 -m uvicorn agents.agent.main:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "[4/4] Starting agent service..."
systemctl daemon-reload
systemctl enable ssh-agent
systemctl start ssh-agent

echo "=================================================="
echo "    Installation Successful! Agent Port: 8080    "
echo "=================================================="
