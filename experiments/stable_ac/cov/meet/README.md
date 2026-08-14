# covmeet — CoV collision search over the 124 unsolved classes

Merge unsolved Aut-classes using **change-of-variables moves only** — no AC/substitution
search, zero search nodes. From every class rep, enumerate every valid CoV
(`cov.enumerate_cov`, the `(z, iso_gen, iso_index)` brute force), Aut-min each output
(`ladder/autcanon_fast.aut_min`), pool all orbits into one store keyed on the exact
canonical pair. An orbit reached by two different classes proves them **stably**
AC-equivalent (never unqualified AC-equivalence) → `124 − S` remaining. Tracked per
class alongside: any orbit **below** the seed's Aut-min (`[DROP]` / `improved_below_seed`).

Design + measurements (branching ≈ 3 orbits/state after Aut-min collapse; `aut_min`
flat in length; CoV never descends at depth ≤ 3 from the reduced starts — the search is
a *meeting* search, not a descent): `covmeet.py`'s module docstring.

| file | role |
|---|---|
| `covmeet.py` | engine: seeds, expansion workers, bucketed shortest-first frontier, append-only jsonl events, resume-by-replay, merges (union-find) + drops |
| `verify_covmeet.py` | independent check: full structural replay + segment-by-segment edge replay (`--sample K` / `--full`); exit 0 = verifies |
| notebook | [`experiments/notebooks/stable_ac/covmeet_vast.ipynb`](../../../notebooks/stable_ac/covmeet_vast.ipynb) — CONFIG / SETUP / RUN / STATUS, for a vast.ai CPU box |
| tests | `tests/stable_ac/test_covmeet.py` — resume==uninterrupted, torn-tail repair, merge + drop detection, determinism, serial==parallel |

## The output folder is the whole state

`OUT_DIR` holds one append-only `covmeet_<seedset>_<family>.jsonl` (identity = seed set
+ family tag, nothing else) plus a derived `*_summary.json`. Every wave is fsynced.
Crash/preempt recovery: download `OUT_DIR` any time; on a new box upload it to the same
path and **Restart & Run All** — the torn last line is repaired, events replay, the run
continues. Runs are deterministic given the config, and `WAVE`/`CHUNK`/`WORKERS` change
throughput only, never the final masks/merges/classes.

Event rows: `meta` (session), `seed`, `edge` (child orbit + parent + `(z, iso, br)` move
+ parent mask + census multiplicity), `x` (expansion done: `ncov` raw CoVs → `norb`
orbits — the per-state census), `merge`, `drop`. Merges and drops are re-derived on
replay; the rows are for humans.

Finished or interim results get committed under `results/stable_ac/covmeet/` (hand the
downloaded folder back and it lands there) — never beside this code.

## No length cap

`REJECT_LEN=239` is the packed greedy solver's ceiling and this pipeline never calls
that solver; covmeet passes an effectively infinite `reject_len` and bumps the family
tag to `subnc2pxysbnolim` accordingly (a different family must never share a resume
file). States store their Aut-min rep only, so unbounded expansion costs nothing.
