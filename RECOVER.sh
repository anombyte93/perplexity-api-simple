#!/bin/bash

##############################################################################
# Perplexity API Free - Recovery Script
#
# Run this if the service is broken or not working.
# This will rebuild and restart everything from scratch.
#
# Usage: ./RECOVER.sh
##############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Perplexity API - Recovery Mode${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

cd "$SCRIPT_DIR"

# Step 1: Stop everything
echo -e "${YELLOW}[1/6]${NC} Stopping all containers..."
docker-compose down 2>/dev/null || true
sleep 2

# Step 2: Clean up Docker
echo -e "${YELLOW}[2/6]${NC} Cleaning up Docker resources..."
docker system prune -f 2>/dev/null || true

# Step 3: Verify settings exist
echo -e "${YELLOW}[3/6]${NC} Checking configuration files..."
if [ ! -f ".env" ]; then
    echo -e "${RED}✗ Missing .env file!${NC}"
    echo -e "${YELLOW}  Creating from example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}  ⚠ IMPORTANT: Edit .env and add your PERPLEXITY_COOKIE${NC}"
    else
        echo -e "${RED}✗ No .env.example found!${NC}"
        exit 1
    fi
fi

if [ ! -f ".api_keys.json" ]; then
    echo -e "${YELLOW}  Creating empty API keys file...${NC}"
    echo '{"keys":{}}' > .api_keys.json
fi

# Step 4: Rebuild image
echo -e "${YELLOW}[4/6]${NC} Rebuilding Docker image..."
docker-compose build --no-cache

# Step 5: Start service
echo -e "${YELLOW}[5/6]${NC} Starting service..."
docker-compose up -d

# Step 6: Wait and verify
echo -e "${YELLOW}[6/6]${NC} Waiting for service to be healthy..."
sleep 10

if curl -sf http://localhost:8765/health > /dev/null 2>&1; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  ✓ Recovery Complete!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}Service:${NC}  http://localhost:8765"
    echo -e "${BLUE}Status:${NC}   docker ps | grep perplexity"
    echo -e "${BLUE}Logs:${NC}     docker logs perplexity-api-server -f"
    echo ""
    echo -e "${GREEN}The service is now running!${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}  ✗ Service Not Responding${NC}"
    echo -e "${RED}================================================${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. Check logs: ${BLUE}docker logs perplexity-api-server${NC}"
    echo -e "  2. Check .env file has PERPLEXITY_COOKIE set"
    echo -e "  3. Verify Docker is running: ${BLUE}systemctl status docker${NC}"
    echo ""
    echo -e "${YELLOW}For manual intervention:${NC}"
    echo -e "  - View logs: ${BLUE}docker logs perplexity-api-server -f${NC}"
    echo -e "  - Restart: ${BLUE}docker-compose restart${NC}"
    echo -e "  - Stop: ${BLUE}docker-compose down${NC}"
    echo ""
    exit 1
fi
