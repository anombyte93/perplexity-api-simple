/**
 * Perplexity API Free - Chrome Extension
 * Background service worker
 */

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('Perplexity API Free extension installed!');

    // Open welcome page on first install
    chrome.tabs.create({
      url: chrome.runtime.getURL('instructions.html')
    });
  } else if (details.reason === 'update') {
    console.log('Perplexity API Free extension updated to version', chrome.runtime.getManifest().version);
  }
});

// Handle extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  // This will be handled by the popup, but we can add additional logic here if needed
  console.log('Extension icon clicked');
});

// Message handler for communication between popup and background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);

  if (request.action === 'getCookies') {
    // Handle cookie retrieval requests
    chrome.cookies.getAll({ domain: request.domain }, (cookies) => {
      sendResponse({ cookies });
    });
    return true; // Keep the message channel open for async response
  }

  if (request.action === 'validateServer') {
    // Validate server connection
    fetch(`${request.serverUrl}/health`)
      .then(response => response.ok)
      .then(isValid => sendResponse({ valid: isValid }))
      .catch(() => sendResponse({ valid: false }));
    return true; // Keep the message channel open for async response
  }

  if (request.action === 'openInstructions') {
    // Open instructions in a new tab
    chrome.tabs.create({
      url: chrome.runtime.getURL('instructions.html')
    });
    sendResponse({ success: true });
  }

  return false;
});

// Keep service worker alive (if needed for long-running operations)
chrome.runtime.onStartup.addListener(() => {
  console.log('Extension service worker started');
});

// Alarm for periodic tasks (if needed in future)
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'healthCheck') {
    // Perform periodic health checks if configured
    chrome.storage.sync.get(['serverUrl', 'apiKey'], (result) => {
      if (result.serverUrl && result.apiKey) {
        fetch(`${result.serverUrl}/health`, {
          headers: {
            'Authorization': `Bearer ${result.apiKey}`
          }
        })
          .then(response => {
            console.log('Health check:', response.ok ? 'OK' : 'Failed');
          })
          .catch(error => {
            console.error('Health check error:', error);
          });
      }
    });
  }
});

// Optional: Set up periodic health check (disabled by default)
// chrome.alarms.create('healthCheck', { periodInMinutes: 60 });

console.log('Perplexity API Free background service worker loaded');
