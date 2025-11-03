/**
 * Perplexity API Free - Chrome Extension
 * Popup script for MCP server setup
 */

// DOM elements
const apiKeyInput = document.getElementById('apiKey');
const serverUrlInput = document.getElementById('serverUrl');
const setupBtn = document.getElementById('setupBtn');
const syncPerplexityCookieBtn = document.getElementById('syncPerplexityCookieBtn');
const syncChatGPTCookieBtn = document.getElementById('syncChatGPTCookieBtn');
const statusDiv = document.getElementById('status');

// Load saved settings
chrome.storage.sync.get(['apiKey', 'serverUrl'], (result) => {
  if (result.apiKey) {
    apiKeyInput.value = result.apiKey;
  }
  if (result.serverUrl) {
    serverUrlInput.value = result.serverUrl;
  }
});

// Auto-save settings on change
apiKeyInput.addEventListener('input', () => {
  chrome.storage.sync.set({ apiKey: apiKeyInput.value });
});

serverUrlInput.addEventListener('input', () => {
  chrome.storage.sync.set({ serverUrl: serverUrlInput.value });
});

/**
 * Display status message
 */
function showStatus(message, type = 'info') {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  statusDiv.style.display = 'block';
}

/**
 * Hide status message
 */
function hideStatus() {
  statusDiv.style.display = 'none';
}

/**
 * Validate API key format
 */
function validateApiKey(apiKey) {
  return apiKey && apiKey.startsWith('pplx_') && apiKey.length > 10;
}

/**
 * Test API key against server
 */
async function testApiKey(serverUrl, apiKey) {
  try {
    const response = await fetch(`${serverUrl}/health`, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });

    if (response.ok) {
      return { success: true };
    } else {
      const text = await response.text();
      return { success: false, error: `Server returned ${response.status}: ${text}` };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * Get cookies from a domain
 */
async function getCookies(domain) {
  try {
    console.log('🔵 getCookies called for domain:', domain);

    // Check if chrome.cookies API is available
    if (!chrome.cookies) {
      console.error('❌ chrome.cookies API not available!');
      throw new Error('Chrome cookies API not available. Check permissions.');
    }

    console.log('🔵 Calling chrome.cookies.getAll...');
    const cookies = await chrome.cookies.getAll({ domain });
    console.log('🔵 chrome.cookies.getAll returned:', cookies.length, 'cookies');

    // Also try without the dot
    if (cookies.length === 0 && domain.startsWith('.')) {
      const altDomain = domain.substring(1);
      console.log('🔵 Trying alternative domain (without dot):', altDomain);
      const altCookies = await chrome.cookies.getAll({ domain: altDomain });
      console.log('🔵 Alternative domain returned:', altCookies.length, 'cookies');
      return altCookies;
    }

    return cookies;
  } catch (error) {
    console.error('❌ Error getting cookies:', error);
    console.error('❌ Error details:', error.message, error.stack);
    return [];
  }
}

/**
 * Format cookies as string for server
 */
function formatCookies(cookies) {
  return cookies
    .map(cookie => `${cookie.name}=${cookie.value}`)
    .join('; ');
}

/**
 * Sync Perplexity cookies to server
 */
async function syncPerplexityCookie() {
  const apiKey = apiKeyInput.value.trim();
  const serverUrl = serverUrlInput.value.trim();

  console.log('🔵 Starting Perplexity cookie sync...');
  console.log('🔵 API Key:', apiKey.substring(0, 10) + '...');
  console.log('🔵 Server URL:', serverUrl);

  if (!validateApiKey(apiKey)) {
    console.error('❌ Invalid API key format');
    showStatus('❌ Invalid API key format', 'error');
    return;
  }

  try {
    syncPerplexityCookieBtn.disabled = true;
    syncPerplexityCookieBtn.innerHTML = '<span class="spinner"></span> Syncing...';

    // Get Perplexity cookies
    console.log('🔵 Attempting to get cookies from .perplexity.ai...');
    const cookies = await getCookies('.perplexity.ai');
    console.log('🔵 Found cookies:', cookies.length);
    console.log('🔵 Cookie details:', cookies.map(c => ({ name: c.name, domain: c.domain })));

    if (cookies.length === 0) {
      console.error('❌ No cookies found for .perplexity.ai');
      showStatus('❌ No Perplexity cookies found. Please login to perplexity.ai first.', 'error');
      return;
    }

    const cookieString = formatCookies(cookies);
    console.log('🔵 Cookie string length:', cookieString.length);
    console.log('🔵 Cookie string preview:', cookieString.substring(0, 100) + '...');

    // Send to server
    console.log('🔵 Sending cookie to server:', `${serverUrl}/api/save-cookie`);
    const response = await fetch(`${serverUrl}/api/save-cookie`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cookie: cookieString })
    });

    console.log('🔵 Response status:', response.status);
    console.log('🔵 Response ok:', response.ok);

    if (response.ok) {
      const result = await response.json();
      console.log('✅ Success! Response:', result);
      showStatus('✅ Perplexity cookie synced successfully!', 'success');
    } else {
      const error = await response.text();
      console.error('❌ Server error:', error);
      showStatus(`❌ Failed to sync cookie: ${error}`, 'error');
    }
  } catch (error) {
    console.error('❌ Exception occurred:', error);
    console.error('❌ Error stack:', error.stack);
    showStatus(`❌ Error: ${error.message}`, 'error');
  } finally {
    syncPerplexityCookieBtn.disabled = false;
    syncPerplexityCookieBtn.innerHTML = '🔮 Sync Perplexity Cookie';
  }
}

/**
 * Sync ChatGPT cookies to server
 */
async function syncChatGPTCookie() {
  const apiKey = apiKeyInput.value.trim();
  const serverUrl = serverUrlInput.value.trim();

  if (!validateApiKey(apiKey)) {
    showStatus('❌ Invalid API key format', 'error');
    return;
  }

  try {
    syncChatGPTCookieBtn.disabled = true;
    syncChatGPTCookieBtn.innerHTML = '<span class="spinner"></span> Syncing...';

    // Get ChatGPT cookies
    const cookies = await getCookies('.openai.com');
    if (cookies.length === 0) {
      showStatus('❌ No ChatGPT cookies found. Please login to chat.openai.com first.', 'error');
      return;
    }

    const cookieString = formatCookies(cookies);

    // Send to server
    const response = await fetch(`${serverUrl}/api/save-chatgpt-cookie`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ cookie: cookieString })
    });

    if (response.ok) {
      const result = await response.json();
      showStatus('✅ ChatGPT cookie synced successfully!', 'success');
    } else {
      const error = await response.text();
      showStatus(`❌ Failed to sync cookie: ${error}`, 'error');
    }
  } catch (error) {
    showStatus(`❌ Error: ${error.message}`, 'error');
  } finally {
    syncChatGPTCookieBtn.disabled = false;
    syncChatGPTCookieBtn.innerHTML = '🤖 Sync ChatGPT Cookie';
  }
}

/**
 * Generate MCP configuration
 */
function generateMcpConfig(serverUrl, apiKey) {
  return {
    "mcpServers": {
      "perplexity-free": {
        "command": "npx",
        "args": ["-y", "@perplexity-api-free/mcp-client"],
        "env": {
          "PERPLEXITY_API_KEY": apiKey,
          "PERPLEXITY_API_BASE_URL": serverUrl
        }
      }
    }
  };
}

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Clipboard error:', error);
    return false;
  }
}

/**
 * Setup MCP server
 */
async function setupMcpServer() {
  const apiKey = apiKeyInput.value.trim();
  const serverUrl = serverUrlInput.value.trim();

  // Validate inputs
  if (!validateApiKey(apiKey)) {
    showStatus('❌ Invalid API key format. Must start with "pplx_"', 'error');
    return;
  }

  if (!serverUrl) {
    showStatus('❌ Please enter server URL', 'error');
    return;
  }

  try {
    setupBtn.disabled = true;
    setupBtn.innerHTML = '<span class="spinner"></span> Testing connection...';
    hideStatus();

    // Test API key
    const testResult = await testApiKey(serverUrl, apiKey);
    if (!testResult.success) {
      showStatus(`❌ Connection failed: ${testResult.error}`, 'error');
      return;
    }

    // Generate config
    setupBtn.innerHTML = '<span class="spinner"></span> Generating config...';
    const config = generateMcpConfig(serverUrl, apiKey);
    const configJson = JSON.stringify(config, null, 2);

    // Copy to clipboard
    setupBtn.innerHTML = '<span class="spinner"></span> Copying to clipboard...';
    const copied = await copyToClipboard(configJson);

    if (copied) {
      showStatus(
        '✅ Success! Configuration copied to clipboard. Open instructions to complete setup.',
        'success'
      );

      // Open instructions page
      setTimeout(() => {
        chrome.tabs.create({ url: chrome.runtime.getURL('instructions.html') });
      }, 1000);
    } else {
      showStatus('✅ Configuration ready! Please copy manually:', 'info');
      console.log(configJson);
      alert('Configuration:\n\n' + configJson);
    }

    // Save settings
    chrome.storage.sync.set({ apiKey, serverUrl });

  } catch (error) {
    showStatus(`❌ Error: ${error.message}`, 'error');
  } finally {
    setupBtn.disabled = false;
    setupBtn.innerHTML = 'Setup MCP Server';
  }
}

// Event listeners
setupBtn.addEventListener('click', setupMcpServer);
syncPerplexityCookieBtn.addEventListener('click', syncPerplexityCookie);
syncChatGPTCookieBtn.addEventListener('click', syncChatGPTCookie);

// Enter key to submit
apiKeyInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') setupMcpServer();
});

serverUrlInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') setupMcpServer();
});
