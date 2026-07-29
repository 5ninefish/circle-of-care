"""
CIRCLE of Care — Streamlit demo dashboard.

Run: streamlit run ui/dashboard.py

Landing view IS the instruction translator (design doc D3 "Champion
Landing") — everything else lives in secondary tabs. No login (D7 — ACL's
official rules require externally accessible links with no login gate).
Synthetic data only (Margaret Chen, fictional).
"""

import sys
from pathlib import Path

# Make the repo root importable regardless of Streamlit's script-relative sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # picks up ANTHROPIC_API_KEY from a local .env if present

from core import audit, session_guard
from core.translator import translate_live, canned_result
from data.margaret_chen import (
    SYNTHETIC_DATA_BADGE,
    SAMPLE_DISCHARGE_INSTRUCTIONS,
    CARE_LOG_TIMELINE,
)

FOOTER_TEXT = "Organizes instructions from your care team. Not medical advice. Verify changes with your provider."

st.set_page_config(page_title="CIRCLE of Care", page_icon="🌀", layout="wide")

# Design system per DESIGN.md — Restrained Industrial-Organic. Fraunces for
# hero/headline scale only, Source Sans 3 for body/UI, IBM Plex Mono for
# data fields (audit log, structured output). Amber replaces red for
# uncertainty flags — a flag should read "confirm this," not "emergency."
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --cream: #FAF7F2;
        --cream-dim: #F1ECE3;
        --charcoal: #3A342E;
        --charcoal-soft: #6B6259;
        --line: #E4DCCE;
        --clay: #B5563C;
        --clay-deep: #9A4530;
        --sage: #5B7A5B;
        --sage-tint: #E4EBE1;
        --amber: #C08A3E;
        --amber-tint: #F6E9D3;
    }

    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--cream);
    }
    html, body, [class*="css"] {
        font-family: 'Source Sans 3', -apple-system, sans-serif;
        color: var(--charcoal);
    }
    [data-testid="stMainBlockContainer"] { padding-top: 2.5rem; }

    /* Hero title — Fraunces, headline scale only */
    h1 {
        font-family: 'Fraunces', Georgia, serif !important;
        font-weight: 500 !important;
        color: var(--charcoal) !important;
        letter-spacing: -0.01em;
    }
    h2, h3 { color: var(--charcoal) !important; }
    [data-testid="stCaptionContainer"], .stCaption, small {
        color: var(--charcoal-soft) !important;
    }

    /* Buttons — flat clay, no gradients */
    .stButton button, .stButton button[kind="primary"], button[kind="primary"] {
        background-color: var(--clay);
        color: #FFFFFF;
        border: 1px solid var(--clay);
        border-radius: 4px;
        font-weight: 600;
    }
    .stButton button:hover, button[kind="primary"]:hover {
        background-color: var(--clay-deep);
        border-color: var(--clay-deep);
        color: #FFFFFF;
    }
    .stButton button[kind="secondary"], button[kind="secondary"] {
        background-color: transparent;
        color: var(--clay);
        border: 1px solid var(--clay);
        border-radius: 4px;
    }

    /* Tabs — active tab underlined in clay */
    [data-baseweb="tab-list"] { border-bottom: 1px solid var(--line); gap: 1.5rem; }
    [data-baseweb="tab"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        color: var(--charcoal-soft);
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: var(--clay) !important;
        border-bottom-color: var(--clay) !important;
    }
    [data-baseweb="tab-highlight"] { background-color: var(--clay) !important; }

    /* Bordered containers (agent cards, checklist items) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line) !important;
        border-radius: 8px !important;
        background-color: #FFFFFF;
    }

    /* Alerts — amber for uncertainty, never red; sage for success */
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
        background-color: var(--amber-tint) !important;
        border-radius: 8px;
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
        background-color: var(--sage-tint) !important;
        border-radius: 8px;
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
        background-color: var(--cream-dim) !important;
        border-radius: 8px;
    }
    [data-testid="stAlertContentWarning"] p, [data-testid="stAlertContentSuccess"] p, [data-testid="stAlertContentInfo"] p {
        color: var(--charcoal) !important;
    }

    /* Data fields — mono, reinforces "this is a real log" */
    [data-testid="stDataFrame"], [data-testid="stDataFrame"] * {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stTextArea"] textarea {
        background-color: var(--cream-dim);
        border-color: var(--line);
        border-radius: 8px;
        font-family: 'Source Sans 3', sans-serif;
    }

    hr, [data-testid="stDivider"] { border-color: var(--line) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

CATEGORY_LABELS = {
    "medication": "Medication",
    "repositioning": "Repositioning",
    "dietary": "Dietary",
    "transport": "Transport",
    "other": "Other",
}


# ---------------------------------------------------------------------------
# Header — shown above every tab
# ---------------------------------------------------------------------------
st.title("CIRCLE of Care")
st.caption("Agentic AI care coordination — removes the mechanical orchestration from the caregiver, not just reminds them.")
st.info(SYNTHETIC_DATA_BADGE, icon="🔒")

tab_translate, tab_rhythm, tab_agents, tab_audit = st.tabs(
    ["🔀 Translator", "📅 Care Rhythm", "🤖 Agent Console", "🧾 Audit Log"]
)


# ---------------------------------------------------------------------------
# TAB 1 — Instruction Translator (the landing view / the whole $100K argument)
# ---------------------------------------------------------------------------
with tab_translate:
    st.subheader("Instruction Translator")
    st.markdown(
        "Paste (or edit) verbal or discharge instructions from a care team below, "
        "then click **Translate**. The result is a structured schedule your aides "
        "and family can actually follow — not another reminder app."
    )

    if "source_text" not in st.session_state:
        st.session_state["source_text"] = SAMPLE_DISCHARGE_INSTRUCTIONS

    source_text = st.text_area(
        "Care instructions",
        key="source_text",
        height=260,
        label_visibility="collapsed",
    )

    guard = session_guard.guard_status()
    col_btn, col_status = st.columns([1, 3])
    with col_btn:
        translate_clicked = st.button("Translate ➜", type="primary", use_container_width=True)
    with col_status:
        st.caption(
            f"Session translations used: {guard['session_count']}/{guard['session_limit']}"
        )

    if translate_clicked:
        text_to_translate = st.session_state["source_text"].strip()
        if not text_to_translate:
            st.warning("Paste some instructions first.")
        else:
            with st.status("Got it — structuring this into a care schedule…", expanded=False) as status_box:
                if session_guard.daily_cap_reached():
                    result = canned_result(
                        text_to_translate,
                        "Today's demo capacity is fully used — showing a precomputed example so the demo keeps working.",
                    )
                    audit.log_action("Translate (daily cap reached)", "served precomputed example")
                elif session_guard.session_limit_reached():
                    result = canned_result(
                        text_to_translate,
                        f"You've reached the {session_guard.SESSION_TRANSLATION_LIMIT}-translation limit for this "
                        "session — here's a representative example instead. Refresh the page to start a new session.",
                    )
                    audit.log_action("Translate (session limit reached)", "served representative example")
                else:
                    session_guard.increment_session_translation_count()
                    session_guard.increment_daily_call_count()
                    result = translate_live(text_to_translate)
                    audit.log_action(
                        f"Translate ({result.outcome})",
                        f"{len(result.items)} item(s), uncertain={result.uncertain}",
                    )
                status_box.update(label="Done.", state="complete")

            st.session_state["last_result"] = result
            st.session_state["confirmed"] = False

    result = st.session_state.get("last_result")
    if result:
        if result.outcome == "canned":
            st.warning(result.message, icon="⚠️")
        elif result.message:
            st.caption(result.message)

        if result.uncertain:
            st.warning(
                "⚠️ Uncertainty flagged — one or more items are missing information "
                "or need clinician confirmation. See flags below.",
                icon="⚠️",
            )

        col_source, col_checklist = st.columns(2)

        with col_source:
            st.markdown("**Verbatim source text**")
            st.text_area(
                "Verbatim source",
                value=result.source_text,
                height=420,
                disabled=True,
                label_visibility="collapsed",
            )

        with col_checklist:
            st.markdown("**Structured care schedule**")
            for item in result.items:
                low_confidence = item.get("confidence") != "high" or item.get("flags")
                title = item.get("task", "Untitled task")
                badge = "🟡 needs confirmation" if low_confidence else "🟢 high confidence"
                with st.container(border=True):
                    st.markdown(f"**{title}**  \n{badge}")
                    meta_bits = []
                    cat = CATEGORY_LABELS.get(item.get("category"), item.get("category"))
                    if cat:
                        meta_bits.append(f"Category: {cat}")
                    if item.get("frequency"):
                        meta_bits.append(f"Frequency: {item['frequency']}")
                    if item.get("timing"):
                        meta_bits.append(f"Timing: {item['timing']}")
                    if meta_bits:
                        st.caption(" · ".join(meta_bits))
                    if item.get("notes"):
                        st.markdown(item["notes"])
                    for flag_text in item.get("flags", []):
                        st.markdown(f"🚩 {flag_text}")

        st.divider()
        confirmed = st.session_state.get("confirmed", False)
        if confirmed:
            st.success("Schedule confirmed — this is now the active care schedule.")
        else:
            if st.button("Confirm this schedule", type="secondary"):
                st.session_state["confirmed"] = True
                audit.log_action("Confirm schedule", f"{len(result.items)} item(s) confirmed by caregiver")
                st.rerun()
            st.caption("Nothing is treated as a live schedule until a caregiver confirms it.")


# ---------------------------------------------------------------------------
# TAB 2 — Care Rhythm timeline (LIVE, synthetic data)
# ---------------------------------------------------------------------------
with tab_rhythm:
    st.subheader("Care Rhythm — the recipient's care timeline")
    st.caption("Every completed, in-progress, and scheduled task across medication, wound care, positioning, diet, and transport.")
    st.dataframe(CARE_LOG_TIMELINE, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# TAB 3 — Agent Console
# ---------------------------------------------------------------------------
with tab_agents:
    st.subheader("Agent Console — the agents behind the scenes")
    st.caption("CIRCLE of Care is an agentic architecture, not a single chatbot. This console telegraphs the full design.")

    uncertain_count = 0
    last = st.session_state.get("last_result")
    if last:
        uncertain_count = sum(1 for i in last.items if i.get("confidence") != "high" or i.get("flags"))
    overdue_count = sum(1 for row in CARE_LOG_TIMELINE if row["status"] not in ("Completed", "Scheduled"))

    with st.container(border=True):
        st.markdown("### 🟢 Sentinel Vigilance — *LIVE*")
        st.caption("The second pair of eyes: watches the care schedule and the translator's own output for anything that needs a human look.")
        st.markdown(
            f"Currently watching **{len(CARE_LOG_TIMELINE)}** Care Rhythm entries and the latest translation. "
            f"**{overdue_count}** timeline item(s) in progress, **{uncertain_count}** translated item(s) flagged for confirmation."
        )

    st.markdown("#### Roadmap agents — Phase 2")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("### ⚪ Circle-Orchestrator")
            st.caption("Phase 2")
            st.markdown("Coordinates aides, transport (Handivan/Catholic Charities), and on-call contacts — the human dispatcher role, automated.")
    with col_b:
        with st.container(border=True):
            st.markdown("### ⚪ Empathy Buffer")
            st.caption("Phase 2")
            st.markdown("Smooths tone and framing across every message — shared coordination and dignity, never surveillance of care workers or the recipient.")
    with col_c:
        with st.container(border=True):
            st.markdown("### ⚪ Baselines Extractor")
            st.caption("Phase 2")
            st.markdown("Learns the recipient's normal patterns over time so Sentinel Vigilance can tell a real anomaly from a normal day.")


# ---------------------------------------------------------------------------
# TAB 4 — Audit log (append-only)
# ---------------------------------------------------------------------------
with tab_audit:
    st.subheader("Audit Log")
    entries = audit.get_entries()
    st.markdown(f"**Every action is logged — {audit.entry_count()} entries this session.**")
    if entries:
        st.dataframe(entries, use_container_width=True, hide_index=True)
    else:
        st.caption("No actions logged yet this session — try the Translator tab.")


# ---------------------------------------------------------------------------
# Persistent footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(FOOTER_TEXT)
