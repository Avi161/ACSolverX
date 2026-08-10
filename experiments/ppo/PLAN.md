# PPO from scratch (PyTorch) — reproduction plan

Branch `experiments/ppo`. **The port is written, tested and pushed; no replication number exists yet.** This file pins the exact spec the PyTorch port matches, records what building it turned up, and says what is left to run.

Repo-scoped [`CLAUDE.md`](../../CLAUDE.md) says this branch's work is CPU + numba only, no JAX/GPU/PPO, and that `ppo_ac_s.py` / `network.py` are "a spec to port from, never import". The user has explicitly asked for PPO here, so **this branch is a deliberate exception to that rule** — the no-PPO line applies to the greedy/heuristic branches, not to `experiments/ppo/`. The "spec to port from, never import" half still holds: the JAX files stay read-only references.

## Step 0 — the only thing being reproduced first

The Two-Hump **baseline**, unchanged: same env, same network, same hyperparameters, same reward. No `s20_mk2`, no CoV, no shaping. The point is to prove the PyTorch stack is faithful before any of our own ideas are attached to it. Heuristic rewards come after this passes.

## The spec, as pinned from the code

### Environment — `envs/ac_s.py` (`ACS`), instantiated in `ppo_ac_s.py:46-55`

| knob | value |
|---|---|
| `n_gen` | 2 |
| `max_length` (per relator, `L`) | **24** |
| observation | flat `int8` `(48,)` = `[r1(24) | r2(24)]`, alphabet `{-2,-1,0,1,2}` |
| action | `[i, j, k1, k2]`; packed index `(((k1-1)*L + (k2+j)*(-1)^j) * 4) + (i*2 + j)`, **2304** total |
| reward (dense) | `-clip(count_nonzero(x), 0, 10) * (1-terminated) + 1000 * terminated` |
| terminated | `count_nonzero(x) == n_gen` |
| truncated | `time >= max_steps_in_episode` = **96** |
| initial states | `data/AC19_extended.txt` — **156,762** presentations |
| `cycle_penalty` / `noop_penalty` | 0.0 / 0.0 (off in the baseline) |

Wrappers, in order: `LogWrapper` → `NormalizeVecReward(gamma)` → `LogPathsProbsS(NUM_ENVS)`. `NormalizeVecReward` (`wrappers.py:319`) divides reward by the running std of the discounted return accumulator — a Welford update over the batch, **not** a reward-mean subtraction. Getting this wrong changes the value scale and nothing will match.

Env reset is not uniform: `ppo_ac_s.py:93-98` pins envs `0..633` to fixed `init_states[idx]` (`sample=False`) and lets the remaining 1,746 sample. **The 634 is not arbitrary** — `data/AC19_extended.txt`'s first 634 lines are exactly the first 634 lines of `data/1190MS.txt` (verified: prefix match to line 634, first divergence at 635), and those 634 are precisely the MS presentations that appear anywhere in the extended file at all (`634 / 1190`, indices `0..633`, contiguous). So the pin means **one env permanently dedicated to each Miller–Schupp target present in the training set**, while the other 1,746 sample the full pool. The port must copy this, and must derive 634 from the data rather than hardcoding it.

### Network — `network.py` (`RelativeDualRingActorCritic`)

2 layers · 4 heads · `head_dim` 8 · `mlp_dim` 32 · `embedding_dim` 32 · `vocab_size` 5 · `max_len` 24 · gelu. Shared `Embed(5, 32)` applied to `relator + 2`. Each block: pre-LayerNorm → cyclic **relative-position** self-attention per ring (learned `rel_emb [H,L,Dh]`, distances taken mod the ring's true length) → cross-attention both directions → residual MLP. Critic: masked-mean pool per ring → concat(64) → `Dense(256)` → `Dense(256)` → `Dense(1)`, orthogonal `sqrt(2)`/`sqrt(2)`/`1.0`. Actor: outer product of the two rings → `Dense(128)` → `Dense(4)` orthogonal `0.01` → flatten to 2304, invalid actions set to `-1e9`.

The action mask is semantic, not just padding: `(i,j)` is legal iff `r1[i] == -r2[j]` (type 0) or `r1[i] == r2[j]` (type 1), and both positions are non-pad.

### PPO hyperparameters — `ppo_ac_s.py:337-360`

| knob | value |
|---|---|
| `LR` | `5 * 5e-4` = **2.5e-3**, `ANNEAL_LR = False` |
| `NUM_ENVS` | `1190 * 2` = **2380** |
| `NUM_STEPS` | 96 |
| `TOTAL_TIMESTEPS` | 1e9 ⇒ **4,377 updates** |
| `UPDATE_EPOCHS` / `NUM_MINIBATCHES` | 3 / 8 (minibatch = 28,560) |
| `GAMMA` / `GAE_LAMBDA` | 0.999 / 0.95 |
| `CLIP_EPS` / `ENT_COEF` / `VF_COEF` | 0.2 / 0.01 / 0.5 |
| `MAX_GRAD_NORM` | 0.5, applied **before** Adam (`optax.chain`) |
| optimizer | Adam, `eps = 1e-5` |
| advantage | normalized **per minibatch**, not per batch |
| value loss | PPO2 clipped: `0.5 * max((v-t)^2, (clip(v)-t)^2)` |
| `SEED` | 14 |

## The `610model` checkpoint — provenance, read off disk

`ppo_checkpoints/610model/{900,950,1000}` turns out to be readable without orbax: the `config` item is saved with `ocp.args.JsonSave`, so `1000/config/metadata` is plain JSON, and `*/array_metadatas/process_0` carries every array's shape. What that says:

- **It is this exact baseline.** The saved config is `ppo_ac_s.py`'s config dict verbatim — `LR 0.0025`, `NUM_ENVS 2380`, `NUM_STEPS 96`, `UPDATE_EPOCHS 3`, `NUM_MINIBATCHES 8`, `MINIBATCH_SIZE 28560`, `GAMMA 0.999`, `GAE_LAMBDA 0.95`, `CLIP_EPS 0.2`, `ENT_COEF 0.01`, `VF_COEF 0.5`, `MAX_GRAD_NORM 0.5`, gelu, `ANNEAL_LR false`, `CYCLE_PENALTY 0.0`, `NOOP_PENALTY 0.0`, `NUM_UPDATES 4376`. Only the seed differs from the script default: **`SEED 142`**, not 14.
- **It is upstream, not ours.** `ENTITY "Math-AI-Caltech"`, `PROJECT "Some_Experiments_PPO"` — a Caltech run, not one of our W&B runs.
- **It is the DRT arm.** The `params` shapes are `RelativeDualRingActorCritic` exactly: critic `Dense_0 [64,256] → Dense_1 [256,256] → Dense_2 [256,1]`, actor `Dense_3 [64,128] → Dense_4 [128,4]`, plus `RelativeDualRingBlock_*`. So `610model` is `PPO-SUB-DRT`, and the name matching the `605–610` range of the `+ AC-19` row is consistent but not proof.
- **Step 1000 is where it stopped, not the end.** `NUM_UPDATES` is 4376 and `max_to_keep=3` at `save_every=50` explains why only 900/950/1000 survive. So this is ~23% of the paper's budget (≈229M of 1e9 timesteps) — useful as a parity fixture, not as a reproduction of the table row.
- **One residual mismatch.** `solve_data` is length **157,217**, but today's `data/AC19_extended.txt` is 156,762 lines. The training file was 455 rows larger than the one in the repo. Params parity is unaffected (weights don't depend on `init_states`), but a byte-exact *retrain* of this checkpoint is not possible from the repo as it stands.

## What is built

| file | what it is | gate |
|---|---|---|
| `acs_data.py` | presentation loading, re-padding, and `ms_prefix_length` (the 634 pin, derived) | `tests/ppo/test_env.py` |
| `acs_moves.py` | batched S-move: reverse, cyclic reduce, rotate, concatenate, Booth lex-min | trace-equal to `acs_spec.py` over 12,288 transitions |
| `acs_spec.py` | scalar transliteration of `envs/ac_s.py` + `ac_moves.py`, test support only | it *is* the oracle |
| `acs_env.py` | `VecACS` — the env plus all three wrappers fused | `tests/ppo/test_env.py` |
| `policy.py` | torch `RelativeDualRingActorCritic` + the semantic action mask | `tests/ppo/test_policy_and_ppo.py` |
| `transplant.py` | orbax/flax params → torch `state_dict`, 95/95 arrays, no silent skips | `test_transplant_covers_every_checkpoint_array` |
| `ppo.py` | GAE, clipped surrogate, PPO2 value loss, per-minibatch advantage norm | GAE checked against the hand-written recursion |
| `beam.py` | beam decode + resumable jsonl (`repair_jsonl` before any append) | `tests/ppo/test_beam.py` |
| `run_ppo.py` | the four stages `convert` / `parity` / `train` / `beam_eval` | `tests/ppo/test_notebook.py` |
| `results_table.py` | the replication table, from beam jsonls over `1190MS` and nothing else | `tests/ppo/test_results_table.py` |
| `verify_beam.py` | certificate check: replays every solved row through `acs_spec` alone | `tests/ppo/test_verify_beam.py` — tampered certificates must fail |
| `../notebooks/ppo/ppo_baseline.ipynb` | the A100 Colab driver, CONFIG / SETUP / RUN / TABLE | executed cell by cell in `test_notebook.py` |

Answers to what this section used to ask for: the GPU is an **A100**; `torch` is installed locally, and `jax`/`flax`/`orbax` are not — the cross-framework parity gate runs on Colab, where they ship with the image. W&B goes to project `acsolver`, entity `avigyapaudel045-aisc`.

## What building it turned up

- **Upstream's Booth rotation is not lex-min.** `ac_moves.py`'s "Booth" step returns a rotation the textbook algorithm does not, on words the search actually reaches. The port reproduces upstream's function, deliberately — a correct lex-min would be a *different environment*, and every checkpoint and paper number was produced under upstream's. `test_upstream_booth_is_not_lex_min` pins the divergence so nobody "fixes" it.
- **The paper's "+ AC-19" arm is `data/AC19_extended.txt`, not `data/AC19.txt`.** The extended file opens with the first 634 lines of `1190MS` verbatim, which is exactly `parallel_sample[:634] = False`. Raw `AC19.txt` shares **no** prefix with `1190MS` (`ms_prefix_length` = 0) and contains only 171 of the 1190 MS rows anywhere in it — a run on it pins nothing, so it is not a row of the table. It is available in the notebook as a clearly-labelled extra.
- **`NUM_ENVS = 2380` for the `1190MS` arm is a reconstruction.** Only the AC-19 arm's config shipped with `610model`. `1190 * 2` is upstream's own expression and gives one pinned env per MS presentation plus one sampler, but nothing on disk confirms the 1190MS arm ran at that width.
- **`SEED` is 142, not the script's 14** — the shipped checkpoint's saved config says so, and `DEFAULT_CONFIG` follows the checkpoint.
- **The shipped `610model` is a free replication.** It is step 1000 of 4376 and named for ~610 solves, so beam-decoding it over `1190MS` should land near the paper's 607.2 **with no training at all**. That is the notebook's third rung and the gate on everything after it: a few off is consistent with the two documented beam deviations, tens off means the env, the net or the decode is wrong.
- **The beam jsonl name is the resume key, so it carries the policy.** `run_beam` skips presentations already in the file, so a name that omitted the checkpoint would make seed 2 write nothing and report seed 1's count. `beam_tag` folds in the checkpoint stem *and its update count*, since a `.pt` is a moving target.

## Two caveats on the table you pasted

**The denominators are not the same.** Those PPO numbers (457 … 607) and greedy numbers (533 … 640) are counts out of the **1190 Miller–Schupp presentations** — `GS-SUB (1M) NODES = 640` is exactly our `data/ms640_solved.txt`, so that row is already reproduced and is the anchor. `benchmark/subsets/benchmark_subset_10` is 10 rows sampled from our own 66-row benchmark, one per difficulty bin; it is a fine smoke test but its count is not comparable to anything in the table. So every number here is a beam decode over the full `data/1190MS.txt`, and `results_table.py` refuses to read a run over any other file. The pipeline is proved by the tests and by the shipped-checkpoint rung, not by a smaller denominator.

**"Same budget" needs defining.** Greedy's budget is nodes expanded *per presentation*; PPO's is training timesteps spent *once, across all presentations*, after which inference is nearly free. They are not commensurable, which is why the paper reports them as two separate blocks rather than one ratio. The honest comparison is the one the paper makes — solve count per method, with greedy's node budget stated — and separately, a nodes-equivalent column for the beam-search decode (`beam/beam_search.py` already scores `cum_log_prob + log_softmax + alpha*value` against these checkpoints, so the PPO arm's per-presentation search cost is measurable there).

## The local 1,000-node cap

Everything local is a **correctness** check, never a result. Concretely: env parity is random rollouts (no search at all), policy parity is one forward pass on a fixed batch (no search at all), and the PPO loop is proved on a handful of updates against a hand-computed GAE — none of these need a budget. The only local step that spends nodes is decoding, and there the cap binds: **beam width × depth ≤ 1,000 expansions**, ~10 presentations. Any solve count from a local run is a smoke test and is reported as such; every number that goes in the table comes from Colab.

This costs nothing, because a search at budget `B` is exactly the first `B` expansions of any longer search — a bigger local budget would buy a slower repro, not a different behaviour.

## What is left to run

The notebook's `STAGES` list is the order, cheapest gate first. Nothing below has been run yet.

1. **`parity`** — minutes. Closes the one gate that cannot close locally: same weights, same batch, JAX vs torch, TF32 off. Everything it can check without JAX already passes in `tests/ppo`.
2. **`beam_upstream`** — well under an hour on an A100. Beam-decode the shipped `610model` over `1190MS` at 1024 × 150. Expect ~605–610. **This is the gate on training**: if it lands there, env + net + weights + decode are all correct and the only remaining variable is optimisation.
3. **`train`** — the long pole. `MAX_UPDATES = 1000` (where upstream's own artefact stopped) per (arm, seed), resumable across sessions via the checkpoint + Drive mirror. Run one seed first and read `sps` from the heartbeat before committing to five. 4376 updates × 5 seeds × 2 arms is not one Colab session and is not claimed to be.
4. **`beam_trained`** — one beam per trained checkpoint, same 1024 × 150 over `1190MS`.
5. **`verify_beam`** — `python3 -m experiments.ppo.verify_beam results/ppo/beam-*.jsonl` on any machine, no GPU, no torch. Every solved row is replayed through `acs_spec` alone and must reach a trivial presentation at exactly its recorded `path_length`. Run it before quoting any count: the beam gathers its path through 150 steps of dedup and no-op kills, and a mis-gathered path still looks like a path.
6. **The table** — `results_table.py` prints it from the beam jsonls, with the paper's published rows alongside as a clearly-labelled reference. Training-time `num_solved` is refused: on the AC-19 arm it counts over 156,762 rows, not 1190.

**Runtime, measured where it could be.** One beam step is one forward of `beam_width` states; locally that is 240 ms at batch 1024 on CPU (137,765 params, 2 blocks), so the whole `beam_upstream` worst case — 1190 × 150 forwards with nothing solving early — is ~12 h on this laptop and, on an A100 where a model this small is launch-bound rather than FLOP-bound, minutes to tens of minutes. Training is heavier: 228,480 states collected per update plus 3 epochs of forward+backward over the same, so roughly 2.3M forward-equivalents per update, which puts a 1000-update arm in the low hours. Both are estimates from a CPU measurement, not from a GPU: the beam heartbeat prints pres/min inside the first minute and the training heartbeat prints `sps`, and those are the real numbers. `ALLOW_TF32 = False` is deliberate — upstream pins `jax_default_matmul_precision=float32`, and TF32's ~1e-3 relative error can flip a top-k tie at the margin — so it costs throughput on purpose until the replication number lands.

The greedy block of the table (`GS-SUB` at 10k / 100k / 1M nodes) is not produced here — that is `experiments/notebooks/greedy_baseline.ipynb` over the same 1190 denominator, and `GS-SUB (1M) = 640` is already reproduced as `data/ms640_solved.txt`.
