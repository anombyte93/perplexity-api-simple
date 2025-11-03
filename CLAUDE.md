# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Perplexity API Simple** is a lightweight Python-based API server that provides a simple HTTP interface to Perplexity AI. It serves as a drop-in replacement for the official Perplexity API, designed specifically for integration with TaskMaster AI and Claude Code MCP servers.

## Architecture

### Core Components

1. **Flask API Server** (`src/perplexity_api_server.py`)
   - Main HTTP server providing REST endpoints
   - **Two API formats:**
     - `/search` - Native Perplexity format (RECOMMENDED)
     - `/chat/completions` - OpenAI-compatible format (for TaskMaster/MCP)
   - Handles API key management, authentication, and usage tracking
   - Cookie-based Perplexity authentication with hot-reload support
   - Web dashboard for key management and cookie configuration
   - All API keys stored in `.api_keys.json` (gitignored)
   - Cookie stored in `.env` (gitignored)

2. **Perplexity Client** (`src/perplexity_fixed.py`)
   - Wrapper around Perplexity's SSE streaming API
   - Uses `curl-cffi` to impersonate Chrome for requests
   - Handles response parsing from Perplexity's internal format
   - Supports multiple modes: 'auto', 'pro', 'reasoning', 'deep research'
   - Model mapping system to translate user-friendly model names to Perplexity's internal model IDs

3. **Web Dashboard** (`web/index.html`)
   - Single-page HTML interface for API key management
   - Cookie configuration with hot-reload capability
   - Usage statistics and monitoring

### Key Design Patterns

- **Dual API Format**:
  - Native `/search` endpoint: Direct Perplexity format (query, mode, sources)
  - Compatible `/chat/completions`: OpenAI-like format for existing integrations
- **Mode-to-Model Mapping**: `/chat/completions` maps model names like `sonar-pro` to Perplexity modes
- **Hot Cookie Reload**: Cookie updates via web dashboard don't require server restart (recreates client instance)
- **SSE Response Parsing**: Perplexity uses Server-Sent Events with nested JSON structures in 'FINAL' steps
- **Plain Text Responses**: Both endpoints return raw Perplexity text (not JSON-wrapped)

## Development Commands

### Starting the Server

```bash
# Recommended: Use startup script
./scripts/start_server.sh

# Manual start (loads .env automatically)
export $(cat .env | xargs) && python src/perplexity_api_server.py

# With debug mode
FLASK_DEBUG=1 python src/perplexity_api_server.py

# Custom port
PORT=9000 python src/perplexity_api_server.py
```

### Testing

```bash
# Quick health check
curl http://localhost:8765/health

# Test native Perplexity endpoint (RECOMMENDED)
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "mode": "auto"}'

# Test with specific mode and model
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain quantum computing", "mode": "pro", "model": "gpt-4o"}'

# Test OpenAI-compatible endpoint (for backward compatibility)
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer pplx_your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar", "messages": [{"role": "user", "content": "What is Python?"}]}'
```

### Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Core runtime dependencies only
pip install curl-cffi websocket-client flask flask-cors
```

### Docker

```bash
# Build image
docker build -t perplexity-api-simple .

# Run container (with persistent API keys)
docker run -p 8765:8765 \
  -e PERPLEXITY_COOKIE="your-cookie" \
  -v $(pwd)/.api_keys.json:/app/.api_keys.json \
  perplexity-api-simple
```

## Important Implementation Details

### API Endpoints

**Native Perplexity Format** (`/search`) - RECOMMENDED
```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_key" \
  -d '{
    "query": "What is Python?",
    "mode": "auto",              # auto, pro, reasoning, deep research
    "model": "gpt-4o",           # Optional: specific model within mode
    "sources": ["web"],          # Optional: web, scholar, social
    "json_mode": false           # Optional: extract JSON from conversational responses
  }'
```

**JSON Extraction Mode** (for TaskMaster AI and strict JSON requirements)
```bash
# When asking Perplexity to generate JSON, it often adds conversational text.
# Use json_mode=true to automatically extract clean JSON from the response.

curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_key" \
  -d '{
    "query": "Generate a task in JSON format with fields: title, description, details",
    "mode": "pro",
    "json_mode": true            # Automatically extracts JSON from conversational text
  }'

# Response will be clean JSON only, no extra text:
# {"title": "...", "description": "...", "details": "..."}
```

**OpenAI-Compatible Format** (`/chat/completions`) - For TaskMaster/MCP
```bash
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer pplx_key" \
  -d '{
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "What is Python?"}],
    "json_mode": false           # Optional: extract JSON from conversational responses
  }'
```

### Model Name Translation (OpenAI-Compatible Endpoint Only)

When using `/chat/completions`, model names are mapped to Perplexity modes:
- `sonar` → `auto` mode → `turbo` model
- `sonar-pro` → `pro` mode → `pplx_pro` model
- `sonar-reasoning` → `reasoning` mode → `pplx_reasoning` model
- `sonar-deep-research` → `deep research` mode → `pplx_alpha` model

Native `/search` endpoint uses modes directly (no translation needed).

See `perplexity_fixed.py:47-69` for complete mapping.

### Response Parsing

Perplexity's SSE format requires special handling:
1. Stream contains multiple `event: message` chunks
2. Final answer is in `event: end_of_stream` chunk
3. Answer text is in `steps[].content.answer` where `step_type == 'FINAL'`
4. The `answer` field itself is JSON-encoded and must be parsed twice

See `perplexity_fixed.py:165-184` for extraction logic.

### API Key Management

- Keys are stored as dictionary in `.api_keys.json`: `{api_key: {name, created, last_used, usage_count, active}}`
- Keys are validated on every request via `validate_api_key()` function
- Token tracking uses rough approximation: 1 word ≈ 1.3 tokens
- Web dashboard requires valid API key to update cookies (security measure)

### Cookie Hot-Reload

The `/api/save-cookie` endpoint allows updating cookies without restart:
1. Validates API key
2. Saves to `.env` file
3. Recreates global `client` instance with new cookies
4. Returns `requires_restart: false` to frontend

See `perplexity_api_server.py:451-497`.

## Configuration

### Environment Variables

```bash
# .env file format
PERPLEXITY_COOKIE=<full-cookie-string-from-browser>
PORT=8765  # Optional, defaults to 8765
```

### Getting Perplexity Cookie

1. Login to https://www.perplexity.ai
2. Open DevTools (F12) → Application/Storage → Cookies
3. Copy entire cookie string (all cookie fields semicolon-separated)
4. Either add to `.env` or use web dashboard at http://localhost:8765

## Common Integration Patterns

### TaskMaster AI

TaskMaster requires strict JSON responses. This proxy server supports `json_mode` to automatically extract clean JSON from Perplexity's conversational responses.

**Setup:**
```bash
export PERPLEXITY_API_KEY="pplx_<generated-key>"
export PERPLEXITY_API_BASE_URL="http://localhost:8765"
```

**Usage:**
```bash
# For research-backed task generation
tm add-task --prompt "Create authentication system" --research

# For PRD parsing with research
tm parse-prd --research

# For task expansion with research
tm expand-task 5 --research
```

**Note:** TaskMaster automatically sends `json_mode: true` when it expects JSON responses. The proxy server will extract clean JSON from Perplexity's conversational output, fixing the common issue where Perplexity adds explanatory text before/after JSON.

### Claude Code MCP Server

Update `~/.claude/mcp_config.json`:
```json
{
  "mcpServers": {
    "perplexity-free": {
      "command": "node",
      "args": ["/path/to/mcp-server/build/index.js"],
      "env": {
        "PERPLEXITY_API_KEY": "pplx_<generated-key>",
        "PERPLEXITY_API_BASE_URL": "http://localhost:8765"
      }
    }
  }
}
```


## WSL Specifics

- Server binds to `0.0.0.0` by default (accessible from Windows host)
- Access from Windows: `http://<wsl-ip>:8765` (get IP via `ip addr show eth0 | grep inet`)
- Port 8765 should be accessible without additional firewall configuration

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process on port 8765
lsof -i :8765
kill -9 $(lsof -t -i :8765)
```

### Dependencies Missing
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# Check Flask specifically
python3 -c "import flask; print(flask.__version__)"
```

### Cookie Authentication Failing
- Ensure cookie string includes all fields (not just one field)
- Try hot-reloading via web dashboard instead of manual .env edit
- Verify you're logged into Perplexity.ai in the same browser
- Cookie may expire; regenerate from browser DevTools

### JSON Extraction Issues (TaskMaster AI)
If TaskMaster is receiving "Invalid JSON response" errors:

1. **Enable json_mode explicitly**: Ensure your integration sends `"json_mode": true` in the request body
2. **Check server logs**: The server logs show `🔧 JSON extraction applied` when extraction runs
3. **Test with curl**: Verify JSON extraction works with a direct curl request:
   ```bash
   curl -X POST http://localhost:8765/search \
     -H "Authorization: Bearer pplx_your-key" \
     -H "Content-Type: application/json" \
     -d '{"query": "Generate JSON with title and description fields", "mode": "pro", "json_mode": true}'
   ```
4. **Verify response**: The response should be pure JSON with no conversational text
5. **Check Perplexity prompt**: If Perplexity's AI isn't generating JSON at all, adjust your prompt to be more explicit about JSON format requirements

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
