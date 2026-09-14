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
python3 $R --engine bestfirst --score length --workers 4 --no-states --out records/census.jsonl  # all 72,779 rows
python3 research/ac_hashfree_cascade_20260914/verify.py records/*.jsonl
python3 research/ac_hashfree_cascade_20260914/make_results.py records/*.jsonl
python3 research/ac_hashfree_cascade_20260914/analyse727.py     # structure of the 727 leftovers
```
