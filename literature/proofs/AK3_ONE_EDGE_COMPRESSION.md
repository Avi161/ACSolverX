# One-edge second-stage compression for AK(3)

Date: 2026-07-24

Status: the stable-compression theorem and cyclic seam lemma are **PROVEN**.
The bounded AK(3) candidate in Section 6 is **UNVERIFIED** until its exact
certificate is built and independently replayed.

## 1. Setup

The immediate two-stabilization theorem in
`AK3_TWO_STABILIZATION.md` starts with a balanced presentation on \(x,y\),
adjoins \(z,t\), compresses one source relator to a template containing one
\(y^{\pm1}\), and removes \(y\). It produces a rank-three tuple

\[
 {\cal R}=(A_0,A_1,A_2)\subset F(x,z,t)
\]

stably AC-equivalent to the source presentation.

Write

\[
 \nu_x(W)=\#\{k:W_k\in\{x,x^{-1}\}\}.
\]

For a freely reduced word \(W\), let \(\operatorname{cyc}(W)\) be its cyclic
reduction. A rotation means a cyclic permutation of a cyclically reduced
word. In string notation, uppercase letters denote inverses.

## 2. The finite cyclic one-edge move

Choose distinct indices \(i,j\), a sign
\(\delta\in\{+1,-1\}\), a rotation \(U\) of \(A_i\), and a rotation \(V\) of
\(A_j^\delta\). Replace the target relator by

\[
 A_i'=\operatorname{cyc}(UV)
\]

and leave the other two relator conjugacy classes unchanged.

This is the Definition-2.1 cyclic multiplication move used by the repository.
Indeed, rotations are conjugates of their relators. Conjugate \(A_i\) to
\(U\), conjugate \(A_j^\delta\) to \(V\), multiply the target by the other
relator, restore the non-target relator to its original cyclic
representative, and cyclically reduce the target by conjugation. Relator
inversion, conjugation, and multiplication are AC1--AC3 operations.

There is no need for a separate sign on the target. If the target is inverted
before multiplication, then

\[
 (U^{-1}V)^{-1}=V^{-1}U,
\]

whose cyclic word is the same as \(UV^{-1}\). That case already occurs by
changing \(\delta\).

### Scope warning

This finite move does **not** exhaust multiplying arbitrarily conjugated
relators. Modulo a global conjugation, arbitrary representatives can produce

\[
 UcVc^{-1}
\]

with an unrestricted relative conjugator \(c\). The theorem below is complete
for products of signed cyclic rotations, which is exactly the finite move
class being certified. It makes no claim about all \(c\).

## 3. Cyclic seam completeness

The finite census need only enumerate rotations satisfying

\[
 \operatorname{last}(U)
   =\operatorname{first}(V)^{-1}.
\tag{3.1}
\]

The following lemma proves that this does not lose a newly created isolator
inside the cyclic-rotation move class.

### Lemma 3.1 (cancelling-seam normal form) — PROVEN

Let \(P,Q\) be nonempty cyclically reduced words. Suppose

\[
 \nu_x(P)\ne1,\qquad \nu_x(Q)\ne1,
\]

and for some rotations \(U\) of \(P\) and \(V\) of \(Q\),

\[
 \nu_x(\operatorname{cyc}(UV))=1.
\]

Then there are rotations \(U'\) of \(P\) and \(V'\) of \(Q\) such that

\[
 \operatorname{cyc}(U'V')=\operatorname{cyc}(UV)
\]

as cyclic words and the displayed seam of \(U'V'\) satisfies (3.1).

### Proof

Neither factor can have zero \(x^{\pm1}\)-occurrences. If, say,
\(\nu_x(P)=0\), every \(x^{\pm1}\) in the concatenation belongs to \(Q\).
Because \(Q\) is cyclically reduced, cancelling across either factor seam
cannot cancel an \(x\)-letter of \(Q\) against a letter of \(P\). Thus its
\(x\)-count cannot change to one. Consequently

\[
 \nu_x(P)\ge2,\qquad \nu_x(Q)\ge2.
\]

The unreduced product therefore has at least four \(x^{\pm1}\)-occurrences,
whereas its cyclic reduction has one. At least one inverse pair cancels.
There are no cancellable adjacent pairs internal to \(U\) or \(V\), because
both factors are cyclically reduced. Hence the first cancellation occurs at
one of the two factor seams in the cyclic word \(UV\).

If it occurs at the displayed seam between \(U\) and \(V\), (3.1) already
holds.

Otherwise the first cancellation occurs at the wrap seam between the last
letter of \(V\) and the first letter of \(U\). Write

\[
 U=aU_1,\qquad V=V_1a^{-1}.
\]

Rotate the factors in the target-first order:

\[
 U'=U_1a,\qquad V'=a^{-1}V_1.
\]

Their displayed seam contains \(aa^{-1}\), and

\[
 \operatorname{cyc}(U'V')
 =\operatorname{cyc}(U_1aa^{-1}V_1)
 =\operatorname{cyc}(U_1V_1).
\]

On the other hand,

\[
 \operatorname{cyc}(UV)
 =\operatorname{cyc}(aU_1V_1a^{-1})
 =\operatorname{cyc}(U_1V_1).
\]

Thus the rotations with a displayed cancelling seam yield the same cyclic
target relator.

This argument also covers cancellation cascades. It uses only the first
cross-factor cancellation. After moving a wrap cancellation to the displayed
seam, all remaining free and cyclic cancellations act on a conjugate of the
same word and therefore produce the same reduced cyclic word. \(\square\)

### Corollary 3.2

For a rank-three tuple with no relator satisfying \(\nu_x=1\), every signed
cyclic one-edge move that creates a relator with \(\nu_x=1\) has a witness
enumerated by the cancelling-seam rule (3.1).

The corollary permits duplicate witnesses. It asserts completeness of the
resulting cyclic target relators, not uniqueness of their cuts.

## 4. One-edge stable-compression theorem

### Theorem 4.1 — PROVEN

Let \({\cal R}=(A_0,A_1,A_2)\subset F(x,z,t)\) be obtained from a balanced
rank-two presentation \(P\) by the first stage of the proven triangular
two-stabilization theorem. Apply one finite cyclic move from Section 2,
obtaining

\[
 {\cal R}'=(A_0',A_1',A_2').
\]

Suppose some \(A_k'\) contains exactly one \(x^{\pm1}\). Rotate it to

\[
 x^\epsilon q(z,t)
\]

and define

\[
 e_x=
 \begin{cases}
 q^{-1},&\epsilon=+1,\\
 q,&\epsilon=-1.
 \end{cases}
\]

Delete \(A_k'\), substitute \(x=e_x\) in the other two relators, and relabel
\(z,t\) as a rank-two basis. If the resulting pair is \((B_0,B_1)\), then

\[
 P\sim_{\mathrm{st}}\langle z,t\mid B_0,B_1\rangle.
\]

### Proof

The first two stabilizations, template compression, and removal of \(y\) are
stable-AC composites by the prior theorem. The single cyclic multiplication
is an AC1--AC3 composite by Section 2. The relator \(A_k'\) is an
\(x\)-isolator, so the substitution-and-removal lemma deletes \(x\) and
substitutes \(e_x\) in the two survivors. Finally, a signed relabeling of the
surviving basis is a stable ambient automorphism. Composing the chains proves
the claim. \(\square\)

### Corollary 4.2 (finite seam decision)

If the source rank-three tuple has no immediate \(x\)-isolator, it is enough
to test the cancelling-seam moves of Lemma 3.1. Every accepted output is
stably AC-equivalent to the original rank-two presentation.

## 5. Canonical source quotient

The finite AK(3) decision cyclically reduces every relator after the first
removal and quotients rank-three tuples only by:

1. relator order;
2. cyclic rotation of each relator;
3. inversion of each relator.

These are AC1--AC3 symmetries. The quotient does not rename \(x,z,t\), because
\(x\) is the distinguished generator removed in the second stage. It also
does not quotient by arbitrary automorphisms of \(F(x,z,t)\).

Canonicalizing before the one-edge census is complete: every finite cyclic
move from any representative transports to a signed cyclic move from its
canonical representative, with possibly permuted target/other indices and
different rotation offsets.

## 6. Bounded AK(3) candidate

Start with

\[
 \mathrm{AK}(3)
 =\langle x,y\mid x^3y^{-4},\;xyxy^{-1}x^{-1}y^{-1}\rangle.
\]

Use exactly the previously certified first-stage bounds:

- nonempty freely reduced defining words \(w_z,w_t\in F(x,y)\), each of
  length at most two;
- a freely and cyclically reduced braid template of length two through six;
- exactly one \(y^{\pm1}\) in the template;
- at least one occurrence of each of \(z^{\pm1},t^{\pm1}\);
- literal expansion equal to an orientation of the braid relator.

Remove \(y\), canonicalize the resulting rank-three tuple as in Section 5,
and discard tuples already containing one \(x^{\pm1}\), since the immediate
certificate decides those. Exhaust every cancelling-seam move from
Corollary 3.2, remove \(x\) whenever possible, and compute the complete
rank-two Whitehead floor.

### One-edge floor-12 lemma — UNVERIFIED

Within these bounds, some one-edge output has Aut-floor at most 12.

A floor at most 12 would enter the class covered by the repository's
classical length theorem, but a complete stable proof would still need to
expand the exact corridor and replay the classical endpoint certificate.

A minimum of 13 would refute only this bounded lemma. It would not decide:

- longer defining words or templates;
- two or more second-stage multiplications;
- moves with an unrestricted relative conjugator;
- nontriangular generator dependencies;
- stable AC-triviality or nontriviality of AK(3).

## 7. Certificate obligations

An exact certificate for Section 6 must:

1. regenerate every accepted first-stage source identity;
2. reproduce the cyclic rank-three quotient without ambient automorphisms;
3. replay one witness for every raw rank-two output, including both rotation
   offsets and the signed other relator;
4. recheck the one-\(x\) gate and substitution-and-removal result;
5. verify every complete Whitehead witness independently;
6. rerun the full seam census and compare its trace, counts, output
   partition, floor distribution, minimum, and verdict.

No bounded null from this certificate is an AC invariant or a counterexample.
