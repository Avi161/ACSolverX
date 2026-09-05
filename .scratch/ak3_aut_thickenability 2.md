# Simultaneous ambient automorphisms do not presently transport exact thickenability

## Verdict

Let

\[
P=\langle x_1,\ldots,x_n\mid r_1,\ldots,r_m\rangle
\]

be a presentation in the exact word-realized sense used by
`literature/proofs/AK3_NEUWIRTH.md`: the spelling of every relator, including
every occurrence, is part of the presentation complex.  The following three
statements must not be conflated.

1. **Signed permutations are invariant.**  Simultaneously permuting the
   generators, or replacing one generator by its inverse, gives a cellular
   homeomorphism of the exact presentation complexes.  Hence it preserves
   thickenability in both directions.
2. **Stable AC class is invariant under all ambient automorphisms on a
   balanced trivial-group presentation.**  This is Proposition 3.3 of
   `literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md`.  It is an algebraic
   stable-AC theorem, not a thickenability theorem.
3. **For a Nielsen transvection, exact-complex thickenability has not been
   proved invariant.**  A handlebody homeomorphism or meridian-disc slide
   realizes the induced automorphism of the *marked free group*, but it does
   not identify the old embedded presentation spine with the exact complex
   whose relators are the words \(\phi(r_i)\) on the old rose.

Thus the strongest presently justified AK(3) conclusion is:

> The proved nonthickenability of the displayed AK(3) complex propagates
> through signed permutations (and relator reordering/orientation changes that
> are actual cellular homeomorphisms), but it does **not** presently propagate
> through the whole \(\operatorname{Aut}(F_2)\)-orbit.  In particular, reduced
> transvection images must not be discarded as automatically nonthickenable.

There is no counterexample in the local sources showing that a transvection
actually changes thickenability.  Accordingly the blanket assertion
"thickenability is not invariant" is also **[unverified]**.  What is proved
below is that the standard handlebody argument does not prove invariance and
that the exact missing implication is real, not a wording issue.

## 1. The exact object and the easy generators

For an exact word presentation, \(K_P\) consists of one vertex, one oriented
loop for each \(x_i\), and one 2-cell whose attaching boundary traverses the
specified letters of each \(r_j\).  This is the object in
`literature/proofs/AK3_NEUWIRTH.md`, especially its scope paragraph and
Sections "Neuwirth genus potential" and "What the criterion does not imply."

If \(\phi\) permutes the basis, relabel the loop cells.  If
\(\phi(x_i)=x_i^{-1}\), reverse the characteristic map of the \(i\)-th loop.
Extend the resulting graph homeomorphism over every 2-cell using the same
characteristic disc.  This is a cellular homeomorphism

\[
K_P\cong K_{\phi(P)}.
\]

This proves exact thickenability invariance for permutations and inversions;
no handlebody or Andrews--Curtis argument is needed.

The third Nielsen generator is different.  For

\[
\tau(x_i)=x_i x_j,\qquad \tau(x_k)=x_k\quad(k\ne i),
\]

there is no homeomorphism of the one-vertex rose inducing \(\tau\): a graph
homeomorphism of a rose only gives a signed permutation.  Consequently
\(K_P\) and \(K_{\tau(P)}\) are not related by the preceding cellular
homeomorphism argument.

## 2. What the handlebody argument really gives

Let \(H\) be a genus-\(n\) handlebody with a marked spine \(R\).  A handlebody
homeomorphism naturally determines only an outer automorphism of
\(\pi_1(H)\).  To obtain the specified \(\phi\in\operatorname{Aut}(F_n)\), one
must additionally choose a basepoint and a basing path (or a based lift).
Changing that path composes with an inner automorphism, so it simultaneously
conjugates all relators; that ambiguity cannot be suppressed for an exact
semigroup spelling.  The elementary outer realizations are standard:

- exchange two 1-handles for a basis permutation;
- turn one 1-handle over for inversion;
- slide a meridian disc/1-handle for a transvection.

Lackenby makes the last point explicit: a disc slide in the first meridional
system changes generators by Nielsen move (5), and reversing a disc
orientation gives move (6) (arXiv:2606.06122v1, Section 6, pp. 20--22,
especially lines 1262--1273 and 1299--1303 in the text extraction).  Section
2.2, pp. 6--8, gives the exact semigroup substitutions for those moves.

Now grant the handlebody argument its strongest missing hypotheses: choose a
based lift that induces the actual automorphism \(\phi\), not merely its outer
class, and suppose the handlebody homeomorphism extends over an ambient
neighbourhood containing the embedded 2-cell pages.  Even under these extra
assumptions, the extension carries the embedded spine to another embedded
spine whose 1-skeleton is the *moved* rose \(R'=h(R)\).  In the intrinsic edge
basis of \(R'\), its attaching words are still \(r_1,\ldots,r_m\).  The words
\(\phi(r_i)\) appear only after expressing the loops of \(R'\) in the fixed
marking of \(R\).  Replacing the moved rose by that fixed rose requires a
retraction/fold

\[
R'\longrightarrow R.
\]

That fold is not an embedding and is not the restriction of the handlebody
homeomorphism to a cellular self-homeomorphism of \(R\).  Replacing the moved
rose by the fixed rose therefore replaces an embedded spine by a homotopy model;
it does not produce an embedding of the exact complex
\(K_{\phi(P)}\).

Equivalently, a Heegaard diagram records disjoint attaching curves on
\(\partial H\) and their elements in \(\pi_1(H)\).  Applying \(h\) preserves
the disjoint curve system.  Exact presentation-complex thickenability asks for
more: a compatible embedded book of occurrence pages along one specified
rose, with the reversal coupling at the two ends of every generator.  Passing
from curves to their words on another rose can introduce folds, bigons, and
free cancellations.  The handlebody homeomorphism does not supply the
required occurrence-page embedding after that passage.

This is precisely why Lackenby changes conventions before Theorem 6.4.  He
states that after treating relations as elements of the free group rather
than words in the free semigroup, thickenability is "not immediately
well-defined," because one semigroup realization might be thickenable while
another is not (arXiv:2606.06122v1, p. 22, lines 1312--1320).  That warning is
directly load-bearing here.

## 3. Why disc slides and 3-deformations do not close the gap

Lackenby's Theorem 6.3 uses meridian-disc slides to obtain a
\(Q^*\)-transformation from a thickenable presentation to a standard one.  It
does **not** assert that every intermediate exact presentation complex is
thickenable.  In the same proof:

- slides in the first meridian system give Nielsen generator moves;
- slides in the second system give relator multiplication/conjugation moves.

Both are changes of Heegaard data.  If "the core of the changed handle
decomposition is automatically the exact embedded presentation complex" were
a valid general principle, the same argument would also make relator slides
preserve thickenability.  No such AC-invariance theorem is available; the
tracked Neuwirth proof correctly says a negative verdict cannot be transported
along an AC path.

Likewise, formal 3-deformation does not solve the issue.  Lackenby's Lemma 5.1
identifies \(Q^{**}\)-transformations with formal 3-deformation, while
Proposition 5.2 proves only the direction

\[
\text{common 3-manifold regular neighbourhood}
\Longrightarrow
\text{3-deformation equivalent}.
\]

The converse needed here is not stated.  An abstract expansion/collapse
sequence need not present every intermediate polyhedron as an embedded spine
of one common 3-manifold.

Therefore the exact missing lemma for a transvection is:

> **[unverified] Transvection spine lemma.**  For every embedded exact
> presentation complex \(K_P\), a Nielsen 1-handle slide can be accompanied by
> occurrence-page moves in a common regular neighbourhood so that the final
> embedded spine is cellularly the exact chosen spelling of
> \(K_{\tau(P)}\); conversely the inverse slide recovers \(K_P\), including all
> free-cancellation pairs.

Neither the local proof corpus nor the cited primary sources prove this lemma.
Without it, the handlebody argument stops one step before exact
thickenability.

## 4. Separation from the stable ambient-automorphism theorem

For a balanced presentation of the trivial group, Proposition 3.3 of
`literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md` proves

\[
P\sim_{\mathrm{st}}\phi(P).
\]

Its proof adjoins fresh generator--relator pairs and performs substitution and
removal.  This establishes equality of stable AC classes.  It neither embeds
the final exact 2-complex nor says that thickenability is stable-AC invariant.
Indeed, the whole Lackenby strategy seeks a *later* thickenable representative;
a negative at one representative is intentionally one-sided.

For AK(3), therefore,

\[
K_{AK3}\text{ nonthickenable}
\quad\centernot\Longrightarrow\quad
K_{\phi(AK3)}\text{ nonthickenable}
\]

with the present theorem set, even though
\(AK3\sim_{\mathrm{st}}\phi(AK3)\) is proved.

## 5. Safe finite route

No broad Aut search is needed to state the safe next experiment.  For any
predeclared finite list \(S\subset\operatorname{Aut}(F_2)\):

1. record each automorphism by explicit Nielsen generators and record both the
   literal semigroup substitution and the chosen freely/cyclically reduced
   output;
2. treat every resulting word tuple as a new exact complex and run the full
   Neuwirth criterion independently, retaining a replayable rotation witness
   for a positive or a complete obstruction certificate for a negative;
3. quotient without recomputation only by actual cellular symmetries: signed
   generator permutations, relator permutation, cyclic change of a 2-cell
   basepoint, and 2-cell orientation reversal, each with an explicit
   homeomorphism argument;
4. do not transfer a negative across a transvection or across free reduction;
   test the literal and reduced spellings separately unless the exact local
   cancellation/spine lemma has first been proved;
5. independently validate any positive by constructing its regular
   neighbourhood and checking that it is a 3-manifold (and, in the balanced
   trivial case, a 3-ball), before invoking Lackenby's Theorem 1.3.

A successful positive on one exact Aut-image would still be decisive for
stable AC: Lackenby's theorem trivializes that thickenable image classically,
and the proved stable ambient-automorphism theorem carries the conclusion back
to AK(3).  The present audit only says that a negative at the base cannot prune
those candidates.

## Sources

1. `literature/proofs/AK3_NEUWIRTH.md`, exact occurrence model, Neuwirth
   criterion, and the explicit non-invariance guard for AC paths.
2. `literature/proofs/AK3_NEUWIRTH_PHASE_OBSTRUCTION.md`, theorem that the
   displayed AK(3) complex is nonthickenable and its deliberately local scope.
3. `literature/proofs/AK3_DUAL_SOURCE_COMPRESSION.md`, Proposition 3.3
   (stable ambient automorphisms in every rank).
4. Marc Lackenby, *The stable Andrews--Curtis conjecture and thickenable
   presentations of the trivial group*, arXiv:2606.06122v1: Section 2.2
   (Nielsen moves (5),(6)); Section 5, Lemma 5.1 and Proposition 5.2; Section
   6, Lemma 6.2 and Theorem 6.3; and especially p. 22, lines 1312--1320 on the
   semigroup/free-group thickenability ambiguity.
5. L. Neuwirth, *An algorithm for the construction of 3-manifolds from
   2-complexes*, Math. Proc. Camb. Phil. Soc. **64** (1968), 603--614,
   especially pp. 604--611.  The primary article supplies the exact
   presentation-complex criterion; it does not state ambient-Aut invariance.
