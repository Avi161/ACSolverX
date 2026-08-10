"""Local overrides for the PPO suite.

`tests/conftest.py` has a session-scoped autouse `numba_warm` that imports the
numba greedy solver. This suite is pure torch and touches none of it, so warming
numba here would cost 30-60 s of compilation for nothing -- and, worse, would make
`pytest tests/ppo` un-runnable on a GPU image (Colab A100) that has torch but no
numba. Overriding the fixture in this package's conftest is the pytest-sanctioned
way to say "not applicable here" without editing the shared file.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def numba_warm():
    """No-op: nothing under tests/ppo goes through the numba solver."""
    return None
