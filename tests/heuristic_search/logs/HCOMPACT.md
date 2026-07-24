# HCOMPACT — the tuned ordering at ~78 bytes per state

Engineering, not an experiment: no new search claims, only the same search made to fit. `experiments/heuristic_search/hcompact.py` runs the recommended ordering on `greedy_compact`'s packed layout — nibble arena, int32 binary heap, open-addressing visited table — plus two arrays the heuristic needs (`score: float64`, `seg: uint8`).

## The identity claim, and how it is proven

`greedy_search_hcompact` is **pop-for-pop the same search** as `greedy_search_h(keep_path=False)`, not merely the same solve rate. The argument has three legs, each verified rather than assumed:

1. **Bit-identical scores.** Children are generated and scored by calling the *same* numba kernel `hsolve` calls (`expand_and_score_nj`); the root is scored by the *same* Python expression `hsolve` uses for its root. No `fastmath` anywhere in the chain (grepped), so identical operation sequences give identical IEEE doubles, and `score[a] != score[b]` resolves exactly where `hsolve`'s does.
2. **The tie-break sorts like the key.** The comparator is (seg, score, depth, row-memcmp), mirroring `hsolve`'s heap tuple `((seg, score), depth, key)`. The arena row memcmp-sorts exactly like the packed key — `greedy_compact`'s pinned invariant — and the two code tables agree (`hfast._pack`'s `(2,4,1,3)` ≡ `greedy_compact._code_of`).
3. **Same discovery order** (same kernel, same enumeration), so `depth` and the first-seen statistics land on the same states. One deliberate divergence from `greedy_compact`: min/max on discovery use `hsolve`'s two independent `if`s, not the heavy solver's `elif`.

**Evidence: 880 paired searches, 0 mismatches** (`verify_hcompact.py`) — all 66 benchmark rows + 12 unsolved-124 rows (full-budget burns, worst case for tie-break traffic), budgets 500 and 1,000, comparing every scalar field **and the first-seen min/max/expanded relator strings**, which pin discovery order (they update on strict inequality only, so they are deterministic — unlike the heavy solver's set-tie-broken strings, which the repo rightly forbids asserting). Five configs, chosen so **no branch ships unverified**: the three shipped orderings plus a depth-carrying config (exercises the `sc += seg_depth·nd` post-processing; 75 solves under it) and a no-INF-segment config (exercises the `seg = n_seg` fallback; 55 solves). A further 100 pairs run with the chunk size shrunk to 200 so the njit↔Python re-entry — never crossed at budgets ≤1,000 under the production chunk of 1,024 — is crossed four times per search. The grow-copy-rehash path fired repeatedly inside the sweep and is forced explicitly by `tests/heuristic_search/test_hcompact.py::test_growth_preserves_the_search` (`reserve_states=1`).

**One honest caveat on what the strings prove** (from the adversarial review): the first-seen strings pin discovery order only *up to the pops that lock each extremal length*; a tie-break divergence after that lock would be invisible on a budget-exhausted unsolved row. The sharp guard is **solved** rows — a late divergence moves `nodes_explored`/`path_length` — which is why the verifier asserts a nonzero solve count *per shipped ordering* (recommended 80, lean 80, baseline 55 across the matrix) rather than in aggregate, and why the unsolved-124 tail leans on the uniqueness proof rather than the strings alone.

The plan for this port was adversarially reviewed before shipping (independent Opus advisor, instructed to break the correctness argument). Its one true correctness trap — transcribing the packed key verbatim into nibbles, which mis-aligns r2 against the byte-aligned root and breaks *dedup*, not just ordering — is exactly what the separator-scan packer avoids; its remaining findings (depth/fallback branches unverified, chunk boundary never crossed at test budgets, grow must carry `score`/`seg`) are each closed by a named case above.

## What it buys

| | `hsolve` keep_path=True | `hsolve` keep_path=False | `hcompact` |
|---|---|---|---|
| memory | 36.5 kB/node | 24 kB/node | **~78 B/state** (≈ 8.6 kB/node at 110 states/pop) |
| 10⁶-node search | ~36.5 GB | ~24 GB | **~7 GB reserved** |
| ceiling on 51 GB | ~1.4M | ~2M | **~5M** |
| speed (1k burns, the 124) | — | 2,583 pops/s | **2,931 pops/s** (+13%) |
| certificate | yes | recovered by re-run | recovered by re-run |

Reservation for 10⁶ at cap 48, measured from the real containers: **6.97 GiB, 78.2 B/state** over 95.7M slots. At 3×10⁶ the reservation is ~22 GB — comfortable on 51 GB; ~5×10⁶ (~36 GB) is the new ceiling. Wall-clock does not shrink: at the Colab-measured 500–700 pops/s a 3×10⁶ burn is **71–100 min per presentation**, so budget hours, not RAM, is now the binding constraint — which is the point of the port.

**One sizing note for the 124:** they discover ~110 states/pop at budget 1,000, above the repo model's ~83, so at large budgets the default reservation can be exceeded once — the solver then grows loudly (a doubling copy) and the search is unchanged (pinned by the growth test). To avoid the transient copy spike, pass `reserve_states ≈ 120 × budget`.

## How to use it

`hsearch_ab.ipynb` CONFIG: `ENGINE = "hcompact"`. Result-neutral like `KEEP_PATH` and `HIGH_SPEEDUP` — rows are byte-identical across engines (verified end-to-end through `run_ab` at budget 1,000: 16/16 rows equal minus `secs`, certificates present on every solve), so it stays out of the filename identity and files resume across engines. Direct use:

```python
from experiments.heuristic_search.hcompact import greedy_search_hcompact
from experiments.heuristic_search.hsolve import RECOMMENDED
stats = greedy_search_hcompact(r1, r2, node_budget=3 * 10**6,
                               max_relator_length=48, config=RECOMMENDED)
```

Returns `greedy_search_h(keep_path=False)`'s exact dict (empty `path`/`path_moves`; `path_length` correct on a solve). Recover a certificate by re-running the one solved presentation through `greedy_search_h(keep_path=True)` — deterministic, so exact; `run_ab` does this automatically.
