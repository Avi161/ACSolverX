# Architecture

`run.py` (CLI) -> `acx/runner.py` (configs, rows, verification, `results/`) -> one method module.
Everything below is pinned by the tests named in each section.

| module | what | entry point |
|---|---|---|
| `acx.core` | words, presentations, moves, priorities, `SearchConfig` | `Presentation`, `step`, `SearchConfig.load` |
| `acx.search` | best-first greedy; `spec` (pure Python) and `fast` (numba) backends | `search(pres, cfg) -> Result` |
| `acx.search.fast.kernels` | reusable numba kernels: `encode`/`decode`, `expand`, `score`, `children` | used by `hybrid`, `cov`, `ngen` |
| `acx.verify` | `replay` (the only judge), `decode` (S-moves -> elementary moves), `pack` | `replay(pres, path)` |
| `acx.aut` | Whitehead canonical form, numba twin, transport, equivalence-certificate checker | `aut_canon`, `solve_via_aut_min` |
| `acx.cov` | one-shot change of variables (family `subnc2pxysb`) | `run_cov(pres, CoVConfig)` |
| `acx.hybrid` | cascade + rank-two/higher-rank best-first search, certified | `solve(pres, HybridConfig)` |
| `acx.ngen` | n-generator search, SAC transform to relators of length <= 3, lift | `solve(pres, NGenConfig)` |
| `acx.rl` | optional (torch): the 610model policy as a beam search | `acx.rl.solve.solve(pres)` |
| `acx.data` | datasets, benchmarks, splits by name; `MS(n, w)`, `AK(n)` | `rows(name)` |

## Words and presentations (`acx.core.words`)

- A **word** is a tuple of nonzero ints: `1=x, 2=y, 3=z, ...`, sign = exponent.
  `parse("xYy") == (1, -2, 2)`, `fmt` is the inverse.
- `Presentation(n_gen, rels)` is frozen; `rels` a tuple of words.
  `Presentation.parse("YYXyx", "Yx")`, `.from_flat(ints, n_rel=2)` (dataset
  layout), `.strs`, `.total`, `.reduced(cyclic)`, `.canonical()`, `.is_trivial()`.
- `reduce(w, cyclic=True)`: free reduction, then main's guarded cyclic tail.
- **Canonical form**: each relator is the least rotation of itself or its
  inverse in **Booth order** `Y < y < X < x` (`canonical_word`); relators are
  then sorted by `(length, Booth order)` (`canonical_rels`). This is main's
  `canonical_pair_nj`.
- **Key order** (heap tie-break) is a different order: `X < Y < x < y`, codes
  `X=1, Y=2, x=3, y=4`. `state_key(rels, n_gen)` is the
  tuple of per-relator code tuples (canonical order, shorter relator first).
  Tuples compare element by element and a proper prefix is the smaller, so at
  2 generators it sorts exactly like main's `(r1_str, r2_str)` and like
  `hcompact`'s `_row_less_h`.
- `free(w)` is free reduction only; `conjugators(w, t)` yields every `(sign, c)` with
  `c^-1 w^sign c == t` (the conjugacy witness of transport and certify).

## Moves (`acx.core.moves`)

- **S-move** `Move(i, j, s, k1, k2)` (0-based, `i != j`, `s = +-1`):
  `r_i <- rotate(r_i, k1) + rotate(r_j**s, k2)`, legal only if the seam cancels
  (`rotate(r_i,k1)[-1] == -rotate(r_j**s,k2)[0]`). `rotate(w, k)[m] == w[m-k]`
  (main's `np.roll(arr, 2k)`). The child is `reduce(..., cyclic)` per relator,
  then `canonical_rels`. The indices refer to the **canonical** parent.
  Main's `(target, jsign, k1, k2)` is `from_legacy(...)`/`to_legacy(m)`.
- `enumerate_moves(rels)` yields every legal S-move in the order
  `i -> j -> s(+1, -1) -> k1 -> k2` (main's order; the depth tie-break depends on it).
- **Elementary / stable moves** are dicts (1-based relators, free reduction
  only): `{"op":"invert","target":t}`, `{"op":"swap"[,"a":1,"b":2]}`,
  `{"op":"conjugate","target":t,"by":"x"}` (`r_t <- by^-1 r_t by`),
  `{"op":"multiply","target":t,"source":s}` (`r_t <- r_t r_s`),
  `{"op":"stabilize"}` (AC4: add generator n+1 and relator `(n+1,)`),
  `{"op":"destabilize"}` (AC5: drop the last generator and a relator equal to
  it; it must occur nowhere else).
- A **path** is a list mixing `Move`s and dicts. `step(pres, mv)` applies one.
  `Trace(pres)` emits elementary moves (`do`, `conj` by a word, `invert`, `multiply`), each applied
  by `elementary_step`; the decoder, transport (`Emitter`) and lift write their paths with it.
  JSON: `encode_path` (S-move -> `[i, j, s, k1, k2]`), `decode_path` (also reads
  main's `"t_j_k1_k2"` strings).

## Priorities (`acx.core.priority`)

`length` = total length (int). `s20_mk2` = L + 20 S + 2 MK (float, two
generators only), computed as `acc=0.0; acc+=1.0*L; acc+=2.0*MK; acc+=20.0*S`
(the fast engine's order; bit-identical). Definitions in the module docstring.
No other priority exists.

## Config (`acx.core.config.SearchConfig`, frozen)

| field | default | meaning |
|---|---|---|
| `priority` | `"length"` | `"length"` or `"s20_mk2"` |
| `cap` | `24` | per-relator cap on generated children; `None` = uncapped |
| `budget` | `10_000` | maximum pops |
| `backend` | `"spec"` | `"spec"` or `"fast"` |
| `capture_path` | `True` | return the path of a solve |
| `cyclic` | `True` | cyclic reduction of children |
| `trace` | `False` | return the popped states (parity tests) |

`SearchConfig.load(toml_path, ["cap=none", "budget=1000"])`: keys at top level
or under `[search]`; `cap = "none"` means `None`; unknown keys raise.
Other modules keep their own frozen config dataclass and nest a `SearchConfig`.
Every cap of every config (`SearchConfig.cap`, `HybridConfig.r2_cap`/`dyn_cap`,
`CoVConfig.max_len`/`cap_headroom`, the RL `cap`) is read by `parse_cap`: a positive
int or `"none"` (`0` and bools raise).

## Search (`acx.search.search(pres, cfg=None, **overrides) -> Result`)

`pres` is a `Presentation` or relator strings. The engine computes
`start = pres.reduced(cfg.cyclic).canonical()`, calls the backend's
`run(start, cfg) -> Result`, and **replays every returned path** with
`acx.verify.replay(pres, path, cyclic=cfg.cyclic, cap=cfg.cap)` (raises if invalid).

`Result` (frozen): `solved`, `pops` (main's `nodes_explored`; the solving pop
counts), `path` (tuple of `Move` from `start`, or `None` when unsolved or
`capture_path=False`), `start`, `end` (the popped all-length-1 state or
`None`), `stats` (dict), `trace` (tuple of popped states as tuples of relator
strings, when `cfg.trace`), `path_length`.

`stats` keys every backend must report **identically** (`PARITY_STATS`):
`discovered` (distinct states inserted, root included), `cap_rejected`,
`min_total` / `max_total` (over discovered states), `max_total_expanded` and
`max_expanded` (the first popped state of strictly largest total, as strings).
The engine adds `backend` and `seconds` (not compared).

### The search, exactly (what `fast` must reproduce step for step)

1. Heap entry `(priority(state), depth, state_key(state))`; root depth 0.
   This is a strict total order (keys are unique), so no insertion counter is
   needed and the pop sequence is independent of the heap implementation.
2. Loop while the heap is non-empty and `pops < budget`: pop the least entry,
   `pops += 1`, update `max_expanded` if its total is strictly larger, append
   to `trace`; if every relator has length 1, stop solved.
3. Expand: for each move of `enumerate_moves(state)`: reduce the new relator.
   If `cap` is set and the new relator **or any untouched relator** is longer
   than `cap`, `cap_rejected += 1` and skip (before canonicalisation and
   dedup; so every legal S-move of an expanded state whose child is over the
   cap counts once, including all moves of a state whose untouched relator is
   over the cap, e.g. an over-cap start). Otherwise canonicalise; if the key
   was seen, skip; else record `(parent, move)` and push at `depth + 1`.
   A state's depth and parent are its first discoverer's (no decrease-key).
4. `cap=None`: no rejection; the fast backend widens or reallocates its buffers
   instead of rejecting.
5. Counting for a numba backend. `cap_rejected` counts moves, not distinct
   children. A kernel that skips a whole relator block because the untouched
   relator exceeds the cap (`hexpand`'s `len_oth > cap: continue`) must still
   add the number of seam-legal moves of that block. Skipping a child whose
   conjugacy-chain predecessor was emitted (`hexpand`'s cyclic cut-shift skip)
   is exact, because a rejected child is never marked emitted. `discovered`
   also counts states still in the heap when the budget ends.

## Verification (`acx.verify`)

`replay(pres, path, cyclic=True, cap=None, normalize=True, require_trivial=True)`
returns the list of states and raises `ReplayError` unless every move is legal,
`|det|` of the exponent-sum matrix is 1 at the start and after every move, no
S-move child exceeds `cap`, and the end is trivial (each relator cyclically
reduces to one letter, all generators present). `normalize=True` starts from
the reduced canonical form (search paths); elementary paths acting on raw words
pass `normalize=False`. `is_valid(...)` is the boolean form. A result counts
only after it replays on the presentation it claims to solve: an aut-assisted
solve after transport to the original row; a CoV `stable_cert` replays its
search leg here and its transform in the CoV module, and is reported
separately from an `ac_path`.

## Fast backend (`acx.search.fast`)

States are rows of Booth symbols `b = 2 (n - |g|) + (g > 0)` (integer order is
Booth order, the inverse is `b ^ 1`), one byte each, in a flat arena with an
int32 heap and an FNV-1a dedup table; paths are int32 `(parent, move)`, so caps
of 128 and above work. Uncapped runs start at the longest start relator and
re-lay rows wider on demand. The kernels (`expand`, `score`, `children`) are
general in generators and relators; `tests/test_fast.py` pins trace equality with
`spec`.

## Other methods

Each module keeps a frozen config and returns typed results; `acx.runner` maps
them to records (`kind`, `aut_assisted`, `cost`, `sub_moves`, `elem_moves`):

- `acx.aut.solve_via_aut_min(pres, cfg) -> (Result on the rep, elementary path on pres or None)`;
  `transport(pres, phi, path, start)` carries any path through Aut(F2) and replays it (F2 only).
- `acx.cov.run_cov(pres, CoVConfig) -> CoVResult` of `Outcome(kind, image, result, path, cap)`;
  `acx.cov.verify(pres, outcome)`: an `ac_path` replays on the row, a `stable_cert`
  replays its transform (`check_cert`) and its search leg on the image.
- `acx.hybrid.solve(pres, HybridConfig) -> HybridResult(solved, stage, units, steps, kind, path)`;
  `path` is elementary (plus AC4/AC5 for a `stable_cert`), replayed with `normalize=False`.
- `acx.ngen.solve(pres, NGenConfig) -> NGenResult(kind, search, sac, moves)`; a SAC solve is
  lifted to an elementary stable path (`stable_cert`).
- `acx.rl.solve.solve(pres, model, width, steps, alpha, cap) -> Result` (S-moves, `pops` =
  network evaluations; two generators, relators of length <= 24).

`acx.runner.load_config` checks a config completely before anything is written: a method reads only its
sections (`SECTIONS`: greedy and aut `[search]`, cov `[search]` + `[cov]`, ngen `[search]` + `[ngen]`, hybrid
`[hybrid]`, rl `[rl]`), and `method_config(cfg)` builds the method's settings, raising on any other section,
unknown key or invalid value.

## Data (`acx.data`)

`rows(name)` resolves `DATASETS` (`ms640`, `ms_unsolved`, `1190ms`, `ac19`,
`ac19_extended`, `ac1m`; flat-int `.txt[.gz]`, `id` = line index), `BENCHMARKS`
(CSVs with `r1`, `r2`, `.gz` allowed: `bench10..60`, `ladder20..500`,
`ladder20..300_s20hard`, `ac19_autmin`, `ac1m_autmin`, `u124`; `id` = `name`,
else `pres_id`) and `SPLITS` (`ac1m_hard_holdout60`). Each row is `Row(id, pres, meta)`.

## Tests

`pytest` runs the default selection (about 2 minutes on one core); `pytest -m ""`
adds the tests marked `slow` (full parity sets, AC19 sample, speed). `tests/data/greedy_golden.json`
is main's baseline golden file.
