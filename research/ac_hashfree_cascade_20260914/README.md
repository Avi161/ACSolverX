# Hash-free, table-free cascade for the AC19 Aut-minimal census

`hfcascade.py` is a deterministic solver for balanced two-generator presentations that
keeps **no visited set, no hash map and no pattern table**.  Every decision is read off
the current pair of words; the only memory is the certificate path itself.  It was built
to answer one question: how much of the AC19 Aut-minimal census (72,779 rows,
`data/AC19_extended_aut_min.csv`) can such a procedure solve within 1,000 work units,
against the 72,052 rows the census policy (`research/supermoves_20260908/final_policy.py`,
which keeps both a closed set and Baumslag–Solitar spelling tables) solves at the same
budget.  `EXPLAINER.md` describes that policy and the MS-640 cascade it grew from;
`RESULTS.md` has the measurements.

## The procedure

| stage | what it does | memory | charge |
|---|---|---|---|
| A | pair Whitehead descent: apply the Nielsen map (`x->xy, x->xY, y->yx, y->yX`) that most reduces the total cyclic length, while one exists | none | 1 per image evaluation, 1 per accepted map |
| B | relator descent: shorten ONE relator with Nielsen maps, carrying the companion along even when it grows; a relator that reaches length 1 is a primitive donor and its letter is deleted from the companion one substitution at a time; abelianisation (det ±1) forces the residue to be the other generator | none | same, plus 1 per deletion |
| C | pinch cascade: parse a relator as `g^a h^p g^-a h^q` (a generator with exactly two syllables of opposite exponent); its four consequences `g^a h^p -> h^-q g^a`, `g^-a h^-q -> h^p g^-a`, `h^-p g^-a -> g^-a h^q`, `h^q g^a -> g^a h^-p` pinch the companion's g-syllables away whenever the enclosed h-exponent is divisible (an exponent-level dry run decides applicability for free); each rule use is one substitution move; a companion left as `g^s h^r` with `|s|=1` or `|r|=1` is primitive and stage B finishes | none | 1 per rule use |
| D | descent without a closed set: children are all seam-cancelling rotation products `rot(r_i) . rot(r_j^±1)`; engine `beam` keeps the `w` best distinct children of a level (distinctness by sorting), engine `bestfirst` keeps a heap of every generated state and may pop a state twice; the finishing gates of B and C are tried, free preflight first, on every generated child | the parent chain | 1 per expanded state |

Scores available for D: `length` (total length) and `s20` (`L + 20 S + 2 MK`, the
repository's recommended ordering, computed from cyclic blocks).

Engines for D (`engine=`): `beam` and `bestfirst` are the pure-Python references;
`fast` is the same best-first search on the repository's compiled child expansion and
Nielsen/permutation transforms (`experiments/heuristic_search/core/hexpand.py`,
`experiments/search/basis_moves.py`) with a block-sorted closed set checked at pop time
and, with `perms=True`, states canonical under the eight signed generator permutations;
`hybrid` (`hfhybrid.py`) is the fast engine with dynamic-rank moves added to the same
frontier: every popped rank-two state also offers `define` children (a new generator for
a repeated cyclic digram), higher-rank states are expanded with capped products,
`define`, `eliminate` and Nielsen transvections (the moves of
`research/ac_dynamic_rank_20260913`), and a child that returns to rank two re-enters the
fast path.  Signed-permutation canonicalisation is applied when a rank-two state is popped
(once per expansion, the permutation joining that state's step), not to every generated
child; a free precheck on the packed key (a one-letter relator, a single occurrence of a
generator, or exactly four cyclic syllables) decides whether a generated child is handed to
the finishing gates.  The define children of a rank-two state are generated lazily: a placeholder
carrying the priority the best of them would have sits in the higher-rank frontier and is
expanded only if that frontier is served at that priority.  Two frontiers: the rank-two heap ordered by total length and the
higher-rank heap ordered by total length plus `penalty` letters per generator above two
(default 5); the higher-rank heap is served when its best priority is no worse and the
higher-rank pops so far are at most `dyn_ratio` (default 0.5) times the rank-two pops
plus 20, otherwise its states wait.  These two numbers are the solver's only tuned
parameters.  A hybrid certificate without `dyn` steps is an ordinary rank-two AC
certificate (with automorphism transport); one with `dyn` steps proves *stable*
AC-triviality of a trivial-group presentation, because `define`/`eliminate` are the
Lemma-11 composites of arXiv:2408.15332 and are not expanded.  `verify_hybrid` replays
both step kinds with the two independent verifiers.

Certificates use the repository's mixed-step contract (`automorphism` steps carrying a
Nielsen map, `substitution` steps carrying `target_jsign_k1_k2`) and are replayed by
`verify.py`, which shares no code with the solver.  An automorphism step is sound because
the moves after it, transported back by the inverse automorphism, are AC moves on the
original pair, and the terminal basis pair Nielsen-reduces to `(x, y)` by AC moves
(`research/supermoves_20260908/primitive_patterns.md`, section 2).

## Reproduce

```bash
python3 -m unittest research.ac_hashfree_cascade_20260914.test_hfcascade
R=research/ac_hashfree_cascade_20260914/run_census.py
python3 $R --unsolved --engine bestfirst --score length --out records/u727_bf_len.jsonl   # the 727 policy leftovers
python3 $R --sample 2000 --seed 1 --engine bestfirst --score length --out records/s2000.jsonl
python3 $R --engine fast --score length --closed-set sorted --nielsen --perms --workers 4 --no-states --out records/census_fast.jsonl   # all 72,779 rows, rank two
python3 $R --engine hybrid --workers 4 --no-states --out records/census_hybrid.jsonl                            # all 72,779 rows, hybrid (final)
python3 research/ac_hashfree_cascade_20260914/run_ms640.py --out records/ms640_fast.jsonl                        # MS-640 timing, one core, rank-two engine
python3 research/ac_hashfree_cascade_20260914/run_ms640.py --engine hybrid --out records/ms640_hybrid.jsonl      # MS-640 timing, one core, final
python3 research/ac_hashfree_cascade_20260914/verify_all.py records/*.jsonl records/*.jsonl.gz                     # replay every stored certificate
python3 research/ac_hashfree_cascade_20260914/verify.py records/*.jsonl
python3 research/ac_hashfree_cascade_20260914/make_results.py records/*.jsonl
python3 research/ac_hashfree_cascade_20260914/analyse727.py     # structure of the 727 leftovers
```
