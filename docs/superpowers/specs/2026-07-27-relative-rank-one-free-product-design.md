# Relative rank-one free-product design

Date: 2026-07-27

## Objective

Remove the conditional hypothesis from Result 58 as far as normal-form
theory permits.  For a free product

\[
P=A*C
\]

and \(u\in P\), decide exactly when the natural homomorphism

\[
\Phi_u:A*\langle s\rangle\longrightarrow P,
\qquad
\Phi_u|_A=\operatorname{id}_A,\quad \Phi_u(s)=u
\]

is injective.  Then apply the answer to

\[
B=BS(3,4),\qquad G=B*\langle z\rangle,\qquad
u=z^{-1}gz.
\]

The target is a theorem, not a bounded normal-form census.

## Corrected theorem

Write the reduced normal form of \(u\notin A\) as

\[
u=a_0wa_1,
\]

where \(a_0,a_1\in A\) are the optional endpoint syllables and \(w\)
begins and ends in \(C\).  Then the exact criterion is

\[
\boxed{\Phi_u\text{ is injective}
\iff w\text{ has infinite order}.}
\]

If \(u\in A\), the core is empty and \(\Phi_u\) is not injective.
Necessity for a nonempty core is immediate after the endpoint Nielsen
transformation: if \(w\) has finite order \(n\), then \(s^n\) is a
nontrivial kernel word for the transformed map.

Infinite order of \(u\) itself is not sufficient.  In

\[
C_2*C_2=\langle a,c\mid a^2=c^2=1\rangle,
\qquad A=\langle a\rangle,
\]

the element \(u=ac\) has infinite order, but \(aua=u^{-1}\).  Its
\(A\)-trimmed core is the order-two element \(c\), exactly as the
criterion predicts.

## Normal-form proof

The relative Nielsen map

\[
s\longmapsto a_0sa_1
\]

is an automorphism of \(A*\langle s\rangle\), so it is enough to prove
injectivity for \(s\mapsto w\).

The load-bearing lemma is:

> If an infinite-order reduced word begins and ends in the same free
> factor, then every nonzero power has a reduced normal form beginning
> and ending in that same factor.

Prove the lemma simultaneously for both factors by induction on
syllable length.  If the last and first syllables do not cancel, powers
concatenate with only a nonzero same-factor merge.  If they cancel,
write \(w=c\,r\,c^{-1}\); the shorter infinite-order word \(r\) begins
and ends in the other factor, so induction applies.

Now take a nontrivial reduced word in \(A*\langle s\rangle\).  Its
nonzero \(s\)-powers map to words beginning and ending in \(C\), while
its internal \(A\)-syllables are nontrivial.  Every seam is therefore
of type \(C|A|C\), so the image is reduced and nontrivial.

## AK(3) application

The HNN extension

\[
BS(3,4)=\langle x,y\mid yx^3y^{-1}=x^4\rangle
\]

is torsion-free: a finite subgroup acting on its Bass--Serre tree fixes
a vertex, whose stabilizer is a conjugate of the torsion-free base
\(\langle x\rangle\).  The free product
\(G=B*\langle z\rangle\) is therefore torsion-free by the same tree
argument.

Consequently, for the element \(u=z^{-1}gz\) in Result 58,

\[
\Phi_u\text{ is injective}\iff u\notin B.
\]

Indeed, \(u\notin B\) has a nonempty trimmed core, and every nonempty
element of the torsion-free group \(G\) has infinite order.  Notice
that this specialization uses torsion-freeness of the whole free
product, not merely infinite order of the untrimmed \(u\).

Result 58 then obstructs every \(g\notin zBz^{-1}\).  The exact
remaining A--D cases are the internal elements

\[
g=zbz^{-1}
\]

with \(e_y(b)=1\) in the two \(h\)-fibers and \(e_y(b)=0\) in the
negative identity fiber.

## Independent replay

A dependency-free syllable reducer will replay:

- free-product reduction and powers;
- trimming of the two \(A\)-end syllables;
- the two induction branches of the power lemma;
- noncancellation of representative alternating relative words;
- the finite-core, infinite-untrimmed \(C_2*C_2\) counterexample; and
- the internal-element kernel counterexample.

The executable replay is not evidence for the universal theorem.  The
proof is the induction above; tests protect the displayed reductions
and prevent accidental omission of the torsion exception.

## Boundary

This result removes all noninternal elements from Result 58's
unresolved residue.  It does not handle \(u\in B\), and it does not
prove AK(3), AC, or stable AC.
