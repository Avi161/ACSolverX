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

### [2026-07-02] greedy_nrel n=3 hot path: incremental canonical + byte-key + manual roll (9x) [WORKS]
Profiling a hard n=3 solve (`cProfile` on `solve_one`, 10k nodes) showed the cost was NOT the search
but: `np.roll` (~20%, its per-call `normalize_axis_tuple` overhead), the `tuple(int(x) for x in r)`
sort key in `canonical_tuple` (~19%, 16M `int()` calls) computed separately from `state_to_key`'s bytes
pass, and `canonical_relator` run on ALL relators of every neighbor though only ONE changes. Fixes, all
correctness-preserving (both test suites still green): (1) `_roll(a,k)=concatenate((a[-k:],a[:-k]))`
replaces `np.roll` in the hot loop; (2) `canonical_key(state)` builds the key in one pass, sorting by
`(len, bytes)` (the +128 byte encoding preserves value order, so bytes-compare == lex-by-value) — no
int-tuple; (3) the solver keys **incrementally** — since a neighbor changes exactly relator `move[0]`
and the popped state's relators are already canonical, recanonicalize only that one and reuse the
parent's byte-parts (`key.split(b"\\x00")`); (4) `visited` stores only `parent_key` (not `(parent,move)`)
and `_retrace` re-derives moves via `get_neighbors(parent)` — retrace runs only on short solved paths.
Result: ~**9x** faster (364 -> ~3300 nodes/s) and ~**2x** less memory (~14.7 -> ~7.5 KB/node), and
throughput is now depth-STABLE (was collapsing as visited/heap grew). Rule: profile before optimizing a
slow search; the win was in the per-node bookkeeping, not the algorithm. The `~7.5 KB/node` memory rate
is the sweep's binding constraint (RAM caps parallel workers before cores do at the 1M tier).

### [2026-07-02] Notebook multiprocessing worker must live in an IMPORTABLE module [WORKS][TRAP]
`calibrate.ipynb` parallelizes probes with `multiprocessing.Pool.imap_unordered`. A worker function
defined inside a notebook cell pickles by `__main__` reference — works under fork (Colab/Linux) but
[TRAP] fails under spawn (macOS default) and in any exec/`-c` harness with `PicklingError: Can't pickle
... __main__`. Fix: put the worker in an importable module (`calibrate_probe.py`, `probe(task)`) and
`from calibrate_probe import probe` — picklable under fork AND spawn, and unit-testable. Also: `Pool(...,
maxtasksperchild=1)` gives a fresh forked child per probe so each `ru_maxrss` is that probe's own peak
(reused workers report cumulative high-water). Parent warms numba before the Pool so forked children
inherit compiled code. On macOS set `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` to test fork locally;
Colab (Linux) needs nothing. And `spread_idx(n,k)` must guard `k<=1` (divide-by-`k-1`) — a dogfood with
`N_EASY=1` caught it.

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

### [2026-07-04] User-facing bundles: only real results; totals count the unit the reader cares about [WORKS][TRAP]
The website shipped leftover probe arms (g@12k, xY/yx/Xy@12k) next to the real r1/r2/x/y@500k
results, and its stats counted (presentation × arm) cells — dataset totals read 10,710 instead of
1190 and the user called the data "messed up with redundancies". [TRAP] A bundle that mixes probe
runs with real results, or counts row-units instead of the domain unit (presentations), reads as
wrong data even when technically consistent. Rule: user-facing bundles carry exactly the arms in
the organized results/ tree; every stat counts presentations, with buckets that partition the
total (solved / unsolvedSearched / coveredViaReps / notAttempted — see groupStats v2 oracle table
in website/tools/test_data.js). The hard-550 ↔ 261-reps link is materialized as rep_idx/class_name
on registry_1190MS.jsonl rows by build_reps_bundle.py::annotate_registry_1190 (grid says 544 of
550 have a rep; 6 boundary idx 634-639 are grid-nontrivial but were run directly — direct wins).

### [2026-07-04] Animation pacing: fixed-duration glides read as a blur; background tabs throttle timers [WORKS][TRAP]
The move player's rotate phase was one 1100ms CSS glide regardless of rotation amount k — the user
couldn't process it. Fix that worked: per-slot stepped motion (240ms tick + 90ms gap, capped 3s by
shrinking tick time, never smoothing) with the ring cut advancing per tick. Rule: when an animation
teaches structure (k rotations), make the motion COUNTABLE — one visible tick per unit. [TRAP] When
verifying animation timing via MutationObserver in a Chrome tab driven remotely, an unfocused tab
clamps setTimeout to ~1s, so tick intervals read ~1000ms regardless of DUR values — verify the
STRUCTURE (number/order of discrete transform targets) from instrumentation, and trust foreground
playback for wall-clock pacing. JS edits also need cmd+shift+r (cache-busting ?v= on index.html
does NOT bust <script src> caches).

### [2026-07-05] AK(3) z=w word sweep: per-form perf differs ~6x; greedy plateaus at total-len 13 [WORKS][TRAP]
The AK(3) "wormhole" sweep (`experiments/stable_ac/one_generator/{ak3_words,ak3_probe,run_ak3_wormhole,
report_ak3}.py`, results under `results/stable_ac/3_generators_w_choices/ak_3_test/`) stabilizes AK(3)
to 3 generators with a chosen `z=w(x,y)` (~95 literature-grounded words × 8 families) and runs the n=3
greedy solver. Two AK(3) forms swept: **textbook** `<x,y|xyx=yxy,x³=y⁴>` (where the paper's words are
provably isolatable) and **rep** `13_1` (`YXyXYx`/`YYYXXXX`, `ms_reps_unsolved` idx 0). [TRAP] Do NOT
extrapolate compute across forms: rep-form n=3 runs ~780–1160 nodes/s and ~5 GB @500k (⇒ ~10 GB, ~21
min @1M), but **textbook-form runs ~4600 nodes/s and only ~2–4 GB @1M (~4.5 min/word)** — a ~6x speed
and ~2.5x memory gap for the *same* group, same solver, just different relator shape. Measure per-form;
a 500k rep probe wildly over-estimated textbook cost. **Finding:** at 100k, **0/194 (word×form) solved**;
the search drives total relator length down to a **plateau at 13** (trivial=3) and sticks — the AK(3)
"second hump." At full 1M the flagship theory words (`xyx`=Fagan, `yxy`, `x³`, `y⁴`, `wk` k=0) each ran
the FULL 1,000,000 nodes and stayed at mtl=13, unsolved — even provably-isolatable words don't let
*ordinary greedy substitution* escape (the Lemma-11 destabilization is a supermove greedy doesn't do).
Rule: for a memory-bounded long sweep, run 1 pool worker with `maxtasksperchild=1` (fresh forked child
per item releases each item's peak RSS; serial in-process accumulates it and OOMs a 17 GB box); size
workers from a per-form 1M base-case measurement, not a cross-form extrapolation. `min_total_len` was
added to `NRelatorSolver` (additive) to rank how close each unsolved word got.

### [2026-07-05] greedy_nrel canonical order DIVERGED from the paper; aligned to Y<y<X<x [TRAP][WORKS]
The port `greedy_nrel.py` canonicalized relators with **natural signed-int order** (`Y<X<x<y`,
3-gen `Z<Y<X<x<y<z`), but the original two-hump code `greedy_search.ipynb` uses **`Y < y < X < x`**
(its `find_minimal_rotation`/`lex_cmp_*` docstrings say so literally; `char_to_array` + `is_less_than`
= group by generator with higher id first, inverse before generator). [TRAP] A port can pass a
solved-set differential oracle yet still use a *different canonical order* — because the order only
breaks priority-queue **ties**, not the rotation+inversion equivalence, so the SOLVED SET is
order-invariant but **node counts / which path is found** are not (borderline-budget cases can flip).
Fixed: added `_paper_lt` (order `Z<z<Y<y<X<x`, higher |gen| first, `-g` before `+g`), routed
`find_minimal_rotation` + `_lex_less` through it, and made `_relator_bytes`/`key_to_state` a
reversible rank-byte encoding whose byte-order == that order (letters→1..6, 0 stays the separator).
**Gold-verified**: `canonical_relator`/`canonical_pair` now match the notebook's `canonical_relator_nj`/
`canonical_pair_nj` byte-for-byte (0 mismatches / 4000+3000 random 2-gen words), a brute-force
paper-order reference for the 3-gen z-extension (0/4000), key round-trip (0/3000). Head-to-head solve
of easy idx 0 (`z∈{x,y,r1,yxy}`, both orders) → identical solved/path_len/nodes/verified. **AK(3)
sweep results are order-INVARIANT** (0 solved, min_total_len=13, nodes=budget under any order), so the
running sweep (natural order, started pre-fix) needn't restart; new/resumed runs use the paper order.
Rule: when porting the GS solver, the canonical **letter order** is load-bearing for paper-faithful
node counts — verify it against the notebook, not just the solved set.

### [2026-07-05] Website views that build innerHTML by string concat need esc() on every record-derived string [WORKS][TRAP]
The 9-phase website overhaul shipped a verdict panel / ranking bars / hard-class table built by string
concatenation into innerHTML (dashboard.js, comparison.js). An adversarial review pass (opus subagent
over `git diff HEAD~10..HEAD`) caught stored XSS: uploaded-JSONL strings (`reg.name`, arm names via
`armSymbol`, which passes unknown arms through) reached those sinks unescaped — and the Append/Replace
upload feature exists precisely to load other people's bundles. [TRAP] viewer.js is immune because it
builds DOM via the `h()`/textContent helper; the trap is only in views that switched to innerHTML
concat for table/markup convenience. Fix: `ACXData.esc()` (the charts.js escaper, exported) wraps every
record-derived interpolation. Rule: in this codebase, any new innerHTML sink gets `esc()` on anything
that ever came from a parsed record — or better, use `h()`. Same review also caught byK[0] counting
never-attempted presentations as "solved by none" under partial uploads (fixed: `attempted - union`),
proving the review-after-implementation convention pays for itself even after per-phase browser gates.

### [2026-07-06] 16 GB Mac: 1M-node greedy runs jetsam the whole background process group [TRAP]
`night_lanes.py` was silently killed 3x, always minutes after `laneC_*@1000000` started. Cause:
gn greedy's visited dict holds ~40x budget entries (pushed children, not expansions) — a 1M-node
run ramps to ~40M entries / 12-16 GB within ~4 min and macOS jetsam kills the PROCESS GROUP (the
background zsh wrapper dies too, reported as "stopped" with no OOM message anywhere; leaked-semaphore
warnings in the log are the only trace). Rule: on the 16 GB box cap gn budgets at ~400k
(~4 GB) and StableSolver at ~400k (24 KB/node); the 0.8-2M tier is Colab-only (50 GB). Size from
VISITED (~40x budget), not from expanded-node counts. A killed runner + resumable JSONL made all 3
kills lossless — the append+flush+fsync convention is what saved the night.

### [2026-07-05] Certificate tamper tests: sign-flipping a length-1 relator is NOT a tamper [TRAP][WORKS]
Lane D's cert-chain smoke "tamper" flipped `states[mid]["relators"][0][0] *= -1` and the verifier
(correctly) accepted it — in the degenerate end-of-chain states the relator had length 1, and
inverting a whole relator is AC2, which certificate state equality quotients out (canonical
equality = reorder + rotate + invert per relator). [TRAP] A tamper test that "passes" this way reads
as a verifier soundness hole but isn't. Rule: semantic tampers for AC certificates must change the
cyclic-word equivalence class — flip an INTERIOR letter of a relator of length ≥ 3 in a middle
state. Same session, related [WORKS]: solve-phase candidate selection "all ≤ tl_cap OR top-N"
ballooned 754 candidates past top=60 in the quick gate (caught because quick mode exercises the
full pipeline); selection is now "shortest top-N among those ≤ tl_cap"
(`plateau_elim.py::phase_solve`). Rule: give every long-sweep script a --quick end-to-end mode and
RUN it before the real launch — both bugs surfaced there, not in unit tests.

### [2026-07-05] Hard-solved "wormhole" word sweep: another clean negative; only relator-derived words solve [WORKS][TRAP]
Sibling of the AK(3) sweep: `run_hard_wormhole.py` throws ~97 `z=w(x,y)` words (8 families) at two
HARD-but-solvable MS targets (idx 625, 610 — 2-gen greedy solves them but only after 60–80k nodes /
300–660-move paths, so there's a real baseline to beat) via `z=w` stabilization + n=3 greedy, at a
100k-node SCREEN (1M full tier specified but **user-gated, NOT run**). Results under
`results/stable_ac/3_generators_w_choices/hard_solved_test/`: idx 625 = 98 words / 4 solved, idx 610 =
99 words / 2 solved — but in BOTH the only solvers are relator-derived (`control` z=r1/r2 + `relhalf` =
a half/inverse of r1) and they **TIE** z=r1's node count (77,395 / 61,082), not beat it. **0 of ~180
generic-family (word×target) runs solved**; every structurally-different word (incl. the theory `wk`
AK-isolation family) plateaus at total length 16–18 (trivial 3). All 6 solve paths reload→replay to
trivial (`gn.verify_path`). [TRAP] `verify_path(states, n_gen)` needs each relator as a **numpy int
array** — JSON-loaded path records are plain Python lists and hit numba `Unknown attribute 'dtype'` in
`inverse_relator`; coerce `[[np.asarray(rel, np.int64) for rel in st] for st in rec['states']]` before
replay. **Finding = greedy substitution does NOT exploit a named `z=w`** (no clever word beats the dumb
z=r1; none solves where dumb words fail) — same conclusion as AK(3); the useful `z=w` is Fagan's
Lemma-11 atomic destabilization, a supermove greedy can't do. Rule: the sweep resumes by
`(idx, word_name, budget)` — a killed run continues with `--phase screen`; `report_hard.py`'s
`finding_section()` recomputes the negative headline from the streams so a regenerate stays honest.
Run it with the repo `.venv` python (has numba), not system `python3`.
