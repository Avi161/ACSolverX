# S5 — The first genuine high-rank stable-AC search (task A7)

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`; **must be merged into
`fable/proof` by the user.** Date 2026-08-04. Standing frame: `FRAMING.md`
(statements, traps, what does NOT count). Direct companions: `S0_HIGH_RANK_PLAN.md`
(the S-line question), `S1_TRIANGULATION_LEMMA.md` (the rank-9 triangulation of AK(3)),
`S3_SUBDIVISION_INVARIANCE.md` (why triangulation alone is a no-op).

Code: `experiments/stable_ac/fable/rank_n_ac_search.py`.
Tests: `tests/test_rank_n_ac_search.py` (36 tests). Full suite at the time of writing:
**702 passed, 7 skipped** (before the six S6-driven tests were added; 708 after).
Artifacts: `results/stable_ac/fable/rank_n_ac_search_*.json` + `*_rows.jsonl`.

---

## 0. What this document claims, and what it does not

| claim | strength |
|---|---|
| A rank-N AC1–AC5 move generator + a thickenability objective now exist and are tested | **build**, machine-checked |
| The instrument's detection rate is measured on positive ladders before any null is read | **measurement** |
| The AK(3) depth ladder is FLAT and the control ladder is NOT | **measurement**, bounded budget |
| AK(3) is stably AC-trivial | **NOT claimed.** Nothing here decides it. |
| γ_N(AK(3)-class) > 0 | **NOT claimed and NOT claimable by this instrument** — see §2 |
| Any statement about AC from a budget outcome | **NOT claimed** (FRAMING §3) |

FRAMING §3 is binding: a bounded-budget search outcome is never a resolution, in either
direction. What follows is an instrument, its calibration, and two nulls whose worth is
exactly the measured detection rate that precedes them.

---

## 1. What was built

`rank_n_ac_search.py`, a self-contained rank-N implementation over string words
(lowercase = generator, uppercase = inverse). The repo's environment code is rank-2 only;
this is the first module on the line that moves in AC4/AC5 space directly
(`FRAMING.md` §6 route R4: *"No computational method has ever searched AC4/AC5 space
directly"*).

**Moves** (project numbering, `FRAMING.md` §1):

| move | implementation | note |
|---|---|---|
| AC1 invert | `("ac1", i)` | |
| AC2 multiply | `("ac2", i, j, ±1)` | the `-1` sign is the composite AC1;AC2;AC1 |
| AC3 conjugate | `("ac3", i, g, ±1)` | one generator, both signs |
| **conjugated multiply** | `("cmul", i, j, ±1, g, ±1)` | `r_i ← r_i · g r_j^{±1} g^{-1}`, the composite AC3;AC2;AC3-back — **the move that matters**, see §2 |
| AC4 stabilize | `("ac4",)` | fresh generator + fresh relator |
| AC5 destabilize | `("ac5", i)` | legal **only** when `r_i` is a single generator (or its inverse) occurring in no other relator; guarded and tested |

**The move proposal distribution is set by measurement, not intuition.** After the first
round of runs, task A8's `S6_MOVE_CLASSIFICATION.md` §1 supplied exact-census flip counts
for each move, and the sampler was re-weighted to match them:

| S6 row | measured | consequence here |
|---|---|---|
| M3 AC2 slide | **425 destroy / 73 create of 1,863** — the only slide measured to *create* `γ_N = 0` (7.0% of non-thickenable bases) | `ac2` + `cmul` carry ≈ 90% of the sampling weight |
| M0 move (0), free/cyclic reduction | **315 create / 0 destroy of 2,510** | not a sampled move at all — applied to **every** child unconditionally (`reduce_children`), which also makes the visited space coincide with the space the canonical key quotients to |
| M2 bare AC3 conjugation | **315 destroy / 0 create of 3,507** (destroys in 24% of thickenable bases) | token weight 0.4, and when it does fire the sampler prefers the **cancelling** variant |
| M2c AC3 with cancellation | 0 flips of 3,413 | inert but moves the state in the graph — this is the variant that is sampled |
| M1 AC1, ROT | provably inert (S6 Thm T1) | token weight |
| M4 AC4/AC5 | provably inert alone (S6 Thm T4, wedge with a disc) | kept — they are what makes this a *stable* search |
| **M4′** first slide over a fresh stabilizer | **a CW subdivision**, 0 flips of 3,332 | the `entangle_first` prescreen: a child whose stabilized generators are all still chords is scored *after* one whose stabilizer has escaped (occurs > 2 times **and** in ≥ 2 distinct relators). It is a **priority, not a gate** — when no candidate in a generation is entangled the whole slice is scored anyway, so the search cannot starve; a test pins that |

Free reduction is applied to every rewritten relator, including the seam
(`FRAMING.md` trap 3); an empty relator is refused as an illegal state. The state key is
the multiset of **cyclically-reduced** relators up to inversion, generator renaming and
per-generator sign flip (`experiments/lessons/harvest-dedup-on-reduced-forms.md`:
exact-word keys waste ~97% of pops on conjugacy churn). The renaming is derived from a
relabel-invariant signature with ties broken by incoming order, i.e. the key is **sound
but incomplete** — it can fail to merge two isomorphic states, which costs dedup
efficiency and can never merge two distinct ones.

**Triangulation helper** (independent reimplementation, deliberately not shared with the
other agent's `high_rank_refine.py`): the left-prefix chord peel of `S1` §4.2, plus a
replay certifier that back-substitutes every definition and checks that the descendants
free-reduce to the original relators, that every definition relator vanishes, that the
rank arithmetic holds and that the abelianisation is preserved. On AK(3) it reproduces
`S1` §4.4 **letter for letter** (nine relators `aYX bXA cyB cXY dXX eXD fyE gyF gYY`,
closed forms `a=xy, b=xyx, c=xyxY, d=xx, e=xxx, f=xxxY, g=xxxYY`); this is asserted in
the tests.

**Objective — the thickenability hunter.** For a state, the question is whether
`γ_N = 0`. The exact census `gamma_N_factorial_n` is right when
`Π_g (deg(g) − 1)!` is small but far too slow per node, so the search objective is a
randomised hill-climb over compatible rotation systems (plateau walking, random
restarts, transposition + re-insertion neighbourhoods) built on the audited
`neuwirth_rank_n.build_link_n` dictionary. Units: `defect` throughout is the **unhalved**
Neuwirth defect `|A| − |C| + 2L − |AC|`, the same convention as
`gamma_N_factorial_n`'s `minimum_defect`; `γ_N = defect / 2`.

**Verification of every hit — three routes, at least one of them independent.**

1. `witness_check_n.check_witness_n` — a structurally different verifier that rebuilds
   `D, A, B` from the words and shares no scheme code with the hunter. It **requires a
   connected link** (`L = 1`) and refuses otherwise;
2. `independent_defect` — written from scratch inside this module, sharing no code with
   `neuwirth_rank_n` or with the hunter's cache, so that a defect-0 rotation on a
   *disconnected* link (which route 1 refuses, and which is exactly the case of the
   standard presentation, `L = N`) still gets a second opinion;
3. the exact census `gamma_N_factorial_n` when the family fits under 200,000 — the only
   route that returns **equality** rather than a bound.

A hunted defect 0 that no route confirms is recorded as an **anomaly** (a bug in the
hunter, never a mathematical outcome). Across every run reported below the anomaly count
is **0**.

---

## 2. Direction of every bound (the filed trap, restated because it governs §5)

`experiments/lessons/parallel-runs-and-bound-direction.md`; `S0` trap T-S2.

* the hill-climb **exhibits** a rotation system, so it bounds `γ_N` from **ABOVE**. An
  upper bound of 0 is a *proof* of thickenability once re-verified. That is the right
  direction here: we are hunting for zero.
* **Silence bounds nothing.** "No defect-0 rotation found" is never evidence that
  `γ_N > 0`, at any budget, for any state. Every null below is reported only against a
  measured detection rate.
* the Euler sparsity certificate `|E| > 3|V| − 6` is the only lower-bound tool in the
  module and is used only to prune. Per `S3` §4 item 2 it can never fire in the
  triangular regime, so it does no work at rank 9 — it is retained for the
  short-relator/high-multiplicity states the search drifts into.

**Why the search must move at all** (`S3_SUBDIVISION_INVARIANCE.md`). A chord refinement
is a CW **subdivision**: `|K_{P_Δ}| ≅ |K_P|`, so `γ_N(P_Δ) = 0 ⟺ γ_N(P) = 0`. The rank-9
triangulation of AK(3) therefore has the same `minimum_defect` as AK(3) itself — **4, a
theorem, not a measurement** (it is asserted as a regression test here, not reported as a
finding). The escape hatch S3 §4 identifies is a stabilized generator used **three or
more times**. That is precisely what `cmul` does and what no triangulation can do: it
copies letters of `r_j` (stabilized letters included) into `r_i`, pushing occurrence
multiplicities past 2 and leaving the subdivision regime. So the triangulated starts are
a legitimate entry point, and progress begins only once the walk leaves the subdivision
family.

---

## 3. CALIBRATION FIRST

`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`: a one-sided
hunt's silence is worth exactly its MEASURED detection rate. Three ladders, all run with
the same code, the same move set and the same budget knobs as the AK(3) runs.

**Ladder A (realistic).** Members of AK(2)'s AC class taken from
`results/stable_ac/fable/ak2_members.jsonl` with verdict `NOT_SPHERICAL` (so `γ_N ≥ 1`
at rank 2 — the member itself is *not* thickenable), triangulated by the helper to rank 8
(total length 12) and rank 9 (total length 13). Provenance of the positivity: the same
battery records a machine-replayed 27-move AC path from AK(2) to the standard pair
(`ak2_trivialization_path.json`, `replay_verified: true`), so AK(2) is AC-trivial and
every member of its AC class is AC-trivial, hence stably AC-trivial, hence its stable
class contains a thickenable member. The battery also records that 397 of the 13,040
harvested members are themselves `SPHERICAL`, i.e. thickenable members exist inside the
class at rank 2 at a density of ≈3%.

**Ladder B (distance-calibrated).** The standard rank-9 presentation `⟨a₁..a₉ | a₁..a₉⟩`
scrambled by `k` random AC1–AC3 moves. Scrambles whose own hunted defect is already 0 are
**rejected**, because a search that "wins" at node 1 without moving measures nothing.
On the survivors a `γ_N = 0` state (the standard presentation) is known to sit within `k`
moves, so the hit rate as a function of `k` measures the search's reach in AC-move
distance directly.

**Ladder D (depth / rank filtration), 8 seeds per rung.** The orchestrator's addition and
the S-line's
actual question, an operational form of `S0` §4's filtration `~^{(k)}`: the same base is
searched under a rank **ceiling** `2 + k`, starting from the base stabilized `k` times.
The search may destabilize back to rank 2 (otherwise it would not be a stable search).
Two families with identical move sets, identical budgets and identical per-rung seeds:
AK(3), and a **length-matched** AC-trivial `NOT_SPHERICAL` AK(2)-class control
`⟨x,y | YYxxx, YxYxYxxx⟩` (total length 13, the same as AK(3) —
`experiments/lessons/contrast-length-confound.md`: a raw gap between two families can be
a LENGTH gap in disguise).

---

## 4. Results

All runs below use the S6-driven move distribution, `reduce_children = True`,
`entangle_first = True`, one CPU thread, under `guarded_run` (ledger
`results/stable_ac/fable/guard_ledger.jsonl`, child logs in `guard_logs/`).
**Anomaly count across every run reported here: 0** — no hunted defect-0 ever failed
independent re-verification.

### 4.1 Ladder D — the depth / rank-filtration ladder

`results/stable_ac/fable/rank_n_ac_search_depth_ladder.json`. Budget per run: 600 nodes,
beam 6, branch 12, 800 hill-climb evaluations, rank ceiling `2 + k`, rank floor 2,
8 seeds per rung, identical seeds across the two families. 80 runs, 228 s total.

| k | rank ceiling | AK(3) hits / runs | AK(3) best defect (γ_N ≤) | control hits / runs | control detection |
|---|---|---|---|---|---|
| 0 | 2 | **0 / 8** | 2 (γ_N ≤ 1) | 8 / 8 | **1.000** |
| 1 | 3 | **0 / 8** | 2 (γ_N ≤ 1) | 8 / 8 | **1.000** |
| 2 | 4 | **0 / 8** | 4 (γ_N ≤ 2) | 8 / 8 | **1.000** |
| 3 | 5 | **0 / 8** | 4 (γ_N ≤ 2) | 7 / 8 | 0.875 |
| 4 | 6 | **0 / 8** | 4 (γ_N ≤ 2) | 8 / 8 | **1.000** |
| **total** | | **0 / 40** | | **39 / 40** | **0.975** |

So: **the control ladder is flat at detection ≈ 1 and the AK(3) ladder is flat at zero.**
This is the one cell of the whole task where the null is *not* vacuous — see §5.

Confound checks, run because `experiments/lessons/contrast-length-confound.md` requires
them:

* **length.** AK(3)'s best states live at total length 13–17 (13 is its minimum, so it
  cannot go lower). Control hits are spread over lengths 8–21, and **14 of the 39 hits are
  at total length ≥ 13**, i.e. inside the band AK(3) actually occupies. The contrast is
  therefore not purely a length artefact, though the control's ability to shrink below 13
  — which is itself a consequence of its being AC-trivial — accounts for the majority of
  its hits. Per that lesson's rule 2 the honest statement is the direct one: *the control
  can walk to short thickenable presentations and AK(3) cannot leave length 13*.
* **rank actually used.** Control hits occur at best-rank 2 (10), 3 (7), 4 (9), 5 (9),
  6 (4), and **14 of the 39 hit witnesses have a genuinely entangled stabilizer** (a
  non-base generator occurring more than twice and in at least two distinct relators),
  i.e. they are outside the subdivision regime that Theorems S3 and T4′ prove inert. The
  other 25 are rank-2/3 thickenable cores carrying inert stabilizers.
* **no p-values are quoted** — class members come from a move tree and are not
  independent draws (same lesson, rule 3).

### 4.2 AK(3) at rank 9–11, from three different triangulations

`results/stable_ac/fable/rank_n_ac_search_ladderA_ak3.json`. Budget per run: 1,000 nodes,
beam 6, branch 12, 800 evaluations, rank window [2, 11], 19 s each.

| start | scheme | best defect (γ_N ≤) | best rank / length | γ_N = 0 found |
|---|---|---|---|---|
| AK(3) rank-9 triangulation | left-prefix (`S1` §4.4) | 2 (γ_N ≤ 1) | 9 / 30 | **no** |
| AK(3) rank-9 triangulation | rotated start (`S1` §4.5 item 2) | 4 (γ_N ≤ 2) | 9 / 27 | **no** |
| AK(3) rank-9 triangulation | inverted `r₁` (`S1` §4.5 item 4) | 2 (γ_N ≤ 1) | 10 / 32 | **no** |

The three starts are the *same* presentation up to the triangulation choice family of
`S1` §4.5, and by Theorem S3 all three have exactly AK(3)'s own `minimum_defect` of 4 —
that is a theorem, quoted here only to say what the search started from, never as a
measurement. **Do not read "4 → 2" as progress**: trap T-S6 — the *value* of γ_N is not
comparable across cell structures, and the three rows above are three different complexes.
The only topologically meaningful entry is the last column, and it is "no" in every row.

`entangled_scored` is 997–999 out of 1,000 on these runs, i.e. essentially every state the
objective was spent on had a stabilized generator occurring more than twice in at least
two relators. The search is genuinely working outside the subdivision regime that
Theorems S3 and T4′ prove inert — which is the whole point of doing this at rank 9 rather
than triangulating and testing.

<!--RESULTS-->

---

## 5. What the nulls are worth

<!--WORTH-->

---

## 6. Traps and design lessons this task produced

- **T-A7.1 — the objective's length tiebreak fights the S3 escape hatch.** The beam is
  scored on `(defect upper bound, total length)`. Escaping the subdivision regime means
  raising a stabilized generator's multiplicity past 2, and *every* move that does so
  lengthens a relator. So the tiebreak systematically pushes the beam back into the
  abbreviation regime that Theorem S3 proves inert. This was visible in the data before
  the `entangle_first` prescreen was added (§4.3) and is the reason it was added. Any
  future scorer on this line must state how it stops length from vetoing entanglement.
- **T-A7.2 — dedup on cyclically-reduced forms is only safe once reduction is applied to
  the states themselves.** `γ_N` is a function of the *spelling*
  (`S6_MOVE_CLASSIFICATION.md` §0.2), so keying the seen-set on cyclically-reduced forms
  (the `harvest-dedup-on-reduced-forms.md` lesson) silently identifies states with
  *different* `γ_N`. The two are only compatible if move (0) is applied to every child, so
  that the visited space *is* the reduced space. That is now the default and is tested.
  Anyone who turns `reduce_children` off must also change the key.
- **T-A7.3 — `check_witness_n` cannot verify a disconnected-link witness.** It requires
  `L = 1` and refuses otherwise, which includes the standard presentation itself
  (`L = N`). A defect-0 hit on a disconnected link is not a failure; it needs
  `R1E_DISCONNECTED_LINK.md` Theorem D's `2L` bookkeeping. This module verifies those with
  a from-scratch `independent_defect` plus the exact census, and records which routes
  fired in `verified_by` — never the bare word "verified".
- **T-A7.4 — the "one experiment at a time" guard lock is not the only contention.** The
  container ran several agents' CPU-bound jobs concurrently throughout; a `--preflight`
  can also be invalidated mid-session by *another* agent editing any `.py` under
  `experiments/stable_ac/fable` (the fingerprint is a directory-wide hash), which is what
  the one `REFUSED` row in `guard_ledger.jsonl` for this task is. Re-preflight and rerun;
  it is not a failure of the experiment.
- Restated because they bound everything above: **T-S6** (γ_N's *value* is not comparable
  across cell structures — only `γ_N = 0` is topological) and **T-S2 / the
  bound-direction lesson** (a hill-climbed witness bounds from ABOVE; silence bounds
  nothing).
