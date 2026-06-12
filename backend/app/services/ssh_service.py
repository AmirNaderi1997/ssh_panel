import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import asyncssh
from backend.app.core.exceptions import SSHConnectionException, BusinessRuleException
from backend.app.core.logging import logger
from backend.app.core.security import decrypt_field
from backend.app.models.server import Server


class SSHService:
    @asynccontextmanager
    async def _connect(self, server: Server):
        """Establish an async SSH connection to the remote server using key or password."""
        connect_kwargs = {
            "host": server.ip_address,
            "port": server.ssh_port,
            "username": server.root_username,
            "known_hosts": None,  # Ignore known hosts check for ease of dynamic server additions
        }

        if server.auth_method == "SSH_KEY":
            if not server.ssh_key:
                raise BusinessRuleException(f"SSH Key not configured for server {server.name}")
            connect_kwargs["client_keys"] = [asyncssh.import_private_key(server.ssh_key)]
        else:
            if not server.root_password_encrypted:
                raise BusinessRuleException(f"Root password not configured for server {server.name}")
            decrypted_password = decrypt_field(server.root_password_encrypted)
            connect_kwargs["password"] = decrypted_password

        try:
            async with asyncssh.connect(**connect_kwargs) as conn:
                yield conn
        except Exception as e:
            logger.error("SSH connection failed", server=server.name, error=str(e))
            raise SSHConnectionException(server.name, str(e))

    async def execute_command(self, server: Server, command: str) -> tuple[int, str, str]:
        """Execute a shell command on a server and return exit code, stdout, and stderr."""
        async with self._connect(server) as conn:
            result = await conn.run(command)
            return result.exit_status, result.stdout, result.stderr

    async def check_connectivity(self, server: Server) -> bool:
        """Check if connection to the server can be established and authenticated."""
        try:
            async with self._connect(server) as conn:
                return True
        except Exception:
            return False

    async def check_user_exists(self, server: Server, username: str) -> bool:
        """Check if a Linux user account exists on the server."""
        code, stdout, _ = await self.execute_command(server, f"id {username}")
        return code == 0

    async def create_linux_user(self, server: Server, username: str, password: str, expiry: datetime) -> None:
        """Create a Linux user account with password and expiration date."""
        # Check if already exists
        exists = await self.check_user_exists(server, username)
        if exists:
            raise BusinessRuleException(f"User {username} already exists on server {server.name}")

        # Command to create user, set shell to /usr/sbin/nologin or similar for VPN usage
        # Format expiration date as YYYY-MM-DD
        expiry_str = expiry.strftime("%Y-%m-%d")
        
        # Useradd command. We use nologin or false to prevent shell login, only allowing SSH tunneling
        create_cmd = (
            f"useradd -m -s /usr/sbin/nologin -e {expiry_str} {username}"
        )
        code, _, stderr = await self.execute_command(server, create_cmd)
        if code != 0:
            raise BusinessRuleException(f"Failed to create user: {stderr}")

        # Set password
        passwd_cmd = f"echo '{username}:{password}' | chpasswd"
        code, _, stderr = await self.execute_command(server, passwd_cmd)
        if code != 0:
            # Rollback user creation
            await self.execute_command(server, f"userdel -r {username}")
            raise BusinessRuleException(f"Failed to set user password: {stderr}")

    async def delete_linux_user(self, server: Server, username: str) -> None:
        """Delete a Linux user account and their home directory."""
        code, _, stderr = await self.execute_command(server, f"userdel -r {username}")
        # Note: If user does not exist, userdel returns non-zero, we check if they exist first or ignore
        if code != 0 and "does not exist" not in stderr:
            raise BusinessRuleException(f"Failed to delete user: {stderr}")

    async def change_password(self, server: Server, username: str, new_password: str) -> None:
        """Update a Linux user's password."""
        passwd_cmd = f"echo '{username}:{new_password}' | chpasswd"
        code, _, stderr = await self.execute_command(server, passwd_cmd)
        if code != 0:
            raise BusinessRuleException(f"Failed to change password: {stderr}")

    async def set_expiration(self, server: Server, username: str, expiry: datetime) -> None:
        """Change the expiration date of a Linux user account."""
        expiry_str = expiry.strftime("%Y-%m-%d")
        code, _, stderr = await self.execute_command(server, f"chage -E {expiry_str} {username}")
        if code != 0:
            raise BusinessRuleException(f"Failed to set account expiration: {stderr}")

    async def lock_user(self, server: Server, username: str) -> None:
        """Lock a Linux user account (suspend)."""
        code, _, stderr = await self.execute_command(server, f"usermod -L {username}")
        if code != 0:
            raise BusinessRuleException(f"Failed to lock user: {stderr}")

    async def unlock_user(self, server: Server, username: str) -> None:
        """Unlock a Linux user account (activate)."""
        code, _, stderr = await self.execute_command(server, f"usermod -U {username}")
        if code != 0:
            raise BusinessRuleException(f"Failed to unlock user: {stderr}")

    async def get_active_sessions(self, server: Server) -> list[dict]:
        """Fetch active SSH login sessions from the server."""
        # Runs command to list active processes for sshd or netstat/ss connections
        # Specifically we can use `w -h` or parse ss command for established ssh connections.
        # Let's run `w -h` to see logged in users: username, tty, ip, login_time, idle, what
        code, stdout, stderr = await self.execute_command(server, "w -h")
        if code != 0:
            logger.error("Failed to run 'w' command on server", server=server.name, error=stderr)
            return []

        sessions = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                # w output: USER TTY FROM LOGIN@ IDLE WHAT
                sessions.append({
                    "username": parts[0],
                    "tty": parts[1],
                    "source_ip": parts[2],
                    "login_time": parts[3],
                })
        return sessions

    async def get_system_stats(self, server: Server) -> dict:
        """Get system resources utilization stats (CPU, RAM, Disk)."""
        # Get RAM usage
        # free -m -> returns used/total
        ram_cmd = "free | grep Mem | awk '{print $3/$2 * 100}'"
        
        # Get CPU usage
        cpu_cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
        
        # Get Disk usage
        disk_cmd = "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"

        # Get Load Average
        load_cmd = "cat /proc/loadavg | awk '{print $1,$2,$3}'"

        # Execute combined commands to save roundtrips
        combined_cmd = f"{ram_cmd} && {cpu_cmd} && {disk_cmd} && {load_cmd}"
        code, stdout, stderr = await self.execute_command(server, combined_cmd)
        
        if code != 0:
            logger.error("Failed to collect stats from server", server=server.name, error=stderr)
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "disk_percent": 0.0,
                "load_avg": [0.0, 0.0, 0.0]
            }

        lines = stdout.strip().split("\n")
        try:
            ram_percent = float(lines[0]) if len(lines) > 0 else 0.0
            cpu_percent = float(lines[1]) if len(lines) > 1 else 0.0
            disk_percent = float(lines[2]) if len(lines) > 2 else 0.0
            load_avg = [float(x) for x in lines[3].split()] if len(lines) > 3 else [0.0, 0.0, 0.0]
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "ram_percent": round(ram_percent, 2),
                "disk_percent": round(disk_percent, 2),
                "load_avg": load_avg
            }
        except (ValueError, IndexError) as e:
            logger.error("Error parsing stats", server=server.name, error=str(e), output=stdout)
            return {
                "cpu_percent": 0.0,
                "ram_percent": 0.0,
                "disk_percent": 0.0,
                "load_avg": [0.0, 0.0, 0.0]
            }
