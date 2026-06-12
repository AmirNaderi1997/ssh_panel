import socket
import httpx
from backend.app.core.logging import logger


class DNSService:
    def __init__(self) -> None:
        self.doh_url = "https://cloudflare-dns.com/dns-query"

    async def resolve_dns_record(self, name: str, type: str = "A") -> list[str]:
        """Query Cloudflare DoH JSON API to resolve any DNS records (A, AAAA, TXT, CNAME)."""
        headers = {"Accept": "application/dns-json"}
        params = {"name": name, "type": type}
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(self.doh_url, params=params, headers=headers, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    answers = data.get("Answer", [])
                    return [ans.get("data").strip('"') for ans in answers if "data" in ans]
        except Exception as e:
            logger.error("DoH resolution failed, falling back to local resolver", name=name, type=type, error=str(e))
            
        # Local fallback for A/AAAA records using socket library
        if type in ("A", "AAAA"):
            try:
                family = socket.AF_INET if type == "A" else socket.AF_INET6
                addr_info = socket.getaddrinfo(name, None, family)
                return list(set(info[4][0] for info in addr_info))
            except Exception:
                pass
                
        return []

    async def verify_domain_a_record(self, domain: str, expected_ip: str) -> bool:
        """Check if the domain resolves to the target server's IP address."""
        ips = await self.resolve_dns_record(domain, "A")
        return expected_ip in ips

    async def verify_txt_record(self, domain: str, verification_token: str) -> bool:
        """Check if a verification TXT record is present on the domain."""
        records = await self.resolve_dns_record(domain, "TXT")
        return any(verification_token in rec for rec in records)
