# AK(3) QW Transported-Tail Plan

**Goal:** Prove every signed source
\(q^\eta W^\epsilon\beta(V)\), with
\(V\in\langle\!\langle R\rangle\!\rangle\), is a two-deletion
self-loop.

**Architecture:** Delete the unique-z source to transfer \(\beta(V)\)
into W, recognize the transferred word as a left transported primitive
q-source, delete it, then return the resulting rank-two relator modulo
the retained R-slot.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Check all four sign pairs.
- Require V to be q-free and in the normal closure of R.
- Keep both deletion slots distinct in the stated order.
- AK(3) remains open.

### Task 1: Tail-transfer theorem

- [x] Manufacture the coherent tail from the A-slot.
- [x] Give both sign-dependent unique-z automorphisms and inverses.
- [x] Prove the uniform transferred W image.
- [x] Prove later changed-source traffic vanishes.

### Task 2: Left transported deletion

- [x] Give \(\ell_{V,\eta}\) and its inverse for both eta signs.
- [x] Compute the second deletion map.
- [x] Derive the exact general rank-two endpoint.
- [x] Prove classical return modulo R.

### Task 3: Exact replay and checkpoint

- [x] Replay several nontrivial V normal-closure words and all signs.
- [x] Verify both automorphism pairs and deletion maps.
- [x] Verify the V=R endpoint and two-factor return.
- [x] Complete hostile audit and focused tests.
- [ ] Record Result 45, commit, and push.
