# AK3: the seven-vertex fake-surface input

Status: source combinatorics checked; no reducing 3-deformation certified.

## Source and terminal target

[Fagan's dissertation](https://escholarship.org/content/qt6fm617h4/qt6fm617h4.pdf),
Section 4.6.1 and Theorem 4.12, supplies an explicit complexity-seven fake
surface stably equivalent to AK3. [Fagan--Qiu--Wang, Theorem 1](https://arxiv.org/pdf/2412.12293v2)
proves stable AC for contractible fake surfaces of complexity below six
with connected 1-skeleton. A certified 3-deformation between such an
endpoint and this source would therefore suffice for stable AK3, not
ordinary AK3. These are external theorem dependencies; the current
checker does not independently replay the dissertation's equivalence.

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
but that does not certify a 3-deformation. The local signed rewrite and
its handling of shared external edges still require independent audit.
No candidate above is accepted as an equivalent endpoint on these checks
alone. In particular, the source-only embedded-face checker cannot simply
be applied to the candidate: its second face repeats a vertex.

Convergence budget: at most three checkpoints, counting this source
checkpoint, to obtain an independently certified complexity reduction.
First certify the occurrence-level local move; then inspect a bounded
explicit continuation. Do not open a broad move census or a new residual
family merely because the moves preserve valid link graphs. If the budget
expires without a reduction, freeze this input and return to the existing
proof gates. Stable AK3 and ordinary AK3 remain unproved here.
