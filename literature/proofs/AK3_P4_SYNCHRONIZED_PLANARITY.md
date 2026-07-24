# Synchronized planarity for four-germ \(P_4\) links

Date: 2026-07-24

Status: the \(P_4\) classification and finite criterion are **PROVEN**.  The
AK(3) primitive-quotient candidate is **REFUTED** by the independently
replayed production certificate.

## 1. Scope

Retain the exact occurrence dictionary

\[
(D,A,B,\nu)
\]

from `AK3_NEUWIRTH.md` and the notation of
`AK3_SYNCHRONIZED_PLANARITY.md`.  No word is freely or cyclically reduced and
no occurrence is identified.  The \(A\)-link \(G_A\) is assumed connected
and loopless on the four germs

\[
V=\{x^+,x^-,y^+,y^-\}.
\]

The simple support considered here is the path

\[
a-b-c-d. \tag{1.1}
\]

Write

\[
P=P_{ab},\qquad M=P_{bc},\qquad Q=P_{cd}
\]

for its three nonempty parallel classes, with multiplicities

\[
p=|P|,\qquad m=|M|,\qquad q=|Q|.
\]

A Neuwirth-compatible rotation still means

\[
C_{\tau v}=B C_v^{-1}B. \tag{1.2}
\]

The only question is whether \(G_A\) has a spherical rotation satisfying
(1.2).

## 2. The path-bundle classification

### Lemma 2.1 (three block intervals)

In every spherical embedding of \(G_A\), each of \(P,M,Q\) forms one cyclic
interval at each incident vertex.

#### Proof

Consider the \(p\) parallel \(ab\)-edges.  Their complement in \(S^2\) has
\(p\) regions, each incident with one angular gap between consecutive
\(P\)-darts at \(b\).  The vertex \(c\) belongs to one such region.  Every
\(bc\)-edge has its interior in that same region: after leaving \(b\), it
cannot enter another complementary region without crossing an \(ab\)-edge.
The connected remainder through \(c-d\) lies there as well.  Thus all
non-\(P\) darts at \(b\) occupy one angular gap, and the complementary
cyclic interval is exactly the \(P\)-block.  At the leaf \(a\), all darts
already belong to \(P\).

The same argument with the \(cd\)-edges proves that \(Q\) is a block at
\(c\) and \(d\).

Now remove the \(m\) parallel \(bc\)-edges.  The component containing \(a\)
lies in one complementary region, so all \(P\)-darts at \(b\) occupy one
angular gap between consecutive \(M\)-darts.  Independently, the component
containing \(d\) lies in one complementary region, so all \(Q\)-darts at
\(c\) occupy one angular gap.  The complements of those single gaps are the
cyclic \(M\)-intervals at \(b\) and \(c\).  The two outer components may lie
in the same or in different complementary regions; the lemma does not
identify their two gaps. \(\square\)

### Lemma 2.2 (endpoint orders and the central shift)

Let

\[
L=(e_0,\ldots,e_{m-1})
\]

be the linear order of the central class \(M\) at \(b\), cut at the
\(P\)-block.  Then its linear order at \(c\), cut at the \(Q\)-block, has
the form

\[
\operatorname{shift}_s(\operatorname{rev}L)
\qquad\text{for a unique }s\in\mathbb Z/m. \tag{2.1}
\]

The cyclic orders in each outer class at its two endpoints are opposite.
After cutting the order at the adjacent block at \(b\) or \(c\), this may be
represented by an exactly reversed linear order at the leaf endpoint.

#### Proof

For any parallel class in a spherical embedding, consecutive arcs at one
endpoint occur in the opposite cyclic order at the other endpoint: the
regions between consecutive arcs are digons before other material is
inserted into their angular gaps.  Hence the endpoint cycles for \(M\) are
opposite.

Lemma 2.1 supplies a distinguished gap at \(b\), occupied by \(P\), and a
distinguished gap at \(c\), occupied by \(Q\).  Cutting two opposite cyclic
orders at independently chosen gaps produces a reverse linear order followed
by one and only one cyclic shift.  This gives (2.1).

For \(P\), the block at \(b\) supplies a linear cut while the leaf rotation
at \(a\) has no distinguished origin.  Any cyclic shift at \(a\) is the same
rotation cycle, so the opposite endpoint cycles have a representative that
is the exact linear reverse.  The argument for \(Q\) is identical.
\(\square\)

### Theorem 2.3 (complete \(P_4\)-bundle classification)

A rotation system of \(G_A\) is spherical if and only if:

1. the three parallel classes are blocks as in Lemma 2.1;
2. the outer endpoint orders are reversed as in Lemma 2.2; and
3. for exactly one \(s\in\mathbb Z/m\), the central endpoint orders satisfy
   (2.1).

There is no further macro-rotation choice.  The number of labeled spherical
rotation systems is

\[
p!\,m!\,m\,q!. \tag{2.2}
\]

#### Proof

Necessity is Lemmas 2.1 and 2.2.  After each bundle is contracted, the simple
support is a path.  Every support vertex has degree at most two, so its cyclic
neighbor order is unique.

For sufficiency, embed the central \(bc\)-dipole on \(S^2\) with opposite
endpoint cycles.  Select the gap at \(b\) prescribed by the cut before
\(L\), and embed the \(ab\)-dipole in a small closed disc meeting the central
embedding only at \(b\).  Select at \(c\) the gap encoded by \(s\), and embed
the \(cd\)-dipole in another such disc.  If both selected gaps border the
same central complementary region, choose the two outer discs disjoint
inside that region.  Otherwise choose them in their respective regions.
The reversed outer endpoint orders give planar dipoles.  This realizes the
specified rotation on the sphere.

At \(b\), the two block boundaries linearize both \(P\) and \(M\), giving
\(p!\) and \(m!\) choices.  The leaf rotation at \(a\) is then forced as a
cycle.  At \(c\), the relative central gap has \(m\) choices and the
linearized \(Q\)-block has \(q!\) choices; the leaf rotation at \(d\) is
forced.  These data are uniquely read from the rotation system, proving
(2.2). \(\square\)

The factor \(m\) is load-bearing.  Fixing one exact reversal of the central
linear orders would silently discard embeddings in which the two outer
path components occupy different central gaps.

## 3. Exact slot schemes

Orient the path as in (1.1).  Give the labeled edges in each parallel class
all-different ranks:

\[
z_e\in\{0,\ldots,|P_{uv}|-1\}.
\]

For every central shift \(s\in\mathbb Z/m\), define one slot scheme
\(Q_s\):

- at \(b\), expand the rotation as \(P,M\);
- at \(c\), expand it as
  \(\operatorname{shift}_s(\operatorname{rev}M),Q\);
- at \(a\) and \(d\), use the reversed endpoint rank order of their outer
  class.

Each incident-class slot map is injective, and its images partition all
slots at its vertex.  The outer maps and the central map at \(b\) are signed
affine maps.  At \(c\), the central map is

\[
z\longmapsto (m-1-z+s)\bmod m, \tag{3.1}
\]

inside its \(m\)-slot block.

Use these slot maps in equation (4.3) of
`AK3_SYNCHRONIZED_PLANARITY.md`.  The proof of its Theorem 4.3 requires only
injective inverse slot lookup, complete phase enumeration, propagation around
every component of the \(A\)-contracted \(B\)-constraint graph, and global
all-different rank checks.  It therefore applies verbatim after additionally
enumerating all \(m\) schemes \(Q_s\).

### Corollary 3.1 (finite compatible-sphericity criterion)

For connected loopless four-germ support \(P_4\), a Neuwirth-compatible
spherical rotation exists if and only if one of the \(m\) central-shift
schemes admits phases and all-different ranks satisfying all equations
(4.3).

Before returning NO, an implementation must exhaust:

1. all \(m\) central shifts;
2. all phase pairs in
   \(\mathbb Z/n_{x^+}\times\mathbb Z/n_{y^+}\);
3. every seed rank for every constraint component; and
4. every retained component-solution combination.

Every positive must reconstruct the four rotations, replay (1.2), verify the
rank partitions, and independently obtain Euler characteristic two.

## 4. AK(3) primitive-quotient application

The verified primitive-single certificate contains 303 distinct exact
rank-two quotient presentations.  The existing \(K_4\), \(K_4-e\), and
\(C_4\) criterion decides 264 of them negatively.  The other 39 all have
connected loopless simple support \(P_4\).

The chained certificate
`results/stable_ac/theory/ak3_primitive_quotient_thickenability.json`
recomputes all 303 decisions.  It finds

\[
82\ K_4,\qquad 138\ (K_4-e),\qquad 44\ C_4,\qquad 39\ P_4,
\]

and no compatible spherical rotation in any case.  Its ordered decision
trace is

```text
d5c257eb0c2974a0eeb7d4c91b63fc54e4c113e32ae175fd8651070457cf1186
```

The verifier recursively replays the primitive-single source certificate,
rederives all exact quotients, reruns all finite rank decisions, repeats the
476-pair factorial calibration, and requires complete payload equality.

Each quotient comes with a verified stable path from AK(3): a certified
rank-three corridor, a certified primitive-relator straightening, and a
certified removal.  Consequently:

> If any one of the 303 exact quotients is thickenable, then Lackenby's
> Theorem 1.3 makes that quotient classically AC-trivial, and AK(3) is
> stably AC-trivial.

This implication uses no claim that thickenability is invariant under an
ambient free-group automorphism or under Andrews--Curtis moves.  It tests the
exact quotient complexes themselves.

This complete null refutes only the finite primitive-quotient
thickenability attempt.  It does not obstruct a thickenable rank-three
state, another stable representative, or AK(3) itself.

## 5. Proof-audit status

A hostile review independently found the central-gap issue before seeing the
implemented repair.  It produced two explicit failures of a naive
zero-shift-only rule:

\[
\langle x,y\mid \mathtt{xY},\mathtt{yy}\rangle
\]

has middle multiplicity two and compatible spherical rotations only in the
omitted relative shift, while

\[
\langle x,y\mid \mathtt{xxx},\mathtt{xxy}\rangle
\]

gives a length-three-only example with middle multiplicity four.  These
examples support rather than refute Theorem 2.3 because it retains every
shift in \(\mathbb Z/m\).

The dependency-free rank implementation was then exhaustively compared with
the independent factorial Neuwirth permutation census on all 476 canonical
cyclically reduced \(P_4\) word-pairs of total length at most seven.  The two
methods agreed on all 444 spherical and all 32 non-spherical cases, and
accepted witnesses exercised nonzero central shifts.  This verifies the
slot-map convention, the shift sign, the phase/rank propagation, and both
positive and negative branches on a complete finite calibration family.
