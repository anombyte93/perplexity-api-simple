# API Endpoints Guide

## Overview

The Perplexity API Simple server now provides **two API formats**:

1. **Native Perplexity Format** (`/search`) - RECOMMENDED
2. **OpenAI-Compatible Format** (`/chat/completions`) - For backward compatibility with TaskMaster AI and MCP servers

Both endpoints return **plain text responses** (not JSON-wrapped), which is the raw output from Perplexity.

---

## Native Perplexity Format (Recommended)

### Endpoint: `/search`

**Why use this endpoint?**
- Direct, simple API that matches Perplexity's native parameters
- No translation layer - parameters map directly to Perplexity
- Supports optional model selection within modes
- Cleaner request format

### Request Format

```bash
POST /search
Authorization: Bearer pplx_your-api-key
Content-Type: application/json

{
  "query": "Your question here",           # Required: The search query
  "mode": "auto",                          # Optional: auto, pro, reasoning, deep research (default: auto)
  "model": "gpt-4o",                       # Optional: Specific model within mode
  "sources": ["web"]                       # Optional: web, scholar, social (default: ["web"])
}
```

### Response Format

Plain text response from Perplexity:

```
Your answer text here...
```

### Examples

**Basic search (auto mode):**
```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'
```

**Pro mode with specific model:**
```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain quantum computing",
    "mode": "pro",
    "model": "gpt-4o"
  }'
```

**Reasoning mode:**
```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Solve this math problem: ...",
    "mode": "reasoning"
  }'
```

**Scholar search:**
```bash
curl -X POST http://localhost:8765/search \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Recent papers on machine learning",
    "mode": "pro",
    "sources": ["scholar"]
  }'
```

---

## OpenAI-Compatible Format

### Endpoint: `/chat/completions`

**Why use this endpoint?**
- Backward compatibility with TaskMaster AI
- Compatible with OpenAI-based MCP servers
- Familiar format for developers used to OpenAI API

### Request Format

```bash
POST /chat/completions
Authorization: Bearer pplx_your-api-key
Content-Type: application/json

{
  "model": "sonar",                        # Required: Model name (maps to mode)
  "messages": [                            # Required: Chat messages array
    {
      "role": "user",
      "content": "Your question here"
    }
  ],
  "sources": ["web"]                       # Optional: web, scholar, social
}
```

### Model Name Mapping

The `model` parameter is automatically mapped to Perplexity modes:

| Model Name | Perplexity Mode | Internal Model |
|------------|-----------------|----------------|
| `sonar`, `sonar-small`, `sonar-medium` | `auto` | `turbo` |
| `sonar-pro` | `pro` | `pplx_pro` |
| `sonar-reasoning` | `reasoning` | `pplx_reasoning` |
| `sonar-deep-research` | `deep research` | `pplx_alpha` |

You can also use mode names directly: `auto`, `pro`, `reasoning`, `deep research`

### Response Format

Plain text response from Perplexity (same as `/search`):

```
Your answer text here...
```

### Examples

**Basic search:**
```bash
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar",
    "messages": [{"role": "user", "content": "What is Python?"}]
  }'
```

**Pro mode:**
```bash
curl -X POST http://localhost:8765/chat/completions \
  -H "Authorization: Bearer pplx_your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "Explain quantum computing"}]
  }'
```

---

## Comparison

| Feature | `/search` (Native) | `/chat/completions` (Compatible) |
|---------|-------------------|----------------------------------|
| **Request format** | `{query, mode, model, sources}` | `{model, messages}` |
| **Query field** | `query: "text"` | `messages[0].content` |
| **Mode selection** | Direct: `mode: "pro"` | Mapped: `model: "sonar-pro"` |
| **Model selection** | `model: "gpt-4o"` within mode | Not supported |
| **Response** | Plain text | Plain text |
| **Use case** | New integrations, direct usage | TaskMaster AI, MCP servers |

---

## Common Integration Patterns

### Python

**Native format:**
```python
import requests

response = requests.post(
    'http://localhost:8765/search',
    headers={'Authorization': 'Bearer pplx_your-key'},
    json={
        'query': 'What is Python?',
        'mode': 'auto'
    }
)
print(response.text)
```

**Compatible format:**
```python
import requests

response = requests.post(
    'http://localhost:8765/chat/completions',
    headers={'Authorization': 'Bearer pplx_your-key'},
    json={
        'model': 'sonar',
        'messages': [{'role': 'user', 'content': 'What is Python?'}]
    }
)
print(response.text)
```

### JavaScript/Node.js

**Native format:**
```javascript
const response = await fetch('http://localhost:8765/search', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer pplx_your-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'What is Python?',
    mode: 'auto'
  })
});
const answer = await response.text();
console.log(answer);
```

### TaskMaster AI

```bash
export PERPLEXITY_API_KEY="pplx_your-key"
export PERPLEXITY_API_BASE_URL="http://localhost:8765"

# TaskMaster will automatically use /chat/completions endpoint
tm parse-prd --research
```

---

## Migration Guide

If you're currently using the `/chat/completions` endpoint and want to switch to the native `/search` format:

**Before:**
```json
{
  "model": "sonar-pro",
  "messages": [{"role": "user", "content": "What is Python?"}]
}
```

**After:**
```json
{
  "query": "What is Python?",
  "mode": "pro"
}
```

The response format remains unchanged (plain text), so no changes needed on the response handling side.
