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

## Result persistence & resumability (append-only JSONL)

Any script that produces per-item results over a long sweep (per-presentation greedy/beam
runs, dataset labeling, evaluation over MS(1190) / AC-19 / AC-1M) **must be crash-safe and
resumable** — these will run on cloud servers where jobs get pre-empted or die, and we cannot
afford to lose or recompute finished work.

- **Write JSONL, not JSON, for per-item result streams:** one complete JSON object per line,
  one line per item (e.g. per presentation `idx`). Prefer `.jsonl` over `.json` whenever the
  output is a stream of records.
- **Append-only, flush per line:** open in append mode; after each record write
  `json.dumps(obj) + "\n"`, then `f.flush()` (and `os.fsync(f.fileno())` for cloud/NFS). A
  crash then loses at most the single in-flight item.
- **Resume from the last object:** on startup, read the existing `.jsonl`, collect completed
  ids, skip them, and continue; ignore a trailing truncated/corrupt line (recompute that one
  id). Re-running a finished sweep is a no-op; a killed sweep continues where it stopped.
- **One stream per method/arm, merged at report time.** Never rewrite a whole file to update
  one field — that isn't crash-safe. Cheap, fully-derived artifacts (index-only labels) may
  stay `.json`. Keep the tiny shared helpers (`jsonl_done_ids`, `jsonl_append`) in one module
  and reuse them across every sweep.

## PLAN conventions (authoring & feedback)

Writing an implementation plan, or reviewing one, follows the convention in
**`.claude/conventions/plan-conventions.md`**. In short: write a `PLAN.md` before coding
(advisor before and after, base-case before any full sweep, a `[ ]`/`[X]`/`[X][-]` TODO
checklist, claims grounded in the repo); and when asked for feedback, write a severity-ordered
critical review (WHAT → WHY → HOW) to a sibling `<PLAN_STEM>_FEEDBACK.md`. Open that file before
authoring a plan or giving feedback.

## Testing conventions (independent verification — make the code strong)

For any non-trivial algorithm — anything where a silent bug **corrupts** rather than degrades
results, and everything we present as a finding — follow **`.claude/conventions/testing-conventions.md`**.
In short: get your own suite green, then **launch a separate adversarial subagent to author an
INDEPENDENT suite in a separate test file**, black-box (spec + public API only, forbidden from reading
the implementation internals or your tests) so it builds its own oracle and can catch shared blind
spots. **Never leak a load-bearing design choice** to that agent (it will confirm, not check it) —
oracle such choices from an *independent source* (a second reference impl, the paper, the production
env) and triangulate ≥2 ways. Tag each check by how independent it is; state when the executable gold
gate is deferred. Open that file before writing tests for, or claiming correctness of, such code.

## Lessons Learned

### [2026-07-02] Independent test subagents: give the contract, never the mechanism [WORKS][TRAP]
Building Phase 2 `greedy_nrel.py` I launched an "independent" subagent to write tests — but the
prompt **stated my n=3 move-set scheme** ("unordered pairs, lower-index leader, dual-slot emit").
advisor() caught it: the agent will now **confirm that scheme, not check it** — I leaked the one thing
I needed independence on, so its "all pass" certifies primitives + plumbing, NOT the design choice.
[TRAP] Handing a load-bearing design/algorithm decision to the independent verifier turns adversarial
verification into rubber-stamping. Rule: give the independent agent the **contract** (public API +
invariants) and the **problem/math**, never the **mechanism**; forbid it from reading the impl
internals or my test file; have it derive its oracle from an independent source. For a load-bearing
choice, oracle it from a *different* source and **triangulate ≥2 ways**. Codified in
`.claude/conventions/testing-conventions.md` (linked from "Testing conventions" above) — consult it by
default for any non-trivial algorithm. Corollary [WORKS]: for the AC substitution move I triangulated
across THREE agreeing implementations — notebook `get_neighbors_nj` (executable), env
`envs/ac_moves.py::s_move` (read statically; `neighbour = rot(r0)·rot(r1^±)` into slot `i`), and mine
— which is far stronger than any one self-check.

### [2026-07-02] verify_path that shares get_neighbors can't catch move-gen bugs; env s_move is the gold gate [WORKS]
The verification ladder for the greedy solvers: `solved` (reached trivial, could be a false positive)
→ `verify_path` (independent replay) → JAX env `check_paths`/`s_move` (gold). Critically, `verify_path`
**recomputes neighbors with the same `get_neighbors` the solver uses**, so it catches search/parent-
pointer bugs but is **blind to a move-generation bug** (its own docstring says so). Only the real env
`envs/ac_moves.py::s_move` catches move-gen — and that env's shipped `s_move` is **hardcoded to splice
`r0·r1`** (`rotate_relator_k(0,…)`/`(1,…)`), so it structurally cannot do the `(r_i, z)` n=3 moves;
plus JAX isn't installed on the greedy/CPU boxes. So the n=3 move set has **no executable gold check
until Phase 4** generalizes `s_move`. Rule: never let "unit tests pass + n=3 sanity solves" read as
"n=3 moves gold-verified" — n=2 move-gen is verified (differential oracle + env source triangulation);
n=3 is a faithful-by-construction generalization of the env convention, gold check deferred. Say this
explicitly in any n=3 coverage headline.

### [2026-07-02] Notebook `reduce_relator_nj` reads past the array on full cancellation [TRAP]
`baseline_n2/greedy_ac.py::reduce_relator_nj` (lifted verbatim from `greedy_search.ipynb`) reads
`rel[add_index+1]` at the index-0 wrap branch; when a word **fully cancels to empty** this is out of
bounds and (numba, no bounds check) fabricates a **garbage length-1 relator** — e.g. splicing `yxXY`
yields a phantom `Y` "neighbour". The n-relator port's `greedy_nrel.reduce_relator` is stack-based and
returns empty correctly. [TRAP] When differential-testing against the notebook, reduce raw notebook
splices with the **correct** reducer and **drop full-cancellation results on both sides** before
comparing — else the phantom neighbours cause false mismatches. On real balanced MS presentations full
cancellation doesn't arise, so the solved-set differential oracle is unaffected (verified: 0 mismatches
incl. hard idx 600 @ 9505 nodes). Do not "fix" the notebook file — keep it verbatim; the port is where
correctness lives.

### [2026-07-02] Persist solved paths for n≥3, not just a verified flag [WORKS]
The n=2 greedy Phase 0.5 streams (`experiments/stable_ac/one_generator/baseline_n2/`) store only
`path_len`/`path_verified` — the actual move sequence is computed, checked by in-process
`verify_path`, then **discarded**. Accepted for the n=2 reproduction (we only need the solved-count
+ length distribution), but it means no solve can be re-audited, replayed, fed to the JAX
`envs/utils.py::check_paths` gold gate, or shown to anyone after the run. Rule: for **n≥3** — and any
run whose solves we present as findings (esp. the `z=w` class-solves on the 261 reps) — the solver
MUST persist the retraced path to disk: a sidecar `results/paths_<arm>_<tier>.jsonl` keyed by `idx`
holding the move+state sequence (see PLAN.md Phase 2 "Persist the path" + Phase 3). Every reported
solve must point at a stored, re-runnable path. A `path_verified:true` boolean is proof to *this run*;
a stored path is proof anyone can re-run — those are not the same thing, and a headline "trivialized
class `<name>`" claim needs the latter.

### [2026-07-01] Subagent model — use Sonnet 5 for research/exploration [WORKS]
When launching Explore / general-purpose subagents for read-and-report codebase
exploration, pass `model: sonnet` (Sonnet 5) rather than inheriting the Opus session
default. Read-and-report exploration does not need Opus, and Sonnet is cheaper/faster
for it. Rule: for any Explore/search subagent, set the `model` override to `sonnet`
unless the task genuinely requires Opus-level reasoning (e.g. adversarial verification,
hard design synthesis).
