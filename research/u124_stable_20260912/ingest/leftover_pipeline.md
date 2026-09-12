# Leftover-solver pipeline (from `claude/ac19-leftover-solver-notebook-6yan6d`)

Branch tip `9f50ff3a`. Campaign discipline, not a theorem source.

## Search engine

- Compact heap search (`hcompact`), packed canonicalisation, 2-bit rows in later
  engine generations.
- Default U124 heuristic: `s20_mk2` = length + 20·syllable + 2·mean-knot.
- Hard rule on that branch: never quote “0 of 124” without both `s20_mk2` @
  10,000,000 **and** `s40_gen` @ 10,000.
- Path capture was off for most of the 10M run. A solve would be recovered by
  a deterministic re-run of that one row with paths on.

## U124 10M result (artifact)

`results/heuristic_search/u124_10m/RESULTS.md`: 124/124 finished, **0 solved**.
14 observed shortenings, **uncertified**. Input table is the **initial** 124
(byte-identical to `aca_124.csv` on proofs), total 2446.

## What to reuse

- Cheap canonicalisation and the leftover hard-tail lists as **development
  stress rows**, not as proof.
- Keep theorem discovery off the search heap. If a search state looks
  promising, freeze the words and hand them to a recognizer/certificate
  compiler.

## What not to repeat

- Another 10M ordinary search on the same initial table.
- Reporting `min_relator_length` without a replayed path as a certified
  ordinary-AC reduction.
