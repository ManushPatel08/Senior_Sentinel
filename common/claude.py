"""The Claude API client shared by the scam judge, the "Why?" explainer and the scam radar.

Every text model call goes to Claude. Grok Voice stays on xAI (relay/tokens.py mints the station's voice tokens, the
Senior Sentinel Line runs in xAI's Voice Agent Builder, ai/render_clips.py renders the spoken clips with xAI TTS).

Env: ANTHROPIC_API_KEY.
"""

from __future__ import annotations

from functools import lru_cache

from common.config import env

MODEL = "claude-opus-5-5"
# A safety-classifier decline is re-run server-side on the model Anthropic picks for that category, so a false
# positive on a scam story costs a retry instead of an answer. Needs client.beta.messages.
FALLBACK = {"betas": ["server-side-fallback-2026-07-01"], "fallbacks": "default"}


class MissingKey(RuntimeError):
    """ANTHROPIC_API_KEY is not set."""


@lru_cache(maxsize=1)
def client():
    import anthropic

    key = env("ANTHROPIC_API_KEY")
    if not key:
        raise MissingKey("ANTHROPIC_API_KEY is not set")
    # Callers hold hard deadlines and fall back on their own, so a retry would only spend the budget.
    return anthropic.Anthropic(api_key=key, max_retries=0)


def reply_text(resp) -> str:
    """The text of a structured-output reply; raises ValueError when Claude declined or was cut off."""
    if resp.stop_reason == "refusal":
        raise ValueError("Claude declined")
    if resp.stop_reason == "max_tokens":
        raise ValueError("reply cut off at max_tokens")
    return "".join(b.text for b in resp.content if b.type == "text")
