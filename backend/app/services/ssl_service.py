import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.exceptions import EntityNotFoundException, BusinessRuleException
from backend.app.models.domain import Domain
from backend.app.repositories.domain_repo import DomainRepository
from backend.app.repositories.server_repo import ServerRepository
from backend.app.repositories.certificate_repo import CertificateRepository
from backend.app.services.acme_service import ACMEService
from backend.app.services.dns_service import DNSService
from backend.app.services.nginx_service import NginxService


class SSLService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.domain_repo = DomainRepository(db)
        self.server_repo = ServerRepository(db)
        self.cert_repo = CertificateRepository(db)
        self.dns_service = DNSService()
        self.acme_service = ACMEService(db)
        self.nginx_service = NginxService()

    async def add_domain(self, domain_name: str, type: str, server_id: uuid.UUID) -> Domain:
        """Register a new domain and link it to a routing node."""
        existing = await self.domain_repo.get_by_name(domain_name)
        if existing:
            raise BusinessRuleException(f"Domain '{domain_name}' already registered")

        server = await self.server_repo.get(server_id)
        if not server:
            raise EntityNotFoundException("Server", server_id)

        domain = Domain(
            domain=domain_name,
            type=type,
            server_id=server_id,
            dns_status="PENDING",
            ssl_status="NONE",
        )
        self.db.add(domain)
        await self.db.flush()
        return domain

    async def verify_dns(self, domain_id: uuid.UUID) -> bool:
        """Run verification check on domain DNS record alignment."""
        domain = await self.domain_repo.get(domain_id)
        if not domain:
            raise EntityNotFoundException("Domain", domain_id)

        server = await self.server_repo.get(domain.server_id)
        if not server:
            raise EntityNotFoundException("Server", domain.server_id)

        # Verify A record
        is_verified = await self.dns_service.verify_domain_a_record(domain.domain, server.ip_address)
        domain.dns_status = "VERIFIED" if is_verified else "FAILED"
        self.db.add(domain)
        await self.db.flush()
        return is_verified

    async def issue_and_deploy_ssl(self, domain_id: uuid.UUID) -> None:
        """Validate DNS, order ACME certificate, and configure remote Nginx webserver."""
        domain = await self.domain_repo.get(domain_id)
        if not domain:
            raise EntityNotFoundException("Domain", domain_id)

        server = await self.server_repo.get(domain.server_id)
        if not server:
            raise EntityNotFoundException("Server", domain.server_id)

        # 1. Verify DNS
        dns_ok = await self.verify_dns(domain_id)
        if not dns_ok:
            raise BusinessRuleException(
                f"DNS A-Record verification failed. The domain '{domain.domain}' "
                f"does not resolve to target node IP '{server.ip_address}'."
            )

        # 2. Request certificate from ACME CA
        certificate = await self.acme_service.issue_cert_via_acme(domain, method="HTTP-01")

        # 3. Deploy to remote nginx instance
        from backend.app.core.security import decrypt_field
        decrypted_key = decrypt_field(certificate.private_key_encrypted)
        
        await self.nginx_service.deploy_domain_vhost(
            server=server,
            domain=domain,
            cert_pem=certificate.certificate_pem,
            key_pem=decrypted_key
        )
        
        domain.ssl_status = "ACTIVE"
        self.db.add(domain)
        await self.db.flush()
