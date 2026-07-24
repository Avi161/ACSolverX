# AK(3) Primitive-Pair Corridor Plan

**Goal:** Prove the primitive-pair elimination theorem and exactly decide
whether any relator pair in the certified rank-three corridor states extends
to a basis of \(F_3\).

**Architecture:** A theorem note proves simultaneous two-relator elimination.
A dependency-free rank-three Whitehead layer carries automorphism witnesses
and certifies local minima. A corridor census rebuilds all cyclic rank-three
sources and tests their three relator pairs. A separate verifier replays
source identities, automorphisms, and every no-descent gate.

**Constraints:** New task files only; no AC graph search; CPU only; complete
Whitehead enumeration; push checkpoints at least every twenty minutes; no PR
or merge.

## Tasks

- [ ] Create `literature/proofs/AK3_PRIMITIVE_PAIR.md`.
- [ ] Prove primitive-pair elimination and the Whitehead minimum-two
  criterion for cyclic conjugacy classes.
- [ ] Create `rank3_whitehead.py` test-first.
- [ ] Cross-check its rank-two second-kind automorphisms against `autcanon`.
- [ ] Pin positive `("xz", "t")` and negative `("xx", "z")` fixtures.
- [ ] Create `primitive_pair.py` and rebuild all cyclic rank-three states.
- [ ] Test all three relator pairs per source with composed witnesses.
- [ ] Create `primitive_pair_certificate.py` with independent replay.
- [ ] Generate and verify `ak3_primitive_pair.json`.
- [ ] Adjudicate in `AK3_PRIMITIVE_PAIR.md`.
- [ ] On a positive, expand the complete stable proof. On a null, use the
  minimum-shape distribution to select the next nontriangular mechanism.
- [ ] Run regressions, commit, push, and continue the proof loop.
