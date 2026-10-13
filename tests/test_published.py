"""The published numbers: the committed run summaries, and a sample of MS640 searched again so the code is checked too.

``results/<run>/summary.json`` holds what README.md and docs/RESULTS.md quote. The constants below are those numbers, so
a rerun of a config that moves one fails here at once (a summary that is not shipped is skipped). The sample reruns 40
MS640 rows under both priorities and both backends and compares the pops of every row with the published runs.
"""
import json
import os

import pytest
from conftest import ROOT

from acx.core.config import SearchConfig
from acx.search import search

# run: (rows solved, rows, total cost in units); the cost is given where the published numbers have it.
PUBLISHED = {
    "ms640_length_fast": (606, 640, None),
    "ms640_s20_mk2_fast": (626, 640, None),
    "ms640_hybrid": (640, 640, 25_064),
    "ac19_hybrid": (72_779, 72_779, 2_489_726),
    "ac1m_raw_hybrid": (1_136_135, 1_136_154, 47_236_671),
    "bench60_length": (40, 60, None),
    "bench60_s20_mk2": (52, 60, None),
    "bench60_cov": (39, 60, None),
    "bench60_hybrid": (60, 60, 4_783),
    "ladder200_length": (40, 188, None),
    "ladder200_s20_mk2": (116, 188, None),
    "ladder200_hybrid": (188, 188, None),
}


@pytest.mark.parametrize("run", PUBLISHED)
def test_published_summaries_are_pinned(run):
    path = os.path.join(ROOT, "results", run, "summary.json")
    if not os.path.exists(path):
        pytest.skip(f"{path} is not shipped")
    with open(path) as f:
        summary = json.load(f)
    solved, rows, cost = PUBLISHED[run]
    assert (summary["solved"], summary["rows"]) == (solved, rows)
    assert cost is None or summary["cost"]["total"] == cost


# MS640 rows 5, 21, ..., 629 at cap 24 and budget 10,000: the pops of each row in the published runs (None: not
# solved). LENGTH solves 38 of the 40, S20_MK2 all 40; each row matches the run in results/ms640_*_fast.
STRIDE = range(5, 640, 16)
PUBLISHED_POPS = {
    "length": [5, 4, 6, 4, 8, 9, 21, 5, 4, 12, 16, 6, 23, 6, 66, 61, 5, 4, 10, 3, 9, 9, 8, 23, 5, 9, 62, 8, 204, 7,
               156, 7, 3, 438, 1411, 1404, 9567, 9407, None, None],
    "s20_mk2": [5, 4, 6, 4, 8, 9, 155, 5, 4, 11, 11, 6, 33, 6, 34, 36, 5, 4, 9, 3, 11, 8, 8, 77, 5, 9, 54, 8, 72, 7,
                65, 7, 3, 190, 391, 2390, 1584, 5059, 9167, 7254],
}


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("priority", PUBLISHED_POPS)
def test_ms640_stride_sample_reproduces_the_published_runs(ms640, backend, priority):
    """The fast backend searches all 40 rows. The spec backend is about a hundred times slower, so it takes the rows
    that the published runs solve in at most 500 pops (34 of 40 on LENGTH, 35 on S20_MK2)."""
    published = dict(zip(STRIDE, PUBLISHED_POPS[priority]))
    ids = [pid for pid, pops in published.items() if backend == "fast" or (pops is not None and pops <= 500)]
    cfg = SearchConfig(priority=priority, backend=backend, cap=24, budget=10_000)
    got = {}
    for pid in ids:
        r = search(ms640[pid], cfg)
        got[pid] = r.pops if r.solved else None
    assert got == {pid: published[pid] for pid in ids}
