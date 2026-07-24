# Rigid six-germ thickenability for the primitive-free AK(3) corridor

Date: 2026-07-24

Status: the rigid-support and signed-rank reduction theorems are **PROVEN**.
The finite 64-state AK(3) thickenability candidate is **REFUTED** by the
exact certificate in Section 6.

## 1. Exact scope

Use the exact occurrence dictionary \((D,A,B,\nu)\) from
`AK3_NEUWIRTH.md`, now on the six germs

\[
V=\{x^+,x^-,z^+,z^-,t^+,t^-\}.
\]

The involution

\[
\tau=(x^+\ x^-)(z^+\ z^-)(t^+\ t^-)
\]

pairs the two ends of each generator.  A compatible rotation \(C\) satisfies

\[
C_{\tau v}=B C_v^{-1}B. \tag{1.1}
\]

Words are used exactly as supplied.  No free reduction, cyclic reduction,
or occurrence identification is part of the thickenability decision.

Among the 3,016 certified rank-three corridor states, 64 have no primitive
relator.  An independent support inventory finds that every one has:

- a connected loopless six-vertex \(A\)-link;
- 11 simple support edges;
- degree sequence \((3,3,3,4,4,5)\); and
- complement equal to a five-vertex path plus one isolated vertex.

The inventory is authenticated by the production certificate.  The theorem
below is independent of that inventory.

## 2. The simple support \(H=K_6-E(P_5)\)

Label the missing path edges

\[
01,\quad12,\quad23,\quad34
\]

and let vertex \(5\) be isolated in the complement.  Thus \(H\) contains
every edge of \(K_6\) except those four.

### Lemma 2.1

The graph \(H\) is planar and 3-connected.

#### Proof

One spherical rotation is

\[
\begin{aligned}
0&:(2,4,3,5),&
1&:(3,4,5),\\
2&:(0,5,4),&
3&:(0,1,5),\\
4&:(0,2,5,1),&
5&:(0,3,1,4,2).
\end{aligned} \tag{2.1}
\]

Its seven face boundaries have lengths

\[
3,3,4,3,3,3,3.
\]

Hence \(V=6\), \(E=11\), \(F=7\), and

\[
V-E+F=2,
\]

so (2.1) is a cellular embedding in \(S^2\).

For 3-connectivity, delete any two vertices.  If vertex \(5\) remains, it is
adjacent in \(H\) to every other remaining vertex and the graph is connected.
If \(5\) is deleted, one additional vertex is deleted from the complementary
path \(P_5\).  The remaining complement is \(P_4\), \(P_3\) plus an isolated
vertex, or \(2K_2\).  Its complement is connected in each case.  Therefore
deleting any two vertices from \(H\) leaves a connected graph. \(\square\)

By Whitney's theorem, (2.1) and its simultaneous reversal are the only
spherical rotations of \(H\).

## 3. Parallel expansions of a rigid support

Let \(G\) be obtained from a finite simple 3-connected planar graph \(H\) by
replacing every support edge \(uv\) with a nonempty labeled parallel class
\(P_{uv}\) of multiplicity \(m_{uv}\).

### Theorem 3.1 (rigid parallel-expansion classification)

A rotation system of \(G\) is spherical if and only if:

1. every \(P_{uv}\) is one cyclic interval at both endpoints;
2. cutting those two intervals at the common nonclass gap gives reversed
   linear endpoint orders; and
3. replacing every interval by its support-neighbor symbol gives one of the
   two Whitney rotations of \(H\).

Consequently, the number of labeled spherical rotations is

\[
2\prod_{uv\in E(H)}m_{uv}!. \tag{3.1}
\]

#### Proof

Fix \(uv\).  The parallel \(uv\)-arcs divide \(S^2\) into \(m_{uv}\)
regions.  Since \(H-\{u,v\}\) is connected, the positive expansion of that
subgraph puts every other support vertex in one region \(R\).  Every
non-\(uv\) edge incident with \(u\) or \(v\) also lies in \(R\), because its
other endpoint lies there and its interior cannot cross a \(uv\)-arc.

Thus all nonclass darts occupy the single \(R\)-gap at both endpoints.
Every \(P_{uv}\) is one block, and all other regions between its consecutive
arcs are empty digons.  Reading those digons cuts both endpoint blocks at
the same \(R\)-gap and gives exactly reversed linear orders.  This is the
step that fails for the middle class of a \(P_4\) support: there the deletion
of the two middle vertices disconnects the two outer components, allowing
independent gaps.

Delete all but one representative edge from every parallel class.  Block
contiguity makes the induced support rotation independent of the chosen
representatives.  Whitney rigidity gives one of the two support rotations.
This proves necessity.

Conversely, embed \(H\) using either Whitney rotation and replace each
support edge by a narrow ribbon containing the chosen labeled linear order.
The order at the other endpoint is reversed.  The ribbons have disjoint
interiors, so the expanded rotation is spherical.

For either support orientation, every parallel class has an independent
labeled linear order, giving (3.1). \(\square\)

Applying Theorem 3.1 to Lemma 2.1 gives a complete classification for every
positive parallel expansion of \(K_6-E(P_5)\).

## 4. Three-pipe signed ranks

Fix the lexicographically first of the two reflected support rotations.
This loses no compatible solution.  Reflecting replaces every local cycle
by \(C'_v=C_v^{-1}\).  From (1.1),

\[
C'_{\tau v}
=C_{\tau v}^{-1}
=B C_v B
=B(C'_v)^{-1}B,
\]

simultaneously for \(v=x^+,z^+,t^+\).  Thus all three pipes remain
compatible under one global reflection.

For each of the 11 parallel classes, assign its labeled edges all-different
ranks

\[
z_e\in\{0,\ldots,m_{uv}-1\}.
\]

Expand the fixed macro-rotation into class blocks.  At the reference endpoint
of a class, use increasing ranks; at the other endpoint, use decreasing
ranks.  The resulting slot maps are injective and their images partition
the complete cyclic slot set at every germ.

For each positive generator germ \(g^+\), choose a phase

\[
s_g\in\mathbb Z/n_{g^+}.
\]

Every occurrence contributes the same modular reversal equation as equation
(4.3) of `AK3_SYNCHRONIZED_PLANARITY.md`.  Contracting the \(A\)-edges turns
the \(B\)-pairs into a 2-regular constraint graph: one cycle for each exact
relator.  For fixed phases, one seed rank determines at most one rank around
its whole constraint cycle by injective inverse slot lookup.

### Theorem 4.1 (rigid six-germ criterion)

An exact six-germ \(K_6-E(P_5)\) link has a compatible spherical rotation if
and only if some phase triple

\[
(s_x,s_z,s_t)
\in
\mathbb Z/n_{x^+}\times
\mathbb Z/n_{z^+}\times
\mathbb Z/n_{t^+}
\]

and some retained seed assignment close consistently around every constraint
cycle and satisfy the global all-different rank conditions in all 11 classes.

#### Proof

Theorem 3.1 supplies the unique macro-rotation up to the reflection already
removed above, together with reversed class blocks.  Ranks encode every
linear class order.  The phase lemma and constraint-cycle propagation proof
of `AK3_SYNCHRONIZED_PLANARITY.md`, Theorem 4.3, use only injective slot maps
and apply unchanged to three pipes.  Per-cycle and cross-cycle rank-bitset
checks are exactly the global all-different conditions.  Hence the finite
system is necessary and sufficient. \(\square\)

## 5. Fail-closed obligations

A solver may return NO only after checking all of the following:

1. the exact \(D,A,B,\nu\) occurrence dictionary;
2. all six germs present, a connected loopless link, and simple support
   explicitly isomorphic to \(K_6-E(P_5)\);
3. exactly two reflected spherical macro-rotations among all 6,912 simple
   rotation systems;
4. injective class slot maps partition every germ rotation;
5. all three phase ranges;
6. every seed rank on every constraint cycle;
7. every retained cross-cycle combination and all 11 rank partitions; and
8. an independent reconstruction of every positive with (1.1) and Euler
   characteristic two.

Any other support is unsupported, not non-spherical.

## 6. Exact finite decision

The chained certificate rederives the complement of all source indices
having a primitive-relator occurrence.  It obtains exactly 64 sources.
Every source has the proved \(K_6-E(P_5)\) support, and every exact search
returns NO after exhausting:

\[
118{,}976
\quad\text{phase triples and}\quad
1{,}741{,}883
\quad\text{component seeds}.
\]

There are no surviving component combinations and no positive witnesses.
The ordered decision trace is

```text
11bd5e72743f0b9b4ec8d4851b6c0f48b7e1f7cbc28ff4a2dc748b2fb437386b
```

The certificate also compares the signed-rank solver with the independent
factorial occurrence-permutation census on a \(K_6-E(P_5)\) fixture.  Both
return NO after the latter exhausts 17,280 local orders.  Independently
enumerating all 6,912 simple-support rotations gives exactly the two
reflected spherical rotations required by Whitney rigidity.

Certificate:

```text
results/stable_ac/theory/ak3_rank3_rigid_thickenability.json
```

Verifier:

```text
experiments/stable_ac/thickenable/rank3_rigid_thickenability_certificate.py
```

## 7. AK(3) implication

Every one of the 64 finite targets is a certified rank-three presentation of
the trivial group stably equivalent to AK(3).  Therefore one compatible
spherical rotation, after the mandatory independent regular-neighbourhood
audit, would make that exact presentation classically AC-trivial by
Lackenby's Theorem 1.3 and would prove AK(3) stably AC-trivial.

The complete null refutes only this 64-state exact-complex attempt.  It does
not obstruct another rank-three corridor, another stable representative, or
AK(3) itself.
