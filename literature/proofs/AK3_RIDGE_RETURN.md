# The five-orbit ridge return from AK(3) compression

Date: 2026-07-24

Status: the stable implication is **PROVEN**. The finite orbit-2 return
proposition in Section 4 is **UNVERIFIED** until its chained certificate is
built and replayed.

## 1. Ridge roots

The certified post-compression census has a finite child set \({\cal D}\).
Every \(D\in{\cal D}\) is stably AC-equivalent to AK(3): it is reached by the
proven stable corridor followed by one classical AC multiplication.

Let \(m\) be the minimum complete Whitehead floor among \({\cal D}\), and let
\({\cal M}\) contain one complete Whitehead representative from every
Aut(\(F_2\))-orbit at floor \(m\). For every \(M\in{\cal M}\),

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}M,
\]

because an ambient free-group automorphism is stably realizable.

The production upstream certificate reports \(m=15\) and five such
representatives. The chained certificate must derive both facts rather than
assume them.

## 2. One full ridge edge

For every \(M=(R_0,R_1)\in{\cal M}\), enumerate both targets, both signs of
the other relator, and all cyclic rotations. Replace the target by the
cyclic reduction of the two rotated factors and canonicalize the pair.

As in `AK3_POST_COMPRESSION_EDGE.md`, each child is classically AC-equivalent
to its root and therefore stably AC-equivalent to AK(3). No seam filter or
length cap is used.

## 3. Stable implication

### Theorem 3.1 — PROVEN

If any ridge child has complete Aut-floor at most 12, then AK(3) is stably
AC-trivial.

### Proof

Compose:

1. the certified stable compression corridor;
2. its first post-removal classical edge;
3. the ambient automorphism carrying the floor-15 child to its selected
   representative \(M\);
4. the full ridge edge;
5. a complete Whitehead automorphism to total length at most 12;
6. MM03 Theorem 1.1 for the final balanced trivial-group presentation.

Every step before MM03 has an explicit stable or classical witness. Thus the
composite is a stable AC trivialization. \(\square\)

## 4. Finite return proposition

Let

\[
 O_2=(\texttt{YYXXyx},\texttt{YYYxyXX})
\]

be AK(3)'s orbit-2 representative. The repository contains an independently
replayed classical AC path from AK(3) to \(O_2\).

### Five-orbit return proposition — UNVERIFIED

The complete full one-edge image of \({\cal M}\):

1. has no child of Aut-floor at most 12;
2. has minimum floor 13;
3. has exactly one canonical child at that minimum;
4. that child's complete Whitehead representative is \(O_2\).

If certified, this proposition proves that the floor-minimizing continuation
of the finite corridor returns to AK(3)'s known classical AC class. It is a
normal-form result for this corridor, not progress toward triviality.

## 5. Certificate obligations

The chained verifier must:

1. independently verify the entire post-compression certificate;
2. extract all and only its minimum-floor Aut representatives;
3. verify that the root-child image has at most 1,000 states;
4. independently replay each signed rotation product;
5. independently verify every Whitehead witness;
6. compare the full rerun payload;
7. check the exact minimum child count and orbit-2 identity.

## 6. Negative scope

A verified return proposition does not rule out:

- a non-minimal floor-15 child leading to a better later path;
- a different stable corridor;
- a second rank-three multiplication before removal;
- a nontriangular dependency;
- a path whose useful coordinate change is not a Whitehead-minimum
  representative.

It does rule out the most economical greedy continuation of the certified
floor-14 corridor: descend through its minimum ridge orbits and take one more
edge. The next proof attempt must change the pre-removal algebra rather than
mistake orbit-2 for an escape.
