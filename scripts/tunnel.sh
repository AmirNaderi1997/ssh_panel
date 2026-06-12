#!/bin/bash

# WireGuard Tunnel Configuration Script for SSH Manager Pro
# This script sets up a secure WireGuard tunnel between the Panel Server (Iran) and the Agent Server (Offshore).

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}    SSH Manager Pro - WireGuard Tunnel    ${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run this script as root (sudo bash tunnel.sh)${NC}"
    exit 1
fi

echo -e "${YELLOW}Installing WireGuard and required tools...${NC}"
apt-get update -y
apt-get install -y wireguard iptables iproute2 ufw

# Enable IPv4 forwarding
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sysctl -p

mkdir -p /etc/wireguard
cd /etc/wireguard
umask 077

echo ""
echo -e "Which server is this?"
echo -e "1) ${CYAN}Panel Server${NC} (Domestic / Iran - routes traffic to offshore)"
echo -e "2) ${CYAN}Agent Server${NC} (Offshore / Remote - runs the actual SSH VPN)"
read -p "Select mode [1/2]: " SERVER_MODE

# Generate Keys
PRIVATE_KEY=$(wg genkey)
PUBLIC_KEY=$(echo "$PRIVATE_KEY" | wg pubkey)

if [ "$SERVER_MODE" == "1" ]; then
    echo -e "\n${CYAN}=== PANEL SERVER CONFIGURATION ===${NC}"
    echo -e "Your Panel Server Public Key is:"
    echo -e "${GREEN}${PUBLIC_KEY}${NC}\n"
    
    echo -e "Please run this script on your ${YELLOW}Agent Server (Offshore)${NC} and select Option 2."
    read -p "Enter the Agent Server's Public Key: " PEER_PUB_KEY
    read -p "Enter the Agent Server's Public IP address: " PEER_IP
    read -p "Enter the port you want users to connect to on this Panel Server for SSH VPN (e.g., 2222): " SSH_FORWARD_PORT

    # Configure wg0 for Panel
    cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = ${PRIVATE_KEY}
Address = 10.8.0.1/24
ListenPort = 51820
# Setup NAT routing and Port Forwarding for SSH VPN
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostUp = iptables -t nat -A PREROUTING -p tcp --dport ${SSH_FORWARD_PORT} -j DNAT --to-destination 10.8.0.2:22
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -t nat -D PREROUTING -p tcp --dport ${SSH_FORWARD_PORT} -j DNAT --to-destination 10.8.0.2:22

[Peer]
PublicKey = ${PEER_PUB_KEY}
AllowedIPs = 10.8.0.2/32
Endpoint = ${PEER_IP}:51820
PersistentKeepalive = 25
EOF

    echo -e "\n${GREEN}Configuration saved. Starting WireGuard...${NC}"
    systemctl enable wg-quick@wg0
    systemctl restart wg-quick@wg0

    echo -e "${GREEN}==========================================${NC}"
    echo -e "Panel Server Tunnel configured!"
    echo -e "Internal IP: 10.8.0.1"
    echo -e "Traffic on port ${SSH_FORWARD_PORT} is now forwarded to the Offshore server via the tunnel."
    echo -e "You can securely connect your Panel to the Agent API using: http://10.8.0.2:5000"
    echo -e "${GREEN}==========================================${NC}"

elif [ "$SERVER_MODE" == "2" ]; then
    echo -e "\n${CYAN}=== AGENT SERVER (OFFSHORE) CONFIGURATION ===${NC}"
    echo -e "Your Agent Server Public Key is:"
    echo -e "${GREEN}${PUBLIC_KEY}${NC}\n"
    
    echo -e "Please ensure you have generated the Panel Server's Public Key."
    read -p "Enter the Panel Server's Public Key: " PEER_PUB_KEY
    read -p "Enter the Panel Server's Public IP address: " PEER_IP

    # Configure wg0 for Agent
    cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = ${PRIVATE_KEY}
Address = 10.8.0.2/24
ListenPort = 51820

[Peer]
PublicKey = ${PEER_PUB_KEY}
AllowedIPs = 10.8.0.1/32
Endpoint = ${PEER_IP}:51820
PersistentKeepalive = 25
EOF

    echo -e "\n${GREEN}Configuration saved. Starting WireGuard...${NC}"
    systemctl enable wg-quick@wg0
    systemctl restart wg-quick@wg0

    echo -e "${GREEN}==========================================${NC}"
    echo -e "Agent Server Tunnel configured!"
    echo -e "Internal IP: 10.8.0.2"
    echo -e "Make sure your SSH Agent service is listening on 0.0.0.0 or 10.8.0.2 to accept Panel connections."
    echo -e "${GREEN}==========================================${NC}"

else
    echo -e "${RED}Invalid selection. Exiting.${NC}"
    exit 1
fi
