# AK(3) Primitive-Single Removal Plan

**Goal:** Prove and exactly decide whether removing an individually primitive
relator from any bounded rank-three corridor reaches a rank-two presentation
of Aut-floor at most 12.

**Architecture:** Extend the cross-checked rank-three Whitehead layer to one
cyclic word. Load the 3,016 verified rank-three sources, reduce every distinct
relator, and for each primitive occurrence apply its witness to the full
tuple, remove the resulting basis generator, and certify the rank-two output.
A chained verifier validates the upstream primitive-pair certificate and
independently replays every reduction/removal/Aut witness.

**Constraints:** New task artifacts; no AC graph search; CPU only; one
straightening witness per primitive conjugacy class is sufficient by quotient
orbit independence; push within twenty minutes; no PR or merge.

## Tasks

- [ ] Create `literature/proofs/AK3_PRIMITIVE_SINGLE.md`.
- [ ] Prove primitive-relator removal.
- [ ] Prove the quotient rank-two Aut-orbit is independent of the chosen
  straightening automorphism.
- [ ] Add single-word Whitehead reduction and replay tests.
- [ ] Create `primitive_single.py` and exact small-slice tests.
- [ ] Enumerate all verified sources and compute complete output floors.
- [ ] Create `primitive_single_certificate.py`.
- [ ] Independently verify the upstream source certificate, all Whitehead
  gates, removals, and rank-two Aut witnesses.
- [ ] Generate/replay `ak3_primitive_single.json`.
- [ ] Adjudicate in `AK3_PRIMITIVE_SINGLE.md`.
- [ ] On floor at most 12, expand the stable proof; otherwise formulate the
  next genuinely nontriangular mechanism and continue.
