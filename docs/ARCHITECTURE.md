# Architecture

`run.py` (CLI) -> the package `acx/runner/` (configs, rows, verification, `results/`) -> one method module; `compare.py`
-> the package `acx/report/`. How to use them is in [USAGE.md](USAGE.md); the tests named in each section pin what is
said here.

| module | what | entry point |
|---|---|---|
| `acx.core` | words, presentations, moves, priorities, `SearchConfig`, the cap counter | `Presentation`, `Move`, `SearchConfig` (`step` is in `acx.core.moves`, `CapCount` in `acx.core.capcount`) |
| `acx.search` | best-first search; `spec` (pure Python) and `fast` (numba) backends | `search(pres, cfg) -> Result` |
| `acx.search.fast.kernels` | package of reusable numba kernels: `encode`/`decode`, `expand`, `score`, `children` | used by `hybrid` and `aut` |
| `acx.verify` | `replay` (the only judge), `decode` (S-moves -> elementary moves), `pack` | `replay(pres, path)`, `ReplayError`, `abs_det` |
| `acx.aut` | Whitehead canonical form, numba twin, transport, equivalence-certificate checker | `aut_canon`, `solve_via_aut_min` |
| `acx.cov` | one-shot change of variables (family `subnc2pxysb`, or the exhaustive `suballpxyb8` with `[cov] family`) | `run_cov(pres, CoVConfig)` |
| `acx.hybrid` | cascade + rank-two/higher-rank best-first search, certified | `solve(pres, HybridConfig)` |
| `acx.ngen` | n-generator search, SAC transform to relators of length <= 3, lift, rank-n sweep | `solve(pres, NGenConfig)`, `acx.ngen.sweep` |
| `acx.rl` | optional (torch): the paper's policy as a beam search | `acx.rl.solve.solve(pres)` |
| `acx.data` | datasets, benchmarks, splits by name, your own `.txt`/`.csv`/`.jsonl` files, row selection; `MS(n, w)`, `AK(n)` | `rows(name_or_path)`, `select(rows, spec)`, `parse_presentation` |
| `acx.runner` | `run.py`'s config check, method records, the run folder and its resume, `summary.json` | `load_config`, `run` |
| `acx.report` | `compare.py`'s table and HTML page: `load`, `table`, `charts`, `page` | `load_run`, `markdown`, `html_page` |

Top level: `from acx import Presentation, Move, SearchConfig, search, Result, replay, ReplayError`.

## Words and presentations (`acx.core.words`)

- A **word** is a tuple of nonzero ints: `1=x, 2=y, 3=z, ...`, sign = exponent. `parse("xYy") == (1, -2, 2)`, `fmt` is
  the inverse (generators past the 26th print as `g27`).
- `Presentation(n_gen, rels)` is frozen; `rels` a tuple of words. `Presentation.parse("YYXyx", "Yx")`,
  `.from_flat(ints, n_rel=2)` (the dataset layout), `.strs`, `.reduced(cyclic)`, `.canonical()`, `.normal(cyclic)`,
  `.is_trivial()`.
- `reduce(w, cyclic=True)`: free reduction, then the cyclic tail. `free(w)` is free reduction only.
- **Canonical form**: each relator is the least rotation of itself or its inverse in **Booth order** `Y < y < X < x`
  (`canonical_word`); relators are then sorted by `(length, Booth order)` (`canonical_rels`).
- `Presentation.normal(cyclic)` is `reduced(cyclic).canonical()` repeated until it stops changing (one pass when
  cyclic). It is the state a search starts from and a replay normalises to, so `Result.start` replays on its own.
- **Key order** (the heap tie-break) is a different order, `X < Y < x < y`: `state_key(rels, n_gen)` is the tuple of
  per-relator code tuples, and `state_bytes` is the same order as bytes (what the cap counter and the fast kernels
  compare). At two generators it sorts like the pair of relator strings.
- `conjugators(w, t)` yields every `(sign, c)` with `c^-1 w^sign c == t` (the witness used by transport and certify).

## Moves (`acx.core.moves`)

- **S-move** `Move(i, j, s, k1, k2)` (0-based, `i != j`, `s = +-1`): `r_i <- rotate(r_i, k1) + rotate(r_j**s, k2)`,
  legal only if the seam cancels. `rotate(w, k)[m] == w[m-k]` (`np.roll`). The child is `reduce(..., cyclic)` per
  relator, then `canonical_rels`; indices refer to the **canonical** parent. `from_legacy(target, jsign, k1, k2)` builds
  one from the baseline's 1-based tuple.
- `enumerate_moves(rels)` yields every legal S-move in the order `i -> j -> s(+1, -1) -> k1 -> k2` (the depth tie-break
  depends on it).
- **Elementary / stable moves** are dicts (1-based relators, free reduction only): `{"op":"invert","target":t}`,
  `{"op":"swap"[,"a":1,"b":2]}`, `{"op":"conjugate","target":t,"by":"x"}` (`r_t <- by^-1 r_t by`),
  `{"op":"multiply","target":t,"source":s}` (`r_t <- r_t r_s`), `{"op":"stabilize"}` (AC4: add generator n+1 and
  relator `(n+1,)`), `{"op":"destabilize"}` (AC5: drop the last generator and a relator equal to it).
- A **path** is a list mixing `Move`s and dicts; `step(pres, mv)` applies one. `Trace(pres)` records elementary moves
  (`do`, `conj`, `invert`, `multiply`, `conjugated_multiply`); the decoder, transport (`Emitter`) and the n-generator
  lift write their paths with it. JSON: `encode_path` (S-move -> `[i, j, s, k1, k2]`), `decode_path`.

## Priorities (`acx.core.priority`)

`length` = total length (int). `s20_mk2` = L + 20 S + 2 MK (float, two generators only), accumulated in the order the
fast engine uses so that both backends agree bit for bit. These are the only two priorities
([METHODS.md](METHODS.md) section 6).

## Config (`acx.core.config.SearchConfig`, frozen)

| field | default | meaning |
|---|---|---|
| `priority` | `"length"` | `"length"` or `"s20_mk2"` |
| `cap` | `24` | per-relator cap on generated children; `"none"`/`None` = uncapped ([CAP.md](CAP.md)) |
| `budget` | `10_000` | maximum pops |
| `backend` | `"spec"` | `"spec"` or `"fast"` |
| `capture_path` | `True` | return the path of a solve |
| `cyclic` | `True` | cyclic reduction of children |
| `trace` | `False` | return the popped states (parity tests) |

`SearchConfig.load(toml_path, ["cap=none", "budget=1000"])`: keys at top level or under `[search]`; unknown keys raise.
Other modules keep their own frozen config and nest a `SearchConfig`. Every cap of every config
(`SearchConfig.cap`, `HybridConfig.r2_cap`/`dyn_cap`/`slack`, `CoVConfig.max_len`/`cap_headroom`, the RL `cap`) is read
by `parse_cap`: a positive int or `"none"` (`0` and bools raise; `slack` and `cap_headroom` may be 0). Every switch
(`capture_path`, `cyclic`, `trace`, the runner's `path` and `decode`, `rankn.inverse`) is read by `require_bool`: a
string such as `"False"` raises.

## Search (`acx.search.search(pres, cfg=None, **overrides) -> Result`)

`pres` is a `Presentation` or relator strings. The engine computes `start = pres.normal(cfg.cyclic)`, calls the
backend's `run(start, cfg) -> Result`, and **replays every returned path** with
`acx.verify.replay(pres, path, cyclic=cfg.cyclic, cap=cfg.cap)`. A start with `|det| != 1` is reported unsolved.

`Result` (frozen): `solved`, `pops` (the solving pop counts), `path` (tuple of `Move` from `start`, or `None`),
`start`, `end` (the popped all-length-1 state), `stats`, `trace` (popped states, when `cfg.trace`), `depth` (the solved
state's depth, `None` when unsolved), `path_length` (`len(path)`, or `depth` when no path was captured; identical on both
backends).

`stats` keys that both backends must report **identically** (`PARITY_STATS`): `discovered` (distinct states
inserted, root included), the six cap-counter fields (`cap`, `cap_dropped`, `cap_dropped_min_total`,
`cap_would_pop`, `cap_first_bind`, `cap_needed`; [CAP.md](CAP.md)), `min_total` / `max_total` (over discovered
states), `max_total_expanded` and `max_expanded` (the first popped state of strictly largest total). The engine adds
`backend` and `seconds` (not compared).

### The search, exactly (what `fast` reproduces step for step)

1. Heap entry `(priority(state), depth, state_key(state))`; root depth 0. Keys are unique, so this is a strict total
   order and the pop sequence does not depend on the heap implementation.
2. Loop while the heap is non-empty and `pops < budget`: pop the least entry, `pops += 1`, update `max_expanded` if its
   total is strictly larger, append to `trace`; if every relator has length 1, stop solved.
3. Expand: for each move of `enumerate_moves(state)`, reduce the new relator. If `cap` is set and the new relator
   **or any untouched relator** is longer than `cap`, count it in the cap counter (`cap_dropped += 1`, with the heap
   key it would have had) and skip; this happens before dedup, so every legal move of a state with an over-cap
   untouched relator (an over-cap start) counts once. Otherwise canonicalise; if the key was seen, skip; else record
   `(parent, move)` and push at `depth + 1`. A state's depth and parent are its first discoverer's (no decrease-key).
4. `cap = None`: no rejection and no counting; the fast backend widens or reallocates its buffers instead.
5. `cap_dropped` counts moves, not distinct children. The fast kernel skips a child that is a cyclic cut shift of the
   previous child of the same block (the raw words are conjugate, so it is the same cyclic word); the move is still
   counted. `discovered` also counts states still in the heap when the budget ends.

## Cap counters (`acx.core.capcount`)

One small package every search calls; it compares the heap keys the search passes and knows no heuristic.
`counter.py`: `CapCount(cap)` with `drop(key, total, longest, ident)`, `pop(bar)`, `end(ran_dry, left)` and
`record(prefix)`. `kernels.py` (`cc_drop`, `cc_pop`) and `arrays.py` (`CapArrays`): the numba twin for the fast
engine (parity in `tests/test_capcount.py`). `records.py`: `FIELDS`, `blank()`, `combine()` (searches run one after
another) and `summarize()` (the `caps` block of `summary.json`). The contract is in [CAP.md](CAP.md); `tests/test_cap_invariant.py` pins "count 0 means the same run at any
larger cap" on both backends.

## Verification (`acx.verify`)

`replay(pres, path, cyclic=True, cap=None, normalize=True, require_trivial=True)` returns the list of states and raises
`ReplayError` unless every move is legal, `|det|` of the exponent-sum matrix is 1 at the start and after every move, no
S-move child exceeds `cap`, and the end is trivial (each relator cyclically reduces to one letter, all generators
present). `normalize=True` starts from `pres.normal(cyclic)` (search paths); elementary paths on raw words pass
`normalize=False`. `abs_det(pres)` is the `|det|` it checks. A result counts only after it replays on the presentation
it claims to solve: an aut-assisted solve after transport to the row; a CoV `stable_cert` replays its search leg here
and its transform in `acx.cov.check_cert`, and is reported separately from an `ac_path`.

`decode(pres, path)` / `decode_and_replay` turn S-moves into elementary moves; `pack`/`unpack` are their JSON form
(`I`, `S`, `C`, `M`, `Z`, `D`).

## Fast backend (`acx.search.fast`)

The package: `best_first.py` (the pop loop), `arrays.py` (the state arena), `heap.py`, `dedup.py`, `cap_stats.py` (the
cap counters) and `kernels/`. States are rows of Booth symbols `b = 2 (n - |g|) + (g > 0)` (integer order is Booth order, the inverse is `b ^ 1`),
one byte each, in a flat arena with an int32 heap and an FNV-1a dedup table; paths are int32 `(parent, move)`, so caps
of 128 and above work. Uncapped runs start at the longest start relator and re-lay rows wider on demand. The kernels
(`expand`, `expand_drops`, `score`, `children`, `reduce_buf`, `canon_buf`) are general in generators and relators.
With a cap, the engine counts in two stages (the least dropped score per pop during the search, an exact replay of the
few pops whose drops could win afterwards); `tests/test_fast.py` pins trace equality with `spec`.

## Other methods

Each module keeps a frozen config and returns typed results; `acx.runner.methods` maps them to records (`kind`,
`aut_assisted`, `cost`, `sub_moves`, `elem_moves`, the cap-counter fields; [USAGE.md](USAGE.md) lists every field):

- `acx.aut.solve_via_aut_min(pres, cfg) -> (Result on the representative, elementary path on pres or None)`;
  `transport(pres, phi, path, start)` carries any path through Aut(F2) and replays it (F2 only).
- `acx.cov.run_cov(pres, CoVConfig) -> CoVResult(outcomes, pops, stats)` of `Outcome(kind, image, result, path, cap)`;
  `acx.cov.verify(pres, outcome)`: an `ac_path` replays on the row, a `stable_cert` replays its transform
  (`check_cert`) and its search leg on the image. Modules: `images.py` (`enumerate_images`, `class_key`), `family.py`
  (`FAMILIES` and the rules of each), `substitution.py` (the word operations), `certificate.py`
  (`apply_steps`, `check_cert`), `run.py` (`run_cov`).
- `acx.hybrid.solve(pres, HybridConfig) -> HybridResult(solved, stage, units, steps, kind, path, stats)`; `path` is
  elementary (plus AC4/AC5 for a `stable_cert`), replayed with `normalize=False`; `stats` has the counters of its three
  limits. `acx.hybrid` also exports `certify`, `Aut`, `encode_steps` and `decode_steps`. Modules: `steps.py` (the step
  types, the `Run` that applies them, `encode_steps`/`decode_steps`), `cascade.py` and `pinch.py` (stages A-C and the
  finishing gates), `search.py` (with `frontier.py`, `kernels.py` and `dynrank.py`), `capwatch.py`, `solver.py`
  (`solve`), `elementary.py` and `frame.py` (`certify`: the certificate as elementary moves).
- `acx.ngen.solve(pres, NGenConfig) -> NGenResult(solved, kind, search, sac, moves)`; a SAC solve is lifted to an
  elementary stable path (`stable_cert`). Modules: `sac.py` (the transform), `solver.py` (`solve`, `NGenConfig`,
  `NGenResult`), `lifting.py` (`lift`), and the package `sweep/`, the rank-n brute force ([RANK3.md](RANK3.md)).
- `acx.rl.solve.solve(pres, model, width, steps, alpha, cap) -> Result` (S-moves, `pops` = network evaluations; two
  generators, relators of length <= 24).

The runner is a package, one job per module, and nothing is re-exported but `load_config`, `method_config`, `run`,
`select` (from `acx.data`) and `summarize`:

- `config`: `load_config` checks a config completely before anything is written. `SECTIONS` says which sections a
  method reads (greedy and aut `[search]`, cov `[search]` + `[cov]`, ngen `[search]` + `[ngen]`, hybrid `[hybrid]`,
  rl `[rl]`, rankn `[search]` + `[rankn]`); `method_config(cfg)` builds the method's settings and raises on any other
  section, unknown key or invalid value.
- `methods`: one function per method (`SOLVERS`), returning a record; `output`: the `path` and `fields` options;
  `caps`: the counters of a record and the `caps` block; `summary`: `summary.json` (`COST_UNIT`).
- `rundir`: the run folder. `prepare` writes `config.json` and refuses a folder written under another config, a
  `paths.jsonl` without its `config.json` and a smaller run into a published folder (`write_config`, the first of
  these, is shared with the rank-n sweep); `read_records` reads `paths.jsonl` the same way for the resume and for
  `run.py` (a cut-off last line is skipped, an earlier bad line stops the run); `drop_changed` forgets the records of
  rows that changed or left the input.
- `execute`: `run` picks the rows (`acx.data.select`), resumes an interrupted run (a record counts only for the
  presentation in its `pres`), skips repeated row ids, solves AK(2) once, unrecorded, before the timed rows, and writes
  `results/<name>/{config.json, paths.jsonl, summary.json}`; `rankn` is handed to `acx.ngen.sweep.run`, which also
  refuses a row that is not two-generator, two-relator and a run that would shrink a published summary. A row with
  `|det| != 1`, or whose method raises, is recorded unsolved with an `error`. `summary.json` always covers every
  record in `paths.jsonl`.

## Data (`acx.data`)

`rows(spec)` resolves `DATASETS` (`ms640`, `ms_unsolved`, `1190ms`, `ac19`, `ac19_extended`, `ac1m`; flat-int
`.txt[.gz]`, `id` = line index), `BENCHMARKS` (CSVs: `bench10..60`, `ladder20..500`, `ladder20..300_s20hard`,
`ac19_autmin`, `ac1m_autmin`, `u124`) and `SPLITS` (`ac1m_hard_holdout60`), or a path to a `.txt`, `.csv` or `.jsonl`
file (optionally `.gz`; formats in [USAGE.md](USAGE.md)). `parse_presentation("xxYYY, xyxYXY")` reads one line. Each row
is `Row(id, pres, meta)`. `select(rows, spec)` picks rows by a slice `a:b[:c]` or by ids, as `--rows` does;
`stem_of(path)` is a file's name without the suffixes `rows` reads it by (the run name of `--input`).

## Tests

`pytest` runs the default selection (a few minutes); `pytest -m ""` adds the tests marked `slow` (full
parity sets, AC19 sample, speed). `tests/data/greedy_golden.json` is the baseline's golden file.
