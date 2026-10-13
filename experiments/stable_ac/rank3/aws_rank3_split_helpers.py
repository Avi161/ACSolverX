"""Split the ARM helper box into three, one per third of the presentations.

Two helpers on the same task order run each other's tasks again, so each helper
gets its own presentations (``--pres``). ``--path-sample-target`` is scaled by
k/640, which keeps the sample fraction target / (words x k) equal to the full
run's 2000 / (words x 640): a shard from a helper then holds the paths a full
run samples.

    python3 experiments/stable_ac/rank3/aws_rank3_split_helpers.py OUT_DIR

writes OUT_DIR/ud_armA.sh, ud_armB.sh, ud_armC.sh (logs run_armA.log, ...).
"""

import os
import sys

FULL_TARGET = 2000  # run_rank3_bf.py --path-sample-target default
HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "aws_rank3_arm_helper_box.sh")
RUN = "--min-len 9 --max-len 10 --no-sub --reverse --no-merge --out-dir $D1 )"
LOG = "run_arm2.log"


def groups(n=640):
    """Three interleaved groups; every size is a multiple of 8, so target() is whole."""
    cut = n // 24 * 24
    out = [[], [], []]
    for i in range(n):
        out[i % 3 if i < cut else (i - cut) // 8].append(i)
    return out


def target(k, n=640):
    q, r = divmod(FULL_TARGET * k, n)
    assert r == 0, "a fractional target would change the sample fraction"
    return q


def render(src, name, ids):
    assert src.count(RUN) == 1 and src.count(LOG) == 1
    run = (RUN[:-2] + " \\\n      --path-sample-target "
           f"{target(len(ids))} --pres {','.join(map(str, ids))} )")
    return src.replace(RUN, run).replace(LOG, f"run_arm{name}.log")


def main(out_dir):
    src = open(HELPER).read()
    os.makedirs(out_dir, exist_ok=True)
    for name, ids in zip("ABC", groups()):
        path = os.path.join(out_dir, f"ud_arm{name}.sh")
        with open(path, "w") as f:
            f.write(render(src, name, ids))
        print(path, len(ids), target(len(ids)))


if __name__ == "__main__":
    main(sys.argv[1])
