# CIRCLE of Care

Phase 1 demo for the ACL Caregiver AI Challenge. Agentic AI care coordination
layer — the wedge: translating verbal/discharge care instructions into a
structured, confirmable daily schedule, with an append-only audit trail and
a live "second pair of eyes" (Sentinel Vigilance) agent.

All data in this demo is synthetic ("Margaret Chen," a fictional care
recipient). No real family data appears anywhere in this repository — see
`scripts/check_no_real_data.py`.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add an Anthropic API key (needed for the
live translator; without it the app still runs end-to-end using the
built-in canned-example fallback):

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
streamlit run ui/dashboard.py
```

Opens at http://localhost:8501. No login required.

## What's here

- `ui/dashboard.py` — the Streamlit app. Landing tab is the instruction
  translator; Care Rhythm, Agent Console, and Audit Log are secondary tabs.
- `core/translator.py` — the LLM wrapper (Anthropic `claude-haiku-4-5`).
  No dose/frequency inference — ambiguous or missing details are flagged,
  never guessed. Handles timeout/5xx and malformed-JSON failure modes by
  falling back to a precomputed example.
- `core/session_guard.py` — triple spend guard: cheapest capable model,
  a 5-translations-per-session limit, and a daily call cap (env var
  `CIRCLE_DAILY_CALL_CAP`, default 200) that flips the whole widget to
  precomputed examples once tripped.
- `core/audit.py` — append-only in-session audit log.
- `data/margaret_chen.py` — synthetic sample discharge instructions and a
  synthetic Care Rhythm timeline.
- `data/canned_examples.py` — precomputed translator outputs used by every
  fallback path.
- `scripts/check_no_real_data.py` — the data-safety gate. Run before every
  deploy:
  ```bash
  cp scripts/denylist.example.txt scripts/denylist.txt   # then fill in real identifiers
  python3 scripts/check_no_real_data.py
  ```
  `scripts/denylist.txt` is gitignored — never commit it.

## Not in scope for Phase 1

Login/auth (none — ACL's rules require no-login public links), real
integrations (SMS to aides, Handivan booking, smart-home bridge), voice
interface, CI/CD. Circle-Orchestrator, Empathy Buffer, and Baselines
Extractor are shown as labeled Phase 2 roadmap cards in the Agent Console,
not implemented.
