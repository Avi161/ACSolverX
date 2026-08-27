# Speedups — every performance claim, with its conditions

Each entry states what was measured, on what, against what, and where the run lives. A
ratio without its conditions is not a result.

## Node efficiency (the ordering itself)

- **`s20_mk2` vs plain greedy, bench60 @1M**: node geo-mean ratio **0.300** (median 0.342,
  faster on 53/60 rows). Certificates are *not* shorter — the win is queue discipline.
- **solved_1hop 432 orbits**: geo-mean **0.671** on the 388 rows all arms solved.
- **Per-row anecdotes at matched cap 24**: `ms633` 26,838 → **108** nodes (248×), `ms628`
  26,774 → 107 (250×) — audited, but the rows were picked *because* the ordering wins big
  on them; quote the geo-means, not these.
- **Substitution supermoves**: ≈**1600×** exploration-efficiency over the prior elementary-
  move baseline — the paper's claim (README), conditioned on its published setup.

## Engine and infrastructure (research branches; not ported, recorded)

- **`hcompact`** (packed-arena engine): ~**78 B/state**, ~**13% faster**, pop-identical
  over 880 paired searches, 0 mismatches. A 10⁶-state reserve drops from ~24 GB to ~7 GB;
  a 51 GB ceiling moves from ~2M to ~5M nodes.
  (`origin/worktree-hsearch-hyper`, `results/heuristic_search/HCOMPACT.md`.)
- **`keep_path=False`** low-memory mode: **1.53×** less RAM, search bit-identical.
- **`N_WORKERS` spawn pool**: the 10⁶-node campaign drops to **~12–30 h on 8 cores**
  (`origin/worktree-hsearch-hyper`, `runners/run_ab.py`).
- **CoV K=4 beam pipeline**: ≈**3.0×** mean wall-time vs a full 1,000-node greedy on the
  11 rows both arms leave unsolved (2.61 s vs 0.88 s/row) — machine-local, ratios are the
  durable part. **Carry the advisor's walk-back with it**: K was selected in-sample over 7
  values on the same 60 rows, the beam only *tied* the best-first climb (49/60 vs 49/60,
  same rows), and 19/60 rows ran above the controls' cap.
  (`origin/cursor/heur-u124-s20mk2-a42e`, `results/comparison/covbeam_*`.)
- **covmeet orbit memo**: **2.6–6.5×** (134 → 51 ms/state cold, 21 ms warm) on the CoV
  meeting search — the engine work survived even though the search itself returned a null
  (see [`stable-ac-learnings.md`](stable-ac-learnings.md)).

## PPO throughput

- **31.18 s/update** on a Colab A100 with TF32 **off** (a deliberate parity cost; arms
  train with it on) → ~8.7 h per 1,000-update arm. The workload is bandwidth- and
  launch-bound, not FLOP-bound: 137,765 params moving 228,480 transitions/update.
- Hardware corollary: a GB10 box measures ~117–120 GB/s vs an A100's ~1,555 GB/s — an
  order of magnitude down on a bandwidth-bound job. Rent one 2-GPU box and run both arms
  on identical silicon.
- Memory: gradient accumulation at `MICRO_BATCH=2048` cuts an ~8 GB autograd grid to a
  couple of GB with advantage-normalisation still over the full minibatch; the einsum
  relative-position path avoids a several-GB tensor outright.

## The one cost worth knowing about

**numba cold start**: ~30–60 s compiling ~17 `@njit` entry points, once per process. It is
why the main CI job carries a 20-minute timeout for a 2-minute suite, and why no test
carries a tight per-test timeout. `tests/ppo` imports no numba at all — that is why its CI
job doesn't pay it.
