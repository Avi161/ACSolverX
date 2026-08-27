# Running a PPO arm on vast.ai

The two arms of [`SHAPED_REWARD_PLAN.md`](SHAPED_REWARD_PLAN.md) were written for two Colab A100s. This is the same run on a rented box instead. Nothing about the experiment changes; only the machine and the way the config reaches the runner do.

## 1. Which GPU — read this before renting anything

**This workload is bound by memory bandwidth and kernel-launch latency, not by FLOPS or VRAM.** The network is 137,765 parameters — 2 transformer blocks, `embedding_dim` 32, `mlp_dim` 32, `head_dim` 8, ring length 24. An update collects 228,480 transitions through 96 *sequential* env steps, then does 3 epochs × 8 minibatches with `MICRO_BATCH = 2048` gradient accumulation, so roughly 335 optimiser micro-steps per update, each one a stack of tiny matmuls. Every one of those is a kernel launch on a matrix too small to fill an A100. `PLAN.md` reached the same conclusion from the other direction: "on an A100 where a model this small is launch-bound rather than FLOP-bound".

Three consequences, and they are the whole GPU decision:

- **VRAM is free headroom you do not need.** Gradient accumulation at micro-batch 2048 keeps the footprint to a couple of GB. A 24 GB card is already oversized. Paying for capacity buys nothing.
- **Memory bandwidth is the number to sort on.** It sets how fast those thousands of small kernels stream their operands.
- **Clock speed matters more than usual**, because launch overhead is a per-kernel fixed cost and there are a great many kernels.

### The GB10 offers: no

| | GB10 (the listings) | A100 40 GB | RTX 4090 | RTX 5090 |
|---|---|---|---|---|
| memory bandwidth | **117–120 GB/s measured** (273 GB/s raw spec) | ~1,555 GB/s | ~1,008 GB/s | ~1,792 GB/s |
| memory | 119 GB unified LPDDR5X | 40 GB HBM2e | 24 GB GDDR6X | 32 GB GDDR7 |
| CPU | Cortex-A725 (aarch64) | x86 | x86 | x86 |

The GB10 is a **capacity** part — a DGX Spark SoC whose selling point is fitting a very large model in 119 GB of unified memory on a desk. That is the exact opposite of this job. Its own listing reports **116.7 and 120.5 GB/s**, which is roughly **an order of magnitude below an A100** and below every RTX card worth considering; against the bandwidth-bound workload above that is close to a linear slowdown. The 119 GB you would be paying for is unusable here. On top of that it is `aarch64` with CUDA 13, so the PyTorch wheel is the ARM build rather than the standard one — install friction on the one run you want to be boring.

At $0.34–0.38/hr it looks cheap. It is not cheap per unit of this experiment, and an 8.7 h run stretched by even 3× costs far more in wall-clock than the price gap saves.

### What to rent instead

**Yes, your RTX cards work — and they are a good fit.** A 4090 or 5090 has the bandwidth and the clocks this workload wants, and 24/32 GB is ample. But *which* card is the second question. The first one is:

> **Both arms must run on the same hardware.**

The control is mid-run on a Colab A100. The arm notebooks' own header says they "differ in exactly four lines — ARM, SHAPING, LAMBDA, and the Drive folder — so any difference in their results is the reward and nothing else." That guarantee does not survive changing the GPU architecture underneath one arm. `ALLOW_TF32` is `True` for training, so both arms already run through tensor cores, and different architectures give different kernels, different reduction orders, different rounding. At **one seed** — which is what §2 of the plan specifies to start — a hardware difference between arms is a confound sitting directly on top of the effect you are measuring, and there is no way to separate them afterwards.

In preference order:

1. **One vast machine with 2× identical GPUs, run both arms on it** (one per GPU, `CUDA_VISIBLE_DEVICES=0` and `=1`). Identical silicon, driver, torch build, and CPU. The Colab control becomes a free extra replicate rather than the comparison. At ~9 h this is roughly $10–25 all-in depending on the card, and it is the only option that keeps the pre-registered guarantee intact. **Recommended.**
2. **A single A100 on vast for the treatment.** Same `sm_80` architecture as the Colab control, so the mismatch is small — though not zero, since Colab's A100 and a rented one can differ in driver and torch build.
3. **Treatment on an RTX, control left on Colab.** Fastest and cheapest, and the one to avoid: it is the case where the hardware and the reward change together.

If you take option 1, pick on bandwidth and price: a 2× RTX 5090 box is the strongest, 2× 4090 is the value pick, 2× A100 is the conservative pick. **One check before you commit to 5090s:** confirm the template's torch is `cu128` or newer, since Blackwell consumer cards need `sm_120` support — `python -c "import torch; print(torch.__version__, torch.cuda.get_device_name(0))"` on the box, before starting anything. A 4090 runs on any recent build.

## 2. vast.ai from zero

1. **Account and credit.** Sign up at vast.ai, add credit under Billing. You are billed per second while an instance exists — including while it sits idle and including its disk — so the habit that matters is destroying instances you are done with.
2. **Search.** The search page lists offers from independent hosts, so quality varies and the filters are the product. Set **GPU model**, **# of GPUs = 2** (for option 1), and **disk ≥ 40 GB**. Then filter to **verified** hosts with **reliability > 98%**, and set **max duration** comfortably above 12 h so the host cannot reclaim the box mid-run. Sort by `$/hr`. The `DLPerf` and `DLP/$/hr` columns are a generic deep-learning composite — they do **not** describe a 137k-parameter launch-bound model, so treat them as noise here and sort on price among cards you have already chosen on bandwidth.
3. **On-demand, not interruptible.** Interruptible (bid) instances are ~2–3× cheaper and this code *is* resume-safe, so it is genuinely viable later. For a first-ever vast run, take on-demand: you are learning the platform and an eviction mid-run is a failure mode you do not need yet.
4. **Template.** Pick a **PyTorch** template (CUDA 12.x). Do not pick a bare CUDA image — you would be installing torch by hand for no reason. Launch with **Jupyter** if you want to run the arm notebook as-is, or **SSH** for the headless path below.
5. **Connect.** Add your SSH public key in vast's Account settings *before* launching, then use the `ssh -p <port> root@<host>` line from the instance card. The Jupyter option gives you a browser URL and a token from the same card.
6. **Destroy when finished** — but only after §4 has pulled your results off the box. Stopping an instance still bills for storage; destroying it deletes the disk.

## 3. Setting the run up

```bash
git clone --branch experiments/ppo https://github.com/Avi161/ACSolverX.git
cd ACSolverX
pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

`requirements.txt` is the platform-independent base. **Do not install `requirements-cuda.txt`** — that pulls the whole JAX stack, which only the `convert` and `parity` stages need, and neither is in this run (see below). Leave the preinstalled torch alone; reinstalling it is how a working image gets broken.

Two environment variables:

```bash
export ACSOLVERX_ALLOW_BIG=1          # REQUIRED: without it the 1024x150 bench60 beam
                                      # hits the repo's 1,000-expansion local cap
export WANDB_API_KEY=<your key>       # never hardcode it into a file
```

**Stages.** The treatment arm trains from scratch and never reads `610model`, so drop `convert` and `parity` — that is what keeps JAX/orbax off the box entirely. What remains is `train` → `beam_eval` → `report`.

**Getting the config right is the one real trap.** `run_ppo.py`'s command-line defaults are *not* the notebook's: `BEAM_WIDTH` 8 against the notebook's 1024, `BEAM_MAX_STEPS` 100 against 150, `EVAL_DATASET` `1190MS` against `benchmark60`, `USE_WANDB` off, and a different `OUT_DIR`. Run the arm under those and you get a number that looks like the experiment and is not it. So do not hand-write a config — generate it from the notebook that defines the arm:

Generate the arm notebooks first — `python3 -m experiments.ppo.make_arm_notebooks`
writes `ppo_arm_control.ipynb` and `ppo_arm_s20mk2.ipynb` into
`experiments/notebooks/ppo/`; they are generated from the baseline template, not
committed. `arm_config.py` reads them, so it runs only after that step.

```bash
python -m experiments.ppo.arm_config s20mk2 --smoke --out /root/s20mk2_smoke.json
python -m experiments.ppo.arm_config s20mk2 --full  --out /root/s20mk2_full.json
```

[`arm_config.py`](arm_config.py) executes the notebook's CONFIG cell and applies exactly the merge its RUN cell applies, so the headless run and the Colab run cannot drift. It prints the tag, dataset, beam size and TF32 setting for you to eyeball. Confirm it says `beam 1024x150`, `benchmark60`, `tf32 True`, and the tag `ppo-drt-AC19_extended_ho60-s20mk2-lam0.2-s142`.

*Alternative:* launch the instance with Jupyter, run `python3 -m experiments.ppo.make_arm_notebooks`, and then run the generated `experiments/notebooks/ppo/ppo_arm_s20mk2.ipynb` unchanged. Its SETUP cell already has a non-Colab path (it walks up to the repo root and sets `MIRROR_DIR = None`), so the only edit is trimming `STAGES` to `["train", "bench60", "report"]`. This sidesteps the config question entirely and is the better choice if you would rather not touch a shell.

## 4. Running it

**Smoke first — this is a repo hard rule, and it has already earned its keep.** The control arm's mandatory smoke is what caught the GPU-resume crash fixed in `91c74c0b` two pushes ago: RNG states came back on CUDA and `set_state` refused them. That bug was only reachable on a GPU, on a *second* execution. A first run on unfamiliar hardware is exactly the situation the rule exists for.

```bash
tmux new -s ppo                       # so a dropped SSH connection does not kill the run
CKPT=results/ppo/s20mk2/ppo-drt-AC19_extended_ho60-s20mk2-lam0.2-s142.pt

python -m experiments.ppo.run_ppo --stage train     --config /root/s20mk2_smoke.json
python -m experiments.ppo.run_ppo --stage beam_eval --config /root/s20mk2_smoke.json --set BEAM_CHECKPOINT=$CKPT
python -m experiments.ppo.run_ppo --stage report    --config /root/s20mk2_smoke.json
```

Two updates plus a time-bounded benchmark-60 eval, ~8 minutes. Read `seconds_per_update` off the heartbeat and compare it against **31.18 s/update** (the Colab A100 figure, TF32 off). That number is the whole point of the smoke on a new box: it tells you what the full 1000 updates will cost here before you commit to them. Paste the block between the `====` lines back into the chat before starting the full run — that is the gate §4 of the plan asks for.

**`--set BEAM_CHECKPOINT` is not optional, and leaving it off does not raise a useful error.** The notebook's RUN cell passes it per-stage (`run("beam_eval", BEAM_CHECKPOINT=ckpt)`), so it is not in the config `arm_config.py` writes. Without it, `stage_beam` (`run_ppo.py:594`) falls through to `PARAMS_NPZ` — the 610model — which on this box does not exist, because `convert` never ran. You would discover that after training, ~9 h in, on a machine billing by the second. Worse if the npz *did* exist: it would beam the upstream model and write a perfectly well-formed jsonl of the wrong thing. Run the smoke to see it work before the full run depends on it.

Then the real thing:

```bash
python -m experiments.ppo.run_ppo --stage train     --config /root/s20mk2_full.json
python -m experiments.ppo.run_ppo --stage beam_eval --config /root/s20mk2_full.json --set BEAM_CHECKPOINT=$CKPT
python -m experiments.ppo.run_ppo --stage report    --config /root/s20mk2_full.json
```

1000 updates, ~8.7 h at the Colab rate. It resumes from its checkpoint if anything drops, so a lost connection costs at most the time since the last `SAVE_EVERY = 25` checkpoint. For option 1 above, run the second arm concurrently on the other GPU:

```bash
python -m experiments.ppo.arm_config control --full --out /root/control_full.json
CKPT_C=results/ppo/control/ppo-drt-AC19_extended_ho60-s142.pt

CUDA_VISIBLE_DEVICES=1 python -m experiments.ppo.run_ppo --stage train     --config /root/control_full.json
CUDA_VISIBLE_DEVICES=1 python -m experiments.ppo.run_ppo --stage beam_eval --config /root/control_full.json --set BEAM_CHECKPOINT=$CKPT_C
CUDA_VISIBLE_DEVICES=1 python -m experiments.ppo.run_ppo --stage report    --config /root/control_full.json
```

The two arms write to separate `OUT_DIR`s and carry different tags (`...-s20mk2-lam0.2-s142` vs `...-s142`), so they cannot resume from each other's checkpoint — the trap `train_tag` exists to close.

**Persistence.** There is no Drive mount here, so `MIRROR_DIR` is `None` and the instance disk is the only copy. W&B carries the metrics live (same entity `avigyapaudel045-aisc`, project `acsolver`, group `ppo-shaped-reward`, so the arms overlay on one chart), but **not** the checkpoints or the jsonls. Pull those down before destroying the instance, and periodically during the run:

```bash
# from your laptop
scp -P <port> -r root@<host>:/root/ACSolverX/results/ppo ./results/ppo_vast
```

**Verify before quoting any count.** `python -m experiments.ppo.verify_beam results/ppo/**/beam-*.jsonl` replays every solved row through `acs_spec` alone and needs no GPU — run it on your laptop after pulling the results down.
