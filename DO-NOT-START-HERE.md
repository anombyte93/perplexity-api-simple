# ⚠️ DO NOT START FROM THIS DIRECTORY!

## This is the DEVELOPMENT directory

**Production runs from:**
```
/home/anombyte/Projects/Programs/perplexity-api-simple/
```

## ❌ Don't Do This Here:
```bash
# DON'T run these in this directory:
docker-compose up
./START.sh
systemctl start perplexity-api
```

## ✅ Instead:

### To start/restart the service:
```bash
cd /home/anombyte/Projects/Programs/perplexity-api-simple
./START.sh
```

### Or use systemd:
```bash
sudo systemctl start perplexity-api
```

### To recover if broken:
```bash
cd /home/anombyte/Projects/Programs/perplexity-api-simple
./RECOVER.sh
```

## 🔄 What IS This Directory For?

This is where you:
- Make code changes
- Test new features
- Update documentation
- Commit to git

## 📤 Deploying Changes

When ready to deploy your changes to production:
```bash
cd "/home/anombyte/Projects/projects/Deployed - Public/perplexity-api-simple"
./scripts/deploy-to-production.sh
```

This will:
1. Stop production
2. Backup your settings
3. Copy new code to production
4. Restore settings
5. Rebuild and restart

---

**Remember:** Production = Programs directory, Development = Projects directory!
