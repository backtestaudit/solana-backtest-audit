#!/usr/bin/env python3
"""Check 2 — Loss = cost identity.

Separates two very different diagnoses in about five minutes:

  (a) IMPLEMENTATION BUG / COST PROBLEM
      observed loss ~= n * size * round_trip_cost   ->  gross ~= 0
      Your code is probably fine; the edge does not cover costs.

  (b) PRICE COLLAPSE / NO EDGE
      observed loss >> cost                          ->  gross strongly negative
      Fees explain almost nothing. The asset actually fell after entry.

These have completely different fixes, so confusing them wastes months.

Usage:
    python3 audit_fee_identity.py
    from audit_fee_identity import audit
    audit(n=148, total_pnl=-85.1, size=1.0, round_trip_pct=2.8, wins=24)
"""
import sys


def audit(n, total_pnl, size, round_trip_pct, wins=None):
    cost = n * size * round_trip_pct / 100.0
    gross = total_pnl + cost
    per_trade = total_pnl / n if n else 0.0
    per_pct = per_trade / size * 100 if size else 0.0
    cost_share = abs(cost / total_pnl) * 100 if total_pnl else 0.0

    print("=" * 60)
    print("CHECK 2 — LOSS DECOMPOSITION (bug vs no-edge)")
    print("=" * 60)
    print(f"  trades / size          : {n} x {size}")
    print(f"  total PnL              : {total_pnl:+.2f}")
    print(f"  per trade              : {per_trade:+.4f} ({per_pct:+.1f}%)")
    print(f"  round-trip cost        : {cost:.2f} ({round_trip_pct}% x {n})")
    print(f"  GROSS (before costs)   : {gross:+.2f}")
    print(f"  share of loss from cost: {cost_share:.1f}%")
    print()

    if abs(total_pnl) > 0 and cost_share > 90 and abs(gross) / abs(total_pnl) < 0.15:
        print("  VERDICT: cost dominates -> gross ~= 0")
        print("           Implementation is likely fine. No edge, or edge < cost.")
        print("           FIX: find real edge, or move to a lower-fee venue.")
    elif per_pct < -30:
        print(f"  VERDICT: PRICE COLLAPSE dominates ({per_pct:.1f}%/trade)")
        print("           Not a fee problem. Price fell hard after entry.")
        print("           FIX: stop-loss structure / entry filters / different population.")
    elif gross > 0 and total_pnl < 0:
        print("  VERDICT: gross is positive, costs are eating it")
        print("           FIX: reduce size, lower-fee venue, better fills.")
    else:
        print(f"  VERDICT: gross is {'positive' if gross > 0 else 'negative'}")
    print()

    if wins is not None and n:
        wr = wins / n
        need = 0.95 / (0.95 + 1.50) * 100
        print(f"  win rate {wr*100:.1f}% ({wins}/{n})")
        print(f"  break-even at payoff (-95% / +150%): {need:.1f}%")
        if wr * 100 < need:
            print(f"  -> you must filter out ~{(1 - wr*100/need)*100:.0f}% of losers to break even")
    return gross


if __name__ == "__main__":
    # Reference case.
    audit(n=148, total_pnl=-85.1, size=1.0, round_trip_pct=2.8, wins=24)
    sys.exit(0)
