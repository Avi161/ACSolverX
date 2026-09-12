# Rigid-link block-count obstruction and independent corner audit

Status: all sixteen planar unknowns in the frozen `stable_neuwirth_report.json`
have an exact necessary-condition obstruction. The other sixty-nine
nonplanar-support exclusions have independently checked Kuratowski subdivision
certificates. This excludes compatible spherical links for these **85 exact
word tuples**. It does not exclude other representatives, stable moves, or AC
triviality of an input.

Source report SHA256:
`71f193ca7937c9fbba82fda1464243d83007439ac8d1fb6dd6c73ed9e7ae383e`.
The complete reproducible witnesses are in `rank3_neuwirth_extension.json`;
`rank3_neuwirth_extension.py` is the small verifier/obstruction module. The
source report's `aca_24` tuple is its older total-16 tuple, not the subsequently
found total-15 tuple. The latter is assessed separately below.

## Rigid-support generalization

All sixteen simple supports have exactly six vertices, no loops, and are
3-connected and planar. There are 10, 11, or 12 support edges. Thus they meet
the hypotheses of the already proved parallel-expansion theorem in
`codex/proofs:literature/proofs/AK3_RANK3_RIGID_THICKENABILITY.md`, Theorem3.1.
That theorem is stated for **any** finite simple 3-connected planar support;
the old solver's restriction to K6 minus P5 is an implementation restriction.

Whitney's uniqueness theorem gives one spherical macro-rotation up to global
reflection. See the primary research paper
[Georgakopoulos and Kim, 2-complexes with unique embeddings in 3-space](https://arxiv.org/abs/2109.04085),
which states this classical graph theorem explicitly. Here only its graph
statement is used, not a three-dimensional uniqueness claim.

For completeness, every parallel class between support vertices u,v is a
single cyclic interval in any spherical embedding. Indeed the parallel arcs
divide the sphere into regions. The connected graph H-{u,v} lies entirely
in one region, as do all other edges incident to u or v. All other regions
are empty digons. The parallel-edge orders at their two endpoints are
therefore reversed linear orders. Collapsing the intervals gives one of the
two Whitney macro-rotations. Conversely, expanding edges into such reversed
ribbons preserves sphericity.

Global reflection preserves the required generator-pipe compatibility
C_negative = B C_positive^-1 B. Hence it is sufficient to inspect one
macro-rotation. This does not permit independent reflection at individual
germs. The implementation also checked every obstruction after reflecting
all six macro-rotations simultaneously.

## A cheaper necessary condition than signed-rank propagation

Fix that macro-rotation and replace each neighboring support edge by a block
whose length is its parallel multiplicity. For a positive generator germ g
and its negative germ G, let

    P_g(j) = parallel class occupying positive slot j,
    N_g(j) = parallel class occupying negative slot j,
    d_g    = the common germ degree.

For each actual occurrence, B pairs a positive endpoint e with a negative
endpoint B(e). Let M_g(p,q) count occurrences whose two endpoints belong to
parallel classes p and q. Pipe reversal forces a cyclic phase s_g such that

    slot(B(e)) = -slot(e)-s_g mod d_g.

Consequently every compatible spherical link must satisfy, for every p,q,

    M_g(p,q) = #{j : P_g(j)=p and N_g(-j-s_g)=q}.       (1)

This equation forgets individual edge ranks, so it is necessary, not
sufficient. Its advantage is that it needs only d_g cyclic shifts. If no
phase satisfies (1) for even one generator, the link is not compatibly
spherical. This is a complete negative certificate, with no phase-tuple or
rank search. Surviving phases alone must be reported UNKNOWN unless further
rank-consistency work or an explicit spherical rotation supplies a decision.

The JSON saves every observed class-pair count and, for every rejected phase,
one mismatching class pair together with the actual and predicted counts.
For each source, deletion of every set of zero, one, or two support vertices
was checked to leave a connected graph (22 checks). NetworkX supplies one
planar embedding, whose rotation structure is also checked.

## Exact sixteen-row result

| Tuple | Simple edges | Phase checks | Generators with no phase |
|---|---:|---:|---|
| aca_24 |12|16|x,y,z|
| aca_54 |11|16|y,z|
| aca_55 |12|17|x,y|
| aca_57 |12|18|x,y,z|
| aca_59 |11|17|y|
| aca_79 |11|18|y,z|
| aca_80 |12|18|x,y|
| aca_82 |11|20|x,y,z|
| aca_83 |10|20|x,y,z|
| aca_86 |12|20|x,y|
| aca_101 |12|21|x,y,z|
| aca_108 |12|22|y,z|
| aca_109 |12|21|x,y|
| aca_111 |12|22|x,y|
| aca_112 |12|22|x,y,z|
| aca_114 |10|21|x,y,z|

Total:309 phase checks, at most22 on an input. No factorial orders, rank
assignments, or symbolic search nodes were enumerated. The module plus its
controls ran in approximately0.17 CPU seconds on this run.

## Independent audit of root's conventions

For a cyclic adjacent pair ab in a relator, the corner connects the arrival
germ a^-1 to the departure germ b. A separate literal-word reconstruction of
these unordered corner classes agrees with the source A/B dictionary for
all85 exact tuples. Each A pair is counted once, whereas each letter has one
B-paired occurrence. Thus root's simple graph is the correct underlying
support of the occurrence multigraph, not an exponent or syllable graph.

For any rotation C, faces are cycles of AC (equivalently CA, by conjugacy).
The number of vertices is cycles(C), edges is |A|/2, and connected components
are the orbits of <A,C>. Root's expression

    |A|/2 - cycles(C) + 2*components - cycles(AC)

is therefore twice the sum of orientable genera. Root's `_build_C` makes the
negative rotation B-reversed, as required. Fixing the first positive endpoint
removes only cyclic rotational redundancy. Its mixed-radix index sampling is
bounded, not exhaustive when the factorial order product exceeds the cap;
root correctly preserved those cases as unknown. No positive root witness
was present, so no thickenability-to-AC theorem is invoked in this audit.

For each of the69 nonplanar simple supports, the module saves NetworkX's
Kuratowski edge subgraph and independently suppresses all degree-two vertices.
The resulting graph is checked directly to be K5 or K3,3. Thus these negatives
have an explicit subdivision witness, rather than only a repeated Boolean
planarity call. Any embedding of the full multigraph would embed this support,
so the support obstruction is sound.

The new exact `aca_24` tuple `(XXZYY,XXyxZ,XYzYZ)`, total15, has a nonplanar
simple support as well. A K3,3 subdivision uses the support edges

    XZ, Xz, YZ, Yz, Xx, Yx, xy, Zy, yz.

These nine edges already form K3,3, with parts {X,Y,y} and {Z,z,x}.
This is an additional exact-complex exclusion, separate from the old85 report.

## Controls and limits

Sixty-four positive controls were constructed from the planar octahedron:
choose all4^3 pipe phases, pair opposite germs by reversed slots, and recover
literal relator words from the alternating A/B cycles. Each construction has
a compatible spherical rotation by construction. All64 pass the necessary
block-count test. The controls are not claimed to present the trivial group.
All16 negative results are invariant under global reflection.

The signed-rank solver can indeed be generalized to every loopless
3-connected planar support by replacing its K6-P5 classifier and factorial
macro-rotation enumerator with verified connectivity and one planar embedding.
The rank equations and all-different constraints then remain unchanged.
There is no reason to implement that additional search for the current16,
because (1) already rejects every one. Outside the rigid hypotheses, this
module returns unsupported/unknown, except for separately certified nonplanar
supports. Nothing here proves an unbounded exclusion over stabilizations,
word moves, free reductions that alter the exact complex, or ambient frames.

## Arbitrary-rank statement and the six recursive endpoints

The interval-count obstruction is rank-independent. For any finite balanced
or unbalanced word tuple on r generators, form its exact occurrence link.
If its simple support is loopless, planar, and3-connected, the parallel-class
argument and Whitney rigidity apply regardless of r. For each of its r pairs
of opposite germs, equation(1) remains necessary. Checking all phases takes
sum_g d_g shifts, equal to the total number of letter occurrences. A failed
phase set still gives an exact negative; a surviving system remains unknown.
The module now uses these general hypotheses instead of requiring six germs.
No SPQR or nonrigid-support extension is asserted.

After the independent recursive audit, the six new rank-four endpoints were
checked exactly. The JSON records their full words and pins the source audit.

| Rank-four endpoint | Simple edges | Exact obstruction |
|---|---:|---|
| aca_108 |19|verified Kuratowski subdivision|
| aca_109 |16|verified Kuratowski subdivision|
| aca_111 |18|verified Kuratowski subdivision|
| aca_112 |19|verified Kuratowski subdivision|
| aca_113 |15|verified Kuratowski subdivision|
| aca_114 |15|rigid interval-count failure for u,x,y,z|

The `aca_114` support has eight vertices and passes every deletion of up to
two vertices. Its20 cyclic phase checks leave no phase for any of its four
generators. All six exact new complexes are therefore excluded. The five
nonplanar witnesses are independently reduced to K5 or K3,3 in the same way
as the earlier69. This adds six exact-complex exclusions and makes no claim
about an entire stable equivalence class.

As a rank-four implementation control,81 further compatible fixtures were
constructed from a spherical cube embedding, one for each of its3^4 pipe
phase choices. All81 pass the necessary condition. Together with the64
rank-three octahedral fixtures, there are145 constructed positive controls.
The planar rank-four negative also retains its obstruction under global
reflection. The final module run, including these controls and all listed
checks, took approximately0.25 CPU seconds.
