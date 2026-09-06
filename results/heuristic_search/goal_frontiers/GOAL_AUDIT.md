# Completion audit

User objective: a fast heuristic or combination solving ideally60/60,
with strictly more than55/60 acceptable, within10k per presentation;
screen at1k first and keep runtime similar to greedy.

| Requirement | Evidence | Status |
|---|---|---|
| Full subset coverage, ideally60 | `matched_10k/runs.jsonl`:60 independently run candidate rows, all solved | Met |
| At most10,000 per row | All component charges sum to `nodes_explored`; maximum404, total6,286 | Met |
| Screen at1k before10k | `cascade_screen` then `cascade_1k`, followed by `matched_10k`; exact1k paths/counts preserved | Met |
| Runtime similar to greedy | Fresh alternating matched run:1.060101s total candidate vs40.565478s greedy; exact40 shared means12.797500ms vs163.049177ms | Met |
| Account for lookahead/combination cost | Accepted normalization transforms, macro root+each rewrite, every restart/search pop all summed; extra image evaluations logged and included in timing | Met with explicit accounting definition |
| General rule rather than an answer table | Solver reads signed words, no IDs/classes/saved results/paths; generic short-relator recognizer and fixed fallbacks | Met |
| Legal, reviewable solutions | All60 candidate paths verified with word-level moves and separate compiled substitution decoder; basis images replay literally | Met |
| Honest length bounds | Ordinary cap48, macro cap256, observed peak131;11 certificates exceed48 | Met; larger caps authorized by user |
| Local-load constraint | Serial one-thread searches with cooldowns; every search budget<=10k; no long-budget local campaign | Met |
| Preservation of production behavior | Production defaults untouched; separate experimental modules and source snapshots | Met |

The result does not establish an initial-state scalar hardness classifier,
held-out transfer, universal coverage outside subset60, or ordinary
substitution-only certificates for paths containing basis changes. None
of those claims is substituted for the measured goal.

Validation:35 focused rewrite/cascade tests; previously22 basis/frontier
tests;100 solved records in the matched run pass two certificate decoders;
all120 records reproduce their respective previously saved paths/counts.
Exact data, hashes, parameter settings and clocks are retained in the
phase manifests, snapshots and per-presentation JSON records.
