# Dynamic-rank AC search: definitions and eliminations as moves

Question (from the user, 2026-09-13): every balanced presentation can be
re-expressed at higher rank with every relator of length at most three
(triangulation).  Does searching in that higher-rank space, letting the rank go
up and down by "substitution moves", (a) solve presentations more effectively,
or (b) separate the 124 unsolved Miller–Schupp representatives (U124) from
solved ones, including the very hard solved ones?

Earlier studies on this branch had fixed the rank and the dictionary
(`research/ac19_triangle_theory_20260913`: no progress on hard rows, with the
parity/bigon lemmas as the reason) or used definitions only to shorten
(`research/rank_unbounded_20260912`, `research/u124_rank_3h_20260912`: 0/124
solves, no solved-row control).  This directory does the missing experiment:
definitions and eliminations are *search moves* next to ordinary AC products, the
solve condition is the empty presentation, and the same engine is run as a
rank-two control on the 60-row solved difficulty ladder.

| file | what |
|---|---|
| `dynrank.py` | the engine: words, permutation-canonical states, the three moves (`product`, `define`, `eliminate`), `triangulate`, best-first search, exhaustive closure |
| `verify.py` | independent replayer (own word code): rebuilds every step from the parent and the event, checks the algebraic identity of each move, follows recorded renamings, accepts only paths ending at the empty presentation |
| `test_dynrank.py` | unit tests: canonical forms, renaming invariance against brute force, move identities, define/eliminate round trip, replay + tamper detection, control never changes rank, closure verdicts |
| `run_ladder.py` | panel runner (60-row ladder `benchmark/subsets/benchmark_subset_60.csv`, 124 U124 rows `data/ms_unsolved_reps/aca_124_best.csv`); replays every solved certificate before writing it |
| `make_results.py` | renders the tables in `RESULTS.md` from the JSONL records |
| `records/` | JSONL records with full certificates, logs, the closure pilot |
| `RESULTS.md` | numbers and conclusions |

## The moves and what a certificate proves

A state is a balanced presentation `(R_1..R_n)` on generators `1..n`; relators
are cyclic words up to inversion, the tuple is sorted, and (in the `dyn`/`tri`
arms) generators are renamed to a canonical order by an individualisation–
refinement pass (inversions of generators are not quotiented).

* `product`: `R_i <- rot(R_i) . rot(R_j^±1)`, an ordinary AC move at fixed rank
  (the conjugator is a prefix of `R_i` times a prefix of `R_j`).  Result capped
  at `cap` letters.
* `define`: for a cyclic digram `d = ab` occurring at least twice, add generator
  `h = n+1` with relator `h^-1 ab` and rewrite every relator by its shortest
  tokenisation.  Rank `n -> n+1`.
* `eliminate`: a relator in which generator `g` occurs exactly once, `R = g^e u`,
  is solved for `g`; substitute in the other relators, drop `R`, renumber.  Rank
  `n -> n-1`.  A unit relator is the special case `u` empty, so the empty
  presentation (rank 0) is the solve condition, and the classical "reach `{x,y}`"
  is the special case where only units are eliminated (the `ctrl` arm).

For a presentation of the trivial group both `define` and `eliminate` are
stable AC composites: `define` is a stabilisation followed by AC moves that turn
the relator `h` into `h (ab)^-1` (possible because `ab` lies in the normal
closure of the relators) and then rewrite occurrences of `ab` by multiplying
with conjugates of `h^-1 ab`; `eliminate` is the reverse (rewrite occurrences of
`g` by conjugates of `R`, then AC moves reduce `R` to `g`, then destabilise).
This is Lemma 11 of Shehper et al. (arXiv:2408.15332) as already used on this
branch.  **The AC moves whose existence that argument gives are not expanded**;
a path to the empty presentation is a certificate of *stable* AC-triviality
with those two composite steps taken as primitives, and with at most
`#define` stabilisations in play at once.  `product` steps are elementary and
replayed literally.

## Arms

| arm | moves | cap | total-length ceiling | renaming canonical | start |
|---|---|---:|---|:---:|---|
| `ctrl` | products, eliminate units only | 24 | none | no | rank-two root |
| `dyn` | products, define, eliminate | 8 | `L + 8` | yes | rank-two root |
| `dyn_norelabel` | as `dyn` | 8 | `L + 8` | no | rank-two root |
| `tri` | products, eliminate (no define: fixed dictionary) | 8 | `L + 8` | yes | all-triangle root from `triangulate` (its definitions are prepended to the certificate) |

Priority everywhere is `(total length, longest relator, rank)`; one *pop*
expands one state and generates all its children.  Budget 2,000 pops per row
and arm.  Best-first search is deterministic, so one run at 2,000 pops gives the
result at every smaller budget.

## Reproduce

```sh
cd research/ac_dynamic_rank_20260913
python3 -m pytest -q test_dynrank.py
python3 run_ladder.py --panel ladder --arms ctrl,dyn,dyn_norelabel --pops 2000 --out records/ladder_p2000.jsonl
python3 run_ladder.py --panel ladder --arms tri --pops 2000 --out records/ladder_tri_p2000.jsonl
python3 run_ladder.py --panel u124   --arms dyn --pops 2000 --out records/u124_dyn_p2000.jsonl
python3 verify.py records/*.jsonl
python3 make_results.py records/ladder_p2000.jsonl records/ladder_tri_p2000.jsonl records/u124_dyn_p2000.jsonl > RESULTS_TABLES.md
```
