# One-edge primitive compression in rank-three AK(3) corridors

Date: 2026-07-24

Status: the stable implication is **PROVEN**. The finite floor-12 candidate is
**UNVERIFIED** until its full certificate is built and replayed.

## 1. Primitive product theorem

Let

\[
 {\cal R}=(A_0,A_1,A_2)\subset F(x,z,t)
\]

be stably AC-equivalent to AK(3). Choose \(i\ne j\), a sign
\(\delta\in\{\pm1\}\), and cyclic rotations \(U\) of \(A_i\) and \(V\) of
\(A_j^\delta\). Replace

\[
 A_i\longmapsto W=\operatorname{cyc}(UV).
\]

This is a Definition-2.1 AC1--AC3 composite.

### Theorem 1.1 — PROVEN

If the cyclic conjugacy class \([W]\) is primitive in \(F(x,z,t)\), the new
rank-three presentation is stably AC-equivalent to a balanced rank-two
presentation. If that quotient has complete rank-two Aut-floor at most 12,
AK(3) is stably AC-trivial.

### Proof

The product move is classical AC. Apply the primitive-single removal theorem
to \(W\). If the quotient floor is at most 12, compose its complete ambient
automorphism with MM03 Theorem 1.1 as scoped in `MU_CRITERION.md`. \(\square\)

The quotient Aut-orbit is independent of the chosen automorphism
straightening \(W\), by the proven quotient-independence theorem.

## 2. Exact necessary gates

### Abelian gate

If \(W\) is primitive, its exponent-sum vector in \(\mathbb Z^3\) is a
primitive vector. Therefore

\[
 \gcd(|e_x(W)|,|e_z(W)|,|e_t(W)|)=1.
\]

Rotations do not change this vector, so the gate is computed once per ordered
target/other/sign choice.

### Whitehead-graph gate

Use the cyclic Whitehead graph on the six signed basis letters, with an edge
from \(p\) to \(q^{-1}\) for every cyclic adjacent pair \(pq\).

The classical cut-vertex lemma says that a cyclically reduced primitive word
of length greater than one has a disconnected Whitehead graph or a cut
vertex. A connected graph without a cut vertex therefore certifies
nonprimitivity without running descent.

The production gate must be cross-checked on every already-certified
primitive relator from the primitive-single census; zero may be rejected.

Words passing both gates undergo complete rank-three Whitehead descent. The
fast implementation changes only scoring: it computes the cyclic length of
all 90 images, applies a chosen strict descent, and canonicalizes that one
image. The endpoint and composed automorphism are checked by the existing
independent replay layer.

## 3. Finite candidate

Use all 3,016 verified cyclic rank-three sources. Enumerate:

- all ordered target/other pairs;
- both signs of the other relator;
- every cyclic rotation of both factors.

Deduplicate by `(source, target, canonical product word)`. For every primitive
product, apply its Whitehead witness to the full child tuple, remove it, and
compute the complete rank-two floor.

### One-edge primitive floor-12 lemma — UNVERIFIED

At least one induced quotient has complete Aut-floor at most 12.

A positive proves stable AC-triviality. A negative refutes only this finite
one-edge primitive corridor; it is not an obstruction to other stable
representatives or two-edge/nontriangular mechanisms.
