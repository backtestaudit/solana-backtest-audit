#!/usr/bin/env python3
"""Check 1 — Survivorship / coverage audit.

The most common reason a crypto backtest is invalid: the universe came from a
"top N by volume" snapshot, which is by definition the assets that already
went up. Measure coverage against the number of assets that were actually
created in the window.

Usage:
    python3 audit_survivorship.py
    # or import and call:
    from audit_survivorship import audit
    audit(universe_size=114, window_hours=19.9, pools_per_hour=143)
"""
import sys


def audit(universe_size, window_hours, pools_per_hour, selection_note=""):
    expected = window_hours * pools_per_hour
    coverage = universe_size / expected * 100 if expected else 0.0

    print("=" * 60)
    print("CHECK 1 — SURVIVORSHIP / COVERAGE")
    print("=" * 60)
    print(f"  backtest universe      : {universe_size} assets")
    print(f"  observation window     : {window_hours:.1f} hours")
    print(f"  assets created in window: ~{expected:.0f} ({pools_per_hour:.0f}/h)")
    print(f"  COVERAGE               : {coverage:.1f}%")
    print()

    if coverage >= 80:
        grade, verdict = "A", "PASS - near-full population"
    elif coverage >= 40:
        grade, verdict = "B", "CAUTION - partial universe, dead assets likely missing"
    elif coverage >= 10:
        grade, verdict = "C", "WARNING - selection bias suspected, treat as upper bound"
    else:
        grade, verdict = "D", "** INVALID ** - top-N snapshot, backtest is not predictive"

    print(f"  GRADE: {grade} - {verdict}")
    print()
    print("  Thresholds:")
    print("    A (80%+)   full population -> unbiased")
    print("    B (40-80)  partial -> dead assets excluded")
    print("    C (10-40)  selection bias -> results are an upper bound")
    print("    D (<10)    top-N snapshot -> backtest invalid")
    print()

    if selection_note:
        print(f"  Selection method: {selection_note}")
        print()

    if coverage < 40:
        print("  FIX: rebuild the universe by collecting every asset created in the")
        print("       window (point-in-time), not by filtering a current top-N list.")
    return coverage


if __name__ == "__main__":
    # Reference case: the failure this repo documents.
    audit(
        universe_size=114,
        window_hours=19.9,
        pools_per_hour=143,
        selection_note="24h volume top-200 snapshot, age <= 33h",
    )
    sys.exit(0)
