# AK(3) quotient one-\(D\) catalyst design

Date: 2026-07-25

## Objective

Classify the one-\(z\) targets obtainable from exactly one cross
multiplication between the \(B\)- and \(D\)-slots when arbitrary fixed-\(R\)
gauge moves may occur before and after it:

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1}.
\]

The deliverable is an unbounded mechanism theorem. It must not claim that
AK(3) is trivial.

## Rejected shortcut

After quotienting by \(R\), the ambient group is

\[
H=
\langle x,t\mid x^3=t^4\rangle*\langle z\rangle
=G*\langle z\rangle .
\]

It is false that intersecting axes of two hyperbolic elements in the
Bass--Serre tree always reduce to literal signed cyclic rotations. Axes may
meet only at a vertex, whose stabilizer is a conjugate of \(G\) or
\(\langle z\rangle\). The residual product has the form

\[
U h V h^{-1},
\qquad
h\in G\ \text{or}\ h\in\langle z\rangle .
\]

Any proof omitting this vertex twist is incomplete.

## Correct classification

Use the Bass--Serre tree to split arbitrary relative conjugators into:

1. disjoint axes, where translation length is \(2+4+2d\ge8\), while a
   one-\(z\) shadow has length \(2\) because its weight is \(6\) or \(8\);
2. a shared edge, corresponding to \(h=1\); and
3. a shared vertex, leaving \(h\) in one of the two vertex factors.

For the last two cases, enumerate the two syllable rotations of \(B\), the
four rotations of \(D\), and the four rotations of \(D^{-1}\).

For a \(G\)-vertex twist, free-product reduction forces a unique \(h\) in
each of the sixteen signed rotation cells. The exact \(2\times4\) tables
must be displayed and replayed. For a \(\langle z\rangle\)-vertex twist
\(h=z^k\), the exponent equations have four solutions for each sign; these
must also be displayed and replayed.

Every one-\(z\) result must reduce to one of

\[
\operatorname{cyc}(z^{-1}t^{-1}xtx),
\qquad
\operatorname{cyc}(z^{-1}txtx^{-1}).
\]

## Endpoint argument

The tails

\[
e_+=t^{-1}xtx,\qquad
e_-=txtx^{-1}
\]

are nontrivial in \(G\), with torus-knot weights \(8\) and \(6\). Hence
\(z^{-1}e_\pm\) are cyclically reduced free-product words of syllable
length two.

Normalize a final actual one-\(z\) target by inversion and cyclic
conjugation to \(z^{-1}e\). The free-product conjugacy theorem then makes
its quotient shadow exactly \(z^{-1}e_+\) or \(z^{-1}e_-\), not merely an
unspecified conjugate.

All fixed-\(R\) gauge moves vanish in \(H\), including factors conjugated by
words containing \(z\). Evaluation at \(z=e\), followed by the proved
fixed-relator normal-closure lemma, makes the eliminated endpoint
classically AC-equivalent to the corresponding standard one-\(D\)
endpoint, hence to AK(3).

## Verification

The dependency-free replay will:

- implement exact normal form in \(G*\langle z\rangle\);
- pin the four literal signed-rotation witnesses;
- pin all sixteen unique \(G\)-vertex twists;
- pin the four \(\langle z\rangle\)-vertex solutions per sign; and
- verify sample pre-catalyst fixed-\(R\) gauges on both slots.

The replay is a certificate for the finite residue. Unbounded completeness
comes from the Bass--Serre trichotomy and the uniqueness equations in the
tables.

## Scope

The theorem covers exactly one \(B/D\) cross multiplication, arbitrary
fixed-\(R\) gauge moves before and after it, arbitrary conjugators, either
target role, a restored source shadow, and elimination of that cross target
as the final generator isolator.

It does not cover:

- eliminating the restored source instead of the cross target;
- a second \(B/D\) cross multiplication;
- a changed normal closure for \(R\);
- a final primitive eliminator with several \(z^{\pm1}\)-occurrences;
- another stabilization; or
- dual-source primitive-pair compression.
