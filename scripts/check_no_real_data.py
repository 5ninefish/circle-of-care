#!/usr/bin/env python3
"""
Data-safety pre-deploy gate (CRITICAL — non-negotiable per the design doc's
Test & Validation Plan).

Greps the repository — and optionally any other directory you point it
at (e.g. a rendered static export of the app) — for real family
identifiers, and fails LOUDLY (non-zero exit, printed matches) if any
are found.

This script ships with the MECHANISM only. It has no real identifiers
built in — Dalen fills those into scripts/denylist.txt (gitignored,
never committed) before running this in anger. Until that file exists,
the script runs against scripts/denylist.example.txt and warns that no
real denylist is configured yet, so a clean run before the list is
populated must not be mistaken for "safe to deploy."

Usage:
    python3 scripts/check_no_real_data.py
    python3 scripts/check_no_real_data.py --denylist path/to/list.txt
    python3 scripts/check_no_real_data.py --check-dir /path/to/rendered/output

Run this before EVERY deploy.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DENYLIST = REPO_ROOT / "scripts" / "denylist.txt"
EXAMPLE_DENYLIST = REPO_ROOT / "scripts" / "denylist.example.txt"

# Directories never worth scanning: VCS internals, virtualenvs, caches.
SKIP_DIR_NAMES = {".git", "venv", ".venv", "__pycache__", "node_modules", ".streamlit"}

# Skip obviously-binary extensions; everything else is read as text.
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".pyc", ".ico"}


def load_denylist(path: Path) -> list:
    if not path.exists():
        return []
    terms = []
    for line in path.read_text(errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in p.parts):
            continue
        if p.suffix.lower() in SKIP_EXTENSIONS:
            continue
        yield p


def scan(root: Path, terms: list) -> list:
    """Returns a list of (file, line_number, term, line_text) matches."""
    if not terms:
        return []
    lower_terms = [(t, t.lower()) for t in terms]
    matches = []
    for path in iter_files(root):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            lower_line = line.lower()
            for original, lowered in lower_terms:
                if lowered in lower_line:
                    matches.append((path, lineno, original, line.strip()))
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="CRITICAL data-safety gate: block real family data from public artifacts.")
    parser.add_argument("--denylist", type=Path, default=DEFAULT_DENYLIST, help="Path to the denylist file (default: scripts/denylist.txt)")
    parser.add_argument("--check-dir", type=Path, default=REPO_ROOT, help="Directory to scan (default: repo root). Pass a rendered-app export directory to also check app output.")
    args = parser.parse_args()

    using_example = not args.denylist.exists()
    denylist_path = args.denylist if not using_example else EXAMPLE_DENYLIST
    terms = load_denylist(denylist_path)

    if using_example:
        print(
            "WARNING: scripts/denylist.txt does not exist yet — running against the "
            "example template, which contains NO real identifiers.\n"
            "This is NOT a pass — it means the gate has nothing real to check for.\n"
            "Copy scripts/denylist.example.txt to scripts/denylist.txt and fill in the "
            "real family's identifying details before trusting this gate.\n",
            file=sys.stderr,
        )

    matches = scan(args.check_dir, terms)

    if matches:
        print("DATA SAFETY GATE FAILED — real-family identifiers found:\n", file=sys.stderr)
        for path, lineno, term, line in matches:
            rel = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
            print(f"  {rel}:{lineno}  matched '{term}'  ->  {line}", file=sys.stderr)
        print(f"\n{len(matches)} match(es) across the scanned directory. DO NOT DEPLOY.", file=sys.stderr)
        return 1

    if using_example:
        print("No matches against the EXAMPLE denylist (expected — it's empty of real terms). "
              "Populate scripts/denylist.txt before deploying.")
        return 0

    print(f"Data safety gate passed — no matches for {len(terms)} denylist term(s) in {args.check_dir}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
