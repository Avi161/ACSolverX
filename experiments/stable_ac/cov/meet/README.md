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

## The output folder: a bounded snapshot + a tiny certificates file

`OUT_DIR` holds three things (identity = engine tag + seed set + family tag):

| file | what | size |
|---|---|---|
| `covmeet3_<seeds>_<family>.snap` (+`.snap.prev`) | the WHOLE store — orbits 2-bit-packed, masks, expanded flags, census, parent pointers and moves — checkpointed atomically every `snapshot_every` s (default 300) and at every stop; sha256-trailed; corrupt main falls back to prev | ~28 B/orbit, **bounded** (~2 snapshots, tracks the store, not the runtime) |
| `covmeet3_<seeds>_<family>_certs.jsonl` | ONLY results: `meta`/`seed` rows + **full chains** on `merge` and `drop` | KBs |
| `*_summary.json` | derived summary, atomic-replaced | KBs |

Why not hashing: at 10⁸+ orbits a collision-safe digest needs 128 bits = 16 bytes,
while the exact pair 2-bit-packed is ~5–10 bytes at measured shell lengths — the exact
state is *smaller* than any safe hash, and a colliding digest would be a false merge.

Crash/preempt recovery: download `OUT_DIR` any time; on a new box upload it to the same
path and **Restart & Run All** — resume loads the newest valid snapshot and
deterministically re-does at most `snapshot_every` seconds of work. Parents are IN the
snapshot, so merge/drop chains survive restarts whole; a merge re-fired during a
re-done interval at worst duplicates a certificate row, which the verifier dedupes.
Runs are deterministic given the config; `WAVE`/`CHUNK`/`WORKERS` change throughput
only, never the final masks/merges/classes.

Speed: `aut_min` is 89% of per-state cost; `_aut_min_memo` (exact, keyed on
`relabel_min` — equal keys imply the same Aut-orbit) collapses ~66 children to ~21
computations and re-reaches to zero. Measured 134 → 51 ms/state cold, 21 ms warm.

Finished or interim results get committed under `results/stable_ac/covmeet/` (hand the
downloaded folder back and it lands there) — never beside this code.

## No length cap

`REJECT_LEN=239` is the packed greedy solver's ceiling and this pipeline never calls
that solver; covmeet passes an effectively infinite `reject_len` and bumps the family
tag to `subnc2pxysbnolim` accordingly (a different family must never share a resume
file). States store their Aut-min rep only, so unbounded expansion costs nothing.
