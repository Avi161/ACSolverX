# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

AC-SolverX trains JAX/PPO reinforcement-learning agents to trivialize balanced
presentations of the trivial group (the Andrews–Curtis conjecture search
problem) using composite **substitution** ("S-move") supermoves and a
**Dual-Ring Transformer** policy/value network. `README.md` is authoritative for
the math background, dataset semantics, and CLI flag reference — read it for any
of those. This file captures the cross-file architecture and invariants that the
README does not.

## Commit discipline (ALWAYS — for traceability)

**After implementing any plan, `git add` the work and `git commit` it.** Never leave
completed, verified work uncommitted — every plan/phase must land as a focused commit so
the git history *is* the trace of what was built and why. This is non-negotiable; do not
wait to be reminded.

- **One logical change per commit.** Prefer per-plan / per-phase commits over a single
  mega-commit — separate, scoped commits are what make the history traceable. Don't bury
  a phase's deliverables inside an unrelated bulk commit.
- **Commit only after verification is green** (tests pass, determinism checked, originals
  confirmed untouched). Never commit known-broken work.
- **Write extremely detailed commit messages.** Summary line + body covering: *what*
  changed and *why*, the files added/modified, the key results/numbers, *how it was
  verified*, and any superseded decisions or scope notes. Assume the reader has only the
  commit message, not the conversation that produced it — the body is the durable record.
- **Branch, don't commit to the default branch.** If on `main`, branch first; topic work
  lands on a feature branch (e.g. `test/eda`). Commit locally; **push only when asked.**

## Plan TODO checkboxes (ALWAYS — for traceable plans)

Track every plan/spec's steps as checkboxes so progress is visible and auditable:

- Each **discrete, executable step** is a `- [ ]` item. Checkboxes go on steps ONLY — never on
  decision tables, rationale, or prose; don't force them onto non-actionable text.
- When a step is executed **and verified**, flip it to `- [x]`.
- When adding checkboxes to an **existing** plan, mark already-finished steps `- [x]` **honestly**
  — never default everything to `- [ ]` (that hides completed work and is the opposite of the point).
- If a step turns out wrong or could be phrased better, **DISCUSS the change with `advisor()` first**,
  then apply it and mark the item `- [x][-]` (done AND changed) with an inline note stating **exactly
  what it changed from → to**, so the collaborator can see and understand it. Never silently rewrite a
  step — the `[-]` + from→to note is the audit trail.

## Dual-reviewer workflow (ALWAYS — plan + post-implementation)

Every non-trivial task gets **two complementary reviewers** at **two checkpoints**.
`advisor()` catches code-level / methodology traps in-conversation; the **Field Advisor**
(`.claude/agents/field-advisor.md`, opus, grounded in the two `literature/` PDFs + the
`.research_executor/` cache) brings deep, paper-grounded **domain** judgment.

**Checkpoint 1 — in plan mode, before writing any code.** Whenever Claude enters/produces a
plan, review that plan with **BOTH** `advisor()` **and** the Field Advisor (warm-pre →
`tmp/field_advisor_pre.md`) before exiting plan mode / starting implementation. Do not begin
coding until both have weighed in.

**Checkpoint 2 — after the code is implemented (and verified green).** Review the produced
artifacts again with **`advisor()` first, then the Field Advisor** (post →
`tmp/field_advisor_post.md`). Address what they surface before declaring the task done.

Rules:
- **Both reviewers, both checkpoints — not one or the other.** They are complementary.
- On **active disagreement** between the two, surface both verdicts **verbatim** and let the
  user weight; do not silently pick a side.
- **How to invoke the Field Advisor:** interactive session → Agent tool with
  `subagent_type: "field-advisor"`; background/remote session (fixed registry) → spawn
  `general-purpose`/`claude` with `model: opus` and a prompt telling it to read
  `.claude/agents/field-advisor.md` as its full contract. Pass the goal verbatim + the mode
  (warm-pre / post). See `.research_executor/FIELD_ADVISOR_CHARTER.md`.
- Skip both only for genuinely trivial / mechanical edits (typo, rename, one-line config).

## Literature (`literature/`, local-only context — currently *untracked*, not gitignored)

The two source papers live here — read them for the math/RL background, not just
the README:

- `literature/AC_Paper_for_ICML2026-2.pdf` — **"The Two-Hump Problem"** (ICML
  2026), *this repo's own paper*. Authoritative for: the two-hump difficulty
  distribution, the S-move/substitution action space, the Dual-Ring Transformer,
  the AC-19/AC-1M datasets, and the **canonical form (Definition E.1)** — a
  presentation is canonical when each relator is the lex-min over all cyclic
  rotations of `r` and `r⁻¹`, and the pair is ordered `r₁ ≤_lex r₂`. **Note:** for
  state-keying/dedup the project pins the lab's *implemented* canonicalizer
  `canonical_pair_nj` (`greedy_search.ipynb`), not E.1's appendix statement — same
  equivalence classes (rotation + inverse + swap), but pair ordered
  **length-then-lex** under alphabet order `y⁻¹ < y < x⁻¹ < x`. The greedy CSV
  (`data/all_presentations_len_8_to_19_GS_solved_copy2.csv`) is NOT stored in this
  form — its relators are only *reduced* and pairs *shortest-first* (no
  rotation/inverse min) — yet its stored states are empirically **1:1 with true
  `canonical_pair_nj` classes** (verified in `experiments/eda.ipynb` P2-11), so
  joining other sources still requires canonicalizing via `canonical_pair_nj`. The
  env's per-move Booth rotation is **not** a canonical form (one relator only, no
  inverse-min, numeric int8 order) — route env state through `canonical_pair_nj`.
  See `experiments/CLAUDE_ROUGH_PLAN.md` §2.
- `literature/Math_ML_paper.pdf` — **"What Makes Math Problems Hard for RL"**
  (Shehper et al., arXiv 2408.15332), the *prior/companion* paper. PPO baseline
  (solves 431/1190), a decoder-only transformer that classifies GS-solvability
  (F1≈0.94), and topological/neighborhood hardness features (XGBoost F1≈0.96).
  Neither paper builds a continuous distance-until-trivialization regressor —
  that gap is the subject of `experiments/CLAUDE_ROUGH_PLAN.md`.

## Commands

Always run Python entry points **from the repository root** — `data/` and
`ppo_checkpoints/` are resolved as relative paths, and `beam/` + `scripts/`
prepend the repo root to `sys.path` to import `envs`/`network`.

```bash
# Install (base + exactly one accelerator file; JAX is pinned in the accel file)
pip install -r requirements-cuda.txt        # NVIDIA CUDA 12
pip install -r requirements-rocm.txt        # AMD ROCm  (the original acenv backend)

# Train (writes Orbax checkpoints under ppo_checkpoints/<name>/)
python ppo_ac_s.py --ckpt_path my_run --save_every 50        # --w 1 enables wandb
python ppo_ac_s.py                                            # no --ckpt_path = trains, saves nothing

# Evaluate a checkpoint with beam search
python beam/beam_search.py --ckpt_path 610model --beam_width 1024 --start 0 --end 634

# Validate that stored solving paths actually trivialize (the repo's "test")
python scripts/analysis/check_checkpoint_paths.py --ckpt_path 610model --max_paths 10

# Greedy-search baseline (GS-Sub): open and run greedy_search.ipynb (numpy+numba only, no JAX/GPU)

# AC-1M ships gzipped; decompress before using stem "AC1M"
gunzip -k data/AC1M.txt.gz
```

There is **no unit-test suite, linter, or formatter** configured. Correctness of
a trained model is verified empirically by `scripts/analysis/check_checkpoint_paths.py`,
which replays each saved path move-by-move in a fresh env and asserts it reaches
the trivial presentation in the stored number of steps. Run it after any change
to the env, the S-move implementation, or the action packing.

## The action-packing invariant (read before touching the policy or env)

A move is the 4-tuple `[i, j, k1, k2]` (`i`=which relator is substituted,
`j`=invert the other relator first, `k1`/`k2`=cyclic rotations). The policy emits
a single flat `Categorical` index ("`sample`") that is packed/unpacked as:

```
sample = (((k1 - 1) * L + (k2 + j) * (-1)**j) * 4) + (i * 2 + j)
```

with **`L = 24`** (the per-relator `max_length`). This exact formula and its
inverse are duplicated across **five** places that MUST stay byte-identical:

- `network.py` — the actor head reshapes `[B, L_half, L_half, 4]` logits so this
  index layout holds (`i*2+j` is the innermost axis); invalid actions are masked.
- `ppo_ac_s.py` — `_env_step` unpacks `sample → action` for stepping; `_loss_fn`
  re-packs `action → sample` to recompute `log_prob`.
- `beam/beam_search.py` — `beam_step` unpacks (`L = 24` hardcoded), `decode_path`
  for output.
- `wrappers.py` — `LogPathsProbsS.encode_action` packs moves into `best_paths`.
- `envs/utils.py` — `encode_action` / `decode_action` / `decode_path`
  (default `max_length=24`), used by path validation and replay.

If you change `L`/`max_length`, change it in `ppo_ac_s.py:46`,
`beam/beam_search.py:67`, and every `max_length=24` default in `envs/utils.py`
together. A mismatch silently corrupts decoded paths rather than erroring.

`EnvParams.max_length` defaults to **64**, but the training/beam/validation
scripts all construct `ACS(max_length=24)`, so 24 is the real operating value.

## Architecture

**Environment (`envs/`)** is gymnax-style. A presentation is a flat
`jnp.int8` array of length `n_gen * max_length` (= `2 * 24`): two zero-padded
relators. Generators encode as `x→1, y→2, x⁻¹→-1, y⁻¹→-2`, padding `0`.

- `envs/environment.py` — base `Environment.step` does **auto-reset**: after
  `step_env`, it calls `reset_env(idx, sample)` and `lax.select`s on `done`. So
  on episode end an env either re-runs the same initial state (`sample=False`)
  or samples a new one (`sample=True`) — there is no separate reset call in the
  training loop. `idx`/`sample` live on the ACS `EnvState`, not the base class.
- `envs/ac_s.py` — `ACS`. `step_env` applies the move via
  `jax.lax.switch(action[0], self._actions, ...)`. Terminal = `count_nonzero(x)
  == n_gen` (trivial presentation). Dense reward
  `-clip(count_nonzero, 0, 10)*(1-term) + 1000*term`. Tracks a per-episode
  `visited_hashes` ring buffer for optional cycle/noop penalties
  (`--cycle_penalty`, `--noop_penalty`).
- `envs/ac_moves.py` — the S-move (`s_move`, `setup_s_actions`): rotate both
  relators, optionally invert one, concatenate-with-cancellation
  (`_concatenate`), `cyclic_reduce`, then re-canonicalize via Booth's algorithm
  (`booth_lex_min_rotation_masked`). **A move whose result would exceed
  `max_length` is silently a no-op** (the state is returned unchanged) — both the
  reward shaping and beam search special-case this.

**Network (`network.py`)** — `RelativeDualRingActorCritic` (the one PPO uses;
`DualRingActorCritic` is an absolute-position alternative). Splits the input into
two relators ("rings"), runs self-attention within each ring + cross-attention
between them, with **cyclic relative-position** embeddings. The actor masks
logits with a **semantic mask** (only substitutions where at least one letter
cancels: `r1 == ±r2`) combined with a padding mask, so invalid moves get `-1e9`.

**Wrappers (`wrappers.py`)**, applied in `ppo_ac_s.py` as
`LogWrapper → NormalizeVecReward → LogPathsProbsS`:
- `LogPathsProbsS` is the important one. It maintains, across all parallel envs
  and over the whole run: `solved_idx`, `path_lengths`, `best_paths` (shortest
  packed path per initial state), and an **adaptive sampling distribution
  `probs`** over initial states (less-solved / less-attempted states get sampled
  more). `_propagate_min_value` reduces per-env results to the best path per
  unique initial-state index. `solved_idx/path_lengths/best_paths` are exactly
  what gets written to the checkpoint's `solve_data`.

**Training loop (`ppo_ac_s.py`)** — the PPO update is a jitted single
`_update_step`, but the **outer loop is a plain Python `for`**, not
`jax.lax.scan`, specifically so Orbax can checkpoint between updates (it cannot
run inside a scan). `NUM_ENVS = 1190*2`; `L = 24`; dataset
`AC19_extended`. The first **634** initial states are the `1190MS.txt`-derived
benchmark and are pinned to deterministic reset (`parallel_sample[:634] = False`)
— wandb's `num_solved_interesting` counts solves among these.

## Checkpoints (Orbax) — restore sizing gotcha

Checkpoints use `ocp.CheckpointManager(item_names=("params","solve_data","config"))`.
Restoring **`solve_data` requires correctly-shaped dummy arrays**, and those
shapes depend on the *training* run, not the eval target:

- first dim = **line count of the training dataset file** (number of initial
  states),
- `best_paths` width = training **`NUM_STEPS`**, read back from the saved
  `config`.

`beam/beam_search.py` and `scripts/analysis/check_checkpoint_paths.py` both do a two-stage
restore: load `config` first to get `NUM_STEPS`, size the dummies, then load
`params` + `solve_data`. Pass `--training_dataset` (beam) / `--dataset`
(validator) to match the run; a wrong size makes the restore fail or misalign
indices. The pretrained `ppo_checkpoints/610model/` (latest step 1000) was
trained on `AC19_extended` and solves 610 of the first 634 presentations.

## Repository conventions

- `data/<stem>.txt` is the unit of dataset selection: `ACS(initial_states_file=
  "<stem>")` takes the bare stem (no `data/`, no `.txt`), one Python-literal
  presentation per line. `1190MS.txt` is the MS benchmark; `AC19_extended` is the
  default training set.
- `.gitignore` keeps only `ppo_checkpoints/610model/` (all other checkpoints
  ignored), ignores the decompressed `data/AC1M.txt`, and ignores `main.tex` (the
  paper draft is local-only; this is the public code repo).
- JAX is pinned to **0.6.0**; `jax_default_matmul_precision` is set to `float32`
  at import in the JAX modules — keep it.
- **Resumable data/results loops → always JSONL.** Any training loop or long
  data/results-collection run (especially GPU/Colab runs that can be preempted)
  must append **one record per finished unit** to a `.jsonl` file with
  `f.flush(); os.fsync(f.fileno())` per write, and on startup read that file back
  to a `done` set and skip already-finished work. If the GPU/kernel dies, you
  resume from the last good line instead of restarting from scratch. This is the
  pattern in `experiments/beam_harvest_pilot.ipynb` (`## 9. Resume + JSONL
  persistence`). Never hold collected results only in memory. Write to a durable
  path (Drive/project tree), never `/tmp`.
- **Notebook cell references (collaborator preference):** when authoring notebooks,
  number every cell's markdown header sequentially (`## 1.`, `## 2.`, …; use a suffix
  like `## 9b.` when inserting between cells — do not renumber). **When pointing the user
  to a cell in chat, refer to it by its full visible header — `` `## 2. Mount Google Drive` ``
  — NEVER by a bare "Cell N".** The notebook shows section headers, not positional indices,
  and the two diverge (section `## 6` is the 15th cell), so "Cell 6" gets read as section
  `## 6` and sends the user to the wrong place. [TRAP] this exact collision confused the user
  on 2026-06-25. See `[[notebook-cell-naming]]`.

## Lessons Learned

> Append a dated entry after any task that errored, needed a retry, or revealed a
> non-obvious pattern. Format: `### [YYYY-MM-DD] Topic` → what happened → rule.
> Tag `[WORKS]` / `[TRAP]`; never delete entries, mark stale ones `[SUPERSEDED]`.

### [2026-06-25] Batched-beam wave size: peak is one fused alloc, not a smooth per-pres sum [TRAP]
`experiments/beam_harvest_pilot.ipynb` batches `W` presentations through one `network.apply`.
The GPU peak is dominated by a **single fused actor-head activation** (`x_joint`-derived,
`~[W*B,24,24,2D]`), so it does NOT grow as a smooth `fixed + W*per_pres` line. Measured on an
80 GB A100 at B=16384: **W=6 peaks ~59.2 GB and runs; W=7 OOMs** (`RESOURCE_EXHAUSTED:
allocate 67,645,748,608 bytes` = a single ~67.6 GB block — XLA can't get it contiguous on top
of live buffers + CUDA/cuDNN reserve, even though `memory_stats` shows only ~3 GB used at the
moment of the failed alloc, because `XLA_PYTHON_CLIENT_PREALLOCATE=false` allocates on demand).
Rule: **W=6 is the proven ceiling at B=16384 on 80 GB**; don't trust a linear per-presentation
extrapolation to push higher. After an OOM, Runtime→Restart (the pool is left dirty). The cap
lives in the `## 4. Pilot configuration` cell (`WAVE_SIZE`) and the `## 9b` auto-sizer
(`TARGET_FRAC=0.75`). `T_CAP` (horizon cap) is independent of this and does not change the peak.

### [2026-06-24] Beam env must use max_steps = the search horizon, not the training horizon [TRAP]
`beam/beam_search.py:68` builds its env with `max_steps_in_episode=args.max_steps`
(the beam horizon T, e.g. 150) — **not** the PPO training `NUM_STEPS` (96). Reason:
`beam_step` kills beams on `dones` (`new_alive = parent_alive & (~dones) & ...`,
`beam_search.py:218`), and `dones` includes truncation (`time >= max_steps_in_episode`).
If you build the beam env with `max_steps=96` but search to T=150, **every beam dies at
step 96** and no path longer than 96 is ever found. Rule: any standalone beam/harvest code
must construct `ACS(..., max_steps_in_episode=BEAM_MAX_STEPS)`, distinct from the §2
training `env` (HORIZON=96). The path-validation env should likewise be sized to the path
width (`replay_packed_path`/`check_paths` size it to `best_paths.shape[1]`).

### [2026-06-24] Batched beam = jax.vmap of beam_search.py's beam_step over a wave [WORKS]
To harvest many presentations at once, `jax.vmap(beam_step, in_axes=(0,...,None))` over a
wave axis `W = wave_size * attempts`; per-element temperature schedule `(W,T)` lets attempt
0 run deterministic (temp 0) and the rest Gumbel-explored in the SAME wave. `network.apply`
/ `params` / the env are closed over (not mapped); the inner `jax.vmap(env.step_env)` nests
fine. Two spots in `beam_step` use unbatched-constant ops that are cleaner to rewrite for
the outer vmap: build `is_first` via a batched-slice concat
(`concatenate([sorted_hashes[:1], sorted_hashes[:-1]])` then `.at[0].set(True)`) and use
`jnp.zeros_like(alive)` (not `jnp.zeros(B)`) as the scatter target for `keep`. Per-presentation
early-stop can't `break` inside vmap — pull `terminated.any(axis=1)` / `alive.any(axis=1)`
to host each step and record solve/dead, breaking the wave when all elements are done.
Implemented inline in `experiments/harvest_AC19.ipynb` §5. **Correctness guard:** an
equivalence cell asserts batched temp-0 solve length == serial `beam_search.py` temp-0, and
every harvested path is replayed via `envs.utils.replay_packed_path` before it is written.
(Engine is [unverified] on H100 until the §5 smoke test passes on Colab.)

### [2026-06-25] PPO+Beam harvest pipeline — Phase 1 done (data prep), beam pending [WORKS]
Plan: `experiments/PPO_BEAM_HARVEST_PLAN.md` — run 610model + paper-config beam
(B=16,384, T=150, α=0, 5 seeds, Gumbel) over **all 17,635** greedy-CSV presentations to
get shorter paths + new solves, then min-aggregate d-o-t labels per canonical state.
Phase 1 (no GPU) is built and verified:
- `scripts/lib/canon.py` — the lab canonicalizer (`canonical_pair_nj` etc.) ported VERBATIM
  from `greedy_search.ipynb` cell 2, **numba-optional** (passthrough `njit` shim when
  numba absent, e.g. the repo's py3.9 `../.venv`). Adds env-int8 bridges
  (`env_state_to_strs`, `strs_to_presentation_literal`, `canon_key`). This is the reusable
  `canon()` module the `CLAUDE_ROUGH_PLAN.md` roadmap needs.
- `scripts/build/csv_to_initial_states.py` → `data/greedy_all.txt` (env literals, all 17,635 rows:
  12,681 greedy-solved + 4,954 greedy-unsolved) + `data/derived/paths/greedy_all_index.csv`
  (`line_idx,r1,r2,greedy_solved,greedy_path_length`). Line *i* ↔ index row *i* (verified).
- `scripts/tests/validate_canon.py` (gate G2) reproduces eda P2-11/P0-3 exactly: 202,565 on-path
  states → **25,209 stored == 25,209 canonical (1:1), 0 d-o-t disagreement**.
Run gates with `../.venv/bin/python` (has numpy/pandas, NO jax/numba). The env loader is
idempotent on 24-padded 48-int literals, so `beam_search.py --dataset greedy_all` loads them
unchanged. [TRAP] beam over 17,635×5 seeds at B=16,384 is ≫ the paper's beam budget (paper
ran B=16,384 on ~1,190 only) — use the **width ladder** (cheap B=1,024 pass first, then full
B on the unsolved remainder) and pilot ~200 first. Beam Gumbel **temperature is unspecified
in the paper**; default explore seeds to `--temperature 1.0 --temp_end 0.0`.
