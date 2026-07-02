# PLAN_FEEDBACK — one_generator/PLAN.md

Strict review of the one-generator `z = w(x,y)` plan. Format: **what → why → fix**.
Ordered by severity. Repo facts re-verified this session: MS(1190) = 1190 lines,
`max|r1| = 17`, `max|r2| = 15` (so the `L = 24` claim in Phase 1 holds).

---

## 1. The `z=r1⁻¹` / `z=r2⁻¹` arms are redundant — by the plan's own skip rule

**What.** The plan skips `x⁻¹/y⁻¹` as "mere orientation flips of `z=x`/`z=y`" but keeps
`r1⁻¹/r2⁻¹` as separate arms. These are the same kind of flip.

**Why.** The relabeling `z ↦ z⁻¹` (an automorphism fixing x, y) maps the `z=r1` arm's
z-relator `z·r1⁻¹` to `z⁻¹·r1⁻¹ ≡ (r1·z)⁻¹ ≡ z·r1` — exactly the `z=r1⁻¹` arm. Every
plan-relevant operation is equivariant under it: substitution moves, free/cyclic reduction,
the per-relator canonicalization (already inversion-invariant via `canonical_relator_nj`),
the length priority, and the blocked state. The two searches are isomorphic; the only
difference is heapq tie-breaking on key strings. This is the identical argument used to
skip `x⁻¹/y⁻¹`, so keeping `r1⁻¹/r2⁻¹` is inconsistent — and burns ~33% of the sweep
compute measuring tie-break noise.

**Fix.** Drop the two inverse arms (6 → 4 words: `{x, y, r1, r2}`). If tie-break
sensitivity is actually wanted, measure it cheaply on one arm with a randomized heap
tie-break seed instead of two full extra arms.

## 2. Budget sweep × JSONL resumability: the resume key is underspecified

**What.** Each arm writes one `.jsonl` keyed by `idx`, but the budget sweep is `max_nodes ∈ {100k, 1M}`. An idx recorded as *unsolved at 100k* will be skipped by the resume logic when the 1M pass runs.

**Why.** `jsonl_done_ids(path)` keyed on `idx` alone cannot distinguish "done at 100k"
from "done at 1M"; either the 1M pass silently no-ops, or you duplicate idx lines and
every downstream merge has to guess which line wins. This is a bug-in-waiting in the
exact crash/preempt scenario the JSONL convention exists for.

**Fix.** One stream per (arm, budget): `greedy_z_<w>_100k.jsonl` and
`greedy_z_<w>_1m.jsonl`, where the 1M pass enumerates **only idx unsolved at 100k**
(also saves compute — solved cases never rerun). Merge at report time keeps
"which budget solved it" for free.

## 3. `max_len` parity between baseline and arms is a confound

**What.** The notebook cap is on the **sum** of relator lengths
(`len(nr1r) + len(nr2r) < max_len`). The plan says "max_len generous (≥ initial z-relator
length + headroom)" but never pins the rule relative to the baseline.

**Why.** If baseline and z-arms share one sum-cap, the arm's z-relator (up to 18 letters
for `z=r1`) eats the headroom available to r1/r2 — the arm searches a strictly smaller
(r1, r2) region and any "coverage regression" is an artifact of the cap, not of
stabilization. If the arm cap is bumped ad hoc, efficiency comparisons drift instead.

**Fix.** Switch to a **per-relator** cap (mirrors the env's `L = 24` semantics), same
value for every relator in every arm — then the r1/r2 subspace constraint is identical
across baseline and arms by construction. Record the cap per line (already planned) and
state the rule once in `greedy_nrel.py`'s docstring. Bonus: a per-relator cap also bounds
the state space, which helps issue 5.

## 4. The Phase 0.5 HARD gate conflates "implementation bug" with "new discovery"

**What.** The gate says a greedy solve at idx ≥ 640 invalidates the labels → stop and
re-derive.

**Why.** The paper's "never solved outside the 640" is a statement about *their* runs
(specific tie-breaks, caps, budgets). Our GS-Sub differs in tie-breaking and possibly cap
semantics; a genuine solve at idx ≥ 640 would be a (small but real) research finding, not
automatically an ordering error. Auto-stopping throws that signal away.

**Fix.** On any idx ≥ 640 solve: quarantine the line, **replay the returned path**
(free+cyclic reduce each step, assert it ends at all-relators-length-1 — the Phase 3
re-verification already specifies this machinery). Replay passes → keep the labels, log it
as a new solve. Replay fails → then it's a solver bug, stop and fix. Only an
*irreproducible* solve should invalidate the ordering assumption.

## 5. Wall-clock budget is under-scoped; `get_neighbors` needs one cheap optimization

**What.** No runtime estimate anywhere in the plan, and the notebook's
`get_neighbors_nj` allocates `np.roll` copies for every rotation pair *before* checking
the boundary-cancellation condition.

**Why.** Notebook cell 5 measures ~10k nodes / 1.9 s single-core. At that rate: 100k
budget ≈ 19 s × 550 unsolved ≈ 3 h per arm; the 1M escalation ≈ 29 h per arm; times
5 arms (baseline + 4 words after issue 1) — and n=3 has 6 ordered relator pairs vs 2,
so a ~3× branching multiplier on top. That is CPU-weeks single-core, silently.

**Fix.** Three cheap levers: (a) in the n-relator `get_neighbors`, read the two boundary
letters directly from the arrays (two indexed lookups per rotation pair) and only
materialize concat+reduce for pairs that actually cancel — cancellation is sparse, this
is an order-of-magnitude constant-factor win; (b) parallelize across presentations with
`multiprocessing` — the per-idx JSONL streams already make this shard-safe; (c) the
100k→1M escalation from issue 2. Also a porting trap: the notebook's
`np.roll(r1, 2*i)` rolls by 2 because of the (n,2) bool layout — the int port must roll
by `i`, or every rotation is wrong.

## 6. Memory at 1M nodes / n=3 is unbudgeted; `new_seen` doubles it

**What.** The solver stores every *generated* (not just expanded) canonical state as a
Python string-tuple in `visited`, plus a duplicate copy in `new_seen`.

**Why.** At 1M expanded nodes with n=3 branching, generated states plausibly reach
10⁷–10⁸; Python str-tuple keys at ~100+ B each puts a single arm into tens of GB. A
preempted cloud box will OOM before the JSONL resumability ever matters.

**Fix.** Drop `new_seen` from the sweep path (it is only used for post-hoc "minimal
element" prints); key `visited` on compact `bytes` (int8-encoded relators joined by a
separator) instead of character strings — ~4× smaller and hashes faster. Log peak RSS
per line so the 1M runs are observable.

## 7. Expect `z=x` / `z=y` node-usage inflation from length-neutral aliasing — pre-register it

**What.** With z-relator `z·x⁻¹`, swapping any single occurrence `x ↔ z` in r1/r2 is a
length-neutral substitution.

**Why.** Best-first on total length exhausts each length level before growing, so the
search will enumerate large chunks of the ~2^(#x-occurrences) alias orbit at the *initial*
length before making progress. `z∈{x,y}` arms will likely show much worse node usage and
budget-exhaustion "regressions" that say nothing about stabilization being bad — they
measure alias-orbit blowup. Unflagged, this will be misread in Phase 3 headline plots.

**Fix.** No code change needed — pre-register the expectation in the plan and interpret
`z∈{x,y}` coverage regressions as budget artifacts unless replay says otherwise. Optionally
report a per-arm "distinct states modulo `z↦x` relabel" diagnostic to quantify the orbit
inflation. (This also makes `z=r1`/`z=r2` the arms where a real wormhole signal is most
likely to be visible — worth saying in the plan.)

## 8. Minor (one-liners)

- **numba warm-up:** JIT compilation lands in the first presentation's `wall_time_s`
(visible in the notebook's 1.9 s cell). Run one throwaway solve before the sweep, and
keep dtypes fixed (int8 everywhere) to avoid silent recompiles.
- **Path-length convention:** define whether a `z=w` arm's `path_len` includes the
implicit stabilization move (+1). Either is fine; cross-arm plots must use one rule.
- **Positive note worth keeping:** the single blocked state is more robust than it looks because `canonical_relator_nj` is inversion-invariant and the tuple is sorted, the 2-step revert `(r1,r2,z·r1⁻¹) → ([z],r2,z·r1⁻¹) → ([z],r2,r1⁻¹)` canonicalizes to exactly the blocked key and is caught. Pre-flight check 4 should assert this specific 2-step variant, not just the direct 1-step revert.

