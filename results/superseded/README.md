# `results/superseded/`

Artifacts that are no longer the reference for anything, but are kept for provenance rather than deleted outright — they document what an earlier stage of the project produced and looked at, even though a later result replaced them.

"Superseded" here means: kept, never cited as evidence, and never the input to any script in this repo. If you find yourself about to read a number out of something under this directory to support a claim, stop — find its replacement first (each subdirectory below says what that is) and cite that instead.

## `graphs/`

`baseline_nodes_explored.png`, `baseline_path_length.png`, `difficulty_ranking.csv` — moved here from a directory that used to sit directly under `results/`. No script in the repo produces these; they were made ad hoc. `difficulty_ranking.csv` (the 640 sorted by `(nodes_explored, path_length, pres_id)`) is superseded by `benchmark/difficulty_bins.csv`, which carries the same ranking as its `difficulty_rank` column, plus the bin, the Aut class, and the 50k columns. Use that instead.
