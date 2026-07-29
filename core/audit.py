"""
Append-only audit log for the current Streamlit session.

Per Codex adoption #5 in the design doc: call it "append-only," never
"immutable" — this is an in-session log, not a cryptographic ledger.
"""

from datetime import datetime

import streamlit as st

_STATE_KEY = "audit_log"


def _ensure_log() -> list:
    if _STATE_KEY not in st.session_state:
        st.session_state[_STATE_KEY] = []
    return st.session_state[_STATE_KEY]


def log_action(action: str, detail: str = "") -> None:
    """Append one entry. Never mutates or removes prior entries."""
    entries = _ensure_log()
    entries.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "detail": detail,
        }
    )


def get_entries() -> list:
    return list(_ensure_log())


def entry_count() -> int:
    return len(_ensure_log())
