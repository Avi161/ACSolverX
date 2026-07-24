# Primitive-pair elimination in rank-three AK(3) corridors

Date: 2026-07-24

Status: the elimination theorem is **PROVEN**. The finite AK(3) corridor
candidate in Section 4 is **UNVERIFIED** until its Whitehead certificate is
built and replayed.

## 1. Primitive conjugacy-class pairs

Let

\[
 P=\langle a,b,c\mid A,B,C\rangle
\]

be a balanced presentation of the trivial group.

Call the relator conjugacy classes \(([A],[B])\) a primitive pair if there is
an automorphism \(\phi\in\operatorname{Aut}(F(a,b,c))\) such that
\(\phi(A)\) and \(\phi(B)\), after independent conjugation and inversion, are
two distinct basis generators.

This conjugacy-class formulation is the correct one for AC relators:
independent conjugation and inversion are AC3 and AC1.

## 2. Simultaneous elimination

### Theorem 2.1 (primitive-pair elimination) — PROVEN

If two relator conjugacy classes of \(P\) form a primitive pair, then \(P\)
is stably AC-trivial.

### Proof

Apply the stable ambient automorphism realizing \(\phi\). Independently
conjugate and invert the two primitive relators so that they are exactly
\(a\) and \(b\). The presentation is now

\[
 \langle a,b,c\mid a,b,D(a,b,c)\rangle.
\]

Use the relators \(a,b\) to eliminate every \(a^{\pm1},b^{\pm1}\) occurrence
from \(D\), then remove the two generator-relator pairs by inverse
stabilizations. This leaves

\[
 \langle c\mid c^n\rangle,
\]

where \(n\) is the exponent sum of \(c\) in \(D\).

All preceding transformations preserve the trivial presented group.
Therefore \(\langle c\mid c^n\rangle\) is the trivial group, which forces
\(|n|=1\). Equivalently, after the first two relator rows become basis rows,
the determinant-\(\pm1\) abelianization matrix forces the remaining diagonal
entry to be \(\pm1\). Invert the last relator if necessary and remove
\((c,c)\). The result is the empty presentation, stably equivalent to the
standard balanced presentation. \(\square\)

### Corollary 2.2

If any rank-three tuple produced by a proven AK(3) stable corridor contains a
primitive relator pair, AK(3) is stably AC-trivial.

## 3. Exact Whitehead criterion

Treat each relator as a cyclic word. Whitehead's length-reduction theorem for
a finite tuple of conjugacy classes states:

> If an automorphism strictly lowers the tuple's total cyclic length, a
> second-kind Whitehead automorphism lowers it.

Repeated strict descents terminate and reach the complete minimum length in
the Aut(\(F_3\))-orbit.

### Proposition 3.1 — PROVEN

Two nontrivial cyclic conjugacy classes form a primitive pair if and only if
their complete Whitehead minimum consists of two one-letter words on distinct
basis generators.

### Proof

If they are primitive, an automorphism sends them to two distinct basis
letters, so their minimum total is at most two. Nontrivial conjugacy classes
cannot have length zero, hence the minimum is exactly two.

Conversely, a total-two minimum consists of two one-letter cyclic words. If
their underlying generators are distinct, a signed permutation sends them to
two chosen basis generators, so the original pair is primitive.

The distinctness gate is necessary: two copies of the same basis conjugacy
class have total two but do not extend to a basis. \(\square\)

The descent certificate carries the composed automorphism. A negative
certificate carries the endpoint and checks all 90 nonidentity second-kind
rank-three Whitehead automorphisms, proving no strict descent remains.

## 4. Finite AK(3) candidate

Rebuild every cyclic rank-three tuple arising from the already-certified
two-stabilization bounds:

- defining words \(w_z,w_t\) of length at most two;
- braid templates of length at most six;
- one \(y^{\pm1}\);
- both \(z^{\pm1}\) and \(t^{\pm1}\);
- exact literal expansion to the AK(3) braid relator.

Quotient only relator order, rotation, and inversion, retaining generator
names. Test all three unordered relator pairs in every state.

### Primitive-pair corridor lemma — UNVERIFIED

At least one tested relator pair has Whitehead minimum two on distinct basis
generators.

A positive proves stable AC-triviality by Theorem 2.1. A negative refutes only
this finite corridor lemma. It is not a primitive-pair obstruction for all
stable representatives and says nothing about stable nontriviality.
