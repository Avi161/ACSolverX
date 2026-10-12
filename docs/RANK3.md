# Rank-3 and rank-n brute force, and the n-generator package

Add a generator `z` and the relator `Z.w` to a two-generator presentation, for every freely reduced word `w`, and
search each stabilised start with the ordinary best-first search. It answers one question: does knowing the right
word for each presentation make greedy cheaper? Ported from `origin/rank3/brute-force-baseline` (commit `068ea77d`,
`experiments/stable_ac/rank3/`). The sweep is `acx/ngen/sweep.py`; the search is `acx.search.search`, unchanged.

## What is searched

- **Start.** `<x, y, z | r1, r2, Z.w>` for `w` in `x, y` (rank 3); `<x, y, z1, z2 | r1, r2, Z1.w1, Z2.w2>` for every
  multiset of two words (rank 4); three words for rank 5. `extra` = 1, 2, 3 in `[rankn]`.
- **Words.** All freely reduced words of length `min_len..max_len` over `x, y, X, Y`, one of each pair `{w, w^-1}`:
  `2 * 3**(n-1)` of length `n`, in a fixed depth-first order (`reduced_words`). `inverse = true` searches `w^-1`
  instead (the same start up to renaming `z`; only heap ties can differ).
- **Control and null stabilisation.** Per row the 2-generator search and the start with empty words (`Z1, .., Zk`)
  run too and must agree on (solved, pops, path length); otherwise the row is refused.
- **Priority** is LENGTH. `S20_MK2` is defined for two generators only, so the sweep refuses it. The cap is the
  config's (`cap = 24`, an int, or `"none"`); it never decides a pop silently, because the cap counters
  (`acx.core.capcount`, [METHODS](METHODS.md)) record every dropped child and whether it would have been popped.
- **What a solve means.** A solved stabilised start certifies *stable* AC triviality of the row only after a lift
  (see the next section). The sweep reports "solved from the stabilised start"; it never writes an `ac_path` or a
  `stable_cert`.

## Run

```
python run.py --config configs/rank3_bf.toml                  # MS640, words of length 1-4, budget 1,000, cap 24
python run.py --config configs/rank3_bf.toml --rows 0:40      # a smoke, seconds
python run.py --config configs/rank4_bf.toml --rows 7:640:40  # a rank-4 slice (a full run is ~2 core-hours)
python -m acx.ngen.sweep --config configs/rank5_bf.toml --verify 100   # the same config, then 100 cells re-run on the other backend
```

`run.py` loads the config with the runner (method `rankn`, `acx.runner.method_config`), which refuses bad keys and
S20_MK2 before anything is written; the runner then hands the run to `acx.ngen.sweep.run`.

`[search]` is a `SearchConfig` (priority `length`, `budget <= 65535`, `1 + max_len <= cap`); `[rankn]` holds `extra`,
`min_len`, `max_len`, `inverse`, `sample`. Unknown keys and invalid values are errors at load.

Results go to `results/<name>/`: `config.json`, `rows/<id>.npz` (one atomic file per row, so a killed run resumes;
a file from another config is an error, never merged), `summary.json`, `summary.md`. A row file holds, per start,
`nodes` (pops), `path_len` (-1 unsolved), `min_total`, the five cap counters `cap_dropped`, `cap_dropped_min_total`,
`cap_would_pop`, `cap_first_bind`, `cap_needed` (-1 = none), plus the control and null records and a deterministic
sample of solved paths (`sample`). **The row files are large; keep them out of git** (`results/*/rows/`).

`sweep.verify(dir, recheck=N)` (also `--verify N`) checks: control equals null stabilisation (and their cap counters,
scores shifted by `extra`), shapes and ranges, cap-counter rules, every stored path through `acx.verify.replay`, and
`N` random cells re-run on the other backend. Measured here (3 workers): lengths 1-3 over all of MS640 (16,640 searches) take 4.6 minutes, length 4 alone
(34,560 searches) about 9 minutes. Length 10 (37.8 M searches) is a cluster job.

## Reproduction against the baseline's stored results

Budget 1,000, cap 24, MS640, fast backend; every cell compared with the baseline's `rank3_bf_ms640_b1000_cap24_*.npz`
and `rankn_bf_ms640_b1000_cap24_r{4,5}.npz` on the branch (`nodes`, `path_len`, `min_total`, `cap_dropped`, and the
control's solved/pops/path length):

| slice | cells | solved | mismatches |
|---|---|---|---|
| control, 640 rows (also equal to the null stabilisation) | 640 | 554 | 0 |
| rank 3, lengths 1-3 | 16,640 | 11,438 | 0 |
| rank 3, length 4 | 34,560 | 23,696 | 0 |
| rank 3, lengths 1-2, `inverse = true` | 5,120 | - | 0 |
| rank 4, 16 rows (`--rows 7:640:40`) | 5,616 | 2,899 | 0 |
| rank 5, 16 rows (`--rows 0:640:40`) | 1,920 | 1,150 | 0 |

Checked on the current code (`nodes`, `path_len`, `min_total`, `cap_dropped`, `cap_dropped_min_total`; the rank 4 and 5
slices compare `nodes`, `path_len` and the control and null records, since the baseline stores no cap counters for
them): lengths 1-3 over all MS640, length 4 over all MS640, `inverse = true` lengths 1-2 over all MS640, and the two
rank-4 and rank-5 slices: 0 mismatches in every cell.

The summary tables agree too (solved by some word up to length 1/2/3/4: 403 / 472 / 516 / 540; a random word solves
60.1% / 68.4% / 69.8% / 68.6% of its starts; lost 151 / 82 / 38 / 18). The cap dropped a child in 4 of the 16,640
searches of lengths 1-3 (the same 4 cells as the baseline, the same smallest dropped total) and could bind in none.
The baseline's `cap_first_bind` is a conservative total-length test; acx's counters are exact (strict full heap key,
first-drop keys), so a baseline bind may be a tie that acx clears, and a baseline null implies an acx null.

Published numbers of the baseline (MS640, budget 1,000, cap 24; `benchmark/rank3_bf/` holds its tables): control 554;
the oracle over lengths 1-10 solves 578 (24 gained, 0 lost); the best single word `yXYYYxyyy` solves 528; rank 4: 506
solved by some start, rank 5: 416; the cap dropped a child in 45,315 of 4,960,112 counted searches and could bind in
none.

## Differences from the baseline

- The search is `acx.search` (spec and fast), not `solvern` / `solvern_fast`: the same canonical form, tie-break, move
  order and cap rule, pop for pop with cyclic reduction on. With `cyclic = false` acx re-reduces the untouched relators
  at every pop (the baseline's `solvern` kept them as stored); the sweep ships `cyclic = true`.
- Not ported: the 2,187-word block shards, the relator-subword arm (needs the change-of-variables word family), and
  the shortlex, cross-validation and class-view analyses.
- Pops are stored as `uint16` (budget at most 65,535); the minimum total is stored exactly (the baseline clipped it to
  a byte).

## The n-generator package (`acx.ngen`)

Cyclic reduction (`cyclic = false`): the search starts from `Presentation.normal(cyclic)`, and a presentation with no
definition is searched as it is (`solve` does not search its cyclic reduction); with `cyclic = false` the cyclic
reduction of an input can change its relators by conjugation, so the path would not replay on the input otherwise.

`solve(pres, NGenConfig)` searches a presentation of any rank with `acx.search.search` (spec and fast backends).

- `sac = true` (default): triangulate (`acx.ngen.sac`), search the root, and on a solve lift the path (`acx.ngen.lift`)
  to elementary stable AC moves: a `stable_cert`. A presentation whose relators are already of length <= 3 needs no
  definition and yields an `ac_path`.
- `sac = false`: search the presentation itself; a solve is an `ac_path`, replayed with the search's normal form.
- Refused up front: SAC with any priority but LENGTH (raised when the config is built, so `run.py` refuses
  `configs/ngen_sac.toml --set search.priority=s20_mk2` before it writes a result); more than 26 generators (the
  search names generators by the letters of `acx.core.words.GEN_CHARS`, so a larger root is refused before the
  search rather than failing after it). The 26-generator limit is a stopgap: lifting it needs the letter names in
  `acx.core.words` and `acx.search` changed, which this package does not own.

### The stable-AC transform (`acx.ngen.sac`)

A *definition* adds a generator `h` with the relator `d^-1 h` for a cyclic digram `d = ab`, and rewrites every relator
by replacing `ab` with `h` (and `BA` with `H`) wherever that shortens it. Each definition shortens some relator longer
than 3, so repeating it terminates; the rank grows by one per definition.

- The digram defined next has the most cyclic occurrences over all relators (ties: the most occurrences inside
  relators longer than 3, then the smaller digram).
- A relator is rewritten as its shortest rewriting (`tokenize`, ties: the smaller word) over the rotations of the
  relator, oriented as the source's canonical form: the least rotation in int order of the relator or of its inverse.
  This reproduces the tie-breaks of the source on the MS640, AC19 and 1190ms rows (`tests/test_ngen.py` pins a sample).
- Relators keep their positions, so the lift can track them.

A definition is a stabilisation (generator `h`, relator `h`), the automorphism `h -> d^-1 h` and AC moves (multiplying
by conjugates of the defining relator). So a solve of the root proves *stable* AC triviality of the source.

### The lift (`acx.ngen.lift`)

Let `t_k = d_k^-1 h_k` be the k-th defining relator, `U = (r.., h_1..h_m)` the source after `m` stabilisations and
`T = (r.., t_1..t_m)`. Let `beta` fix the source generators and send `h_k` to `beta(d_k) h_k`. It is an automorphism
with `beta(t_k) = h_k`, so `beta(T) = U`, and AC moves are equivariant under it. The elementary path from `T` is:

1. **undefine**, definition by definition: in every relator of the current state, invert and rotate as
   `sac.rewrite` chose, then turn each `d` into `h_k` by multiplying with `Q^-1 t_k Q` (`Q` the rest of the word), and
   each `d^-1` into `H_k` by multiplying with the conjugate of `t_k^-1`. This reaches `sac.root` from `T`.
2. **solve** the root with the search's S-moves, each expanded as in `acx.aut.transport` (align to the canonical form,
   conjugate the source, multiply, conjugate back). The end is the basis `(x, y, h_1, .., h_m)` up to `beta`.
3. **clean**: the relator of `h_j` is `beta(d_j) h_j`; its letters before `h_j` are deleted one at a time by
   multiplying with a conjugate of the unit relator of that letter.
4. **destabilize** `m` times.

The moves are then replayed on the source (`acx.verify.replay`, `normalize=False`) before they are returned. The length
is large (a conjugation costs one move per letter, and `beta(h_k)` grows with the nesting of the definitions) but
deterministic; nothing searches.
