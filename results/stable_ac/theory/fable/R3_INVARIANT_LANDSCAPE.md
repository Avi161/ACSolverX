# R3 — Disproof-side invariant landscape (status: DORMANT, documented)

Claim addressed: **disproof of stable ACC** would need a quantity invariant under AC1–AC5
separating some balanced presentation of 1 (e.g. AK(n)) from standard. This note maps what
any such invariant must evade, from a literature audit (29-07-2026; abstract-level only —
the session proxy blocks all scholarly full-texts; every load-bearing item must be re-read
from PDF before use in a proof. Citations verified to exist via search index).

## The four walls (independent no-go results)

1. **χ = 1 homology collapse** (Bobtcheva, math/0012121; Bobtcheva–Quinn, math/0012212):
   for the Lie-family (quantum-group) categories over Z_(p)[v], the 0-term Ohtsuki-expansion
   2-complex invariant "depends only on homology" when χ ≥ 1. Balanced presentations have
   χ = 1 and (for trivial group) trivial homology ⇒ these Quinn-type invariants are provably
   constant across all our objects. (Scope: Lie family, 0-term. Higher terms/other
   categories not covered by that sentence — see cracks.)
2. **Universal-pairing non-positivity** (Khovanov–Krushkal–Nicholson, arXiv:2312.07429):
   the universal pairing for 2-complexes is not positive; two 2-complexes with the same π₁
   and χ are 3-deformation equivalent to complexes whose difference is a null vector —
   "the universal pairing does not detect the difference between simple homotopy equivalence
   and 3-deformations". Kills every "positive/unitary" TQFT-style invariant for AK(n) vs
   standard (same π₁ = 1, same χ = 1). Strongest known no-go in our exact setting.
3. **Semisimple blindness** (Reutter, arXiv:2001.02288, Thm A): semisimple oriented 4d
   TQFTs cannot distinguish S²×S²-stably-diffeomorphic 4-manifolds; "all currently known 4d
   field theories are semisimple". Kills any invariant of a 4-thickening evaluated by a
   semisimple theory.
4. **Closed-4-manifold standardness** (Gompf 1991 Topology 30; Akbulut Ann. Math 171 (2010);
   Gompf AGT 10 (2010)): the Akbulut–Kirby / Cappell–Shaneson homotopy 4-spheres associated
   with AK(n) are standard — any invariant factoring through the closed smooth 4-manifold
   agrees on AK(n) and standard.

Also: Barmak's winding invariant (arXiv:1806.11493, 1904.10072) genuinely distinguishes
Q*-classes (AC + Nielsen) — but its mechanism (GL₂ \ GE₂ over Z[X±,Y±]) is expected to die
under stabilization (GL_n = GE_n range); it is a Q* result, **not** Q**. Terminology pin
(Barmak): Q = AC moves, Q* = + Nielsen, Q** = + stabilization; Q**-equivalence ⟺
3-deformation of presentation complexes.

## The single identified crack

A candidate must be simultaneously: non-(simple-)homotopy, non-homological, not a function
of (π₁, χ), non-positive-pairing, not factoring through the closed 4-manifold, non-semisimple,
and genuinely Q**-invariant. The only known structural home: **non-semisimple, spine-dependent
functionals on the Bobtcheva–Piergallini category 4HB of 4-dim 2-handlebodies up to
2-deformation** (math/0612806; Bobtcheva arXiv:2309.04830 proves 4HB is a strict REFINEMENT
of the spine (2-complex) category — so spine-dependence must be proven, not assumed):

- **D1**: Beliakova–De Renzi's non-semisimple Kerler–Lyubashenko functor J₄ on 4HB
  (arXiv:2105.02789) — isolate its spine-dependent output sub-family (analogue of
  Bobtcheva–Messia's "second subset"), then test non-constancy at χ = 1. Step one has never
  been done by anyone.
- **D2 (cheapest check)**: Bobtcheva–Messia's spine-only HKR family (AGT 3 (2003),
  math/0206307) has NO published evaluation on any AK(n). Either it dies by an extension of
  the χ ≥ 1 collapse beyond the Lie family (then write that down — a publishable negative),
  or it is an unexploited computation. Requires the PDF.

Parked secondary: ideal-valued Turaev–Viro (King math/0509187 — announced AC application
never appeared); FKL spineless-5-manifold route (arXiv:2401.03498 — needs an exotica
detector, inherits walls 3+1); trisection non-semisimple triples (arXiv:2309.08461 — none
found ≤ dim 11, and wall 4 applies anyway).

## Also logged (positive-direction, others' work)

- Fagan–Qiu–Wang arXiv:2412.12293: stable ACC ⟺ every contractible **fake surface**
  3-deforms to a point; proved for complexity < 6. A reformulation route this line may
  revisit (R5 candidate) — complexity replaces χ as the grading, which is also the escape
  hatch for wall 1 (the collapse fails at χ < 0 / different gradings).
- No post-Lackenby invariant-side work found (June 2026 preprint; index lag).

## Route status

DORMANT: blocked on PDF access for D1/D2 (proxy denies all scholarly hosts this session) and
outprioritized by R1 (decidable, positive-direction). Reactivation trigger: PDF access, or an
R1/R2 dead end. Next concrete actions on reactivation: (1) re-read math/0012212's χ ≥ 1
proof and check whether it extends to all unimodular ribbon HKR input (if yes → negative
result write-up; if no → evaluate the Bobtcheva–Messia family on AK(3)); (2) the J₄
spine-descent question.

## Wall 5 (added ~13:45 UTC, from the R3′ advisor vet): the min-realization tautology

Any realization-level defect functional (γ_N, digon excess, phase-defect aggregates —
anything computed from an exact word realization) has exactly one canonical
(0)-invariant class version: Φ_min(class) = min over exact realizations. But
Φ_min = 0 ⟺ the class contains a thickenable member — i.e. the natural class-functional
IS the open target, not a tool for it (for AK(3)'s stable class, Φ_min = 0 is literally
the stable-triviality question via the master equivalence's easy half). Consequence:
every R3′ candidate must be a genuine RELAXATION — a computable functional PROVABLY
lower-bounding Φ_min strictly below the per-realization value — or it is either
ill-posed (realization-dependent, killed by move (0): exact AC3 conjugation always
creates an A-loop) or tautological. This wall is move-formalism-generated rather than
topological, so it constrains word-combinatorial candidates that walls 1–4 do not
reach. Recorded as a committed negative regardless of what the grafting calculus
produces.
