# AK(3) qW-inverse D-tail compression merge design

Date: 2026-07-26

## Objective

Determine the full stable pair-deletion endpoint of the integer family

\[
Q_k=qW^{-1}D^k,
\qquad k\in\mathbb Z,
\]

and determine whether the two first tails \(k=\pm1\) have any other
primitive-single second deletion. The calculation must transport the
whole four-relator tuple through explicit ambient straighteners.
Primitivity of \(Q_k\) alone does not determine the surviving
presentation.

## Method

Use explicit automorphisms and quotient maps, not AC graph search.

- Expose \(Wq^{-1}=\beta(Rz^{-1}xt)\) and prove the resulting ordered
  pair with D extends to a basis by a based Whitehead certificate.
- Use a triangular Nielsen shear to straighten
  \(qW^{-1}D^k\) and D simultaneously for arbitrary k.
- Compute the full A/W quotient and prove it is independent of k.
- For \(k=\pm1\), also compress each earlier 12/13-step cyclic
  certificate into four automorphism blocks with explicit inverses.
- Apply the blocks to every relator at the checkpoint
  \((A,W,D,Q_\delta)\), straighten \(Q_\delta\) to \(q\), and delete q.
- Classify the three surviving rank-three relators by complete
  Whitehead descent.
- Straighten and delete the unique primitive survivor.
- Compare the two resulting rank-two pairs by an explicit
  automorphism and one ordinary retained-source AC factor.
- Identify the endpoint with the already proved rank-three compression
  corridor.

## Verified claims

The independent replay and hostile audit establish:

1. \((Q_k,D)\) is a based primitive pair for every integer k;
2. deleting it sends every k to the same rank-two Aut-orbit;
3. for \(k=\pm1\), the D-image is the unique primitive survivor after
   deleting \(Q_k\);
4. one retained-source factor reduces the common pair to the exact
   floor-14 endpoint in
   `literature/proofs/AK3_RANK3_COMPRESSION.md`.

## Boundary

Even if all four claims hold, the result proves neither AK(3) nor
stable AC. It closes the pure D-power pair-compression route, and for
the first two powers it closes the immediate primitive-single second
deletion by merging into a previously certified stable corridor. It
does not rule out primitive-pair deletion using one of the six
nonprimitive \(Q_{\eta,\epsilon,\delta}\) rows, histories with another
\(Wq^{-1}\) block, changes to the displayed survivor or carrier
relators, or a different first primitive slot. D-only left/right
splits around one \(qW^{-1}\) block are included in the theorem.
