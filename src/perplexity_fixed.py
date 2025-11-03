#!/usr/bin/env python3
"""
Fixed Perplexity AI Client
Patches the broken perplexity-api library

Usage:
    from perplexity_fixed import PerplexityFixed
    client = PerplexityFixed()
    answer = client.search("What is Python?")
"""

import json
from uuid import uuid4
from curl_cffi import requests


class PerplexityFixed:
    def __init__(self, cookies=None):
        """
        Initialize the Perplexity client

        Args:
            cookies: Optional cookies dict for authenticated requests
        """
        self.session = requests.Session(impersonate='chrome')
        if cookies:
            self.session.cookies.update(cookies)

    def search(self, query, mode='auto', model=None, sources=None, stream=False):
        """
        Search using Perplexity AI

        Args:
            query: The question to ask
            mode: Search mode ('auto', 'pro', 'reasoning', 'deep research')
            model: Model to use (None for default, or specify like 'gpt-4o', 'claude 3.7 sonnet', etc.)
            sources: List of sources (['web'], ['scholar'], ['social']) or None for default
            stream: Whether to stream responses (generator)

        Returns:
            Answer text (or generator if stream=True)
        """
        if sources is None:
            sources = ['web']

        # Map model preferences based on mode
        model_mapping = {
            'auto': {
                None: 'turbo'
            },
            'pro': {
                None: 'pplx_pro',
                'sonar': 'experimental',
                'gpt-4.5': 'gpt45',
                'gpt-4o': 'gpt4o',
                'claude 3.7 sonnet': 'claude2',
                'gemini 2.0 flash': 'gemini2flash',
                'grok-2': 'grok'
            },
            'reasoning': {
                None: 'pplx_reasoning',
                'r1': 'r1',
                'o3-mini': 'o3mini',
                'claude 3.7 sonnet': 'claude37sonnetthinking'
            },
            'deep research': {
                None: 'pplx_alpha'
            }
        }

        json_data = {
            'query_str': query,
            'params': {
                'attachments': [],
                'frontend_context_uuid': str(uuid4()),
                'frontend_uuid': str(uuid4()),
                'is_incognito': False,
                'language': 'en-US',
                'last_backend_uuid': None,
                'mode': 'concise' if mode == 'auto' else 'copilot',
                'model_preference': model_mapping.get(mode, {}).get(model, 'turbo'),
                'source': 'default',
                'sources': sources,
                'version': '2.18'
            }
        }

        resp = self.session.post(
            'https://www.perplexity.ai/rest/sse/perplexity_ask',
            json=json_data,
            stream=True
        )

        if stream:
            return self._stream_response(resp)
        else:
            return self._get_full_response(resp)

    def _stream_response(self, resp):
        """Stream response chunks"""
        for chunk in resp.iter_lines(delimiter=b'\r\n\r\n'):
            content = chunk.decode('utf-8')

            if content.startswith('event: message\r\n'):
                try:
                    json_str = content[len('event: message\r\ndata: '):]
                    content_json = json.loads(json_str)

                    # Try to extract text from blocks
                    if 'blocks' in content_json and content_json['blocks']:
                        for block in content_json['blocks']:
                            if 'text' in block:
                                yield block['text']

                    # Or from text field if it exists (final chunk)
                    elif 'text' in content_json:
                        text_data = json.loads(content_json['text'])
                        yield self._extract_answer_from_steps(text_data)

                except Exception:
                    continue

            elif content.startswith('event: end_of_stream\r\n'):
                return

    def _get_full_response(self, resp):
        """Get the complete response"""
        final_text = ""
        last_chunk = None

        for chunk in resp.iter_lines(delimiter=b'\r\n\r\n'):
            content = chunk.decode('utf-8')

            if content.startswith('event: message\r\n'):
                try:
                    json_str = content[len('event: message\r\ndata: '):]
                    content_json = json.loads(json_str)
                    last_chunk = content_json

                    # Extract text from blocks if available
                    if 'blocks' in content_json and content_json['blocks']:
                        for block in content_json['blocks']:
                            if 'text' in block:
                                final_text = block['text']

                except Exception:
                    continue

            elif content.startswith('event: end_of_stream\r\n'):
                # Try to get text from the last chunk's 'text' field
                if last_chunk and 'text' in last_chunk:
                    try:
                        text_data = json.loads(last_chunk['text'])
                        answer = self._extract_answer_from_steps(text_data)
                        if answer:
                            return answer
                    except Exception:
                        pass

                # Otherwise return what we got from blocks
                return final_text if final_text else "No answer received"

        return final_text if final_text else "No answer received"

    def _extract_answer_from_steps(self, steps):
        """Extract the answer text from the steps data structure"""
        if not isinstance(steps, list):
            return ""

        # Look for FINAL step (the answer is in the FINAL step, not ANSWER step)
        for step in steps:
            if isinstance(step, dict) and step.get('step_type') == 'FINAL':
                content = step.get('content', {})
                if 'answer' in content:
                    # The answer field is a JSON string, parse it
                    try:
                        answer_data = json.loads(content['answer'])
                        if isinstance(answer_data, dict) and 'answer' in answer_data:
                            return answer_data['answer']
                    except:
                        # If parsing fails, return raw answer
                        return content['answer']

        return ""


# Convenience function
def search(query, mode='auto', model=None, sources=None):
    """Quick search function"""
    client = PerplexityFixed()
    return client.search(query, mode=mode, model=model, sources=sources)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python perplexity_fixed.py \"your question\"")
        sys.exit(1)

    question = sys.argv[1]
    print(f"\n🔍 Querying: {question}\n")

    answer = search(question)
    print("=" * 80)
    print("ANSWER:")
    print("=" * 80)
    print(answer)
    print("=" * 80)
