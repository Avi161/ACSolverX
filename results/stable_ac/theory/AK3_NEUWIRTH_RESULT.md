# What counts

The load-bearing statement is about an **exact word-realized presentation
complex**, not its group and not its Andrews--Curtis class.  With the
occurrence conventions proved in
[`AK3_NEUWIRTH.md`](../../../literature/proofs/AK3_NEUWIRTH.md), a connected
Neuwirth link is orientably thickenable exactly when its compatible rotation
surface can be a sphere, equivalently when \(\gamma_N=0\).  For a balanced
presentation of the trivial group, such a positive would imply classical
AC-triviality.  No positive was found here.

The independent exhaustive target certificate
[`ak3_neuwirth_census.json`](ak3_neuwirth_census.json) enumerates all
\(5!\,6!=86{,}400\) compatible cyclic-order pairs for each exact target.  Its
direct permutation implementation and independent dart audit agree on the
complete ordered traces.

| Exact presentation | Defect histogram (defect: count) | Minimum \(\gamma_N\) | Minimizers |
|---|---:|---:|---:|
| AK(3), `xxxYYYY | xyxYXY` | `4:724, 6:14882, 8:55438, 10:15356` | 2 | 724 |
| orbit-2, `YYXXyx | YYYxyXX` | `2:2, 4:702, 6:14932, 8:55132, 10:15632` | 1 | 2 |

Thus the exact AK(3) value \(\gamma_N=2\) is **census-derived**.  The orbit-2
lower bound is also proved without enumeration by forced digon saturation
and a cyclic-neighbour contradiction, and its upper bound is independently
face-traced on an explicit torus rotation in
[`ORBIT2_NEUWIRTH_GENUS.md`](../../../literature/proofs/ORBIT2_NEUWIRTH_GENUS.md).
The support there is a planar abstract \(K_4\); the obstruction is the
synchronized reversal constraint, not abstract graph nonplanarity.

The non-factorial decision method is the signed-rank theorem in
[`AK3_SYNCHRONIZED_PLANARITY.md`](../../../literature/proofs/AK3_SYNCHRONIZED_PLANARITY.md).
For connected loopless support \(K_4\), \(K_4-e\), or \(C_4\), it classifies
all spherical rotation schemes, translates the opposite-generator
\(B\)-reversal into two phase families, and propagates ranks exactly around
the relator cycles with global all-different checks.  The implementation was
exhaustively cross-checked against the factorial census on all 1,412
supported canonical cyclically reduced word-pairs of total length at most
seven: 328 \(K_4\), 568 \(K_4-e\), and 516 \(C_4\), with agreement on every
YES and NO.  It also agreed on all 18 height-17 component states affordable
to the factorial check—six \(86{,}400\)-case states and twelve
\(518{,}400\)-case states.  The finite checks, including positive witnesses
and split \(K_4-e\) cuts, are in
[`test_neuwirth_rank_solver.py`](../../../tests/stable_ac/test_neuwirth_rank_solver.py).

Finally,
[`AC17_CERTIFICATE.json`](../../../experiments/stable_ac/cov/ak_3_universal_test/AC17_CERTIFICATE.json)
replays a classical AC path from AK(3) to orbit-2 through total length at most
17.  Its length is **17 Definition-2.1 macro edges, not 17 elementary
moves**.  It proves that the two exact presentations are classically
AC-equivalent to each other; it does not trivialize either one.

# What was ruled out

The target census rules out an orientable thickening of each of the two exact
base complexes: AK(3) has minimum genus two and orbit-2 has minimum genus one.
Those different values inside one classical AC class also show concretely
that \(\gamma_N\) is not an AC invariant.  It must be recomputed after every
move, so neither negative verdict can be transported to another
representative.

The component certificate
[`ak3_component_thickenability.json`](ak3_component_thickenability.json)
then decides every state in the closed height-17 component:

- root `xxxYYYY | xyxYXY`; canonical root
  `YXYxyx | YYYYxxx`;
- total-length ceiling 17, per-relator child cap 16, cyclic moves enabled,
  and the full rather than seam-only Definition-2.1 child set;
- node cap 1,000, actual pops 1,000, component size 1,000, queue exhausted,
  canonical fixed points checked, and closure under the bounded child
  generator verified;
- authenticated source commit
  `fbeb16beed7bf4a92ff8937733f748e2ac32f328`;
- sorted-state digest
  `630a583617aa0f24ac365eca2d5b151d2dd9e3f6a963130a0b36009871cb0361`
  and ordered-decision digest
  `04d662297d88910a423e955eb5456bdb6f6bbe4fb88e4e47879ab6bf6a6e660e`;
- support counts \(720\ K_4+278\ (K_4-e)+2\ C_4=1{,}000\);
- verdict counts `NOT_SPHERICAL: 1000`, hence dispositions
  `NOT_THICKENABLE_EXACT_COMPLEX: 1000`.

There was no spherical witness, no positive thickenability verdict, and no
candidate requiring independent Regina validation.  This is an exhaustive
negative for that **bounded component and those exact complexes**.  It is not
an obstruction to classical AC, stable AC, or a thickenable representative
outside the component.

# Live leads

The decisive one-sided route remains to reach any thickenable presentation in
AK(3)'s classical or stable move class.  The height-17 component is closed and
negative, so that route must leave this bounded component—by greater height,
by stable AC4/AC5 moves, or by another rigorously certified change of
representative.  A positive compatible spherical rotation would then need
the independent regular-neighbourhood/Regina audit before being promoted.

The signed-rank formulation is the main reusable theoretical gain: it
replaces factorial rotation enumeration on the three proved four-germ
support types by exact scheme/phase/seed propagation.  Supports outside
\(K_4\), \(K_4-e\), and \(C_4\), disconnected links, and links with \(A\)-loops
remain fail-closed and require the general Synchronized Planarity route or a
new proof.

Two proof questions remain worthwhile without overselling computation:
derive the AK(3) lower bound \(\gamma_N\ge2\) structurally rather than from its
86,400-case census, and determine how useful \(\gamma_N\) is as a
non-invariant search potential along carefully chosen AC4/AC5 move families.
Its non-invariance is a feature for finding a zero, but forbids using a
positive value as a conserved obstruction.

# Open ledger

- **Exact-complex thickenability:** AK(3) is certified non-thickenable in its
  displayed word realization (\(\gamma_N=2\)); orbit-2 is likewise
  non-thickenable (\(\gamma_N=1\)).  All 1,000 exact complexes in the closed
  height-17 component are certified non-thickenable.
- **Classical AC:** AK(3) and orbit-2 are certified equivalent to each other
  by 17 Definition-2.1 macro edges.  Neither is certified equivalent to the
  standard presentation.  The bounded negative does not prove classical
  nontriviality.
- **Stable AC:** AK(3)'s stable AC-triviality remains **OPEN**, as recorded in
  [`IDEAS.md`](../../../experiments/IDEAS.md),
  [`OBSTRUCTION_BARRIER.md`](OBSTRUCTION_BARRIER.md), and the corrected
  source-status note
  [`literature/txt/README.md`](../../../literature/txt/README.md).  The
  source chain once used to claim stable triviality is broken by the MMS02
  p.10 Wirtinger-presentation misprint documented in Shehper et al.'s
  Appendix F.
- **Repository conflict:** the statement in the older
  [`ak_3_universal_test/RESULTS.md`](../../../experiments/stable_ac/cov/ak_3_universal_test/RESULTS.md)
  that AK(3) is stably AC-trivializable is stale and conflicts with those
  corrected open-status sources.  The certificate payloads themselves do
  not conflict: AC17 asserts only AK(3)-to-orbit-2 classical equivalence, and
  both Neuwirth certificates assert only exact-complex and bounded-component
  negatives.

Therefore AK(3) remains open.  Nothing in these results proves that it is a
counterexample to either the classical or stable Andrews--Curtis conjecture.
