# Primitive-single compressed-relator screen

Status: **pass**; 19/19 fixed panel rows evaluated.

This applies the known primitive-single-relator removal theorem. It is not a new theorem or an ordinary expanded certificate. The source presentations are known trivial-group Miller–Schupp representatives; triviality is a hypothesis of the stable defining-word and ambient-map realizations.

A candidate has D=Z w and exact templates I[z=w]=oriented R, C[z=w]=S. Every generator appearing in cyclically reduced I must occur at least twice; z must appear and the abelian exponent gcd must be one. Thus the existing literal single-occurrence isolator is excluded. Defining words are literal cyclic substrings of length2..6. Each decomposition call retains at most64 templates; two shortest companion templates are kept, then64 shortest distinct candidate combinations per row.

Each complete descent round tests all90 rank3 Type-II Whitehead maps against I. The chosen invertible map acts on all three relators, followed by explicit individual conjugation/inversion witnesses. A singleton I is normalized to its positive generator, that generator is set to1 in both remaining words, and the pair is relabelled to x,y and strictly Nielsen-reduced. Primitivity alone is never labelled a gain.

Every stored rank3 boundary counts all three relators, including D. The reported maximum is only the maximum over these recorded boundaries. A theorem-backed stable realization of an ambient rank3 map may briefly use rank4; its internal ordinary states and maximum length have not been expanded or bounded.

The shared budget is1000 word-image evaluations per input, including all rank3 candidate images, chosen whole-tuple images, and rank2 Nielsen candidate images. Candidate template generation and independent replay are timed separately from these work counts. No heap, search campaign, JIT, or AK3 rerun is used.

Planted checks: {"corrupt_macro_rejection": 5, "image_budget_boundaries": 12, "independently_replayed_planted_primitive_macros": 4, "invalid_candidate_rejection": 3, "rank3_maps_with_both_inverse_compositions": 90}.

Panel CPU time (candidate generation and independent replay included): 2.206906s. Serial cooldown:0.1s after each new row.

| Input | Eligible candidates | Tried | Primitive endpoints | Images | Input L | Best endpoint L | Gain |
|---|---:|---:|---:|---:|---:|---:|---|
| aca_116 | 0 | 0 | 0 | 0 | 14 | None | False |
| aca_1 | 2 | 2 | 0 | 180 | 15 | None | False |
| aca_13 | 9 | 5 | 1 | 969 | 16 | 17 | False |
| aca_30 | 11 | 5 | 0 | 915 | 17 | None | False |
| aca_55 | 11 | 2 | 2 | 917 | 18 | 27 | False |
| aca_80 | 24 | 5 | 0 | 918 | 19 | None | False |
| aca_59 | 37 | 6 | 0 | 912 | 20 | None | False |
| aca_79 | 90 | 6 | 0 | 912 | 21 | None | False |
| aca_82 | 50 | 3 | 2 | 917 | 22 | 37 | False |
| aca_109 | 38 | 3 | 2 | 933 | 23 | 41 | False |
| aca_108 | 83 | 6 | 1 | 966 | 24 | 45 | False |
| aca_101 | 728 | 3 | 2 | 933 | 25 | 38 | False |
| aca_117 | 0 | 0 | 0 | 0 | 14 | None | False |
| aca_9 | 0 | 0 | 0 | 0 | 15 | None | False |
| aca_67 | 38 | 4 | 1 | 972 | 20 | 30 | False |
| aca_86 | 32 | 3 | 2 | 933 | 22 | 37 | False |
| aca_106 | 40 | 3 | 2 | 965 | 21 | 26 | False |
| aca_54 | 48 | 11 | 0 | 990 | 19 | None | False |
| aca_5 | 20 | 7 | 0 | 912 | 19 | None | False |

Strict endpoint gains: 0/19 evaluated rows. Primitive endpoint occurrences: 15. Every stored attempt and endpoint passed the independent string-rewrite verifier.

The JSON contains full map inverses, whole tuples, source orientations, exact compression substitutions, canonicalization witnesses, deletion/relabel witnesses, rank2 descent, all boundary lengths, per-candidate charges and source hashes. A null result concerns only these finite templates and the declared shared budget.

Known theorem source: `codex-proofs/literature/proofs/AK3_PRIMITIVE_SINGLE.md`. The prior AK3 negative census was read for scope and was not rerun.
