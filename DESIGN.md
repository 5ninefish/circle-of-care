# Design System — CIRCLE of Care

## Product Context
- **What this is:** Phase 1 demo for the ACL Caregiver AI Challenge — an agentic
  AI care-coordination dashboard (Streamlit). Landing tab is an instruction
  translator; secondary tabs are Care Rhythm, Agent Console, Audit Log.
- **Who it's for:** An ACL judge reviewing a cold link with no domain context,
  ~3-5 minute tolerance, forming a one-sentence verdict.
- **Space/industry:** Caregiver coordination / health tech, adjacent to
  medication-reminder apps (Medisafe, Caring Village) but positioned against
  them — the product removes the orchestration task, not just reminds.
- **Project type:** Data-forward web dashboard (Streamlit), not a marketing site.

## Aesthetic Direction
- **Direction:** Restrained Industrial-Organic — systems-forward, data-dense,
  credible layout crossed with a warm, earthy (non-clinical) color language.
- **Decoration level:** Minimal — typography, color, and spacing carry the
  system. No illustration, no stock photography.
- **Mood:** The core capability should read as real, working infrastructure —
  calm, not clinical or alarmist.
- **Reference sites:** caringvillage.com, trywarm.app (visual research only —
  CIRCLE of Care deliberately departs from the category's warm-photography
  convention; see Decisions Log).

## Typography
- **Display/Hero:** Fraunces — warm humanist serif, used ONLY at headline
  scale. Every category competitor uses a geometric sans; a serif at hero
  scale is the fastest signal this isn't another reminder app.
- **Body:** Source Sans 3 — clean, legible, generous at reading size, doesn't
  compete with the display serif.
- **UI/Labels:** Source Sans 3 (same as body).
- **Data/Tables:** IBM Plex Mono, used narrowly on timestamps, entry IDs, and
  JSON/structured fields (Audit Log, translator output) — never paragraph
  text. Signals "real log," not a designed mockup.
- **Code:** IBM Plex Mono.
- **Loading:** Google Fonts CDN —
  `Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600` +
  `Source+Sans+3:wght@400;500;600;700` + `IBM+Plex+Mono:wght@400;500`.
- **Scale:** hero 40-64px (clamp), section heading 28px, body 15-17px,
  label/mono 11-13px.

## Color
- **Approach:** Restrained — one accent, one supporting state color, warm
  neutrals.
- **Primary/accent:** `#B5563C` (clay/terracotta) — Translate CTA, active tab,
  primary buttons.
- **Secondary:** `#5B7A5B` (sage) — Sentinel Vigilance "LIVE" status, success
  states, confirmed checklist items.
- **Semantic — uncertainty/flag:** `#C08A3E` (warm amber) — deliberately
  replaces red. A flagged item should read "confirm this," not "emergency."
- **Neutrals:** `#FAF7F2` (cream, background) → `#3A342E` (charcoal, text);
  warm throughout, never cool hospital blue-gray.
- **Dark mode:** Redesign surfaces (`#211D19` bg / `#2E2924` surface /
  `#F1ECE3` text), tint colors desaturated ~15-20% against the dark surface
  rather than reused at full saturation.

## Spacing
- **Base unit:** 8px.
- **Density:** Comfortable — generous enough to feel calm, tight enough to
  scan the whole screen in one view.
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48) 3xl(64).

## Layout
- **Approach:** Grid-disciplined — leans into Streamlit's native tab/column
  structure rather than fighting it.
- **Grid:** Single-column content within each tab, max content width below;
  card grids auto-fit at `minmax(220-260px, 1fr)`.
- **Max content width:** 1080px.
- **Border radius:** sm 4px (buttons, inputs), md 8px (agent cards), lg 12px
  (containers/mockup panels). No uniform bubbly radius.

## Motion
- **Approach:** Minimal-functional. Streamlit gives limited room for custom
  JS motion; keep to CSS transitions only.
- **Easing:** enter(ease-out) exit(ease-in) move(ease-in-out).
- **Duration:** micro(50-100ms) short(150-250ms) medium(250-400ms).
- **Signature moment:** the "Got it — structuring this into a care
  schedule…" instant-ack uses a subtle pulsing dot (1.6s ease-in-out loop) —
  the one deliberate animation in the system, required by the DX review's
  instant-ack rule (D7).

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-07-28 | Initial design system created | Created by `/design-consultation`. Direction: Restrained Industrial-Organic. Memorable-thing brief: "the capability is real, and it feels calm, not clinical." |
| 2026-07-28 | Zero photography/illustration | Breaks from the caregiver-app category norm (Caring Village, Warm both lead with warm lifestyle photos) — avoids any synthetic-data ambiguity risk and lets the translator moment itself carry the emotional weight instead of stock imagery. |
| 2026-07-28 | Amber, not red, for uncertainty/flags | A flagged instruction should read as "needs your confirmation," never as an alarm — keeps the system in the calm/administrative-support register, not clinical-emergency. |
| 2026-07-28 | Serif hero type in an all-sans category | Fastest available signal of differentiation from the "reminder app" competitive set, used narrowly (headline scale only) to avoid legibility cost at small sizes. |
| 2026-07-28 | No default OS/browser emoji anywhere in the app | Colorful emoji (tab icons, status circles, flag markers) read as cheap against the restrained serif/mono system. Replaced with plain text labels, palette-colored dot glyphs (`●`/`○` in sage/muted), and pill-badge spans (`.pill-amber`/`.pill-sage`) styled with the exact DESIGN.md hex values instead. |
