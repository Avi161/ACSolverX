"""A pure-Python port of the dual and triple queue engines of ACSolverES (E. Steffen).

Ported from ``native/native_standard_successors.cpp`` (``standard_successors``, ``run_compact_dual_gs``,
``run_compact_triple_gs``) of https://github.com/ElliotSteffen/ACSolverES at 2a458e4, so that the CoV step can be
swapped for the full CoV family without running the original code. Only the configuration of the paper runs is kept:
the length score, no frontier pruning, no checkpoints. ``max_total`` is the original strict bound on |r1| + |r2|
(65 in our earlier runs); ``None`` removes it, which the C++ cannot do.

States are pairs of words over the letters ``a b c d`` = ``Y y X x``: the C++ orders letters ``Y < y < X < x``, so
Python string comparison is the engine's ``solver_less``. ``to_xy`` / ``from_xy`` convert.

Faithfulness is checked by ``check_port.py``: with the 24 auto-CoV maps the dual gives the nodes and path of every row
of the committed ``results/elliot_10k`` / ``elliot_100k`` runs of the original engine.
"""
import heapq
from array import array

_INV = str.maketrans("abcd", "badc")
_TO_XY = str.maketrans("abcd", "YyXx")
_FROM_XY = str.maketrans("YyXx", "abcd")
PAIRS = {("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")}


def to_xy(w):
    return w.translate(_TO_XY)


def from_xy(w):
    return w.translate(_FROM_XY)


def inverse(w):
    return w[::-1].translate(_INV)


def reduce_word(w):
    """Free reduction, then cyclic reduction (``reduce_word`` of the C++)."""
    stack = []
    for c in w:
        if stack and (stack[-1], c) in PAIRS:
            stack.pop()
        else:
            stack.append(c)
    left, right = 0, len(stack)
    while right > left + 1 and (stack[left], stack[right - 1]) in PAIRS:
        left += 1
        right -= 1
    return "".join(stack[left:right])


def min_rotation(w):
    n = len(w)
    if n < 2:
        return w
    d = w + w
    return min(d[i:i + n] for i in range(n))


def canonical_word(w):
    f, i = min_rotation(w), min_rotation(inverse(w))
    return f if f < i else i


def canonical_pair(a, b):
    """The C++ ``canonical_pair``: each word up to rotation and inversion, the pair by (length, word)."""
    a, b = canonical_word(a), canonical_word(b)
    if len(a) > len(b) or (len(a) == len(b) and not a < b):
        a, b = b, a
    return a, b


def standard_successors(first, second, max_total=None):
    """The S-move children of ``(first, second)`` in the C++ order (seam-cancelling products, both replacements)."""
    out = []
    n = len(first)
    red_first, red_second = reduce_word(first), reduce_word(second)
    for cand in (second, inverse(second)):
        m = len(cand)
        for fr in range(n):
            fs = (n - fr) % n
            last = first[(fs + n - 1) % n]
            rot_first = first[fs:] + first[:fs]
            for cr in range(m):
                cs = (m - cr) % m
                if (last, cand[cs]) not in PAIRS:
                    continue
                nb = reduce_word(rot_first + cand[cs:] + cand[:cs])
                if max_total is None or len(nb) + len(red_second) < max_total:
                    out.append(canonical_pair(nb, red_second))
                if max_total is None or len(red_first) + len(nb) < max_total:
                    out.append(canonical_pair(red_first, nb))
    return out


START, STANDARD, COV, COMPLETE = 0, 1, 2, 3
_F_SUB_EXP, _F_COV_Q, _F_COV_EXP, _F_CC_Q, _F_CC_EXP = 1, 2, 4, 8, 16


class _Graph:
    """The ``seen`` map and the state records of one search, kept compact (a 10^7-unit search holds ~6e8 states).

    A state is stored once, as the string ``r1|r2``; a heap entry is one int, ``priority << 32 | id``, where the
    priority packs (length, depth tie, insertion) in the C++ order.
    """

    def __init__(self, deepest=True):
        self.key, self.seen, self.special = [], {}, {}
        self.parent, self.depth, self.gap = array("l"), array("l"), array("l")
        self.kind, self.flags = bytearray(), bytearray()
        self.sign = -1 if deepest else 1
        self.ins = 0
        self.sub = []

    def prio(self, length, depth, sid):
        """The heap entry of ``sid``: smaller pops first, as (length, sign * depth, insertion) do in the C++."""
        self.ins += 1
        return (((length << _DEPTH_BITS) | (self.sign * depth + _DEPTH_MID)) << _INS_BITS | (self.ins - 1)) << 32 | sid

    def state(self, sid):
        return tuple(self.key[sid].split("|"))

    def add(self, state, parent, depth, gap, kind, move=None):
        """``enqueue_new_state``: a new state goes to the sub queue; returns its id, or None if already seen."""
        k = state[0] + "|" + state[1]
        if k in self.seen:
            return None
        sid = len(self.key)
        self.seen[k] = sid
        self.key.append(k)
        self.parent.append(-1 if parent is None else parent)
        self.depth.append(depth)
        self.gap.append(gap)
        self.kind.append(kind)
        self.flags.append(0)
        if move is not None:
            self.special[sid] = move
        heapq.heappush(self.sub, self.prio(len(k) - 1, depth, sid))
        return sid

    def path(self, sid):
        ids = []
        while sid >= 0:
            ids.append(sid)
            sid = self.parent[sid]
        ids.reverse()
        states = [self.state(i) for i in ids]
        moves = [self.special.get(i, {"move_type": "standard_substitution"}) for i in ids[1:]]
        return states, moves


_DEPTH_BITS, _DEPTH_MID, _INS_BITS = 24, 1 << 23, 40
_SID = (1 << 32) - 1


def _score(entry):
    """The length (total |r1| + |r2|) a heap entry was queued with."""
    return entry >> (32 + _INS_BITS + _DEPTH_BITS)


def _expand(g, sid, expander, kind, counters, enqueue=True):
    neighbors, generated, valid = expander(g.state(sid))
    counters["cov_generated"] += generated
    counters["cov_valid"] += valid
    n = 0
    if enqueue:
        for state, move in neighbors:
            if g.add(state, sid, g.depth[sid] + 1, 0, kind, move) is not None:
                n += 1
    counters["cov_enqueued"] += n
    return neighbors


def _sub_pop(g, sid, max_total, counters):
    """Expand a state popped from the sub queue; True if it is the trivial presentation."""
    a, b = g.state(sid)
    if len(a) == 1 and len(b) == 1:
        return True
    depth, gap = g.depth[sid] + 1, g.gap[sid] + 1
    for st in standard_successors(a, b, max_total):
        counters["standard_generated"] += 1
        if g.add(st, sid, depth, gap, STANDARD) is not None:
            counters["standard_enqueued"] += 1
    return False


def _top(queue, g, flag):
    """Drop stale heads (``discard_stale``) and return the head entry, or None."""
    while queue and g.flags[queue[0] & _SID] & flag:
        heapq.heappop(queue)
    return queue[0] if queue else None


def _counters():
    return dict(nodes=0, sub_pops=0, cov_pops=0, cc_pops=0, cc_empty_pops=0, standard_generated=0,
                standard_enqueued=0, cov_generated=0, cov_valid=0, cov_enqueued=0)


def _result(g, solved, final, counters, extra=None):
    states, moves = g.path(final) if solved else (None, None)
    out = dict(counters, solved=solved, path=states, moves=moves, seen=len(g.key),
               max_seen_total=max(len(k) for k in g.key) - 1)
    out.update(extra or {})
    return out


def run_dual(start, expander, budget, max_total=None, threshold=2, seed=True, min_gap=0, deepest=True):
    """``run_compact_dual_gs`` (length score): a sub queue and one CoV queue fed by ``expander``.

    ``expander(state) -> (neighbors, n_generated, n_valid)`` with ``neighbors`` a list of ``(canonical state, move)``.
    The CoV queue is popped when its head is at least ``threshold + 1`` shorter than the sub head; one unit per pop.
    """
    g = _Graph(deepest)
    counters = _counters()
    s0 = canonical_pair(reduce_word(start[0]), reduce_word(start[1]))
    g.add(s0, None, 0, 0, START)
    cov = []
    if seed:
        g.flags[0] |= _F_COV_EXP | _F_COV_Q
        _expand(g, 0, expander, COV, counters)
    solved, final = False, None
    while counters["nodes"] < budget:
        sub_head, cov_head = _top(g.sub, g, _F_SUB_EXP), _top(cov, g, _F_COV_EXP)
        if sub_head is None and cov_head is None:
            break
        use_cov = sub_head is None or (cov_head is not None and _score(sub_head) - _score(cov_head) >= threshold + 1)
        if not use_cov:
            sid = heapq.heappop(g.sub) & _SID
            g.flags[sid] |= _F_SUB_EXP
            counters["nodes"] += 1
            counters["sub_pops"] += 1
            if _sub_pop(g, sid, max_total, counters):
                solved, final = True, sid
                break
            if not g.flags[sid] & _F_COV_Q and g.gap[sid] >= min_gap:
                g.flags[sid] |= _F_COV_Q
                heapq.heappush(cov, g.prio(len(g.key[sid]) - 1, g.depth[sid], sid))
        else:
            sid = heapq.heappop(cov) & _SID
            g.flags[sid] |= _F_COV_EXP
            counters["nodes"] += 1
            counters["cov_pops"] += 1
            _expand(g, sid, expander, COV, counters)
    return _result(g, solved, final, counters)


def run_triple(start, auto_expander, cov_expander, budget, max_total=None, auto_threshold=2, cov_threshold=2,
               seed_auto=True, seed_cov=True, min_gap_auto=0, cov_prefilter=None, charge_empty_cov_pops=True,
               deepest=True):
    """``run_compact_triple_gs`` (length score, total-length activation): sub, auto and CoV queues.

    Each step pops the queue with the least ``head score + offset`` (offsets 0, ``auto_threshold``, ``cov_threshold``;
    ties go sub, auto, CoV). The original charges no unit for a CoV pop with no neighbor and admits a state to the
    CoV queue only if ``cov_prefilter(state)`` holds (its composite-count rule); both are parameters here.
    """
    g = _Graph(deepest)
    counters = _counters()
    s0 = canonical_pair(reduce_word(start[0]), reduce_word(start[1]))
    g.add(s0, None, 0, 0, START)
    auto, cov = [], []
    if seed_auto:
        g.flags[0] |= _F_COV_Q | _F_COV_EXP
        _expand(g, 0, auto_expander, COV, counters)
    if seed_cov:
        g.flags[0] |= _F_CC_Q | _F_CC_EXP
        _expand(g, 0, cov_expander, COMPLETE, counters)
    solved, final = False, None
    while counters["nodes"] < budget:
        heads = (_top(g.sub, g, _F_SUB_EXP), _top(auto, g, _F_COV_EXP), _top(cov, g, _F_CC_EXP))
        if heads == (None, None, None):
            break
        best, pick = None, None
        for rank, (head, off) in enumerate(zip(heads, (0, auto_threshold, cov_threshold))):
            if head is not None and (best is None or _score(head) + off < best):
                best, pick = _score(head) + off, rank
        if pick == 0:
            sid = heapq.heappop(g.sub) & _SID
            g.flags[sid] |= _F_SUB_EXP
            counters["nodes"] += 1
            counters["sub_pops"] += 1
            if _sub_pop(g, sid, max_total, counters):
                solved, final = True, sid
                break
            length = len(g.key[sid]) - 1
            if not g.flags[sid] & _F_COV_Q and g.gap[sid] >= min_gap_auto:
                g.flags[sid] |= _F_COV_Q
                heapq.heappush(auto, g.prio(length, g.depth[sid], sid))
            if not g.flags[sid] & _F_CC_Q and (cov_prefilter is None or cov_prefilter(g.state(sid))):
                g.flags[sid] |= _F_CC_Q
                heapq.heappush(cov, g.prio(length, g.depth[sid], sid))
        elif pick == 1:
            sid = heapq.heappop(auto) & _SID
            g.flags[sid] |= _F_COV_EXP
            counters["nodes"] += 1
            counters["cov_pops"] += 1
            _expand(g, sid, auto_expander, COV, counters)
        else:
            sid = heapq.heappop(cov) & _SID
            g.flags[sid] |= _F_CC_EXP
            neighbors, generated, valid = cov_expander(g.state(sid))
            counters["cov_generated"] += generated
            counters["cov_valid"] += valid
            if not neighbors:
                counters["cc_empty_pops"] += 1
                if not charge_empty_cov_pops:
                    continue
            counters["nodes"] += 1
            counters["cc_pops"] += 1
            if counters["nodes"] < budget:
                for state, move in neighbors:
                    if g.add(state, sid, g.depth[sid] + 1, 0, COMPLETE, move) is not None:
                        counters["cov_enqueued"] += 1
    return _result(g, solved, final, counters)


def composite_prefilter(state):
    """The original triple's admission rule for its complete-CoV queue (``complete_cov_composite_eligible``)."""
    def composite(v):
        return v >= 4 and any(v % d == 0 for d in range(2, int(v ** 0.5) + 1))
    for w in state:
        nx = sum(c in "cd" for c in w)
        ny = len(w) - nx
        if composite(nx - 1) or composite(ny - 1):
            return True
    return False
