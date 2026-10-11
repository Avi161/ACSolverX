# acx interfaces

Read this before writing any acx module. Everything here is pinned by
`tests/test_core.py`, `tests/test_spec.py`, `tests/test_replay.py`.

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
  `X=1, Y=2, x=3, y=4` (`to_codes`, `code`). `state_key(rels, n_gen)` is the
  tuple of per-relator code tuples (canonical order, shorter relator first).
  Tuples compare element by element and a proper prefix is the smaller, so at
  2 generators it sorts exactly like main's `(r1_str, r2_str)` and like
  `hcompact`'s `_row_less_h`.
- Fast-engine layout: `to_bool_array(w)` is main's `(n, 2)` bool array
  (`[is_x, positive]`), `from_bool_array` its inverse.

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
or under `[search]`; `cap = "none"` or `0` means `None`; unknown keys raise.
Other modules keep their own frozen config dataclass and nest a `SearchConfig`.

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

## Data (`acx.data`)

`load(name_or_path, ids=None)` for `ms640`, `ms_unsolved`, `1190ms`, `ac19`,
`ac19_extended`, `ac1m` (gz), returning `Row(id, pres, meta)` with `id` = line
index as a string. `load_csv(path_or_name)` for benchmark CSVs (`bench60`,
`ladder60`, ...; needs `r1`, `r2` columns; `id` = `name`, else `pres_id`).
`load_split(path, "holdout")` for split JSONs with `<part>_rows`.

## Tests

`.venv/bin/python -m pytest tests/test_core.py tests/test_spec.py tests/test_replay.py -q`
(about 25 s). `tests/data/greedy_golden.json` is main's baseline golden file.

## Hints for module builders (added by the orchestrator)

- n-generator / SAC transform to relators of length <= 3: it already exists as `triangulate` in
  `origin/claude/vigilant-babbage-nnbuj0:research/ac_dynamic_rank_20260913/dynrank.py`
  (another copy: `research/u124_rank_3h_20260912/high_rank_triangles.py`). Measured: 25/60 bench60
  from the frozen triangle root vs 34/60 at rank two and 42/60 dynamic; 0/4 on hard AC19 rows.
- Reference numbers from the ORIGINAL code (for parity checks):
  `/mnt/project-files/finalized-research-run/work/reference/` (MS640 LENGTH 606/640 and S20_MK2 626/640
  at budget 10,000 cap 24; 554 and 574 at 1,000; per-row CSVs with pops and path length; hfhybrid MS640
  640/640, 25,064 units, 2.4 s warm).
- cov/all-subsets-sweep adds only an exhaustive CoV family (suballpxyb8) that solves nothing the default
  subnc2pxysb family misses; borrow its certificate provenance fields (z_word, pattern, iso_gen,
  iso_index, iso_expr, defining_relator) and dedup by relabel_key. Report:
  `/mnt/project-files/finalized-research-run/work/all_subsets_sweep.md`.
