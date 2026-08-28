# W6c: the CUT family — proved, built, and two closed rank-three AC balls fully decided

Date: 2026-08-28 · Lane: `fable/proofs` · Status: **two new certified families
(CUT and the Lemma I reduced route), 1,027 newly decided AC-ball states, the
closed ≤ 16 and ≤ 18 balls COMPLETELY decided, zero positives, zero quarantine
events**

Checker: `checkers/rank3_cut_family_solver.py` (seven modes, all guarded, all
green — **279 checks, 0 failures**). It imports `rank3_shift_family_solver`
(W6b) and `rank3_link_graph` (W6); it forks nothing.

Run records: `checkers/out/w6c_controls.json`,
`w6c_bruteforce_crosscheck.json`, `w6c_shape_completeness.json`,
`w6c_repo_agreement.json`, `w6c_reduced_route.json`, `w6c_targets.json`,
`w6c_coverage_report.json`, `w6c_ball_coverage_c{16,18,20,22}.json` (+ the
sliced `.jsonl` beside each).

```bash
for mode in controls crosscheck shape-completeness repo-agreement reduced targets; do
  python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
    python3 fable/proofs/checkers/rank3_cut_family_solver.py $mode
done
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_cut_family_solver.py ball-coverage --ceiling 20
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/rank3_cut_family_solver.py coverage-report
```

---

## 0. The answers in one paragraph

W6b §8 asked for the `cut` family: one bundle `β = {u,v}` of multiplicity `m`
whose complement splits into **two pieces that each touch both endpoints** (the
rank-three `K4−e` shape), blocking 898 of the 1,204 states W6b could not reach.
It is built here and proved by **Lemma G (piece contraction)** and **Lemma H
(cut decoupling)**; the cut parameter is `s ∈ {0..m}`, exactly the repo's
certified `neuwirth_rank_solver._k4_minus_edge_scheme`, and the rank-2 `K4−e`
family is its **degenerate case in the literal sense that its two pieces are
single vertices, so Lemma G's contraction is the identity** — checked not by
verdict agreement alone but by showing the two scheme sets **generate exactly
the same set of rotation systems on 120 instances**. Building the family
exposed a second, strictly more general lemma that costs nothing extra —
**Lemma I (book contraction)**: contract only the *book* bundles (W6b Lemma B
licenses that), keep every non-book bundle at full multiplicity, and enumerate
*all* rotation systems of the reduced multigraph `Ĥ`. That assumes nothing at
all about the non-book bundles and decides MIXED, three-piece and multi-split
supports whenever the closure fits a declared budget. Together with W6's proven
bare-row splitting (Lemma F, generalised off the letter `z`), the result is:

| ceiling | ball states | W6b decided | **W6c decided** | complete? |
|---:|---:|---:|---:|---|
| 16 | 17 | 12 | **17 (100 %)** | **YES** |
| 18 | 125 | 48 | **125 (100 %)** | **YES** |
| 20 | 503 | 178 | **479 (95.2 %)** | no — 24 left |
| 22 | 1,868 | 664 | **1,691 (90.5 %)** | no — 177 left |

**Every decided state is `NOT_SPHERICAL`. No positive was produced on any
target or any of the 2,513 classified ball states, so the quarantine line was
never reached on anything that matters (§7).** All six W6/W6b targets are now
decided by this checker alone, including `Q_rank2` and `Q_stabilized`, which
W6b had to hand to the repo's rank-2 solver.

> **The closed rank-three AC balls at total-length ceilings 16 and 18 are now
> FULLY DECIDED — 17 of 17 and 125 of 125 — and every state in them is
> non-thickenable.** That is a clean bounded null: **no thickenable state
> exists anywhere in the closed rank-three AC ball around `(AK3, z)` at
> ceilings ≤ 18**, for the move set and canonicalisation W6 §4 declares.

---

## 1. The families

`G` is the occurrence link multigraph (`AK3_NEUWIRTH.md`'s `A`/`B`/`C`
dictionary, built by `rank3_link_graph.build_link` — imported, not re-derived),
`H` its simple support, a **bundle** `β = {u,v}` a parallel class of
multiplicity `m_β`, and `pieces(β)` the connected components of `H − {u,v}`.
W6b's BOOK (`|pieces| = 1` everywhere) and SPLIT_ENDPOINT (one bundle with two
pieces, one touching only `u`, the other only `v`) are inherited and
**delegated verbatim** to `rank3_shift_family_solver` — control (10) below pins
that delegation as verdict-identical on 463 states.

> **Family CUT.** `G` is connected and loopless, every generator occurs,
> exactly one bundle `β = {u,v}` with `m_β = m ≥ 2` has `|pieces(β)| = 2` with
> **both pieces meeting both of `u` and `v`**, and every other bundle of
> multiplicity ≥ 2 is BOOK.
>
> **Route BARE_ROW (Lemma F).** Some generator occurs in exactly one relator,
> that relator being the one-letter word `g^{±1}`. Drop both and recurse.
>
> **Route REDUCED (Lemma I).** Anything else that is connected, loopless and
> uses every generator, provided the reduced-multigraph rotation closure fits
> the declared budget (default 300,000). Fails closed above it.

### Lemma A (bundle regions) — W6b, PROVEN, reused verbatim

The `m` arcs of a bundle meet only at `u` and `v`, so they cut `S²` into
exactly `m` regions (Euler: `V=2, E=m, F=m`), and every component of
`G − {u,v}` lies in the closure of exactly one of them. ∎

### Lemma G (piece contraction) — PROVEN. *This is what changes with two pieces.*

Let `G ⊂ S²` and `β = {u,v}` any bundle, with pieces `P₁,…,P_k`. Contracting
each `P_i` to a vertex `p_i` is a sequence of contractions of non-loop edges of
an embedded graph, so it preserves the genus and **preserves the cyclic order
of the darts at `u` and at `v`** (neither is contracted). The contracted graph
is the multigraph on `{u,v,p₁,…,p_k}` with `m` parallel `u–v` edges, `a_i ≥ 0`
edges `u–p_i`, `b_i ≥ 0` edges `v–p_i`, and no `p_i–p_j` edge (distinct pieces
are non-adjacent in `H − {u,v}` by definition). In that contracted graph the
bundle `{u,p_i}` has connected complement whenever anything else remains
attached, so **W6b Lemma B applies to it**: the darts from `u` into `P_i` are
consecutive in the rotation at `u`. Contraction preserved that cyclic order, so
the statement is about `G` itself. ∎

### Lemma H (cut decoupling) — PROVEN. *The completeness lemma of this family.*

Assume family CUT, pieces `P₁, P₂` both meeting both endpoints. In **every**
spherical rotation system of `G`:

1. every bundle other than `β` is book (W6b Lemma B), so deleting `m_γ − 1`
   edges from each is deletion of non-bridges, preserves sphericity, and the
   `G`-rotation is recovered by re-inserting each such bundle as one block;
2. at `u` the darts into `P₁` form one contiguous block `D₁` and the darts into
   `P₂` a contiguous block `D₂` (Lemma G), so the `m` arcs of `β` occupy the
   two remaining gaps, in runs of sizes `s` and `m − s` for some
   `s ∈ {0,…,m}`; likewise at `v`;
3. deleting all but one arc of `β` as well leaves a spherical rotation system
   `ρ` of `H`, whose rotation at `u` is `(D₁, arc, D₂)` or `(D₁, D₂, arc)` —
   in **either** case its arc-deleted cyclic order at `u` is `(D₁, D₂)` with
   the same internal orders, and the same at `v`.

Hence every spherical rotation system of `G` is obtained from some **macro
rotation** `ρ` (a spherical rotation system of `H`, enumerated exactly as in
W6b) by blowing up every non-`β` bundle as one block in `ρ`-order, reading
`ρ`'s arc-deleted order at `u` and `v` as `(D₁, D₂)`, and inserting the `m`
arcs into the two gaps at each end. ∎

**What changes relative to W6b Lemma B/C, stated exactly.** Lemma B removed all
bundle freedom because with one piece there is one occupied region, so both
gaps at an endpoint collapse to one and the reversal alignment is pinned by
that region. Lemma C gave back a single offset `t ∈ ℤ_m` because with
`P₁` touching only `u` and `P₂` only `v`, *each endpoint separately* still sees
one gap — the two ends just no longer agree on which region. **With two pieces
touching both endpoints, both gaps are real at both ends simultaneously**, and
the two-run split — the cut — is the parameter. That is one integer, not a
shift and not a rotation, and it is the same integer the repo's certified
`_k4_minus_edge_scheme` carries.

**What Lemma H does not claim.** It does not claim every `(macro, cut)` shape
is spherical; it claims the converse inclusion. A generated shape that is not
spherical can never carry a witness (the replay recomputes the Euler
characteristic), so the solver discards it up front. That discard is **lossless
and proved so**: permuting ranks inside a parallel class relabels the same
edges at *both* endpoints simultaneously, an isomorphism of the embedded graph,
so a scheme's Euler characteristic does not depend on the rank assignment.

### Lemma I (book contraction) — PROVEN, and strictly more general

Let `B` be the set of bundles with `|pieces| = 1` and `m ≥ 2`. By W6b Lemma B
each is book in every spherical rotation system of `G`, so deleting `m − 1` of
its edges (non-bridges) preserves sphericity, and re-inserting them as one
block preserves it back (drawing `m` parallel arcs side by side adds `m − 1`
edges and `m − 1` faces, leaving `χ` fixed). Hence the spherical rotation
systems of `G` are in bijection with

  (spherical rotation systems of `Ĥ`) × (a labelling of each book bundle's `m`
  edges by its `m` block positions),

where `Ĥ` is `G` with **exactly** the book bundles contracted. **Nothing is
assumed about the non-book bundles**: they are carried at full multiplicity and
their placement is enumerated, not constructed. ∎

Lemma I subsumes Lemma H logically but not practically: `Ĥ`'s closure is
`Π_w (deg_Ĥ(w) − 1)!`, which for a CUT state is far larger than `H`'s. So CUT
(cheap, constructed) runs first and REDUCED (general, enumerated) is the
fallback — and on every instance where both apply they are two **independent**
derivations of the same scheme set, cross-checked in §5(f).

### Lemma F (bare-row splitting) — PROVEN; W6 Lemma W6.1 off the letter `z`

If some generator `g` occurs in exactly one relator and that relator is the
one-letter word `g^{±1}`, the link graph is the disjoint union of the link
graph of the presentation with `g` and that row removed, and a single edge
`g⁺—g⁻`; `m_g = 1` so the compatible orderings biject; the extra component has
`|C| = 2, |A| = 1, |AC| = 1, L = 1`, hence `χ = 2` and genus 0; genus is
additive over components. So `γ_N(P) = γ_N(P minus that row)` exactly. ∎
(W6 proved this for `z`; the proof never uses which generator it is. All 43
disconnected states of the ceiling-22 ball are of exactly this shape.)

Lemmas D (gauge) and E (reflection) are W6b's, unchanged and reused. Lemma E is
again deliberately **not** used to halve anything.

### Enumerated, not proven (finite, closed, counted, raising rather than truncating)

the macro rotations of `H`; the cut `s ∈ {0..m}` together with four redundant
sign conventions at `v`; every rotation system of `Ĥ`; the phase tuples; and
the rank assignments, by seeded propagation around the 2-regular constraint
graph — `neuwirth_rank_solver._propagate_component` **shared verbatim with the
repo's certified solvers** — followed by a depth-first exact cover. A negative
is returned only when the whole case set has been consumed; a truncated
enumeration raises, and a `Ĥ` closure above the budget returns `UNSUPPORTED`
rather than a verdict (controlled in §5(e)).

---

## 2. The targets — all six decided, by this checker alone

| target | family | route | verdict |
|---|---|---|---|
| `Tpub = (A, B, Xyz)` | BOOK | W6b delegated | `NOT_SPHERICAL` |
| `Txy = (A, B, zYX)` (certified AC-trivial) | BOOK | W6b delegated | `NOT_SPHERICAL` |
| `ak3_rank2` | BOOK | W6b delegated | `NOT_SPHERICAL` |
| `ak3_stabilized = (AK3₁, AK3₂, z)` | BARE_ROW | Lemma F → W6b | `NOT_SPHERICAL` |
| `Q_stabilized = (Q₁, Q₂, z)` | BARE_ROW | **Lemma F → CUT** | `NOT_SPHERICAL` |
| `Q_rank2` | **CUT** | **CUT** | `NOT_SPHERICAL` |

`Q_rank2` and `Q_stabilized` were `UNSUPPORTED` in W6b and were decided in W6
only by *importing* the repo's certified rank-2 verdict. They are now decided
**inside this lane's own machinery**, and that verdict is checked against the
repo's `neuwirth_rank_solver` (§5(c)). `Tpub`'s W6b decision is untouched: W6c
delegates it and reproduces it byte for byte.

---

## 3. Coverage — the closed balls at 16 and 18 are fully decided

Reading W6's own state lists (`out/w6_ac_ball_c{N}.json`, produced under the
1,000-pop law) through this solver:

| ceiling | ball states | W6 certified | W6b | **W6c** | newly decided | all negative? | **complete?** |
|---:|---:|---:|---:|---:|---:|---|---|
| 16 | 17 | 0 | 12 | **17** | +5 | yes | **YES** |
| 18 | 125 | 0 | 48 | **125** | +77 | yes | **YES** |
| 20 | 503 | **0** | 178 | **479** | +301 | yes | no |
| 22 | 1,868 | 24 | 664 | **1,691** | +1,027 | yes | no |

Route breakdown of the decided states:

| ceiling | W6b delegated (BOOK) | CUT | Lemma F (bare row) | Lemma I (`Ĥ`) | undecided |
|---:|---:|---:|---:|---:|---:|
| 16 | 12 | 0 | 5 | 0 | 0 |
| 18 | 48 | 56 | 13 | 8 | 0 |
| 20 | 178 | 254 | 27 | 20 | 24 |
| 22 | 664 | 898 | 43 | 86 | 177 |

`CUT` decided exactly the 898 states W6b's census predicted at ceiling 22 — the
prediction and the delivery agree to the state.

> **Ceilings 16 and 18 are COMPLETE.** Every canonical rank-three AC state
> reachable from `(AK3, z)` through states of total length ≤ 18 — all 125 of
> them — is decided, and every one is `NOT_SPHERICAL`, i.e. `γ_N > 0`. **There
> is no thickenable state anywhere in that closed ball.** W6's sharpest number
> was "0 of the 503 states of the closed ≤ 20 ball lie in any certified
> family"; the ≤ 20 ball is now 95.2 % decided and the two balls inside it are
> closed out entirely.

### Residual profile — what is left and what it would need

| blocker (disjoint buckets) | c20 | c22 | what a family for it would have to do |
|---|---:|---:|---|
| two CUT bundles, **sharing a germ vertex** | 4 | 58 | two cut parameters at once, interleaved at the shared vertex; all 140 multi-cut states of the ceiling-22 ball share a vertex (0 disjoint), so a product `cut₁ × cut₂` construction is *not* obviously complete and the `Ĥ` route is the honest fallback |
| two or more MIXED bundles only (one piece meets both endpoints, the other only one) | 10 | 71 | MIXED is already a *single*-bundle special case of the same two-run construction (one gap degenerates at `v`); what is missing is several at once |
| one CUT plus two MIXED | 0 | 2 | both of the above simultaneously |
| a bundle with ≥ 3 pieces, mixed with the above | 10 | 46 | Lemma A gives `k` occupied regions out of `m`; the parameter is a composition of `m` into `k` parts, not one integer |
| link disconnected | 0 | 0 | **cleared** — Lemma F handles all 43 |

The `Ĥ` route already decides *any*
of these shapes — 86 such states at ceiling 22 — whenever
`Π_w (deg_Ĥ(w) − 1)!` fits the 300,000 budget. The residual is therefore not a
missing theorem but a **closure that is too large**: the remaining states have
`Ĥ` closures from `10⁶` to `4 × 10¹⁸`.

---

## 4. What "the rank-2 `K4−e` family is the degenerate case" means, precisely

At rank 2 the support has four germs. A bundle `{u,v}` whose complement is two
pieces each touching both endpoints forces the other two germs to be those two
pieces, each adjacent to both `u` and `v`, and non-adjacent to each other —
i.e. **`K4−e` with the missing edge between the pieces and `{u,v}` the central
bundle**. Conversely a `K4−e` support with central multiplicity ≥ 2 is family
CUT (with central multiplicity 1 it is BOOK — the case W6b already covered).
The degeneracy is Lemma G's: **each piece is a single vertex, so the contraction
is the identity map**, and `cut_scheme` reduces literally to
`_k4_minus_edge_scheme`. Measured, not asserted (`repo-agreement`):

* 120 rank-2 CUT instances, **support `K4−e` on 120/120**;
* **pieces are single vertices on 120/120**;
* verdicts agree with the certified `neuwirth_rank_solver` on **120/120**;
* and the strong form: the scheme set built here and the repo's certified
  `embedding_schemes` **generate exactly the same set of rotation systems** on
  **120/120** — 0 mismatches. Verdict agreement could hide a scheme-set
  difference that happens not to matter; this cannot.

The repo's two pinned `P4` decisions (`("X","XY")` spherical,
`("X","XXXYXY")` not) also still reproduce, through the W6b delegation.

---

## 5. Validation battery — every item could have failed, none did

279 checks across six modes, 0 failures.

**(a) Brute-force cross-check on the CUT family** (`crosscheck`): 22 pinned
instances (10 rank-2, 12 rank-3, cut multiplicities 2–5) each compared against
a **complete enumeration of all compatible orderings** with the exact `γ_N`
formula, plus a **seeded sweep of 120 random CUT instances** (65 rank-2, 55
rank-3). **0 disagreements.** Both verdicts present in both the pinned set and
the sweep (51 spherical / 69 not), so it is not a one-sided null.

**(b) Lemma H checked as a SET IDENTITY, not a count** (`shape-completeness`):
for 12 pinned instances and a further **120 swept** ones, *every* spherical
rotation system of the multigraph `G` was enumerated directly and compared with
the set generated by (kept cut scheme) × (rank assignment). Not only is
`truth ⊆ built` everywhere (completeness — the direction Lemma H claims), the
two sets are **equal** everywhere (the scheme set is not over-general either).
This is stronger than W6b's Lemma-B count control, which compared cardinalities.

**(c) Agreement with the repo's certified ladder** (`repo-agreement`): §4 —
120 instances, verdicts and **scheme sets** identical; the two pinned `P4`
decisions; and `Q_rank2`.

**(d) Lemma D gauge invariance**: re-gauging one germ's slots cyclically leaves
the verdict unchanged on 8 CUT instances.

**(e) Corruption controls — seven, each required to *move* something:**

| corruption | must do | did |
|---|---|---|
| cut set truncated to `s = 0` (= treat the cut bundle as BOOK; breaks Lemma H) | flip a verdict | **6/6 fixtures flip** `SPHERICAL → NOT_SPHERICAL` |
| macro set truncated to one rotation (breaks Lemma B/H macro completeness) | flip a verdict | **6/6 fixtures flip** |
| block reversal dropped (breaks W6b Lemma B(iii)) | move verdicts | **4 of 22** CUT fixtures move |
| Euler characteristic off by one | kill a positive | `SPHERICAL → NOT_SPHERICAL` |
| `Ĥ` scheme set truncated to one scheme (breaks Lemma I) | flip a verdict | **5/5 fixtures flip** |
| block reversal dropped, `Ĥ` route | move verdicts | **3 of 17** fixtures move |
| `Ĥ` budget starved to 1 | fail closed, never fabricate a verdict | **17/17 return `UNSUPPORTED`** |

Also **measured and recorded rather than assumed**: the Euler filter on cut
schemes is *not* vacuous — it discards shapes on every one of the 22 fixtures;
and restricting the four redundant sign conventions at `v` to the repo's single
`_k4_minus_edge_scheme` convention moved **0 of 22** verdicts. The other three
are therefore empirically redundant and are carried anyway, so that **no
orientation convention is load-bearing** in the completeness argument. Because
they are inert, they are reported as a measurement, not as a control.

**(f) Two independent derivations of the same scheme set** (`reduced`): the
constructed CUT schemes (Lemma H) and the enumerated `Ĥ` schemes (Lemma I)
agree on **40/40** shared instances. This is a real cross-check: one is a
closed-form construction from `H`'s macro rotations, the other a brute-force
enumeration that assumes nothing about the cut bundle.

**(g) The `Ĥ` route against brute force** (`reduced`): 17 pinned instances that
are *outside* CUT — MIXED bundles, bundles with three and four pieces, several
split bundles at once — each with exact `γ_N` from complete enumeration (11
spherical, 6 not), plus a **120-instance seeded sweep** across BOOK (77),
SPLIT_ENDPOINT (13), CUT (9) and out-of-family (21) support, with both verdicts
present (65 / 55). **0 disagreements**, and Lemma I's set identity — checked
directly against complete enumeration on all 17 pinned instances and throughout
the sweep — holds on every one.

**(h) Lemma F checked numerically, not only argued**: `γ_N(r₁,r₂,Z)` equals
`γ_N(r₁,r₂)` by complete enumeration on 8 fixtures, and the reduction's verdict
matches.

**(i) W6b delegation is verdict-identical** on **463** BOOK/SPLIT_ENDPOINT ball
states read back out of `w6b_ball_coverage_c*.jsonl`, and the coverage report
asserts per ceiling that **W6c decides everything W6b decided** — 0 regressions
at every ceiling. W6c can never silently move a W6b decision.

**(j) Fail-closed route table**: the six targets land in the families §2 states,
asserted.

**(k) Every negative is exhaustive**: a non-exhaustive negative raises rather
than being reported, both in the solver and again when the ball rows are
re-read.

---

## 6. Quarantine report (doctrine)

Pipeline B (Regina `isBall` on an independently built `N(K)`) **does not exist
in this repo**, so every spherical verdict is `SPHERICAL_REQUIRES_REGINA /
quarantined-suspected-bug` and is claimed as nothing.

* **No target produced a positive** — all six are `NOT_SPHERICAL`.
* **No AC-ball state produced a positive** — 0 across all 2,513 classified
  states, at every ceiling, asserted by the coverage report.
* Positives occurred **only on validation fixtures** — the pinned cross-check
  and shape instances and the seeded sweeps. Each is reported as
  `SPHERICAL_REQUIRES_REGINA`, is used **only** to prove the solver can produce
  positives at all (a solver that always says `NOT_SPHERICAL` would pass a
  one-sided battery, and every corruption control here is built on a positive
  that must die), and supports no claim about any presentation.

---

## 7. Scope and nonclaims

* **No AK(3) claim, no AC claim, no stable-AC claim, no bridge claim.** Nothing
  here says AK(3) is or is not AC-trivial, stably AC-trivial, or thickenable.
* **`γ_N > 0` decides ONE SPELLING.** AC moves change the link graph, and
  stable-ACC explicitly permits passing through non-thickenable states
  (`NEUWIRTH_FEASIBILITY` §(a)). Every negative below is per-spelling.
* **The completeness of the ≤ 16 and ≤ 18 balls is a closure for W6 §4's
  declared move set and canonicalisation** (AC2 over the 6 ordered pairs, AC3
  with the 6 single-letter conjugators, canonical form = lexicographic minimum
  over cyclic rotations and inversion, relators sorted). A different move set
  reaches more states; the "no thickenable state in the closed ball" statement
  is a statement about *that* ball. It says nothing about ceilings above 18,
  where 24 and 177 states remain undecided, nor about the length-30 region where
  AK(3)'s greedy work lives (`10⁵–10⁶` states, W6 §4).
* **What is proved here:** Lemmas G, H and I, with the proofs in §1; Lemma F as
  a restatement of W6 Lemma W6.1 whose proof never used the letter `z`. The
  completeness of the scheme set for CUT follows from G and H; for the REDUCED
  route it follows from I plus a complete finite enumeration.
* **What is enumerated:** everything in §1's last block — finite, closed,
  counted, raising rather than truncating, and failing closed above a declared
  budget.
* **What is inherited, not re-derived:** the `A`/`B`/`C` occurrence dictionary
  and the `γ_N` formula (`AK3_NEUWIRTH.md`, via `rank3_link_graph`); the
  propagation kernel (`neuwirth_rank_solver._propagate_component`) and the
  `K4−e` cut convention (`_k4_minus_edge_scheme`); W6b's BOOK/SPLIT_ENDPOINT
  path and Lemmas A–E; Theorem 2 itself; and **Lackenby Thm 1.3, which still
  could not be read** (arXiv egress-blocked, no local text) — W6 §1's caveat
  stands unchanged, and if Thm 1.3 turns out to carry a rank-2 hypothesis then
  the *relevance* of everything here falls with it (the `γ_N` computation does
  not).
* **Nothing was searched.** This solver pops no state; the 1,000-pop law is not
  stressed. The AC ball it reports on is W6's, already closed under that law.
  The `Ĥ` and brute-force enumerations are complete finite closures over
  rotation systems, not searches.
* The family precondition is checked on the **exact** words; a differently
  spelled representative of the same presentation can leave the family.

---

## 8. Most decisive next step

**Two CUT bundles at once — and specifically two that share a germ vertex,
because in this ball 140 of 140 multi-cut states do.** It is worth 58 states at
ceiling 22 and 4 at ceiling 20, and it is the only remaining blocker whose
geometry is already understood: each bundle contributes its own `s ∈ {0..m}`,
and the one thing needing proof is how the two two-run splits interleave at the
shared vertex — where a naive product `cut₁ × cut₂` is *not* obviously complete.
The `Ĥ` route is the ready-made oracle to develop it against: it decides these
states outright whenever the closure fits, so a constructed multi-cut scheme set
can be validated by **set identity against `Ĥ`** on exactly the states that
matter, not on toy instances. Closing multi-cut and multi-MIXED together would
take ceiling 20 to 503/503 — a third, and much larger, fully decided closed
ball.

Three things **not** to do:

* **Do not read "ceilings 16 and 18 are fully decided and all negative" as
  evidence about AK(3).** It is a bounded null about a small neighbourhood in
  one spelling-quotient, exactly as narrow as W6b's was. It prunes 142 states.
* **Do not raise the `Ĥ` budget as a strategy.** The residual closures run from
  `10⁶` to `4 × 10¹⁸`; the budget buys a handful of states and then stops. The
  next 177 states need a theorem, not a bigger enumeration — the same lesson
  W6 §4 recorded about brute-forcing `γ_N`.
* **Do not announce a positive if one appears.** Pipeline B is still absent and
  is still the binding constraint on the entire upside, exactly as in W3b, W6
  and W6b.
