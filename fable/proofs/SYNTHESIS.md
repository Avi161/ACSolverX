# SYNTHESIS — the fable/proofs lane after 21 cycles

Date: 2026-08-28 · Covers cycles 1–21 (`67ac7fd` … `c829f4d`), notes W1–W6c and
W2b–W2l, every claim bound to a commit in `LOG.md` and replayable by the named
checker.

## The verdict, honestly

**AK(3) remains open in both directions.** Nothing in this lane proves it
AC-trivializable, stably AC-trivializable, or a counterexample. What the lane
established instead is a body of theorems that materially narrows *where a
decision can come from* — by proving the known obstruction technology
systematically blind (with proofs, not absence of evidence), by reducing the
positive route to concrete decidable objects and deciding every one reachable
so far (all negative, all per-spelling), and by driving the codex tower's
quotient program to a single precisely-stated open lemma.

## Direction 1: trivialization (the positive route)

- **Theorem W5.1** (cycle 11): the MMS02 bridge `(A,B,zYX) ~AC (A,B,Xyz)` is
  *equivalent* to "AK(3) is AC-trivial after exactly one stabilization" —
  also equivalent to `Tpub` being AC-trivial and to `(Q1,Q2,z)` being
  AC-trivial. The bridge is not a shortcut to the stable question; it *is*
  the one-stabilization question.
- **Every cheap separating invariant is blind, with proofs** (cycles 1, 11):
  all finite groups (BLM + the W1 vacuity theorem), abelianization, Fox/
  Alexander over `Z[F3^ab]` (the junk ideal is the whole augmentation ideal),
  cyclic Alexander, free nilpotent classes 2 and 3 (explicit verified
  connecting chains, 47 and 991 moves). Nothing known forbids the bridge.
- **The thickenability route is open in theory and closed in practice so
  far** (cycles 13, 15, 16): the Neuwirth/Lackenby machinery is rank-general
  on the repo's records; a bare stabilization row is thickenability-inert
  (Lemma W6.1), so the genuinely new rank-3 object is `Tpub` — decided **NOT
  thickenable as spelled** by a new certified solver family with a proved
  completeness lemma (3,120 cases exhaust 2.1e16 orderings). The closed
  rank-3 AC ball around `(AK3,z)` is **completely decided at ceilings 16 and
  18** (no thickenable state exists) and 95%/91% decided at 20/22 — every
  decision negative, zero quarantine events. Negatives are per-spelling:
  the route stays open on the undecided residue and on larger balls
  (production-scale closure is a Colab handoff, not a local run).

## Direction 2: counterexample (the obstruction route, through the codex tower's quotient)

The hardest depth-4 signature's period-two quotient (`Q = C2*Z`) — the layer
the codex tower anchors on — was quantified and then climbed:

- **Layer 0** (cycles 4–6, 9): the baseline family is unbounded (17 → 106
  essential chains at caps 12 → 17, no plateau) but collapses to an exact
  **six-parameter normal form** (generator = census at every tested cap, 0
  missed / 0 spurious). A per-baseline tower cannot terminate.
- **Layer 1** (cycles 10, 14, 17, 20): liveness does **not** factor through
  conjugacy classes (a proved obstruction to the naive uniformization), yet
  layer 1 is **obstruction-free for the entire census**: the double-coset
  invariant gives `d = 1` on all 44 finite-index chains (PROVED — the image
  of the operator columns is exactly `ker ε`, so every window is solvable
  over `Z`) and on all 23 infinite-index chains (EVIDENCED — exact margin
  law, not a theorem). Explicit corrections verify literally in `F(c,t)`.
- **Layer 2** (cycles 18, 19, 21): no torsion anywhere (`Γ` is torsion-free
  on 67/67), `d₂ = 1`, and `Ξ_Z : C₂ → W_Q` is an **isomorphism** — so the
  entire layer-2 question is whether one affine-quadratic residual class
  `Ξ_Z(Θ(F))` can vanish over the complete correction family (conditional
  on the source's (3.1)+(3.5)). Complete mod-2 enumerations exclude zero on
  every tested sublattice of every analysable baseline (up to 2^20 classes
  on a saturated direction set) — but the finite computation is one-sided
  in exactly the direction that cannot fire, so **no obstruction is
  claimed**. The missing piece is now one precise lemma (the Θ translation
  cocycle / finite generation of `V_{H_fin}` up to the `Q`-action — W2m,
  in flight at time of writing).

Either resolution of that lemma is decisive *for this quotient*: attainable
everywhere ⇒ the quotient is blind through layer 2 and the codex tower
cannot terminate the signature inside it; unattainable for a baseline ⇒ the
program's first genuine death certificate, killing that baseline's entire
lift family.

## What the lane paid for its rigor (and why the numbers can be trusted)

Three defects were found *by the lane's own controls* and repaired with full
reconciliation, each now a lesson in `LESSONS.md`:

1. The W1 finite-quotient test was theorem-forced vacuous → rewritten as the
   vacuity theorem (cycle 2).
2. A base-coset re-rooting bug under W2g's coset tables → caught by an
   effective vanishing control installed at review, fixed, results
   *strengthened* (cycle 14).
3. A wrong `L0` operator column on 59/67 chains — invisible to every control
   anchored at the codex witness, exposed by literal free-group verification
   (cycle 19) → all five columns re-derived, the whole chain re-verified
   claim by claim, retractions posted in place (cycle 20).

Standing discipline: every delegate result is replayed independently before
commit; every solution is verified in the object the equation is about, not
the linearisation; every note carries scope/nonclaims; every cycle is a
two-step SHA-bound commit.

## What would decide AK(3) from here, concretely

Ranked by leverage:

1. **W2m's lemma, either way** — decides the layer-2 question on the
   complete family for this quotient.
2. **A thickenable AC-reachable rank-3 spelling** — any quarantined positive
   surviving independent rotation replay + Regina (Pipeline B) would prove
   AK(3) AC-trivial after one stabilization. The solver families now decide
   91–100% of the enumerated ball; the residue and larger ceilings are
   enumerable at production scale (Colab handoff).
3. **A uniform layer-≥2 argument over the census** (or a different quotient
   with better torsion) — the only counterexample-side route this lane's
   results leave standing inside the period-two quotient.
4. **Production-scale search closures** (user-run): ceilings 19–20 of the
   rank-2 component, deeper mu-ladders, wider bridge preflights — all
   config-ready in the notes.

## Nonclaims

No claim about AK(3)'s AC or stable-AC status, in either direction. Layer-1/2
statements are about one quotient of one signature and are conditional where
marked. Thickenability negatives are per-spelling. Census caps are ceilings;
every count is a lower bound.
