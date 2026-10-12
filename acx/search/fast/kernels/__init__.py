"""Numba kernels for one state, shared by the fast backend, the hybrid and the automorphism code. No fastmath is
used, so scores are bit-identical to ``acx.core.priority``.

``encoding`` (the Booth-symbol layout, tie-break bytes), ``words`` (reduction, canonical form, relator order),
``expand`` (every child of a state, in ``acx.search.spec`` order), ``score`` (the heap priority) and
``scored_children`` (``children``, the Python entry). The names other modules use are re-exported here.
"""
from .encoding import decode, encode, key_code, tie_bytes
from .expand import child_width, expand, expand_drops, max_children
from .score import PRIORITY_IDS, priority_id, score
from .scored_children import children
from .words import canon_buf, reduce_buf, rel_less
