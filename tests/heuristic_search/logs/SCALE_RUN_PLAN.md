# The unsolved-124 campaign at 10⁶ nodes — the plan, before the trigger is pulled

Everything below is arithmetic from measured quantities, written down **before** the bench66 100k run finished, so the decision procedure is on record rather than reconstructed after the fact.

## The gate — RESOLVED: FIRE (2026-07-24, [EXP-28](EXP28_colab_scale.md))

The bench66 run at 100k landed. The raw gap metric read "turned over" — a saturation artifact: **the tuned ordering finished the benchmark at 62,534 nodes (60/60 graded)**, so past that point the gap could only compress. Where headroom existed the scale answer is emphatic: 6/6 on bin 9 where the baseline takes 0/6 at 100k, and a **3.4×–23× node multiplier** against the baseline's `nodes_1M` on the hump band. A tuned run at 10⁶ therefore probes a baseline-equivalent ~3.4M–23M, and 3×10⁶ probes ~10M–70M — past the 10⁷ regime the 124 are known to survive. Prior for solves stays low (bin-8 parity rows show the multiplier can be ~1×), but this is the first probe of a genuinely new region. The campaign below is the right next spend.

## What to run

The notebook (`experiments/heuristic_search/hsearch_ab.ipynb`), CONFIG cell only:

```python
DATASET   = "unsolved124",
SUBSET    = None,
ARMS      = ["recommended"],          # NOT ["baseline", "recommended"] — see below
NODE_BUDGET = 1_000_000,
CHECKPOINTS = [1_000, 5_000, 10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000],
MAX_RELATOR_LENGTH = 48,
ENGINE    = "hcompact",               # ~7 GB per search at 10^6, not 24 — see memory
RESUME    = True,
OUT_STEM  = "hsearch_ab",
```

**Pick the budget once, as large as the hours allow.** A search at budget B is the first B pops of any longer search, so a 3×10⁶ run *contains* the 10⁶ run at every checkpoint — but the budget is part of the output filename identity, so a later, larger run starts a NEW file and re-pays everything already burned. Decide the ceiling from wall-clock before starting (10⁶ ≈ 50–85 h; 3×10⁶ ≈ 150–250 h), never plan to "extend later".

**Drop the baseline arm.** The 124 are the classes the baseline greedy left unsolved at **10 million** nodes — its 10⁶ result is already known to be 0/124, with certainty, from the data that defined the set. Running it again would cost the same ~50 hours as the treatment arm to reproduce a number we already have. This is not the EXP-10 mistake in reverse: the historical baseline was run on these exact 124 presentations, same solver family, at 10× the budget — same denominator, stricter condition. (The report's gap section simply won't render without a `baseline` arm in the file; the comparison lives in the sentence above.)

## Memory — why the engine choice matters

Measured worst-case on these exact rows at cap 48 (full-budget burns): `hsolve` costs **36.5 kB per node popped with the certificate map, 24 kB without** (`KEEP_PATH=False`) — at 10⁶ that is ~36.5 GB vs ~24 GB peak per search, the first a memory-guard coin-flip on a 51 GB Colab. **`ENGINE="hcompact"` replaces both: ~78 B per state, ~7 GB reserved for a 10⁶ search**, and it moves the machine's budget ceiling from ~2M to ~5M nodes ([HCOMPACT.md](HCOMPACT.md) — same search pop for pop, 880-pair cross-check, +13% faster). All three modes are result-pure and write identical rows (pinned by `tests/heuristic_search/test_hsolve.py` and `test_hcompact.py`); `run_ab` recovers the certificate of anything that solves by an automatic deterministic re-run, whose memory is bounded by the *solve's* node count, not the budget. Rows written under any mode resume interchangeably.

## Time — a multi-session campaign, and that is fine

Rates now **measured at scale in EXP-28's full-budget tails**: the user's VM sustained **~170–820 nodes/s** on the open rows at 100k under `hsolve` (state-size dependent; the earlier 742/s reading was one mid-burn sample, not the tail). Budget hours from ~200–500 nodes/s: a 10⁶ burn is **~33–85 min per presentation**, so 124 searches is **~70–170 hours single-arm** (`hcompact` is ~13% faster at small heaps and should degrade less at depth — treat that as upside, not a plan input). No Colab session survives that: the campaign is 4–8 sessions of Restart → Run All, and the per-row append-and-fsync plus `RESUME=True` means a disconnect costs at most the search in flight. Nothing needs babysitting beyond re-opening the notebook.

If that is too many hours, cut the *rows*, never the budget's tail: run the 124 in difficulty order if a priority subset exists, or accept a first pass at 250k (~17–43 h) — the checkpoint column means a later 10⁶ pass resumes nothing wasted, because a longer search's first 250k pops are exactly the shorter search. (But remember the budget-in-filename rule from above: a later, larger run starts a new file.)

## What to expect, and what would actually be signal

The honest prior is still **0/124**, but EXP-28 sharpened it in both directions. Against it: both ordering families went 0 for 3,920 searches at budget 1,000, and on the bin-8 band (ms622–ms625) the tuned multiplier is only ~1×. For it: on bin 9 the multiplier is 3.4–23×, so a tuned 10⁶ probes a baseline-equivalent **~3.4M–23M** and a tuned 3×10⁶ probes **~10M–70M — beyond the 10⁷ regime the 124 are defined by surviving**. The ordering changes *which* states are in the ball, not just their order; the 124 have never been searched in this ball at depth.

**One solve would be a major result** — the first member of the 124 ever solved by direct search. The row's `path_moves` is the certificate (recovered automatically despite `KEEP_PATH=False`); verify it by replay through `moves_to_states` before believing it, and treat the presentation's whole AC-class as settled, not just the row.

Short of a solve, the run still pays: `min_relator_length` per row at 10⁶ against the known 10⁷ baseline floors says whether the tuned ball is reaching *lower* states — the floor-census lesson applies, so census the floor states' Aut-orbits before reading "same floor" as "no progress".
