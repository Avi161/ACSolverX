# AK3: the seven-vertex fake-surface input

Status: source combinatorics and one equivalent complexity-seven endpoint
certified. The three-checkpoint geometric continuation is frozen without
a complexity reduction. The source-to-AK3 correspondence is replayed below.

## Source and terminal target

[Fagan's dissertation](https://escholarship.org/content/qt6fm617h4/qt6fm617h4.pdf),
Section 4.6.1 and Theorem 4.12, supplies an explicit complexity-seven fake
surface stably equivalent to AK3. [Fagan--Qiu--Wang, Theorem 1](https://arxiv.org/pdf/2412.12293v2)
proves stable AC for contractible fake surfaces of complexity below six
with connected 1-skeleton. A certified 3-deformation between such an
endpoint and this source would therefore suffice for stable AK3, not
ordinary AK3. The below-six terminal theorem remains an external dependency;
the source-to-AK3 correspondence now has the independent literal replay below.

## Checked finite input

The eight signed attaching words are pinned in
[`ak3_fagan_fake_surface_certificate.py`](../../experiments/stable_ac/ak3_fagan_fake_surface_certificate.py).
With vertex indices modulo seven, edge $i$ runs from $v_i$ to $v_{i+1}$,
and edge $i+7$ from $v_i$ to $v_{i+2}$, for $1\leq i\leq7$.
Every attaching path closes without repeating a boundary vertex. Every
edge has exactly three face occurrences; every vertex link is exactly
$K_4$. The counts are $(V,E,F)=(7,14,8)$, hence Euler characteristic one.
This count alone does not prove contractibility.

At a disk corner, the incoming and outgoing core germs occupy two vertices
of its $K_4$ link. A chosen side sheet meets the incoming germ and one
external germ $h$. Continue to the unique corner joining $h$ to the
outgoing germ. Tracking this through the entire boundary gives a permutation
of the two initial side sheets. The implementation keys corners by both
vertex and face, valid because the source face boundaries are embedded;
it is not a validator for arbitrary nonembedded faces after a move.

The independent replay uses signed predecessor/edge/successor triples
instead of the implementation's corner sets. The resulting input table is:

| Disk | Boundary length | Sheet permutation |
| --- | ---: | --- |
| 1 | 4 | identity |
| 2 | 6 | identity |
| 3 | 6 | identity |
| 4 | 4 | identity |
| 5 | 5 | swap |
| 6 | 5 | identity |
| 7 | 5 | swap |
| 8 | 7 | identity |

For disk 1, the two side-sheet circuits, starting on edge 1, are
$(7,3,8,5,7)$ and $(8,6,2,3,8)$. Repeated face labels at different
corners are distinct transport positions. A corrupted edge-sign control
is rejected by the path-closure check.

## Move gate and convergence limit

Disks 1 and 4 meet the input conditions for a trivial four-sided embedded
disk move. Such a move preserves complexity; it is not itself the required
reduction. The primary general move diagram was visually inspected in
Fagan--Qiu--Wang, Figure 5, using the PDF skill after the dissertation's
local download returned an empty file.

[Unverified geometric transition] A transcription trial of the dissertation's
Section 4.5.3 for disk 1 gives these candidate attaching words:

```text
(3,15,17,-16)
(3,11,13,-16,18,-12,-10)
(-18,10,-4,-14)
(4,12,-6,-11,15)
(6,14,-15,19,-13)
(19,-16,10,5,-11)
(5,13,-17,-14,-12)
(3,19,-17,4,5,6,-18)
```

The trial retains seven $K_4$ vertex links and three occurrences per edge,
but those checks alone do not certify a 3-deformation. The local signed
rewrite and its handling of shared external edges remain unaudited as a
geometric move. In particular, the source-only embedded-face checker cannot
simply be applied to the candidate: its second face repeats a vertex.
The separate algebraic certificate below establishes endpoint equivalence
without asserting that this is the published local rewrite.

## Certified endpoint equivalence by two donor factors

**Terminal theorem for this checkpoint.** The displayed target is a
complexity-seven fake surface whose maximal-tree-collapsed presentation,
under the explicit cotree marking below, is ordinary AC-equivalent to a
maximal-tree-collapsed presentation of the source. Consequently, using
the source correspondence replayed below, its presentation is stably AC-equivalent
to AK3. This does not trivialize either presentation.

The generic endpoint checker identifies oriented edge endpoints using
every attaching-word corner, without assuming embedded face boundaries.
It independently verifies $(V,E,F)=(7,14,8)$, connectedness, triple edge
incidences and all seven $K_4$ links. The source and target spanning trees
are respectively
\[
T=\{2,4,7,8,9,11\},\qquad U=\{4,11,15,16,18,19\}.
\]
Both are checked to have six distinct edges, no cycle, and all seven
vertices. Collapse each tree; name target cotree edge 17 as $x_1^{-1}$,
and retain the other cotree names. This is a choice of names for two free
bases, not an assertion that an arbitrary generator substitution is an
ordinary AC move. The collapsed source rows, in integer-word notation,
are

```text
(1,-3)
(3,13,-12,-10)
(10,-14)
(12,-6)
(6,14,-13)
(10,5)
(5,13,1,-14,-12)
(1,3,5,6)
```

The target differs only in its first row, which is inverted, and its
last row, which is $(3,1,5,6)$. Put $r=x_1x_3^{-1}$, and let $w,w'$
denote these source and target last rows. Literal free reduction gives
\[
ww'^{-1}=x_1x_3x_1^{-1}x_3^{-1}
=r\,(x_3r^{-1}x_3^{-1}).
\]
Use the retained first row to left-multiply $w$ by the inverse of this
two-factor product, restoring the donor after each conjugation/inversion.
This yields $w'$ exactly. Invert the first row last. All other rows are
unchanged, proving the stated ordinary AC equivalence in the common
marked free group.

Tree collapse and the source correspondence transfer stable equivalence and
trivial fundamental group to the target. For this finite connected
two-complex, simple connectivity and Euler characteristic one imply
$H_2=0$: its second homology is free abelian and has rank zero. Thus it is
acyclic and simply connected, hence contractible by Hurewicz and Whitehead.
This conclusion uses the transferred fundamental-group statement, not
Euler characteristic alone. The finite incidence checks do not by themselves
establish the required fundamental-group statement.

The independent tests reconstruct endpoint identifications with set
merging, replay the tree collapses and donor identity, and reject an
incomplete tree and a corrupted conjugator. All 28 focused fake-surface,
boundary-corridor and preimage tests pass. Neither an exact local
geometric rewrite nor a complexity reduction is claimed.

## Independent source-to-AK3 replay

For a second source maximal tree
$T_0=\{2,3,5,7,10,13\}$, the eight collapsed rows are

```text
(1,9,-8)
(11,-12)
(8,-4,-9,-14)
(4,12,-6,-11)
(6,14,-8)
(-11,-9)
(1,-14,-12)
(1,4,6)
```

Keep the original row numbers through the following deletions. A defining
row containing its eliminated generator exactly once can be normalized
to that generator times a word in the others, used to substitute in the
remaining rows, and then removed by inverse stabilization. Apply:

| Original donor row | Eliminated generator | Defining word |
| --- | --- | --- |
| 2 | 11 | $(12)$ |
| 6 | 12 | $(-9)$ |
| 3 | 4 | $(-9,-14,8)$ |

Conjugate original row 4 by $x_9$, giving
$w=x_{14}^{-1}x_8x_9^{-1}x_6^{-1}$. The retained original row 1 is
$r=x_1x_9x_8^{-1}$. With $w'=x_{14}^{-1}x_1x_6^{-1}$, the sole
non-defining correction is the literal identity
\[
ww'^{-1}=x_{14}^{-1}r^{-1}x_{14}.
\]
Thus the inverse of this conjugate corrects row 4 to $w'$ while restoring
row 1. Continue the defining-row deletions:

| Original donor row | Eliminated generator | Defining word |
| --- | --- | --- |
| 4 | 6 | $(-14,1)$ |
| 5 | 8 | $(-14,1,14)$ |
| 7 | 9 | $(14,-1)$ |

The remaining original rows 1 and 8 are exactly
\[
(1,14,-1,-14,-1,14),\qquad (1,1,-14,-14,-14,1,1).
\]
Name $x=x_{14}$ and $y=x_1$, in this order. Conjugate the first row by
$x$; invert the second and conjugate it by $y^2$. The result is the
standard AK3 pair
\[
\bigl(xyx\,y^{-1}x^{-1}y^{-1},\ x^3y^{-4}\bigr).
\]
This explicitly fixes the final generator naming instead of relying on
the dissertation's prose identification. These are six defining-generator
deletions and one retained-donor correction, not a trivialization.

For completeness, the group presented by this pair is trivial. The braid
relation makes $\Delta=xyx$ interchange $x$ and $y$ by conjugation.
Hence $x^3=y^4$ also implies $y^3=x^4$, and then
$x=x^4x^{-3}=y^3y^{-4}=y^{-1}$. The power relation gives $y^7=1$,
while the braid relation gives $y^2=1$, so $x=y=1$. These group
consequences are not asserted to be available live AC rows.

There is no circular use of the trivial-group hypothesis here: read the
defining substitutions first as ordinary Tietze eliminations and the
retained-row identity as a group-preserving relation replacement. These
establish that every intermediate balanced presentation has the same
trivial group as AK3. The stable defining-row and ambient-substitution
principles may then be applied with that hypothesis established. The
independent replay checks all six unique generator occurrences, each
vanishing defining row, the corrected recipient, and both final relators;
a wrong-sign correction is a can-fail control. All 29 focused certificate
tests pass.

Changing from $T_0$ to the earlier tree $T$ changes a free basis of the
graph fundamental group and the chosen paths to the face basepoints.
The latter give permitted row conjugations; the former gives an ambient
free-group automorphism. Both collapsed presentations are balanced and
present the trivial group, as just proved. The stable ambient principle
in [Proposition 3.3](AK3_DUAL_SOURCE_COMPRESSION.md#proposition-33-stable-ambient-automorphisms-in-every-rank)
therefore applies. This carries the replayed stable AK3 correspondence
to the first endpoint without assuming the geometric transcription is
correct. No ordinary-AC equivalence to AK3 follows from this argument.

## Convergence decision: frozen at checkpoint three

The source checkpoint and the certified first endpoint used two of the
three allotted checkpoints. The final bounded trial inspected the other
source four-gon (disk 4), with face-length vectors
\[
(5,4,7,4,5,5,5,7),\qquad (5,6,6,4,4,6,6,5)
\]
for its two orientations. Following the first orientation by the exposed
disk-2 four-gon in orientation zero gives
$(6,4,6,6,5,4,4,7)$. Every candidate still has seven vertices and no
face of length at most three. These are unpromoted transcription trials,
not certified geometric moves or an exhaustive enumeration.

The required complexity reduction was not obtained, so the geometric
continuation is frozen. Preserve the source, the one algebraically
certified endpoint, and the independent source correspondence; do not
extend the move ledger or count complexity-preserving endpoints as net
progress. This supplies no obstruction to a different geometric or AC
route. Stable AK3 and ordinary AK3 remain unproved here.
