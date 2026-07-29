"""
Precomputed (canned) translator outputs.

Used whenever the live LLM path is unavailable: timeout/5xx, malformed
JSON after one retry, per-session rate limit hit, or the daily spend cap
tripped. Keeps the demo working end-to-end with zero live API risk.

Each entry follows the same schema the live translator returns:
    {"items": [ {task, category, frequency, timing, notes,
                 confidence, flags[]}, ... ]}
"""

# The precomputed translation of data.margaret_chen.SAMPLE_DISCHARGE_INSTRUCTIONS.
# Shown as the fallback result whenever the box still contains (or closely
# matches) the pre-filled sample text.
CANNED_PRIMARY_RESULT = {
    "items": [
        {
            "task": "Take Furosemide 20mg by mouth",
            "category": "medication",
            "frequency": "4x daily",
            "timing": "With breakfast, lunch, dinner, and before bed",
            "notes": "Take with food.",
            "confidence": "high",
            "flags": [],
        },
        {
            "task": "Take Lisinopril",
            "category": "medication",
            "frequency": "1x daily",
            "timing": "Morning",
            "notes": None,
            "confidence": "low",
            "flags": ["Dosage not stated in source text — check pharmacy label before administering."],
        },
        {
            "task": "Crimp drainage container tubing clamp shut before shower or transfer",
            "category": "other",
            "frequency": "Before each shower/transfer",
            "timing": None,
            "notes": "Prevents leakage.",
            "confidence": "high",
            "flags": [],
        },
        {
            "task": "Empty and record wound drainage output",
            "category": "other",
            "frequency": "Daily",
            "timing": "Each morning",
            "notes": None,
            "confidence": "high",
            "flags": [],
        },
        {
            "task": "Remove prepared meals from refrigerator before serving",
            "category": "dietary",
            "frequency": None,
            "timing": "~30 minutes before serving",
            "notes": "Do not microwave pureed meals — changes texture.",
            "confidence": "high",
            "flags": [],
        },
        {
            "task": "Reposition (turn/wedge) while in bed",
            "category": "repositioning",
            "frequency": "Every 4 hours",
            "timing": None,
            "notes": "Alternate: left side, back, right side.",
            "confidence": "high",
            "flags": [],
        },
        {
            "task": "Book Handivan pickup (Catholic Charities)",
            "category": "transport",
            "frequency": None,
            "timing": "24 hours in advance of the ride",
            "notes": "Have recipient ready at the door with rollator 10 minutes before pickup.",
            "confidence": "medium",
            "flags": ["Exact pickup time not specified in source text — confirm per booking."],
        },
    ]
}

# Three canned instruction -> checklist pairs, used for the TRL-style
# "representative outputs" fallback when a caller wants variety (e.g. after
# the daily cap trips) rather than just re-showing the primary example.
CANNED_EXAMPLES = [
    {
        "source_text": "Give the water pill twice a day, once when she wakes up and once "
                        "around dinnertime. Skip the evening dose if her ankles aren't swollen.",
        "result": {
            "items": [
                {
                    "task": "Give diuretic ('water pill')",
                    "category": "medication",
                    "frequency": "2x daily",
                    "timing": "On waking and around dinnertime",
                    "notes": "Evening dose is conditional on ankle swelling.",
                    "confidence": "low",
                    "flags": [
                        "Medication name and dose not specified — confirm with pharmacy label before administering.",
                        "Conditional dosing rule ('skip if not swollen') requires a caregiver judgment call — flag for clinician confirmation.",
                    ],
                }
            ]
        },
    },
    {
        "source_text": "Aide needs to help with the standing pivot transfer every time, and "
                        "check the oxygen tank level before each outing.",
        "result": {
            "items": [
                {
                    "task": "Assist with standing pivot transfer",
                    "category": "other",
                    "frequency": "Every transfer",
                    "timing": None,
                    "notes": None,
                    "confidence": "high",
                    "flags": [],
                },
                {
                    "task": "Check oxygen tank level",
                    "category": "other",
                    "frequency": "Before each outing",
                    "timing": None,
                    "notes": None,
                    "confidence": "high",
                    "flags": [],
                },
            ]
        },
    },
    {
        "source_text": "Call the on-call nurse line if temperature goes above normal, and "
                        "log any missed meals in the binder by the kitchen.",
        "result": {
            "items": [
                {
                    "task": "Call on-call nurse line",
                    "category": "other",
                    "frequency": None,
                    "timing": "If temperature rises above normal",
                    "notes": None,
                    "confidence": "low",
                    "flags": ["'Above normal' has no numeric threshold in source text — flag for clinician confirmation."],
                },
                {
                    "task": "Log any missed meals in the kitchen binder",
                    "category": "dietary",
                    "frequency": "As needed",
                    "timing": None,
                    "notes": None,
                    "confidence": "high",
                    "flags": [],
                },
            ]
        },
    },
]
