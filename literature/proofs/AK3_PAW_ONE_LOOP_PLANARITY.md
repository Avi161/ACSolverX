# Paw-core one-loop synchronized planarity for two-hop AK(3) images

Date: 2026-07-24

Status: the paw-core rotation and signed-rank reduction theorems are
**PROVEN**.  The finite two-hop AK(3) CoV thickenability candidate is
**REFUTED** by the exact certificate in Section 7.

## 1. Exact scope

Let \(G_0\) be a positive parallel expansion of the paw graph: a triangle
on \(a,b,c\), together with a pendant edge \(ad\).  Write

\[
m_{ab},m_{ac},m_{bc},m_{ad}>0
\]

for the four parallel-class multiplicities and put

\[
p=m_{ab}+m_{ac}=\deg_{G_0}(a)-m_{ad}.
\]

Let \(G\) be obtained from \(G_0\) by adding exactly one loop edge \(\ell\)
at a vertex \(v\ne a\).  Thus \(v\) is not the articulation vertex and
\(G_0-v\) is connected.

The occurrence dictionary and \(B\)-reversal convention are exactly those
of `AK3_SYNCHRONIZED_PLANARITY.md`.  Exact supplied words are not reduced.

## 2. The cut-vertex block lemma

### Lemma 2.1

Let a connected graph be embedded in \(S^2\), and suppose \(G-a\) has
exactly two connected components \(Q_1,Q_2\).  For each \(Q_i\), all darts
at \(a\) whose other endpoint lies in \(Q_i\) form one cyclic interval.

#### Proof

If one component's darts do not form one interval, then, because there are
exactly two components, the cyclic order contains four alternating darts
from \(Q_1,Q_2,Q_1,Q_2\).  In \(Q_1\), join the corresponding other
endpoints by a path avoiding \(a\); together with the two incident edge arcs
this contains a Jordan curve through \(a\).  The alternating \(Q_2\)-darts
leave \(a\) into opposite sides of that curve.  A path between their other
endpoints inside \(Q_2\) avoids \(a\), so it must cross the first curve,
contradicting the embedding.  Hence both dart sets are cyclic intervals.
\(\square\)

For the paw, \(G_0-a\) has exactly two components: the connected
\(bc\)-component and the pendant vertex \(d\).  Thus the complete triangle
part and the \(ad\)-dipole part are complementary cyclic intervals at \(a\).

## 3. Spherical rotations of a parallel paw

### Lemma 3.1 (parallel triangle)

In every spherical rotation of a positive parallel expansion of \(K_3\),
each parallel class is one cyclic block and the two endpoint linear orders
are reversed.  Conversely, every three independent labeled linear class
orders with reversed opposite orders is spherical.  The exact number of
labeled spherical rotations is

\[
m_{ab}!\,m_{ac}!\,m_{bc}!. \tag{3.1}
\]

#### Proof

For a class \(P_{uw}\), the third triangle vertex lies in one complementary
region of the \(uw\)-dipole.  Every non-\(uw\) triangle edge lies in that
same region, forcing one class block and reversed endpoint orders.  Deleting
all but one representative per class leaves the simple triangle, whose
degree-two cyclic rotations are unique.  Conversely, expand the three
edges of a planar triangle into narrow parallel ribbons.  The three labeled
linear orders are independent, proving (3.1). \(\square\)

### Theorem 3.2 (parallel paw classification)

Fix the triangle slot order at \(a\).  Every spherical rotation of \(G_0\)
is obtained uniquely by:

1. choosing the three labeled linear orders from Lemma 3.1;
2. choosing a labeled linear order of the \(m_{ad}\) pendant edges, reversed
   at \(d\); and
3. inserting the pendant block into one of the \(p\) cyclic gaps of the
   triangle rotation at \(a\).

Consequently,

\[
N(G_0)=
p\,
m_{ab}!\,m_{ac}!\,m_{bc}!\,m_{ad}!. \tag{3.2}
\]

#### Proof

Lemma 2.1 makes the triangle and pendant darts complementary intervals at
\(a\).  Deleting the pendant block gives exactly a spherical parallel
triangle rotation, classified by Lemma 3.1.  The pendant edges form a
dipole, so their endpoint orders are reversed.  The deleted interval has a
unique insertion gap among the \(p\) triangle darts, and its labeled linear
order is uniquely recoverable.

Conversely, embed the parallel triangle in \(S^2\).  Draw the ordered
pendant dipole in a small disc placed in the chosen angular gap at \(a\).
Its interior is disjoint from the triangle.  This constructs every datum
above and proves (3.2). \(\square\)

The chosen gap may lie inside a triangle parallel class.  In the full paw
rotation that class can therefore appear on both linear sides of the
pendant interval, although it is still one cyclic block after the pendant
block is deleted.  A solver that permits insertion only between neighbor
classes is incomplete.

## 4. Adding the loop

Since \(v\ne a\), the graph \(G_0-v\) is connected.  The Jordan-loop proof
of Theorem 2.1 in `AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md` applies verbatim:
in every spherical rotation, the two loop darts are consecutive, and
deleting them gives a spherical rotation of \(G_0\).

If \(q=\deg_{G_0}(v)\), every spherical rotation of \(G\) is obtained
uniquely from a Theorem 3.2 rotation by choosing one of the \(q\) gaps at
\(v\) and one of the two loop-dart orders.  Therefore

\[
N(G)=
2pq\,
m_{ab}!\,m_{ac}!\,m_{bc}!\,m_{ad}!. \tag{4.1}
\]

## 5. Exact slot and rank criterion

Use all-different ranks in the four nonloop parallel classes and fixed rank
zero on the one-edge loop class.

At the articulation \(a\), first assign the parallel-triangle slots, insert
the pendant class into every gap \(g\in\{0,\ldots,p-1\}\), and shift the
following triangle slots by \(m_{ad}\).  At \(d\), use the reversed pendant
order.  Then at the loop vertex \(v\), insert the two loop darts into every
one of the \(q\) core gaps and in both orders.

These images partition every germ rotation.  The two cyclic phases and
constraint-component propagation from
`AK3_SYNCHRONIZED_PLANARITY.md`, Theorem 4.3, therefore apply unchanged.

### Theorem 5.1

An exact paw-core one-loop link in the scope of Section 1 has a compatible
spherical rotation if and only if some paw gap, loop gap, loop orientation,
phase pair, component-seed assignment, and global rank partition satisfy
all modular \(B\)-reversal equations.

#### Proof

Theorems 3.2 and 4.1 give a complete and nonredundant parameterization of
the underlying spherical rotations.  The slot construction encodes every
labeled order in that parameterization.  The phase lemma is equivalent to
the two \(B\)-reversed generator-pipe rotations, while component propagation
and the global rank partitions are exactly the remaining modular and
all-different constraints. \(\square\)

## 6. Fail-closed obligations

A negative decision must verify:

1. exactly one loop edge;
2. a positive parallel paw core;
3. loop attachment away from the articulation;
4. every one of the \(p\) triangle-to-pendant gaps;
5. every loop gap and both loop-dart orders;
6. slot partitioning at all four germs;
7. every phase pair, component seed, and retained combination; and
8. independent witness reconstruction with Euler characteristic two.

Any other support is unsupported.

## 7. Two-hop AK(3) scope

Composing the exact 34 one-hop AK(3) subword-CoV outputs with the same
gated family produces 1,724 raw second hops and 1,352 distinct exact output
pairs.  Their support inventory is:

| support | outputs | spherical |
|---|---:|---:|
| \(K_4\) | 334 | 0 |
| \(K_4-e\) | 399 | 0 |
| \(C_4\) | 57 | 0 |
| \(P_4\) | 2 | 0 |
| \(K_4\) plus one loop | 164 | 0 |
| \(K_4-e\) plus one loop | 374 | 0 |
| paw plus one loop | 22 | 0 |
| **total** | **1,352** | **0** |

For all 22 paw cases, the loop is attached away from the articulation and
the hypotheses above hold.

The exact searches exhaust 82,776 planar schemes, 10,328,938 phase pairs,
and 50,566,572 component seeds.  There are no unsupported outputs and no
positive requiring regular-neighbourhood validation.

Certificate:

```text
results/stable_ac/theory/ak3_two_hop_cov_thickenability.json
```

Verifier:

```text
experiments/stable_ac/thickenable/two_hop_cov_thickenability_certificate.py
```

This complete null refutes only the exact two-hop
CoV-thickenability attempt.  It does not cover three CoV hops, another
stable family, or stable AK(3).
