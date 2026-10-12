# The relator-length cap and its counters

A best-first search keeps a child state only if both of its relators are at most `cap` letters long. The cap bounds
the size of the search graph, so a search at cap 24 and a search at cap 48 are different searches. This note says how
`acx` makes sure the cap never decides silently what the search does. For the search itself see
[METHODS.md](METHODS.md) section 4 and 5; for the interfaces see [ARCHITECTURE.md](ARCHITECTURE.md).

## The cap is a config value

`SearchConfig.cap` (TOML `cap = 24` under `[search]`, or `--set search.cap=48`) is a positive integer or `"none"`
(`none` = uncapped; the default is 24). Nothing in the code fixes it. Every other limit of the same kind is read the
same way (`acx.core.config.parse_cap`): the hybrid's `r2_cap` (also `"parent"`), `dyn_cap` and `slack`, CoV's
`max_len` and `cap_headroom`, the RL beam's `cap`. `run.py` rejects a section that the method does not read, so a cap
cannot be set and then ignored.

An uncapped run drops nothing and keeps no counter: its record has `cap: null`, `cap_dropped: 0` and the other fields
`null`/`0`. It searches a larger graph, so each pop costs more; how much more is measured in
[PERFORMANCE.md](PERFORMANCE.md).

## What is counted, and by whom

A cap drops a child and the search never sees it. The question for a reader is: **would the search have popped that
child, before it finished, had the cap been larger?** If yes, the cap changed the run; if never, it did not.

The answer needs only the order in which the search pops states, and that order is whatever the active heuristic says
(`LENGTH`, `S20_MK2`, or one added later). So the counting is one small package, `acx/core/capcount/`, which
**knows no heuristic**. Every search (the `spec` and `fast` backends of `acx.search`, the hybrid, CoV, the RL beam,
and the n-generator and rank-n searches through `acx.search`) calls it with scores only:

```python
cc = CapCount(cap)
cc.drop(key, total, longest, ident)   # the cap dropped a child; key = the heap key the search would have pushed it under
cc.pop(bar)                           # the search popped an entry with key `bar` (called before it expands)
cc.end(ran_dry, left)                 # the search stopped
cc.record()                           # -> the six fields below
```

`key` is the full heap key of the active priority, for example `(priority, depth, state_bytes)`; the module compares
keys with `<` and nothing else. The fast backend (numba) uses a jitted twin of the same logic
(`acx/core/capcount/kernels.py`, driven by `CapArrays` in `acx/core/capcount/arrays.py`), pinned to `CapCount` by
`tests/test_capcount.py`.

## The six fields

Every search record carries these (`acx.core.capcount.FIELDS`; `cap_` is renamed `dyn_cap_` or `slack_` for the
hybrid's other limits, which count a little differently: see below):

| field | meaning |
|---|---|
| `cap` | the cap watched (`null` = uncapped; the hybrid's `r2_cap` default is the string `"parent"`) |
| `cap_dropped` | children not pushed because a relator is over the cap, one per move (a state reached by several moves counts several times) |
| `cap_dropped_min_total` | the least total relator length among the dropped children (`null` if none) |
| `cap_would_pop` | distinct dropped states that the search would have popped before it stopped (see below) |
| `cap_first_bind` | the pop number (1 = the start) of the first pop at which a dropped state would have gone first; `pops + 1` if the queue ran dry; `null` iff `cap_would_pop` is 0 |
| `cap_needed` | the smallest cap at which the search changes: the least longest-relator among the would-pop states; `null` iff `cap_would_pop` is 0 |

`summary.json` has a `caps` block with one entry per counter prefix the method reports (`cap`; the hybrid also
`dyn_cap` and `slack`): the cap(s), `rows`, `rows_dropped` (rows where the cap dropped anything), `rows_would_pop`
and `raise_ids` (the rows where raising the cap changes the search, up to 100 ids), the sums `dropped` and
`would_pop`, and `dropped_min_total`, `first_bind_min`, `needed_min`, `needed_max`. CoV adds `cap_legs_bound`, the
number of searches of its rows in which the cap bound.

## What "would have been popped" means, and the guarantee

The search pops entries in increasing heap-key order. A dropped child has the key it would have been pushed under. It
**would have been popped** if its key sorts before the key of a pop that really happened, or, if the queue ran dry,
if it would have filled the budget that was left. Ties cannot occur (the key ends in the state itself). A state is
judged once, under the key of the first move that dropped it, matching how the search dedups states when it first
discovers them.

The guarantee, for the `spec` and `fast` searches, exactly:

- **`cap_would_pop == 0`**: the same run at any larger cap pops the same states in the same order and returns the
  same path. The cap did not matter.
- **`cap_would_pop > 0`**: the run at a cap of at least `cap_needed` differs from this one; at any cap below
  `cap_needed` it is the same run.

Note that the guarantee does not say "the same row is solved": a different pop order can solve a row in a few more or
fewer pops. On MS640 at cap 24, S20_MK2 row 527 solves in 7,458 pops (`cap_would_pop` 21, `cap_first_bind` 1,653,
`cap_needed` 25) and in 7,479 pops at cap 25 or uncapped, with the same path length 120.

Per-run counts are in [RESULTS.md](RESULTS.md), section "Relator-length cap".

## The hybrid's three limits

The hybrid ([METHODS.md](METHODS.md) section 10) cuts its search in three places, each with its own counter:

| prefix | limit | default | `_needed` is |
|---|---|---|---|
| `cap_*` | `r2_cap`, the longest relator of a rank-two child | `"parent"` | the child's longest relator |
| `dyn_cap_*` | `dyn_cap`, the longest relator a higher-rank product or elimination may create | 8 | the child's longest relator |
| `slack_*` | `slack`, how far above the search root's total length a higher-rank state may be | 8 | the child's total minus the root's total (in slack units) |

- The default `r2_cap = "parent"` (a child relator may not exceed the parent's total length) can never reject, because
  a child relator has at most `l_i + l_j - 2` letters, below the parent's total. An integer `r2_cap` does reject, and
  counting its drops is slower. `slack = "none"` lifts the ceiling.
- The counts are of what the hybrid tells apart: `*_dropped` counts classes of dropped children (plus the tail moves of
  the solving pop), not moves, and `*_would_pop` counts distinct canonical pairs (at rank two, up to
  a signed permutation of the generators, as the search dedups). `*_first_bind` is a work unit of the search; the
  cascade's units before it are not counted.
- The hybrid has two queues (rank two, higher rank), so a dropped child waits in a pool for its queue and is compared
  with the key of whichever pop would have served that queue; a dropped rank-two child that the finishing gates would
  act on counts at once. Its counts are first order: a dropped state is judged against the run that happened. **Zero
  in all three means the same run at any larger limit; a non-zero count says only that the run may change.**
- Example: `ac19_239` with the default limits solves in 150 units with `dyn_cap_would_pop` > 0, first bind at unit 110
  and `dyn_cap_needed` 11. At `dyn_cap` 11 it solves in 153 units and reads `dyn_cap_needed` 13, so the next raise
  changes it again; at 13 the count is 0 (154 units).

## CoV and RL

- **CoV** (change of variables) runs one search per image, and a row is those searches one after another. The row's
  record sums `cap_dropped` and `cap_would_pop` over the legs, takes the least `cap_dropped_min_total` and
  `cap_needed`, and numbers `cap_first_bind` in the row's pops. `cap` is `search.cap`; images are searched at
  `max(cap, longest written relator + cap_headroom)`. `max_len`
  (images longer than 239 letters do not exist in the family) selects which images are searched, and is not a
  search cap, so it is not counted.
- **RL beam search** has no queue. The beam picks its children from the network's scores, then the cap removes some,
  so every picked child over the cap took a beam slot a larger cap would have used: `cap_would_pop == cap_dropped`.
  `cap_first_bind` is the first step that picked one, and the cap is at most 24, the policy's input width, so a zero
  means the same run at every cap up to 24.
- **n-generator and rank-n searches** use `acx.search`, so they report the six fields unchanged. The rank-n sweep
  stores the five counters per start (`-1` = none); its summary counts the searches in which the cap dropped a
  child and those in which it could bind ([RANK3.md](RANK3.md)).

## What to do when the count is non-zero

1. Read `cap_needed` (or `dyn_cap_needed`, `slack_needed`, per limit). It is the smallest value at which the run
   changes.
2. Rerun the rows in `caps.cap.raise_ids` of `summary.json` with that limit raised to the needed value, for example
   `python run.py --config configs/s20_mk2_fast.toml --rows 527 --set search.cap=25 --set name=row527_cap25`, and
   read the new counters. When `cap_would_pop` is 0 at the new value, the run no longer depends on the cap; if it is still non-zero, raise again.
3. Quote a result at the cap it was run at (the result tables list it), and name the rows with `would_pop > 0` at
   that cap.

A non-zero count never makes a record wrong: every path is replayed on the row it claims to solve, under the cap it
was found at. The counters only say whether the run depends on that cap.
