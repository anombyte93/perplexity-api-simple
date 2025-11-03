# 🚀 Perplexity API Free - Quick Start Guide

## Fresh Installation (Clone from GitHub)

### Prerequisites

- Docker & Docker Compose installed
- Linux/macOS/WSL2 (Windows)
- 5 minutes

### One-Command Install

```bash
git clone https://github.com/anombyte93/perplexity-api-simple.git
cd perplexity-api-simple
./INSTALL.sh
```

That's it! The installer will:
- ✅ Set up production directory
- ✅ Configure systemd for auto-start
- ✅ Build Docker image
- ✅ Start the service
- ✅ Enable boot auto-start

### Manual Installation (If You Prefer)

#### Step 1: Clone Repository
```bash
git clone https://github.com/anombyte93/perplexity-api-simple.git
cd perplexity-api-simple
```

#### Step 2: Configure Environment
```bash
cp .env.example .env
nano .env  # Add your PERPLEXITY_COOKIE
```

#### Step 3: Start with Docker
```bash
docker-compose up -d
```

#### Step 4: Generate API Key
Visit `http://localhost:8765` and click "Generate New API Key"

---

## Getting Perplexity Cookie

### Option 1: Chrome Extension (Easiest)
1. Start the server: `docker-compose up -d`
2. Download extension: `http://localhost:8765/download/extension`
3. Install in Chrome: `chrome://extensions/` → Load unpacked
4. Click extension icon → "Sync Perplexity Cookie"

### Option 2: Manual (DevTools)
1. Login to https://www.perplexity.ai
2. Press F12 (DevTools)
3. Application → Cookies → https://www.perplexity.ai
4. Copy all cookies (semicolon-separated)
5. Paste in `.env` file

---

## Verification

```bash
# Check if running
curl http://localhost:8765/health

# View dashboard
open http://localhost:8765

# Test API
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "sonar", "messages": [{"role": "user", "content": "Hello"}]}'
```

---

## Production Setup (Recommended)

For a stable production install that survives updates:

```bash
./INSTALL.sh
```

This installs to `~/Projects/Programs/perplexity-api-simple/` with:
- ✅ Systemd service (auto-start on boot)
- ✅ Recovery scripts (`./RECOVER.sh`)
- ✅ Easy restart (`./START.sh`)
- ✅ Safe update workflow

Production location: `~/Projects/Programs/perplexity-api-simple/`

---

## Using with Claude Code

### TaskMaster AI Integration

The API is configured to work with TaskMaster AI globally. TaskMaster will automatically use your Perplexity API for research features.

**Restart Claude Code** after installation to load the configuration.

### Direct API Usage

You can also use the API directly in any project:

```javascript
const response = await fetch('http://localhost:8765/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'sonar-pro',
    messages: [{role: 'user', content: 'Your query'}]
  })
});
```

---

## Management Commands

### If Using Production Install

```bash
cd ~/Projects/Programs/perplexity-api-simple

./START.sh       # Quick start/restart
./RECOVER.sh     # Full recovery if broken

# Or use systemd:
sudo systemctl start perplexity-api
sudo systemctl stop perplexity-api
sudo systemctl status perplexity-api
```

### If Using Docker Directly

```bash
cd perplexity-api-simple

docker-compose up -d       # Start
docker-compose down        # Stop
docker-compose restart     # Restart
docker-compose logs -f     # View logs
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs perplexity-api-server
sudo journalctl -u perplexity-api -f

# Full recovery
cd ~/Projects/Programs/perplexity-api-simple
./RECOVER.sh
```

### Cookie Expired

Use the Chrome extension:
1. Click extension icon
2. "Sync Perplexity Cookie"
3. Done! (no restart needed)

### Port Already in Use

```bash
# Find what's using port 8765
sudo lsof -i :8765

# Change port in .env
PORT=9000
```

---

## What Gets Installed

### Files & Directories
```
~/Projects/Programs/perplexity-api-simple/  (Production)
├── .env                    # Your config (NOT in git)
├── .api_keys.json          # Your keys (NOT in git)
├── START.sh                # Quick start script
├── RECOVER.sh              # Recovery script
├── docker-compose.yml      # Docker config
├── Dockerfile              # Image definition
├── src/                    # Python source
├── web/                    # Dashboard UI
└── extension/              # Chrome extension

~/.claude/mcp_config.json   # Global MCP config
/etc/systemd/system/perplexity-api.service  # System service
```

### What's Protected (Never Pushed to Git)
- `.env` - Contains your Perplexity cookie
- `.api_keys.json` - Contains your API keys

### What's Safe to Push
- All code
- Documentation
- Docker configs
- Scripts

---

## Next Steps

1. **Configure Cookie**: Use Chrome extension or manual method
2. **Generate API Keys**: Visit http://localhost:8765
3. **Test API**: Try a sample request
4. **Integrate**: Use with Claude Code, TaskMaster, or custom apps

---

## Support

- **GitHub Issues**: https://github.com/anombyte93/perplexity-api-simple/issues
- **Documentation**: See `README.md` and `DOCKER.md`
- **Production Guide**: See `SETUP-COMPLETE.md` (after install)

---

**Ready to start!** Run `./INSTALL.sh` for automatic setup or `docker-compose up -d` for quick start.
