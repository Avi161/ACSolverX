"""Shared fixtures; ``tests/data/greedy_golden.json`` is the baseline golden file."""
import json
import os
import sys
from functools import lru_cache

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from acx import data  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "data", "greedy_golden.json")


@lru_cache(maxsize=None)
def dataset(path):
    """``data/*.txt`` as a list of ``Presentation`` (cached)."""
    return [r.pres for r in data.load(path)]


def golden_entries():
    """The entries of the golden file."""
    with open(GOLDEN) as f:
        return json.load(f)["entries"]


@pytest.fixture(scope="session")
def ms640():
    return dataset("data/ms640_solved.txt")
