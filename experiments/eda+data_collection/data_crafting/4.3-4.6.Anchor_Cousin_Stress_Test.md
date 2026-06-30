# 4.3–4.6 — Anchor + Cousin Stress-Test

*A self-contained Colab/A100 notebook that hammers the **16 known-hard d-o-t classes** with the
project's strongest available search, to confirm their high/censored labels survive serious compute
**before** the training archive (Phase 2) trusts them. Slots between Phase 1 (`build_anchors.py`,
`4.1.Results_Phase1.md`) and Phase 2 (`build_training_archive.py`).*

**Status:** built + **dry-run-verified on every CPU-runnable cell**; the GPU/Colab path is
`[unverified]` pending first A100 run. Reviewed by `advisor()` + the Field Advisor at plan
(`tmp/field_advisor_pre.md`) and post-implementation.

---

## 0. Why this exists (the gap it closes)

The 16 classes are currently labelled *known-hard* on a **weak budget**:
- **8 named anchors** (`data/derived/dot/anchors.jsonl`) — AK(3)–AK(8) + Length-14 — censored,
  `tier=named`, `loss_type=hinge`, `bound_B=150` (the "very high label").
- **8 cousins** (`short_hard` in `data/derived/dot/ak_trap_set.json`) — in-archive censored rows
  with `total_len ≤ 13` that *look like* AK(3) but were only **"unsolved-within-budget," not proven
  hard** (`3.DATA_DISTRIBUTION_PLAN.md` CLARIFYING #2). They go to **train with `short_hard ×3`
  weight** (`4.0` §7.3), so a cousin that is actually solvable is a **weighted-wrong training label**.

This step escalates the search and records a defensible verdict. **Verdict language is deliberate:**
*"survived the strongest available search at budget X"* — **never "proven hard."** Neither engine is
a neutral hardness oracle (greedy is length-greedy GBFS; the 610model policy is OOD on these basins).

The deliverable: **`experiments/eda+data_collection/stress_test/1.anchor_cousin_stress.ipynb`**
(14 code cells, `## N.` convention). Sub-phases map to this doc's sections:

| step | what | notebook cells |
| --- | --- | --- |
| **4.3** | setup + build the 16 targets (+ 2 controls) + env/ckpt | `## 1–6` |
| **4.4** | greedy stress (RAM-bounded numba GS-Sub + AK certificate) | `## 7–8` |
| **4.5** | beam stress (610model, B=32,768 × 5 seeds) + guard + validation | `## 9–12` |
| **4.6** | verdict (named→HALT, cousin→three-way) + sanity | `## 13–14` |

---

## 4.3 — Setup, targets, env  (`## 1–6`)

| cell | source | what it does |
| --- | --- | --- |
| `## 1` XLA flags | verbatim `2.beam_harvest_pilot.ipynb` cell 1 | `XLA_PYTHON_CLIENT_PREALLOCATE=false`, autotune off — **before any JAX import** (honest `memory_stats` for wave sizing). |
| `## 2` Repo setup | verbatim `beam_harvest` `## 1` | Colab: clone `Avi161/ACSolverX` branch `test/eda`, `pip install -r requirements-cuda.txt`. Local: walk up to repo root, no-op. |
| `## 3` Mount Drive | adapted `beam_harvest` `## 2` | `RUN_TAG="anchor_cousin_stress"` → `RUN_DIR` (durable, resumable). Local fallback `_stress_local/`. |
| `## 4` Config | **new** | One `CONFIG` dict drives everything (budgets, B, seeds, paths) + the **resumable JSONL helpers** (`load_records`, `load_done_ids`, `append_record` with `fsync` per record — both engines append to one file). |
| `## 5` Build targets | **new** | Construct the 16 targets + 2 controls; **GATE**; write the dataset file. |
| `## 6` Imports/env/ckpt | adapted `beam_harvest` `## 5–6` | JAX float32; `ACS(max_length=24, max_steps_in_episode=T=150, initial_states_file="stress_targets")`; restore `610model` **params only**; shared engine constants (`hash_vec`, `HASH_SENTINEL`, `GLOBAL_VISIT_CAP`). |

**The 16 targets (`## 5`).** 8 named anchors read from `anchors.jsonl` (label recovered from
`ak_trap_set.json`'s named map); 8 cousins split from the `short_hard` keys. Each is canonicalised
with `canon.canon_key`; **`AK_KEYS = {(canon_r1, canon_r2): label}`** for the 8 named is built here
for the 4.4 certificate scan.

**GATE.** `assert {canon_key(t) for 16 targets} == set(ak_trap_set["keys"])` — the targets are
*exactly* the labelled trap-set classes. Verified ✅ (`GATE OK: 16 target keys == ak_trap_set keys (16)`).

**Dataset file.** `## 5` writes **`data/stress_targets.txt`** (a runtime artifact, regenerated each
run; not committed) — 18 lines via `canon.strs_to_presentation_literal`: **rows 0–15 = the 16
targets, rows 16–17 = the 2 positive controls**. The beam env (`## 6`) loads it by index. A
round-trip check re-reads each line → `env_state_to_strs` → `canon_key` and asserts the key matches.

**Positive controls.** Picked from `merged_best_paths_index.csv`: the first 2 rows with **both**
`greedy_solved` and `beam_solved`, short (`total_len ≤ 12`, `beam_len ≤ 10`) → idx 0
(`xxxyy / xyyxY`, beam 3 / greedy 4) and idx 1 (`xxyxy / xyyxY`, beam 4 / greedy 5). They prove the
harness can actually solve (4.5 `## 10`).

---

## 4.4 — Greedy stress  (`## 7–8`)

### `## 7` — the greedy solver (self-contained)

Copied from `greedy_search.ipynb` cells 0–2 (`ACRelatorSolver`, the numba S-move/canonicalisation
tree) with **three surgical edits**:

1. **numba-optional shim** (mirrors `scripts/lib/canon.py`) — runs in numba-less envs (passthrough
   `njit`), keeps numba speed on Colab.
2. **env-consistent neighbour gate:** `len(nr1r)+nr2r < max_len` → **`len(nr1r) ≤ 24 and len(nr2r) ≤ 24`**.
   This mirrors the env's silent no-op on relator length > 24, so **every greedy state is a legal env
   state** (per-relator cap, not a sum cap). *Verified the cap holds:* no state with a relator > 24
   appears in AK(3)'s `seen`.
3. **`max_seen` RAM guard** on the search loop (see the finding below).

The solver is always run with **`stop_early=False`** — otherwise AK(3)–AK(7) (which are in the
notebook's built-in `counterexamples` dict, `range(3,8)`) would **return at depth 0** the instant
their own initial state is popped. (The AK certificate is done post-hoc instead; see below.)

### KEY FINDING — greedy is RAM-bound, not node-bound

The greedy **frontier** (`new_seen` / `visited`) grows ~**45 states per popped node**; measured
**~406 B/state**. So the literal "10M nodes" budget is **memory-infeasible**:

| popped nodes | frontier `|seen|` | RAM |
| --- | --- | --- |
| 100k | 4.74 M | 1.92 GB (measured) |
| 1 M | ~47 M | ~19 GB |
| **10 M** | **~470 M** | **~190 GB ← infeasible** |

And `PLAN.md:117` shows GS-Sub **plateaus at 1M nodes** (640@1M == 640@10M) — past 1M greedy gains
nothing. So `## 8` **RAM-bounds greedy** to the largest depth that fits Colab RAM (≈ the 1M-node
plateau), retaining full greedy power. This is the `[-]` deviation from the user's stated "10M."

### `## 8` — the greedy run (RAM-bounded, parallel, resumable)

- **Pre-flight:** warm the numba `@njit` tree once (a trivial solve) **before forking**; run one
  target to `PREFLIGHT_NODES=200k` to measure `bytes_per_state` and `states_per_node`; free that
  frontier (`del; gc.collect()`) before the pool.
- **Sizing:** `WORKERS` = how many can each reach the 1M-node plateau within `0.70 × RAM`;
  `SEEN_CAP` fills each worker's RAM slice (capped by the node ceiling). A loud **NOTE** prints when
  the literal `GREEDY_NODES` is RAM-infeasible and what the effective budget is.
- **Run:** `multiprocessing` **fork** `Pool(maxtasksperchild=1)` (each worker recycled to free its
  huge `seen` set) over the 16 targets + 2 controls. Each `_greedy_one` returns a **small summary**
  (never the multi-million-state `seen`), appended to the resumable JSONL.
- **AK-equivalence certificate (the headline cousin signal):** after each search, scan `new_seen`
  against the **full 8 named AK canonical keys** (excluding self). **A cousin reaching an AK(k)
  canonical class is *proven* AC-equivalent to AK(k)** — S-moves are AC-moves, so this holds even
  though the search is capped/incomplete. (Note: the built-in dict omits AK(8); we scan all 8 from
  `anchors.jsonl`.) *Verified the scan can fire:* greedy's own canonicalisation byte-matches the
  `AK_KEYS` format, and AK(3)'s own key is in its `seen`.
- **Positive control:** `assert` greedy solved both controls — else the harness is broken.

**Per-record fields (greedy):** `greedy_solved, greedy_len, nodes_visited, n_seen,
best_len_reached, ak_key_touched, stop_reason ∈ {solved, seen_cap, node_cap, frontier_exhausted},
wall_time, max_nodes, max_seen, per_relator_cap=24`. `best_len_reached` (the shortest relator-sum
ever reached — the censoring context `PLAN.md:158` requires) is captured from the `min(new_seen)` the
solver previously discarded.

---

## 4.5 — Beam stress  (`## 9–12`)

| cell | source | what it does |
| --- | --- | --- |
| `## 9` engine | **verbatim** `2.beam_harvest_pilot.ipynb` §7 `make_engine(B)` | `jax.vmap(beam_step)` over a wave of `(idx, seed, temp, temp_end)`; per-element temp schedule; the two documented vmap-safety fixes. `RUN_WAVE, RUN_BATCH = make_engine(B)` with **B=32,768**. |
| `## 10` guard + controls | adapted `beam_harvest` `## 8` | (a) batched engine matched **byte-for-byte** to released `beam/beam_search.py` on the 2 controls; (b) **beam at B must SOLVE** both controls under production config. |
| `## 11` beam run | adapted `beam_harvest` `## 10` | 16 targets × 5 seeds, full horizon T=150, resumable. |
| `## 12` validate | adapted `beam_harvest` `## 13` | `replay_packed_path` every beam solve; assert `terminated ∧ nsteps == beam_len`; drop unvalidated. |

**Wave-size cap (`## 11`).** The GPU peak is a single fused actor-head alloc scaling with **W·B**
(not linearly). `wave_size = min(auto_wave(B), 3)`: **W=3 × 32,768 = 98,304 == the proven-OK
W=6 × 16,384 point (~59 GB)**; W=4 × 32,768 > the W=7 × 16,384 OOM point. The cap can never drift
into an OOM.

**Seeds / temperature (`## 11`).** `SEEDS=[0,1,2,3,4]`: seed 0 deterministic (temp 0); seeds 1–3
Gumbel-explore (temp **1.0→0.0**); seed 4 a **sustained high temp 1.5** (FA: 610model is OOD on these
basins, so the 5 seeds — not the 2× width — are the more valuable axis; one sustained seed broadens
basin coverage). This is the binding escalation: prior harvest ran B=16,384; this is a genuine 2× to
32,768 + the project-standard 5 seeds (`2.PPO_BEAM_HARVEST_PLAN.md:135`).

**Per-record fields (beam):** `seed, beam_solved, beam_len, packed_path, beam_width, horizon, wall_time`.

**[TRAP] handled:** the beam env (`## 6`) is built with `max_steps_in_episode = T = 150` (the
**search** horizon), not the training NUM_STEPS=96 — else every beam dies at step 96.

---

## 4.6 — Verdict + sanity  (`## 13–14`)

### `## 13` — verdict + relabel flags

Per-target merge of greedy + beam, with **provenance-separated distances** (FA: `greedy_len` is NOT
an env d-o-t — the env no-ops on `new_size > 24` computed **before** `cyclic_reduce`, greedy gates on
the **reduced** length, so greedy can traverse edges the env cannot). **`relabel_dot` is taken ONLY
from the env-validated beam path; `greedy_len` is reported separately, never folded in.**

**Fork on `group`:**
- **named anchor trivialised → `ANOMALY_SOLVED` → HALT/ESCALATE** banner. A replay-validated AK(n)
  solve is a refutation of Andrews–Curtis (extraordinary) or — far likelier — an env/canon/dedup
  bug. **Never relabel.**
- **cousin → three-way `status`:**
  - **`trivialized`** (reached trivial) → **RELABEL-NEEDED** banner (`relabel_dot` from the beam
    path; a greedy-only solve needs env-packed reconstruction first). Archive is **NOT** edited.
  - **`certified_AK_equivalent`** (`ak_key_touched` set) → genuinely hard *by certificate*; keep censored.
  - **`still_unsolved`** → unsolved under budget (weakest claim); keep censored.
  - **special flag:** the `total_len=12` cousin `YXXYx|YYYYXyX` is *predicted trivializable* (theory:
    total length < 13 ⇒ trivializable); a non-trivialized status there ⇒ investigate the harness, not "hard."

Writes **`anchor_stress_summary.json`** (verdict + per-target rows) + a **repo mirror**
(`data/derived/dot/anchor_stress_summary.json`, `...anchor_stress_results.jsonl`).

### `## 14` — sanity checks (Field Advisor §d)

(a) env config invariants; (b) the 8 cousins still `censored` in the **live** `dot_archive`;
(c) distance-as-class-invariant (a control solved from a 2nd canonical representative → same length);
(d) action-space equivalence (greedy `get_neighbors_nj` vs env `(i,j,k1,k2)` S-moves on a sample
state — best-effort, `[unverified]`, GPU-only, wrapped in try/except).

---

## Results (dry-run, local CPU)

**Verified green:**

| check | result |
| --- | --- |
| `## 5` GATE | ✅ 16 target keys == `ak_trap_set` keys |
| dataset round-trip | ✅ 18 rows written, every line re-keys correctly |
| greedy controls | ✅ idx0 solved `glen=4`, idx1 solved `glen=5` |
| greedy AK(3) | unsolved at 100k nodes, `best_len=13` (no length drop), `stop=node_cap` |
| greedy cousin `…YYYYXyX` (len 12) | unsolved at 200k nodes, `best_len=12` (needs the full budget / flagged in `## 13`) |
| per-relator ≤24 cap | ✅ no relator > 24 ever enters `seen` |
| AK certificate format | ✅ greedy's own canon byte-matches `AK_KEYS`; AK(3)'s own key ∈ `seen` → scan can fire |
| greedy worker + JSONL resume + positive control | ✅ |
| `## 13` verdict (injected fakes) | ✅ named AK(3) fake-solve → **HALT/ESCALATE**; len-12 cousin fake-solve → **RELABEL-NEEDED** (d-o-t 7, beam-validated); others correct three-way |
| all 14 code cells | ✅ compile |

**`[unverified]` (no GPU locally):** `## 6` (imports/env/ckpt), `## 9–12` (engine/guard/beam/validate),
`## 14(d)`. Derived verbatim from the proven `2.beam_harvest_pilot.ipynb` + interface-checked
(`beam_search.py` CSV columns `presentation_idx/solved/path_length/path` confirmed absolute; `reset_env`
and `EnvState` signatures confirmed). **Run them first on a clean A100.**

---

## How to run (Colab A100)

1. Open the notebook on Colab with an **A100 (high-RAM)** runtime.
2. Run `## 1–10` top to bottom. `## 10` runs the correctness guard + positive controls; on PASS it
   prints **"set `CONFIG['RUN_GUARD']=False`, Runtime→Restart, re-run."**
3. Set `RUN_GUARD=False`, **Restart**, re-run — greedy (`## 8`) resumes/skips from the JSONL, then the
   heavy beam pass (`## 11`) runs on a clean GPU.
4. `## 12` validates; `## 13` prints the verdict + any HALT/RELABEL banner and writes the summary.

**Resumable:** every record is `fsync`'d to `RUN_DIR/anchor_stress_results.jsonl` on Drive; a
preempted session continues from the last good line (greedy keyed by `(greedy, key)`, beam by
`(beam, key, seed)`).

---

## All files

**Deliverable (committed):**
- `experiments/eda+data_collection/stress_test/1.anchor_cousin_stress.ipynb` — the notebook.
- `experiments/eda+data_collection/data_crafting/4.3-4.6.Anchor_Cousin_Stress_Test.md` — this doc.

**Inputs it reads:**
- `data/derived/dot/anchors.jsonl` — 8 named anchors (labels under test).
- `data/derived/dot/ak_trap_set.json` — 16 keys (GATE) + the named map.
- `data/derived/labels/dot_archive.jsonl` — cousins' current censored rows + live-archive sanity.
- `data/derived/paths/merged_best_paths_index.csv` — positive-control selection.
- `ppo_checkpoints/610model/` — beam policy (params only).
- `greedy_search.ipynb` cells 0–2 — greedy solver source (copied + 3 edits).
- `experiments/eda+data_collection/beam_harvest/2.beam_harvest_pilot.ipynb` — setup/engine/guard/validate source.
- `scripts/lib/canon.py` — `canon_key`, `canonical_pair_str`, `strs_to_presentation_literal`, `env_state_to_strs`.
- `beam/beam_search.py` — oracle for the `## 10` guard; `envs/utils.py` — `replay_packed_path`.

**Outputs it writes (runtime artifacts, regenerated each run — not committed):**
- `data/stress_targets.txt` — the 18-row env dataset (16 targets + 2 controls).
- `RUN_DIR/anchor_stress_results.jsonl` (+ repo mirror `data/derived/dot/anchor_stress_results.jsonl`) — one record per (target × engine [× seed]).
- `RUN_DIR/anchor_stress_summary.json` (+ repo mirror `data/derived/dot/anchor_stress_summary.json`) — per-target verdict.

---

## Review trail

- **Plan (Checkpoint 1):** `advisor()` + Field Advisor warm-pre (`tmp/field_advisor_pre.md`). Folded
  in: the AK certificate (FA #1), `greedy_len` ≠ env d-o-t + named/cousin fork (FA #2), positive
  controls (FA #3), verdict language, wave cap, RAM-bound greedy.
- **Post-implementation (Checkpoint 2):** `advisor()` — verified the AK-certificate format match and
  absolute `presentation_idx` (both clean); applied the pre-flight-free + smaller-pre-flight fix and
  the `[unverified]` GPU-path tags. Field Advisor post review recorded in `tmp/field_advisor_post.md`.
- **One surfaced reviewer disagreement (not silently reconciled):** `advisor()` calls a greedy
  non-solve "≈ zero information"; the **Field Advisor** calls it a "strong-but-not-exhaustive probe"
  (GBFS over a *global* visited set *can* escape basins). The notebook reports greedy as a
  strong-but-bounded probe and never phrases a greedy non-solve as "proven hard."
