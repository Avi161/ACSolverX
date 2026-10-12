# Independent test brief (shared by every tester)

You are an independent tester of a computational experiment. You write ONE
self-contained Python 3.12 script (numpy allowed, nothing else outside the
standard library). It will be run later on an AWS box against the real result
files. You never run it yourself.

## Hard rules

- **No local compute.** Do not run Python, pytest, a solver, a loop over data
  or anything CPU-bound on this machine. The only command you may run on your
  script is a syntax check:
  `python3 -I -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" <file>`.
  Reading files (Read, grep, head) is fine.
- Do not call any `mcp__hearthbot__` tool. Do not use AWS, git, or the network.
- The repo clone (called REPO below) is READ-ONLY. Write only inside the
  testers' own directory (called OUT below; committed as this directory), and
  only the files your task names.
- **Independence.** Your script must not import anything from REPO. Do not read
  these files at all (they are what is being checked):
  `verify_rank3_bf.py`, `summarize_rank3_bf.py`, `plot_rankn_vs_control.py`,
  `rankn_checks.py`, `tests/stable_ac/test_rank3_bf.py`, and
  `experiments/stable_ac/solvern_fast.py`. Your task says what else you may read.
- Do not weaken a check to make it pass. If the definition is ambiguous, pick
  the reading you think is right, say so in your notes, and let it fail.

## Script contract

- CLI: `python3 <script>.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]`
  - `RESULTS_DIR`: one flat directory with every result file listed below.
  - `DATASET`: path of `ms640_solved.txt`.
  - `workers` (default 1), `minutes` (default 30): a wall-clock box for scripts
    that search; when time is up, stop and report what was compared.
- Skip (and list as skipped) any expected file that is absent; lengths 9 and 10
  and budget-10,000 lengths 7+ may be missing.
- Write `OUT_JSON`: `{"script": ..., "checks": [{"name": ..., "compared": int,
  "mismatches": int, "detail": ...}], "mismatches": total, "skipped": [...],
  "first_mismatches": [up to 50 concrete examples]}` and print a one-line
  summary per check. Exit code 0 if no mismatch, 3 if any mismatch, 1 on a
  crash. A check that compared 0 items must be reported as such, never as a pass.
- Memory: the largest array is 640 x 39,366 uint16. Load one file at a time.
- Also write `OUT/<script name>.md`: what each check does, what you assumed,
  and anything in the data formats or definitions that looked wrong to you.

## The experiment

Dataset `data/ms640_solved.txt` in REPO: 640 lines, line p (0-based) is
presentation p. Each line is a Python list of 2*L integers: relator r1 padded
with zeros to length L, then r2 padded with zeros. Letters: 1 = x, 2 = y,
-1 = X = x^-1, -2 = Y = y^-1. In strings: x, y, z, a, b for generators 1..5 and
the capital for the inverse. Every presentation `<x,y | r1,r2>` is balanced and
presents the trivial group.

Search: greedy best-first over AC moves ("nodes" = states popped from the
heap), node budget B (1,000 or 10,000), a child is dropped when any relator is
longer than 24. Solved = a state where every relator has length 1 was reached
within the budget. The 2-generator search of `<x,y | r1,r2>` is the **control**.

Rank-3 start for a word w in x,y: `<x,y,z | r1, r2, Z·w>` (third relator: the
letter -3 followed by w). Rank 2+k start for words w_1..w_k:
`<x,y,z_1..z_k | r1, r2, Z_1·w_1, .., Z_k·w_k>` (relator i: letter -(2+i)
followed by w_i). The **null** start uses empty words.

Word family for length n: every freely reduced word of length n in x,y,X,Y,
one representative per unordered pair {w, w^-1} (so 2*3^(n-1) words).

### Result files (stem `rank3_bf_ms640_b<B>_cap24`, B = 1000 or 10000)

- `<stem>_control.jsonl`: one JSON object per presentation: `pres_id`, `r1`,
  `r2` (strings), `node_budget`, `solved`, `nodes_explored`, `path_length`,
  plus `n2_*` and `null_*` copies of (solved, nodes, path_length) from the
  rank-n solver at rank 2 and from the null rank-3 start.
- `<stem>_L<n>.npz` (n = 1..10): `pres_ids` int32 [640]; `words` str [K]
  (the word family of length n, e.g. 'xY'); `nodes` uint16 [640, K] = nodes
  popped by the rank-3 search of presentation `pres_ids[i]` with word
  `words[k]`; `path_len` int16 [640, K] = length of the solution path, -1 when
  not solved (solved <=> path_len >= 0); `min_total` uint8; `block_seconds`;
  `meta` (JSON string: `node_budget`, `max_relator_length_cap`, ...).
- `<stem>_L<n>_inv.npz` (n = 1..6): same layout for the inverse words (the
  other member of each pair {w, w^-1}), in the same order.
- `<stem>_L<n>_sample.jsonl` and `<stem>_L<n>_sample_paths.jsonl`: a sample of
  solved (presentation, word) pairs. Sample rows carry `pres_id`, `z_word`,
  `r1`, `r2`, `z_relator`, `word_index`, `solved`, `nodes_explored`,
  `path_length`; path rows carry `name` ("ms640_<pres_id>"), `z_word`, `r1`,
  `r2`, `z_relator`, `path_moves` (list of move strings).
- `<stem>_relsub.jsonl`, `<stem>_relsub_paths.jsonl`: the same search for words
  w that are subwords of a relator of the presentation (rows carry
  `family_tag: "relsub"`, `z_word`, `pres_id`, `solved`, `nodes_explored`,
  `path_length`, ...); every solved row has a path row (match on
  `name` + `z_word`).
- `rankn_bf_ms640_b1000_cap24_r<R>.npz` (R = 4, 5): `pres_ids` [640]; `meta`
  JSON with `rank`, `extra_generators` k, `max_word_len` m, `words` (the word
  families of lengths 1..m concatenated); `combos` int16 [C, k] = every multiset
  of k word indices; `nodes`, `path_len` [640, C] as above; `base` int32
  [640, 3] = (solved 0/1, nodes, path_len) of the 2-generator control; `null`
  [640, 3] = the same for the null start.
- `rankn_bf_ms640_b1000_cap24_r<R>_sample_paths.jsonl`: rows `rank`, `pres_id`,
  `index` (column in `combos`), `z_words`, `nodes_explored`, `path_moves`.
- Derived outputs under test (may be read as data, never trusted):
  `<stem>_summary.json`, `<stem>_summary.md`,
  `<stem>_control_vs_start_L<a>-<b>.md`,
  `rankn_bf_ms640_b1000_cap24_r<R>_summary.json`,
  `rankn_bf_ms640_b1000_cap24_r<R>_control_vs_start.md`.

Small real examples of every file type are in `OUT/../schema/` and
`OUT/../post_preview/` (read them to learn the exact formats).
