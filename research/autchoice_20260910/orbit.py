"""Balls in the Aut(F2)-orbit of a presentation, every image carrying its own witness.

``ball(pair, radius, cap)`` is a breadth-first search over the 20 Whitehead automorphisms
(``autcanon.AUTOS``, fixed order) from ``canon_pair(pair)``.  Nodes are Aut-images of the
pair, **deduplicated by ``words.relabel_key``** -- the canonical form under the 8 signed
permutations -- because a signed permutation only renames the generators and the search
engine does not care which is called ``x``.  The representative that is recorded and
later *run* is the first image discovered in BFS order (``canon_pair`` of the elementary
application), never the relabel key itself; for the identity that is exactly the pair the
ladder ran, so the identity's cost stays comparable with the ladder's record.

Every node carries

    seq    the AUTOS indices applied, in application order (``seq[0]`` first)
    phi    the composite automorphism, built with ``autcanon.compose`` and verified with
           ``autcanon.check(start, image, phi)`` before the node is returned
    depth  == len(seq); the identity (depth 0) comes first

Images whose longer relator exceeds ``cap`` are dropped and not expanded (the engine
would refuse them at that cap anyway).  Nothing here is random: the AUTOS order, the BFS
queue and the dedup make the ball a deterministic function of the input.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS, ID, check, compose  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    SIGNED_PERMS, apply_pair, canon_pair, relabel_key, replay_move, rot, inv,
)

ROOT_STATE = canon_pair('x', 'y')          # ('Y', 'X'): the trivial presentation, canonical


def apply_sequence(pair, seq):
    """Apply ``AUTOS[i]`` for ``i in seq`` one at a time (elementary steps), canonicalising
    after each; returns the final canonical pair."""
    cur = canon_pair(*pair)
    for i in seq:
        cur = apply_pair(cur, AUTOS[i])
    return cur


def compose_sequence(seq):
    """The composite automorphism of ``seq`` (``seq[0]`` applied first)."""
    phi = dict(ID)
    for i in seq:
        phi = compose(AUTOS[i], phi)
    return phi


def ball(pair, radius, cap=48):
    """BFS ball of ``radius`` around ``canon_pair(pair)``; see the module docstring.

    Returns a list of dicts ``{r1, r2, seq, phi, depth, rkey}`` -- identity first, then in
    BFS discovery order.  ``rkey`` is the relabel key the node was deduplicated on.
    """
    start = canon_pair(*pair)
    if max(len(start[0]), len(start[1])) > cap:
        raise ValueError(f'start pair exceeds cap {cap}: {start}')
    first = {'r1': start[0], 'r2': start[1], 'seq': [], 'phi': dict(ID), 'depth': 0,
             'rkey': relabel_key(start)}
    out = [first]
    seen = {first['rkey']}
    frontier = [first]
    for depth in range(1, radius + 1):
        nxt = []
        for node in frontier:
            src = (node['r1'], node['r2'])
            for i, a in enumerate(AUTOS):
                img = apply_pair(src, a)
                if max(len(img[0]), len(img[1])) > cap:
                    continue
                key = relabel_key(img)
                if key in seen:
                    continue
                seen.add(key)
                phi = compose(a, node['phi'])
                if not check(start, img, phi):
                    raise AssertionError(f'witness failed: {start} -> {img} via {phi}')
                rec = {'r1': img[0], 'r2': img[1], 'seq': node['seq'] + [i], 'phi': phi,
                       'depth': depth, 'rkey': key}
                out.append(rec)
                nxt.append(rec)
        frontier = nxt
    return out


def find_relabel(src_pair, target_pair):
    """The signed permutation ``sigma`` with ``apply_pair(src, sigma) == target``, or None."""
    for _, sigma in SIGNED_PERMS:
        if apply_pair(src_pair, sigma) == target_pair:
            return sigma
    return None


def all_moves(pair):
    """Every Definition 2.1 move ``(target, jsign, k1, k2)`` available from ``pair``."""
    r1, r2 = pair
    for target, (ri, rj) in ((1, (r1, r2)), (2, (r2, r1))):
        for jsign in (1, -1):
            for k1 in range(max(1, len(ri))):
                for k2 in range(max(1, len(rj))):
                    yield (target, jsign, k1, k2)


def greedy_descent(pair, max_steps=200):
    """Strict length descent by AC moves: at each step the move (over ``all_moves``) whose
    result has the smallest total length, ties broken by the canonical state; stops when no
    move shortens the pair.  Returns ``(states, moves)``; ``states[0]`` is the start."""
    cur = canon_pair(*pair)
    states, moves = [cur], []
    for _ in range(max_steps):
        best = None
        for m in all_moves(cur):
            nxt = replay_move(cur, m)
            t = len(nxt[0]) + len(nxt[1])
            if t < len(cur[0]) + len(cur[1]) and (best is None or (t, nxt) < best[:2]):
                best = (t, nxt, m)
        if best is None:
            break
        cur = best[1]
        states.append(cur)
        moves.append(best[2])
    return states, moves


def ball_sizes(pair, radii=(1, 2, 3), cap=48):
    return {r: len(ball(pair, r, cap)) for r in radii}


if __name__ == '__main__':
    import csv
    import time
    rows = list(csv.DictReader(open(ROOT / 'benchmark' / 'ladder' / 'ladder_20.csv')))
    for row in rows:
        t0 = time.perf_counter()
        sizes = ball_sizes((row['r1'], row['r2']))
        print(f"{row['name']:>14} L{row['level']:>2} {row['form']:>11} len={row['start_len']:>3} "
              f"ball r1/r2/r3 = {sizes[1]:>3}/{sizes[2]:>4}/{sizes[3]:>5}  "
              f"({time.perf_counter() - t0:.2f}s)")
