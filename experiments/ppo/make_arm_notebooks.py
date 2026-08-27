"""Generate the two arm notebooks from one template.

The control and the treatment are one experiment. Everything about them must be identical
except the reward, so hand-maintaining two notebooks is exactly the wrong shape: the first
time someone fixes a bug in one and not the other, the comparison silently stops measuring
the reward and starts measuring the difference between two notebooks.

So both are generated here, from the same SETUP (lifted verbatim from `ppo_baseline.ipynb`,
which is the pattern this repo pins), the same RUN, and the same TABLE. The arms differ in
exactly four lines: `ARM`, `SHAPING`, `LAMBDA`, and the Drive folder they mirror to --
separate folders because both would otherwise race on the two fixed-name report files.

Regenerate with:  python3 -m experiments.ppo.make_arm_notebooks
"""

import json
import os

from experiments.ppo import acs_data

NB_DIR = os.path.join(acs_data.ROOT, "experiments", "notebooks", "ppo")
BASELINE = os.path.join(NB_DIR, "ppo_baseline.ipynb")

ARMS = [
    dict(name="control", label="CONTROL (unshaped baseline reward)", shaping="None",
         lam="0.0", job="ppo-arm-control",
         why="The reward the 610model was trained with, unchanged:\n"
             "#   reward = 1000 if terminated else -min(nnz, 10)\n"
             "# This arm exists because our run differs from the published one in several\n"
             "# ways at once -- held-out data, PyTorch instead of JAX, possibly TF32 -- so\n"
             "# the shaped arm cannot be read against the 610model's 49/60. It can only be\n"
             "# read against THIS."),
    dict(name="s20mk2", label="TREATMENT (L + 20*S + 2*MK shaping)", shaping='"s20mk2"',
         lam="0.2", job="ppo-arm-s20mk2",
         why="Potential-based shaping on top of the same base reward:\n"
             "#   Phi(s) = -LAMBDA * (L + 20*S + 2*MK),  F = GAMMA*Phi(s') - Phi(s)\n"
             "# Policy-invariant (Ng, Harada & Russell 1999) and it telescopes, so no cycle\n"
             "# can farm it. The weights come from a 70,723-orbit A/B where this ordering\n"
             "# cut the unsolved residual from 221 to 39 against plain length.\n"
             "# LAMBDA = 0.2 is measured, not chosen: on transitions that actually change\n"
             "# the state the median |dh| is 10.9, so the median shaping term is ~2.2 --\n"
             "# about a fifth of the flat -10 the base reward pays."),
]

CONFIG = '''# ===== PPO ARM: {label} — CONFIG (edit ONLY this cell) =====
# Runtime: A100. This notebook is ONE ARM of a two-arm experiment. Run it and its
# sibling `ppo_arm_{other}.ipynb` side by side on two A100s: they are generated from
# one template and differ in exactly four lines -- ARM, SHAPING, LAMBDA, and the Drive
# folder -- so any difference in their results is the reward and nothing else.
#
# {why}

ARM      = "{name}"
SHAPING  = {shaping}       # None = control; "s20mk2" = L + 20*S + 2*MK
LAMBDA   = {lam}           # strength of the shaping term; 0 is a hard zero

REPO_URL = "https://github.com/Avi161/ACSolverX.git"
BRANCH   = "claude/results-collection-org-wmvpxu"
REPO_DIR = "ACSolverX"
CLONE       = True
UPDATE_REPO = True            # git reset --hard so a RESTART pulls the latest push
MOUNT_DRIVE = True
INSTALL_REAL_DISTRAX = False  # run_ppo ships a shim verified bit-identical to distrax

# --- the training set -------------------------------------------------------
# `AC19_extended` with the 60 benchmark presentations removed. It is BUILT on the VM
# from the shipped file plus the frozen benchmark CSV -- not committed -- so it cannot
# drift from the benchmark it is defined against.
#
# Why it matters: 54 of the 60 evaluation presentations are in `AC19_extended`, and all
# 54 sit inside the first 634 lines, which is the block that gets PINNED one-env-each for
# the whole run. Training on the shipped file means training on 54/60 of the test set.
#
# The removal has a trap, already handled in the runner: benchmark row `bin 0` is line 0
# of the file, so the shipped prefix walk (`acs_data.ms_prefix_length`) returns 0 on the
# filtered file and pinning would switch OFF entirely, in both arms, silently.
# `heldout.ms_prefix_length` counts membership instead and gives 580 = 634 - 54.
DATASET = "AC19_extended_ho60"
SEED    = 142

# 1000 updates, the step count of the shipped 610model. Measured at 31.2 s/update with
# TF32 off, so ~8.7 h. Resumable: a disconnect continues from the checkpoint, and raising
# this later costs only the extra updates.
MAX_UPDATES = 1000

# --- smoke ------------------------------------------------------------------
# True -> 2 updates and a time-bounded benchmark-60 eval, ~8 minutes. Run it ONCE per
# arm before the real thing. It is not a formality: it measures seconds/update on THIS
# machine and proves the optimiser step, the checkpoint, the Drive mirror and the
# evaluation all fire. Compare its seconds_per_update against 31.18 (TF32 off) to see
# what ALLOW_TF32 bought.
SMOKE_RUN     = True
SMOKE_SECONDS = 300

# --- output -----------------------------------------------------------------
# SEPARATE Drive folders per arm. The checkpoints and jsonl already carry arm-specific
# tags, but `smoke_report.json` and `report_history.jsonl` are fixed names -- two live
# sessions mirroring to one folder would race on them.
LOCAL_OUT_DIR = "results/ppo/{name}"
DRIVE_OUT_DIR = "/content/drive/MyDrive/acsolverx_results/ppo/{name}"

cfg = {{
    "DEVICE": "auto",

    # 74% of an update is the optimiser, not rollout collection (collect 8.0 s vs learn
    # 23.2 s measured), and the batch is 228,480 transitions through a 137k-parameter
    # net -- large-batch fp32 matmul, which is exactly what TF32 accelerates. The parity
    # stage forces TF32 OFF regardless, so the gate is unaffected, and both arms use the
    # same setting, so the comparison is unaffected too.
    "ALLOW_TF32": True,

    "MICRO_BATCH": 2048,
    "ROLLOUT_CHUNK": 4096,
    "SAVE_EVERY": 25,
    "HEARTBEAT_EVERY_S": 60,

    "CKPT_DIR":   "ppo_checkpoints/610model",
    "CKPT_STEP":  None,
    "PARAMS_NPZ": "ppo_checkpoints/610model_params.npz",

    # --- evaluation ---------------------------------------------------------
    # benchmark-60, by standing rule. 60 rows are only 45 Aut orbits, so every headline
    # is reported both ways. Bins 0-6 saturate for any competent model (a TWO-UPDATE
    # model scored 318/331 on the easy head where the trained one scored 331/331), so
    # the arms can only differ on bins 7-9: 18 rows, 11 orbits. Thin, and said up front.
    "EVAL_DATASET": "benchmark60",
    "EVAL_START": 0,
    "EVAL_END": None,
    "BEAM_WIDTH": 1024,
    "BEAM_MAX_STEPS": 150,
    "BEAM_ALPHA": 0.0,
    "BEAM_TEMPERATURE": 0.0,
    "BEAM_TEMP_END": 0.0,
    "BEAM_TIME_BUDGET_S": None,
    "PARITY_BATCH": 256,

    "USE_WANDB": True,
    "AUTO_AUTHENTICATE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",
    "WANDB_PROJECT": "acsolver",
    "WANDB_GROUP": "ppo-shaped-reward",     # one group, both arms, so they overlay
    "WANDB_JOB_TYPE": "{job}",
    "WANDB_TAGS": ["ppo", "shaped-reward", "{name}"],
    "WANDB_NOTES": None,
}}

# --- swap-ins ---------------------------------------------------------------
# The full run, after the smoke:      SMOKE_RUN = False
# A second seed once one is done:     SEED = 1        (new tag, new checkpoint)
# Gentler shaping if training is unstable (treatment arm only):  LAMBDA = 0.1

print(f"config loaded: arm={{ARM}} shaping={{SHAPING}} lambda={{LAMBDA}}")
'''

RUN = '''# ==================== RUN =================================================
# Restart -> Run All continues: `train` resumes from its checkpoint and `beam_eval`
# skips presentations already in its jsonl. Nothing here needs a manual step -- the
# held-out training file and the 60-row evaluation file are built on first use.
import os
from experiments.ppo import bench60
from experiments.ppo.ppo import make_config
from experiments.ppo.run_ppo import main, train_tag

cfg["OUT_DIR"] = os.path.join(REPO_ROOT, LOCAL_OUT_DIR)
cfg["MIRROR_DIR"] = DRIVE_OUT_DIR if (IN_COLAB and MOUNT_DRIVE) else None
cfg["DATASET"] = DATASET
cfg["SEED"] = SEED
cfg["SHAPING"] = SHAPING
cfg["LAMBDA"] = LAMBDA
cfg["MAX_UPDATES"] = MAX_UPDATES

# `parity` is kept in the ladder even though this arm trains from scratch: it carries
# the env self-check, and the reward path is the thing under test.
STAGES = ["convert", "parity", "train", "bench60", "report"]
if SMOKE_RUN:
    cfg["MAX_UPDATES"] = 2          # meaningless numbers, real code path
    cfg["SAVE_EVERY"] = 1           # so the checkpoint and the mirror are exercised
    cfg["BEAM_TIME_BUDGET_S"] = SMOKE_SECONDS
    cfg["USE_WANDB"] = False

TAG = train_tag(DATASET, SEED, SHAPING, LAMBDA)
print(f"{'SMOKE' if SMOKE_RUN else 'FULL'} RUN: {' -> '.join(STAGES)}")
print(f"  arm={ARM}  tag={TAG}  updates={cfg['MAX_UPDATES']}  tf32={cfg['ALLOW_TF32']}")

BASE = dict(make_config())
BASE.update(cfg)

def run(stage, **over):
    c = dict(BASE)
    c.update(over)
    c["STAGE"] = stage
    return main(c)

results = {}

if "convert" in STAGES:
    results["convert"] = run("convert")

if "parity" in STAGES:
    results["parity"] = run("parity")

if "train" in STAGES:
    results["train"] = run("train")

if "bench60" in STAGES:
    # An ordinary beam over a 60-row dataset, so it resumes, verifies every certificate
    # and reports through the same code as the 1190-row run. Re-runnable at any time
    # against the checkpoint on disk -- including from a second session, mid-training.
    ckpt = os.path.join(cfg["OUT_DIR"], TAG + ".pt")
    if os.path.exists(ckpt):
        results["bench60"] = run("beam_eval", BEAM_CHECKPOINT=ckpt)
    else:
        print(f"skip bench60: no checkpoint at {ckpt} yet")

if "report" in STAGES:
    results["report"] = run("report", SMOKE_RUN=SMOKE_RUN)

print("\\ndone:", ", ".join(results))
'''

TABLE = '''# ==================== TABLE ===============================================
# The deliverable. A different lifetime from the run: it only reads disk, so
# re-printing it never re-runs a stage, and it can be run against a partially
# trained checkpoint at any point.
#
# Reported at ROW level and ORBIT level, always both -- benchmark-60's 60 rows are
# 45 Aut orbits (class 106 alone appears 8 times), so a bare n/60 overstates any
# method that happens to suit a duplicated orbit. `bins7-9` is the subset the arms
# can actually differ on; bins 0-6 saturate.
from experiments.ppo import bench60

print(bench60.format_table(bench60.summarise(cfg["OUT_DIR"])))
'''


def build(baseline=BASELINE, out_dir=NB_DIR):
    with open(baseline) as fh:
        setup = "".join(json.load(fh)["cells"][1]["source"])   # verbatim, never a copy

    written = []
    for i, arm in enumerate(ARMS):
        other = ARMS[1 - i]["name"]
        cells = [CONFIG.format(other=other, **arm), setup, RUN, TABLE]
        nb = {"cells": [{"cell_type": "code", "execution_count": None, "metadata": {},
                         "outputs": [], "source": c.splitlines(keepends=True)}
                        for c in cells],
              "metadata": {"accelerator": "GPU",
                           "colab": {"provenance": [], "gpuType": "A100"},
                           "kernelspec": {"display_name": "Python 3", "name": "python3"},
                           "language_info": {"name": "python"}},
              "nbformat": 4, "nbformat_minor": 0}
        path = os.path.join(out_dir, f"ppo_arm_{arm['name']}.ipynb")
        with open(path, "w") as fh:
            json.dump(nb, fh, indent=1)
            fh.write("\n")
        written.append(path)
    return written


if __name__ == "__main__":
    for p in build():
        print("wrote", p)
