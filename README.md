# Perplexity API Simple

A simple, clean drop-in replacement for the official Perplexity API. Perfect for using with TaskMaster AI and Claude Code MCP server.

<p align="center">
  <img width="764" height="719" alt="Cost_Savings" src="https://github.com/user-attachments/assets/fff961ba-3de0-4e1b-881e-8c76dd634204" />
</p>

## Features

- ✅ **100% Perplexity-focused** - No multi-provider complexity
- ✅ **OpenAI-compatible API** - Works with any OpenAI SDK
- ✅ **Cookie authentication** - Use your Perplexity account for free searches
- ✅ **Web dashboard** - Manage API keys and monitor usage
- ✅ **Hot-reload cookies** - Update cookies without restarting
- ✅ **Token tracking** - Monitor your usage

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

## Available Models

- `sonar` - Default Perplexity model (fast)
- `sonar-pro` - Pro model (more accurate)
- `sonar-reasoning` - Reasoning model (deep thinking)
- `sonar-deep-research` - Deep research mode

## API Endpoints

- `GET /` - Web dashboard
- `POST /chat/completions` - Perplexity API endpoint
- `POST /v1/chat/completions` - OpenAI-compatible endpoint
- `GET /models` - List available models
- `GET /health` - Health check

## Cookie Setup (Optional)

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
│   ├── perplexity_api_server.py  # Main server
│   └── perplexity_fixed.py       # Perplexity client
├── web/
│   └── index.html                # Dashboard
├── scripts/
│   └── start_server.sh           # Startup script
├── requirements.txt
├── .env.example
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

## Security

- API keys are stored locally in `.api_keys.json`
- Cookies are stored in `.env` (never committed to git)
- The server runs locally and doesn't expose your keys to the internet
- Use HTTPS in production deployments

## Contributing

This is a simplified, Perplexity-focused version. For multi-provider support, see the main [perplexity-api-free](https://github.com/yourusername/perplexity-api-free) project.

## License

MIT

<p align="center">
<img width="1715" height="492" alt="perplexity-mcp-free" src="https://github.com/user-attachments/assets/601979c0-ad67-4d92-908b-f3b770cc3842" />
<img width="468" height="746" alt="LinkedIn Visual" src="https://github.com/user-attachments/assets/3ba429f9-b196-441b-beef-598b10c81bd6" />
</p>
