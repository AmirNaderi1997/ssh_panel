import os
import uuid
from backend.app.core.exceptions import BusinessRuleException
from backend.app.core.logging import logger
from backend.app.models.domain import Domain
from backend.app.models.server import Server
from backend.app.services.ssh_service import SSHService


class NginxService:
    def __init__(self) -> None:
        self.ssh_service = SSHService()

    def _generate_vhost_config(self, domain: str, ssl_cert_path: str | None = None, ssl_key_path: str | None = None) -> str:
        """Generate Nginx Virtual Host config file content."""
        if ssl_cert_path and ssl_key_path:
            # SSL Configuration
            config = f"""server {{
    listen 80;
    server_name {domain};
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {domain};

    ssl_certificate {ssl_cert_path};
    ssl_certificate_key {ssl_key_path};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        else:
            # Standard HTTP Configuration
            config = f"""server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
        return config

    async def deploy_domain_vhost(self, server: Server, domain: Domain, cert_pem: str | None = None, key_pem: str | None = None) -> None:
        """Write Nginx virtual host file on remote server and reload config."""
        logger.info("Deploying Nginx Virtual Host config", server=server.name, domain=domain.domain)
        
        # Paths
        vhost_path = f"/etc/nginx/sites-available/{domain.domain}"
        symlink_path = f"/etc/nginx/sites-enabled/{domain.domain}"
        
        cert_path = None
        key_path = None
        
        if cert_pem and key_pem:
            cert_path = f"/etc/nginx/ssl/{domain.domain}.crt"
            key_path = f"/etc/nginx/ssl/{domain.domain}.key"
            
            # Make sure ssl folder exists
            await self.ssh_service.execute_command(server, "mkdir -p /etc/nginx/ssl")
            
            # Write cert files
            # Echoing multi-line PEM files using standard EOF cat is highly robust
            cert_write_cmd = f"cat << 'EOF' > {cert_path}\n{cert_pem}\nEOF"
            key_write_cmd = f"cat << 'EOF' > {key_path}\n{key_pem}\nEOF"
            
            await self.ssh_service.execute_command(server, cert_write_cmd)
            await self.ssh_service.execute_command(server, key_write_cmd)
            
        config_content = self._generate_vhost_config(domain.domain, cert_path, key_path)
        
        # Write config file on server
        write_config_cmd = f"cat << 'EOF' > {vhost_path}\n{config_content}\nEOF"
        code, _, stderr = await self.ssh_service.execute_command(server, write_config_cmd)
        if code != 0:
            raise BusinessRuleException(f"Failed to write nginx config: {stderr}")
            
        # Enable config by symlinking
        symlink_cmd = f"ln -sf {vhost_path} {symlink_path}"
        await self.ssh_service.execute_command(server, symlink_cmd)

        # Test and reload Nginx
        test_code, _, test_stderr = await self.ssh_service.execute_command(server, "nginx -t")
        if test_code != 0:
            # Rollback symlink
            await self.ssh_service.execute_command(server, f"rm -f {symlink_path}")
            raise BusinessRuleException(f"Nginx config validation failed: {test_stderr}")
            
        reload_code, _, reload_stderr = await self.ssh_service.execute_command(server, "systemctl reload nginx")
        if reload_code != 0:
            raise BusinessRuleException(f"Nginx reload failed: {reload_stderr}")
            
        logger.info("Nginx config deployed successfully", server=server.name, domain=domain.domain)
