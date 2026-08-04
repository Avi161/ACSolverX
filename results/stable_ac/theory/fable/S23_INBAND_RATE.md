# S23 — Is the IN-BAND certificate creation rate ever nonzero, and does extra rank help it?

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch. No
PR opened (`FRAMING.md` trap 10). **Nothing here proves or disproves the AC or the stable AC
conjecture**, and nothing here is a claim about AK(3)'s stable class.

New code, this file only: `experiments/stable_ac/fable/s23_inband_rate.py`
(`controls` | `hunt` | `table`). It modifies nothing; `s12_hunt`, `s21_audit_gen_replay` and
`s18_s5_chain_audit` are imported read-only.

Units: `defect` is the UNHALVED Neuwirth defect, **`γ_N = defect // 2`**
(`experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md`). AK(3) has
`minimum_defect` 4, i.e. `γ_N = 2`. **Bound direction:** every hit certifies `γ_N = 0` for
that state and so bounds `γ_N` from **ABOVE**; every null bounds **nothing** from below
(`experiments/lessons/parallel-runs-and-bound-direction.md`). **No p-values** are quoted:
per-trial probability is target-specific and move-tree states are not independent draws
(`experiments/lessons/contrast-length-confound.md` rule 3).

---

## 0. The question, and the answer in four sentences

Trap **T-S20** killed target-versus-control comparison by showing that every control hit
escapes *downward in length* into the Havas–Ramsay region AK(3) cannot enter. The only
remaining meaningful form of the brief's question is therefore:

> **Is the IN-BAND creation rate ever nonzero — for anyone — and does extra rank help it?**

1. **It is nonzero, but barely: exactly one in-band creation in 48 rank-ceiling-2 trials
   across six roots**, and 26 of the other 27 hits leave the band. The single witness is
   fully verified (8 legal AC moves, root exact defect 4, witness exact `γ_N = 0`, every
   chain node of total length ≥ 13), so "certificate-hunting in band is impossible" is
   **false**.
2. **It does not rise with rank. At a decide-matched budget the raw rate falls 4/10 at
   ceiling 2 to 0/10 at ceiling 3**, and the in-band rate is 0 at every ceiling ≥ 3 in every
   run recorded here — confirming A18's direction (extra rank hurts) on a five-control set,
   with the sharp qualification that **ceilings 4 and 5 are instrument-starved** (median 32
   and 88 decided states per run) and their nulls are therefore uninformative.
3. **The one in-band witness does not rescue the comparison — it exposes a second exit.**
   Its whole chain carries the length-4 relator `XXXY = x⁻³y⁻¹`, which is a **primitive**
   element of `F(x,y)`; and across all 27 hits, **27 of 27 chains pass through a state with a
   relator of length ≤ 5, and 0 of 27 keep every relator at length ≥ 6** (AK(3)'s minimum
   relator length). T-S20 recurs one level finer: total length ≥ 13 is not the only door.
4. Incidental but the cleanest single observation in the file: **the one control matched to
   AK(3) on relator shape `[6,7]` *and* free of a unit abelianisation row (`C3walk`) scored
   0/8 — exactly like AK(3)** — while the four controls that differ on those axes scored
   5/8, 6/8, 8/8, 8/8.

---

## 1. The instrument, and why the budget is denominated in DECIDES

The hunt is `s12_hunt.hunt`'s move family and decider, reached through
`s21_audit_gen_replay.hunt_tracked`'s parent tracking. `s23_inband_rate.hunt_budgeted` is a
faithful clone of that clone with **two added stopping criteria and nothing else changed**
(same `s12_hunt.slides`, same `s12_hunt.decide`, same cyclically-reduced seen-set, same RNG
call order).

The reason for the change is a measured instrument asymmetry [MEASURED, this clone]:

| state | decider path | cost per decided state |
|---|---|---|
| rank 2, length ≈ 13–20 | `r1c_v2_solver` (cut schemes) | ≈ 0.001–0.002 s |
| rank ≥ 3 | `classify_cut_support` → **UNSUPPORTED** → factorial census | ≈ 0.5–1.5 s, up to ≫ 10 s |

At rank ≥ 3 the R1c-v2 solver declines every state sampled and everything falls through to
the census, so a *pop*-denominated budget hands the rank-2 arm several hundred times more
decided states per second than the rank-5 arm. "Extra rank hurts" would then be a statement
about the decider's speed. The ladder below is therefore budgeted in **decided states**
(`decide_budget = 250`), with a node cap of 2,000 (the session cap) and a 220 s per-run
wall-clock safety net. Every run records `pops`, `decided`, `undecided` and its **stop
reason**, and those columns are printed beside every verdict
(`experiments/lessons/instrument-the-search-before-reading-its-null.md`).

Persistence: one JSONL row is appended and `fsync`ed per (ceiling, trial), so an interrupted
run still leaves every completed trial on disk. This run *was* stopped at its wall-clock
budget, and §5 says exactly which cells that truncated.

## 2. In band — the two definitions actually used

| name | test |
|---|---|
| **weak** | `min` over **every node of the chain** of total length ≥ 13 |
| **strong (elim)** | weak, **and** the witness's `elim` core has total length ≥ 13 |
| **strong (tietze)** | weak, **and** the witness's `tietze` core has total length ≥ 13 |

The core reductions are `S18_S5_RECHECK.md`'s, reused verbatim
(`s18_s5_chain_audit._elim_once`, `._tietze_kill_unit`), not reinvented: `elim` deletes every
generator occurring exactly once (AC3 + one ambient automorphism + AC5 — stable-AC legal at
rank 2, **[ASSERTED] at rank > 2**, `FRAMING.md` trap 2); `tietze` deletes every bare-generator
relator and strikes that generator everywhere (group-legal, **not** an AC move — a structural
description, hence the strictest reading). Two further chain-wide variants (no node anywhere
on the chain has a short core) are computed and stored; they agree with the witness-only
variants on every row here.

Rationale, from T-S20: total length is inflatable by inert AC4 discs, so a long witness can
be a short core in costume.

## 3. The controls [MEASURED]

Requirement: rank 2, total length 13, **exact-census** `minimum_defect` 4 (`γ_N = 2` —
AK(3)'s own descent depth), AC-trivial, and **no relator shared with any other control**.

A measured obstacle worth recording. Of the **118** members of `data/ms640_solved.txt` of
total length 13, the exact census gives `{defect 2: 108, defect 4: 4, undecided: 6}` — and
**all four defect-4 members share the relator `YYXyx`** (`s23_provenance.json`). The solved
Miller–Schupp ladder can therefore contribute exactly **one** defect-4 control without a
shared-relator artifact. The other four come from the second, unrelated source.

| label | source | presentation | shape | ab. rows | unit row? | census | defect | γ_N |
|---|---|---|---|---|---|---|---|---|
| `C1ms` | MS ladder (`ms640_solved`) | `⟨x,y \| YYXyx, YXYXXyxx⟩` | [5,8] | (0,−1),(−1,−1) | yes | 86,400 | **4** | 2 |
| `C2walk` | fresh AC walk, 74 steps | `⟨x,y \| xYXyx, YxyyXYXY⟩` | [5,8] | (1,0),(−1,−1) | yes | 86,400 | **4** | 2 |
| `C3walk` | fresh AC walk, 59 steps | `⟨x,y \| xYXXXYx, yxYXyx⟩` | **[6,7]** | (−1,−2),(1,1) | **no** | 120,960 | **4** | 2 |
| `C4walk` | fresh AC walk, 70 steps | `⟨x,y \| YxYXXyyxx, XXXY⟩` | [4,9] | (1,0),(−3,−1) | yes | 120,960 | **4** | 2 |
| `C5walk` | fresh AC walk, 43 steps | `⟨x,y \| YYXyyxyX, XyxyX⟩` | [5,8] | (−1,1),(−1,2) | **no** | 86,400 | **4** | 2 |
| **AK(3)** | target | `⟨x,y \| xyxYXY, xxxYYYY⟩` | **[6,7]** | (1,−1),(3,−4) | **no** | 86,400 | **4** | 2 |

Every root is `NOT_SPHERICAL` by **exact census** (a solver verdict was not accepted for a
root). AC-triviality: `C1ms` is a solved Miller–Schupp instance; the four walk controls carry
an explicit AC chain from `⟨x,y | x,y⟩`, and all four chains were **independently
re-verified** step-by-step by `s21_audit_gen_replay.verify_chain` — **0 bad steps in
74 + 59 + 70 + 43 = 246 moves**, every chain starting at `("x","y")`
(`s23_provenance.json`).

## 4. Run A — rank ceiling 2, node budget 2,000 [MEASURED, artifact `s23_pow_*.jsonl`]

8 trials × 6 roots = 48 runs, `branch = 6`, `headroom = 4`, distinct seed per trial. This is
the *power* arm: at rank 2 the decider is cheap, so the full 2,000-node cap is affordable.

| root | raw hits | created | **weak in band** | **strong (elim)** | **strong (tietze)** | trials |
|---|---|---|---|---|---|---|
| `C1ms` | 6 | 6 | 0 | 0 | 0 | 8 |
| `C2walk` | 5 | 5 | 0 | 0 | 0 | 8 |
| `C3walk` | **0** | — | 0 | 0 | 0 | 8 |
| `C4walk` | 8 | 8 | **1** | **1** | **1** | 8 |
| `C5walk` | 8 | 8 | 0 | 0 | 0 | 8 |
| **pooled controls** | **27** | **27** | **1** | **1** | **1** | **40** |
| **AK(3)** | **0** | — | 0 | 0 | 0 | **8** |

Every one of the 27 hits is a **creation**: chain defect starts at 4 and ends at 0 (no chain
starts at the property — the T-S19 test passes).

Minimum total length reached on the 27 hit chains:

```
 2  3  4  4  4  4  5  5  7  7  7  7  8  8  9  9  9  9  9  9  9 10 10 10 11 11 | 13
 ^--------------------- 26 of 27 leave the band ---------------------------^   in band
```

T-S20 reproduced exactly, now with full chain records rather than endpoints: **the raw rate
27/40 = 0.68 on the controls collapses to 1/40 = 0.025 once the chain is required to stay in
band**, and AK(3)'s 0/8 is what a 0.025 rate predicts.

## 5. Run B — the rank ladder at a matched decide budget [MEASURED, artifact `s23_rows_*.jsonl`]

Rank ceiling = `2 + kstab` (kstab fresh generators adjoined as bare relators; the move family
never introduces a letter, so no state exceeds the ceiling). 2 trials per (root, ceiling),
`decide_budget = 250`, node cap 2,000, per-run wall cap 220 s.

| rank ceiling | arm | trials | raw | weak in band | strong (elim) | strong (tietze) | decides min/median/max | stop reason |
|---|---|---|---|---|---|---|---|---|
| **2** | controls | 10 | **4** | 0 | 0 | 0 | 85 / 250 / 252 | 6 budget, 4 hit |
| **2** | AK(3) | 2 | 0 | 0 | 0 | 0 | 250 / 250 / 250 | 2 budget |
| **3** | controls | 10 | **0** | 0 | 0 | 0 | 46 / 250 / 253 | 6 budget, 4 wall |
| **3** | AK(3) | 2 | 0 | 0 | 0 | 0 | 250 / 251 / 251 | 2 budget |
| **4** | controls | 9 | 0 | 0 | 0 | 0 | **7 / 32 / 153** | **9 wall** |
| **4** | AK(3) | 2 | 0 | 0 | 0 | 0 | 30 / 216 / 216 | 2 wall |
| **5** | controls | 4 | 0 | 0 | 0 | 0 | **55 / 88 / 164** | **4 wall** |
| **5** | AK(3) | 1 | 0 | 0 | 0 | 0 | 52 / 52 / 52 | 1 wall |

**Read the `decides` and `stop` columns before reading the zeros.** Across ceilings 2 and 3,
**16 of 24 runs reached the matched 250-decide budget**, 4 stopped early *because they hit*,
and 4 were cut by the wall clock (at 46–164 decides); so that comparison is meaningful. Ceilings 4 and 5 did **not**: every single run there was cut
off by the wall clock after a median of 32 and 88 decided states, one to two orders of
magnitude short of the matched budget. A single decide at rank 4–5 on a long relator was
measured at up to ~60 s. **The ceiling-4 and ceiling-5 nulls are uninformative** — they are
what a starved search returns, not a property of rank 4 and 5
(`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`,
`…/instrument-the-search-before-reading-its-null.md`).

**Truncation, stated plainly:** the job was stopped at its wall-clock budget with **40 of the
48 planned runs complete**. The missing 8 are ceiling-5 trials (`C1ms` has all 8 of its runs;
`C2walk`/`C3walk` have no ceiling-5 row at all; `C3walk` is missing one ceiling-4 row). Those
cells are absent from the table, not counted as zeros.

## 6. The one in-band witness, dissected [MEASURED + independently re-verified]

`C4walk`, trial 4, seed 20292480, 331 pops / 207 decided states, `stop = hit`.

```
root    L13 rank2 defect 4   <x,y | YxYXXyyxx, XXXY>
        L22 rank2            <x,y | YxYXXyyxx, XXXYXXYYxxyXy>
        L17 rank2            <x,y | XXXY, XXXYXXYYxxyXy>
        L19 rank2            <x,y | XXXY, XXXYXXYYxxyxyxy>
        L15 rank2            <x,y | XXXY, XXYYxxyxyxy>
        L17 rank2            <x,y | XXXY, XYYxxyxyxyxxy>
        L21 rank2            <x,y | XXXY, XYYxxyxyxyxxxxyxy>
        L21 rank2            <x,y | XXXY, XYYxxyxyxyxxxxyXX>
witness L15 rank2 defect 0   <x,y | XXXY, xxyxyxyxxxx>          SPHERICAL, gamma_N = 0
```

* all 8 steps re-verified as legal AC moves by `s21_audit_gen_replay.verify_chain` — **8/8**;
* root defect **4** by exact census (120,960 cases), witness `SPHERICAL` by the R1c-v2 solver;
* rank 2 throughout, so `elim` core = `tietze` core = the state itself — **strong in band
  under both definitions, and chain-wide**;
* minimum total length on the chain **13** — it never leaves the band.

So this is a real, in-band, created `γ_N = 0` certificate from a `γ_N = 2` root at rank 2.
The existence claim in §0.1 rests entirely on this one chain, and the chain is clean.

**And it still is not a control rate AK(3) can be compared against.** `XXXY = x⁻³y⁻¹` is a
**primitive** element of `F(x,y)`: `{x, x⁻³y⁻¹}` is a generating pair, hence a free basis, so
the root is one change of basis from `⟨x,y | w, y⟩`. That relator is present in the root and
in every node from step 2 onward — the chain stays "in band" by total length only because the
*other* relator stays long. AK(3) has no relator of length < 6 and no unit abelianisation row.

The general form of this, across **all 27** Run-A hits [MEASURED]:

| shortest relator ever reached on the hit's chain | 1 | 2 | 3 | 4 | 5 | ≥ 6 |
|---|---|---|---|---|---|---|
| hits | 7 | 3 | 7 | 9 | 1 | **0** |

**Zero of 27 hits keep every relator at length ≥ 6.** The length band was the door T-S20
closed; the short-relator regime is a second door, and every hit recorded here goes through
one or the other. A third band criterion — *no relator on the chain shorter than the target's
shortest* — is the obvious next iteration, and under it the in-band rate measured here is
**0/40 on the controls**, the same value AK(3) returns.

## 7. The two questions, answered

**(i) Is the in-band creation rate zero everywhere, or nonzero somewhere?**
**Nonzero — but only just, and only at rank ceiling 2.** One in-band creation in 48 trials at
the 2,000-node budget (1/40 = 0.025 on the controls; 0/8 on AK(3)); zero in-band creations in
all 40 runs of the decide-matched ladder, at every ceiling including 2. Certificate-hunting in
band is not *impossible* — the existence proof is §6 — but at these budgets it is a
~2–3 % per-trial event on the one control of five that admits it, and AK(3)'s null is exactly
what such a rate predicts. **The instrument is one-sided: this bounds `γ_N` from above on the
states it certifies and bounds nothing at all from below.**

**(ii) Does the in-band rate rise, fall, or stay flat with rank ceiling?**
**It does not rise.** At the matched decide budget the *raw* rate falls from 4/10 (ceiling 2)
to 0/10 (ceiling 3), and the in-band rate is 0 at every ceiling ≥ 3 in every run here. This
**confirms A18's direction** (8/40 at ceiling 2 against 0/32 at ceilings 3–6) on a five-control
set built from two unrelated sources rather than one control — with two qualifications that
must travel with the number:

* the ceiling-2 → ceiling-3 comparison is decide-matched (median 250 vs 250) and is the part
  that carries information;
* the ceiling-4 and ceiling-5 cells are **starved, not negative**. They bound nothing. If
  extra rank helped at ranks 4–5, this instrument could not have seen it: it decided a median
  of 32 and 88 states per run there against 250 at ceilings 2–3.

**Consequence for the brief's hypothesis.** No support was found for "extra rank makes
certificates easier to create", and the one honest measurement of the rank axis points the
other way at fixed detection power. This agrees with `S22_FINAL_ANSWER.md` §1 and adds the
missing in-band control: it is now measured that the in-band rate at rank 2 is nonzero, so
"the rank-3+ zeros are just the in-band rate being zero for everyone" is **not** the whole
explanation at ceiling 3 — the ceiling-2 arm found an in-band certificate under the same
protocol and the ceiling-3 arm did not.

## 8. Status of every claim

| # | claim | status |
|---|---|---|
| §3 five controls, exact defect 4, no shared relator | exact census per root, `s23_controls*.json` | **measured** |
| §3 only 4 of 118 length-13 MS members have defect 4, all sharing `YYXyx` | exact census over all 118, `s23_provenance.json` | **measured** |
| §3 walk controls AC-trivial | explicit chains from `⟨x,y\|x,y⟩`, 246/246 steps re-verified | **measured** |
| §4 27/40 raw, 1/40 in band, AK(3) 0/8, 27/27 created | `s23_pow_*.jsonl`, 48 rows on disk | **measured**, bounded budget |
| §5 ladder table | `s23_rows_*.jsonl`, 40 rows on disk | **measured**, bounded budget |
| §5 ceilings 4–5 starved | `stop = wall_budget` on 16/16 such runs; decide counts recorded | **measured** |
| §6 the in-band chain, 8/8 legal, defect 4 → 0 | chain **reconstructed** from the parent tree, then each node decided independently | **measured** (chain *reconstructed*, not imputed) |
| §6 `XXXY` is primitive in `F(x,y)` | `{x, x⁻³y⁻¹}` generates `F(x,y)`; a 2-element generating set of `F₂` is a basis | **proved** |
| §6 0 of 27 hits stay above relator length 6 | recomputed from the persisted chains | **measured** |
| §7 A18's 8/40 vs 0/32 | quoted from `S18_S5_RECHECK.md` §5 | **cited**, not re-run here |
| "AK(3) cannot go below total length 13" | Havas–Ramsay via `FRAMING.md` §1 | **cited**, not re-verified this session |
| `elim` reduction legal at rank > 2 | stable ambient automorphism principle beyond rank 2 | **[ASSERTED]**, `FRAMING.md` trap 2 |

The reported chain is the first-seen-parent path from root to witness, so it is *a* legal AC
chain, not necessarily a shortest one; every step was independently re-checked.

Every rate in this file is the detection rate of a **one-sided, upper-bound-only** instrument
at a bounded budget. Nothing here bounds `γ_N` on AK(3)'s stable class from below, and the
AK(3) zeros in §§4–5 are not evidence about AK(3).

## 9. Artifacts and reproduction

New code: `experiments/stable_ac/fable/s23_inband_rate.py`. **The version of this script
committed in `982ca8a` is an earlier draft**; the working-tree version (with `hunt_budgeted`
and the `--decide-budget` / `--branch` flags) is the one that produced every artifact below,
and it is uncommitted — this agent was instructed not to commit.

One field in the two `table` artifacts is named misleadingly and must not be quoted:
`starved_runs(pops<budget and no hit)` counts every run that stopped before the 2,000-node
cap, which in the matched ladder is *every* run, since the stopping criterion there is the
decide budget. The real starvation evidence is the `decides` and `stop` columns of §5.

New artifacts, all under `results/stable_ac/fable/`:
`s23_controls.json`, `s23_controls_b.json`, `s23_provenance.json`,
`s23_pow_{C1ms,C2walk,C3walk,C4walk,C5walk,ak3}.jsonl`,
`s23_rows_{…}.jsonl`, `s23_table_power_ceil2.json`, `s23_table_matched.json`.

```
python -m experiments.stable_ac.fable.s23_inband_rate controls \
    --want-ms 3 --want-walk 3 --time-budget 300 --out results/stable_ac/fable/s23_controls.json

python -m experiments.stable_ac.fable.s23_inband_rate hunt \
    --root YxYXXyyxx,XXXY --label C4walk --source control \
    --ceilings 2 --trials 8 --nodes 2000 --branch 6 --seed 20260804 \
    --out results/stable_ac/fable/s23_pow_C4walk.jsonl

python -m experiments.stable_ac.fable.s23_inband_rate hunt \
    --root YxYXXyyxx,XXXY --label C4walk --source control \
    --ceilings 2,3,4,5 --trials 2 --nodes 2000 --branch 6 --seed 20260804 \
    --decide-budget 250 --wall-budget 220 \
    --out results/stable_ac/fable/s23_rows_C4walk.jsonl

python -m experiments.stable_ac.fable.s23_inband_rate table \
    --rows 'results/stable_ac/fable/s23_rows_*.jsonl' \
    --out results/stable_ac/fable/s23_table_matched.json
```

Whole job: controls built 10:46–10:55 UTC (2026-08-04, two `controls` invocations of 300.6 s
and 200.8 s), hunts launched 10:55:41 and stopped at 11:22:14 UTC — **26 min 33 s wall clock
on 4 cores**, all searches ≤ 2,000 nodes, all processes `nice -n 10`, `ps` checked before
launch. Timestamps read from `date -u`, not estimated.

## 10. What the next iteration should do

1. **Add the relator-length band.** Require that no state on the chain has a relator shorter
   than the target's shortest (6 for AK(3)). Under it the measured control rate is 0/40 and
   AK(3)'s 0/8 is again exactly predicted — which means the honest statement is now
   *"every mechanism this instrument has for creating certificates is one AK(3) is denied"*,
   the T-S20 verdict at finer grain, and the fourth successive confirmation that
   target-versus-control is the wrong instrument.
2. **`C3walk` deserves its own experiment.** It is the only control matched to AK(3) on shape
   `[6,7]` and on the absence of a unit abelianisation row, and it is the only control that
   behaves like AK(3) (0/8). One root at n = 8 is an observation, not a result; a matched
   family of `[6,7]`-shaped, no-unit-row, defect-4 controls would test whether *shape*, not
   difficulty, is what the whole control programme has been measuring.
3. **A cheaper rank ≥ 4 decider is the binding constraint.** The R1c-v2 cut-scheme solver
   declines every rank ≥ 3 state sampled here, so the census carries the whole load and costs
   0.5–60 s per state. Until that is fixed, no honest statement about ranks 4–6 can be made at
   any budget this session type can afford — and any file that reports a rank ≥ 4 zero without
   its decide count is reporting starvation.
