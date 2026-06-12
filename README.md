# SSH Manager Pro — Enterprise SSH VPN Management Panel

SSH Manager Pro is a production-grade, centralized web dashboard designed to manage SSH VPN tunneling nodes and client accounts. It is built using FastAPI (Python) on the backend, React (TypeScript) on the frontend, Celery for tasks queues, PostgreSQL for data storage, and Redis for rate-limiting, session caching, and broker operations.

## Features

- **Centralized Server Nodes management**: Support adding remote nodes via SSH Keys or Root Password.
- **SSH VPN Accounts Automation**: Create, suspend, delete, and migrate user accounts on remote servers instantly.
- **Traffic and Bandwidth Accounting**: Tracks upload and download bytes and auto-suspends accounts that exceed quotas.
- **Real-Time Active Sessions**: Displays connected tunneling client sessions and supports forcing disconnections.
- **SSL certificate automation**: Auto issue Let's Encrypt certificates using HTTP-01 challenge and reload Nginx.
- **Reseller Operations**: Allocates credits and credit balances to reseller groups.
- **Two-Factor Authentication (2FA)**: Strengthen administrator logins using Google Authenticator / Authy TOTP.
- **Compressed Backups**: Complete database JSON gzip serialization and restoration mechanisms.

## Directory Structure

```
webSSHpanel/
├── backend/            # FastAPI python backend api
├── frontend/           # Vite + React + TS frontend panel
├── agents/             # Remote VPS installer & lighter server agent
├── docker/             # Docker Compose orchestration
├── scripts/            # Install, update, and backup scripts
└── README.md
```

## Getting Started

### 1. Panel Installation
To deploy the dashboard panel, run the central install script on your server:

```bash
curl -fsSL https://raw.githubusercontent.com/AmirNaderi1997/ssh_panel/main/install.sh | bash
```

This will verify docker dependencies, configure random secret keys in `docker/.env`, and spin up the backend API, Postgres DB, Redis caching, Celery worker threads, and serve the React panel on Port 80.

**Default Credentials:**
- Username: `admin`
- Password: `adminpassword123`

### 2. Node Agent Installation
Deploy the lightweight agent on target remote VPS nodes using:

```bash
curl -fsSL https://raw.githubusercontent.com/AmirNaderi1997/ssh_panel/main/agents/install.sh | bash
```

The agent runs as a systemd daemon (`ssh-agent.service`) listening on Port 8080 and handles user creations and health checks requests authenticated by a shared secret token.

### 3. Setting Up a Secure WireGuard Tunnel (Optional)
If you want to place the Panel Server in one region (e.g. domestically) and route SSH VPN traffic to an Offshore VPS (Agent Server), you can build an encrypted WireGuard tunnel.

Run the tunnel setup script on **both** your Panel Server and your Agent Server:
```bash
sudo bash scripts/tunnel.sh
```
1. Run it on the **Panel Server** first and choose `Option 1`. It will configure `iptables` and give you a Public Key.
2. Run it on the **Agent Server** and choose `Option 2`. It will ask for the Panel's Public Key.
3. Once completed, all SSH VPN traffic hitting the Panel server on your chosen port will be routed encrypted to the offshore Agent server.

## REST API Versioning

API endpoints are prefix Version 1 under `/api/v1` and documentations are fully available at `/docs` (Swagger UI).
- `/auth`: Handles user logins, 2FA setup, and JWT token refreshes.
- `/users`: CRUD actions for SSH VPN user accounts.
- `/servers`: Node registrations and ping connectivity tests.
- `/domains`: link hostnames and verify DNS routing.
- `/ssl`: Trigger Let's Encrypt certificate issuance.
- `/backups`: Manual backup triggers and database restoration.
- `/dashboard`: Statistical metrics aggregations and historical arrays charts.
