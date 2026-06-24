# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

AC-SolverX trains JAX/PPO reinforcement-learning agents to trivialize balanced
presentations of the trivial group (the Andrews–Curtis conjecture search
problem) using composite **substitution** ("S-move") supermoves and a
**Dual-Ring Transformer** policy/value network. `README.md` is authoritative for
the math background, dataset semantics, and CLI flag reference — read it for any
of those. This file captures the cross-file architecture and invariants that the
README does not.

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
python scripts/check_checkpoint_paths.py --ckpt_path 610model --max_paths 10

# Greedy-search baseline (GS-Sub): open and run greedy_search.ipynb (numpy+numba only, no JAX/GPU)

# AC-1M ships gzipped; decompress before using stem "AC1M"
gunzip -k data/AC1M.txt.gz
```

There is **no unit-test suite, linter, or formatter** configured. Correctness of
a trained model is verified empirically by `scripts/check_checkpoint_paths.py`,
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

`beam/beam_search.py` and `scripts/check_checkpoint_paths.py` both do a two-stage
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

## Lessons Learned

> Append a dated entry after any task that errored, needed a retry, or revealed a
> non-obvious pattern. Format: `### [YYYY-MM-DD] Topic` → what happened → rule.
> Tag `[WORKS]` / `[TRAP]`; never delete entries, mark stale ones `[SUPERSEDED]`.

(none yet)
