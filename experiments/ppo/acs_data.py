"""Presentation loading and the deterministic-pin derivation.

`data/<stem>.txt` is one flat Python list of ints per line -- `[r1 | r2]`, each
relator padded to `len(line) // 2` with zeros, alphabet `1=x, -1=X, 2=y, -2=Y`.
`load_presentations` re-pads to the requested `max_length`, which is exactly what
`envs/utils.py:change_max_relator_length_of_presentation` does, reimplemented
here so nothing in this package imports the JAX tree.

`ms_prefix_length` is the load-bearing one. `ppo_ac_s.py:98` pins the first
**634** envs to fixed initial states with `parallel_sample[:634] = False`, and
634 is not a free parameter: `data/AC19_extended.txt` opens with the first 634
lines of `data/1190MS.txt` verbatim, and those are precisely the Miller-Schupp
presentations that appear in the extended file at all. So the pin dedicates one
env permanently to each MS target present in the training set. Deriving the
count from the data rather than hardcoding it matters because it is **0** for
`data/AC19.txt`, which shares no prefix with the MS file -- an AC19-only run
must pin nothing.
"""

import os
from ast import literal_eval

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def repo_root():
    """Walk up until a directory holds both `experiments/` and `data/`."""
    d = _HERE
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(os.path.join(d, "data")):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = repo_root()
MS_STEM = "1190MS"


def data_path(stem):
    return os.path.join(ROOT, "data", f"{stem}.txt")


def read_raw(stem):
    """The file as a list of flat int lists, unpadded and unchanged."""
    with open(data_path(stem), "r") as fh:
        return [literal_eval(line.strip()) for line in fh if line.strip()]


def repad(presentation, max_length):
    """`envs/utils.py:change_max_relator_length_of_presentation`, in numpy."""
    old = len(presentation) // 2
    n1 = int(np.count_nonzero(presentation[:old]))
    n2 = int(np.count_nonzero(presentation[old:]))
    if max(n1, n2) > max_length:
        raise ValueError(f"relator of length {max(n1, n2)} does not fit in max_length={max_length}")
    r1 = list(presentation[:n1])
    r2 = list(presentation[old:old + n2])
    return r1 + [0] * (max_length - n1) + r2 + [0] * (max_length - n2)


def load_presentations(stem, max_length=24):
    """(S, 2 * max_length) int8 array of initial states, in file order."""
    rows = [repad(p, max_length) for p in read_raw(stem)]
    return np.asarray(rows, dtype=np.int8)


def ms_prefix_length(stem):
    """How many leading lines of `stem` are the leading lines of `1190MS`.

    This is the number of envs `ppo_ac_s.py` pins deterministically: 634 for
    `AC19_extended`, 0 for `AC19`. Comparison is on the *unpadded* relator
    pair, so it is independent of the two files' `max_relator_length` layouts.
    """
    if stem == MS_STEM:
        return len(read_raw(MS_STEM))
    ms = [tuple(repad(p, 24)) for p in read_raw(MS_STEM)]
    train = [tuple(repad(p, 24)) for p in read_raw(stem)]
    n = 0
    while n < len(ms) and n < len(train) and ms[n] == train[n]:
        n += 1
    return n
