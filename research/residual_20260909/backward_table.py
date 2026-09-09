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

Completeness of the enumeration (that no predecessor is missed) is inherited
from the symmetry of the product set -- ``r_i <- r_i . r_j^{+1}`` and
``r_i <- r_i . r_j^{-1}`` undo each other up to the rotation and inversion that
canonicalisation quotients out -- and is checked directly against brute force
on small caps by ``tests/test_ball_policy.py``.

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
import pickle
import subprocess
import time
from pathlib import Path

import numpy as np
from numba import njit

from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move
from experiments.heuristic_search.core.hexpand import (
    _U0, _canon_packed, _encode_packed, _packed_ge, expand_children_h)
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

    ``states[0]`` is ``unpack(key)`` itself, so a caller splices with
    ``states += tail_states[1:]``; every step is a substitution step in the
    certificate schema the decoder reads.
    """
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
    return Path(path).with_suffix('.manifest.json')


def save(table, path, cap=None, build_stats=None, checks=None):
    """Pickle ``table`` to ``path`` and write ``<path stem>.manifest.json``.

    The manifest carries the cap, the size, the depth histogram, the build wall
    seconds, the sha256 of the pickle bytes, the git HEAD and the sha256 of
    every kernel source the table's contents depend on, plus whatever
    ``checks`` the caller ran.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = pickle.dumps(table, protocol=pickle.HIGHEST_PROTOCOL)
    path.write_bytes(blob)
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
    """Load a saved table, checking the pickle's sha256 against its manifest."""
    path = Path(path)
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
    table = build(args.cap, verify=True, aut_edges=args.aut_edges, stats=stats, progress=progress)
    checks = {}
    if not args.no_replay_check:
        started = time.perf_counter()
        replay = check_replay(table)
        replay['wall_seconds'] = time.perf_counter() - started
        checks['replay_all_entries'] = replay
        if not replay['ok']:
            raise SystemExit(f'replay check FAILED: {replay["failure_count"]} bad entries')
    manifest = save(table, args.out, cap=args.cap, build_stats=stats, checks=checks)
    print(json.dumps({k: manifest[k] for k in
                      ('cap', 'aut_edges', 'size', 'max_depth', 'automorphism_entries',
                       'build_wall_seconds', 'sha256', 'bytes')},
                     indent=2))
    return manifest


if __name__ == '__main__':
    main()
