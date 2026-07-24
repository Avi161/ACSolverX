# AK(3) One-Edge Primitive Compression Plan

**Goal:** Decide whether one rank-three AC multiplication can create a
primitive relator whose removal reaches rank-two Aut-floor at most 12.

**Architecture:** Enumerate the full signed cyclic one-edge image of the 3,016
verified rank-three sources, deduplicated by source/target/cyclic target word.
Use exact necessary abelian and Whitehead-graph gates, then a length-only
rank-three Whitehead reducer. Remove every primitive target using the proven
primitive-single theorem and certify all rank-two outputs.

**Constraints:** No graph traversal; full stated one-edge image; new task
artifacts; CPU only; cache canonical product words globally; independently
verify all gates and positive removals; push within twenty minutes; no PR.

## Tasks

- [ ] Create `literature/proofs/AK3_ONE_EDGE_PRIMITIVE.md`.
- [ ] State the primitive-product stable implication.
- [ ] State and test the abelian gcd and Whitehead cut-vertex gates.
- [ ] Cross-check fast and slow Whitehead minima on deterministic fixtures.
- [ ] Create `one_edge_primitive.py` with global word/reduction caching.
- [ ] Run the complete production preflight with progress checkpoints.
- [ ] Create `one_edge_primitive_certificate.py` and independent replay.
- [ ] Generate/replay `ak3_one_edge_primitive.json`.
- [ ] On floor at most 12, expand the stable proof. Otherwise adjudicate the
  exact return orbits and select the next nontriangular mechanism.
- [ ] Commit, push, and continue the proof loop.
