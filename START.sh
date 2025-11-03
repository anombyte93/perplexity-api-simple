#!/bin/bash

##############################################################################
# Perplexity API Free - Quick Start
#
# Simple script to start/restart the service
#
# Usage: ./START.sh
##############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Perplexity API...${NC}"

# Start containers
docker-compose up -d

echo ""
echo -e "${GREEN}✓ Service started!${NC}"
echo -e "${BLUE}URL:${NC} http://localhost:8765"
echo ""
echo "Check status: docker ps | grep perplexity"
echo "View logs:    docker logs perplexity-api-server -f"
echo ""
