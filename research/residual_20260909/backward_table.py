"""The exact backward ball B(cap) of the trivial pair, as a deterministic table.

WHAT THE TABLE IS
=================
``B(cap)`` is the set of canonical pairs ``s`` from which the engine's
substitution move can walk down to the trivial pair ``(x, y)`` while every
relator on the way stays at length ``<= cap``:

    s = s_0 -> s_1 -> ... -> s_d = (x, y),

where each ``s_{i} -> s_{i+1}`` is a child the production expansion kernel
(``experiments.heuristic_search.core.hexpand.expand_children_h``, the kernel
``plain_search_fast`` / ``mid_search`` pop with) actually emits, and every
``s_i`` has ``max(len(r1), len(r2)) <= cap``.  The table maps

    key(s)  ->  (depth d, key(successor s_1), forward move (t, jsign, k1, k2))

with the trivial pair itself stored at depth 0 with ``(None, None)``.  Keys are
``experiments.search.heuristic_1k.pack`` bytes (codes ``X=1, Y=2, x=3, y=4``
separated by a ``0`` byte), the same bytes the searches use as dictionary keys,
so a search can test membership with one hash lookup and, on a hit, read the
remaining certificate straight out of the table.

WHY THE BALL IS BUILT BACKWARDS, AND WHY PREDECESSORS NEED FULL PRODUCTS
=======================================================================
The trivial pair has *no* forward children in the kernel: every child the
kernel emits is a product ``rot_{k1}(r_i) . rot_{k2}(r_j^{jsign})`` whose seam
cancels (``A[-1] = B[0]^{-1}``), and for ``(x, y)`` no seam cancels.  So the
ball cannot be grown forwards.  Predecessors are therefore enumerated with the
*full* product set -- every target, both signs, every rotation ``k1`` of the
target relator and every rotation ``k2`` of the signed partner, with no seam
condition -- because the inverse of an engine move is again a product of that
shape, just not necessarily one the kernel would emit from this end.  Each
candidate is then canonicalised (``canonical_pair_nj``'s rule, computed on
packed words), filtered by ``max relator length <= cap``, and
FORWARD-VERIFIED: the kernel is run on the candidate exactly as the search
would run it (``cap=None`` semantics: expansion cap = the candidate's total
length) and the candidate is admitted only if the successor is literally among
the children the kernel emits, in which case the kernel's own move is stored.

That forward verification is what makes the table *sound*: every stored edge is
an edge the live search can take, and the recorded move is the live kernel's
move, so the stored tail replays.  ``check_replay`` re-derives every stored
edge a second time with the pure-Python ``words.replay_move`` (a different
implementation on a different data type), and the builder's CLI records the
result in the manifest.

WHAT IS EXACT, AND WHAT ``depth`` MEANS
=======================================
Two different claims, checked separately.

*The ball as a SET is exact.*  ``bruteforce_ball(cap)`` computes the true
backward ball the honest way -- enumerate EVERY canonical pair with both
relators of length <= cap, expand each with the kernel, reverse the edges and
BFS from the trivial pair -- and it agrees with ``build(cap)`` key for key:

    cap 6: 117 canonical relators,   6,903 canonical pairs, ball 317
    cap 7: 275 canonical relators,  37,950 canonical pairs, ball 2,333
    cap 8: 693 canonical relators, 240,471 canonical pairs, ball 6,069

(the universe grows about 6x per +1 cap, so this ground truth stops being
affordable above cap 8; ``tests/test_ball_policy.py`` runs the cap-6 case).
Since the ball set is what decides whether a search hits, this is the claim the
policies rest on.

*Every stored edge is real.*  Each admitted predecessor was forward-verified
with the very kernel the searches run, and ``check_replay`` re-derives every
stored edge with the pure-Python ``words.replay_move`` / ``words.apply_pair``.
So a spliced tail is a genuine path of engine moves to the trivial pair --
which is what the certificate decoder then re-checks a third time.

*``depth`` is an upper bound, not a geodesic.*  The predecessor enumeration
finds every state, but not every edge: an edge ``c -> s`` whose product is a
rotation of a CONJUGATE of ``s``'s relator (the case the kernel's cut-shift
skip describes) is not of the enumerated shape, so a state can enter the BFS
one or two layers later than its true backward distance.  Brute force puts the
true eccentricity at 6 / 9 / 14 for caps 6 / 7 / 8 where this builder reports
7 / 10 / 15.  Nothing depends on the number being minimal -- the stored tail is
a valid path of that length, and ``ball_depth`` is reported, never charged --
but it is an upper bound and is documented as one.

DETERMINISM
===========
Frontier states are processed in sorted key order and each state's candidates
in ``(target, jsign, k1, k2)`` order, so the table -- keys, depths, successors
and moves -- is a pure function of ``cap`` and the kernel sources whose hashes
the manifest carries.

CLI
===
    PYTHONPATH=. python3 -m research.residual_20260909.backward_table \\
        --cap 10 --out research/residual_20260909/tables/ball_cap10.pkl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import subprocess
import time
from pathlib import Path

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, canon_rel, replay_move
from experiments.heuristic_search.core.hexpand import (
    _U0, _U3, _canon_packed, _code_of_v, _encode_packed, _packed_ge, expand_children_h)
from experiments.heuristic_search.core.hfast import _arrs
from experiments.search.greedy_baseline import inverse_relator_nj, _reduce_into, _ridx
from experiments.search.heuristic_1k import NIELSEN, pack, unpack

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL_SOURCES = (
    'experiments/heuristic_search/core/hexpand.py',
    'experiments/heuristic_search/core/hfast.py',
    'experiments/equivalence_classes/lib/words.py',
    'experiments/search/greedy_baseline.py',
    'experiments/search/heuristic_1k.py',
    'research/residual_20260909/backward_table.py',
)
FORMAT_VERSION = 1


# ---------------------------------------------------------------------------
# numba: full-product predecessor candidates of one canonical pair
# ---------------------------------------------------------------------------
@njit(cache=True)
def _candidates(r1, r2, cap, out, stride, klen):
    """Write the packed keys of every canonical pair reachable from ``(r1, r2)``
    by one FULL product ``r_i <- rot_{k1}(r_i) . rot_{k2}(r_j^{jsign})`` whose
    canonical form has both relators nonempty and no relator longer than
    ``cap``.  Row ``c`` of the flat buffer ``out`` (stride ``stride``) holds
    ``klen[c]`` bytes: r1 codes, a ``0`` separator, r2 codes -- exactly
    ``heuristic_1k.pack``'s layout.  Returns the number of rows written
    (duplicates included; the caller dedups).

    The enumeration order is ``target -> jsign -> k1 -> k2``, the kernel's own
    order, and the canonical form / pair ordering is ``canonical_pair_nj``'s,
    computed on the packed words ``hexpand`` uses.
    """
    n1 = len(r1)
    n2 = len(r2)
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    nn = n1 + n2
    pbuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    D = np.empty(5, dtype=np.uint64)
    Di = np.empty(5, dtype=np.uint64)
    cnt = 0
    for target in range(1, 3):
        if target == 1:
            ri = r1
            rj = r2
            rj_inv = inv2
        else:
            ri = r2
            rj = r1
            rj_inv = inv1
        ni = len(ri)
        if ni == 0:
            continue
        # the untouched relator: reduce + canonicalise exactly as the kernel does
        lo_r, m_r = _reduce_into(rj, len(rj), True, rbuf)
        if m_r == 0 or m_r > cap:
            continue
        oh, ol = _canon_packed(rbuf, lo_r, m_r, D, Di)
        lo_o = m_r
        for idx in range(2):
            oj = rj if idx == 0 else rj_inv
            no = len(oj)
            if no == 0:
                continue
            for k1 in range(ni):
                for k2 in range(no):
                    for t in range(ni):
                        src = _ridx(k1, t, ni)
                        pbuf[t, 0] = ri[src, 0]
                        pbuf[t, 1] = ri[src, 1]
                    for t in range(no):
                        src = _ridx(k2, t, no)
                        pbuf[ni + t, 0] = oj[src, 0]
                        pbuf[ni + t, 1] = oj[src, 1]
                    lo, m = _reduce_into(pbuf, ni + no, True, rbuf)
                    if m == 0 or m > cap:
                        continue
                    ph, pl = _canon_packed(rbuf, lo, m, D, Di)
                    if target == 1:
                        swap = m > lo_o or (m == lo_o and _packed_ge(ph, pl, oh, ol))
                    else:
                        swap = lo_o > m or (lo_o == m and _packed_ge(oh, ol, ph, pl))
                    o = cnt * stride
                    if (target == 1) != swap:
                        _encode_packed(ph, pl, m, out, o)
                        out[o + m] = 0
                        _encode_packed(oh, ol, lo_o, out, o + m + 1)
                    else:
                        _encode_packed(oh, ol, lo_o, out, o)
                        out[o + lo_o] = 0
                        _encode_packed(ph, pl, m, out, o + lo_o + 1)
                    klen[cnt] = m + lo_o + 1
                    cnt += 1
    return cnt


@njit(cache=True)
def _forward_move(c1, c2, expansion_cap, sa, sb):
    """The kernel move taking the pair ``(c1, c2)`` to the canonical pair whose
    relator code arrays are ``(sa, sb)``, or ``(-1, 0, 0, 0)`` when the kernel
    emits no such child.  Runs ``expand_children_h`` with exactly the flags the
    production searches use (``cyclic=True, skip=True, packed=True``)."""
    cbuf, offs, lens, moves, count = expand_children_h(c1, c2, expansion_cap, True, True, True)
    la_t = len(sa)
    lb_t = len(sb)
    for i in range(count):
        if lens[i, 0] != la_t or lens[i, 1] != lb_t:
            continue
        o = offs[i]
        ok = True
        for t in range(la_t):
            if cbuf[o + t] != sa[t]:
                ok = False
                break
        if ok:
            for t in range(lb_t):
                if cbuf[o + la_t + t] != sb[t]:
                    ok = False
                    break
        if ok:
            return moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3]
    return -1, 0, 0, 0


def _warm(cap):
    """Force both kernels to compile before any timing starts."""
    r1, r2 = _arrs(pack(('x', 'y')))
    stride = 2 * cap + 2
    out = np.empty(16 * stride, dtype=np.uint8)
    klen = np.empty(16, dtype=np.int64)
    _candidates(r1, r2, cap, out, stride, klen)
    _forward_move(r1, r2, 2, np.frombuffer(b'\x03', dtype=np.uint8),
                  np.frombuffer(b'\x04', dtype=np.uint8))


# ---------------------------------------------------------------------------
# the builder
# ---------------------------------------------------------------------------
def build(cap, verify=True, aut_edges=False, stats=None, progress=None):
    """The exact backward ball at ``cap`` as ``key -> (depth, successor, move)``.

    ``verify=True`` (the default, and the only setting any shipped table is
    built with) forward-verifies every admitted predecessor with the kernel and
    stores the kernel's own move.  ``verify=False`` admits every full-product
    candidate and stores no move; it exists only so a test can show that the
    verification really does reject candidates, and its output must never be
    saved as a table.

    ``aut_edges=True`` closes the ball under the four ambient Nielsen
    automorphisms as well: for a table state ``s`` and each ``t`` in
    ``heuristic_1k.NIELSEN``, every ``c = apply_pair(s, u)`` (``u`` again one of
    the four) with ``max relator length <= cap`` and ``apply_pair(c, t) == s``
    becomes a predecessor whose stored move is ``dict(t)`` and whose
    certificate step is ``{'kind': 'automorphism', 'images': t}`` -- exactly
    the edge the ``aut_edges`` arm of ``mid_search`` generates, and exactly the
    edge the mixed-certificate decoder already knows how to replay.  The
    verification is the forward map itself (``apply_pair(c, t) == s``), done in
    pure Python, and ``check_replay`` redoes it independently.

    ``stats``, when a dict is passed, is filled in with the build accounting.
    ``progress``, when callable, is called once per depth with the level stats.
    """
    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 2:
        raise ValueError('cap must be an integer >= 2')
    if not isinstance(aut_edges, bool):
        raise ValueError('aut_edges must be boolean')
    if cap > 64:
        raise ValueError('cap must be <= 64 (the packed canonicalisation path)')
    _warm(cap)
    started = time.perf_counter()
    stride = 2 * cap + 2
    room = 4 * cap * cap + 8
    out = np.empty(room * stride, dtype=np.uint8)
    klen = np.empty(room, dtype=np.int64)

    root = pack(canon_pair('x', 'y'))
    table = {root: (0, None, None)}
    frontier = [root]
    depth = 0
    candidates_seen = 0
    verifications = 0
    levels = []
    while frontier:
        depth += 1
        nxt = []
        level_candidates = 0
        level_verifications = 0
        for skey in frontier:
            sep = skey.index(0)
            sa = np.frombuffer(skey[:sep], dtype=np.uint8)
            sb = np.frombuffer(skey[sep + 1:], dtype=np.uint8)
            r1, r2 = _arrs(skey)
            count = _candidates(r1, r2, cap, out, stride, klen)
            level_candidates += count
            raw = out[:count * stride].tobytes()
            local = set()
            for i in range(count):
                base = i * stride
                ckey = raw[base:base + int(klen[i])]
                if ckey in table or ckey in local:
                    continue
                local.add(ckey)
                if verify:
                    c1, c2 = _arrs(ckey)
                    level_verifications += 1
                    move = _forward_move(c1, c2, len(ckey) - 1, sa, sb)
                    if move[0] < 0:
                        continue
                    table[ckey] = (depth, skey, tuple(int(v) for v in move))
                else:
                    table[ckey] = (depth, skey, None)
                nxt.append(ckey)
            if aut_edges:
                state = unpack(skey)
                back = [apply_pair(state, transform) for transform in NIELSEN]
                forward = {}
                for transform in NIELSEN:
                    for j, candidate in enumerate(back):
                        if max(map(len, candidate)) > cap:
                            continue
                        seen_forward = forward.get((j, id(transform)))
                        if seen_forward is None:
                            seen_forward = apply_pair(candidate, transform)
                            forward[(j, id(transform))] = seen_forward
                        level_candidates += 1
                        if seen_forward != state:
                            continue
                        ckey = pack(candidate)
                        if ckey in table:
                            continue
                        table[ckey] = (depth, skey, dict(transform))
                        nxt.append(ckey)
        candidates_seen += level_candidates
        verifications += level_verifications
        levels.append(dict(depth=depth, new=len(nxt), total=len(table),
                           candidates=level_candidates, verifications=level_verifications,
                           wall=time.perf_counter() - started))
        if progress is not None:
            progress(levels[-1])
        frontier = sorted(nxt)
    wall = time.perf_counter() - started
    if stats is not None:
        stats.update(cap=cap, verified=bool(verify), aut_edges=bool(aut_edges), size=len(table),
                     max_depth=depth - 1, build_wall_seconds=wall,
                     candidates_enumerated=candidates_seen,
                     forward_verifications=verifications,
                     depth_histogram=depth_histogram(table), levels=levels)
    return table


def canonical_relators(cap):
    """Every canonical relator of length 1..``cap``, sorted -- the alphabet of
    the universe of canonical pairs at that cap."""
    found = set()

    def walk(word):
        if word and word[0] != word[-1].swapcase():
            found.add(canon_rel(word))
        if len(word) == cap:
            return
        for letter in 'xXyY':
            if word and word[-1] == letter.swapcase():
                continue
            walk(word + letter)

    walk('')
    return sorted(word for word in found if word)


def bruteforce_ball(cap):
    """The true backward ball at ``cap``, computed without any predecessor
    enumeration: expand EVERY canonical pair with both relators of length
    <= ``cap`` with the kernel, reverse the edges, BFS from the trivial pair.

    Returns ``{key: depth}``.  Exact by construction and exponentially more
    expensive than ``build`` (the universe is ~6x larger per +1 cap), so it is
    the ground truth for small caps only.
    """
    from collections import deque
    from experiments.heuristic_search.core.hexpand import expand_and_score_h
    from experiments.heuristic_search.core.hfast import compile_config
    from experiments.search.heuristics import BASELINE_CONFIG
    upto, weights, _unused = compile_config(BASELINE_CONFIG)
    relators = canonical_relators(cap)
    universe = set()
    for i, first in enumerate(relators):
        for second in relators[i:]:
            universe.add(pack(canon_pair(first, second)))
    predecessors = {}
    for key in universe:
        r1, r2 = _arrs(key)
        blob, offsets, lengths, _segs, _scores, _t, _k, _moves, count = expand_and_score_h(
            r1, r2, len(key) - 1, True, upto, weights, True, True)
        raw = blob.tobytes()
        for i in range(count):
            start = int(offsets[i])
            child = raw[start:start + int(lengths[i])]
            sep = child.index(0)
            if max(sep, len(child) - sep - 1) > cap:
                continue
            predecessors.setdefault(child, set()).add(key)
    root = pack(canon_pair('x', 'y'))
    depth = {root: 0}
    queue = deque([root])
    while queue:
        state = queue.popleft()
        for previous in predecessors.get(state, ()):
            if previous not in depth:
                depth[previous] = depth[state] + 1
                queue.append(previous)
    return depth


def has_automorphism_edges(table):
    """Whether any stored edge is a Nielsen automorphism rather than a
    substitution -- i.e. whether the table was built with ``aut_edges=True``."""
    return any(isinstance(move, dict) for _depth, _successor, move in table.values())


def depth_histogram(table):
    """``{depth: count}`` with string keys, JSON-ready and sorted by depth."""
    counts = {}
    for depth, _successor, _move in table.values():
        counts[depth] = counts.get(depth, 0) + 1
    return {str(key): counts[key] for key in sorted(counts)}


def table_cap(table):
    """The largest relator length present -- the cap the table was built at
    (every ball at ``cap`` contains a pair with a relator of that length for
    every cap this campaign uses; the manifest carries the declared value)."""
    return max(max(len(word) for word in unpack(key)) for key in table)


# ---------------------------------------------------------------------------
# exactness checks
# ---------------------------------------------------------------------------
def check_replay(table, limit=None):
    """Replay every stored edge with the pure-Python ``words.replay_move``.

    Returns ``{'entries': n, 'checked': m, 'failures': [...]}``.  A stored
    ``(key, successor, move)`` passes when ``replay_move(unpack(key), move)``
    -- free/cyclic reduction and canonicalisation done by a second,
    independent implementation -- is exactly ``unpack(successor)``, and when
    the successor's stored depth is one less than the key's.  An automorphism
    entry (the stored move is a ``dict`` of generator images, only present in
    an ``aut_edges`` table) is replayed with ``words.apply_pair`` instead.
    """
    failures = []
    checked = 0
    for key, (depth, successor, move) in table.items():
        if successor is None:
            if depth != 0 or move is not None:
                failures.append(dict(key=list(unpack(key)), reason='bad_root_entry'))
            continue
        if limit is not None and checked >= limit:
            break
        checked += 1
        if move is None:
            failures.append(dict(key=list(unpack(key)), reason='missing_move'))
            continue
        replayed = (apply_pair(unpack(key), move) if isinstance(move, dict)
                    else replay_move(unpack(key), move))
        if replayed != unpack(successor):
            failures.append(dict(key=list(unpack(key)), move=list(move),
                                 expected=list(unpack(successor)), got=list(replayed)))
            continue
        if successor not in table or table[successor][0] != depth - 1:
            failures.append(dict(key=list(unpack(key)), reason='successor_depth'))
    return dict(entries=len(table), checked=checked, failures=failures[:20],
                failure_count=len(failures), ok=not failures)


def tail(table, key):
    """``(states, steps)`` from ``key`` down to the trivial pair.

    A ``CompactTable`` supplies its own index-walking fast path; anything with
    a ``tail`` method is used directly.

    ``states[0]`` is ``unpack(key)`` itself, so a caller splices with
    ``states += tail_states[1:]``; every step is a substitution step in the
    certificate schema the decoder reads.
    """
    walk = getattr(table, 'tail', None)
    if walk is not None:
        return walk(key)
    states = [list(unpack(key))]
    steps = []
    while True:
        _depth, successor, move = table[key]
        if successor is None:
            return states, steps
        if isinstance(move, dict):
            steps.append({'kind': 'automorphism', 'images': move})
        else:
            steps.append({'kind': 'substitution', 'move': '_'.join(str(int(v)) for v in move)})
        states.append(list(unpack(successor)))
        key = successor


# ---------------------------------------------------------------------------
# persistence
# ---------------------------------------------------------------------------
def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _git_head():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def _kernel_hashes():
    return {name: _sha256((ROOT / name).read_bytes()) for name in KERNEL_SOURCES}


def manifest_path(path):
    """The manifest beside a table file.

    ``.pkl`` keeps the historical ``<stem>.manifest.json``; ``.npz`` appends
    instead (``<stem>.npz.manifest.json``) so a compact table and a dict table
    of the same ball never share -- and overwrite -- one manifest."""
    path = Path(path)
    if path.suffix == '.npz':
        return path.with_name(path.name + '.manifest.json')
    return path.with_suffix('.manifest.json')


def save(table, path, cap=None, build_stats=None, checks=None):
    if isinstance(table, CompactTable):
        return table.save(path, build_stats=build_stats, checks=checks)
    """Pickle ``table`` to ``path`` and write ``<path stem>.manifest.json``.

    The manifest carries the cap, the size, the depth histogram, the build wall
    seconds, the sha256 of the pickle bytes, the git HEAD and the sha256 of
    every kernel source the table's contents depend on, plus whatever
    ``checks`` the caller ran.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = pickle.dumps(table, protocol=pickle.HIGHEST_PROTOCOL)
    scratch = path.with_suffix(path.suffix + '.partial')
    scratch.write_bytes(blob)
    os.replace(scratch, path)
    stats = dict(build_stats or {})
    levels = stats.pop('levels', None)
    manifest = dict(
        format_version=FORMAT_VERSION,
        pickle=path.name,
        cap=int(cap if cap is not None else stats.get('cap', table_cap(table))),
        size=len(table),
        max_relator_length=table_cap(table),
        depth_histogram=depth_histogram(table),
        max_depth=max(depth for depth, _s, _m in table.values()),
        build_wall_seconds=stats.get('build_wall_seconds'),
        candidates_enumerated=stats.get('candidates_enumerated'),
        forward_verifications=stats.get('forward_verifications'),
        forward_verified=stats.get('verified', True),
        aut_edges=stats.get('aut_edges', has_automorphism_edges(table)),
        automorphism_entries=sum(1 for _d, _s, move in table.values() if isinstance(move, dict)),
        sha256=_sha256(blob),
        bytes=len(blob),
        git_head=_git_head(),
        kernel_source_sha256=_kernel_hashes(),
        checks=checks or {},
        built_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    )
    if levels is not None:
        manifest['levels'] = levels
    manifest_path(path).write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def load(path, verify_sha256=True):
    """Load a saved table, checking its sha256 against the manifest beside it.

    ``.npz`` gives a ``CompactTable``, ``.pkl`` the plain dict."""
    path = Path(path)
    if path.suffix == '.npz':
        return CompactTable.load(path, verify_sha256=verify_sha256)
    blob = path.read_bytes()
    if verify_sha256:
        mpath = manifest_path(path)
        if not mpath.exists():
            raise FileNotFoundError(f'no manifest beside {path}; cannot verify sha256')
        manifest = json.loads(mpath.read_text())
        digest = _sha256(blob)
        if digest != manifest.get('sha256'):
            raise ValueError(f'{path}: sha256 {digest} does not match manifest '
                             f'{manifest.get("sha256")}')
    table = pickle.loads(blob)
    if not isinstance(table, dict) or not table:
        raise ValueError(f'{path}: not a nonempty table')
    return table


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--cap', required=True, type=int, help='maximum relator length in the ball')
    parser.add_argument('--out', required=True, type=Path, help='destination .pkl (manifest beside it)')
    parser.add_argument('--compact', action='store_true',
                        help='build the uint64/numpy CompactTable and save it as .npz')
    parser.add_argument('--sample', type=int, default=100000,
                        help='compact mode: replay-check this many random entries '
                             'plus every entry of depth <= 3')
    parser.add_argument('--buffer', type=int, default=4000000,
                        help='compact mode: candidate buffer entries per chunk')
    parser.add_argument('--aut-edges', action='store_true',
                        help='also close the ball under the four Nielsen automorphisms')
    parser.add_argument('--no-replay-check', action='store_true',
                        help='skip the pure-Python replay of every stored edge')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)

    def progress(level):
        if not args.quiet:
            print('cap={cap} depth={depth} new={new} total={total} '
                  'candidates={candidates} verifications={verifications} '
                  't={wall:.1f}s'.format(cap=args.cap, **level), flush=True)

    stats = {}
    if args.compact:
        table = build_compact(args.cap, aut_edges=args.aut_edges, stats=stats,
                              progress=progress, buffer=args.buffer)
    else:
        table = build(args.cap, verify=True, aut_edges=args.aut_edges,
                      stats=stats, progress=progress)
    checks = {}
    if not args.no_replay_check:
        started = time.perf_counter()
        if args.compact:
            replay = check_replay_sample(table, sample=args.sample)
            name = 'replay_sampled_entries'
        else:
            replay = check_replay(table)
            name = 'replay_all_entries'
        replay['wall_seconds'] = time.perf_counter() - started
        checks[name] = replay
        if not replay['ok']:
            raise SystemExit(f'replay check FAILED: {replay["failure_count"]} bad entries')
    manifest = save(table, args.out, cap=args.cap, build_stats=stats, checks=checks)
    print(json.dumps({k: manifest[k] for k in
                      ('cap', 'aut_edges', 'size', 'max_depth', 'automorphism_entries',
                       'build_wall_seconds', 'sha256', 'bytes')},
                     indent=2))
    return manifest



# ===========================================================================
# COMPACT MODE: one uint64 per canonical pair, numpy columns instead of a dict
# ===========================================================================
"""
At cap 14 the ball is tens of millions of states and the ``dict`` of ``bytes``
keys used above would need several gigabytes per worker.  Compact mode stores
the same information in four numpy columns and never materialises a Python
object per state.

THE PACKING (a bijection on canonical pairs with both relators of length 1..15)
------------------------------------------------------------------------------
A canonical pair is ``(r1, r2)`` with ``la = len(r1)``, ``lb = len(r2)``, both
in ``1..15``, and (at cap <= 14) ``la + lb <= 28``.  Each symbol is one of the
four engine codes ``X=1, Y=2, x=3, y=4``, so ``code - 1`` is two bits.  The
64-bit word is

    bits 63..60   la              (4 bits, 1..15)
    bits 59..56   lb              (4 bits, 1..15)
    bits 55..0    symbols, two bits each, little-endian:
                  symbol t of r1 at bits 2t, symbol t of r2 at bits 2*(la+t)

which uses ``2*(la+lb) <= 56`` payload bits.  It is a bijection because the two
lengths are recorded separately from the payload and each symbol occupies its
own field; ``_unpack_u64`` inverts it exactly, returning the same
``heuristic_1k.pack`` bytes the dict tables use.  ``0`` is never a valid word
(``la >= 1`` forces a nonzero high nibble), so it doubles as the empty slot of
the build's hash set.

THE MOVE CODE (one int32)
-------------------------
    -1                      no move (the trivial pair itself)
    -2                      substitution, not yet verified (build-time only)
    byte0 = 1 or 2          substitution: target; byte1 = 1 for jsign +1 and
                            2 for jsign -1; byte2 = k1; byte3 = k2
    byte0 = 0               RESERVED for the four Nielsen automorphism steps:
                            byte1 is the index into ``heuristic_1k.NIELSEN``

Every field is at most 14 for cap 14, so the packed value stays far below
2**31 and the column is a plain int32.
"""

_MOVE_NONE = -1
_MOVE_UNVERIFIED = -2
COMPACT_MAX_CAP = 14


@njit(inline='always')
def _u64_word(hi, m, shift):
    """The ``m`` symbols of the packed canonical word ``hi`` (most significant
    symbol first, order values) as ``code - 1`` fields starting at bit
    ``2*shift``."""
    out = np.uint64(0)
    for t in range(m):
        v = (hi >> np.uint64(2 * (m - 1 - t))) & _U3
        out |= np.uint64(np.int64(_code_of_v(v)) - 1) << np.uint64(2 * (shift + t))
    return out


@njit(inline='always')
def _u64_pair(ah, la, bh, lb):
    """Pack the canonical pair (word ``ah`` of ``la`` symbols, word ``bh`` of
    ``lb`` symbols) into one uint64."""
    return ((np.uint64(la) << np.uint64(60)) | (np.uint64(lb) << np.uint64(56))
            | _u64_word(ah, la, 0) | _u64_word(bh, lb, la))


@njit(inline='always')
def _u64_to_arrays(key, a, b):
    """Write the two relators of the packed key into the preallocated bool
    arrays ``a`` and ``b``; return ``(la, lb)``."""
    la = np.int64((key >> np.uint64(60)) & np.uint64(0xF))
    lb = np.int64((key >> np.uint64(56)) & np.uint64(0xF))
    for t in range(la):
        c = np.int64((key >> np.uint64(2 * t)) & np.uint64(3)) + 1
        a[t, 0] = (c & 1) == 1
        a[t, 1] = c >= 3
    for t in range(lb):
        c = np.int64((key >> np.uint64(2 * (la + t))) & np.uint64(3)) + 1
        b[t, 0] = (c & 1) == 1
        b[t, 1] = c >= 3
    return la, lb


def _unpack_u64(key):
    """Packed uint64 -> the ``heuristic_1k.pack`` bytes key (exact inverse)."""
    key = int(key)
    la = (key >> 60) & 0xF
    lb = (key >> 56) & 0xF
    out = bytearray(la + lb + 1)
    for t in range(la):
        out[t] = ((key >> (2 * t)) & 3) + 1
    out[la] = 0
    for t in range(lb):
        out[la + 1 + t] = ((key >> (2 * (la + t))) & 3) + 1
    return bytes(out)


@njit(cache=True)
def _pack_bytes_key(codes):
    """``heuristic_1k.pack`` bytes -> packed uint64, or 0 when the pair does
    not fit the packing (a relator longer than 15 symbols)."""
    n = len(codes)
    sep = -1
    for i in range(n):
        if codes[i] == 0:
            sep = i
            break
    if sep < 0:
        return np.uint64(0)
    la = sep
    lb = n - sep - 1
    if la < 1 or lb < 1 or la > 15 or lb > 15 or la + lb > 28:
        return np.uint64(0)
    out = (np.uint64(la) << np.uint64(60)) | (np.uint64(lb) << np.uint64(56))
    for t in range(la):
        out |= np.uint64(np.int64(codes[t]) - 1) << np.uint64(2 * t)
    for t in range(lb):
        out |= np.uint64(np.int64(codes[sep + 1 + t]) - 1) << np.uint64(2 * (la + t))
    return out


def _decode_move(code):
    """int32 move code -> the object the dict tables store."""
    code = int(code)
    if code < 0:
        return None
    if (code & 0xFF) == 0:
        return dict(NIELSEN[(code >> 8) & 0xFF])
    return (code & 0xFF, 1 if ((code >> 8) & 0xFF) == 1 else -1,
            (code >> 16) & 0xFF, (code >> 24) & 0xFF)


def _encode_move(move):
    """The inverse of ``_decode_move`` (used by the pickle -> compact check)."""
    if move is None:
        return _MOVE_NONE
    if isinstance(move, dict):
        for index, transform in enumerate(NIELSEN):
            if dict(transform) == dict(move):
                return index << 8
        raise ValueError(f'not a Nielsen transform: {move!r}')
    target, jsign, k1, k2 = move
    return (target & 0xFF) | ((1 if jsign == 1 else 2) << 8) | (k1 << 16) | (k2 << 24)


# ---------------------------------------------------------------------------
# numba: packed candidate generation
# ---------------------------------------------------------------------------
@njit(inline='always')
def _nielsen_image(rel, n, m, out):
    """Write ``apply_hom(rel[:n], NIELSEN[m])`` (free reduction NOT applied)
    into ``out``; return its length.  ``out`` must hold ``2*n`` rows."""
    k = 0
    for t in range(n):
        v = 2 * np.int64(rel[t, 0]) + np.int64(rel[t, 1])   # Y=0 y=1 X=2 x=3
        if m == 0:                                          # x -> xy
            if v == 2:
                out[k, 0] = False; out[k, 1] = False; k += 1     # Y
                out[k, 0] = True;  out[k, 1] = False; k += 1     # X
                continue
            if v == 3:
                out[k, 0] = True;  out[k, 1] = True;  k += 1     # x
                out[k, 0] = False; out[k, 1] = True;  k += 1     # y
                continue
        elif m == 1:                                        # x -> xY
            if v == 2:
                out[k, 0] = False; out[k, 1] = True;  k += 1     # y
                out[k, 0] = True;  out[k, 1] = False; k += 1     # X
                continue
            if v == 3:
                out[k, 0] = True;  out[k, 1] = True;  k += 1     # x
                out[k, 0] = False; out[k, 1] = False; k += 1     # Y
                continue
        elif m == 2:                                        # y -> yx
            if v == 0:
                out[k, 0] = True;  out[k, 1] = False; k += 1     # X
                out[k, 0] = False; out[k, 1] = False; k += 1     # Y
                continue
            if v == 1:
                out[k, 0] = False; out[k, 1] = True;  k += 1     # y
                out[k, 0] = True;  out[k, 1] = True;  k += 1     # x
                continue
        else:                                               # y -> yX
            if v == 0:
                out[k, 0] = True;  out[k, 1] = True;  k += 1     # x
                out[k, 0] = False; out[k, 1] = False; k += 1     # Y
                continue
            if v == 1:
                out[k, 0] = False; out[k, 1] = True;  k += 1     # y
                out[k, 0] = True;  out[k, 1] = False; k += 1     # X
                continue
        out[k, 0] = rel[t, 0]; out[k, 1] = rel[t, 1]; k += 1
    return k


@njit(inline='always')
def _nielsen_pair(a, la, b, lb, m, cap, ibuf, rbuf, D, Di):
    """``apply_pair((a, b), NIELSEN[m])`` as a packed uint64, or 0 when a
    relator vanishes or exceeds ``cap``.  Mirrors ``words.apply_pair``:
    apply the homomorphism, free+cyclically reduce, canonicalise, order."""
    n = _nielsen_image(a, la, m, ibuf)
    lo1, m1 = _reduce_into(ibuf, n, True, rbuf)
    if m1 == 0 or m1 > cap:
        return np.uint64(0)
    h1, _l1 = _canon_packed(rbuf, lo1, m1, D, Di)
    n = _nielsen_image(b, lb, m, ibuf)
    lo2, m2 = _reduce_into(ibuf, n, True, rbuf)
    if m2 == 0 or m2 > cap:
        return np.uint64(0)
    h2, _l2 = _canon_packed(rbuf, lo2, m2, D, Di)
    if m1 > m2 or (m1 == m2 and h1 >= h2):
        return _u64_pair(h2, m2, h1, m1)
    return _u64_pair(h1, m1, h2, m2)


@njit(cache=True)
def _candidates_packed(r1, r2, cap, out_key, out_move, base):
    """Full-product predecessor candidates of the canonical pair ``(r1, r2)``
    as packed uint64 words, in ``target -> jsign -> k1 -> k2`` order, each
    tagged ``_MOVE_UNVERIFIED``.  Same enumeration and same filters as
    ``_candidates``; returns how many were written at ``out_key[base:]``."""
    inv1 = inverse_relator_nj(r1)
    inv2 = inverse_relator_nj(r2)
    nn = len(r1) + len(r2)
    pbuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    D = np.empty(5, dtype=np.uint64)
    Di = np.empty(5, dtype=np.uint64)
    cnt = 0
    for target in range(1, 3):
        if target == 1:
            ri = r1; rj = r2; rj_inv = inv2
        else:
            ri = r2; rj = r1; rj_inv = inv1
        ni = len(ri)
        if ni == 0:
            continue
        lo_r, m_r = _reduce_into(rj, len(rj), True, rbuf)
        if m_r == 0 or m_r > cap:
            continue
        oh, _ol = _canon_packed(rbuf, lo_r, m_r, D, Di)
        lo_o = m_r
        for idx in range(2):
            oj = rj if idx == 0 else rj_inv
            no = len(oj)
            if no == 0:
                continue
            for k1 in range(ni):
                for k2 in range(no):
                    for t in range(ni):
                        src = _ridx(k1, t, ni)
                        pbuf[t, 0] = ri[src, 0]; pbuf[t, 1] = ri[src, 1]
                    for t in range(no):
                        src = _ridx(k2, t, no)
                        pbuf[ni + t, 0] = oj[src, 0]; pbuf[ni + t, 1] = oj[src, 1]
                    lo, m = _reduce_into(pbuf, ni + no, True, rbuf)
                    if m == 0 or m > cap:
                        continue
                    ph, _pl = _canon_packed(rbuf, lo, m, D, Di)
                    if target == 1:
                        swap = m > lo_o or (m == lo_o and ph >= oh)
                    else:
                        swap = lo_o > m or (lo_o == m and oh >= ph)
                    if (target == 1) != swap:
                        out_key[base + cnt] = _u64_pair(ph, m, oh, lo_o)
                    else:
                        out_key[base + cnt] = _u64_pair(oh, lo_o, ph, m)
                    out_move[base + cnt] = _MOVE_UNVERIFIED
                    cnt += 1
    return cnt


@njit(cache=True)
def _aut_candidates_packed(r1, r2, self_key, cap, out_key, out_move, base):
    """Nielsen-automorphism predecessors of ``(r1, r2)``: for each transform
    ``i`` and each ``j``, the candidate ``apply_pair(s, NIELSEN[j])`` when
    ``apply_pair(candidate, NIELSEN[i]) == s``.  Emitted in ``i -> j`` order
    with move code ``i << 8``, matching the dict builder."""
    la = len(r1); lb = len(r2)
    nn = 2 * (la + lb) + 4
    ibuf = np.empty((nn, 2), dtype=np.bool_)
    rbuf = np.empty((nn, 2), dtype=np.bool_)
    ca = np.empty((nn, 2), dtype=np.bool_)
    cb = np.empty((nn, 2), dtype=np.bool_)
    D = np.empty(5, dtype=np.uint64)
    Di = np.empty(5, dtype=np.uint64)
    back = np.zeros(4, dtype=np.uint64)
    for j in range(4):
        back[j] = _nielsen_pair(r1, la, r2, lb, j, cap, ibuf, rbuf, D, Di)
    fwd = np.zeros((4, 4), dtype=np.uint64)
    done = np.zeros((4, 4), dtype=np.bool_)
    cnt = 0
    for i in range(4):
        for j in range(4):
            if back[j] == 0:
                continue
            if not done[j, i]:
                na, nb = _u64_to_arrays(back[j], ca, cb)
                fwd[j, i] = _nielsen_pair(ca, na, cb, nb, i, cap, ibuf, rbuf, D, Di)
                done[j, i] = True
            if fwd[j, i] != self_key:
                continue
            out_key[base + cnt] = back[j]
            out_move[base + cnt] = i << 8
            cnt += 1
    return cnt


@njit(cache=True)
def _level_chunk(frontier_keys, start, cap, aut, out_key, out_succ, out_move):
    """Generate the candidates of ``frontier_keys[start:]`` until the output
    buffer would overflow.  Returns ``(states_consumed, candidates_written)``.
    Each candidate carries the POSITION in the frontier of the state that
    proposed it, so the level pass can verify it against that successor and
    store the successor's table index."""
    room = 4 * cap * cap + 20
    cnt = 0
    i = start
    a = np.empty((16, 2), dtype=np.bool_)
    b = np.empty((16, 2), dtype=np.bool_)
    while i < len(frontier_keys):
        if cnt + room > len(out_key):
            break
        la, lb = _u64_to_arrays(frontier_keys[i], a, b)
        r1 = a[:la].copy()
        r2 = b[:lb].copy()
        made = _candidates_packed(r1, r2, cap, out_key, out_move, cnt)
        if aut:
            made += _aut_candidates_packed(r1, r2, frontier_keys[i], cap,
                                           out_key, out_move, cnt + made)
        for t in range(cnt, cnt + made):
            out_succ[t] = i
        cnt += made
        i += 1
    return i - start, cnt


@njit(cache=True)
def _verify_many(cands, succs, moves, cap):
    """Forward-verify every candidate tagged ``_MOVE_UNVERIFIED`` in place.

    Runs the production kernel on the candidate exactly as a search would
    (expansion cap = the candidate's total length) and writes the kernel's own
    move, or ``-1`` when the kernel does not emit the successor.  Candidates
    that already carry a move (the automorphism edges, verified by their own
    forward map at generation time) are left alone.
    """
    a = np.empty((16, 2), dtype=np.bool_)
    b = np.empty((16, 2), dtype=np.bool_)
    sa = np.empty(16, dtype=np.uint8)
    sb = np.empty(16, dtype=np.uint8)
    for n in range(len(cands)):
        if moves[n] != _MOVE_UNVERIFIED:
            continue
        la, lb = _u64_to_arrays(cands[n], a, b)
        skey = succs[n]
        sla = np.int64((skey >> np.uint64(60)) & np.uint64(0xF))
        slb = np.int64((skey >> np.uint64(56)) & np.uint64(0xF))
        for t in range(sla):
            sa[t] = np.uint8(np.int64((skey >> np.uint64(2 * t)) & np.uint64(3)) + 1)
        for t in range(slb):
            sb[t] = np.uint8(np.int64((skey >> np.uint64(2 * (sla + t))) & np.uint64(3)) + 1)
        target, jsign, k1, k2 = _forward_move(a[:la].copy(), b[:lb].copy(),
                                              la + lb, sa[:sla], sb[:slb])
        if target < 0:
            moves[n] = -1
        else:
            moves[n] = (target & 0xFF) | ((1 if jsign == 1 else 2) << 8) | (k1 << 16) | (k2 << 24)
    return moves


# ---------------------------------------------------------------------------
# numba: open-addressing uint64 hash set (build-time membership)
# ---------------------------------------------------------------------------
@njit(inline='always')
def _mix64(x):
    x = x ^ (x >> np.uint64(33))
    x = x * np.uint64(0xff51afd7ed558ccd)
    x = x ^ (x >> np.uint64(33))
    x = x * np.uint64(0xc4ceb9fe1a85ec53)
    return x ^ (x >> np.uint64(33))


@njit(cache=True)
def _hs_add(slots, keys):
    """Insert every key; ``0`` is the empty slot and never a valid key."""
    mask = np.uint64(len(slots) - 1)
    added = 0
    for i in range(len(keys)):
        k = keys[i]
        p = _mix64(k) & mask
        while True:
            cur = slots[p]
            if cur == k:
                break
            if cur == np.uint64(0):
                slots[p] = k
                added += 1
                break
            p = (p + np.uint64(1)) & mask
    return added


@njit(cache=True)
def _hs_missing(slots, keys, out):
    """``out[i] = keys[i] not in slots``."""
    mask = np.uint64(len(slots) - 1)
    for i in range(len(keys)):
        k = keys[i]
        p = _mix64(k) & mask
        while True:
            cur = slots[p]
            if cur == k:
                out[i] = False
                break
            if cur == np.uint64(0):
                out[i] = True
                break
            p = (p + np.uint64(1)) & mask
    return out


@njit(cache=True)
def _hs_rehash(slots, bits):
    bigger = np.zeros(1 << bits, dtype=np.uint64)
    mask = np.uint64(len(bigger) - 1)
    for i in range(len(slots)):
        k = slots[i]
        if k == np.uint64(0):
            continue
        p = _mix64(k) & mask
        while bigger[p] != np.uint64(0):
            p = (p + np.uint64(1)) & mask
        bigger[p] = k
    return bigger


# ---------------------------------------------------------------------------
# numba: sorted-array lookup for the finished table
# ---------------------------------------------------------------------------
@njit(cache=True)
def _find_u64(keys, key):
    """Index of ``key`` in the sorted uint64 array, or -1."""
    lo = 0
    hi = len(keys)
    while lo < hi:
        mid = (lo + hi) >> 1
        if keys[mid] < key:
            lo = mid + 1
        else:
            hi = mid
    if lo < len(keys) and keys[lo] == key:
        return lo
    return -1


@njit(cache=True)
def _find_bytes(keys, codes):
    """Index of the ``heuristic_1k.pack`` bytes key in the sorted array, or -1.

    Takes the ``bytes`` object straight from the search -- numba reads it as a
    read-only uint8 buffer -- so a membership test is one call: pack, then
    binary search, with no Python-level work in between.
    """
    key = _pack_bytes_key(codes)
    if key == np.uint64(0):
        return -1
    return _find_u64(keys, key)


# ---------------------------------------------------------------------------
# CompactTable
# ---------------------------------------------------------------------------
class CompactTable:
    """The backward ball in four numpy columns instead of a Python dict.

    Reads like the dict tables -- ``key in table``, ``table[key]``,
    ``table.get(key)``, ``len(table)`` -- with ``key`` the same
    ``heuristic_1k.pack`` bytes the searches already build, and
    ``table[key] == (depth, successor_key_bytes_or_None, move_or_None)`` in the
    same format, so ``backward_table.tail`` and the whole ball cascade work
    unchanged.  ``tail(key)`` is overridden with an index-walking fast path
    that never re-hashes.

    Columns (all sorted by ``keys``):
        keys   uint64  the packed pair, see the module's COMPACT MODE note
        depth  uint16  BFS layer
        succ   int64   index of the successor row, -1 at the trivial pair
        move   int32   packed move code, -1 at the trivial pair
    """
    __slots__ = ('keys', 'depth', 'succ', 'move', 'cap', 'aut_edges', 'path')

    def __init__(self, keys, depth, succ, move, cap, aut_edges, path=None):
        self.keys = np.ascontiguousarray(keys, dtype=np.uint64)
        self.depth = np.ascontiguousarray(depth, dtype=np.uint16)
        self.succ = np.ascontiguousarray(succ, dtype=np.int64)
        self.move = np.ascontiguousarray(move, dtype=np.int32)
        self.cap = int(cap)
        self.aut_edges = bool(aut_edges)
        self.path = path

    # -- mapping protocol ---------------------------------------------------
    def __len__(self):
        return len(self.keys)

    def index(self, key):
        """Row index of a packed-bytes key, or -1."""
        return _find_bytes(self.keys, key)

    def __contains__(self, key):
        return _find_bytes(self.keys, key) >= 0

    def _entry(self, i):
        successor = int(self.succ[i])
        return (int(self.depth[i]),
                None if successor < 0 else _unpack_u64(self.keys[successor]),
                _decode_move(self.move[i]))

    def __getitem__(self, key):
        i = _find_bytes(self.keys, key)
        if i < 0:
            raise KeyError(key)
        return self._entry(i)

    def get(self, key, default=None):
        i = _find_bytes(self.keys, key)
        return default if i < 0 else self._entry(i)

    def __iter__(self):
        for i in range(len(self.keys)):
            yield _unpack_u64(self.keys[i])

    def items(self):
        for i in range(len(self.keys)):
            yield _unpack_u64(self.keys[i]), self._entry(i)

    def values(self):
        for i in range(len(self.keys)):
            yield self._entry(i)

    # -- certificate tail ---------------------------------------------------
    def tail(self, key):
        """``(states, steps)`` from ``key`` down to the trivial pair, walking
        row indices instead of re-looking-up every successor."""
        i = _find_bytes(self.keys, key)
        if i < 0:
            raise KeyError(key)
        states = [list(unpack(_unpack_u64(self.keys[i])))]
        steps = []
        while True:
            move = _decode_move(self.move[i])
            i = int(self.succ[i])
            if i < 0:
                return states, steps
            if isinstance(move, dict):
                steps.append({'kind': 'automorphism', 'images': move})
            else:
                steps.append({'kind': 'substitution', 'move': '_'.join(str(int(v)) for v in move)})
            states.append(list(unpack(_unpack_u64(self.keys[i]))))

    # -- persistence --------------------------------------------------------
    def save(self, path, build_stats=None, checks=None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        scratch = path.with_suffix(path.suffix + '.partial')
        with scratch.open('wb') as stream:
            np.savez(stream, keys=self.keys, depth=self.depth,
                     succ=self.succ, move=self.move,
                     cap=np.int64(self.cap), aut_edges=np.bool_(self.aut_edges))
        os.replace(scratch, path)
        blob = path.read_bytes()
        stats = dict(build_stats or {})
        levels = stats.pop('levels', None)
        counts = np.bincount(self.depth)
        manifest = dict(
            format_version=FORMAT_VERSION, representation='compact_npz',
            npz=path.name, cap=self.cap, aut_edges=self.aut_edges,
            size=len(self), packing=('la:63-60 lb:59-56 then 2 bits per symbol '
                                     '(code-1), r1 then r2, little-endian'),
            automorphism_entries=int(np.count_nonzero(
                (self.move >= 0) & ((self.move & 0xFF) == 0))),
            depth_histogram={str(d): int(c) for d, c in enumerate(counts) if c},
            max_depth=int(self.depth.max()),
            build_wall_seconds=stats.get('build_wall_seconds'),
            candidates_enumerated=stats.get('candidates_enumerated'),
            forward_verifications=stats.get('forward_verifications'),
            peak_rss_bytes=stats.get('peak_rss_bytes'),
            forward_verified=True,
            sha256=_sha256(blob), bytes=len(blob),
            git_head=_git_head(), kernel_source_sha256=_kernel_hashes(),
            checks=checks or {},
            built_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        )
        if levels is not None:
            manifest['levels'] = levels
        manifest_path(path).write_text(json.dumps(manifest, indent=2) + '\n')
        return manifest

    @classmethod
    def load(cls, path, verify_sha256=True):
        path = Path(path)
        if verify_sha256:
            mpath = manifest_path(path)
            if not mpath.exists():
                raise FileNotFoundError(f'no manifest beside {path}; cannot verify sha256')
            manifest = json.loads(mpath.read_text())
            digest = _sha256(path.read_bytes())
            if digest != manifest.get('sha256'):
                raise ValueError(f'{path}: sha256 {digest} does not match manifest '
                                 f'{manifest.get("sha256")}')
        with np.load(path) as data:
            return cls(data['keys'], data['depth'], data['succ'], data['move'],
                       int(data['cap']), bool(data['aut_edges']), path=str(path))


# ---------------------------------------------------------------------------
# the compact builder
# ---------------------------------------------------------------------------
def _peak_rss():
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    except Exception:
        return None


def _warm_compact(cap):
    root = np.array([_pack_bytes_key(pack(('x', 'y')))], dtype=np.uint64)
    key = np.empty(4096, dtype=np.uint64)
    succ = np.empty(4096, dtype=np.int64)
    move = np.empty(4096, dtype=np.int32)
    for aut in (False, True):
        _level_chunk(root, 0, cap, aut, key, succ, move)
    _verify_many(root, root, np.array([_MOVE_UNVERIFIED], dtype=np.int32), cap)
    slots = np.zeros(16, dtype=np.uint64)
    _hs_add(slots, root)
    _hs_missing(slots, root, np.empty(1, dtype=np.bool_))
    _hs_rehash(slots, 5)
    _find_u64(root, root[0])
    _find_bytes(root, pack(('x', 'y')))


def build_compact(cap, verify=True, aut_edges=False, stats=None, progress=None,
                  buffer=4_000_000, hash_bits=21):
    """``build`` with the compact representation: a ``CompactTable``.

    Same ball, same enumeration, same forward verification -- only the
    bookkeeping changes.  Keys live in a uint64 column, level frontiers are
    numpy arrays, dedup is ``np.unique``, membership during the build is a
    numba open-addressing hash set, and verification is one batched numba call
    per chunk instead of one call per candidate.  The frontier is walked in
    chunks so the candidate buffer (and therefore peak memory) is bounded no
    matter how wide a level gets.

    A candidate whose first proposing successor fails verification is retried
    against its other proposals at the same level, exactly as the dict builder
    does, so the ball and the depths are identical to ``build``'s.  The stored
    successor can differ when several proposals verify, because the frontier is
    ordered by packed key here and by the raw byte key there; both are kernel
    edges and both replay.
    """
    if isinstance(cap, bool) or not isinstance(cap, int) or not 2 <= cap <= COMPACT_MAX_CAP:
        raise ValueError(f'compact mode needs an integer cap in 2..{COMPACT_MAX_CAP}')
    if not isinstance(aut_edges, bool):
        raise ValueError('aut_edges must be boolean')
    if not verify:
        raise ValueError('compact mode always forward-verifies')
    _warm_compact(cap)
    started = time.perf_counter()

    out_key = np.empty(buffer, dtype=np.uint64)
    out_succ = np.empty(buffer, dtype=np.int64)
    out_move = np.empty(buffer, dtype=np.int32)
    missing = np.empty(buffer, dtype=np.bool_)

    root = np.uint64(_pack_bytes_key(pack(canon_pair('x', 'y'))))
    key_chunks = [np.array([root], dtype=np.uint64)]
    depth_chunks = [np.zeros(1, dtype=np.uint16)]
    succ_chunks = [np.full(1, -1, dtype=np.int64)]
    move_chunks = [np.full(1, _MOVE_NONE, dtype=np.int32)]
    total = 1
    slots = np.zeros(1 << hash_bits, dtype=np.uint64)
    filled = _hs_add(slots, key_chunks[0])

    frontier_keys = key_chunks[0]
    frontier_index = np.zeros(1, dtype=np.int64)
    depth = 0
    candidates_seen = 0
    verifications = 0
    levels = []
    while len(frontier_keys):
        depth += 1
        level_keys = []
        level_index = []
        level_candidates = 0
        level_verifications = 0
        start = 0
        while start < len(frontier_keys):
            consumed, count = _level_chunk(frontier_keys, start, cap, aut_edges,
                                           out_key, out_succ, out_move)
            if consumed == 0:
                raise RuntimeError('candidate buffer too small for one state')
            start += consumed
            level_candidates += count
            cand = out_key[:count]
            spos = out_succ[:count]
            mv = out_move[:count]
            _hs_missing(slots, cand, missing[:count])
            fresh = missing[:count]
            cand = cand[fresh]
            spos = spos[fresh]
            mv = mv[fresh]
            if not len(cand):
                continue
            unique, first = np.unique(cand, return_index=True)
            take_pos = spos[first]
            take_move = mv[first].copy()
            level_verifications += int(np.count_nonzero(take_move == _MOVE_UNVERIFIED))
            _verify_many(unique, frontier_keys[take_pos], take_move, cap)
            good = take_move >= 0
            accepted_keys = [unique[good]]
            accepted_pos = [take_pos[good]]
            accepted_move = [take_move[good]]
            bad = unique[~good]
            if len(bad):
                # a first proposal that the kernel does not emit does not
                # disqualify the candidate: retry every other proposal it got
                # at this level, in the same order the dict builder would.
                again = np.isin(cand, bad)
                c2 = cand[again]
                s2 = spos[again]
                m2 = mv[again].copy()
                order = np.argsort(c2, kind='stable')
                c2 = c2[order]; s2 = s2[order]; m2 = m2[order]
                level_verifications += int(np.count_nonzero(m2 == _MOVE_UNVERIFIED))
                _verify_many(c2, frontier_keys[s2], m2, cap)
                ok = m2 >= 0
                if np.any(ok):
                    c3 = c2[ok]; s3 = s2[ok]; m3 = m2[ok]
                    u3, f3 = np.unique(c3, return_index=True)
                    accepted_keys.append(u3)
                    accepted_pos.append(s3[f3])
                    accepted_move.append(m3[f3])
            new_keys = np.concatenate(accepted_keys)
            if not len(new_keys):
                continue
            new_pos = np.concatenate(accepted_pos)
            new_move = np.concatenate(accepted_move)
            order = np.argsort(new_keys, kind='stable')
            new_keys = new_keys[order]
            new_succ = frontier_index[new_pos[order]]
            new_move = new_move[order]
            key_chunks.append(new_keys)
            depth_chunks.append(np.full(len(new_keys), depth, dtype=np.uint16))
            succ_chunks.append(new_succ)
            move_chunks.append(new_move)
            level_index.append(np.arange(total, total + len(new_keys), dtype=np.int64))
            level_keys.append(new_keys)
            total += len(new_keys)
            filled += _hs_add(slots, new_keys)
            while filled * 2 > len(slots):
                hash_bits += 1
                slots = _hs_rehash(slots, hash_bits)
        candidates_seen += level_candidates
        verifications += level_verifications
        if level_keys:
            frontier_keys = np.concatenate(level_keys)
            frontier_index = np.concatenate(level_index)
            order = np.argsort(frontier_keys, kind='stable')
            frontier_keys = frontier_keys[order]
            frontier_index = frontier_index[order]
        else:
            frontier_keys = np.empty(0, dtype=np.uint64)
            frontier_index = np.empty(0, dtype=np.int64)
        levels.append(dict(depth=depth, new=len(frontier_keys), total=total,
                           candidates=level_candidates,
                           verifications=level_verifications,
                           wall=time.perf_counter() - started,
                           rss=_peak_rss()))
        if progress is not None:
            progress(levels[-1])

    keys = np.concatenate(key_chunks)
    depths = np.concatenate(depth_chunks)
    succ = np.concatenate(succ_chunks)
    move = np.concatenate(move_chunks)
    del key_chunks, depth_chunks, succ_chunks, move_chunks
    order = np.argsort(keys, kind='stable')
    rank = np.empty(len(order), dtype=np.int64)
    rank[order] = np.arange(len(order), dtype=np.int64)
    keys = keys[order]
    depths = depths[order]
    move = move[order]
    succ = succ[order]
    known = succ >= 0
    succ = np.where(known, rank[np.where(known, succ, 0)], -1)
    table = CompactTable(keys, depths, succ, move, cap, aut_edges)
    wall = time.perf_counter() - started
    if stats is not None:
        stats.update(cap=cap, verified=True, aut_edges=bool(aut_edges),
                     size=len(table), max_depth=depth - 1,
                     build_wall_seconds=wall, candidates_enumerated=candidates_seen,
                     forward_verifications=verifications, levels=levels,
                     peak_rss_bytes=_peak_rss())
    return table


def check_replay_sample(table, sample=100_000, seed=20260909, shallow_depth=3):
    """Replay a sample of a (compact) table: EVERY entry of depth <=
    ``shallow_depth`` plus a uniform random sample of at least ``sample``
    others, each re-derived with the pure-Python ``words.replay_move`` /
    ``words.apply_pair`` and checked against the stored successor and depth."""
    size = len(table)
    shallow = np.flatnonzero((table.depth <= shallow_depth) & (table.depth > 0))
    rng = np.random.default_rng(seed)
    extra = rng.choice(size, size=min(sample, size), replace=False)
    picked = np.unique(np.concatenate([shallow, extra]))
    failures = []
    checked = 0
    for i in picked:
        i = int(i)
        successor = int(table.succ[i])
        if successor < 0:
            continue
        checked += 1
        move = _decode_move(table.move[i])
        pair = unpack(_unpack_u64(table.keys[i]))
        want = unpack(_unpack_u64(table.keys[successor]))
        got = apply_pair(pair, move) if isinstance(move, dict) else replay_move(pair, move)
        if got != want:
            failures.append(dict(key=list(pair), move=move, expected=list(want),
                                 got=list(got)))
        elif int(table.depth[successor]) != int(table.depth[i]) - 1:
            failures.append(dict(key=list(pair), reason='successor_depth'))
    return dict(entries=size, checked=checked, shallow_entries=int(len(shallow)),
                sample_requested=int(sample), failures=failures[:20],
                failure_count=len(failures), ok=not failures)


if __name__ == '__main__':
    main()
