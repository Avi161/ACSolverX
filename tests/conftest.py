"""Shared fixtures.

Two environment notes that shape everything here:

* The first call into any ``@njit`` function compiles it. There are ~17 of them,
  so a cold run pays 30-60s before the first assertion. ``numba_warm`` pays that
  once per session; never add tight per-test timeouts.
* Temporary files go under the repo (``--basetemp`` in ``pytest.ini``), never
  ``/tmp`` -- agent sandboxes deny it.
"""

import os
import sys

import pytest

# Repo root, found by walking up -- never by counting dirname levels, so this
# file's depth under the repo is not baked in (it moved to tests/ once already).
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


_ROOT = _repo_root()
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run the slow tier (golden sweeps, multiprocessing, subprocesses)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip = pytest.mark.skip(reason="needs --runslow")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session", autouse=True)
def numba_warm():
    """Compile the njit entry points once, before any test is timed or run."""
    from experiments.search.greedy_baseline import greedy_search

    for high in (False, True):
        greedy_search("xy", "xY", 2, max_relator_length=8,
                      cyclic_reduce=True, high_speedup=high)
        greedy_search("xy", "xY", 2, max_relator_length=8,
                      cyclic_reduce=False, high_speedup=high)


@pytest.fixture(scope="session")
def repo_root():
    from experiments.greedy_tests.fixtures.presentations import repo_root as _rr

    return _rr()


@pytest.fixture
def out_dir(tmp_path):
    d = tmp_path / "results"
    d.mkdir()
    return str(d)


@pytest.fixture
def in_tmp_cwd(tmp_path, monkeypatch):
    """Run with cwd inside tmp: HEARTBEAT_DEBUG writes hb_stack_<pid>.txt to cwd."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
