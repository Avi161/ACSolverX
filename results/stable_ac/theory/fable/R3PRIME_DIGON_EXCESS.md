# R3′ seed — the digon-excess form of sphericity (29-07-2026)

Claim addressed: infrastructure for BOTH directions of the R1 equivalence (find γ_N = 0 in
AK(3)'s stable class / prove none exists). Elementary but organizing; to be adversarially
checked before any load-bearing use.

Setting: balanced 2-generator pair, cyclically reduced words, loopless CONNECTED link
(support ⊆ K₄), N = total letters, darts 2N, |C| = 4, L = 1.

**Lemma D1 (no monogons).** For a loopless link, AC has no fixed points: AC(d) = d would
need C(d) = A(d), but C(d) stays at the germ ν(d) while ν(A(d)) ≠ ν(d). So every face has
length ≥ 2 (in darts; face lengths sum to 2N).

**Lemma D2 (excess form).** Write E(C) = Σ_faces (len − 2) = 2N − 2·|AC| for the
digon-excess. Then the defect is |A| − |C| + 2L − |AC| = N − 2 − |AC| = E(C)/2 − 2, so

    genus-sum(C) = E(C)/4 − 1/2 …  [defect = 2·genus-sum; E = 4 + 4·genus-sum]

i.e. **C is spherical ⟺ E(C) = 4**: all faces are digons except a total excess of exactly
four (four triangles' worth in K₄'s tetrahedral picture: 4 triangles × excess 1 = 4 ✓,
consistent with Theorem 3.1's macro-faces; K₄−e and C₄ distribute the same excess
differently).

Consequently:
- γ_N ≥ 1 (non-thickenable) ⟺ every compatible C has E ≥ 8;
- the AK(3) certificate (γ_N = 2) says every compatible C has E ≥ 12 — the census
  histogram (defect ≥ 4 across all 86,400) is exactly this statement.

**Why this matters.** Sphericity = "the A-edges admit a compatible rotation organizing
them into parallel digon chains with only 4 units of slack." The obstruction to
thickenability is thus a statement about the corner structure of the two cyclic words:
which A-edge classes can be made block-parallel under the B-reversal coupling (2.1). The
R3′ program in this language: find a functional of the corner multiset that (a)
lower-bounds E over ALL compatible C, and (b) has controlled behavior under AC1–AC5 at the
CLASS level. (γ_N itself fails (b) — the codex two-line counterexample. The walls of
R3_INVARIANT_LANDSCAPE.md apply to any candidate; a corner-combinatorial invariant is
outside the four walled families, which is what makes this direction worth keeping alive.)

Adversarial check needed: Lemma D1's germ argument uses ν(C(d)) = ν(d) — true since C
permutes darts within a germ cycle by construction; and looplessness for cyclically
reduced words — a loop would need a corner (u, u⁻¹) which reduced words forbid (checked:
also cyclically at the seam). Both steps elementary; audit welcome.

## Addendum (same day): the obstruction is pure synchronization

The link multigraph of any pair with planar simple support (always true at rank 2:
support ⊆ K₄, and parallel edges never destroy planarity) has UNCONSTRAINED orientable
genus 0 — some rotation system embeds it in S². Therefore γ_N > 0 is caused ENTIRELY by
the B-coupling constraint C_{τv} = B C_v⁻¹ B, i.e. by how the occurrence pairing (the
letter order of the two cyclic words) forces the two ends of each generator handle to
interleave. γ_N is a "constrained genus" / synchronization defect of the word pair.

Consequences for R3′:
- Any candidate obstruction must be a functional of the occurrence pairing (word
  combinatorics), not of the abstract multigraph (which is always planar here).
- Move behavior: AC3 is free (cyclic words); AC1 grafts one relator's corner set into the
  other (link grows by the guest's germ degrees, two junction corners replace two seam
  corners); AC4 adds a two-germ component bridged by a single A-edge. γ_N is known
  non-monotone under AC1 in both directions, so only quotient/aggregate functionals can
  survive the class — a candidate must be tested against move-grafting explicitly.
- Related classical machinery to consult when sources are reachable: Wicks forms / genus
  of words (one-face constrained surfaces — dual to our unrestricted-faces,
  constrained-vertices setting), and quadratic-word genus theory. [unverified this
  session — proxy blocks the literature; flag for the user's Colab session.]

## The AK(2) control (29-07, ~08:45 UTC) — calibrating what "zero hits" means

Experiment: exact-key best-first harvest (1,000 pops, cap 15) from AK(2) =
(`xxYYY`,`xyxYXY`) — a TRIVIAL and provably AC-TRIVIAL class — yielding 1,251 canonical
non-degenerate presentations; fable rank solver: **1,251/1,251 NOT_SPHERICAL** (1
UNSUPPORTED). Also: an exhaustive sweep of ALL cyclically-reduced pairs with relator
lengths 3–4 contains NO trivial-group presentations at all, and its 5,872 spherical pairs
are all non-trivial groups.

Reading: sphericity among non-degenerate class members is ~E-rare in EVERY class,
trivial or not; a trivialized class's guaranteed-thickenable members are its
short/degenerate states (standard itself has length-1 relators — below the gate). So
AK(3)'s accumulated zeros are, so far, indistinguishable from the null model — there is
NO phenomenon yet demanding an obstruction. The falsifiable program:
1. Run the AK(2) control at Colab scale until ΣE ≫ 1. Hits at ~E rate ⇒ null model
   validated end-to-end (and the machinery demonstrably CAN find hits).
2. Run AK(3)'s class at matched ΣE. Zero hits when AK(2) shows the expected rate ⇒ a
   genuine class-level phenomenon ⇒ R3′ gets a concrete target.
3. Search-priority upgrade for all future harvests: best-first by E-DESCENDING (the E
   formula rewards concentrated corner distributions, not shortness — a length-ascending
   harvest under-samples the high-E tail). Adopted into the Colab runner spec.

## R3′ arc plan — REVISED per advisor verdict (drafted 13:10, reconciled ~13:45 UTC)

ADVISOR RECONCILIATION (verdict REVISE; every must-address item below):
1. MOVE FORMALISM: the calculus MUST include Lackenby's move (0) (free/cyclic
   reduction). Exact AC3 conjugation w r w⁻¹ ALWAYS creates an A-loop (advisor
   verified: solver UNSUPPORTED); AC3 is "safe" only as (AC3 ∘ (0)). Adopted framing:
   option (a) — Φ(class) := min over exact realizations, automatically (0)-invariant;
   consequence stated honestly: Φ_min = 0 ⟺ the class contains a thickenable member,
   i.e. Φ_min IS the target — so the only meaningful deliverable is a computable STRICT
   LOWER BOUND on Φ_min. This tautology ceiling is now the FIFTH WALL (filed in
   R3_INVARIANT_LANDSCAPE.md).
2. FACTS CORRECTED: the 53-move corridor has 52 decided states + 2 UNSUPPORTED
   (path[23], path[24] — A-loops until reduced; they sit exactly at the reduction
   trap); its transitions are (AC ∘ (0)) composites, NOT exact moves (≥7 strictly
   length-decreasing); it is classical-only (no AC4/AC5 content). The AC2 graft
   DUPLICATES the guest relator (r_j survives): |A′| = |A| + |r_j| (advisor verified
   13 → 19 on the AK(3) self-graft), and A′ is NOT a germ-preserving conjugate of A —
   the structural reason the symmetry-lemma template cannot extend to AC2. The
   addendum's "AC1 grafts" below should read AC2 (project convention AC1 = invert).
3. PRE-REGISTERED CEILING for step 1 (time-boxed): the fibration (restriction
   C′ ↦ C′|_E is well-defined and surjective; fibers = interleavings of the copy's
   darts) + the edge-insertion dichotomy is expected to yield only
   γ_N(post) ≥ γ_N(pre) − 1 per graft — VACUOUS at AK(3) (γ_N = 2) — with the junction
   term a min over factorially large fibers (1.46 × 10¹⁰ for the AK(3) self-graft vs
   the 200k cap). If the write-up lands there: commit as machinery + as a MOVE-ORDERING
   HEURISTIC for harvests (rank grafts by predicted cofaciality/defect change), and
   STOP — no steps 2/4 on that basis.
4. BATTERY (b) REBUILT AS PRE-CONDITION: commit the AK(2) member set and an explicit
   ≤1,000-node AK(2)→standard trivialization path; candidates must be evaluable on the
   length ≤ 2 tail via `gamma_N_factorial_n` (loop- and short-relator-tolerant,
   advisor-verified on ('xXy','yy')) — the discriminating power is ENTIRELY in the
   short tail where Φ must hit 0, not in the 1,251 long members (all NOT_SPHERICAL,
   consistent with any candidate). Run battery (b) BEFORE steps 2/4. Battery (c) is a
   smoke test, not a battery. New legs: AC4/AC5 inertness check of each CANDIDATE
   (Corollary Z covers the defect, not arbitrary functionals — test Φ(P) vs Φ(P+z) on
   the AK3+z root) and a deliberate-mismatch test per the disconnected_split
   discipline.
5. TYPE-CHECK REQUIREMENT for step 2: phases live in Z/deg(g⁺) with deg = (6,6,7,7)
   for AK(3) — no parity map exists (odd y-degree) and every move changes the moduli;
   each candidate must name a realization-independent target group BEFORE being traced.
6. PRIORS (advisor, recorded for honesty): step-1 machinery ~0.7 (no-cancellation
   case) / ~0.2 (with cancellation); genuine invariant ≤ 0.5% — a class functional
   separating AK(3) from standard IS the disproof of stable ACC. Opportunity cost:
   the z-inert-biased rank-2-shadow harvest (handoff item) is higher-EV locally and
   the Δ-defect calculus feeds its move ordering — that synergy is step 1's real value.
7. DEPENDENCY NOTE (advisor): the disproof-side chain needs only the EASY half of the
   master equivalence (standard is thickenable) — NO Lackenby Thm 1.3 dependency,
   unlike the positive direction. A genuine argument for keeping R3′ alive.
8. Codex overlap re-verified DISJOINT; cite their parallel-K₄ lemma/slot table/phase
   equations (lit_AK3_NEUWIRTH_PHASE_OBSTRUCTION.md) rather than re-deriving the
   192-case analysis.

Execution order (revised): battery-(b) artifacts → time-boxed step 1 (no-cancellation
calculus + heuristic) → biased shadow harvest (with the heuristic) → steps 2/4 ONLY if
a candidate survives type-checking and the tail battery.

## Original plan sketch (13:10 UTC, superseded by the reconciliation above)

Claim addressed: DISPROOF side of the stable claim. If a class-functional obstruction
were established and positive on AK(3)'s STABLE class, the master equivalence would give
AK(3) not stably AC-trivial — the stable AC conjecture would be FALSE. (Symmetric
honesty: no such invariant has ever been found by anyone; the plan below is scoped to
produce machinery + falsifiable candidates, not to promise the invariant.)

Plan, in gate order:
1. **Phase-grafting calculus** (pure machinery, provable): formalize how the
   synchronized-planarity phase system (phases s_g per generator, Lemma 4.1; H_{A,B}
   relator-cycle propagation, Lemma 4.2/Thm 4.3; cut-scheme shifts of Thm 6.S) of an
   exact pair TRANSFORMS under each move: AC1 (invert: histogram-safe, symmetry lemma),
   AC3 (rotate: safe), AC2 graft r_i ← r_i r_j (the real content: guest corner set
   spliced at the seam, two seam corners replaced by two junction corners), AC4/AC5
   (Corollary Z: inert). Deliverable: a theorem expressing the post-graft compatible-C
   family and its defect histogram in terms of pre-graft data + junction terms — even
   without any invariance, this is the move-level analysis no per-realization proof
   touches.
2. **Candidate functionals**: from the calculus, extract aggregate summaries with a
   chance of controlled behavior (residues/parities of phase-defect systems, min-excess
   over corner-multiset strata, Kreweras-class aggregates). Each candidate is stated
   with its intended monotonicity/invariance property under the calculus.
3. **Falsification battery FIRST** (before any proof attempt): trace every candidate
   along (a) the 53-move AK(3)↔P25 path (54 exact states, all decided — any claimed
   invariant must survive all 53 moves), (b) the AK(2) corridor (provably trivializable
   class: candidates must NOT be invariantly positive there — 1,251 censused members +
   an explicit trivialization path to standard), (c) the codex 0→1 γ_N jump
   counterexample pair. Only candidates surviving all three go to proof attempts.
4. **Proof or negative write-up**: survivors get adversarial-audited proof drafts;
   failures get committed as negative results steering future sessions (the walls
   document grows).

Division-of-labor check (scout, 13:04 UTC, ab451ab): codex is in per-realization
Fox-calculus/Hessian territory (period-two augmented cut covariance, OPEN) and frozen
Aut-frontier input data; the class-functional seed remains exclusively fable's. No
collision.

## Complementarity note (08:50 UTC): codex phase-obstruction proof

Codex just committed `AK3_NEUWIRTH_PHASE_OBSTRUCTION.md` (a17c7bf): a human,
non-factorial proof that the DISPLAYED AK(3) complex is non-thickenable, derived from the
phase equations — their dormant "derive γ_N ≥ 2 structurally" task waking up. Division of
labor from here: codex owns per-realization phase-obstruction proofs; the fable line owns
(a) the experimental control program (AK(2) control, E-priority harvests, Colab scale),
(b) the rank-3 stable-move hunt, and (c) any CLASS-functional obstruction theory (how
phase systems transform under AC1 grafting — the move-level analysis their per-realization
proofs do not touch). Their proof is the natural technique seed for (c): if the
phase-contradiction pattern can be shown stable under the AC1 corner-grafting operation on
some invariant summary of the phase system, that is the R3′ candidate.
