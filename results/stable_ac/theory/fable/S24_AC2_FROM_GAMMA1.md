# S24 — AC2-driven search launched from AK(3)'s own `γ_N = 1` states

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch. No
PR opened (`FRAMING` trap 10). **No existing file under `experiments/` was modified and no
existing `.md` was edited**; the only new code is
`experiments/stable_ac/fable/s24_ac2_from_gamma1.py`. Nothing was committed or pushed.

---

# VERDICT: **NULL, AND THE NULL IS UNINFORMATIVE — BY ITS OWN CONTROL**

**Nothing reached `γ_N = 0`.** Not on AK(3)'s class, and **not on either control either**.
The control's measured detection rate is **0/18**, so by the repo's own calibration rule
(`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`) AK(3)'s 0/22 is
worth exactly nothing: *a one-sided hunt's silence is worth its measured detection rate, and
this instrument's is zero.* The AK(3) null is reported here so it is on record, and it must
not be quoted as evidence about AK(3).

**What the experiment did produce is a mechanism finding about the instrument**, and it is
artifact-backed: the binding constraint at rank 12 is **not** the node budget (every one of
the 60 trials reached its 400-pop budget) but the **decider on planar survivors**. 95.9 % of
AK(3)-class children were rejected in ~12 ms each by the certified planarity test; of the
4.1 % that survived, **97.8 % could not be decided at all** inside the budget.

Nothing here proves or disproves the AC or the stable AC conjecture.

---

## 1. The launch set (measured)

All states with `minimum_defect = 2` — i.e. **`γ_N = 1`**, since `γ_N = minimum_defect // 2`
(`experiments/lessons/stabilization-that-only-rebookkeeps-is-inert.md`) — extracted from the
three persisted decided pools by `s24_ac2_from_gamma1 launch`
(artifact `results/stable_ac/fable/s24_launch_set.json`, 19.2 s):

| family | pool file | rows at `minimum_defect = 2` | distinct states | ranks | verify sample |
|---|---|---|---|---|---|
| **AK(3)** | `s4b_decided.jsonl.gz` | **527** | **527** | all rank 12 | **12/12 agree** |
| control0 (thickenable rank-2 root) | `s4b_control_decided.jsonl.gz` | 23,083 | 23,083 | 22,835 @ 12, 248 @ 13 | **12/12 agree** |
| control2 (non-thickenable rank-2 roots) | `s4b_ctrl2_decided.jsonl.gz` | 4,986 | 4,986 | 3,920 @ 12, 1,066 @ 13 | **12/12 agree** |

The 527 is exactly the number the brief quoted, and it is **not taken on the persisted
number's word**: a random sample of 12 per family was re-decided in this session with the
repo's own exact census (`s18_s5_chain_audit.defect_of`, cap 200,000) and **36 of 36
recomputations returned `minimum_defect = 2`** (`verify_rows` in the artifact carry the
per-state method and verdict). Every AK(3) launch state has total length 36 and minimum
relator length 3 (they are cubic rank-12 refinements).

**Class membership.** `cubic_split_search`'s own docstring states that every pooled state is
reached from its source by **AC4 + AC1–AC3 only**, so a `γ_N = 0` hit on any of the 527 would
settle AK(3) as stably AC-trivial through Lackenby Thm 1.3. That chain of custody is
**[ASSERTED, read from the producing module's docstring, not re-verified here]**, and Thm 1.3
itself is **[unverified this session]** (`S22` §5). No hit occurred, so nothing rests on it.

### 1a. Planarity of the launch states themselves (measured)

150-state random sample per family (`s24_launch_planarity.json`, 4.1 s):

| family | sampled | planar | non-planar | non-planar **certified** |
|---|---|---|---|---|
| AK(3) | 150 | 24 (16.0 %) | 126 | 126/126 |
| control0 | 150 | 111 (74.0 %) | 39 | 39/39 |
| control2 | 150 | 21 (14.0 %) | 129 | 129/129 |

Consistent with `S20` §5.2's `γ_N = 1` parent row (1,627 planar / 331 non-planar there, a
differently-selected corpus) only in sign, not in level; the two are not comparable samples
and no contrast is claimed. Every non-planar verdict carries a `K3,3`/`K5` subdivision
witness.

---

## 2. The search

**Move set — AC2-rich, no SPLIT.** The repo's existing tested move generator
`s12_hunt.slides` is used unmodified: `r_i ← cyclered(r_i · u r_j^{ε} u⁻¹)` with a random
rotation of `r_j`. That one generator realises **AC2** (the multiply), **AC1** on `r_j`
(`ε = −1`, probability ½), **AC3** (conjugation by a generator, probability ½) and **move
(0)** (`cyclered`). Bare AC1 and bare AC3 applied to `r_i` alone are *inert modulo* the
seen-set key `s12_hunt.canon`, which is the least rotation of the word **or its inverse**, so
adding them could not produce a state the search regards as new. **No SPLIT, no AC4, no AC5**
— the rank never changes.

**Goal test, cheap first** (this is the design the brief asked for):

1. **planarity reject** — `s20_planarity_probe.probe_words`; a *certified* non-planar link
   gives `γ_N ≥ 1` by **Theorem S20.1** (proved, `S20_PLANARITY_OBSTRUCTION.md` §2.2), so the
   state cannot be a certificate and is discarded **without a census**. Measured cost
   ≈ **12 ms/state**. A probe exception or an uncertified verdict fails **open** (the state
   goes on to the census), so the filter can never discard on a crash.
2. **exact census** for planar survivors — `census_size` first, then
   `s18_s5_chain_audit.defect_of` (the same exact census that wrote the persisted
   `minimum_defect` rows) when the census fits under 200,000.
3. **cut-scheme solver** fallback for planar survivors whose census does not fit, under a
   per-trial call budget. Measured cost ≈ **70–110 s/state** — see §4.

**Length caps are relative to the root** (filed lesson): per-relator cap = root's longest
relator + 4 = 7; total cap = root total + 12 = 48.

---

## 3. Instrumentation, printed before any null is read

`experiments/lessons/instrument-the-search-before-reading-its-null.md`. Two arms were run
(they differ only in the per-trial cut-scheme-solver budget: 3 vs 0), and their rows are
pooled below; per-arm rows are in `s24_table_solver.json` and `s24_table_screen.json`.
All figures **measured**, read from the fsync'd JSONL rows, not from console output.

| | **AK(3)** | control0 | control2 |
|---|---|---|---|
| trials | 22 | 18 | 20 |
| distinct launch states | 22 (of 527) | 18 | 20 |
| node budget / trial | 400 | 400 | 400 |
| **`pops`** | **8,800** | 7,200 | 8,000 |
| **trials that reached the node budget** | **22/22** | **18/18** | **20/20** |
| states generated | 12,424 | 10,804 | 11,560 |
| **`planar_rejects`** (certified `γ_N ≥ 1`) | **11,911** | 9,382 | 11,014 |
| planar survivors (`planar_pass`) | 535 | 1,440 | 566 |
| **`decided`** (planar survivors given a verdict) | **12** | 34 | 6 |
| of those, by exact census / by solver | 9 / 3 | 31 / 3 | 6 / 0 |
| **`undecided`** planar survivors | **523** | 1,406 | 560 |
| `restarts` | 42 | 22 | 36 |
| **`spherical` (`γ_N = 0`)** | **0** | **0** | **0** |

> **The number the brief asked for: the planarity filter rejected 11,911 of 12,424 AK(3)-class
> children — 95.9 %** — each rejection a *certified* `γ_N ≥ 1` by Theorem S20.1, not a
> heuristic discard. Pooled over all three families: **32,307 of 34,788 (92.9 %)**.
> That is the cheap screen working exactly as designed: ~12 ms per certified negative against
> ~70–110 s for the solver.

**No trial starved on nodes.** 60/60 trials reached `pops = 400`. The pools never emptied
without a reseed (`restarts` counted and non-zero), and every reseed was from a *visited*
state, not the root.

---

## 4. Hits — raw, in band by total length, in band by minimum relator length

| | **AK(3)** | control0 | control2 |
|---|---|---|---|
| **hits, raw** | **0 / 22** | **0 / 18** | **0 / 20** |
| **hits, in band by total length ≥ 13** | **0** | **0** | **0** |
| **hits, in band by minimum relator length ≥ 6** | **0** | **0** | **0** |
| hits, `no_escape` (chain never below the start's own length *and* min relator length) | 0 | 0 | 0 |

All twelve cells are zero, so the three-way band accounting the brief required carries no
information *this time* — but the machinery is in the script (`band_flags`, and every hit row
would carry the full `chain` with `γ_N`, `total_length` and `min_relator_length` at every
node, re-decided by exact census) and will produce the three columns the moment anything hits.

**A limitation of this corpus that must be stated, not hidden.** The launch states are cubic
rank-12 refinements whose **own** minimum relator length is 3. So the third criterion —
"minimum relator length ≥ 6 throughout" — **excludes the start state itself** and is
**vacuous on both arms here**: on this corpus it could only ever return 0. It is the
criterion that transfers for a *rank-2* search launched at AK(3) (that is T-S20's setting,
`S23_INBAND_RATE.md`); at rank 12 the corpus-appropriate version is the `no_escape` row,
which is also 0. Anyone reading "0 in-band by min relator length" off this table as a
*finding* would be reading a definition.

---

## 5. Why the null is uninformative, stated as the primary result

**The control did not create a certificate either.** control0 is the family whose rank-2
source is itself `SPHERICAL` — its stable class demonstrably contains a `γ_N = 0` member —
and its `γ_N = 1` states are genuinely at `γ_N = 1`, so creation *is* required of them
(this is the T-S19 test: not a control that already has the property). It scored **0/18**.

> **Measured detection rate of this instrument, on a control whose class provably contains a
> certificate: 0/18. Therefore AK(3)'s 0/22 bounds nothing.** Not from below (no null ever
> does — `experiments/lessons/parallel-runs-and-bound-direction.md`), and not usefully from
> above either, because the instrument never demonstrated it can find what it is looking for
> at this rank.

**And the mechanism of the failure is measured, not guessed.** It is the decider, not the
search:

| | AK(3) | control0 | control2 |
|---|---|---|---|
| planar survivors | 535 | 1,440 | 566 |
| of those, **undecided** | **523 (97.8 %)** | 1,406 (97.6 %) | 560 (98.9 %) |

Every one of those undecideds is `census_over_cap`. Measured while calibrating: **every**
planar survivor of an AC2 move from a rank-12 cubic state had exact census > 200,000 — the
cap was tried at 60,000 and at 200,000 and the count of census-decided planar survivors was
0 in both, and tightening the total-length headroom to +3 did not help (0 census-decided in
1,200 pops). The census that costs 9,216 rotations on a *cubic* state is `∏_g (deg g − 1)!`,
and one AC2 product raises two germ degrees, so the census leaves the decidable region
immediately. This is `S13` §1(ii)'s `ℓ/n ≲ 3` decidability boundary biting in the direction
that hurts: the launch states sit exactly on it, and the move that could create a certificate
pushes off it.

The fallback — the repo's certified cut-scheme solver, `s12_hunt.decide` — is exact but
**measured at ~70–110 s per state** on these rank-12 inputs (one AK(3) trial: 400 pops,
3 solver calls, 327 s wall; one control0 trial: 400 pops, 3 solver calls, 231 s wall). At that
price a 30-minute job can afford ~15 solver decisions in total, which is what happened: **6
solver calls across all AK(3) trials, 3 of which returned a verdict** and 3 of which returned
`UNSUPPORTED`. That is the entire high-rank detection power the experiment had.

**Consequence for the S-line's open lead 3** ("AC2, not SPLIT"): the lead is **not refuted
and not confirmed**. What is now measured is that *it cannot be tested at rank 12 with the
current deciders*. S17's AC2-vs-SPLIT contrast lives at **rank 5**, where the exact census is
cheap; moving it to rank 12 moves it out of the decidable region. The correct next step is a
cheaper sufficient test for `γ_N = 0` on planar states (the planarity screen is a certified
*negative* test only — S20.1 is one-directional, and AK(3) itself is the standing witness that
planar ⇏ `γ_N = 0`), **not** a bigger node budget.

---

## 6. Was any `γ_N = 0` state found? **No.**

`spherical = 0` in every trial of every arm (22 + 18 + 20 = 60 trials, 24,000 pops,
34,788 generated states). No state in AK(3)'s stable class was shown thickenable, so the
verification protocol the brief specified for a hit (exact census defect 0, Todd–Coxeter
index 1, independent replay of the whole chain from AK(3)) was never triggered.

---

## 7. Status of every quantitative claim in this file

| # | claim | status |
|---|---|---|
| §1 | 527 AK(3)-class states at `minimum_defect = 2`, all rank 12, all distinct | **measured** (`s24_launch_set.json`) |
| §1 | 36/36 verification recomputations returned `minimum_defect = 2` | **measured** this session, exact census |
| §1 | control0 23,083 / control2 4,986 states at `minimum_defect = 2` | **measured** |
| §1 | every pooled state is in its source's stable class via AC4 + AC1–AC3 | **[ASSERTED]** — read from `cubic_split_search`'s docstring, not re-verified; nothing rests on it (no hit) |
| §1a | launch-state planarity 24/150, 111/150, 21/150 planar | **measured**, all non-planar verdicts Kuratowski-certified |
| §3 | `pops` 8,800 / 7,200 / 8,000; 60/60 trials reached the node budget | **measured**, read from the fsync'd JSONL |
| §3 | `planar_rejects` 11,911 of 12,424 AK(3) children (95.9 %); 32,307 of 34,788 pooled (92.9 %) | **measured** |
| §3 | `decided` 12 / 34 / 6; `undecided` 523 / 1,406 / 560 | **measured** |
| §4 | hits 0/22, 0/18, 0/20 — raw, in-band-by-length, in-band-by-min-relator, `no_escape` | **measured** |
| §4 | the min-relator-≥6 criterion is vacuous on this corpus | **established** — the launch states have min relator length 3 |
| §5 | control detection rate 0/18 ⇒ the AK(3) null is uninformative | **inference** from the measured 0/18, under the repo's stated calibration rule |
| §5 | every planar survivor exceeded the exact-census cap at 60,000 and at 200,000 | **measured** during calibration (2 states × 400 pops each configuration; 3 states × 400 pops at total-headroom +3) |
| §5 | cut-scheme solver ≈ 70–110 s/state at rank 12 | **measured** (327 s and 231 s trials, 3 solver calls each, `elapsed_s` in the JSONL rows) |
| §6 | no `γ_N = 0` state found | **measured**: `spherical = 0` in 60/60 trials |
| — | any bound on `Γ` | **none**. Every instrument here bounds `Γ` from **ABOVE**, and a null bounds nothing at all |

Budget actually spent: node budget **400 per search** (brief's ceiling 2,000), wall clock
**17:53:07 → 18:23:23 UTC = 30 min 16 s** including all calibration (`date -u`-measured), all
processes `nice -n 10` or `nice -n 15`, each with a distinct `--out`.

## 8. Reproduce

```
python3 -m experiments.stable_ac.fable.s24_ac2_from_gamma1 launch --verify 12
python3 -m experiments.stable_ac.fable.s24_ac2_from_gamma1 hunt --family ak3 \
    --states 10 --trials 1 --nodes 400 --branch 10 --rel-headroom 4 --tot-headroom 12 \
    --solver-budget 3 --wall 340 --out results/stable_ac/fable/s24_ak3.jsonl
python3 -m experiments.stable_ac.fable.s24_ac2_from_gamma1 table \
    results/stable_ac/fable/s24_*.jsonl --out results/stable_ac/fable/s24_table.json
```

New artifacts, all under `results/stable_ac/fable/`: `s24_launch_set.json`,
`s24_launch_{ak3,control0,control2}.jsonl`, `s24_launch_planarity.json`,
`s24_{ak3,control0}.jsonl`, `s24_screen_{ak3,control0,control2}.jsonl`,
`s24_table_solver.json`, `s24_table_screen.json`, `s24_combined.json`.
