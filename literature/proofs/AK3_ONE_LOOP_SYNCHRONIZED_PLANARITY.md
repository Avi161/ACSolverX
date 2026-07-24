# One-loop synchronized planarity for stable AK(3) images

Date: 2026-07-24

Status: the one-loop rotation and signed-rank theorems are **PROVEN**.  The
finite 34-image AK(3) CoV thickenability candidate is **REFUTED** by the
exact certificate in Section 6.

## 1. Exact scope

Use the exact four-germ occurrence dictionary \((D,A,B,\nu)\) and Neuwirth
compatibility convention from `AK3_SYNCHRONIZED_PLANARITY.md`.  Let \(G\)
be the \(A\)-link.  This note decides the following new support class:

1. \(G\) has exactly one loop edge \(\ell\), at a germ \(v\);
2. deleting \(\ell\) gives a positive parallel expansion \(G_0\) of
   \(H=K_4\) or \(H=K_4-e\); and
3. no word reduction or occurrence identification is performed.

Both permitted cores satisfy \(H-v\) connected for every vertex \(v\).

## 2. The loop insertion theorem

Write \(d=\deg_{G_0}(v)\), counting parallel edges.  The loop \(\ell\) has
two distinct labeled darts \(\ell_0,\ell_1\) at \(v\).

### Theorem 2.1

A rotation system of \(G\) is spherical if and only if:

1. deleting \(\ell_0,\ell_1\) gives a spherical rotation system of \(G_0\);
   and
2. \(\ell_0,\ell_1\) are consecutive in the cyclic rotation at \(v\).

Equivalently, every spherical rotation of \(G\) is obtained uniquely by
choosing a spherical rotation of \(G_0\), one of its \(d\) angular gaps at
\(v\), and one of the two linear orders

\[
(\ell_0,\ell_1),\qquad(\ell_1,\ell_0).
\]

Hence, if \(N(G_0)\) is the number of labeled spherical rotations of the
core, then

\[
N(G)=2d\,N(G_0). \tag{2.1}
\]

#### Proof

Suppose \(G\) is embedded in \(S^2\).  The loop \(\ell\) is a simple closed
curve and separates the sphere into two discs.  Since \(G_0-v\) is
connected, every vertex other than \(v\) lies in the same disc.  Every
nonloop edge incident with \(v\) also enters that disc: its other endpoint
is there and its interior cannot cross \(\ell\).  Thus all \(G_0\)-darts at
\(v\) occupy one of the two cyclic intervals between \(\ell_0\) and
\(\ell_1\).  The other interval is empty, so the loop darts are consecutive.
Deleting \(\ell\) leaves a spherical embedding of \(G_0\).

Conversely, start with a spherical embedding of \(G_0\).  In any chosen
angular gap at \(v\), draw a sufficiently small loop whose interior disc is
disjoint from \(G_0\).  Either direction around the loop realizes one of the
two labeled dart orders.  This gives a spherical embedding of \(G\).

Deletion recovers the core rotation, insertion gap, and dart order
uniquely.  There are \(d\) cyclic gaps and two dart orders, proving
(2.1). \(\square\)

For a \(K_4\) core with class multiplicities \(m_{uw}\), Theorem 3.1 of
`AK3_SYNCHRONIZED_PLANARITY.md` gives

\[
N(G)=4d\prod_{uw\in E(K_4)}m_{uw}!. \tag{2.2}
\]

For a \(K_4-e\) core, let \(a,b\) be the degree-three vertices, put
\(m=m_{ab}\), and use the four leg multiplicities from Theorem 5.2 of that
note.  Then

\[
N(G)=
2d\,(m+1)!\,
m_{ac}!\,m_{bc}!\,m_{ad}!\,m_{bd}!. \tag{2.3}
\]

## 3. Exact slot schemes

Take every complete core slot scheme already proved for \(G_0\).  For a
chosen gap \(g\in\{0,\ldots,d-1\}\), replace each core slot \(q\) at \(v\)
by

\[
q'=
\begin{cases}
q,&q<g,\\
q+2,&q\ge g.
\end{cases}
\]

Assign the loop darts slots \(g,g+1\) in either order.  At all other germs,
leave the core slots unchanged.  The resulting slot images partition
\(\{0,\ldots,\deg_G(w)-1\}\) at every germ \(w\).

For a \(K_4\) core, one may fix one tetrahedral macro-orientation.  Global
reflection preserves both generator-pipe reversal equations and maps every
embedding using the other macro-orientation to one using the fixed
orientation.  Both loop-dart orders and every gap remain enumerated.

For a \(K_4-e\) core, retaining all \(m+1\) cut schemes is complete.  As in
Theorem 5.2, the cut/rank family already contains both reflected core
rotations; no extra reflection flag is added.

## 4. Signed-rank criterion

Give every nonloop parallel class its existing all-different edge ranks.
The one-edge loop class has the fixed rank zero.  For each generator choose
the same cyclic phase as in equation (4.3) of
`AK3_SYNCHRONIZED_PLANARITY.md`.

Contracting every \(A\)-edge, including \(\ell\), again turns the
\(B\)-pairs into a 2-regular constraint multigraph.  For fixed core scheme,
loop gap, loop orientation, and two phases, a seed rank determines at most
one rank assignment on each constraint component.

### Theorem 4.1

An exact one-loop presentation in the scope of Section 1 has a compatible
spherical rotation if and only if some loop-augmented slot scheme, phase
pair, component-seed assignment, and global all-different rank assignment
satisfy every modular reversal equation.

#### Proof

Theorem 2.1 makes the augmented slot schemes a complete list of spherical
rotations before Neuwirth compatibility is imposed.  The core ranks
parameterize every labeled core order, and the fixed loop rank selects its
two explicitly assigned slots.  Lemma 4.1 and Theorem 4.3 of
`AK3_SYNCHRONIZED_PLANARITY.md` apply to arbitrary injective slot maps whose
images partition each germ rotation; they do not require the \(A\)-edges to
be loopless.  Component propagation is therefore necessary and sufficient,
and the global rank partitions are exactly the remaining all-different
conditions. \(\square\)

## 5. Fail-closed obligations

A solver may return NO only after checking:

1. exactly one loop edge, not merely one loop support class;
2. a \(K_4\) or \(K_4-e\) positive parallel core;
3. every proved core scheme;
4. all \(d\) insertion gaps and both loop-dart orders;
5. injective slot images partitioning every germ rotation;
6. every phase pair, component seed, and retained component combination;
7. every core rank partition; and
8. independent witness reconstruction with \(B\)-reversal and Euler
   characteristic two.

Every other support is unsupported, not non-spherical.

## 6. Stable AK(3) implication

The complete no-collapse subword CoV family of AK(3) has 38 candidate
subwords and 34 distinct exact outputs.  Each output satisfies the hypotheses
of the proved Lemma-11 CoV criterion and is therefore stably AC-equivalent
to AK(3).  Existing loopless theorems decide 24 outputs as non-spherical.
The other ten have exactly the one-loop support of this note.

The chained certificate finds:

| support | outputs | spherical |
|---|---:|---:|
| \(K_4\) | 15 | 0 |
| \(K_4-e\) | 9 | 0 |
| \(K_4\) plus one loop | 2 | 0 |
| \(K_4-e\) plus one loop | 8 | 0 |
| **total** | **34** | **0** |

It exhausts 1,419 planar schemes, 139,804 phase pairs, and 553,571
component seeds.  The ordered decision trace is

```text
d2ecadb2eb740dae256c3afec98ae69564522273313e7a129468e82086279d2d
```

The one-loop solver also agrees with an independent factorial rotation
census on one spherical and one non-spherical fixture, twelve complete
orders each.

Certificate:

```text
results/stable_ac/theory/ak3_cov_thickenability.json
```

Verifier:

```text
experiments/stable_ac/thickenable/cov_thickenability_certificate.py
```

This complete null refutes only the exact one-hop subword-CoV
thickenability attempt.  It does not obstruct another CoV family, a
composition of CoVs, another stable representative, or AK(3) itself.
