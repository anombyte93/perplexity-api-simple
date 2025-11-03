# Perplexity API Simple

A simple, clean drop-in replacement for the official Perplexity API. Perfect for using with TaskMaster AI and Claude Code MCP server.

## Features

- ✅ **100% Perplexity-focused** - No multi-provider complexity
- ✅ **Simple HTTP API** - Easy integration with TaskMaster and Claude Code
- ✅ **Cookie authentication** - Use your Perplexity account for free searches
- ✅ **Chrome Extension** - One-click cookie extraction and MCP setup
- ✅ **Web dashboard** - Manage API keys and monitor usage
- ✅ **Hot-reload cookies** - Update cookies without restarting
- ✅ **Token tracking** - Monitor your usage

## Architecture Overview

This system has **three main components** working together:

```
┌─────────────────────────────────────┐
│   Chrome Extension                  │
│   - Extracts Perplexity cookies     │
│   - Auto-configures MCP             │
│   - One-click setup                 │
└──────────────┬──────────────────────┘
               │ Sends cookies via HTTP
               ▼
┌─────────────────────────────────────┐
│   Perplexity API Server (Flask)     │
│   - OpenAI-compatible HTTP API      │
│   - Cookie management               │
│   - API key generation              │
│   - Web dashboard                   │
│   Port: localhost:8765              │
└──────────────┬──────────────────────┘
               │ HTTP requests
               ▼
┌─────────────────────────────────────┐
│   MCP Server (for Claude Code)      │
│   - Translates MCP protocol         │
│   - Connects Claude to API server   │
│   Location: perplexity-api-free     │
└─────────────────────────────────────┘
```

**How it works:**
1. **Chrome Extension** extracts your Perplexity cookies automatically
2. **API Server** uses cookies to make authenticated Perplexity requests
3. **MCP Server** connects Claude Code to the API server
4. **Claude Code** can now search using your Perplexity account!

## Quick Start

### 1. Installation

```bash
cd /home/anombyte/projects/perplexity-api-simple

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env <<EOF
PERPLEXITY_COOKIE=your-cookie-here-optional
EOF
```

### 2. Start the Server

```bash
# Simple start
./scripts/start_server.sh

# Or manually
export $(cat .env | xargs) && python src/perplexity_api_server.py
```

The server will start at: `http://localhost:8765`

### 3. Generate API Key

1. Open `http://localhost:8765` in your browser
2. Click "Generate New API Key"
3. Copy your API key (starts with `pplx_`)

## Usage

### For TaskMaster AI

Add to your TaskMaster configuration:

```bash
# In your .env or shell profile
export PERPLEXITY_API_KEY="pplx_your-generated-key-here"
export PERPLEXITY_API_BASE_URL="http://localhost:8765"
```

Then use TaskMaster normally with the `--research` flag:

```bash
tm parse-prd --research
tm expand-all --research
```

### For Claude Code (MCP Server)

1. **Generate API Key** from the web dashboard at `http://localhost:8765`

2. **Update your MCP settings** at `~/.claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "perplexity-free": {
      "command": "node",
      "args": [
        "/path/to/perplexity-api-free/mcp-server/build/index.js"
      ],
      "env": {
        "PERPLEXITY_API_KEY": "pplx_your-generated-key-here",
        "PERPLEXITY_API_BASE_URL": "http://localhost:8765"
      }
    }
  }
}
```

3. **Restart Claude Code**

4. **Test the connection**:
   - Ask Claude: "Use Perplexity to search for the latest Python best practices"
   - Claude should use the MCP tool automatically


## Available Models

- `sonar` - Default Perplexity model (fast)
- `sonar-pro` - Pro model (more accurate)
- `sonar-reasoning` - Reasoning model (deep thinking)
- `sonar-deep-research` - Deep research mode

## API Endpoints

- `GET /` - Web dashboard
- `POST /chat/completions` - Chat completions endpoint (returns plain text)
- `GET /models` - List available models
- `GET /health` - Health check
- `POST /api/save-cookie` - Save Perplexity cookie (used by extension)
- `GET /download/extension` - Download Chrome extension as ZIP

## Chrome Extension (Recommended)

The **easiest way** to set up cookies and MCP configuration!

### Installation

**Option 1: Download from Dashboard (Easiest)**
1. Open `http://localhost:8765` in Chrome
2. Scroll to "Chrome Extension" section
3. Click "📦 Download Chrome Extension"
4. Extract the downloaded ZIP file
5. Open Chrome → `chrome://extensions/`
6. Enable "Developer mode" (top-right toggle)
7. Click "Load unpacked"
8. Select the extracted `extension/` folder

**Option 2: Use Extension from Project**
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `/home/anombyte/projects/perplexity-api-simple/extension/`

### Usage

1. **Login to Perplexity** at https://www.perplexity.ai
2. **Click the extension icon** in Chrome
3. **Enter your API key** (from dashboard at localhost:8765)
4. **Click "🔮 Sync Perplexity Cookie"**
5. **Done!** Extension automatically:
   - Extracts all Perplexity cookies from your browser
   - Sends them securely to your local server
   - Server hot-reloads with new cookies (no restart needed!)

### What the Extension Does

The Chrome extension has permission to access cookies from `perplexity.ai` and uses the Chrome Cookies API to:

```javascript
// From extension/scripts/popup.js
const cookies = await chrome.cookies.getAll({
  domain: 'perplexity.ai'
});

const cookieString = cookies
  .map(cookie => `${cookie.name}=${cookie.value}`)
  .join('; ');

// Send to local server
await fetch('http://localhost:8765/api/save-cookie', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${apiKey}`
  },
  body: JSON.stringify({ cookie: cookieString })
});
```

**Security:**
- Extension only accesses `localhost:8765` (your local server)
- Cookies never leave your machine
- Requires your API key for authentication
- All communication is local (not sent to internet)

### Features

- ✅ One-click cookie sync
- ✅ Auto-detects when you're logged in
- ✅ Hot-reload support (no server restart)
- ✅ Also supports ChatGPT cookies
- ✅ MCP configuration generator (coming soon)

## Manual Cookie Setup (Without Extension)

To use your Perplexity account for authenticated searches:

### Getting Your Cookie

1. **Login to Perplexity** at `https://www.perplexity.ai`
2. **Open DevTools** (F12)
3. **Go to Application/Storage → Cookies**
4. **Copy the entire cookie string**

### Option 1: Via Web Dashboard

1. Open `http://localhost:8765`
2. Click "Cookie Settings"
3. Paste your cookie
4. Click "Save" (hot-reloads without restart!)

### Option 2: Via .env File

```bash
# Edit .env file
PERPLEXITY_COOKIE=your-full-cookie-string-here
```

Then restart the server.

## Troubleshooting

### Server Won't Start

```bash
# Check if port 8765 is already in use
lsof -i :8765

# Kill existing process
kill -9 $(lsof -t -i :8765)

# Try again
./scripts/start_server.sh
```

### API Key Not Working

1. Open `http://localhost:8765`
2. Check if your key is active in the dashboard
3. Regenerate a new key if needed

### Cookie Not Working

1. Make sure you're logged into Perplexity.ai
2. Copy the ENTIRE cookie string (not just one field)
3. Try refreshing your Perplexity session
4. Use the web dashboard to update the cookie (hot-reload)

### WSL-Specific Issues

If running in WSL and can't access from Windows:

```bash
# Make sure you're using 0.0.0.0 (not 127.0.0.1)
# Server already binds to 0.0.0.0 by default

# Access from Windows using WSL IP
ip addr show eth0 | grep inet
# Use: http://<wsl-ip>:8765
```

## Development

### Project Structure

```
perplexity-api-simple/
├── src/
│   ├── perplexity_api_server.py  # Main Flask API server
│   └── perplexity_fixed.py       # Perplexity client wrapper
├── web/
│   └── index.html                # Web dashboard (API key management)
├── extension/                    # Chrome extension
│   ├── manifest.json             # Extension config (v1.3.0)
│   ├── popup.html                # Extension popup UI
│   ├── instructions.html         # Setup instructions
│   ├── scripts/
│   │   ├── popup.js              # Cookie extraction logic
│   │   └── background.js         # Background service worker
│   └── icons/                    # Extension icons
├── scripts/
│   └── start_server.sh           # Server startup script
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (gitignored)
├── .api_keys.json                # API keys storage (gitignored)
└── README.md
```

### Running in Development

```bash
# With auto-reload
FLASK_DEBUG=1 python src/perplexity_api_server.py

# With custom port
PORT=9000 python src/perplexity_api_server.py
```

## Docker Support

The easiest way to run this server is with Docker:

```bash
# Quick Start
cp .env.example .env        # Configure your Perplexity cookie
docker-compose up -d        # Start the server
```

Access the dashboard at `http://localhost:8765`

### Full Docker Documentation

For detailed Docker instructions including:
- AWS EC2 deployment
- AWS ECS/Fargate deployment
- Development mode setup
- Monitoring and troubleshooting
- Production best practices

See **[DOCKER.md](DOCKER.md)** for the complete guide.

## Security

- API keys are stored locally in `.api_keys.json`
- Cookies are stored in `.env` (never committed to git)
- The server runs locally and doesn't expose your keys to the internet
- Use HTTPS in production deployments

## Contributing

This is a simplified, Perplexity-focused version. For multi-provider support, see the main [perplexity-api-free](https://github.com/yourusername/perplexity-api-free) project.

## License

MIT

## Credits

Based on the [perplexity-api-free](https://github.com/yourusername/perplexity-api-free) project, simplified for ease of use with TaskMaster and Claude Code.
