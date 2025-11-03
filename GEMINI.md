## Project Overview

This project provides a simple, clean, and local drop-in replacement for the official Perplexity API. It is designed to work seamlessly with tools like TaskMaster AI and Claude Code MCP server. The system uses a personal Perplexity account cookie for authentication, enabling free searches.

The main features include:
- **OpenAI-compatible API:** Works with any OpenAI SDK.
- **Cookie-based authentication:** Uses your Perplexity account for free searches.
- **Chrome Extension:** For one-click cookie extraction and setup.
- **Web dashboard:** To manage API keys and monitor usage.
- **Hot-reload for cookies:** Update cookies without restarting the server.
- **Token tracking:** To monitor your usage.

## Architecture

The system consists of three main components:

1.  **Chrome Extension:** Extracts Perplexity cookies from the browser and sends them to the local API server.
2.  **Perplexity API Server (Flask):** An OpenAI-compatible HTTP API that manages cookies, generates API keys, and serves a web dashboard. It runs on `localhost:8765`.
3.  **MCP Server (for Claude Code):** Translates the MCP protocol and connects Claude to the API server.

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

## Building and Running

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env <<EOF
PERPLEXITY_COOKIE=your-cookie-here-optional
EOF
```

### Running the Server

```bash
# Simple start
./scripts/start_server.sh

# Or manually
export $(cat .env | xargs) && python src/perplexity_api_server.py
```

The server will start at: `http://localhost:8765`

## Usage

### Generating an API Key

1.  Open `http://localhost:8765` in your browser.
2.  Click "Generate New API Key".
3.  Copy your API key (starts with `pplx_`).

### For TaskMaster AI

Add the following to your TaskMaster configuration:

```bash
export PERPLEXITY_API_KEY="pplx_your-generated-key-here"
export PERPLEXITY_API_BASE_URL="http://localhost:8765"
```

### For Claude Code (MCP Server)

Update your MCP settings at `~/.claude/mcp_config.json` with your generated API key and the API base URL.

### For Any OpenAI-Compatible Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8765/v1",
    api_key="pplx_your-generated-key-here"
)

response = client.chat.completions.create(
    model="sonar-pro",
    messages=[
        {"role": "user", "content": "What are the latest developments in AI?"}
    ]
)

print(response.choices[0].message.content)
```

## API Endpoints

-   `GET /`: Web dashboard
-   `POST /chat/completions`: Perplexity API endpoint
-   `POST /v1/chat/completions`: OpenAI-compatible endpoint
-   `GET /models`: List available models
-   `GET /health`: Health check
-   `POST /api/save-cookie`: Save Perplexity cookie (used by extension)
-   `GET /download/extension`: Download Chrome extension as ZIP

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
│   ├── manifest.json             # Extension config
│   ├── popup.html                # Extension popup UI
│   └── scripts/
│       └── popup.js              # Cookie extraction logic
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

```bash
# Build image
docker build -t perplexity-api-simple .

# Run container
docker run -p 8765:8765 \
  -e PERPLEXITY_COOKIE="your-cookie" \
  -v $(pwd)/.api_keys.json:/app/.api_keys.json \
  perplexity-api-simple
```