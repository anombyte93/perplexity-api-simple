# Perplexity API Free - Production Directory

This is your **stable production copy** of Perplexity API Free.

## 🚀 Quick Commands

### Something Broken? Need to Recover?
```bash
./RECOVER.sh
```
This will completely rebuild and restart everything.

### Just Need to Start/Restart?
```bash
./START.sh
```
Quick start without rebuilding.

### Check Status
```bash
# Is it running?
docker ps | grep perplexity

# Check health
curl http://localhost:8765/health

# View logs
docker logs perplexity-api-server -f
```

### Stop Service
```bash
docker-compose down
```

## 📂 Directory Purpose

- **This directory** (`/home/anombyte/Projects/Programs/perplexity-api-simple/`)
  - Production/stable copy
  - What the systemd service uses
  - Auto-starts on boot
  - Your "working" copy

- **Development directory** (`/home/anombyte/Projects/projects/Deployed - Public/perplexity-api-simple/`)
  - Where you make changes
  - Where you work on updates
  - Deploy from here to production

## 🔄 Update Workflow

When you've made changes in the development directory and want to deploy them:

```bash
# From the development directory:
cd "/home/anombyte/Projects/projects/Deployed - Public/perplexity-api-simple"
./scripts/deploy-to-production.sh
```

This will:
1. Stop production container
2. Backup your settings (.env, .api_keys.json)
3. Copy new code to production
4. Restore your settings
5. Rebuild and restart
6. Update systemd service

Your settings are **always preserved** during updates!

## 🔧 Important Files

- `.env` - Your Perplexity cookies and settings (backed up during deploys)
- `.api_keys.json` - Your API keys (backed up during deploys)
- `docker-compose.yml` - Container configuration
- `RECOVER.sh` - Full recovery/rebuild script
- `START.sh` - Quick start script

## 🏥 Troubleshooting

### Service won't start
```bash
./RECOVER.sh
```

### Check what's wrong
```bash
docker logs perplexity-api-server -f
systemctl status perplexity-api
```

### Cookie expired
1. Open Chrome extension
2. Click "Sync Perplexity Cookie"
3. No restart needed!

### Complete reset
```bash
docker-compose down
docker system prune -f
./RECOVER.sh
```

## ⚙️ Systemd Service

The service auto-starts on boot:
```bash
# Check status
systemctl status perplexity-api

# Manual control
sudo systemctl start perplexity-api
sudo systemctl stop perplexity-api
sudo systemctl restart perplexity-api

# View service logs
sudo journalctl -u perplexity-api -f
```

## 📍 Access Points

- **Dashboard**: http://localhost:8765
- **API**: http://localhost:8765/chat/completions
- **Health**: http://localhost:8765/health
- **Extension**: http://localhost:8765/download/extension

## 🆘 Emergency Recovery

If absolutely everything is broken:

1. Delete this directory
2. Re-deploy from development:
   ```bash
   cd "/home/anombyte/Projects/projects/Deployed - Public/perplexity-api-simple"
   ./scripts/deploy-to-production.sh
   ```

---

**Remember**: This is production. Make changes in the development directory, then deploy here!
