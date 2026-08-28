# W6b: `Tpub` is NOT thickenable — the book-decoupling family, proved and built

Date: 2026-08-28 · Lane: `fable/proofs` · Status: **one new certified solver family,
two decided rank-three targets, 902 newly decided AC-ball states, zero positives**

Checker: `checkers/rank3_shift_family_solver.py` (six modes, all guarded, all green).
Run records: `checkers/out/w6b_targets.json`, `w6b_controls.json`,
`w6b_bruteforce_crosscheck.json`, `w6b_truncated_tpub_support.json`,
`w6b_repo_agreement.json`, `w6b_ball_coverage_c{16,18,20,22}.json` (+ the sliced
`.jsonl` beside each).

```bash
for mode in controls crosscheck repo-agreement truncated targets; do
  python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
    python3 fable/proofs/checkers/rank3_shift_family_solver.py $mode
done
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_shift_family_solver.py ball-coverage --ceiling 20
```

---

## 0. The answers in one paragraph

The decoupling lemma W6 §2.5 asked for **holds for `Tpub` outright** — no case
analysis had to be restored. `Tpub`'s simple support is not 3-connected, but its
only 2-cut `{x⁺, x⁻}` **carries no edge**, so no *bundle* straddles it, and every
parallel bundle of multiplicity ≥ 2 has `H − {u,v}` connected. That is exactly the
hypothesis of Lemma B below, and it forces every bundle into book form in every
spherical rotation system, which collapses `2.09 × 10¹⁶` compatible orderings to
**4 macro rotations × 780 phase triples = 3,120 cases**, consumed in full.
Verdict: **`γ_N(Tpub) ≥ 1`, so `Tpub` is NOT orientably thickenable — for this
exact spelling.** The control `Txy = (A, B, zYX)` runs cleanly through the same
machinery and is also `NOT_SPHERICAL`, which is consistent (thickenability is not
implied by AC-triviality). **No positive was produced by any target or by any of
the 2,513 AC-ball states**; the quarantine line was never reached on anything that
matters (see §7).

---

## 1. The family

Let `G` be the occurrence link multigraph (`AK3_NEUWIRTH.md`'s `A`/`B`/`C`
dictionary, built by `checkers/rank3_link_graph.build_link` — imported, not
re-derived), `H` its simple support, and a **bundle** `β = {u,v}` a parallel class
of multiplicity `m_β`. Write `pieces(β)` for the connected components of
`H − {u,v}`.

> **Family BOOK.** `G` is connected and loopless, every generator occurs, and
> `|pieces(β)| = 1` for every bundle with `m_β ≥ 2`.
>
> **Family SPLIT_ENDPOINT.** As above except that exactly one bundle `β = {u,v}`
> with `m_β ≥ 2` has `|pieces(β)| = 2`, with one piece meeting only `u` and the
> other only `v`.

Everything else — a loop, a disconnected link, an absent generator, two split
bundles, a bundle with ≥ 3 pieces, or a bundle whose two pieces both touch both
endpoints (the `K4−e` shape) — **fails closed as `UNSUPPORTED`**.

### Lemma A (bundle regions) — PROVEN

Let `m_β ≥ 2` and let `G` be embedded in `S²`. The `m` arcs of `β` meet only at
`u` and `v`, so they cut `S²` into exactly `m` regions (Euler: `V=2, E=m, F=m`).
Each connected component of `G − {u,v}` is a connected set disjoint from those
arcs, hence lies in the closure of one region; every non-`β` edge either lies
inside such a component or joins `u`/`v` to one, hence lies in that component's
region. So the **occupied** regions are indexed by `pieces(β)`, one region each. ∎

### Lemma B (book decoupling) — PROVEN. *This is the decoupling lemma.*

Assume family BOOK. Then in **every** spherical rotation system of `G`:

1. each bundle occupies exactly one region (Lemma A with one piece), so all the
   non-`β` darts at `u` sit in a single gap and the `m` bundle darts are
   **consecutive** at `u`; likewise at `v` — *book form*;
2. deleting `m_β − 1` edges per bundle deletes only non-bridges, so it preserves
   sphericity and yields a spherical rotation system of `H`; by (1) the
   `G`-rotation is recovered from that `H`-rotation by re-inserting each bundle as
   one block, so the two are in bijection;
3. the arcs of a bundle appear at `v` in the **reverse** cyclic order to `u`, and
   the alignment of that reversal is **pinned**: the unique occupied region is
   bounded by the same ordered pair of arcs seen from either end. So a book bundle
   has **no relative-shift freedom**.

Consequently the spherical rotation systems of `G` are exactly
`(spherical rotation systems of H) × (a bijection of each bundle's m edges to its
m block positions)`. The first factor is enumerated as the **macro rotation**; the
second is the **rank** assignment the phase equations solve for. ∎

*This is the step `neuwirth_rank3_rigid_solver` gets from 3-connectivity of
`K6 − E(P5)` (`H − {u,v}` connected for every pair). Lemma B needs it only at the
pairs that actually carry a bundle — which is why it reaches a support with
`κ = 2` and four macro rotations, where the Whitney-pair argument cannot go.*

### Lemma C (endpoint split) — PROVEN — `neuwirth_p4_solver`'s mechanism, lifted

In family SPLIT_ENDPOINT, at `u` only `P₁` is present, so exactly one region is
occupied *as seen from `u`* and the bundle is book at `u`; likewise at `v` with
`P₂`. But the occupied region at `u` and the one at `v` may now differ, so the
alignment of the reversal is free by an offset `t ∈ Z_m`. Schemes = macro rotations
× `m` shifts, and `m` is a **complete** shift set. ∎ *(On a 4-vertex path support
this is exactly the `P4` solver's central-bundle gap; §5 shows the two agree on the
repo's own pinned decisions.)*

### Lemma D (gauge) — PROVEN, and controlled

A scheme fixes an absolute slot per dart, i.e. a linear representative of a cyclic
order. Cyclically re-gauging the slots at any germ vertex changes every phase
equation `slot(p) + slot(n) + phase ≡ 0 (mod m_g)` by a constant, which the phase
parameter — quantified over all of `Z_{m_g}` — absorbs. So fixing one linear
representative per vertex loses no compatible ordering. ∎

### Lemma E (reflection) — PROVEN, deliberately **not** used

Reversing every rotation preserves both compatibility and the face count, so
spherical compatible orderings come in reflection pairs and the macro rotation set
is closed under reflection. The solver enumerates **all** macro rotations anyway
(4 for `Tpub`, not 2), so no completeness bug can hide behind this lemma.

### Enumerated, not proven (finite, closed, counted)

macro rotations (every rotation system of `H`, kept iff `V − E + F = 2`); the
shift offsets; the phase tuples; and the rank assignments, by seeded propagation
around the 2-regular constraint graph — `neuwirth_rank_solver._propagate_component`
**shared verbatim with the repo's certified solvers** — followed by a depth-first
exact cover over per-component solutions with per-class rank masks. A negative is
returned only when every scheme, phase tuple, and component seed has been
consumed; a truncated enumeration raises instead of answering.

---

## 2. Why `Tpub` lands in BOOK (the sticking configuration that never appeared)

`Tpub = (xzYXyxZXYxyZ, XyxZXYXyxzXYxy, Xyz)`, germ ids `x±,y±,z± = 0..5`.

| bundle | 0–2 | 0–3 | 0–4 | 1–2 | 1–3 | 1–4 | 1–5 | 3–4 | 3–5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| multiplicity | 6 | 6 | 1 | 4 | 1 | 4 | 4 | 1 | 2 |
| `pieces(β)` | 1 | 1 | 1 | 1 | **2** | 1 | 1 | 1 | 1 |
| class | BOOK | BOOK | — | BOOK | — | BOOK | BOOK | — | BOOK |

The one bundle with two pieces is `1–3` (`x⁻y⁻`), and it has **multiplicity 1**: a
single arc does not divide the sphere, so Lemma A is vacuous there and there is no
bundle freedom to decouple. Equivalently: the 2-cut that makes `κ(H) = 2` is
`{0,1} = {x⁺, x⁻}`, and `H` has **no `0–1` edge**, so the cut pair carries no
bundle. Every bundle that could have coupled is book. The same table for
`Txy = (A, B, zYX)` reads identically in structure (only `1–3`, again at
multiplicity 1, has two pieces).

**So the decoupling lemma did not need restoring for either target.** The
SPLIT_ENDPOINT extension (Lemma C) is carried anyway — it is what lets the same
code reproduce the certified `P4` decisions, and it is the first case that *would*
have been needed.

---

## 3. The `Tpub` verdict

| | `Tpub` | `Txy` (control) |
|---|---|---|
| family | **BOOK** | **BOOK** |
| link graph | connected, loopless, planar, 6 germs, 29 corner edges | same |
| compatible orderings | `2.0858 × 10¹⁶` | `2.0858 × 10¹⁶` |
| macro rotations = schemes | **4** | **4** |
| phase triples per scheme | 780 (`13 × 10 × 6`) | 780 |
| (scheme, phase) cases | **3,120 — all consumed** | **3,120 — all consumed** |
| component seed attempts | 18,720 / 18,720 | 15,600 / 15,600 |
| constraint components | 3 (sizes 12, 14, 3) | 3 (sizes 12, 14, 3) |
| (scheme, phase) pairs where all 3 components closed | **0** | **0** |
| `exhaustive` | `True` | `True` |
| verdict | **`NOT_SPHERICAL`** | **`NOT_SPHERICAL`** |

> **`γ_N(Tpub) ≥ 1`. `K_Tpub` does not embed in any orientable PL 3-manifold, so
> `Tpub` is NOT thickenable — for this exact spelling.**

`Tpub`'s link graph **is connected**, so *both* halves of `AK3_NEUWIRTH.md`
Theorem 2 are available for it: `K_P` embeds in an orientable PL 3-manifold **iff**
`γ_N(P) = 0`. The verdict therefore does not lean on the necessity half alone (as
W6's Lemma W6.3 had to for the disconnected stabilized states) — for `Tpub` the
criterion is an equivalence, and the negative is as strong as the criterion gets.

The `Txy` control returning `NOT_SPHERICAL` is **consistent, not contradictory**:
`Txy` is certified AC-trivial, and thickenability is the *sufficient* side of
Lackenby Thm 1.3, never the necessary one. Its role here is mechanical — every
reduction lemma, the macro enumeration, the shift machinery and the propagation
had to run cleanly on it, and its verdict had to survive the same brute-force
cross-check discipline (§5). It did.

The two once-stabilized states are unchanged from W6: `ak3_stabilized` and
`Q_stabilized` are `UNSUPPORTED` here (`A-link is disconnected`) and remain decided
NEGATIVE by W6's Lemma W6.1 + the certified rank-2 solvers. `Q_rank2` is
`UNSUPPORTED` here (its `2–3` bundle is the `K4−e` split-both-ends shape) and is
already decided by `neuwirth_rank_solver`. `ak3_rank2` is BOOK, and this solver,
the repo's certified `K4` solver (W6 control (7)), and a complete
86,400-ordering enumeration (`γ_N = 2`) **all three agree**.

---

## 4. Coverage: what the family does to W6's AC ball

W6's sharpest number was *"0 of the 503 states of the closed ≤ 20 ball lie in any
certified family"*. Re-running that census through this solver
(`ball-coverage`, reading W6's own state lists):

| ceiling | ball states | **decided here** | all `NOT_SPHERICAL`? | W6's certified coverage |
|---:|---:|---:|---|---:|
| 16 | 17 | **12** (71 %) | yes | 0 |
| 18 | 125 | **48** (38 %) | yes | 0 |
| 20 | 503 | **178** (35 %) | yes | **0** |
| 22 | 1,868 | **664** (36 %) | yes | 24 (1.3 %) |

2,513 states classified, **902 decided, every one of them negative, zero
positives, zero non-exhaustive negatives.** The remaining `UNSUPPORTED` states are
dominated by one shape. Re-classifying the 1,204 undecided states of the
ceiling-22 ball by *what blocks them*:

| blocker | states |
|---|---:|
| exactly one bundle, split with both pieces touching both endpoints (the rank-3 `K4−e` shape) | **898** |
| two or more such bundles | 213 |
| a bundle with ≥ 3 pieces, mixed with the above | 50 |
| link graph disconnected (W6's Lemma W6.1 territory) | 43 |

So one more family — a `cut ∈ {0..m}` parameter, exactly
`neuwirth_rank_solver._k4_minus_edge_scheme`'s — would take ceiling-22 coverage
from **664 to 1,562 of 1,868 (84 %)**, and handling several such bundles at once
would reach 1,775 (95 %). That, not a new idea, is the next family (§8).

---

## 5. Validation battery — every item could have failed, none did

**(a) Brute-force cross-check** (`crosscheck`): 23 pinned instances (20 in-family,
3 the repo's own calibrations, which carry link loops and are correctly refused)
plus a **seeded sweep of 250 random instances** (203 BOOK, 47 SPLIT_ENDPOINT,
rank 2 and rank 3). Every in-family instance's verdict was compared against a
**complete enumeration of all compatible orderings** with the exact `γ_N` formula.
**0 disagreements.** Included: AK(3) itself (86,400 orderings, `γ_N = 2`).

**(b) Truncated instances in `Tpub`'s own macro structure** (`truncated`) — the
cross-check the task asked for, since `Tpub` itself is `10¹⁶` away from brute
force. `('YxyZ','XYxz','YxZx')` has **`Tpub`'s literal 9-edge simple support on the
same germ ids** (288 orderings, `γ_N = 1`); ten more are isomorphic to `Tpub`'s or
`Txy`'s support. All 11 are BOOK with **4 macro rotations, exactly like `Tpub`**,
and all 11 agree with brute force. A seeded sweep of **60 further instances
restricted to `Tpub`/`Txy`-isomorphic supports** (48 / 12) agrees everywhere, and
saw **both** verdicts (6 spherical, 54 not) — so it is not a one-sided null.

**(c) Agreement with the repo's certified ladder** (`repo-agreement`): both of the
repo's pinned `P4` decisions reproduce — `("X","XY")` spherical and
`("X","XXXYXY")` not — each also matching `neuwirth_permutation_certificate`'s
factorial replay. A 120-instance sweep against whichever certified rank-2 solver
applies (`P4` 61, `C4` 30, `K4−e` 24, `K4` 5) has **0 disagreements**. The `K4−e`
rows are the multiplicity-1 central-bundle case, where Lemma A is vacuous and the
macro enumeration alone is complete.

**(d) Dictionary controls**: the link data is reproduced field-for-field from the
repo's **rank-2** builder (`neuwirth_rank_solver._build_link_data`, 5 word pairs)
*and* from the repo's independent **rank-3** builder
(`neuwirth_rank3_rigid_solver._build_link_data`, 4 targets). Without the second,
the rank-3 dart dictionary would only ever have been checked against itself — and
the brute-force oracle shares it.

**(e) Lemma B, counted not just argued**: for six small instances, a complete
enumeration of **every** rotation system of the multigraph `G` counts the spherical
ones and compares against Lemma B's prediction `#macro × Π_β m_β!` (× `m` in the
SPLIT_ENDPOINT case): `16/16, 32/32, 64/64, 384/384, 384/384, 64/64`.

**(f) Scheme sphericity**: every scheme built for every target traces a sphere
(`χ = 2`) — the blow-up direction of Lemma B, on the real targets.

**(g) Lemma D gauge invariance**: re-gauging one germ's slots cyclically leaves
the verdict unchanged on 8 instances.

**(h) Corruption controls** — four, each required to *move* something:

| corruption | must do | did |
|---|---|---|
| shift set truncated to `t = 0` (breaks Lemma C) | flip a verdict | **3/3 fixtures flip** `SPHERICAL → NOT_SPHERICAL` |
| macro set truncated to one rotation (breaks Lemma B) | flip a verdict | **3/3 fixtures flip** |
| Euler characteristic computed off by one | kill a positive | `SPHERICAL → NOT_SPHERICAL` |
| bundle reversal dropped (breaks Lemma B(iii)) | move verdicts | **13 of 23** fixtures move |

Plus, measured and recorded rather than assumed: **on this family a negative never
reaches the witness replay at all** (0 of 10 pinned negatives produce a full rank
assignment) — the phase propagation closes every case first. So an "accept every
trace" corruption is *inert* on negatives and cannot be used as a control there;
the genus computation is load-bearing on positives, and every positive witness is
**re-scored independently by `rank3_link_graph`'s own genus formula** from the
rotations alone (11/11 give genus 0 with the `B`-reversal recomputed).

---

## 6. Quarantine report (doctrine)

Pipeline B (Regina `isBall` on an independently built `N(K)`) **does not exist in
this repo**, so every spherical verdict is `SPHERICAL_REQUIRES_REGINA /
quarantined-suspected-bug` and is claimed as nothing.

* **No target produced a positive.** `Tpub`, `Txy`, `ak3_rank2` are all negative;
  the rest are `UNSUPPORTED`.
* **No AC-ball state produced a positive** — 0 across all 2,513 classified states.
* Positives occurred **only on validation fixtures** — 11 pinned cross-check
  instances, 5 pinned truncated instances, and instances inside the seeded sweeps
  (6 of the 60 `Tpub`-support sweep instances). Each is reported as
  `SPHERICAL_REQUIRES_REGINA`, is used **only** to prove the solver can produce
  positives at all (a solver that always says `NOT_SPHERICAL` would pass a
  one-sided battery), and supports no claim about any presentation.

---

## 7. Scope and nonclaims

* **No AK(3) claim, no AC claim, no stable-AC claim, no bridge claim.** Nothing
  here says AK(3) is or is not AC-trivial, stably AC-trivial, or thickenable.
* **`γ_N > 0` decides ONE SPELLING.** AC moves change the link graph; stable-ACC
  explicitly permits passing through non-thickenable states
  (`NEUWIRTH_FEASIBILITY` §(a)). `Tpub` being non-thickenable prunes `Tpub` and
  **decides nothing** about the class it sits in. The 902 ball negatives prune 902
  states out of a ball that is itself `10⁵–10⁶` states at the lengths AK(3)'s
  greedy work lives at.
* **What is proved here:** Lemmas A–E, with the proofs above; the completeness of
  the scheme set for BOOK and SPLIT_ENDPOINT support follows from B and C.
* **What is enumerated:** everything in §1's last block — finite, closed, counted,
  and raising rather than truncating.
* **What is inherited, not re-derived:** the `A`/`B`/`C` occurrence dictionary and
  the `γ_N` formula (`AK3_NEUWIRTH.md`, via `rank3_link_graph`); the propagation
  kernel (`neuwirth_rank_solver._propagate_component`); Theorem 2 itself; and
  **Lackenby Thm 1.3, which still could not be read** (arXiv egress-blocked, no
  local text) — W6 §1's caveat stands unchanged, and if Thm 1.3 turns out to carry
  a rank-2 hypothesis then the *relevance* of this result falls with it (the
  `γ_N` computation does not).
* **Nothing was searched.** The 1,000-pop law is not stressed: this solver pops no
  state. The AC ball it reports on is W6's, already closed under that law.
* The BOOK/SPLIT_ENDPOINT precondition is checked on the **exact** words; a
  differently spelled representative of the same presentation can leave the family.

---

## 8. Most decisive next step

**Add the `cut` family: one bundle whose two pieces touch both endpoints.** It is
`neuwirth_rank_solver._k4_minus_edge_scheme`'s parameter (`cut ∈ {0..m}` arcs
between the two occupied regions) lifted the same way Lemma C lifted the `P4`
shift, and Lemma A already supplies its completeness argument — the two pieces
occupy two regions, so the arcs form at most two runs at each end and the relative
offset is the only freedom. It is worth exactly what the census says: **898 of the
1,204 `UNSUPPORTED` ball states at ceiling 22 are blocked by exactly one such
bundle and nothing else**, so it takes rank-3 coverage from 36 % to **84 %** of
the ball (95 % if several such bundles are allowed at once).

Two things **not** to do:

* **Do not treat `Tpub`'s negative as a dead end for the lever.** It closes the one
  spelling W5 §5 named. The lever needs *some* AC-equivalent thickenable state, and
  the ball census says 36 % of reachable states are now decidable and all decided
  states so far are negative — which is evidence about the *neighbourhood*, not
  about AK(3).
* **Do not announce a positive if one appears.** Pipeline B is still absent, and it
  is now the binding constraint on the entire upside, exactly as in W3b and W6.
