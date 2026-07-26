# AK(3) carrier-edge primitive creation design

Date: 2026-07-26

## Objective

At each of the six nonprimitive D-tail checkpoints

\[
(A,W,D,Q_{\eta,\epsilon,\delta}),
\]

classify the signed-cyclic image of one relator multiplication between
two carriers in \(\{A,W,D\}\), in both target directions. Test the
changed row, every direct pair with an actually surviving row, and
every sequential branch which deletes the newly primitive changed row
first.

## Structural split

- Every A--W child has exactly one \(z^{\pm1}\), hence is primitive by
  an explicit unique-z coordinate.
- The A--D image has no primitive child.
- The W--D image has four exceptional primitive child classes.
- The unchanged Q-row remains nonprimitive and cannot occur directly
  in a primitive pair.

This reduces the apparent carrier census to direct-pair transport for
the unique-z family, four exceptional W--D classes, and rank-three
survivor classification after changed-row-first deletion.

## Exhaustive image

Use the same exact signed-cyclic model as Result 49. Across six
checkpoints, three unordered carrier pairs, and both target directions,
the model has:

- 5,544 literal representatives after quotienting target inversion;
- 11,088 fully oriented indexed literals;
- 4,104 checkpoint-direction-child states;
- 342 global changed-word classes.

The finite Whitehead replay must retain checkpoint and target labels
even though the child word does not depend on Q.

## Proven result

There are no direct primitive pairs. Of the 2,280 primitive-child
states, 2,268 have no primitive rank-three survivor after
changed-row-first deletion. The other 12 are exactly the A-cancellation
child
\(\operatorname{can}(A^{-1}W)=\operatorname{can}(z^{-1}C)\).

A uniform coordinate proof, rather than six separate descents, sends
all 12 to the same raw pair
\((x^3t^{-4},t^{-1}xtxt^{-1}x^{-1})\), whose canonical form is the
rank-two AK(3) floor-13 orbit. No carrier-edge branch in scope reaches
a new endpoint or floor at most 12.

## Boundary

This design does not include arbitrary relative conjugators, deletion
of an unchanged primitive row first, a Q/carrier edge (Result 49), two
row-changing edges, or a changed checkpoint.
