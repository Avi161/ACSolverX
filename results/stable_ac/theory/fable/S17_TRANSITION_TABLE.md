# S17 — the empirical `γ_N` transition table for one SPLIT step

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch. No
PR opened (`FRAMING` trap 10). No existing file under `experiments/` or `ac_solver/` was
modified and no existing `.md` was edited; the only new code is
`experiments/stable_ac/fable/s17_transition_table.py`.

STATUS: **a measurement, not a theorem.** It sharpens `S16_CONTROL_RETRACTION.md` §4 from
"the pipeline never creates a certificate" to a full row-by-row picture of what one SPLIT
step does to `γ_N`, and it answers the calibration question S16 left open: *how many chances
did the `1 → 0` transition actually get?*

**Units, stated once.** `γ_N = minimum_defect // 2`. Every artifact on disk stores
`minimum_defect` (= 2·`γ_N`). Every table below is in `γ_N`. The conversion happens in
exactly one place in the script (`gp, gc = dp // 2, dc // 2`).

---

## 1. Where the pairs come from, and what "reconstructed" means here

`cubic_split_search.beam_search` persists, for every pooled state, the `root` it came from
and the full `trace` of SPLIT records that produced it. `split_apply` is deterministic given
a record, so the chain

    root = s₀ → s₁ → … → s_L = words

is replayable exactly, and each consecutive pair is **one SPLIT step**. That is the whole
method: no new search was run, no move tree was explored, **zero search nodes were used.**

| step | status |
|---|---|
| chains replayed from `root` + `trace` | **reconstructed** (deterministic replay) |
| reconstructed terminal state vs. persisted `words` | **measured**: 170,679 / 170,679 rows matched letter for letter; 0 replay failures, 0 mismatches |
| a sampled 400 chains re-checked with the repo's own `verify_split` | **measured**: 400 / 400 passed |
| defect of a state already in a persisted `*_decided.jsonl.gz` | **read from disk** (measured earlier by `cmd_decide`) |
| defect of a state not previously persisted (the roots and the depth‑1/2 intermediates, plus depth‑3 parents of depth‑4 rows) | **measured here** with `cubic_split_search.fast_min_defect`, `deep_cap = 400,000` — the same function and cap `cmd_decide` used to write the persisted rows |
| a 4-state spot check against the *independent* decider `s12_hunt.decide` (cut-scheme solver, a different code path) | **measured**: 2 states stored at `γ_N = 1` returned `NOT_SPHERICAL`; 2 states stored at `γ_N = 0` returned the solver's inconclusive `UNSUPPORTED` (it never returns a false NO, so this is consistent, not corroborating). No contradiction found; the check is weak on the `γ_N = 0` side and is recorded as such |

Artifacts read (all pre-existing): `s4b_pool.jsonl.gz`, `s4b_decided.jsonl.gz`,
`s4b_control_pool.jsonl.gz`, `s4b_control_decided.jsonl.gz`, `s4b_ctrl2_pool.jsonl.gz`,
`s4b_ctrl2_decided.jsonl.gz`, `s4b_ctrl2_full_decided.jsonl.gz`, `s4b_flips.jsonl`,
`s4b_ak3.jsonl`, `s4b_ak3_run2.jsonl`, `s4b_control.jsonl`, `s4b_ctrl2.jsonl`,
`s4b_ladder.jsonl`.
New artifacts written: `results/stable_ac/fable/s17_transition_table.json`,
`s17_transition_edges.jsonl.gz`, `s17_extra_decided.jsonl.gz`.

**Edge accounting (measured).** 176,484 *distinct* SPLIT edges (deduplicated on
`(canon_state(parent), canon_state(child))`, so an edge shared by thousands of descendant
rows is counted once). Of these, **174,178 have both endpoints decided and form the table**.
2,306 are dropped because the *child* is a rank‑13 state nobody has decided inside the
budget; **no edge is dropped for an unknown parent.** 184 of the 2,306 dropped edges have a
`γ_N = 1` parent — those are the only unobserved outcomes in the row that matters. Nothing
is imputed.

Coverage of the new decides (measured): 20,001 states needed a defect; 17,695 were measured
here; 0 exceeded the census cap; 2,306 (all rank 13) were left undecided when the wall-clock
budget expired. New compute: two tabulation passes of 227 s and 222 s wall clock
(`date -u`-measured, 09:30:46→09:34:33 and 09:37:05→09:40:47 UTC), each under the 4-minute
ceiling; the second pass existed only to raise coverage from 91 % to 98.7 % of edges and to
recover the rank‑9→10 layer, which a census-ordered first pass had starved.

---

## 2. The transition matrix — one SPLIT step, all families, all layers

Rows = `γ_N` **before** the step, columns = `γ_N` **after**. Counts are distinct edges.
**Total pairs the table rests on: 174,178** (measured).

| `γ_N` → | **0** | **1** | **2** | **3** | row total |
|---|---|---|---|---|---|
| **0** | 916 | 1,451 | 650 | 0 | **3,017** |
| **1** | **0** | 30,821 | 25,433 | 134 | **56,388** |
| **2** | 0 | 1,049 | 102,839 | 7,675 | **111,563** |
| **3** | 0 | 0 | 276 | 2,934 | **3,210** |
| col total | 916 | 33,321 | 129,198 | 10,743 | 174,178 |

Two shape facts, both **measured**:

- **Every descent is by exactly 1.** `3→1`, `2→0`, `1→0` are all empty; `3→2` and `2→1` are
  not. Ascents are not so limited: `0→2` (650) and `1→3` (134) both occur, so a
  "`|Δγ_N| ≤ 1`" law is false and cannot be the reason `1→0` is empty.
- **The descent rate collapses with the parent's `γ_N`:**
  from `γ_N = 3`, 276 / 3,210 = **8.598 %**;
  from `γ_N = 2`, 1,049 / 111,563 = **0.940 %**;
  from `γ_N = 1`, 0 / 56,388 = **0 %**.

### By layer (parent rank → child rank)

| layer | from 0 | from 1 | from 2 | from 3 |
|---|---|---|---|---|
| 9 → 10 | {0:117, 1:359} | {1:351, 2:154} | {1:51, 2:723} | — |
| 10 → 11 | {0:40, 1:176, 2:33} | {1:905, 2:773, 3:2} | {1:16, 2:1968, 3:10} | — |
| 11 → 12 | {0:759, 1:916, 2:617} | {1:27741, 2:24012, 3:132} | {1:822, 2:81628, 3:6377} | {2:20, 3:332} |
| 12 → 13 | — | {1:1824, 2:494} | {1:160, 2:18520, 3:1288} | {2:256, 3:2602} |

### By family

**AK(3)** (root `γ_N = 2`; 45,264 pool rows):

| from → | 0 | 1 | 2 | 3 | total |
|---|---|---|---|---|---|
| 1 | **0** | 473 | 659 | 0 | 1,132 |
| 2 | 0 | 136 | 41,971 | 4,229 | 46,336 |
| 3 | 0 | 0 | 24 | 262 | 286 |

So the AK(3) pipeline's descent `2 → 1` is **measured at 136 distinct edges** (it is real —
this is what puts 527 `γ_N = 1` states into AK(3)'s decided histogram), and every one of the
82 distinct `γ_N = 1` AK(3) states that then had a SPLIT applied stayed at `γ_N ≥ 1`.

**Control2** (five non-thickenable rank‑2 sources; 75,095 pool rows):

| from → | 0 | 1 | 2 | 3 | total |
|---|---|---|---|---|---|
| 1 | **0** | 8,306 | 9,925 | 111 | 18,342 |
| 2 | 0 | 216 | 49,685 | 3,430 | 53,331 |
| 3 | 0 | 0 | 252 | 2,672 | 2,924 |

---

## 3. The `1 → 0` cell, and its opportunities

> **`1 → 0` count: 0 (measured).**
> **Opportunities: 56,388 single-SPLIT applications to a state at `γ_N = 1`** (measured),
> from **1,958 distinct `γ_N = 1` parent states** at parent ranks 9, 10, 11 and 12, across
> all three source families. Plus **184** applications whose outcome is unobserved (the
> child is a rank‑13 state left undecided) — a worst case that cannot change "0 observed in
> 56,388 observed outcomes".

Distinct `γ_N = 1` parents by family and rank (measured):

| family | rank 9 | rank 10 | rank 11 | rank 12 | total |
|---|---|---|---|---|---|
| AK(3) | 0 | 51 | 31 | 0 | 82 |
| control0 (thickenable) | 0 | 359 | 740 | 14 | 1,113 |
| control2 (non-thickenable) | 31 | 351 | 326 | 55 | 763 |
| **all** | 31 | 761 | 1,097 | 69 | **1,958** |

**This is not a case where emptiness is uninformative for want of opportunities.** The
repo's calibration rule (`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`)
demands that the number be stated loudly, so: **56,388.** Four independent reasons the
opportunity count is adequate, each with its own number:

1. **The target value is producible by this instrument at these ranks.** 916 distinct
   `γ_N = 0` states were produced *as SPLIT children* — 117 at rank 10, 40 at rank 11,
   759 at rank 12 (measured). So neither the search nor the decider is blind to `γ_N = 0`
   in the rank band where the `1 → 0` null is being read. What is absent is arriving at 0
   from a **positive** parent: all 916 came from `γ_N = 0` parents.
2. **SPLIT demonstrably lowers `γ_N`.** 1,325 descents were observed (1,049 `2→1`, 276
   `3→2`). Descent is a common event, not a hypothetical one.
3. **Extrapolating the measured descent rates predicts a non-trivial count.** The rate falls
   by a factor 8.598 / 0.940 = 9.14 per level; continuing that geometric decay gives a
   predicted `1 → 0` rate of ≈ 0.103 %, i.e. **≈ 58 expected hits** in 56,388 tries. If
   instead the `1 → 0` rate simply equalled the measured `2 → 1` rate, the prediction is
   **≈ 530**. Observed: 0. *Both figures are **asserted** extrapolations under an assumed
   rate-transfer model, not tests.* **No p-value is quoted and none should be**: class
   members come from a move tree and are not independent draws
   (`experiments/lessons/contrast-length-confound.md`).
4. **A same-corpus positive control exists — but only at rank 5.** The already-persisted
   depth‑1 flip census (`s4b_flips.jsonl`, 81 measured parents, rank‑5 triangulations of
   length‑9 AC-trivial sources) ran two arms on *the same parents*:

   | arm | `1 → 0` | opportunities at `γ_N = 1` | rate |
   |---|---|---|---|
   | SPLIT | **0** | 1,470 | 0 |
   | AC2 slide (control arm) | **14** | 1,470 | 0.95 % |

   So "reach `γ_N = 0` in one move from a `γ_N = 1` state" is an attainable event for a
   neighbouring move family on the very same states, and SPLIT specifically does not do it.
   **This positive control exists only at rank 5.** At ranks 9–13 no move of any kind has
   been shown here to take a `γ_N = 1` state to `γ_N = 0` in one step; that is the honest
   gap, and it is why reason 1 (the instrument does emit `γ_N = 0` at ranks 10–12) is
   carrying the calibration in the high-rank band rather than an external control.

   A second, *multi-step* positive control landed in a parallel line this session:
   `S21_MATCHED_NEGATIVE.md` reports the `s12_hunt` slide instrument reaching `γ_N = 0`
   on 35 of 40 runs from AC-trivial rank‑2 roots matched to AK(3) at `γ_N = 2`. That is a
   **different move family and a whole search, not one step**, so it is not a `1 → 0`
   single-step control; what it does show is that `γ_N = 0` is reachable from `γ_N = 2` by
   *some* move sequence, which is exactly what makes SPLIT's 0 creations in 174,178 single
   steps a statement about SPLIT rather than about the target value being unreachable.
   [Read from a parallel agent's write-up; **not re-verified here**.]

Pooling the two SPLIT measurements: **`1 → 0` is 0 in 57,858 opportunities** (56,388
reconstructed here at ranks 9–13 and depths 0–3, plus 1,470 already on disk at rank 5,
depth 1), from 1,958 distinct `γ_N = 1` parents in the reconstructed part plus however many
of the flip census's 81 measured parents sat at `γ_N = 1` — that split is not persisted in
`s4b_flips.jsonl`, so it is **not reconstructible** and is not imputed here.

**Depth coverage, stated because the repo has been burned by depth‑1-only corpora**
(`experiments/lessons/conjectures-tested-only-at-depth-one.md`): the parents in this table
sit at chain depths 0, 1, 2 and 3 — 1,755 edges out of depth 0, 3,923 out of depth 1,
143,356 out of depth 2 and 27,450 out of depth 3 (measured). The `γ_N = 1` row is populated
at every one of those depths: 505 edges out of depth 0, 1,680 out of depth 1, 51,885 out of
depth 2 and 2,318 out of depth 3 (measured). This is **not** a depth‑1 corpus.

---

## 4. The already-thickenable control: how often SPLIT *destroys* a certificate

`γ_N = 0` parents exist only in the control0 family (source `('XYXXY','XXYXYXXY')`, the one
source that is itself `SPHERICAL`), so the control-restricted table and the pooled `γ_N = 0`
row are the same 3,017 pairs.

| from `γ_N = 0` → | 0 | 1 | 2 | row total |
|---|---|---|---|---|
| count | 916 | 1,451 | 650 | 3,017 |

> **Certificate destruction rate: 2,101 / 3,017 = 69.6 %** (measured). A single SPLIT applied
> to a thickenable state destroys thickenability roughly seven times in ten; it preserves it
> 916 times (30.4 %).

An independent confirmation at a completely different rank, already on disk: the rank‑5
depth‑1 flip census gives 643 / 960 = **67.0 %** destruction. Two measurements, ranks 5 and
9–12, agree to within 3 points.

**Why this is the right comparison for "how hard is reaching 0".** The instrument is not shy
about the boundary between `γ_N = 0` and `γ_N > 0` — it crosses it 2,101 times *downward in
quality* (0 → positive) and 916 times it stays. It crosses it **0 times upward** in 56,388
tries from `γ_N = 1` and **0 times** in 174,178 tries from any positive `γ_N` at all
(`n_creations_positive_to_zero = 0`). The barrier is entirely one-way in this data.

Full control0 table for completeness (measured):

| from → | 0 | 1 | 2 | 3 | total |
|---|---|---|---|---|---|
| 0 | 916 | 1,451 | 650 | 0 | 3,017 |
| 1 | **0** | 22,042 | 14,849 | 23 | 36,914 |
| 2 | 0 | 697 | 11,183 | 16 | 11,896 |

---

## 5. Robustness: the sub-table with no `sum|δ|` conditioning

The pool only persists states with `sum|δ| ≤ 4`, so any edge whose **child** sits at chain
depth 3 or 4 is conditioned on the child being near-cubic. The depth‑0→1 and depth‑1→2 layers
are reconstructed from trace prefixes and carry **no such condition on either endpoint**.
Split out (measured):

| | from 0 | from 1 | from 2 | total |
|---|---|---|---|---|
| **unconditioned layers** (parent rank 9 or 10) | {0:157, 1:535, 2:33} = 725 | **{0:0**, 1:1256, 2:927, 3:2} = 2,185 | {1:67, 2:2691, 3:10} = 2,768 | 5,678 |
| conditioned layers (child pooled, `sum|δ| ≤ 4`) | 2,292 | 54,203 | 108,795 | 168,500 |

In the unconditioned layers alone: **`1 → 0` is 0 in 2,185 opportunities**, while `2 → 1`
runs at 67 / 2,768 = 2.4 % — a *higher* descent rate than the pooled 0.94 %. The null is not
an artifact of the near-cubic filter.

---

## 6. Verdict

**(a) — supported, with adequate opportunities.** "SPLIT can lower `γ_N` but never to 0" is
supported by 174,178 reconstructed single-step pairs: 1,325 descents observed, 0 of them into
`γ_N = 0`, with 56,388 opportunities at `γ_N = 1` from 1,958 distinct parents at four ranks
and three source families (57,858 opportunities pooling in the rank‑5 depth‑1 census). It is not
(b): the emptiness is not for want of opportunities — the instrument emits `γ_N = 0` states
at ranks 10–12 (916 of them), descends `γ_N` by one 1,325 times, and a sibling move (AC2)
achieves `1 → 0` on the same parents at rank 5 at 0.95 %. It is not (c): **no transition in
any of the data refutes it** — no `1→0`, no `2→0`, no `3→0`, and no `3→1`, so descent is
always by exactly one and never terminates at 0.

**What this is NOT.** It is an **instrument fact about this move set, this beam and this
budget**, exactly as `S16` §4 said, now with the row structure and the opportunity count
attached. It is **not** a theorem that a SPLIT cannot lower `γ_N` to 0, and it is **not** an
obstruction.

**Bound direction, because this is the repo's most expensive recurring trap**
(`experiments/lessons/parallel-runs-and-bound-direction.md`): every instrument here bounds
`Γ(P) = min{γ_N(Q) : Q ~_st P}` from **ABOVE**. Exhibiting a `γ_N = 0` state would prove
`Γ ≤ 0`. Failing to exhibit one proves nothing at all about `Γ` from below. The empty `1 → 0`
cell therefore **cannot** be read as "AK(3) is far from thickenable", and the 69.6 %
destruction rate **cannot** be read as a lower bound on anything. The single legitimate
reading is the design one: *a search whose only `γ_N`-lowering move never lands on 0 cannot
certify a root with `γ_N > 0`.*

**Two caveats that limit even the instrument reading.** (i) The beam keeps ≤ 40 children per
level (70 % ranked by a cost built from `sum|δ|`, 30 % uniform random), so these edges are a
biased sample of all SPLIT children — biased on distance-to-cubic, not directly on `γ_N`, but
biased. (ii) Depth‑1 and depth‑2 states are reconstructible only when they are ancestors of a
pooled state, so the unconditioned sub-table of §5 is selected on having near-cubic
descendants.

---

## 7. Status of every quantitative claim in this file

| # | claim | status |
|---|---|---|
| §1 | 170,679 chains replayed, 0 failures, 0 terminal mismatches, 400/400 `verify_split` | **measured** (this session) |
| §1 | 176,484 distinct edges, 174,178 in the table, 2,306 dropped (child undecided), 184 of them from a `γ_N=1` parent | **measured** |
| §2 | the 4×4 matrix and all layer/family sub-tables | **measured**: read from persisted decided rows where available, computed with `fast_min_defect` (cap 400,000) otherwise |
| §2 | descent rates 8.598 % / 0.940 % / 0 % | **measured** (ratios of the measured counts) |
| §3 | `1→0` = 0 with 56,388 opportunities, 1,958 distinct parents | **measured** |
| §3 | 916 `γ_N = 0` states produced as SPLIT children at ranks 10–12 | **measured** |
| §3 | "≈ 58 expected" and "≈ 530 expected" | **asserted** extrapolations under an assumed rate-transfer model; **not** tests, and deliberately not p-values |
| §3 | AC2 arm `1→0` = 14 / 1,470 vs SPLIT 0 / 1,470 at rank 5 | **read from disk** (`s4b_flips.jsonl` flip_summary, measured in an earlier session) |
| §4 | destruction rate 2,101 / 3,017 = 69.6 % | **measured** |
| §4 | rank‑5 destruction 643 / 960 = 67.0 % | **read from disk** |
| §5 | unconditioned sub-table, `1→0` = 0 / 2,185, `2→1` = 67 / 2,768 | **measured** |
| §1 | independent-decider spot check, 4 states | **measured**, and weak: only 4 states, and the `γ_N = 0` side came back inconclusive from the cut-scheme solver |
| §3 | `s12_hunt` reaching `γ_N = 0` 35/40 from matched `γ_N = 2` rank‑2 roots | **read from a parallel agent's `S21_MATCHED_NEGATIVE.md`**, not re-verified here; it is a multi-step search rate, not a single-step transition |
| §6 | verdict (a) | **inference** from the measurements above; an instrument fact, not a theorem |
| §6 | "bounds `Γ` from ABOVE" | **established** in `S15_ONE_SIDEDNESS.md` §4, cited |

Nothing here is a proof or a disproof of the AC or the stable AC conjecture, and nothing here
distinguishes AK(3) from a generic non-thickenable balanced trivial-group presentation —
`S16`'s retraction stands untouched.

Reproduce with:

```
python3 -m experiments.stable_ac.fable.s17_transition_table --budget 215 \
    --extra-decided results/stable_ac/fable/s4b_ctrl2_full_decided.jsonl.gz
```
