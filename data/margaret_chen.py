"""
Synthetic demo data for CIRCLE of Care.

"Margaret Chen" is a fictional care recipient invented for this demo.
No real patient, family, or facility data appears anywhere in this file
or anywhere else in this repository. See scripts/check_no_real_data.py
for the pre-deploy safety gate that guards against real data leaking in.
"""

SYNTHETIC_DATA_BADGE = "Demo dataset — synthetic family, no real patient data"

# ---------------------------------------------------------------------------
# Sample discharge / verbal care instructions — pre-filled into the
# translator text box. Deliberately mirrors the burden-audit categories
# named in the design doc: crimp-container instructions, fridge-timing
# instructions, 4x/day medication schedule, 4-hourly repositioning, and
# Handivan/Catholic Charities transport prep.
# ---------------------------------------------------------------------------
SAMPLE_DISCHARGE_INSTRUCTIONS = """\
Margaret Chen — Discharge Instructions (Home Care Summary)

MEDICATIONS
- Furosemide 20mg: take by mouth four times daily with food (breakfast, \
lunch, dinner, and before bed).
- Lisinopril: dosage per pharmacy label, once daily in the morning.

WOUND / DRAINAGE CARE
- Keep the wound dressing dry at all times.
- Crimp the drainage container's tubing clamp shut before Margaret \
showers or transfers, to prevent leakage.
- Empty and record drainage output each morning.

NUTRITION
- Prepared meals should be removed from the refrigerator about 30 \
minutes before serving so they reach room temperature.
- Do not microwave the pureed meals — it changes the texture.

POSITIONING
- Reposition Margaret (turn / wedge) every 4 hours while she is in bed, \
to prevent pressure sores. Alternate: left side, back, right side.

TRANSPORT
- Handivan pickup through Catholic Charities requires 24-hour advance \
booking.
- Have Margaret ready at the door with her rollator 10 minutes before \
the scheduled pickup time.
"""

# ---------------------------------------------------------------------------
# Care Rhythm timeline — synthetic care-log events for the LIVE timeline
# tab. Covers a representative ~30-hour window across the same five
# categories as the sample instructions above.
# ---------------------------------------------------------------------------
CARE_LOG_TIMELINE = [
    {"time": "2026-07-27 07:05", "category": "Medication", "event": "Furosemide 20mg administered with breakfast", "status": "Completed"},
    {"time": "2026-07-27 07:20", "category": "Wound Care", "event": "Drainage output emptied and recorded (32 mL)", "status": "Completed"},
    {"time": "2026-07-27 08:00", "category": "Medication", "event": "Lisinopril administered (AM dose)", "status": "Completed"},
    {"time": "2026-07-27 09:00", "category": "Positioning", "event": "Repositioned — left side", "status": "Completed"},
    {"time": "2026-07-27 11:00", "category": "Nutrition", "event": "Lunch removed from fridge for warm-up window", "status": "Completed"},
    {"time": "2026-07-27 11:35", "category": "Medication", "event": "Furosemide 20mg administered with lunch", "status": "Completed"},
    {"time": "2026-07-27 13:00", "category": "Positioning", "event": "Repositioned — back", "status": "Completed"},
    {"time": "2026-07-27 14:15", "category": "Transport", "event": "Handivan pickup confirmed for 07-28 09:00 (Catholic Charities)", "status": "Completed"},
    {"time": "2026-07-27 17:00", "category": "Positioning", "event": "Repositioned — right side", "status": "Completed"},
    {"time": "2026-07-27 18:05", "category": "Medication", "event": "Furosemide 20mg administered with dinner", "status": "Completed"},
    {"time": "2026-07-27 21:00", "category": "Positioning", "event": "Repositioned — left side", "status": "Completed"},
    {"time": "2026-07-27 21:40", "category": "Medication", "event": "Furosemide 20mg administered before bed", "status": "Completed"},
    {"time": "2026-07-27 22:10", "category": "Wound Care", "event": "Drainage clamp crimped shut ahead of overnight rest", "status": "Completed"},
    {"time": "2026-07-28 01:00", "category": "Positioning", "event": "Repositioned — back", "status": "Completed"},
    {"time": "2026-07-28 05:00", "category": "Positioning", "event": "Repositioned — right side", "status": "Completed"},
    {"time": "2026-07-28 07:10", "category": "Medication", "event": "Furosemide 20mg administered with breakfast", "status": "Completed"},
    {"time": "2026-07-28 07:25", "category": "Wound Care", "event": "Drainage clamp crimped open, dressing checked dry", "status": "Completed"},
    {"time": "2026-07-28 08:50", "category": "Transport", "event": "Rollator staged at door ahead of Handivan pickup", "status": "In progress"},
    {"time": "2026-07-28 09:00", "category": "Transport", "event": "Handivan pickup (Catholic Charities) — clinic appointment", "status": "Scheduled"},
    {"time": "2026-07-28 12:00", "category": "Medication", "event": "Furosemide 20mg — lunch dose", "status": "Scheduled"},
]
