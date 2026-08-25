"""API key validation.

The key is never stored in this repository, never written to a .env file and
never hardcoded. It is typed into a password field at run time, checked once
against the Claude API, and held only for the life of the session.
"""

from __future__ import annotations

import anthropic

# One cheap call proves the key works before the lab spends real tokens on it.
VALIDATION_MODEL = "claude-haiku-4-5"


def validate_anthropic_key(api_key: str) -> str:
    """Return "Valid API Key!" or a message explaining why it was rejected."""
    if not api_key or not api_key.strip():
        return "Invalid - please enter your Anthropic API key."

    try:
        client = anthropic.Anthropic(api_key=api_key.strip())
        client.messages.create(
            model=VALIDATION_MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        return "Valid API Key!"

    except anthropic.AuthenticationError:
        return "Invalid API Key - the key was rejected by Anthropic."
    except anthropic.PermissionDeniedError:
        return "Invalid - this key does not have permission to call the Messages API."
    except anthropic.RateLimitError:
        # The key itself is fine; the account is simply busy.
        return "Valid API Key!"
    except anthropic.APIConnectionError:
        return "Invalid - could not reach the Anthropic API. Check your connection."
    except anthropic.APIStatusError as exc:
        return f"Invalid - Anthropic returned {exc.status_code}."
