# The unsolved-124 campaign at 10⁶ nodes — the plan, before the trigger is pulled

Everything below is arithmetic from measured quantities, written down **before** the bench66 100k run finished, so the decision procedure is on record rather than reconstructed after the fact.

## The gate

Do not launch this campaign until the bench66 run's gap table (`hsearch_ab_bench66_b100000_mrl48.md`, section "The gap over the baseline") says **still widening**. The local study saw +12 → +14 between budgets 500 and 1,000 and everything past that is extrapolation; if the gap flattens by 100k, the ordering buys earliness rather than reach, and burning ~2.5 days of Colab on the 124 buys a foregone conclusion. If it widens, the campaign below is the right next spend.

## What to run

The notebook (`experiments/heuristic_search/hsearch_ab.ipynb`), CONFIG cell only:

```python
DATASET   = "unsolved124",
SUBSET    = None,
ARMS      = ["recommended"],          # NOT ["baseline", "recommended"] — see below
NODE_BUDGET = 1_000_000,
CHECKPOINTS = [1_000, 5_000, 10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000],
MAX_RELATOR_LENGTH = 48,
KEEP_PATH = False,                    # mandatory at this budget — see memory
RESUME    = True,
OUT_STEM  = "hsearch_ab",
```

**Drop the baseline arm.** The 124 are the classes the baseline greedy left unsolved at **10 million** nodes — its 10⁶ result is already known to be 0/124, with certainty, from the data that defined the set. Running it again would cost the same ~50 hours as the treatment arm to reproduce a number we already have. This is not the EXP-10 mistake in reverse: the historical baseline was run on these exact 124 presentations, same solver family, at 10× the budget — same denominator, stricter condition. (The report's gap section simply won't render without a `baseline` arm in the file; the comparison lives in the sentence above.)

## Memory — why `KEEP_PATH = False` is mandatory, not advisory

Measured worst-case on these exact rows at cap 48 (full-budget burns, `measure_memory.py`): **36.5 kB per node popped with the certificate map, 24 kB without**. At 10⁶ nodes that is ~36.5 GB vs ~24 GB peak per search — on a 51 GB Colab the first is a memory-guard coin-flip, the second fits with headroom. The mode is result-pure (pinned by `tests/heuristic_search/test_hsolve.py`) and `run_ab` recovers the certificate of anything that solves by an automatic deterministic re-run, whose memory is bounded by the *solve's* node count, not the budget. Rows written in either mode resume interchangeably.

## Time — a multi-session campaign, and that is fine

Rates measured: ~1,600–2,700 nodes/s on these rows locally at small heaps; **742 nodes/s on Colab mid-way into a 100k burn** (the honest at-scale anchor — the rate falls as the heap and relators grow, so expect 400–700 nodes/s in the tail of a 10⁶ burn). Since ~everything burns the full budget here, per search that is **~24–40 min**, and for 124 searches **~50–85 hours single-arm**. No Colab session survives that: the campaign is 3–5 sessions of Restart → Run All, and the per-row append-and-fsync plus `RESUME=True` means a disconnect costs at most the search in flight. Nothing needs babysitting beyond re-opening the notebook.

If 85 hours is too much, cut the *rows*, never the budget's tail: run the 124 in difficulty order if a priority subset exists, or accept a first pass at 250k (~13–21 h) — the checkpoint column means a later 10⁶ pass resumes nothing wasted, because a longer search's first 250k pops are exactly the shorter search.

## What to expect, and what would actually be signal

The honest prior is **0/124**. At budget 1,000 both ordering families went 0 for 3,920 searches on these classes, and the tuned ordering's wins on the benchmark came from reordering *reachable* solutions, not from reaching new ones. The campaign is still worth running if the gap gate passes, because 10⁶ tuned nodes explore a genuinely different ball than 10⁷ length-ordered nodes — the ordering changes *which* states are in the ball, not just their order (EXP-16's widening gap is the evidence that difference grows with budget).

**One solve would be a major result** — the first member of the 124 ever solved by direct search. The row's `path_moves` is the certificate (recovered automatically despite `KEEP_PATH=False`); verify it by replay through `moves_to_states` before believing it, and treat the presentation's whole AC-class as settled, not just the row.

Short of a solve, the run still pays: `min_relator_length` per row at 10⁶ against the known 10⁷ baseline floors says whether the tuned ball is reaching *lower* states — the floor-census lesson applies, so census the floor states' Aut-orbits before reading "same floor" as "no progress".
