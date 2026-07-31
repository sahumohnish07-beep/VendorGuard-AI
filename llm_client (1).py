"""
llm_client.py — NVIDIA NIM (OpenAI-compatible) LLM wrapper
-------------------------------------------------------------
Used by Agent 3 to turn a rule-based decision into a natural-language
explanation, as described in the original spec ("With an LLM, you can
also generate natural-language explanations").

SECURITY: the API key is read from an environment variable — never
hardcode it in source. Set it before running:

    export NVIDIA_API_KEY="your-key-here"        (macOS/Linux)
    setx NVIDIA_API_KEY "your-key-here"           (Windows)

If the key isn't set, or the API call fails for any reason (no network,
rate limit, bad key, etc.), every function here fails soft and returns
None — the rest of the pipeline keeps working off the rule-based
explanation instead of the LLM one.
"""

import os

DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"
DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"

_client = None
_client_init_attempted = False


def _get_client():
    """Lazily create and cache the OpenAI-compatible client. Returns None
    if the SDK isn't installed or no API key is configured."""
    global _client, _client_init_attempted

    if _client_init_attempted:
        return _client
    _client_init_attempted = True

    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
        _client = OpenAI(base_url=DEFAULT_BASE_URL, api_key=api_key)
    except Exception:
        _client = None

    return _client


def is_available():
    """True if the LLM client is configured and importable."""
    return _get_client() is not None


def generate_explanation(prompt, model=DEFAULT_MODEL, max_tokens=200, temperature=0.2):
    """
    Send a prompt to the LLM and return plain text, or None on any failure
    (missing key, network error, rate limit, etc.) so callers can fall
    back to the rule-based explanation without crashing the pipeline.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            top_p=0.7,
            max_tokens=max_tokens,
            stream=False,
        )
        message = completion.choices[0].message
        if message is not None and message.content:
            return message.content.strip()
        return None
    except Exception:
        return None
