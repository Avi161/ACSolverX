# Independent primitive-compression audit

Status: **PASS for every saved macro boundary and quotient witness.** The endpoint-only source report correctly records zero shorter rank-two endpoints. It must not be read as zero stable intermediate gains: **12 of the exact 19 panel rows reach shorter complete rank-three presentations**. Every defining relator is included in these lengths.

The audit replays 74 attempts, all 522 stored boundaries, 98 whole-tuple rank-three automorphisms, all 15 positive primitive quotient witnesses, and 30 rank-two Nielsen steps. No source compiler, template enumerator, Whitehead search, or orbit search is imported or run. The checker uses its own integer free-group reducer, inverse, substitution and cyclic/inverse canonicalization. The fixed panel equals the original ordered 20-row panel with exactly `aca_115` removed.

| Input | Original length | Minimum rank-three length | Attempt index | Boundary index |
|---|---:|---:|---:|---:|
| aca_13 | 16 | 15 | 3 | 5 |
| aca_80 | 19 | 18 | 0 | 2 |
| aca_59 | 20 | 17 | 0 | 2 |
| aca_79 | 21 | 19 | 2 | 2 |
| aca_82 | 22 | 20 | 0 | 2 |
| aca_109 | 23 | 21 | 0 | 2 |
| aca_108 | 24 | 22 | 0 | 2 |
| aca_101 | 25 | 21 | 1 | 5 |
| aca_86 | 22 | 20 | 0 | 2 |
| aca_106 | 21 | 20 | 1 | 5 |
| aca_54 | 19 | 16 | 0 | 2 |
| aca_5 | 19 | 18 | 0 | 2 |

These minima include attempts that stop as nonprimitive or at a budget boundary. A primitive straightener decreases the isolator's length; it can increase the other two relators. Thus an early total-length gain need not survive at the rank-two endpoint. For example, `aca_59` reaches `(Zxx, YZYzyz, YYYYxzzz)`, total 17 from 20, despite its isolator failing the primitive test.

## Algebra checked

Each candidate's signed source orientation and exact template expansions are checked against the full original pair. The added defining relator is retained. Each saved rank-three automorphism has both inverse compositions checked on every basis generator and is then independently applied to **all three** relators. Each relator canonicalization is replayed using its recorded inversion sign and conjugator, then compared with the independently computed cyclic/inverse representative.

Deletion is admitted only after the isolator has become a literal signed basis generator and its sign has been normalized. That generator is deleted from the other two relators, the singleton relator is removed, and the remaining basis is relabeled bijectively to `x,y`. All saved rank-two Nielsen maps, inverses, endpoints and strict length decreases are checked. No arbitrary quotient or deletion from a merely unimodular relator is admitted.

The underlying primitive-single theorem is already proved in the proof worktree's `literature/proofs/AK3_PRIMITIVE_SINGLE.md`: in a balanced rank-three presentation of the trivial group, a primitive relator can be straightened and destabilized to rank two. This is an application of that theorem, not a new sufficient family. Known triviality is essential for the stable realization of ambient changes; unimodular exponent sums alone are insufficient.

The 14,244 recorded individual word-image evaluations are shared across all attempts per input, with every input at most 1,000. The audit checks per-kind charges and their row sums. Precomputed map inverses, validity checks and the implicit elementary expansion of stable macros are outside this image-evaluation unit. A displayed rank-three boundary counts all three relators, but does **not** bound internal rank: realizing a rank-three ambient automorphism by a defining-generator macro can transiently use rank four. No maximum internal elementary length or expanded ordinary stream is claimed.

## Scope checks

The same independent checker validates all saved signed parameter matches and exact source joins in `ms_census_scope.json`: 842 recognized census rows, 366 terminal rows, all 366 already in the frozen solved-640 set. It checks all 338 saved original-grid cells and their joins to 31 U124 component labels, all 64 residue-normalized targets, and all 64 saved orbit witnesses. Every saved orbit witness is an invertible signed permutation, and their displayed representatives form 32 groups with no cross-component group.

The scope audit replays saved witnesses; it does not rerun recognition, Nielsen descent or full orbit searches, and does not independently prove completeness of the absent matches or the global orbit census. Grid/member labels establish data joins only, never old AC bridges. No new gain, merge or solve is certified from these scope records. The residue probe's 512 `image_evaluations` are map-pair evaluations (1,024 individual word images), a different unit from the primitive screen.

## Reuse and provenance

`check_primitive_compression_independent.py` exposes `verify_attempt(attempt)` and `verify_prefix(attempt, boundary_index)`. The latter returns the complete verified boundary with `relators`, `rank`, `total_length`, `relator_lengths`, `boundary_index`, and `independently_verified: true`, or raises on disagreement. The JSON audit retains a minimum witness pointer for every row and separates rank-three minima from rank-two endpoint minima.

Source report SHA-256: `3ba2fa1943c394c95022d19b6358b1fabd01ec281e4fe6ab87919834009abd32`. Auditor SHA-256: `9bb5c321a6f134deb57adc0841171fc289cdfa3671a6e4274914fde3b1ad1590`. All source hashes pinned in the original report are checked, including the theorem and stable-certificate conventions. Validation completed in 0.164 CPU seconds.
