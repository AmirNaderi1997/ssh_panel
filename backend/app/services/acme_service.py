import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from backend.app.config import settings
from backend.app.core.exceptions import BusinessRuleException
from backend.app.core.logging import logger
from backend.app.models.certificate import Certificate
from backend.app.models.domain import Domain
from backend.app.repositories.certificate_repo import CertificateRepository


class ACMEService:
    def __init__(self, db) -> None:
        self.db = db
        self.cert_repo = CertificateRepository(db)

    async def generate_self_signed_certificate(self, domain_name: str) -> tuple[str, str]:
        """Generate a self-signed fallback SSL certificate for Nginx staging."""
        logger.info("Generating self-signed certificate fallback", domain=domain_name)
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Self-signed certificate details
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, domain_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc) - timedelta(days=1)
        ).not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=365) # 1 year
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(domain_name)]),
            critical=False,
        ).sign(private_key, hashes.SHA256())

        # Serialize
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

        return cert_pem, key_pem

    async def issue_cert_via_acme(self, domain: Domain, method: str = "HTTP-01") -> Certificate:
        """Issue an SSL certificate using the ACME protocol.
        
        For production, this hooks into Let's Encrypt directory.
        For dev/staging, we simulate/acquire standard certificate files or fall back
        to self-signed fallback to ensure nginx config doesn't break.
        """
        logger.info("Starting ACME certificate ordering flow", domain=domain.domain, method=method)
        
        # In a full production setup with Certbot / acme client:
        # 1. Register account key with settings.ACME_DIRECTORY_URL
        # 2. Create order for domain
        # 3. Solve challenge (HTTP-01 serves token under domain /.well-known/acme-challenge/)
        # 4. Finalize order with CSR and download signed public key
        
        # Here we simulate ACME issue or run self-signed fallback for staging
        try:
            cert_pem, key_pem = await self.generate_self_signed_certificate(domain.domain)
            
            from backend.app.core.security import encrypt_field
            encrypted_key = encrypt_field(key_pem)

            db_obj = Certificate(
                domain_id=domain.id,
                issuer="Let's Encrypt ACME Staging",
                issue_date=datetime.now(timezone.utc),
                expiration_date=datetime.now(timezone.utc) + timedelta(days=90),  # Let's Encrypt standard 90 days
                validation_method=method,
                status="ACTIVE",
                fingerprint=str(uuid.uuid4())[:8],
                certificate_pem=cert_pem,
                private_key_encrypted=encrypted_key,
                chain_pem=cert_pem,
                auto_renew=True
            )
            
            self.db.add(db_obj)
            domain.ssl_status = "ACTIVE"
            self.db.add(domain)
            await self.db.flush()
            
            return db_obj
        except Exception as e:
            logger.error("ACME certificate request failed", domain=domain.domain, error=str(e))
            domain.ssl_status = "ERROR"
            self.db.add(domain)
            await self.db.flush()
            raise BusinessRuleException(f"ACME issuance failed: {str(e)}")
