# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Code and datasets for *The Two-Hump Problem* (ICML 2026): a JAX/gymnax RL system that
trains PPO agents to trivialize balanced presentations of the trivial group (the
Andrews–Curtis conjecture search problem), using composite **substitution** supermoves
and a domain-specific **Dual-Ring Transformer** policy/value network. Also ships the
AC-19 and AC-1M datasets. Full mathematical background and dataset/CLI docs are in
`README.md` — read it before making non-trivial changes; this file only adds what the
README doesn't cover.

There is no test suite in this repo.

## Setup

```bash
pip install -r requirements-cuda.txt   # NVIDIA CUDA 12
# or: pip install -r requirements-rocm.txt   # AMD ROCm (load `module load rocm/7.2.0` first)
```
`requirements.txt` is the platform-independent base; the two platform files `-r` it and
then pin JAX 0.6.0 + matching jaxlib. `requirements.txt` deliberately excludes three
stacks from the original project (AlphaZero/mctx-az, Google Cloud/GCS, TensorFlow) —
don't reintroduce them for AC-SolverX work.

All commands below assume the repo root as CWD (scripts resolve `data/` and
`ppo_checkpoints/` relative to it).

## Common commands

```bash
# Train (writes Orbax checkpoints under ppo_checkpoints/<name>/ if --ckpt_path given;
# omit --ckpt_path for a no-checkpoint dry run)
python ppo_ac_s.py --ckpt_path my_run --save_every 50
python ppo_ac_s.py --ckpt_path my_run --w 0 --lr 5e-4 --ent_coef 0.01 --seed 14 \
    --cycle_penalty 0.0 --noop_penalty 0.0
# --resume_from/--resume_step: warm-start params from a different checkpoint (finetuning)

# Beam search against a trained/pretrained checkpoint
python beam/beam_search.py --ckpt_path 610model --beam_width 1024 \
    --start 0 --end 634 --out_csv beam_paths.csv

# Validate a checkpoint's stored solve paths actually replay to the trivial presentation
python scripts/check_checkpoint_paths.py --ckpt_path 610model --max_paths 10

# Decompress the large dataset before use
gunzip -k data/AC1M.txt.gz   # -> data/AC1M.txt, stem "AC1M"
```

`greedy_search.ipynb` (GS-Sub baseline) is standalone: numpy + numba only, no JAX/GPU/checkpoint.

## Architecture

**Presentation encoding.** A presentation is a flat `jnp.array` of length
`n_gen * max_length` (2 relators × `max_length`, zero-padded). Generators: `x → 1`,
`y → 2`, `x⁻¹ → -1`, `y⁻¹ → -2`, `0` = padding. `L = 24` is the max relator length used
by both training (`ppo_ac_s.py`) and beam search — the two files' action
packing/unpacking must stay in sync if this changes.

**Action space.** The agent emits a single packed integer action decoded as
`[i, r, k1, k2]`: `i` selects which relator is modified, `r` picks direction
(fwd/inverse-ish), `k1`/`k2` are splice indices into the two relators-as-cyclic-rings.
`envs/ac_moves.py::setup_s_actions` builds the `jax.lax.switch`-dispatched move table;
`envs/ac_s.py::ACS.step_env` calls into it. Decode arithmetic (`action // (4*L)`,
`% (4*L)`, etc.) lives inline in both `ppo_ac_s.py`'s `_env_step` and
`beam/beam_search.py` — keep them matching if you touch either.

**Environment layer** (`envs/`):
- `environment.py` — abstract gymnax-style base; `reset`/`step` take an explicit
  `idx` (index into a dataset of initial states) and an optional `sample`/`probs` for
  weighted random resets, on top of the usual gymnax API.
- `ac_s.py` — `ACS`: the substitution env. `EnvState` carries `x` (the presentation),
  `idx`, `time`, and a per-episode `visited_hashes` ring buffer used for cycle/no-op
  detection (`cycle_penalty`/`noop_penalty` reward shaping — both default `0.0`,
  off unless passed). Initial states are loaded once at construction from
  `data/<initial_states_file>.txt` (Python-literal lists, one per line) and padded to
  `max_length` via `envs/utils.py::change_max_relator_length_of_presentation`.
  Termination = presentation reduced to `n_gen` nonzero entries (the trivial
  presentation).
- `ac_moves.py` — the substitution-move implementation itself (`setup_s_actions`).
- `int_box.py` — minimal integer `Box` space (observation space is int8, not float).
- `utils.py` — presentation padding/length helpers, plus `check_paths` (used by
  `scripts/check_checkpoint_paths.py` to replay stored solution paths in the real env).

**Network** (`network.py`): `RelativeDualRingActorCritic` (relative cyclic positional
attention — the one actually used by `ppo_ac_s.py`) and `DualRingActorCritic`
(absolute positional encoding, alternative/reference). Both treat the two relators as
a "dual ring" with self-attention within each relator and cross-attention between
them, respecting cyclic symmetry.

**Training** (`ppo_ac_s.py`): standard PurpleJaxRL-style PPO. `make_train(config)`
returns a `train(rng)` closure whose body builds env/network/optimizer and returns
`(runner_state, update_step_fn)` — the **outer training loop is a plain Python `for`
over one jitted PPO update at a time** (not a single big `jax.lax.scan`) specifically
so Orbax checkpoint writes can happen between updates (Orbax can't run inside `scan`).
Wrapped through `wrappers.py`: `LogWrapper` (episode stats), `NormalizeVecReward`
(running reward normalization), `LogPathsProbsS` (tracks best solved path per initial
state — this is what gets written into checkpoint `solve_data` and later validated by
`scripts/check_checkpoint_paths.py`). Dataset is fixed to `AC19_extended` and
`max_length` to `L = 24` at the top of `make_train` — not CLI flags.

**Beam search** (`beam/beam_search.py`): loads an Orbax checkpoint (params + config)
and runs beam search per presentation independently, in parallel with jax vmap-style
batching, over a `[--start, --end)` slice of a dataset. Must use the same `L = 24` and
action-packing scheme as `ppo_ac_s.py`.

**Checkpoints**: Orbax `CheckpointManager` with three items — `params`, `solve_data`
(`solved_idx`, `path_lengths`, `best_paths`, sized off the training dataset's line
count), `config`. `ppo_checkpoints/610model/` is the one pretrained checkpoint
committed to the repo (`.gitignore` excludes all other checkpoint dirs); it solves 610
of the first 634 presentations of `data/1190MS.txt`.

## Literature (`literature/txt/`)

`literature/` holds reference PDFs (gitignored — local context only, not shipped in
the public repo). Reading a PDF page-by-page burns context, so every PDF relevant to
active work gets a companion plain-text extraction under `literature/txt/`:

```bash
pdftotext -layout literature/<paper>.pdf literature/txt/<name>.txt
```

`literature/txt/README.md` indexes what's there and what each source covers. When a
new paper becomes relevant to the branch (added to `literature/` or referenced from
elsewhere, e.g. the Obsidian vault's `surf/lit review/`), convert it the same way and
add an entry to that README instead of re-reading the PDF each time.

Current branch (`test/stable-ac-moves`) is exploring **Stable AC moves** (AC4/AC5:
add/remove a trivial generator+relator) and Lucas Fagan's **"change of variables"**
supermove built on Lemma 11 (substitution-and-removal) from arXiv:2408.15332 — see
`literature/txt/change_of_variables_stable_ac.txt`, `literature/txt/math_ml_paper_2408.15332.txt`
(Section 9, ~line 2475), and `literature/txt/mentor_email_stable_ac_ideas.md` for the
concrete baselines to try (2/3/4/5-generator stabilization first, as dumb baselines,
before the Lemma-11 batch-operation version).

## Data conventions

See README.md's "Datasets" section for full details (canonical form, AC19 vs
AC19_extended vs AC1M provenance). Key point when writing code against these files:
`ACS(initial_states_file=...)` takes the bare stem — no `data/` prefix, no `.txt`
suffix — and the file is one Python-literal flat list per line.
