#!/usr/bin/env python3
"""
Test JSON extraction from conversational Perplexity responses
"""
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from perplexity_api_server import extract_json_from_text


def test_extraction():
    """Test JSON extraction with real example from TaskMaster debug log"""

    # Example from the debug log - Perplexity's response with conversational text before JSON
    perplexity_response = '''I can craft a comprehensive Task #1 for your project based on current best practices for building a real-time cryptocurrency price display in React. Assumptions: the component should be lightweight, rely on public APIs (e.g., CoinGecko, CoinCap), use React hooks, manage data fetching cleanly, and include basic testing and documentation.

{
  "title": "Build a real-time crypto price display React component",
  "description": "Develop a simple React component that shows live cryptocurrency prices by consuming a public API and updates in real-time with minimal UI complexity.",
  "details": "Implementation details here...",
  "testStrategy": "Test strategy here...",
  "dependencies": [1, 3]
}'''

    print("="*80)
    print("Testing JSON Extraction")
    print("="*80)
    print("\nOriginal Response (first 200 chars):")
    print(perplexity_response[:200] + "...")
    print("\n" + "="*80)

    # Extract JSON
    extracted = extract_json_from_text(perplexity_response)

    print("\nExtracted JSON:")
    print(extracted)
    print("\n" + "="*80)

    # Validate it's valid JSON
    import json
    try:
        parsed = json.loads(extracted)
        print("\n✅ PASS: Extracted valid JSON")
        print(f"   Title: {parsed.get('title')}")
        print(f"   Description: {parsed.get('description')[:60]}...")
        print(f"   Dependencies: {parsed.get('dependencies')}")
        return True
    except json.JSONDecodeError as e:
        print(f"\n❌ FAIL: Invalid JSON - {e}")
        return False


def test_pure_json():
    """Test that already-valid JSON is returned as-is"""
    pure_json = '{"test": "value", "number": 123}'

    extracted = extract_json_from_text(pure_json)

    if extracted == pure_json:
        print("\n✅ PASS: Pure JSON returned unchanged")
        return True
    else:
        print("\n❌ FAIL: Pure JSON was modified")
        return False


def test_no_json():
    """Test that non-JSON text is returned unchanged"""
    plain_text = "This is just plain text with no JSON at all."

    extracted = extract_json_from_text(plain_text)

    if extracted == plain_text:
        print("\n✅ PASS: Plain text returned unchanged")
        return True
    else:
        print("\n❌ FAIL: Plain text was modified")
        return False


def test_nested_json():
    """Test extraction with nested objects"""
    nested_response = '''Here's a complex task:

{
  "title": "Test",
  "metadata": {
    "author": "Claude",
    "tags": ["test", "nested"]
  },
  "data": [1, 2, 3]
}

That's the task definition.'''

    extracted = extract_json_from_text(nested_response)

    import json
    try:
        parsed = json.loads(extracted)
        if parsed.get('metadata', {}).get('author') == 'Claude':
            print("\n✅ PASS: Nested JSON extracted correctly")
            return True
        else:
            print("\n❌ FAIL: Nested JSON structure incorrect")
            return False
    except:
        print("\n❌ FAIL: Could not extract nested JSON")
        return False


if __name__ == '__main__':
    print("\n" + "="*80)
    print("JSON Extraction Test Suite")
    print("="*80 + "\n")

    results = []
    results.append(("Conversational + JSON", test_extraction()))
    results.append(("Pure JSON", test_pure_json()))
    results.append(("Plain Text", test_no_json()))
    results.append(("Nested JSON", test_nested_json()))

    print("\n" + "="*80)
    print("Test Results Summary")
    print("="*80)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total = len(results)
    passed_count = sum(1 for _, passed in results if passed)

    print(f"\n{passed_count}/{total} tests passed")
    print("="*80 + "\n")

    sys.exit(0 if passed_count == total else 1)
