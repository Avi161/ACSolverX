# scale10k — 10h mini-research plan (Colab handoff AFTER wall)

Wall: **10 hours** from first `research_scale10k` launch.  
Per-search caps: **≤10,000 nodes** and **≤1 hour** wall.  
Out dir: `results/heuristic_search/scale10k/` (never into live `campaign_12h/`).

Advisor verdict on the first draft: **REVISE** — incorporated below.

## What this answers

What should the user run for a **10–20 hour multi-CPU Colab** campaign?
Arm(s), dataset, budget, cap, workers/chunks — sized from measured pops/s and
anytime curves, not from a pre-committed “s24/s20” guess.

## Arms (pre-registered)

| arm | config | why |
|---|---|---|
| `length` | length-only | control |
| `s12` | `L+12·S` | even/select peak on s_grid 800 |
| `s20` | `L+20·S` | odd-half peak; plateau with s12 |
| `recommended` | shipped multi-feature | different family (not another S weight) |

**Dropped:** `s24` — paired sign test on s_grid: s20≻s24 (33/11, p≈0.001).

## Slices (frozen before scoring)

1. **`slice_l_stratified.json`** — outcome-unconditioned, L-stratified AC1M from the
   24,173 screen. **Headline** arm comparison.
2. **`slice_fresh_hard.json`** — 60 length-hard rows **not** in s_grid’s 800.
   Reach readout only; `length` unsolved@1k is true by construction — label it so.
3. **`unsolved124`** — all 124 ACA classes, **cap 64** (EXP-12 parity). Reach probe;
   expected mostly 0@10k; any solve gets certificate replay.

## Phases

1. Cost profile @1k/5k/10k (local pops/s; Colab sizing still uses EXP-28 rates).
2. Anytime to 10k on L-stratified (cap 48).
3. Anytime to 10k on fresh hard (cap 48).
4. Anytime to 10k on unsolved124 (cap 64).
5. Portfolio: `{s12,s20,s32}` @3333 vs `s20` @10k on 30 fresh hard (matched total nodes).

## Gates

- `reserve_states ≈ 120 × budget` (avoid growth-copy polluting pops/s).
- Anytime claims use **`solved` / `solved_at` only** (prefix-recoverable).
- Solves on unsolved124 → `greedy_search_h(keep_path=True)` replay.
- Do **not** ship Colab CONFIG until `wall_end`.

## Deliverable after wall

`COLAB_RECOMMENDATION.md` + finalize `hsearch_s24_scale.ipynb` CONFIG.
Until then the notebook is a **draft** — do not treat it as the handoff.

## Run

```bash
python3 -m experiments.heuristic_search.runners.research_scale10k
```
