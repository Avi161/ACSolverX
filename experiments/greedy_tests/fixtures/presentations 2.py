"""Presentation fixtures: real datasets, synthetic words, and literature cases.

The literature presentations are fixtures, **not** solvability assertions. AK(n)
for n > 2 and the MMS02 instance below are *stably* AC-trivial (or of unknown
status); their plain AC-triviality is open. A test asserting "solves in N nodes"
would therefore be asserting an open conjecture, and would pass or fail on luck.
They are used only to check that the search does not crash, respects its budget,
and preserves the abelianization invariant.
"""

import ast
import os
import random

from ..spec.presentation import Presentation

_HERE = os.path.dirname(os.path.abspath(__file__))


def repo_root():
    d = _HERE
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(
            os.path.join(d, "data")
        ):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


MS640 = os.path.join("data", "ms640_solved.txt")
MS_UNSOLVED = os.path.join("data", "ms_unsolved_reps", "ms_reps_unsolved.txt")


def load_flat_lines(rel_path):
    with open(os.path.join(repo_root(), rel_path)) as f:
        return [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]


def load_dataset(rel_path, n_rel=2):
    """Every line of a dataset file as a :class:`Presentation`.

    ``n_gen`` is pinned to 2 rather than inferred: a presentation whose relators
    happen to use only ``x`` still lives in the two-generator free group.
    """
    return [
        Presentation.from_flat_ints(ints, n_rel=n_rel, n_gen=2)
        for ints in load_flat_lines(rel_path)
    ]


def ms640(indices=None):
    all_p = load_dataset(MS640)
    if indices is None:
        return all_p
    return [all_p[i] for i in indices]


def ms_unsolved(indices=None):
    all_p = load_dataset(MS_UNSOLVED)
    if indices is None:
        return all_p
    return [all_p[i] for i in indices]


# -- literature ------------------------------------------------------------
# a = x = 1, b = y = 2.


def ak(n):
    """AK(n) = <a, b | a^n b^-(n+1), a b a b^-1 a^-1 b^-1>  (lisitsa, line 66).

    AK(2) is known AC-trivial. AK(n > 2) is open -- do not assert solvability.
    """
    r1 = (1,) * n + (-2,) * (n + 1)
    r2 = (1, 2, 1, -2, -1, -2)
    return Presentation(2, (r1, r2))


#: MMS02's length-14 reduction of the w = x^-1 y z instance of Theorem 1.4
#: (``mms02_andrews_curtis_equivalence.txt``, lines 220-226).
#: Stably AC-trivial by construction; plain AC-triviality unknown.
MMS02_LEN14 = Presentation(
    2,
    (
        (1, 2, -1, -1, -2, 1, -2),   # x y x^-2 y^-1 x y^-1
        (-1, -2, 1, 2, 2, 1, -2),   # x^-1 y^-1 x y^2 x y^-1
    ),
)


# -- synthetic -------------------------------------------------------------


def all_words(n_gen, max_len):
    """Every word (reduced or not) of length <= max_len. 4^L words at n_gen=2."""
    alphabet = [g for g in range(-n_gen, n_gen + 1) if g != 0]
    out = [()]
    frontier = [()]
    for _ in range(max_len):
        frontier = [w + (g,) for w in frontier for g in alphabet]
        out.extend(frontier)
    return out


def random_word(rng, n_gen, length):
    alphabet = [g for g in range(-n_gen, n_gen + 1) if g != 0]
    return tuple(rng.choice(alphabet) for _ in range(length))


def random_presentations(seed, count, n_gen=2, n_rel=2, max_len=8):
    """Seeded, so a failure is reproducible from the seed alone."""
    rng = random.Random(seed)
    out = []
    while len(out) < count:
        rels = tuple(
            random_word(rng, n_gen, rng.randint(1, max_len)) for _ in range(n_rel)
        )
        p = Presentation(n_gen, rels).reduced()
        if all(p.relators):
            out.append(p)
    return out
