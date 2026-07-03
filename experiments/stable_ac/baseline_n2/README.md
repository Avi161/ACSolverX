# Phase 0 + Phase 0.5 — n=2 greedy baseline (GS-Sub) over MS(1190)

Pure 2-generator greedy — **no `z=w`, no stabilization, no n=3, no RL/beam**. This is the paper's
classical baseline plus its reproduction gate, packaged to run on CPU boxes (Colab) in parallel.

- **Phase 0** — `labels_phase0.py` → `results/labels_1190.json`: index-derived reference labels
  (`paper_reference.solved = idx<640`, `in_ac19_extended_prefix = idx<634`) + `r1_len/r2_len`. No compute.
- **Phase 0.5** — `run_greedy.py` / `run_greedy.ipynb`: n=2 greedy over all 1190, four streams.

The solver (`greedy_ac.py`) is lifted **verbatim** from `greedy_search.ipynb::ACRelatorSolver` with one
change: a `cap_mode` that switches the length cap between the notebook's **sum** rule and a **per-relator**
rule. It's numba+numpy only (no JAX), so a box just needs `pip install numba numpy`.

## The four runs (one per box, all independent + resumable)

| box | `CAP` | `BUDGET` | `MAX_LEN` | stream written |
|---|---|---|---|---|
| 1 | `sum`         | `100000`  | 100 | `results/greedy_reprogate_100k.jsonl` |
| 2 | `sum`         | `1000000` | 100 | `results/greedy_reprogate_1m.jsonl` |
| 3 | `per_relator` | `100000`  | 24  | `results/greedy_baseline_100k.jsonl` |
| 4 | `per_relator` | `1000000` | 24  | `results/greedy_baseline_1m.jsonl` |

- **`sum` (reprogate)** = the notebook's native cap → reproduces the paper's **634 @100k / 640 @1m**
  (a deviation ⇒ port bug, not a cap difference).
- **`per_relator` (baseline)** = each relator `< 24` (the env's `L`) → the fair baseline the future
  `z=w` arms will share.
- The **1m** runs do **not** wait on the **100k** runs — launch all four at once (the ~640 easy cases
  stop early regardless of budget, so running 1m over the full set is nearly free).
- Every run **skips idx already in its stream**, so a pre-empted box resumes with zero lost work.

## Run on Colab (recommended)

Open `run_greedy.ipynb`, set `REPO_URL`, then in the params cell set `CAP`/`BUDGET` per the table and
Runtime → Run all. It clones the repo, `pip install`s numba+numpy, mounts Drive, runs the base-case
gate, then the resumable sweep, writing the stream to your Drive folder (`DRIVE_OUT`). Copy the
finished streams into the repo's `results/`. `WORKERS` (default 4) uses that many cores;
`SHARD='i/k'` runs only idx-chunk `i` of `k` if you want to split one stream across extra boxes.

## Run from the CLI (local or any box)

```bash
cd experiments/stable_ac/one_generator/baseline_n2
python labels_phase0.py                                    # once -> results/labels_1190.json
python run_greedy.py --cap sum         --budget 100000  --workers 4   # box 1
python run_greedy.py --cap sum         --budget 1000000 --workers 4   # box 2
python run_greedy.py --cap per_relator --budget 100000  --workers 4   # box 3
python run_greedy.py --cap per_relator --budget 1000000 --workers 4   # box 4
python build_index.py                                      # after all 4 -> min-path index
```
Outputs default to the repo's `results/`. Add `--out_dir <path>` to write elsewhere (e.g. Drive),
`--shard 0/3` to run an idx chunk, `--no_base_case` to skip the gate on resume.

## Outputs (create `results/` and collect these)

Per-idx JSONL line (one per presentation):
```json
{"idx": 0, "solved": true, "path_verified": true, "nodes_explored": 812,
 "path_len": 13, "max_len_along_path": 21, "wall_time_s": 0.04,
 "budget_nodes": 100000, "cap": "sum"}
```
- `path_len` = moves = `len(path)-1` (greedy-found; **not** provably shortest — greedy is best-first on
  relator length, not depth).
- `max_len_along_path` = peak `|r1|+|r2|` on the path (the temporary length "hump").
- `solved` is the raw "reached trivial within budget". `path_verified` re-walks the path independently
  of the search's `visited`/heap **bookkeeping** (so it catches search bugs); it still shares
  `get_neighbors_nj`/canonicalization with the solver, so it does **not** catch a move-generation bug —
  the real-env `check_paths` (JAX, deferred to when the n=3 env exists) is that gold check. A solve is
  only counted downstream when **both** flags are true (so a `solved:true, path_verified:false` line is a
  loud search-bug flag, never silently dropped).

Files under `results/`:
- `labels_1190.json` — Phase 0 reference labels.
- `greedy_reprogate_{100k,1m}.jsonl`, `greedy_baseline_{100k,1m}.jsonl` — the 4 Phase 0.5 streams.
- `solved_path_len_index.json` — `{idx: {min_path_len, from_stream, path_verified}}`, the **minimum
  path length per solved presentation** across all streams (`build_index.py`).

## Base-case gate

Runs before every sweep (skippable with `--no_base_case`): (1) `MS(3,'YXyxy')` reproduces the notebook
(10000 nodes, no trivial); (2) idx 0–4 solve **and** `verify_path` passes; (3) a known-hard idx stays
unsolved. For `sum` boxes, after the run the solved count should land near **634 @100k / 640 @1m**,
essentially all within idx<640 — if far off, adjust `MAX_LEN`. An idx≥640 solve is quarantined and
`verify_path`-checked: a verified one is a real finding, not an auto-failure.

## Files

| file | role |
|---|---|
| `greedy_ac.py` | verbatim n=2 solver + `cap_mode`; `flatlist_to_strs`, `path_stats`, `verify_path`, `solve_one` |
| `jsonl_io.py` | `jsonl_done_ids`, `jsonl_append` (resumable append-only, flush+fsync) |
| `labels_phase0.py` | Phase 0 labels → `results/labels_1190.json` |
| `run_greedy.py` | Phase 0.5 sweep driver (base-case gate + resumable multiprocessing) |
| `run_greedy.ipynb` | thin Colab wrapper over `run_greedy.py` |
| `build_index.py` | min-path-length index over the 4 streams |
