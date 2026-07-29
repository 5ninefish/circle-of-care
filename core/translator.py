"""
The instruction translator — the core new capability of CIRCLE of Care.

Thin LLM wrapper (Anthropic API, Haiku-tier — cheapest capable model) that
converts free-text care instructions into a structured JSON schedule.

Safety guardrails (all required by the design doc, Codex adoption #4):
  - Verbatim source text is always displayed beside the structured result
    (handled in ui/dashboard.py, not here).
  - NO dose/frequency inference: the system prompt instructs the model to
    leave a field null and flag it rather than guess.
  - Every result carries a per-item confidence + flags list so the UI can
    show an uncertainty badge on low-confidence parses.
  - A confirmation step happens in the UI before any schedule is treated
    as "live" — this module never marks anything confirmed.

Failure modes handled here, all with a graceful fallback (never a stack
trace to the user):
  - LLM timeout / 5xx / connection error -> canned-examples fallback.
  - Malformed JSON -> retry once -> canned-examples fallback.
  - Session/day spend guard trips are handled by core.session_guard and
    checked by the caller before invoking this module's live path.
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

import anthropic

from data.canned_examples import CANNED_PRIMARY_RESULT

MODEL_ID = "claude-haiku-4-5"
REQUEST_TIMEOUT_SECONDS = 15.0
MAX_TOKENS = 1536

SYSTEM_PROMPT = """You are a care-instruction structuring assistant inside a home-care \
coordination tool. Convert the caregiver's verbal or discharge instructions into a \
structured JSON schedule.

CRITICAL SAFETY RULE: Never invent, guess, or infer a medication dose, frequency, or \
timing that is not explicitly stated in the source text. If a detail is missing, \
ambiguous, or conditional, leave the corresponding field null and add a short string \
to "flags" describing exactly what is missing or ambiguous — this keeps the caregiver \
and the recipient's actual clinician in the loop rather than the model guessing.

Respond with ONLY valid JSON, no prose, no markdown code fences, matching exactly \
this shape:

{
  "items": [
    {
      "task": "<short description of the task>",
      "category": "<one of: medication, repositioning, dietary, transport, other>",
      "frequency": "<string, or null if not stated>",
      "timing": "<string, or null if not stated>",
      "notes": "<string, or null>",
      "confidence": "<high, medium, or low>",
      "flags": ["<short string per missing/ambiguous detail>"]
    }
  ]
}

Set "confidence" to "low" whenever you had to leave any field null, and to "medium" \
when the instruction is understandable but has a conditional or judgment-call element \
a caregiver would want a clinician to confirm. Use "high" only when the instruction is \
fully explicit."""

RETRY_NUDGE = "\n\nYour previous response was not valid JSON. Respond again with ONLY the JSON object, no other text."


@dataclass
class TranslationResult:
    outcome: str  # "live" | "canned" | "error"
    items: list = field(default_factory=list)
    message: str = ""
    uncertain: bool = False
    source_text: str = ""


def _client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic(api_key=api_key)


def _extract_json(raw_text: str) -> dict:
    """Strip markdown fences if present, then parse. Raises on failure."""
    text = raw_text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()
    return json.loads(text)


def _validate_shape(parsed: dict) -> list:
    """Minimal shape check. Raises ValueError if the schema is off."""
    items = parsed.get("items")
    if not isinstance(items, list):
        raise ValueError("missing 'items' list")
    for item in items:
        if "task" not in item or "category" not in item:
            raise ValueError("item missing required fields")
        item.setdefault("frequency", None)
        item.setdefault("timing", None)
        item.setdefault("notes", None)
        item.setdefault("confidence", "medium")
        item.setdefault("flags", [])
    return items


def _call_once(source_text: str, extra_user_suffix: str = "") -> list:
    client = _client()
    response = client.with_options(timeout=REQUEST_TIMEOUT_SECONDS).messages.create(
        model=MODEL_ID,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Structure the following care instructions:\n\n{source_text}{extra_user_suffix}",
            }
        ],
    )
    raw_text = "".join(block.text for block in response.content if block.type == "text")
    parsed = _extract_json(raw_text)
    return _validate_shape(parsed)


def _is_uncertain(items: list) -> bool:
    return any(
        item.get("confidence") != "high" or item.get("flags")
        for item in items
    )


def translate_live(source_text: str) -> TranslationResult:
    """
    Attempts a live LLM translation. Never raises — always returns a
    TranslationResult, falling back to the canned example on any failure
    (timeout, 5xx/overload, or JSON that stays malformed after one retry).
    """
    # Attempt 1
    try:
        items = _call_once(source_text)
        return TranslationResult(
            outcome="live",
            items=items,
            message="Structured from your text just now.",
            uncertain=_is_uncertain(items),
            source_text=source_text,
        )
    except (json.JSONDecodeError, ValueError):
        pass  # fall through to retry-once path below
    except (
        anthropic.APITimeoutError,
        anthropic.APIConnectionError,
        anthropic.InternalServerError,
        anthropic.RateLimitError,
    ):
        return _canned_fallback(
            source_text,
            "The translator is temporarily unavailable (the AI service didn't respond in time). "
            "Showing a representative example instead — your text was not lost, try again in a moment.",
        )
    except anthropic.APIStatusError as exc:
        if exc.status_code >= 500:
            return _canned_fallback(
                source_text,
                "The translator hit a server error. Showing a representative example instead.",
            )
        return _canned_fallback(
            source_text,
            "The translator couldn't process that request. Showing a representative example instead.",
        )
    except RuntimeError:
        return _canned_fallback(
            source_text,
            "The translator isn't configured with an API key in this environment. "
            "Showing a representative example instead.",
        )

    # Retry once on malformed JSON
    try:
        items = _call_once(source_text, extra_user_suffix=RETRY_NUDGE)
        return TranslationResult(
            outcome="live",
            items=items,
            message="Structured from your text just now (second attempt).",
            uncertain=_is_uncertain(items),
            source_text=source_text,
        )
    except Exception:
        return _canned_fallback(
            source_text,
            "The translator's response couldn't be parsed after a retry. "
            "Showing a representative example instead.",
        )


def _canned_fallback(source_text: str, message: str) -> TranslationResult:
    items = CANNED_PRIMARY_RESULT["items"]
    return TranslationResult(
        outcome="canned",
        items=items,
        message=message,
        uncertain=_is_uncertain(items),
        source_text=source_text,
    )


def canned_result(source_text: str, message: str) -> TranslationResult:
    """Public helper for callers that already decided to skip the live path
    (session limit / daily cap) and want the canned example directly."""
    return _canned_fallback(source_text, message)
