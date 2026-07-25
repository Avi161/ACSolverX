# The one-\(D\) catalyst is an unbounded AK(3) self-loop

Date: 2026-07-24

Status: **PROVEN** for one multiplication of the future eliminator by an
arbitrarily conjugated defining relator.  There is no conjugator-length
bound and no AC graph search.  This closes one catalyst mechanism; it does
not trivialize AK(3).

## 1. The rank-three root

The proved one-source compression corridor reaches the rank-three tuple

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1}
\end{aligned}
\tag{1.1}
\]

over \(F(x,t,z)\).  In string notation,

```text
R = xxxTTTT
B = Zxt
D = TzxZ
```

The tuple presents the trivial group and is stably AC-equivalent to AK(3).
The relator \(B\) is the future \(z\)-eliminator.

The arbitrary-recovery theorem closes every modification of \(B\) using
only consequences of \(R\).  The first different catalyst is one
multiplication targeting \(B\) by an arbitrary conjugate of \(D^{\pm1}\).

## 2. Statement

Choose arbitrary representatives of the conjugacy classes of \(B\) and
\(D^{\pm1}\), multiply them with \(B\) as target, and freely and cyclically
reduce the result.  Allow inversion of the target before or after the
move.

### Theorem 2.1

If the resulting cyclic word contains exactly one occurrence of
\(z^{\pm1}\), then it has one of exactly two cyclic conjugacy classes:

```text
ZTxtx
ZtxtX
```

Solving either relator for \(z\), applying the substitution-and-removal
stable composite, and keeping \(R,D\) as the two survivors produces a
rank-two presentation classically AC-equivalent to AK(3).

Thus no one-\(D\), arbitrary-relative-conjugator multiplication targeting
\(B\) escapes the classical AK(3) class through a generator isolator.

## 3. The arbitrary conjugator reduces to axis intersection

For a cyclic word \(W\), let

\[
\nu_z(W)
=
\#\{\text{occurrences of }z^{\pm1}\text{ in }W\}.
\]

We use the following standard tree normal form.

### Lemma 3.1: bridge normal form

Let \(P,Q\) be nontrivial cyclically reduced words in a free group.  Take
an arbitrary product of a conjugate of \(P\) and a conjugate of \(Q\).
After a global conjugation, its cyclic conjugacy class has one of the
following forms.

1. If the axes of the two conjugates intersect, it is the cyclic reduction
   of
   \[
   UV,
   \tag{3.1}
   \]
   where \(U,V\) are cyclic rotations of \(P,Q\).
2. If the axes are disjoint, it has the cyclically reduced geodesic spelling
   \[
   UcVc^{-1},
   \tag{3.2}
   \]
   where \(c\ne1\) labels the shortest bridge between the axes and
   \(U,V\) are rotations based at the bridge endpoints.

#### Proof

Work in the Cayley tree.  Global conjugation moves the chosen base vertex
without changing the cyclic word.  If the axes meet, put the base vertex
in their intersection.  One translation segment on the first axis followed
by one on the second is labelled by rotations \(U,V\); cyclic reduction
gives (3.1).

If the axes are disjoint, choose the initial vertex at the endpoint of
their unique shortest bridge on the first axis.  The geodesic representative
traverses one fundamental segment on the first axis, the bridge, one
fundamental segment on the second axis, and the bridge in reverse.  Shortest
bridge endpoints prevent cancellation at all four junctions.  The first and
last directions also differ, so there is no cyclic cancellation.  This is
(3.2). \(\square\)

The word \(c\) in Lemma 3.1 is the normalized shortest axis bridge, not the
original written conjugator.  Arbitrarily long written conjugators may
shorten to the same bridge.

Apply the lemma to \(P=B\) and \(Q=D^{\pm1}\).  Rotations and inversion
preserve incidence, and

\[
\nu_z(B)=1,\qquad \nu_z(D^{\pm1})=2.
\tag{3.3}
\]

In the disjoint-axis case, (3.2) is cyclically reduced, so

\[
\nu_z(UcVc^{-1})
=1+2+2\nu_z(c)
\ge3.
\tag{3.4}
\]

It cannot be a one-\(z\) isolator.  Therefore every isolator in Theorem 2.1
comes from the intersecting-axis case (3.1).  The unrestricted conjugator
has disappeared, leaving a finite signed rotation calculation.

## 4. Target orientation and the 24-case residue

It is enough to keep \(B\) positively oriented.  If the target is inverted,
then, up to inversion and cyclic reordering of the output,

\[
(U^{-1}V)^{-1}=V^{-1}U
\]

is the same cyclic word as the case \(UV^{-1}\).  Left-versus-right factor
order is likewise cyclic reordering.  Thus target orientation and order
are already covered by the sign of \(D\).

There are three rotations of \(B\), four rotations of \(D\), and four
rotations of \(D^{-1}\), for

\[
3(4+4)=24
\tag{4.1}
\]

signed rotation products.  Exact free and cyclic reduction leaves four raw
isolator witnesses in two cyclic classes:

| sign | rotation of \(B\) | rotation of \(D^{\pm1}\) | reduced product | isolator rotation |
|---:|---|---|---|---|
| \(+1\) | `Zxt` | `xZTz` | `xtxZT` | `ZTxtx` |
| \(+1\) | `xtZ` | `zxZT` | `xtxZT` | `ZTxtx` |
| \(-1\) | `Zxt` | `XZtz` | `xtXZt` | `ZtxtX` |
| \(-1\) | `xtZ` | `zXZt` | `xtXZt` | `ZtxtX` |

The other twenty products do not have
\(\nu_z=1\).  This proves the classification part of Theorem 2.1.

## 5. Both eliminations return to AK(3)

Put

\[
B_0=xtxt^{-1}x^{-1}t^{-1},
\tag{5.1}
\]

the AK(3) braid relator.

The first isolator equation is

\[
z^{-1}t^{-1}xtx=1,
\]

so

\[
z=t^{-1}xtx.
\tag{5.2}
\]

Substitution in the surviving defining relator gives

```text
TzxZ  ->  TTxtxTXt  ->cyc  TxtxTX.
```

The cyclic reduction is the conjugate

\[
t^{-1}B_0t.
\tag{5.3}
\]

The second isolator equation is

\[
z^{-1}txtx^{-1}=1,
\]

so

\[
z=txtx^{-1}.
\tag{5.4}
\]

This time substitution gives the exact free reduction

```text
TzxZ  ->  xtxTXT,
```

which is \(B_0\) itself.

The other survivor is unchanged in both cases:

\[
R=x^3t^{-4}.
\]

Because the rank-three tuple presents the trivial group, removing the
one-\(z\) relator and substituting (5.2) or (5.4) is the proved
substitution-and-removal stable composite, not a bare AC5 move.  The two
rank-two endpoints are

\[
(R,t^{-1}B_0t)
\quad\text{and}\quad
(R,B_0).
\]

They differ from AK(3) by at most one classical relator conjugation.  This
also makes their complete Aut(\(F_2\))-floor exactly the certified AK(3)
floor \(13\), never at most \(12\).  This completes the proof of
Theorem 2.1.

## 6. Scope

The bridge argument quantifies over every relative conjugator.  The finite
24-case table is the complete residue after that unbounded reduction, not a
bounded-conjugator experiment.

The theorem covers exactly one multiplication targeting \(B\) with
\(D^{\pm1}\) as source.  It does not cover:

- two or more \(D\)-multiplications targeting the eliminator;
- a multiplication targeting \(D\) rather than \(B\);
- the \(R\)-source recovery moves treated by the separate arbitrary-recovery
  theorem;
- a move which first changes \(R\) or the recovery equation;
- a primitive eliminator containing several \(z\)-letters;
- dual-source compression before either old generator is removed; or
- another stabilization architecture.

No failed search or obstruction claim is made.  AK(3) remains open.
