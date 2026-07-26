# AK(3) Transported-Q-Source Gauge Plan

**Goal:** Prove coherent q-dependent changed sources
\(Q=\beta(qV)\) are gauges and close the exact AK source
\(q\beta(R)\).

**Architecture:** Straighten \(Q\) by
\(\delta_V^{-1}\beta^{-1}\), recover the coherent carrier sources
literally, compare the remaining quotient modulo their normal closure,
then replay the exact AK return.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Constraints

- Theory before implementation.
- No AC graph search.
- Require \(\beta(q)=q\) and \(\rho\beta=\rho\).
- Keep \(Q\) distinct, unchanged, and delete it first.
- Permit later traffic only from \(Q\).
- AK(3) remains open.

### Task 1: General theorem

- [x] Prove \(Q=\beta(qV)\) is primitive and manufacturable.
- [x] Compute the exact straightening/deletion map.
- [x] Return every coherent carrier source literally.
- [x] Compare every other survivor modulo the retained normal closure.

### Task 2: AK specialization

- [x] Compute the images of \(x,t,z,q\).
- [x] Compute the exact three-relator endpoint.
- [x] Return the middle relator by conjugation.
- [x] Return the last relator by two R-source factors.

### Task 3: Verification and checkpoint

- [x] Replay both automorphism composition orders.
- [x] Replay representative \(Q\)-normal-closure traffic in every slot.
- [x] Verify all endpoint and return identities.
- [x] Complete focused tests and hostile audit.
- [x] Record Result 43, commit, and push.
