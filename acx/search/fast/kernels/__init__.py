"""Numba kernels for one state, shared by the fast backend, the hybrid and the automorphism code.

Ported from ``hexpand.expand_children_h`` / ``expand_and_score_h``
(``origin/codex/ac-elementary-decoder:experiments/heuristic_search/core/hexpand.py``, commit a8a6b3a4) and
``hfast._feats_nj``, generalised from two relators on main's ``(n, 2)`` bool arrays to any number of relators and
generators. No fastmath is used anywhere, so scores are bit-identical to ``acx.core.priority``.

* ``encoding``: the Booth-symbol layout of a state, ``encode`` / ``decode``, the tie-break bytes.
* ``words``: reduction, canonical form and relator order on symbol buffers.
* ``expand``: every child of a state, in the order ``acx.search.spec`` builds them (and the dropped ones).
* ``score``: the heap priority of a state.
* ``scored_children``: ``children``, the Python entry that ties these together.

Everything is re-exported here, so ``from acx.search.fast.kernels import expand`` and the like keep working.
"""
from .encoding import decode, encode, generator, key_code, tie_bytes
from .expand import child_width, expand, expand_drops, max_children
from .score import LENGTH, PRIORITY_IDS, S20_MK2, priority_id, score
from .scored_children import children
from .words import canon_buf, reduce_buf, rel_less
