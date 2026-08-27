# The PyTorch PPO reproduction

## What exists

[`experiments/ppo/`](../../experiments/ppo/) is a from-scratch PyTorch reproduction of the
JAX training stack (`ppo_ac_s.py`, `network.py`, `wrappers.py`, `envs/`), built to run PPO
training on Colab / vast.ai GPUs without the JAX toolchain. It imports **nothing** from the
JAX tree — the env, the moves, the Dual-Ring policy and the PPO loop are all
reimplemented — and the JAX files stay byte-for-byte what main ships, kept as the read-only
spec. Eighteen modules, three run docs ([`PLAN.md`](../../experiments/ppo/PLAN.md),
[`SHAPED_REWARD_PLAN.md`](../../experiments/ppo/SHAPED_REWARD_PLAN.md),
[`VAST_AI.md`](../../experiments/ppo/VAST_AI.md)), eleven test files under
[`tests/ppo/`](../../tests/ppo/).

## What is verified

- **Checkpoint transplant parity** against the shipped JAX `610model`: **95/95** arrays
  converted with no silent skips; over 256 states / 10,528 legal actions, action masks
  identical, max |Δ logprob| = **3.79e-05**, max |Δ value| = 2.86e-06, argmax and top-10
  agreement **256/256**. Reconfirmed on an A100 (2.80e-05, distrax shim in place).
- **Move semantics**: the batched torch moves are trace-equal to the scalar spec
  (`acs_spec.py`) over 12,288 transitions.
- **Beam smoke** on an A100 at production settings (1024×150): **530/530** certificates
  produced and replayed through the spec alone.
- **Throughput**: **31.18 s/update** on a Colab A100 (TF32 off) → ~8.7 h per 1,000-update
  arm.

## What was never run

**No training run has ever completed.** The port was built, tested and parity-verified;
the control arm was mid-run on a Colab A100 when the line went quiet, and no result was
committed. The only evaluation number anywhere in this line is the *upstream JAX*
`610model`'s **49/60 on bench60** — and that is a reference line, never a bar: 54 of the
60 rows sit inside the model's own pinned training block (and the decisive counter-signal
is bin 8, where all six rows *are* training rows and it scores **0/6** — difficulty
dominates membership). It is not this port's number.

## The shaped-reward A/B (pre-registered, not run)

`shaping.py` uses the `s20_mk2` feature formula as a potential-based shaping term:
`Φ = −λ·(L + 2·MK + 20·S)`, control `λ = 0` vs treatment `λ = 0.2` — policy-invariant by
the telescoping argument, zero at truncation. λ was calibrated on 97,280 real transitions:
median |Δh| ≈ 10.9 on state-changing transitions → a median shaping term of 2.19 ≈ 22% of
the flat −10 step reward. The full design, including why `xyimb` is excluded, is
[`SHAPED_REWARD_PLAN.md`](../../experiments/ppo/SHAPED_REWARD_PLAN.md).

## The held-out training set

`heldout.py` builds `AC19_extended_ho60` (156,762 → 156,708 rows) by removing every
bench60 row. The subtle part is the pin: the naive prefix-walk that derives the 634-row
MS block collapses to 0 on the filtered file (bench60's bin-0 row is line 0 of both
files), silently changing the training recipe in every arm — `ms_prefix_length` re-derives
the pin as a membership walk instead (634 − 54 = **580**), and the tests assert the trap
stays live. Exact-match removal cannot remove Aut-equivalent rows elsewhere in the 156k;
that limitation is documented, not solved.

## Deliberate deviations from upstream

Recorded so a bit-for-bit comparison knows where to look:

- **64-bit dedup hash** in the beam (upstream: 32-bit; at B×T = 153,600 states, int32
  birthday collisions are near-certain and each kills a live beam). Can only help.
- **einsum + gather** for relative positions instead of the upstream `[B,H,L,L,Dh]`
  tensor (several GB at production minibatch). Identical arithmetic.
- **TF32 off** for parity checks (upstream pins float32 matmul precision; TF32's ~1e-3
  error can flip a top-k tie). Training arms turn it on.
- **A 6-line `Categorical` shim** instead of installing distrax, verified bit-identical
  against distrax 0.1.9 (and asserted to return `log_softmax(l)`, not `l`).

## Running it

```
python -m experiments.ppo.run_ppo --stage {convert|parity|train|beam_eval|report} [--config X.json]
python -m experiments.ppo.make_arm_notebooks      # regenerates the two arm notebooks
python -m experiments.ppo.arm_config s20mk2 --full --out s20mk2.json   # after the line above
python -m experiments.ppo.verify_beam results/ppo/**/beam-*.jsonl      # no torch, no GPU
```

The Colab driver is [`experiments/notebooks/ppo/ppo_baseline.ipynb`](../../experiments/notebooks/ppo/ppo_baseline.ipynb);
the two arm notebooks are **generated, not committed** (they differ from the template in
exactly the reward knobs, which is the point of generating them). The bare CLI defaults
are deliberately harmless (beam 8, `1190MS`) — a real run goes through a config; see
[`VAST_AI.md`](../../experiments/ppo/VAST_AI.md).

## Test status, and what is not here

`pytest tests/ppo` with CPU torch: **~149 passed, 2 skipped** (the distrax-shim
cross-check skips without JAX installed; the transplant end-to-end skips without the
gitignored `--stage convert` output). Without torch, the whole directory skips at
collection, which is what keeps the main CI gate on numpy + numba. Sentinel worth knowing:
`test_transplant_covers_every_checkpoint_array` **does** run against main's tracked
checkpoint metadata — if it ever starts skipping, the checkpoint went missing.

Left on the source branch, with the condition for bringing each back:

- `tests/ppo/test_arm_notebooks.py` — reads the two *committed* arm notebooks from disk;
  returns verbatim if the arms are ever committed.
- `tests/ppo/conftest.py` — exists only to no-op a session-autouse `numba_warm` fixture in
  a root `tests/conftest.py` this repo does not have; comes back the day such a conftest
  is added.
- `arm_config.py` therefore ships without automated coverage, and it only works after
  `make_arm_notebooks` has run — a documented two-step launch, not a bug.

House rule: no `__init__.py` under `tests/`, so test-file basenames must stay globally
unique across `tests/` and `tests/ppo/`.
