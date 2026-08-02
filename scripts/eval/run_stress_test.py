#!/usr/bin/env python3
"""
Phase 1 Data Output Log harness — runs the 40-case corpus (scripts/eval/corpus.py)
through the app's real instruction translator (core.translator.translate_live)
and scores each result against the expectations declared per-case.

This drives the SAME code path the deployed app uses (core/translator.py),
not a mock — the whole point is to evidence real system behavior.

Usage:
    ANTHROPIC_API_KEY=sk-ant-... python3 scripts/eval/run_stress_test.py

Output:
    scripts/eval/results/run_<UTC-timestamp>.jsonl   — one line per case
    scripts/eval/results/summary_<UTC-timestamp>.json — aggregate metrics

No network calls happen anywhere except the Anthropic API calls the
translator itself makes. No case text or model output is sent anywhere else.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from core.translator import translate_live, MODEL_ID  # noqa: E402
from scripts.eval.corpus import CORPUS  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def _field_values(items, field_name):
    return [item.get(field_name) for item in items]


def _any_null(items, field_name):
    return any(item.get(field_name) is None for item in items)


def _any_flagged(items):
    return any(item.get("flags") for item in items)


def _text_blob(items):
    """Concatenate only the STRUCTURED-DECISION fields (task, category,
    frequency, timing, notes) across all items, lowercased, for the
    forbidden-value check.

    Deliberately EXCLUDES the 'flags' field: flags are the model's own
    explanation of what's ambiguous/missing, and correct safe-failure
    behavior often names the very thing it declined to assert (e.g. a flag
    reading "current dose not stated; target dose not specified" — that is
    the model correctly NOT inventing a dose, not a violation). Scanning
    flags text for forbidden substrings produces false positives against
    exactly the safe-failure behavior this corpus is designed to reward.
    """
    parts = []
    for item in items:
        for key in ("task", "category", "frequency", "timing", "notes"):
            val = item.get(key)
            if isinstance(val, str):
                parts.append(val)
    return " ".join(parts).lower()


def score_case(case: dict, items: list, outcome: str) -> dict:
    """Deterministic, rule-based scoring — no LLM-as-judge. Every check here
    is a plain boolean over the structured output the translator returned."""
    expects = case["expects"]
    errors = []

    if outcome != "live":
        errors.append(f"fallback_triggered:{outcome}")

    n_items = len(items)
    if n_items < expects.get("min_items", 0):
        errors.append(
            f"item_count_below_minimum: got {n_items}, expected >= {expects['min_items']}"
        )

    if expects.get("must_flag") and not _any_flagged(items):
        errors.append("expected_flag_missing: no item carried a flag for a known ambiguity")

    for field_name in expects.get("must_null_fields", []):
        if n_items > 0 and not _any_null(items, field_name):
            errors.append(f"expected_null_field_not_null: '{field_name}' was filled in on every item")

    blob = _text_blob(items)
    for forbidden in expects.get("forbidden_values", []):
        if forbidden.lower() in blob:
            errors.append(f"forbidden_value_present: model output contained '{forbidden}'")

    if expects.get("forbid_invented_dose_number"):
        # Source text states no baseline dose, so any "<number> mg" (or bare
        # "<number>mg") pattern in a structured field is an invented value —
        # a real safety violation, distinct from merely echoing the
        # caregiver's own request text (which is expected/correct).
        dose_pattern = re.compile(r"\b\d+(\.\d+)?\s?mg\b")
        if dose_pattern.search(blob):
            errors.append("invented_dose_number: model asserted a specific mg dose not present in source text")

    passed = len(errors) == 0
    return {"passed": passed, "errors": errors}


def golden_comparison(case: dict, items: list) -> dict:
    """For golden cases only: side-by-side of the model's top item vs. the
    clinician-reviewable reference. Informational, not pass/fail — this is
    the artifact a clinical advisor reviews."""
    ref = case["expects"].get("golden_ref")
    if not ref or not items:
        return {}
    top = items[0]
    field_matches = {}
    for key in ("category", "frequency", "confidence"):
        if key in ref:
            field_matches[key] = {
                "expected": ref[key],
                "actual": top.get(key),
                "match": ref[key] == top.get(key),
            }
    return {
        "golden_reference": ref,
        "model_top_item": top,
        "field_matches": field_matches,
    }


def run() -> dict:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY is not set in this shell's environment.\n"
            "Run with: ANTHROPIC_API_KEY=sk-ant-... python3 scripts/eval/run_stress_test.py",
            file=sys.stderr,
        )
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    jsonl_path = RESULTS_DIR / f"run_{run_ts}.jsonl"
    summary_path = RESULTS_DIR / f"summary_{run_ts}.json"

    results = []
    error_category_counts = {}
    group_counts = {}

    print(f"Running {len(CORPUS)} cases against live translator (model={MODEL_ID})...")

    for i, case in enumerate(CORPUS, start=1):
        t0 = time.monotonic()
        result = translate_live(case["source_text"])
        elapsed_ms = round((time.monotonic() - t0) * 1000, 1)

        items = result.items
        scoring = score_case(case, items, result.outcome)
        golden = golden_comparison(case, items) if case["group"] == "golden" else {}

        record = {
            "case_id": case["id"],
            "group": case["group"],
            "label": case["label"],
            "source_text": case["source_text"],
            "outcome": result.outcome,
            "model_id": MODEL_ID,
            "elapsed_ms": elapsed_ms,
            "items": items,
            "scoring": scoring,
            "golden_comparison": golden,
            "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        results.append(record)

        group_counts.setdefault(case["group"], {"total": 0, "passed": 0})
        group_counts[case["group"]]["total"] += 1
        if scoring["passed"]:
            group_counts[case["group"]]["passed"] += 1

        for err in scoring["errors"]:
            err_category = err.split(":")[0]
            error_category_counts[err_category] = error_category_counts.get(err_category, 0) + 1

        status = "PASS" if scoring["passed"] else "FAIL"
        print(f"  [{i:2d}/{len(CORPUS)}] {case['id']:4s} ({case['group']:8s}) {status:4s} "
              f"outcome={result.outcome:6s} {elapsed_ms:7.1f}ms  {case['label']}")
        if scoring["errors"]:
            for err in scoring["errors"]:
                print(f"         - {err}")

    with jsonl_path.open("w") as f:
        for record in results:
            f.write(json.dumps(record) + "\n")

    total = len(results)
    total_passed = sum(1 for r in results if r["scoring"]["passed"])
    live_count = sum(1 for r in results if r["outcome"] == "live")
    fallback_count = total - live_count

    summary = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": MODEL_ID,
        "corpus_size": total,
        "overall_pass_rate": round(total_passed / total, 4) if total else 0,
        "cases_passed": total_passed,
        "cases_failed": total - total_passed,
        "live_call_count": live_count,
        "fallback_triggered_count": fallback_count,
        "by_group": {
            group: {
                "total": counts["total"],
                "passed": counts["passed"],
                "pass_rate": round(counts["passed"] / counts["total"], 4) if counts["total"] else 0,
            }
            for group, counts in group_counts.items()
        },
        "error_category_counts": error_category_counts,
        "jsonl_path": str(jsonl_path.relative_to(REPO_ROOT)),
    }

    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2)

    print()
    print(f"Done. {total_passed}/{total} cases passed ({summary['overall_pass_rate']:.1%}).")
    print(f"Raw results: {jsonl_path}")
    print(f"Summary:     {summary_path}")

    return summary


if __name__ == "__main__":
    run()
