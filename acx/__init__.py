"""acx: Andrews-Curtis search, change of variables and verification. Start with ``docs/ARCHITECTURE.md``::

    from acx import Presentation, SearchConfig, search, replay
    res = search(Presentation.parse("xxYXY", "xyyXY"), SearchConfig(budget=1000))
    replay(Presentation.parse("xxYXY", "xyyXY"), res.path)
"""
from .jit_cache import stamp_caches

stamp_caches()                  # before any kernel is defined
from .core import Move, Presentation, SearchConfig
from .search import Result, search
from .verify import ReplayError, replay

__version__ = "0.1.0"
