# My backtest had an 87% win rate. Live trading had 16%.

> Three ways a backtest lies — learned by losing 85 SOL.

---

## TL;DR

A 30-minute scalping bot on PumpSwap migration pools backtested at **+55.7% median, 87% win rate**. Live, it lost **85 SOL over 148 trades at −57.5% per trade**.

The strategy wasn't broken. The **sample** was.

**Coverage: 114 pools backtested / ~2,846 pools created in the window = 4.0%.**

That 4% was selected by "24h volume top 200" — which is, by definition, the pools that already went up. Measuring 30-minute returns inside that cohort is circular.

This repo contains the three checks that would have caught it, plus the data from the failure.

---

## The three checks

### Check 1 — Survivorship / coverage

> Is your universe a "top N by volume" snapshot? What % of pools created in the window does it cover?

| Coverage | Grade | Verdict |
|---|---|---|
| 80%+ | A | Full population — unbiased |
| 40–80% | B | Partial — dead pools likely missing |
| 10–40% | C | Selection bias suspected — treat results as an upper bound |
| **<10%** | **D** | **Top-N snapshot → backtest is invalid** |

**Ours: 4.0% → grade D.** It was invalid from the start.

```bash
python3 audit_survivorship.py
```

### Check 2 — Loss = cost identity

> Is observed loss ≈ `n × size × round_trip_cost`?

If the identity holds, **gross ≈ 0 → no edge**. If loss is far larger, **price collapsed**.

This separates an implementation bug from a missing edge in about five minutes. The two have completely different fixes, and confusing them wastes months.

**Ours:** round-trip cost 2.8%, 148 trades, 1 SOL each → 4.14 SOL. Observed loss 85.1 SOL.
Cost explains **4.9%** of the loss. Gross was **−81.0 SOL (−54.7%/trade)**. Not a bug — price actually collapsed.

```bash
python3 audit_fee_identity.py
```

### Check 3 — Split-half stability

> Is the result positive in both halves of the sample?

**Ours: first half +78.9%, second half +39.3% — it passed.**

**This is the important part: Check 3 alone would not have caught it.** Our backtest passed Check 3 and still lost 85 SOL live.

You need all three. That is the entire reason this repo exists.

```bash
python3 audit_split.py
```

---

## Why the three checks together

| Check | Caught our failure? |
|---|---|
| 1. Coverage | ✅ 4% — invalid immediately |
| 2. Loss identity | ✅ gross −54.7%, not a bug |
| 3. Split-half | ❌ **passed** (+78.9% / +39.3%) |

Any single check is insufficient. Two of three would have flagged it. Check 1 alone would have saved the 85 SOL before a single live trade.

---

## The unbiased number was already available

The same project had a separate report containing:

| Metric | Value |
|---|---|
| Active pool 1h median drift | **−3.60%** (up 15 / down 53) |
| 30-min equivalent + round-trip cost | **−4.6%/trade** |
| Pools that died despite top activity | 59.7% (117/196) |
| Rug within 30 min (−50%) | 14.24% |

The live result of −57.5%/trade has the **same sign** as the unbiased benchmark. That number was available before deployment.

---

## What the live trades looked like

Win/loss decomposition (148 trades, 1 SOL each):

| Metric | Value |
|---|---|
| Total PnL | −85.1 SOL |
| Per trade | −57.5% |
| Win rate | 16.2% (24 wins) |
| Round-trip cost | 2.8% |

The implied payoff — given 16.2% wins and −57.5% average — is roughly **"16% return 1.3–1.8×, 84% go to −90…−100%."**

Break-even win rate at that payoff: **38.8%**. Observed: **16.2%**.

**You would have to filter out two-thirds of the losers** to reach break-even. No entry filter we tested came close.

---

## Bonus: where creator fees actually come from

Same dataset (89 tokens with complete supply/bar data), reconstructing creator fees by market-cap band:

| Finding | Value |
|---|---|
| Top 25% vs rest — volume | **21×** |
| Top 25% vs rest — holders | **21.5×** |
| Max 1-min trade concentration ↔ fees | **ρ = −0.742** |
| Spike-type vs sustained-type fees | $410 vs $8,639 (**21×**) |
| **Launch first hour as % of total fees** | **0.9%** |
| 0.95% fee band ($67k–$235k mcap) share | **97%** of fees |
| Top 10 tokens' share of fees | **58%** |

The counterintuitive one: **concentrating volume into one minute cuts fees by ~21×.** Bots don't create fees — they shorten the token's life.

---

## Usage

```bash
git clone <this-repo>
cd <repo>

# Reconstruct our failure
python3 audit_survivorship.py
python3 audit_fee_identity.py
python3 audit_split.py
```

Each script is standalone, stdlib-only, no dependencies.

### Applying to your own strategy

**Check 1** — you need the number of assets created in your backtest window (not the number that survived). If your universe came from a "top N" list, compute the ratio before anything else.

**Check 2** — plug in `n`, `total_pnl`, `size`, and `round_trip_pct`. The script tells you whether cost or price explains the loss.

**Check 3** — pass your per-trade returns in chronological order.

---

## Files

```
audit_survivorship.py    # coverage → bias grade
audit_fee_identity.py    # loss decomposition: bug vs no-edge
audit_split.py           # split-half stability
examples/our_failure.json  # anonymized real numbers from this case
```

---

## Limitations

- This is a **single case study**, not a general theory of backtest failure. Survivorship was our dominant error; yours may be look-ahead, fee modeling, or fill assumptions.
- The 114-pool cohort came from a top-200 snapshot, so **absolute fee figures are upper bounds**. Relative comparisons (21×, ρ = −0.742) are less sensitive to that bias.
- Check 3 passing does not mean the strategy works — it means the result is stable *within the sample*. True out-of-sample is future data.
- Fee band rates: 0.95% (420–1,470 SOL) and 0.30% (<420 SOL) are confirmed from documentation. Bands above that are approximations, but 97% of fees came from the 0.95% band so the impact is small.

---

## License

MIT — see `LICENSE`.

---

## Contact

If your backtest passes Check 3 but loses live, Check 1 is usually the answer. Open an issue with your coverage ratio and I'll take a look.
