"""Run the L/K/MK-only ablation on the 60-row benchmark through ``hcompact``.

The ablation retains the shipped coefficients on ``L``, ``K`` and ``MK`` and removes only ``S``
and ``xyimb``. It is not a re-tune. Run four cumulative 15-row batches; ``run_ab`` resumes the same
jsonl, so each invocation adds exactly the next 15 presentations while staying inside the local-run
rule.

    .venv/bin/python3 -m experiments.heuristic_search.runners.run_lkmk_ablation --subset 15
    .venv/bin/python3 -m experiments.heuristic_search.runners.run_lkmk_ablation --subset 30
    .venv/bin/python3 -m experiments.heuristic_search.runners.run_lkmk_ablation --subset 45
    .venv/bin/python3 -m experiments.heuristic_search.runners.run_lkmk_ablation --subset 60
"""
import argparse
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, part)) for part in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners import run_ab  # noqa: E402

NODE_BUDGET = 1_000
MAX_RELATOR_LENGTH = 48
LKMK = {"segments": [{"upto": None, "w": {"L": 1.0, "K": 2.53, "MK": 6.418}}]}

assert NODE_BUDGET <= 1_000, "1,000 nodes is the hard local cap -- never raise it"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subset", type=int, required=True, choices=(15, 30, 45, 60),
                        help="cumulative prefix; run 15, 30, 45, then 60")
    args = parser.parse_args()

    run_ab.ARMS["lkmk"] = LKMK
    cfg = {
        "DATASET": "bench66",
        "SUBSET": args.subset,
        "ARMS": ["lkmk"],
        "NODE_BUDGET": NODE_BUDGET,
        "CHECKPOINTS": [NODE_BUDGET],
        "MAX_RELATOR_LENGTH": MAX_RELATOR_LENGTH,
        "RESUME": True,
        "OUT_STEM": "EXP29_lkmk",
        "ENGINE": "hcompact",
        "N_WORKERS": 1,
    }
    run_ab.run_ab(cfg, out_dir="results/heuristic_search/runs")


if __name__ == "__main__":
    main()
