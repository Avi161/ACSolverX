"""Shared fixtures and generators for the fable Neuwirth-stack tests.

Deliberately free of scratch-directory dependencies: every number a test asserts is
either recomputed here or written as a literal.
"""

from __future__ import annotations

import functools
import importlib.util
import itertools
import os
import sys

from experiments.stable_ac.fable import ac_words as W

# ---------------------------------------------------------------------------------
# committed copies of the codex census numbers (pinned literals, no scratch paths)
#
# The codex census file stores the *defect* |A| - |C| + 2L - |AC| (always even) as the
# histogram key and the genus sum defect/2 as ``minimum_genus``.
# ---------------------------------------------------------------------------------
AK3 = ("xxxYYYY", "xyxYXY")
ORBIT2 = ("YYXXyx", "YYYxyXX")
P25 = ("XYxYXyxYYxyXy", "YXyyXYxyxYYx")
Q = ("xxxxyXXYxyXXY", "YxxyXXYxxyXXYxxyXXY")

AK3_CENSUS = {
    "enumerated_cases": 86_400,
    "defect_histogram": {4: 724, 6: 14_882, 8: 55_438, 10: 15_356},
    "minimum_genus": 2,
    "accepting_orders": 0,
    "link_components": 1,
    "degrees": {"x": 6, "y": 7},
}
ORBIT2_CENSUS = {
    "enumerated_cases": 86_400,
    "defect_histogram": {2: 2, 4: 702, 6: 14_932, 8: 55_132, 10: 15_632},
    "minimum_genus": 1,
    "accepting_orders": 0,
    "link_components": 1,
    "degrees": {"x": 6, "y": 7},
}

CODEX_ORACLE_PATH = (
    "/tmp/claude-0/-home-user-ACSolverX/cff13624-d3f2-4044-bd4f-d64680bb928b/"
    "scratchpad/codex_solver/neuwirth_rank_solver.py"
)


def codex_oracle():
    """Import the codex rank solver from its scratch copy, or return ``None``."""
    path = os.environ.get("FABLE_CODEX_ORACLE", CODEX_ORACLE_PATH)
    if not path or not os.path.exists(path):
        return None
    name = "_fable_codex_rank_oracle"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------------
# the deterministic exhaustive small-word batch
# ---------------------------------------------------------------------------------

LETTERS = ("x", "X", "y", "Y")


@functools.lru_cache(maxsize=None)
def cyclically_reduced_words(length: int) -> tuple:
    """Every cyclically reduced word of exactly ``length`` letters, in product order."""
    out = []
    for letters in itertools.product(LETTERS, repeat=length):
        word = "".join(letters)
        if W.is_cyclically_reduced(word):
            out.append(word)
    return tuple(out)


@functools.lru_cache(maxsize=None)
def small_batch(max_total: int = 7) -> tuple:
    """All cyclically reduced ordered word pairs of total length <= ``max_total``.

    Both generators must occur somewhere in the pair.  Exact pairs are deduplicated
    (they are generated distinct, so this is a no-op assertion, checked in the tests);
    no canonicalisation of any kind is applied.
    """
    pairs = []
    for l1 in range(1, max_total):
        for l2 in range(1, max_total - l1 + 1):
            for a in cyclically_reduced_words(l1):
                for b in cyclically_reduced_words(l2):
                    joined = (a + b).lower()
                    if "x" in joined and "y" in joined:
                        pairs.append((a, b))
    return tuple(pairs)
