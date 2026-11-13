#!/usr/bin/env python3
"""Check 3 — Split-half stability.

A result that only works in one half of the sample is regime-dependent and will
not reproduce. IMPORTANT: passing this check does NOT mean the strategy works.
The reference case in this repo passed Check 3 (+78.9% / +39.3%) and still lost
85 SOL live. Check 1 is what catches that failure mode.

Usage:
    python3 audit_split.py
    from audit_split import audit
    audit([1.2, -0.8, 2.5, ...])   # per-trade returns, chronological
"""
import random
import statistics as st
import sys


def audit(returns):
    n = len(returns)
    if n < 10:
        print("Need at least 10 trades for a meaningful split.")
        return None
    h = n // 2
    first, second = returns[:h], returns[h:]

    print("=" * 60)
    print("CHECK 3 — SPLIT-HALF STABILITY")
    print("=" * 60)
    for label, sel in (("first", first), ("second", second), ("all", returns)):
        if not sel:
            continue
        wins = sum(1 for x in sel if x > 0)
        print(
            f"  {label:<7} n={len(sel):<5} median {st.median(sel):+8.2f}"
            f"  mean {st.fmean(sel):+8.2f}  win {100*wins/len(sel):3.0f}%"
        )
    print()

    m1, m2 = st.median(first), st.median(second)
    if m1 > 0 and m2 > 0:
        verdict = "PASS - positive in both halves (not regime-dependent)"
    elif m1 < 0 and m2 < 0:
        verdict = "FAIL - negative in both halves (consistently bad)"
    elif m1 == 0 or m2 == 0:
        verdict = "INCONCLUSIVE - a half has a zero median (too few trades or flat)"
    else:
        verdict = "HOLD - positive in only one half (regime-dependent)"
    print(f"  VERDICT: {verdict}")
    print()
    print("  CAVEAT: this splits the SAME sample. True out-of-sample is future data.")
    print("          A pass here does not validate the strategy — see Check 1.")
    return m1, m2


if __name__ == "__main__":
    # Reference case: our backtest passed this check and still failed live.
    random.seed(1)
    audit([random.gauss(55, 120) for _ in range(98)])
    sys.exit(0)
