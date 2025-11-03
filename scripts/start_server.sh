#!/bin/bash
# Start Perplexity API Server
# Simple startup script that loads .env and starts the server

set -e

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🚀 Starting Perplexity API Server..."
echo "="*80

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env <<EOF
# Perplexity Cookie (optional - for authenticated searches)
# Get this from https://www.perplexity.ai (DevTools → Application → Cookies)
PERPLEXITY_COOKIE=

# Server port (default: 8765)
PORT=8765
EOF
    echo "✅ Created .env template"
    echo "💡 Edit .env to add your Perplexity cookie (optional)"
fi

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✅ Loaded environment from .env"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip install -r requirements.txt
fi

# Start the server
echo ""
echo "Starting server on port ${PORT:-8765}..."
echo ""

exec python3 src/perplexity_api_server.py
