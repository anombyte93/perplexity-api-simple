#!/bin/bash

##############################################################################
# Perplexity API Free - Deploy to Production
#
# This script deploys the current project to /home/anombyte/Projects/Programs/
# as a stable production copy.
#
# Usage: ./scripts/deploy-to-production.sh
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
DEV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROD_DIR="/home/anombyte/Projects/Programs/perplexity-api-simple"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Perplexity API - Deploy to Production${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Development:${NC} $DEV_DIR"
echo -e "${YELLOW}Production:${NC}  $PROD_DIR"
echo ""

# Create Programs directory if needed
mkdir -p "/home/anombyte/Projects/Programs"

# Stop existing production container if running
echo -e "${BLUE}→${NC} Stopping production container (if running)..."
if [ -d "$PROD_DIR" ]; then
    cd "$PROD_DIR" && docker-compose down 2>/dev/null || true
fi

# Backup production settings if they exist
if [ -f "$PROD_DIR/.env" ]; then
    echo -e "${BLUE}→${NC} Backing up production settings..."
    cp "$PROD_DIR/.env" "/tmp/.env.backup"
    cp "$PROD_DIR/.api_keys.json" "/tmp/.api_keys.backup" 2>/dev/null || true
fi

# Copy project to production
echo -e "${BLUE}→${NC} Deploying code to production..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.api_keys.json' \
    --exclude='node_modules' \
    --exclude='.taskmaster' \
    "$DEV_DIR/" "$PROD_DIR/"

# Restore or copy settings
if [ -f "/tmp/.env.backup" ]; then
    echo -e "${BLUE}→${NC} Restoring production settings..."
    cp "/tmp/.env.backup" "$PROD_DIR/.env"
    [ -f "/tmp/.api_keys.backup" ] && cp "/tmp/.api_keys.backup" "$PROD_DIR/.api_keys.json"
    rm -f "/tmp/.env.backup" "/tmp/.api_keys.backup"
else
    echo -e "${YELLOW}⚠${NC}  No existing settings found, copying from dev..."
    [ -f "$DEV_DIR/.env" ] && cp "$DEV_DIR/.env" "$PROD_DIR/.env"
    [ -f "$DEV_DIR/.api_keys.json" ] && cp "$DEV_DIR/.api_keys.json" "$PROD_DIR/.api_keys.json"
fi

# Make scripts executable
chmod +x "$PROD_DIR/scripts/"*.sh 2>/dev/null || true

# Update systemd service
echo -e "${BLUE}→${NC} Updating systemd service..."
cat > /tmp/perplexity-api.service <<EOF
[Unit]
Description=Perplexity API Free - Production
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROD_DIR
ExecStartPre=/usr/bin/docker-compose down
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/perplexity-api.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start service
echo -e "${BLUE}→${NC} Starting production service..."
sudo systemctl enable perplexity-api.service
sudo systemctl restart perplexity-api.service

# Wait for health check
echo -e "${BLUE}→${NC} Waiting for service to be healthy..."
sleep 8

if curl -sf http://localhost:8765/health > /dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo -e "${GREEN}✓ Service is healthy and running${NC}"
    echo ""
    echo -e "${BLUE}Production:${NC} http://localhost:8765"
    echo -e "${BLUE}Status:${NC}     systemctl status perplexity-api"
    echo -e "${BLUE}Logs:${NC}       sudo journalctl -u perplexity-api -f"
    echo -e "${BLUE}Recovery:${NC}   cd $PROD_DIR && ./RECOVER.sh"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Service may not be healthy yet${NC}"
    echo -e "${YELLOW}  Check status: systemctl status perplexity-api${NC}"
    echo -e "${YELLOW}  Check logs: sudo journalctl -u perplexity-api -f${NC}"
    exit 1
fi
