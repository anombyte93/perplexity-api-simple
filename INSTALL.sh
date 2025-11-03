#!/bin/bash

##############################################################################
# Perplexity API Free - Automated Installation
#
# This script sets up Perplexity API Free in production mode.
# Run this after cloning the repository.
#
# Usage: ./INSTALL.sh
##############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default production directory
DEFAULT_PROD_DIR="$HOME/Projects/Programs/perplexity-api-simple"

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║        Perplexity API Free - Installation Script          ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running from git repo
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}✗ Error: docker-compose.yml not found${NC}"
    echo -e "${YELLOW}  Please run this script from the repository root${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Check prerequisites
echo -e "${BLUE}[1/8]${NC} Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not installed${NC}"
    echo -e "${YELLOW}  Install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not installed${NC}"
    echo -e "${YELLOW}  Install Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"

# Step 2: Configure installation
echo -e "\n${BLUE}[2/8]${NC} Configuration"
echo -e "${YELLOW}Where should the production installation be located?${NC}"
echo -e "${CYAN}Default: ${DEFAULT_PROD_DIR}${NC}"
read -p "Press Enter to use default, or type a custom path: " CUSTOM_PROD_DIR

PROD_DIR="${CUSTOM_PROD_DIR:-$DEFAULT_PROD_DIR}"

echo -e "${GREEN}✓ Production directory: ${PROD_DIR}${NC}"

# Step 3: Set up .env file
echo -e "\n${BLUE}[3/8]${NC} Setting up configuration..."

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"

    echo -e "\n${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  IMPORTANT: Configure Your Perplexity Cookie      ${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e ""
    echo -e "To get your Perplexity cookie:"
    echo -e "  1. Login to ${CYAN}https://www.perplexity.ai${NC}"
    echo -e "  2. Open DevTools (F12)"
    echo -e "  3. Go to Application → Cookies → https://www.perplexity.ai"
    echo -e "  4. Copy all cookies (semicolon-separated)"
    echo -e ""
    echo -e "${YELLOW}Or use the Chrome extension later for easy cookie sync!${NC}"
    echo -e ""
    read -p "Press Enter when ready to continue..."
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create empty API keys file if needed
if [ ! -f ".api_keys.json" ]; then
    echo '{}' > .api_keys.json
    echo -e "${GREEN}✓ Created empty .api_keys.json${NC}"
fi

# Step 4: Deploy to production
echo -e "\n${BLUE}[4/8]${NC} Deploying to production directory..."

# Create production directory
mkdir -p "$(dirname "$PROD_DIR")"

if [ -d "$PROD_DIR" ]; then
    echo -e "${YELLOW}⚠ Production directory exists. Creating backup...${NC}"
    if [ -f "$PROD_DIR/.env" ]; then
        cp "$PROD_DIR/.env" "/tmp/.env.backup"
    fi
    if [ -f "$PROD_DIR/.api_keys.json" ]; then
        cp "$PROD_DIR/.api_keys.json" "/tmp/.api_keys.backup"
    fi
fi

# Copy to production
rsync -av --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.api_keys.json' \
    --exclude='node_modules' \
    --exclude='.taskmaster' \
    "$SCRIPT_DIR/" "$PROD_DIR/"

# Restore or copy settings
if [ -f "/tmp/.env.backup" ]; then
    cp "/tmp/.env.backup" "$PROD_DIR/.env"
    [ -f "/tmp/.api_keys.backup" ] && cp "/tmp/.api_keys.backup" "$PROD_DIR/.api_keys.json"
    rm -f "/tmp/.env.backup" "/tmp/.api_keys.backup"
    echo -e "${GREEN}✓ Restored existing settings${NC}"
else
    cp .env "$PROD_DIR/.env"
    [ -f ".api_keys.json" ] && cp .api_keys.json "$PROD_DIR/.api_keys.json"
    echo -e "${GREEN}✓ Copied configuration files${NC}"
fi

chmod +x "$PROD_DIR/scripts/"*.sh "$PROD_DIR/"*.sh 2>/dev/null || true

# Step 5: Set up systemd service
echo -e "\n${BLUE}[5/8]${NC} Setting up systemd service..."

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
echo -e "${GREEN}✓ Systemd service created${NC}"

# Step 6: Build Docker image
echo -e "\n${BLUE}[6/8]${NC} Building Docker image..."
cd "$PROD_DIR"
docker-compose build --quiet
echo -e "${GREEN}✓ Docker image built${NC}"

# Step 7: Start service
echo -e "\n${BLUE}[7/8]${NC} Starting service..."
sudo systemctl enable perplexity-api.service
sudo systemctl start perplexity-api.service
sleep 8

# Step 8: Verify installation
echo -e "\n${BLUE}[8/8]${NC} Verifying installation..."

if curl -sf http://localhost:8765/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Service is healthy and running!${NC}"
    INSTALL_SUCCESS=true
else
    echo -e "${YELLOW}⚠ Service may still be starting...${NC}"
    INSTALL_SUCCESS=false
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}║              Installation Complete!                        ║${NC}"
echo -e "${CYAN}║                                                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}Production Location:${NC}  $PROD_DIR"
echo -e "${GREEN}Web Dashboard:${NC}       http://localhost:8765"
echo -e "${GREEN}Service Status:${NC}      systemctl status perplexity-api"
echo ""

echo -e "${BLUE}═══ Next Steps ═══${NC}"
echo ""
echo -e "1. ${YELLOW}Configure Perplexity Cookie:${NC}"
echo -e "   Edit: ${CYAN}$PROD_DIR/.env${NC}"
echo -e "   Or use Chrome extension at: ${CYAN}http://localhost:8765/download/extension${NC}"
echo ""
echo -e "2. ${YELLOW}Generate API Keys:${NC}"
echo -e "   Visit: ${CYAN}http://localhost:8765${NC}"
echo -e "   Click 'Generate New API Key'"
echo ""
echo -e "3. ${YELLOW}Management Commands:${NC}"
echo -e "   ${CYAN}cd $PROD_DIR${NC}"
echo -e "   ${CYAN}./START.sh${NC}      - Start/restart service"
echo -e "   ${CYAN}./RECOVER.sh${NC}    - Full recovery if broken"
echo ""
echo -e "4. ${YELLOW}Systemd Commands:${NC}"
echo -e "   ${CYAN}sudo systemctl start perplexity-api${NC}   - Start"
echo -e "   ${CYAN}sudo systemctl stop perplexity-api${NC}    - Stop"
echo -e "   ${CYAN}sudo systemctl status perplexity-api${NC}  - Status"
echo ""

if [ "$INSTALL_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ Everything is ready to use!${NC}"
else
    echo -e "${YELLOW}⚠ Check service status:${NC} ${CYAN}systemctl status perplexity-api${NC}"
    echo -e "${YELLOW}  View logs:${NC} ${CYAN}sudo journalctl -u perplexity-api -f${NC}"
fi

echo ""
echo -e "${CYAN}Documentation:${NC} $PROD_DIR/SETUP-COMPLETE.md"
echo ""

# Check if Chrome extension was requested
if [ "$INSTALL_SUCCESS" = true ]; then
    echo -e "${BLUE}Would you like to download the Chrome extension now? (y/n)${NC}"
    read -p "> " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -s -o ~/Downloads/perplexity-extension.zip http://localhost:8765/download/extension
        echo -e "${GREEN}✓ Downloaded to: ~/Downloads/perplexity-extension.zip${NC}"
        echo -e "${YELLOW}  Install: chrome://extensions/ → Load unpacked${NC}"
    fi
fi

echo ""
echo -e "${CYAN}═════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Installation completed successfully!${NC} 🚀"
echo -e "${CYAN}═════════════════════════════════════════════════${NC}"
