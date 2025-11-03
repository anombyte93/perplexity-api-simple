# Perplexity API Free - Chrome Extension

**One-click MCP setup for Claude Code**

This Chrome extension makes it incredibly easy to set up Perplexity AI in Claude Code. Just paste your API key and the extension handles everything!

---

## 🎯 What It Does

1. **Validates your API key** - Tests connection to the server
2. **Generates MCP config** - Creates the perfect configuration
3. **Copies to clipboard** - Ready to paste into Claude Code
4. **Provides instructions** - Step-by-step guide to finish setup

---

## 📦 Installation

### From Chrome Web Store (Coming Soon)
1. Visit the Chrome Web Store
2. Search for "Perplexity API Free"
3. Click "Add to Chrome"

### Manual Installation (For Development)
1. Clone this repository
2. Open Chrome and go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `extension/` directory

---

## 🚀 How to Use

### Step 1: Get Your API Key

You need an API key from a hosted Perplexity API Free server:

- **Local server**: Generate at http://localhost:8765
- **Remote server**: Get from your admin/friend who's hosting it

### Step 2: Open the Extension

Click the extension icon in your Chrome toolbar.

### Step 3: Enter Your Details

1. Paste your API key (starts with `pplx_`)
2. Verify the server URL (auto-detected if possible)
3. Click "Setup MCP Server"

### Step 4: Follow Instructions

The extension will:
1. Test your API key
2. Generate the configuration
3. Copy it to your clipboard
4. Open setup instructions

### Step 5: Complete Setup

Follow the instructions to:
1. Open your MCP config file
2. Paste the configuration
3. Restart Claude Code
4. Done!

---

## 🎨 Features

### Auto-Detection
- Automatically detects server URL if you're on the dashboard page
- Saves your settings for next time
- Validates API key before proceeding

### Smart Configuration
- Generates proper MCP JSON config
- Handles existing configurations
- Platform-specific instructions (Linux, macOS, Windows)

### User-Friendly
- Beautiful, modern UI
- Clear error messages
- Step-by-step guidance
- Copy-paste ready

---

## 📁 Extension Structure

```
extension/
├── manifest.json              # Extension configuration
├── popup.html                 # Main popup UI
├── instructions.html          # Setup instructions page
├── scripts/
│   ├── popup.js              # Popup logic
│   └── background.js         # Background service worker
├── icons/
│   ├── icon16.png            # 16x16 icon
│   ├── icon48.png            # 48x48 icon
│   └── icon128.png           # 128x128 icon
└── README.md                 # This file
```

---

## 🔧 Technical Details

### Permissions Required

- `storage` - Save API key and server URL
- `nativeMessaging` - (Future) Direct MCP setup
- `http://localhost:8765/*` - Test local servers
- `https://*/*` - Test remote servers

### How It Works

1. **Validation**: Sends a test request to `/health` endpoint
2. **Configuration**: Generates proper MCP JSON structure
3. **Clipboard**: Uses Clipboard API to copy config
4. **Instructions**: Opens detailed setup guide

### MCP Package

The extension configures Claude Code to use:
```
npx -y @perplexity-api-free/mcp-client
```

This package (to be published) handles the MCP protocol communication.

---

## 🐛 Troubleshooting

### Extension Not Working

**Issue**: Extension popup doesn't open
- **Solution**: Refresh the extension at `chrome://extensions/`

**Issue**: "Invalid API key" error
- **Solution**:
  - Check your key starts with `pplx_`
  - Verify you copied the complete key
  - Make sure the server is running

**Issue**: Server URL detection fails
- **Solution**: Manually enter the URL (e.g., `http://localhost:8765`)

### Setup Issues

**Issue**: MCP server not loading in Claude Code
- **Solution**:
  - Verify `npx` is installed (`npm install -g npx`)
  - Check the config file path is correct
  - Restart Claude Code completely

**Issue**: "Command not found: npx"
- **Solution**: Install Node.js and npm from https://nodejs.org

---

## 🔐 Security

- API keys are stored locally using Chrome's secure storage
- Keys are never sent to third parties
- All communication is direct to your specified server
- Open source - verify the code yourself!

---

## 📚 For Developers

### Building

The extension is pure HTML/CSS/JavaScript - no build step required!

### Testing

1. Load the extension in developer mode
2. Open popup with a local server running
3. Test the flow end-to-end
4. Check console for errors

### Contributing

We welcome contributions! To add features:

1. Fork the repository
2. Create your feature branch
3. Test thoroughly
4. Submit a pull request

### Future Enhancements

- [ ] Native messaging host for automatic setup
- [ ] Support for other AI tools (not just Claude Code)
- [ ] Built-in server status checker
- [ ] API key manager (multiple keys)
- [ ] Usage statistics viewer

---

## 📖 Related Documentation

- [Main README](../README.md) - Project overview
- [MCP Setup Guide](../docs/MCP_SETUP_GUIDE.md) - Manual setup
- [End User Setup](../docs/END_USER_SETUP.md) - Without extension
- [AWS Deployment](../docs/AWS_DEPLOYMENT.md) - Host your own

---

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/perplexity-api-free/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/perplexity-api-free/discussions)
- **Email**: support@example.com

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details

---

## 🙏 Credits

Made with ❤️ for the community

Part of the [Perplexity API Free](https://github.com/yourusername/perplexity-api-free) project

---

**Make AI accessible to everyone, one click at a time!** 🚀
