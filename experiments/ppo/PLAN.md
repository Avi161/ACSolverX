# PPO from scratch (PyTorch) — reproduction plan

Branch `experiments/ppo`. **Nothing is implemented yet.** This file pins the exact spec the PyTorch port must match and lists what is still needed before writing code.

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

## What I need from you

1. **Colab spec** — which GPU tier you get (T4 / L4 / A100) and how long a run you're willing to leave up. 1e9 timesteps at 2,380 envs is the paper's budget; I need the tier to say whether that is one overnight run or a week, and to size a shortened first run that still means something. **Local stays capped at a 1,000-node budget** (user directive, and the standing rule in [`CLAUDE.md`](../../CLAUDE.md)) — see below for what that does and does not allow.
2. **Permission to install** `torch` locally, plus `jax`/`flax`/`orbax` **once** (none are in `.venv` today; `requirements.txt` pins the JAX stack but it was never installed). JAX is needed only to load `610model`'s weights for the parity check — not for training. Alternative: do the parity check on Colab too and keep the local venv clean.

Defaults I'm taking unless you say otherwise: W&B goes to project `acsolver`, entity `avigyapaudel045-aisc` (the repo's pinned pair); the table is exactly the format you pasted, with the budget caveat below stated alongside it rather than resolved away.

## Two caveats on the table you pasted

**The denominators are not the same.** Those PPO numbers (457 … 607) and greedy numbers (533 … 640) are counts out of the **1190 Miller–Schupp presentations** — `GS-SUB (1M) NODES = 640` is exactly our `data/ms640_solved.txt`, so that row is already reproduced and is the anchor. `benchmark/subsets/benchmark_subset_10` is 10 rows sampled from our own 66-row benchmark, one per difficulty bin. It is the right **smoke test** — greedy gets 8/10 at 50k nodes and 10/10 at 1M, so there is real dynamic range — but a table in the paper's format needs the full 1190. Plan: subset_10 first to prove the pipeline, then `data/1190MS.txt` for the table.

**"Same budget" needs defining.** Greedy's budget is nodes expanded *per presentation*; PPO's is training timesteps spent *once, across all presentations*, after which inference is nearly free. They are not commensurable, which is why the paper reports them as two separate blocks rather than one ratio. The honest comparison is the one the paper makes — solve count per method, with greedy's node budget stated — and separately, a nodes-equivalent column for the beam-search decode (`beam/beam_search.py` already scores `cum_log_prob + log_softmax + alpha*value` against these checkpoints, so the PPO arm's per-presentation search cost is measurable there).

## The local 1,000-node cap

Everything local is a **correctness** check, never a result. Concretely: env parity is random rollouts (no search at all), policy parity is one forward pass on a fixed batch (no search at all), and the PPO loop is proved on a handful of updates against a hand-computed GAE — none of these need a budget. The only local step that spends nodes is decoding, and there the cap binds: **beam width × depth ≤ 1,000 expansions**, ~10 presentations. Any solve count from a local run is a smoke test and is reported as such; every number that goes in the table comes from Colab.

This costs nothing, because a search at budget `B` is exactly the first `B` expansions of any longer search — a bigger local budget would buy a slower repro, not a different behaviour.

## The branch is local-only

`experiments/ppo` exists in this worktree and nowhere else — it has never been pushed. Colab clones from `origin`, so nothing here can run there until it is pushed, and a push on this repo requires the log ritual in [`CLAUDE.md`](../../CLAUDE.md) (a `## HH:MM:SS UTC · \`<shortsha>\`` section in `logs/DD-MM-YYYY.md`, then a follow-up commit filling in the SHA). Say the word and I'll do the logged push; I'm not pushing unasked.

## Build order once the above is answered

1. `experiments/ppo/env.py` — numba/numpy vectorized ACS: S-move step, dense reward, semantic action mask. Gate: identical `(obs, reward, done)` to the JAX env over random rollouts.
2. `experiments/ppo/policy.py` — torch `RelativeDualRingActorCritic`. Gate: **transplant the `610model` flax params into the torch module and require logits/value to match JAX to ~1e-5 on the same batch.** This is the strongest correctness test available and it costs no training.
3. `experiments/ppo/ppo.py` — GAE + clipped surrogate + clipped value loss + per-minibatch advantage norm, hyperparameters exactly as tabled.
4. `experiments/ppo/eval.py` — greedy-decode and beam-decode a checkpoint over a presentation list; emit jsonl in the `run_baseline.py` schema so the existing analysis reads it.
5. `experiments/ppo/run_ppo.py` + `experiments/notebooks/ppo/` — the standard CONFIG / SETUP / RUN Colab pattern, 60 s heartbeat, restart contract, jsonl + W&B.
6. Table: PPO-SUB-DRT (and `+ AC-19` if the budget allows) against GS-SUB at 10k / 100k / 1M nodes, mean over 5 seeds with the range, on 1190MS.
