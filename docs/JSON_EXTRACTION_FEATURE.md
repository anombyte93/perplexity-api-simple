# JSON Extraction Feature for TaskMaster AI

## Problem Statement

When TaskMaster AI asks Perplexity to generate JSON (with strict JSON-only requirements), Perplexity often returns conversational text before or after the JSON object, like:

```
I can craft a comprehensive Task #1 for your project based on current best practices...

{
  "title": "Build a real-time crypto price display React component",
  "description": "Develop a simple React component...",
  "details": "...",
  "testStrategy": "...",
  "dependencies": [1, 3]
}
```

This causes TaskMaster's JSON parser to fail with "Invalid JSON response" errors.

## Solution

Added a `json_mode` parameter to both `/search` and `/chat/completions` endpoints that automatically extracts clean JSON from conversational responses.

### How It Works

1. **Detection**: Tries parsing the entire response as JSON first
2. **Extraction**: If parsing fails, uses regex to find JSON objects `{...}` or arrays `[...]`
3. **Validation**: Validates each candidate match until a valid JSON structure is found
4. **Fallback**: Returns original text if no valid JSON is detected

### Implementation Details

**File**: `src/perplexity_api_server.py:149-195`

```python
def extract_json_from_text(text):
    """Extract JSON object or array from conversational text"""
    # Try parsing entire text first
    try:
        json.loads(text)
        return text
    except:
        pass

    # Find and validate JSON objects {...}
    # Find and validate JSON arrays [...]
    # Return original if no JSON found
```

## Usage

### With Native `/search` Endpoint

```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Generate a task in JSON format with title, description, details",
    "mode": "pro",
    "json_mode": true
  }'
```

**Response** (clean JSON only):
```json
{
  "title": "Build authentication system",
  "description": "Implement user authentication with JWT tokens",
  "details": "Create login, register, and token refresh endpoints"
}
```

### With `/chat/completions` Endpoint

```bash
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [{
      "role": "user",
      "content": "Generate a task in JSON format with title and description"
    }],
    "json_mode": true
  }'
```

## TaskMaster Integration

### Current Setup

```bash
export PERPLEXITY_API_KEY="pplx_<your-key>"
export PERPLEXITY_API_BASE_URL="http://localhost:8765"
```

### Required TaskMaster Update

TaskMaster needs to be updated to send `"json_mode": true` in its request body when calling the Perplexity API for research-backed operations.

**Location to update**: TaskMaster's API client that makes requests to PERPLEXITY_API_BASE_URL

**Example update needed**:
```javascript
// BEFORE
const response = await fetch(`${apiBaseUrl}/chat/completions`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${apiKey}` },
  body: JSON.stringify({
    model: 'sonar',
    messages: [{ role: 'user', content: prompt }]
  })
});

// AFTER
const response = await fetch(`${apiBaseUrl}/chat/completions`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${apiKey}` },
  body: JSON.stringify({
    model: 'sonar',
    messages: [{ role: 'user', content: prompt }],
    json_mode: true  // ← Add this for strict JSON responses
  })
});
```

## Testing

### Unit Tests

Run the test suite:
```bash
python3 tests/test_json_extraction.py
```

**Test Results** (all passing):
- ✅ Conversational + JSON extraction
- ✅ Pure JSON returned unchanged
- ✅ Plain text returned unchanged
- ✅ Nested JSON extraction

### Integration Test

1. Start the server:
   ```bash
   ./scripts/start_server.sh
   ```

2. Test with a TaskMaster-style prompt:
   ```bash
   curl -X POST http://localhost:8765/search \
     -H "Authorization: Bearer pplx_your-key" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "CRITICAL: You MUST respond with ONLY a JSON object. NO other text. Generate a task with fields: title, description, details, testStrategy, dependencies (array of numbers or null)",
       "mode": "pro",
       "json_mode": true
     }'
   ```

3. Verify the response is clean JSON with no extra text

### Server Logs

When JSON extraction is applied, you'll see in the logs:
```
🔧 JSON extraction applied
```

## Known Limitations

1. **Nested Braces**: Very deeply nested JSON (>3 levels) may not be detected if it's malformed
2. **Multiple JSON Objects**: Only extracts the first valid JSON object/array found
3. **Syntax Errors**: If Perplexity generates invalid JSON (e.g., `[1][3]` instead of `[1, 3]`), extraction will fail

## Troubleshooting

### Issue: Still receiving conversational text

**Cause**: `json_mode` parameter not being sent
**Solution**: Verify your request includes `"json_mode": true`

### Issue: Invalid JSON still returned

**Cause**: Perplexity generated malformed JSON
**Solution**: Check server logs for the raw response, adjust your prompt to be more explicit

### Issue: Server not extracting JSON

**Cause**: Old server code running
**Solution**: Restart the server to load the updated code

## Files Modified

1. `src/perplexity_api_server.py`
   - Added `extract_json_from_text()` function (lines 149-195)
   - Updated `/search` endpoint (line 221)
   - Updated `/chat/completions` endpoint (line 288)

2. `CLAUDE.md`
   - Added API endpoint documentation with `json_mode` examples
   - Updated TaskMaster integration section
   - Added JSON extraction troubleshooting guide

3. `tests/test_json_extraction.py` (new)
   - Comprehensive test suite for JSON extraction

## Next Steps for You

1. **Update TaskMaster**: Modify TaskMaster's Perplexity API client to send `"json_mode": true` when making research requests

2. **Test with TaskMaster**: Try running:
   ```bash
   tm add-task --prompt "Create a React component" --research
   ```

3. **Monitor server logs**: Watch for `🔧 JSON extraction applied` messages to confirm it's working

4. **Report issues**: If you encounter edge cases where extraction fails, share the Perplexity response for analysis

## Summary

The JSON extraction feature solves the core issue where Perplexity adds conversational text around JSON responses. By enabling `json_mode: true`, your proxy server will automatically extract clean JSON that TaskMaster's strict parser can handle.

The feature is:
- ✅ Fully tested (4/4 tests passing)
- ✅ Documented in CLAUDE.md
- ✅ Backward compatible (defaults to `false`)
- ✅ Running on your server (restarted with new code)

Ready to use once TaskMaster is updated to send the `json_mode` parameter!
