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

## R5 (fake surfaces) — SCOUTED 29-07 ~15:30 UTC: BLOCKED, and it confirms Wall 5 twice

Fagan–Qiu–Wang arXiv:2412.12293, abstract VERBATIM (mirrored primary copy, since arXiv
itself is proxy-blocked): "The stable Andrews-Curtis conjecture is equivalent to the
conjecture that every contractible fake surface is 3-deformable to a point. We prove
that every contractible fake surface of complexity less than 6 is 3-deformable to a
point by induction." Complexity = number of true vertices (companion paper
arXiv:2406.09439, definitions corroborated by the authors' own code).

Verdict: **BLOCKED, tautologically.** Complexity is minimised over the 3-deformation
class, so: if AK(3) is stably AC-trivial its class contains the point, hence a
complexity-1 surface; if it is not, then by their theorem its class contains nothing
below complexity 6. Hence **min-complexity(AK(3)) < 6 ⟺ AK(3) is stably AC-trivial** —
exhibiting a low-complexity surface in the class IS the proof, there is no cheaper
certificate, and no lower bound on AK(3)'s complexity can exist short of settling the
question. This is precisely **Wall 5 (the min-realisation tautology) instantiated in a
second, independent formalism** — complexity in place of γ_N — which is good evidence
that Wall 5 is a real feature of the problem and not an artefact of our grading.

Secondary blocker: complexity does not separate AK(3) from standard by arithmetic
either, since total length is not an AC invariant. Derivation validated against all 5,389
rows of the authors' census (every edge carries exactly 3 face-germs; |det| = 1 on
5,389/5,389).

[CORRECTED — the sentence that stood here was wrong twice over, and R8 supplies the
repair. It read: "4 AC4 moves plus an AC1 give a 6-generator, length-18 presentation,
exactly the complexity-5 profile." First, under this line's own numbering AC1 is
INVERSION, which is length-preserving — the move meant was AC2. Second, and fatally, the
repaired statement is still false in substance: R8's **Theorem A1** shows the census
profile is sharper than (n generators, n relators, length 3n) — in the tree-collapse
presentation **every generator occurs exactly 3 times**, verified on 5,389/5,389 rows.
The (6, 18) presentation reached by stabilisation has occurrence vector (7, 7, 2, 1, 1, 1),
not (3, 3, 3, 3, 3, 3), so it does not meet the profile at all. What actually reaches the
sharp profile from AK(3) is 7 Tietze splits landing at rank 9 — the complexity-8 profile,
not rank 6. See `R8_FAKE_SURFACE_COMPLEXITY.md` §4.]

Unverified dependencies if anyone revives this: whether "complexity < 6" is stated for
all or only cellular fake surfaces; the exact form and direction of the equivalence
(neither is in the abstract, and the full text is unreachable this session).

## Literature correction to propagate (same scout)

Lisitsa, "Stable Andrews-Curtis trivialization of AK(3) revisited", arXiv:2501.18601,
PUBLISHED in J. Computational Algebra, asserts in its abstract that Shehper et al.
"demonstrated that ... AK(3) ... is stably AC-equivalent to the trivial presentation.
This result eliminates AK(3) as a potential counterexample". That is the RETRACTED
claim: the current Shehper source (github.com/ammedmar/ac_paper, `app/wirtinger.tex`)
says "we cannot use Reidemeister moves to show the stable AC-triviality of MMS3 and
therefore AK(3) as well", and `app/mms.tex` adds that the presentations "are not
necessarily stably AC-trivial". FRAMING.md trap 1 is correct and should note that the
published Elsevier abstract propagates the withdrawn claim — anyone searching the
literature hits it first.
