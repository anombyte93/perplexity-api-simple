#!/usr/bin/env python3
"""
Perplexity API Server - Simple Proxy
Provides a local API server that proxies requests to Perplexity using your cookie

This server uses your Perplexity cookie to make authenticated searches and returns
the raw Perplexity responses.

Perfect for:
- TaskMaster AI
- Claude Code (MCP server)
- Any tool that needs Perplexity search capabilities

Setup:
    1. Create .env file with:
       PERPLEXITY_COOKIE=your-cookie-here

    2. Start server:
       ./scripts/start_server.sh

Usage:
    - Base URL: http://localhost:8765
    - API Key: Generate from web dashboard at http://localhost:8765/
    - Send POST to /chat/completions with query in messages format
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sys
import os
import time
import json
import secrets
import io
import zipfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from perplexity_fixed import PerplexityFixed

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

print("✅ Perplexity Proxy Server")
print("="*80)

# Get cookie from environment if available
cookie_str = os.environ.get('PERPLEXITY_COOKIE')
cookies = None

if cookie_str:
    cookies = {}
    for cookie_pair in cookie_str.split(';'):
        cookie_pair = cookie_pair.strip()
        if '=' in cookie_pair:
            name, value = cookie_pair.split('=', 1)
            cookies[name.strip()] = value.strip()
    print(f"✅ Using cookie authentication for Perplexity")
else:
    print(f"ℹ️  Running in anonymous mode (no cookie)")

# Create client
client = PerplexityFixed(cookies=cookies)
print(f"✅ Perplexity client initialized")

# API keys storage
API_KEYS_FILE = Path(__file__).parent.parent / '.api_keys.json'
ENV_FILE = Path(__file__).parent.parent / '.env'

def load_api_keys():
    """Load API keys from file"""
    if API_KEYS_FILE.exists():
        try:
            with open(API_KEYS_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except:
            return {}
    return {}

def save_api_keys(keys):
    """Save API keys to file"""
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(keys, f, indent=2)

def load_env_file():
    """Load .env file as dict"""
    env_dict = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip()
    return env_dict

def save_env_file(env_dict):
    """Save dict to .env file"""
    with open(ENV_FILE, 'w') as f:
        for key, value in env_dict.items():
            f.write(f"{key}={value}\n")

def get_api_key_from_request():
    """Extract API key from request headers"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    # Support both "Bearer <key>" and just "<key>"
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    else:
        return auth_header

def validate_api_key(api_key):
    """Check if API key is valid and active"""
    if not api_key:
        return False

    keys_dict = load_api_keys()
    if api_key in keys_dict:
        key_data = keys_dict[api_key]
        return key_data.get('active', True)
    return False

def increment_api_key_usage(api_key):
    """Increment usage count and update last_used timestamp"""
    keys_dict = load_api_keys()
    if api_key in keys_dict:
        key_data = keys_dict[api_key]
        key_data['last_used'] = time.time()
        key_data['usage_count'] = key_data.get('usage_count', 0) + 1
        save_api_keys(keys_dict)

def track_api_key_tokens(api_key, input_tokens, output_tokens):
    """Track token usage for an API key"""
    keys_dict = load_api_keys()
    if api_key in keys_dict:
        key_data = keys_dict[api_key]
        key_data['total_input_tokens'] = key_data.get('total_input_tokens', 0) + input_tokens
        key_data['total_output_tokens'] = key_data.get('total_output_tokens', 0) + output_tokens
        save_api_keys(keys_dict)



@app.route('/chat/completions', methods=['POST'])
def chat_completions():
    """
    Main Perplexity proxy endpoint
    Accepts messages in standard chat format and returns raw Perplexity response
    """
    # Validate API key
    api_key = get_api_key_from_request()
    if not validate_api_key(api_key):
        return "Error: Invalid API key", 401, {'Content-Type': 'text/plain; charset=utf-8'}

    increment_api_key_usage(api_key)

    try:
        data = request.json
        print(f"\n📥 Incoming request: {data.get('model', 'unknown model')}")

        # Extract parameters
        messages = data.get('messages', [])
        model = data.get('model', 'sonar')

        # Get the user's query from messages
        query = None
        for msg in messages:
            if msg.get('role') == 'user':
                query = msg.get('content')
                break

        if not query:
            return "Error: No user message found in messages array", 400, {'Content-Type': 'text/plain; charset=utf-8'}

        print(f"🔍 Query: {query[:100]}...")

        # Map model names to our modes
        mode_mapping = {
            'sonar': 'auto',
            'sonar-small': 'auto',
            'sonar-medium': 'auto',
            'sonar-pro': 'pro',
            'sonar-reasoning': 'reasoning',
            'sonar-reasoning-pro': 'reasoning',
            'sonar-deep-research': 'deep research',
            # Also support direct mode names
            'auto': 'auto',
            'pro': 'pro',
            'reasoning': 'reasoning',
            'deep research': 'deep research'
        }

        mode = mode_mapping.get(model.lower(), 'auto')

        # Extract source if specified
        sources = ['web']  # default
        if 'sources' in data:
            sources = data['sources']

        print(f"⚙️  Mode: {mode} | Sources: {sources}")

        # Perform search using our fixed library
        start_time = time.time()
        answer = client.search(
            query=query,
            mode=mode,
            sources=sources
        )
        elapsed = time.time() - start_time

        print(f"✅ Response generated in {elapsed:.2f}s")

        # Track token usage (rough approximation: 1 word ≈ 1.3 tokens)
        prompt_tokens = int(len(query.split()) * 1.3)
        completion_tokens = int(len(answer.split()) * 1.3)
        track_api_key_tokens(api_key, prompt_tokens, completion_tokens)

        # Return exactly what Perplexity gives us
        return answer, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

        return f"Error: {str(e)}", 500, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/api/cost-savings', methods=['GET'])
def get_cost_savings():
    """Calculate cost savings vs official Perplexity Sonar-Pro pricing"""
    keys_dict = load_api_keys()

    total_input_tokens = 0
    total_output_tokens = 0

    # Sum up all token usage across all keys
    for key_data in keys_dict.values():
        if isinstance(key_data, dict):
            total_input_tokens += key_data.get('total_input_tokens', 0)
            total_output_tokens += key_data.get('total_output_tokens', 0)

    # Official Perplexity Sonar-Pro pricing (as of 2025)
    # $3/1M input tokens, $15/1M output tokens
    input_cost = (total_input_tokens / 1_000_000) * 3
    output_cost = (total_output_tokens / 1_000_000) * 15
    total_cost = input_cost + output_cost

    # Format tokens in thousands with K suffix
    def format_tokens(tokens):
        if tokens == 0:
            return "0"
        elif tokens >= 1000:
            return f"{round(tokens / 1000, 1)}K"
        else:
            return str(tokens)

    total_tokens = total_input_tokens + total_output_tokens

    # Model pricing (official Perplexity pricing as of 2025)
    model_pricing = {
        'sonar': {'input': 0.2, 'output': 0.2},  # $0.2/1M tokens
        'sonar-pro': {'input': 3, 'output': 15},  # $3/1M input, $15/1M output
        'sonar-reasoning': {'input': 3, 'output': 15},  # Same as pro
        'sonar-deep-research': {'input': 5, 'output': 5}  # $5/1M tokens
    }

    # For now, we calculate all usage at sonar-pro pricing (most expensive)
    # TODO: Track per-model usage for accurate breakdown
    breakdown = {}
    for model, pricing in model_pricing.items():
        model_input_cost = (total_input_tokens / 1_000_000) * pricing['input']
        model_output_cost = (total_output_tokens / 1_000_000) * pricing['output']
        model_total_cost = model_input_cost + model_output_cost

        breakdown[model] = {
            'saved': round(model_total_cost, 2),
            'tokens': total_tokens,
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens
        }

    return jsonify({
        'total_saved': round(total_cost, 2),
        'total_tokens': total_tokens,
        'total_tokens_formatted': format_tokens(total_tokens),
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens,
        'input_tokens_formatted': format_tokens(total_input_tokens),
        'output_tokens_formatted': format_tokens(total_output_tokens),
        'breakdown': breakdown
    })


@app.route('/api/providers', methods=['GET'])
def get_providers():
    """Stub endpoint for providers - Perplexity only"""
    return jsonify({
        'providers': ['perplexity'],
        'active': ['perplexity']
    })


@app.route('/api/version', methods=['GET'])
def get_version():
    """Return server version"""
    return jsonify({
        'version': '1.0.0',
        'service': 'perplexity-api-simple'
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker and monitoring"""
    has_cookie = client is not None
    return jsonify({
        'status': 'healthy',
        'service': 'perplexity-api-simple',
        'authenticated': has_cookie,
        'version': '1.0.0'
    }), 200


@app.route('/api/toggle-provider', methods=['POST'])
def toggle_provider():
    """Stub endpoint - Perplexity is always enabled"""
    return jsonify({
        'success': True,
        'message': 'Perplexity is the only provider and cannot be disabled'
    })


@app.route('/', methods=['GET'])
def home():
    """Redirect to dashboard"""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'index.html')


@app.route('/dashboard')
@app.route('/web')
def serve_dashboard():
    """Serve the web dashboard"""
    web_dir = Path(__file__).parent.parent / 'web'
    return send_from_directory(web_dir, 'index.html')


# API Key Management Routes
@app.route('/api/list-keys', methods=['GET'])
def list_api_keys():
    """List all API keys"""
    keys_dict = load_api_keys()

    # Convert dictionary format to array format for frontend
    keys_array = []
    if isinstance(keys_dict, dict):
        for full_key, metadata in keys_dict.items():
            key_obj = metadata.copy() if isinstance(metadata, dict) else {}
            key_obj['full_key'] = full_key
            keys_array.append(key_obj)
    elif isinstance(keys_dict, list):
        keys_array = keys_dict

    return jsonify({'success': True, 'keys': keys_array})


@app.route('/api/generate-key', methods=['POST'])
def generate_api_key():
    """Generate a new API key"""
    data = request.json or {}
    name = data.get('name', 'Unnamed Key')

    # Generate a secure random key
    api_key = f"pplx_{secrets.token_urlsafe(32)}"

    # Load existing keys
    keys_dict = load_api_keys()

    # Ensure dictionary format
    if not isinstance(keys_dict, dict):
        keys_dict = {}

    # Create new key entry
    keys_dict[api_key] = {
        'name': name,
        'created': time.time(),
        'last_used': None,
        'usage_count': 0,
        'active': True
    }

    save_api_keys(keys_dict)

    return jsonify({'success': True, 'api_key': api_key})


@app.route('/api/delete-key', methods=['POST'])
def delete_api_key():
    """Delete an API key"""
    data = request.json or {}
    key_to_delete = data.get('key')

    if not key_to_delete:
        return jsonify({'success': False, 'error': 'No key specified'}), 400

    keys_dict = load_api_keys()

    # Ensure dictionary format
    if isinstance(keys_dict, dict):
        if key_to_delete in keys_dict:
            del keys_dict[key_to_delete]
        save_api_keys(keys_dict)

    return jsonify({'success': True})


@app.route('/api/toggle-key', methods=['POST'])
def toggle_api_key():
    """Enable/disable an API key"""
    data = request.json or {}
    key_to_toggle = data.get('key')

    if not key_to_toggle:
        return jsonify({'success': False, 'error': 'No key specified'}), 400

    keys_dict = load_api_keys()

    # Ensure dictionary format
    if isinstance(keys_dict, dict):
        if key_to_toggle in keys_dict:
            keys_dict[key_to_toggle]['active'] = not keys_dict[key_to_toggle].get('active', True)
            save_api_keys(keys_dict)
            return jsonify({'success': True, 'active': keys_dict[key_to_toggle]['active']})

    return jsonify({'success': False, 'error': 'Key not found'}), 404


# Cookie Management Routes
@app.route('/api/cookie-status', methods=['GET'])
def get_cookie_status():
    """Get current cookie status"""
    env_dict = load_env_file()
    cookie_value = env_dict.get('PERPLEXITY_COOKIE', '')

    has_cookie = bool(cookie_value and cookie_value.strip())

    # Show preview of cookie (first 20 chars + ...)
    cookie_preview = None
    if has_cookie:
        cookie_preview = cookie_value[:20] + '...' if len(cookie_value) > 20 else cookie_value

    return jsonify({
        'has_cookie': has_cookie,
        'cookie_preview': cookie_preview
    })


@app.route('/api/save-cookie', methods=['POST'])
def save_cookie_endpoint():
    """Save Perplexity cookie to .env file"""
    # Validate API key for security
    api_key = get_api_key_from_request()
    if not validate_api_key(api_key):
        return jsonify({
            'success': False,
            'error': 'Unauthorized - Valid API key required'
        }), 401

    data = request.json or {}
    cookie_value = data.get('cookie', '').strip()

    if not cookie_value:
        return jsonify({'success': False, 'error': 'Cookie value is required'}), 400

    # Load current .env
    env_dict = load_env_file()

    # Update cookie
    env_dict['PERPLEXITY_COOKIE'] = cookie_value

    # Save to .env
    save_env_file(env_dict)

    print(f"✅ Cookie saved to .env file")

    # Hot-reload the cookie without restarting
    global cookies, client
    cookies = {}
    for cookie_pair in cookie_value.split(';'):
        cookie_pair = cookie_pair.strip()
        if '=' in cookie_pair:
            name, value = cookie_pair.split('=', 1)
            cookies[name.strip()] = value.strip()

    # Recreate client with new cookies
    client = PerplexityFixed(cookies=cookies)

    print(f"✅ Cookie hot-reloaded! Server still running.")

    return jsonify({
        'success': True,
        'message': 'Cookie saved and hot-reloaded! No restart needed.',
        'requires_restart': False
    })


@app.route('/api/clear-cookie', methods=['POST'])
def clear_cookie_endpoint():
    """Clear Perplexity cookie from .env file"""
    # Load current .env
    env_dict = load_env_file()

    # Remove cookie
    if 'PERPLEXITY_COOKIE' in env_dict:
        del env_dict['PERPLEXITY_COOKIE']

    # Save to .env
    save_env_file(env_dict)

    print(f"✅ Cookie cleared from .env file")

    return jsonify({
        'success': True,
        'message': 'Cookie cleared! Please restart the server.',
        'requires_restart': True
    })


@app.route('/download/extension', methods=['GET'])
def download_extension():
    """Download Chrome extension as ZIP file"""
    try:
        # Get extension directory path
        extension_dir = Path(__file__).parent.parent / 'extension'

        if not extension_dir.exists():
            return "Error: Extension directory not found", 404

        # Create ZIP file in memory
        memory_file = io.BytesIO()

        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through extension directory and add all files
            for root, dirs, files in os.walk(extension_dir):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    # Skip hidden files
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    # Create archive name relative to extension directory
                    arcname = Path('extension') / file_path.relative_to(extension_dir)
                    zipf.write(file_path, arcname)

        # Seek to beginning of file
        memory_file.seek(0)

        print("📦 Chrome extension downloaded")

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='perplexity-extension.zip'
        )

    except Exception as e:
        print(f"❌ Error creating extension ZIP: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8765))

    print("\n" + "="*80)
    print("🚀 Perplexity Proxy Server")
    print("="*80)
    print(f"")
    print(f"✅ Server running at: http://localhost:{port}")
    print(f"📊 Web Dashboard: http://localhost:{port}/")
    print(f"🔗 API Endpoint: http://localhost:{port}/chat/completions")
    print(f"")
    print(f"🎯 Quick Start:")
    print(f"   1. Open http://localhost:{port}/ to generate an API key")
    print(f"   2. Send POST requests to /chat/completions")
    print(f"   3. Get raw Perplexity responses")
    print(f"")
    print(f"📝 Available modes:")
    print(f"   - sonar (default/auto)")
    print(f"   - sonar-pro")
    print(f"   - sonar-reasoning")
    print(f"   - sonar-deep-research")
    print(f"")
    print(f"🍪 Cookie: {'✅ Authenticated' if cookies else '❌ Not set (anonymous mode)'}")
    print(f"")
    print(f"Press Ctrl+C to stop")
    print("="*80 + "\n")

    app.run(host='0.0.0.0', port=port, debug=False)
