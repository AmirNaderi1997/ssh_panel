from fastapi import FastAPI, Depends, Header, HTTPException, status
import psutil
import subprocess
from pydantic import BaseModel
from agents.agent.config import agent_settings

app = FastAPI(title="SSH Manager Remote Agent", version="1.0.0")


async def verify_secret(x_agent_secret: str = Header(..., description="Agent Shared Token")) -> None:
    """Validate that the request header matches the shared panel secret."""
    if x_agent_secret != agent_settings.SHARED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized agent request token"
        )


# Schemas
class LinuxUserCreate(BaseModel):
    username: str
    password: str
    expiry: str  # YYYY-MM-DD


class NginxConfigDeploy(BaseModel):
    domain: str
    cert_pem: str
    key_pem: str


# Endpoints
@app.post("/users", dependencies=[Depends(verify_secret)])
def create_linux_user(user: LinuxUserCreate):
    """Create a Linux system user account on this VPS."""
    # check if user exists
    check = subprocess.run(["id", user.username], capture_output=True)
    if check.returncode == 0:
        raise HTTPException(status_code=400, detail="Linux user already exists")

    # useradd
    create_cmd = ["useradd", "-m", "-s", "/usr/sbin/nologin", "-e", user.expiry, user.username]
    res = subprocess.run(create_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {res.stderr}")

    # chpasswd
    passwd_cmd = subprocess.Popen(["chpasswd"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = passwd_cmd.communicate(input=f"{user.username}:{user.password}")
    if passwd_cmd.returncode != 0:
        # Rollback
        subprocess.run(["userdel", "-r", user.username])
        raise HTTPException(status_code=500, detail=f"Failed to set password: {stderr}")

    return {"status": "SUCCESS", "message": f"User {user.username} created"}


@app.delete("/users/{username}", dependencies=[Depends(verify_secret)])
def delete_linux_user(username: str):
    """Delete a Linux system user account and home directory."""
    res = subprocess.run(["userdel", "-r", username], capture_output=True, text=True)
    if res.returncode != 0 and "does not exist" not in res.stderr:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {res.stderr}")
    return {"status": "SUCCESS", "message": f"User {username} deleted"}


@app.get("/stats", dependencies=[Depends(verify_secret)])
def get_system_metrics():
    """Query current CPU, RAM, and Disk loads."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "load_avg": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0.1, 0.2, 0.1]
    }
