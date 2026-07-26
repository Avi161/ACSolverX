# AK(3) qW-inverse D-Tail Compression Merge Plan

**Goal:** Compute the stable pair-deletion endpoint of
\(qW^{-1}D^k\) for every integer k, and classify the second
primitive-single gate for \(k=\pm1\).

**Architecture:** Expose a based rank-four primitive pair, apply an
all-integer Nielsen shear, replay the full pair quotient, classify the
two first sequential quotients, and apply the final rank-two AC factor
into the known compression corridor.

**Tech Stack:** Markdown proof and dependency-free free-group replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Transport the full tuple through every ambient automorphism.
- Verify every claimed automorphism with an explicit inverse or the
  complete Whitehead list.
- Prove nonprimitivity before calling the D-image the unique second
  deletion.
- Distinguish a merge into a known stable corridor from a
  trivialization.
- AK(3) remains open.

### Task 1: First deletion

- [x] Prove \((Wq^{-1},D)\) is a based primitive pair.
- [x] Prove \(qW^{-1}D^k\) is one all-integer Nielsen-shear family.
- [x] Replay the k-independent full A/W pair quotient.
- [x] Record four-block straighteners and exact inverses for both signs.
- [x] Replay the source length chains and terminal q-coordinate.
- [x] Apply each straightener to all three survivor slots and delete q.

### Task 2: Second deletion gate

- [x] Give strict Whitehead descents for both primitive D-images.
- [x] Give complete nonprimitive certificates for both A-images and
  both W-images.
- [x] Prove the D-image is the unique primitive survivor for each sign.

### Task 3: Common rank-two endpoint

- [x] Delete the primitive D-image and record both exact rank-two pairs.
- [x] Map both pairs to one common representative.
- [x] Replay one retained-source AC factor to the known floor-14 pair.
- [x] Bind the endpoint to the proved rank-three compression theorem.

### Task 4: Verification and checkpoint

- [x] Build and run an independent dependency-free replay.
- [x] Obtain a hostile audit.
- [x] Record Result 47 and update the live lead.
- [x] Commit and push.
