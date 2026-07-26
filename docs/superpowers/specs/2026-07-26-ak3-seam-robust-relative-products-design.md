# AK(3) seam-robust relative-product design

Date: 2026-07-26

## Objective

Upgrade Result 49 from signed cyclic representatives to arbitrary
relative conjugators for one Q/carrier multiplication at the six
nonprimitive D-tail checkpoints.

## Tree split

For cyclically reduced nontrivial words U and V, consider the axes of
U and \(cVc^{-1}\) in the standard Cayley tree of the row-specific
transformed basis. No invariance of axis intersection under the basis
change is assumed.

- If the axes are disjoint, their bridge normal form is
  \(U_i b V_j b^{-1}\) with no seam cancellation.
- If the axes meet, choose a common axis vertex. The product is
  conjugate to the free reduction of a signed rotation of U followed
  by a signed rotation of V.

Define the linear-cut Whitehead graph of a cyclic word U by cutting
one cyclic seam and retaining all other adjacent-pair edges. Call U
seam-robust when every cut graph contains a Hamiltonian cycle on all
signed basis vertices.

In the disjoint-axis normal form, the full product graph contains one
linear-cut graph of U. Seam robustness therefore makes the product
connected with no cut vertex, so it is nonprimitive. A primitive
relative product must lie in the finite intersecting-axis rotation
table.

## Six-row certificate

Apply one of

\[
\mathrm{id},\qquad
\alpha,\qquad
\mu\alpha,\qquad
\nu\alpha
\]

to each nonprimitive D-tail row. Every transformed Q-row is
seam-robust.
The verifier will pin:

- the exact transformed word;
- every linear cut;
- a Hamiltonian cycle for every cut;
- the finite transformed carrier rotation tables;
- the inverse image of every primitive child.

## Expected closure

The transformed intersecting-axis tables produce exactly the six
primitive conjugacy classes already found in Result 49, with the same
carrier labels and checkpoints. Since only the changed row differs
and it may be conjugated or inverted independently, every full tuple
is one of Result 49's already transported states.

Thus arbitrary relative conjugators create no additional primitive
changed row, direct primitive pair, or changed-row-first endpoint in
this one-edge Q/carrier stratum.

## Boundary

The theorem concerns one Q/carrier multiplication at the fixed six
checkpoints. It does not cover carrier/carrier products, deletion of
an unchanged primitive row, a nonprimitive changed row followed by
another row change, or two row-changing edges before deletion.
