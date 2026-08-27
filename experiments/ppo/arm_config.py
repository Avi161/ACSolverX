"""Dump an arm notebook's CONFIG cell to a `--config` JSON for headless runs.

`run_ppo.py`'s `__main__` block carries its own defaults, and they are **not** the
notebook's: `BEAM_WIDTH` 8 (not 1024), `BEAM_MAX_STEPS` 100 (not 150),
`EVAL_DATASET` `1190MS` (not `benchmark60`), `USE_WANDB` False, and a different
`OUT_DIR`. Those defaults exist so a bare `python -m experiments.ppo.run_ppo` is
harmless on a laptop; running an *arm* under them would produce a number that
looks like the experiment and is not it.

So a headless box (vast.ai, any bare VM) must not hand-write a config. This reads
the notebook that defines the arm, executes its CONFIG cell — which is pure
assignment, no imports, no side effects — and applies exactly the merge the RUN
cell applies. One template, one source of truth, same as the two notebooks.

    python3 -m experiments.ppo.arm_config s20mk2 --out /tmp/s20mk2.json
    python3 -m experiments.ppo.run_ppo --stage train --config /tmp/s20mk2.json

`MIRROR_DIR` is forced to null: the notebook points it at a Colab Drive mount,
which does not exist off Colab, and `_mirror` would create the literal directory
`/content/drive/...` on the local disk and silently mirror into nothing.
"""

import argparse
import json
import os

from experiments.ppo.ppo import make_config
from experiments.ppo.run_ppo import train_tag

HERE = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK_DIR = os.path.join(os.path.dirname(HERE), "notebooks", "ppo")


def notebook_path(arm):
    return os.path.join(NOTEBOOK_DIR, f"ppo_arm_{arm}.ipynb")


def read_config_cell(path):
    """Return the CONFIG cell source — the first cell, by the template's contract."""
    with open(path) as fh:
        nb = json.load(fh)
    src = "".join(nb["cells"][0]["source"])
    if "ARM" not in src or "cfg = {" not in src:
        raise SystemExit(f"{path}: first cell is not the CONFIG cell")
    return src


def build(arm, smoke=None, repo_root=None):
    """The config the notebook's RUN cell would hand to `main`, for one arm."""
    ns = {}
    exec(compile(read_config_cell(notebook_path(arm)), notebook_path(arm), "exec"), ns)

    root = repo_root or os.path.dirname(os.path.dirname(HERE))
    cfg = dict(ns["cfg"])
    cfg["OUT_DIR"] = os.path.join(root, ns["LOCAL_OUT_DIR"])
    cfg["MIRROR_DIR"] = None            # no Drive mount off Colab; see module docstring
    cfg["DATASET"] = ns["DATASET"]
    cfg["SEED"] = ns["SEED"]
    cfg["SHAPING"] = ns["SHAPING"]
    cfg["LAMBDA"] = ns["LAMBDA"]
    cfg["MAX_UPDATES"] = ns["MAX_UPDATES"]

    smoke = ns["SMOKE_RUN"] if smoke is None else smoke
    if smoke:
        # Identical to the RUN cell's smoke branch. Two updates, a checkpoint every
        # one so the save + resume path really fires, and a wall-clock-bounded beam.
        cfg["MAX_UPDATES"] = 2
        cfg["SAVE_EVERY"] = 1
        cfg["BEAM_TIME_BUDGET_S"] = ns["SMOKE_SECONDS"]
        cfg["USE_WANDB"] = False
    cfg["SMOKE_RUN"] = bool(smoke)

    merged = dict(make_config())
    merged.update(cfg)
    return merged, ns


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("arm", help="arm name, e.g. s20mk2 or control")
    p.add_argument("--out", required=True, help="path to write the JSON config")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--smoke", dest="smoke", action="store_true",
                   help="force the 2-update smoke (default: whatever the notebook says)")
    g.add_argument("--full", dest="smoke", action="store_false",
                   help="force the full run, overriding the notebook's SMOKE_RUN")
    p.set_defaults(smoke=None)
    a = p.parse_args()

    cfg, ns = build(a.arm, smoke=a.smoke)
    with open(a.out, "w") as fh:
        json.dump(cfg, fh, indent=2, sort_keys=True)

    tag = train_tag(cfg["DATASET"], cfg["SEED"], cfg["SHAPING"], cfg["LAMBDA"])
    print(f"wrote {a.out}")
    print(f"  arm      {ns['ARM']}   shaping={cfg['SHAPING']} lambda={cfg['LAMBDA']}")
    print(f"  tag      {tag}")
    print(f"  dataset  {cfg['DATASET']}  seed={cfg['SEED']}  updates={cfg['MAX_UPDATES']}")
    print(f"  eval     {cfg['EVAL_DATASET']}  beam {cfg['BEAM_WIDTH']}x{cfg['BEAM_MAX_STEPS']}")
    print(f"  tf32     {cfg['ALLOW_TF32']}   smoke={cfg['SMOKE_RUN']}")
    print(f"  out      {cfg['OUT_DIR']}")


if __name__ == "__main__":
    main()
