"""
Triple spend guard for the instruction translator, per the CIRCLE of Care
design doc (Distribution Plan -> Access + spend guard):

  1. Cheapest capable model (handled in core/translator.py — Haiku-tier).
  2. Per-session rate limit (~5 translations) — this file.
  3. Hard daily spend cap that flips the widget to precomputed examples —
     this file, backed by a small local counter file (not a database;
     fine for a demo instance).

Rationale: public live LLM endpoints are open wallets. All three layers
degrade gracefully to the canned-examples fallback rather than erroring.
"""

import json
import os
from datetime import date
from pathlib import Path

import streamlit as st

SESSION_TRANSLATION_LIMIT = 5
DAILY_CALL_CAP = int(os.environ.get("CIRCLE_DAILY_CALL_CAP", "200"))

_COUNTER_PATH = Path(__file__).resolve().parent.parent / "data" / ".daily_call_count.json"


# ---------------------------------------------------------------------------
# Per-session limit (in-memory, resets each Streamlit session)
# ---------------------------------------------------------------------------
def get_session_translation_count() -> int:
    return st.session_state.get("translation_count", 0)


def increment_session_translation_count() -> None:
    st.session_state["translation_count"] = get_session_translation_count() + 1


def session_limit_reached() -> bool:
    return get_session_translation_count() >= SESSION_TRANSLATION_LIMIT


# ---------------------------------------------------------------------------
# Daily cap (persisted to a small local JSON counter file, date-scoped)
# ---------------------------------------------------------------------------
def _read_counter() -> dict:
    today = date.today().isoformat()
    if not _COUNTER_PATH.exists():
        return {"date": today, "count": 0}
    try:
        data = json.loads(_COUNTER_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return {"date": today, "count": 0}
    if data.get("date") != today:
        return {"date": today, "count": 0}
    return data


def _write_counter(data: dict) -> None:
    try:
        _COUNTER_PATH.parent.mkdir(parents=True, exist_ok=True)
        _COUNTER_PATH.write_text(json.dumps(data))
    except OSError:
        pass  # non-fatal — worst case the daily cap under-counts for this run


def get_daily_call_count() -> int:
    return _read_counter().get("count", 0)


def increment_daily_call_count() -> None:
    data = _read_counter()
    data["count"] = data.get("count", 0) + 1
    _write_counter(data)


def daily_cap_reached() -> bool:
    return get_daily_call_count() >= DAILY_CALL_CAP


# ---------------------------------------------------------------------------
# Combined check
# ---------------------------------------------------------------------------
def guard_status() -> dict:
    """Single call for the UI to check before attempting a live translation."""
    return {
        "session_count": get_session_translation_count(),
        "session_limit": SESSION_TRANSLATION_LIMIT,
        "session_limit_reached": session_limit_reached(),
        "daily_count": get_daily_call_count(),
        "daily_cap": DAILY_CALL_CAP,
        "daily_cap_reached": daily_cap_reached(),
    }
