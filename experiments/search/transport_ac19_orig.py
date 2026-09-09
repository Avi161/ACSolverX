"""Carry each original's AC certificate onto its Aut-minimal representative.

THE QUESTION
------------
The pre-aut-min originals of the AC19 10M residue all solve (``ac19_orig_10m``)
while their ``Aut(F2)``-minimal representatives exhausted 10,000,000 nodes. Avi
asked: the original's path is known, so apply the same moves to the
representative and show it solves, with the path length for each of the 28.

WHY IT WORKS, AND WHAT "THE SAME MOVES" MEANS
---------------------------------------------
``aut_canon(orig)`` ships the witnessing automorphism ``phi`` with
``canon_pair(phi(orig)) == rep``. AC moves are equivariant under ``Aut(F2)``:
every stored move is ``r_i <- r_i . c^-1 r_j^s c`` for a conjugator word ``c``
(``ac_decode.to_conjugator``), and under ``phi`` it is the same move with
``c -> phi(c)``. So the original's path, transported step by step, is a path
from ``rep`` to ``(phi(t1), phi(t2))`` where ``(t1, t2)`` is the terminal the
search stopped on -- a BASIS of ``F2``, since ``phi`` is an automorphism. By
Nielsen's theorem a basis reaches a terminal pair by moves that are themselves
AC moves; ``ac_decode.reduce_basis`` finds the shortest such tail.

Nothing here searches. It is the algebra of ``decode_elementary`` with a
general ``phi`` as the frame instead of a product of elementary automorphisms,
and the result is replayed from ``rep`` by ``replay_elementary``, which trusts
nothing above it. A certificate this module returns has replayed to
``['x', 'y']`` from the representative's own words.

LENGTHS
-------
``orig_moves`` is the search's ``path_length`` (engine moves, each one
conjugated multiplication). ``tail_moves`` is the Nielsen tail in the same
vocabulary. ``rep_moves = orig_moves + tail_moves`` is the representative's
path length in the same units as every ``path_length`` in the campaign.
``elementary`` is the generator-level count (invert / swap / conjugate-by-a-
letter / multiply), the form that is actually replayed.

    PYTHONPATH=. python3 -m experiments.search.transport_ac19_orig
"""
from __future__ import annotations

import argparse
import json
import os

from experiments.equivalence_classes.lib.autcanon import aut_canon, check, phi_str
from experiments.equivalence_classes.lib.words import (
    apply_hom, canon_pair, canon_rel, free_reduce, inv,
)
from experiments.search import make_ac19_orig_10m_lists as mk
from experiments.search.ac_decode import (
    IDENTITY, _canonical_word_witness, _ElementaryTrace, _emit_canonicalization,
    is_terminal, reduce_basis, replay_elementary, to_conjugator,
)
from experiments.search.decode_ac_jsonl import pack_move
from experiments.search.greedy_baseline import moves_to_states
from experiments.search.run_leftovers_1m import read_rows

OUT_DIR = os.path.join(mk.RESULTS_DIR, "ac19_orig_10m")
SOURCE = {"greedy": "ac19_orig_10m_greedy_b10000000_mrl64.jsonl",
          "s20_mk2": "leftovers_1m_s20_mk2_b1000000_mrl64_paths.jsonl"}
OUT = {arm: f"ac19_orig_10m_transported_{arm}.jsonl" for arm in SOURCE}


def _emit_uncanonicalization(trace, canonical, raw):
    """Moves taking the canonical pair the trace sits on to the raw words.

    The inverse of ``_emit_canonicalization``: ``canon_rel(raw_i)`` is
    ``c^-1 raw_i^sign c``, so ``raw_i`` is ``(c own_i c^-1)^sign``.
    """
    own = [canon_rel(raw[0]), canon_rel(raw[1])]
    if own == list(canonical):
        pass
    elif own[::-1] == list(canonical):
        trace.swap()
    else:
        raise AssertionError(f"{canonical} is not the canonical form of {raw}")
    for i in range(2):
        sign, conjugator = _canonical_word_witness(raw[i], own[i])
        trace.conjugate_word(i + 1, inv(conjugator))
        if sign == -1:
            trace.invert(i + 1)
    if trace.pair != [free_reduce(w) for w in raw]:
        raise AssertionError(f"uncanonicalization ended at {trace.pair}, "
                             f"wanted {raw}")


def _conjugated_step(trace, current, move, frame):
    """One stored move on ``current``, emitted into the trace under ``frame``.

    Returns the raw (uncanonicalized) result in the ORIGINAL frame, which the
    caller canonicalizes against the next recorded state.
    """
    target, source_sign, conjugator = to_conjugator(current, move)
    trace.conjugated_multiply(target, source_sign, apply_hom(conjugator, frame))
    source = current[2 - target]
    oriented = source if source_sign == 1 else inv(source)
    raw = list(current)
    raw[target - 1] = free_reduce(
        current[target - 1] + inv(conjugator) + oriented + conjugator)
    return tuple(raw)


def transport(orig, states, moves, phi, basis_budget=4000):
    """``(elementary_moves, info)``: an AC certificate for ``canon_pair(phi(orig))``.

    ``states``/``moves`` are the original's recorded path (``path`` and
    ``path_moves`` of a solved record). Raises rather than returning anything
    that did not replay.
    """
    orig = (free_reduce(orig[0]), free_reduce(orig[1]))
    if tuple(states[0]) != tuple(canon_pair(*orig)):
        raise ValueError("path does not start at the canonical input")
    if len(states) != len(moves) + 1:
        raise ValueError("states must contain exactly one more entry than moves")
    if not is_terminal(tuple(states[-1])):
        raise ValueError(f"path does not end at a terminal pair: {states[-1]}")
    rep = tuple(canon_pair(apply_hom(orig[0], phi), apply_hom(orig[1], phi)))

    trace = _ElementaryTrace(rep)
    _emit_uncanonicalization(trace, rep, [apply_hom(w, phi) for w in states[0]])

    for index, mv in enumerate(moves):
        current = tuple(states[index])
        target_state = tuple(states[index + 1])
        move = tuple(map(int, mv.split("_")))
        raw = _conjugated_step(trace, current, move, phi)
        _emit_canonicalization(trace, raw, target_state, phi)
        expected = [apply_hom(w, phi) for w in target_state]
        if trace.pair != expected:
            raise AssertionError(f"transport diverged at step {index}: "
                                 f"got={trace.pair}, expected={expected}")

    # The trace now holds phi of the terminal: a basis, not yet a terminal.
    basis = tuple(canon_pair(*trace.pair))
    _emit_canonicalization(trace, tuple(trace.pair), basis, IDENTITY)
    tail = reduce_basis(basis, basis_budget)
    if tail is None:
        raise RuntimeError(f"basis {basis} not reduced within {basis_budget}")
    current = basis
    for move in tail:
        raw = _conjugated_step(trace, current, move, IDENTITY)
        nxt = tuple(moves_to_states(current[0], current[1], [move])[-1])
        _emit_canonicalization(trace, raw, nxt, IDENTITY)
        current = nxt
    if not is_terminal(current):
        raise AssertionError(f"tail ended at {current}, not a terminal")

    terminal = list(current)
    if terminal[0].lower() == "y":
        trace.swap()
        terminal.reverse()
    if terminal[0] == "X":
        trace.invert(1)
    if terminal[1] == "Y":
        trace.invert(2)
    if trace.pair != ["x", "y"]:
        raise AssertionError(f"trace ended at {trace.pair}")
    replayed = replay_elementary(rep, trace.moves)
    if replayed != ["x", "y"]:
        raise AssertionError(f"independent replay from {rep} ended at {replayed}")

    info = {"rep": list(rep), "basis": list(basis),
            "orig_moves": len(moves), "tail_moves": len(tail),
            "rep_moves": len(moves) + len(tail),
            "elementary": len(trace.moves), "replayed": True}
    return trace.moves, info


def transport_arm(arm, derived=None, log=print):
    """Every solved record of ``arm``, transported. Returns the output rows."""
    derived = derived or mk.build()
    want = {r["name"]: r for r in derived[arm]}
    recs = read_rows(os.path.join(OUT_DIR, SOURCE[arm]))
    if len(recs) != len(want):
        raise RuntimeError(f"{arm}: {len(recs)} records for {len(want)} originals")
    out = []
    for r in sorted(recs, key=lambda r: (want[r["name"]]["orbit"], r["name"])):
        row = want[r["name"]]
        orig = (r["r1"], r["r2"])
        _, rep, phi = aut_canon(orig)
        if not check(orig, rep, phi):
            raise AssertionError(f"{r['name']}: aut_canon witness fails its own check")
        if tuple(rep) != (row["rep_r1"], row["rep_r2"]):
            raise AssertionError(f"{r['name']}: canonicalizes to {rep}, "
                                 f"not its listed orbit representative")
        moves, info = transport(orig, r["path"], r["path_moves"], phi)
        out.append({"name": r["name"], "arm": arm, "orbit": row["orbit"],
                    "r1": r["r1"], "r2": r["r2"],
                    "rep_r1": rep[0], "rep_r2": rep[1],
                    "phi": phi_str(phi), "nodes_explored": r["nodes_explored"],
                    **info, "certificate": [pack_move(m) for m in moves]})
        log(f"  {arm:<8} {row['orbit']:<11} {r['name']:<13} "
            f"orig {info['orig_moves']:>3} + tail {info['tail_moves']:>2} "
            f"= {info['rep_moves']:>3} moves  ({info['elementary']:,} elementary)")
    return out


def write(rows, arm):
    path = os.path.join(OUT_DIR, OUT[arm])
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    return path


def per_orbit(rows_by_arm):
    """Shortest transported certificate per orbit, over every original and arm."""
    best = {}
    for arm, rows in rows_by_arm.items():
        for r in rows:
            cur = best.get(r["orbit"])
            key = (r["rep_moves"], r["elementary"])
            if cur is None or key < (cur["rep_moves"], cur["elementary"]):
                best[r["orbit"]] = {"orbit": r["orbit"], "rep": [r["rep_r1"], r["rep_r2"]],
                                    "via": r["name"], "arm": arm,
                                    "orig_moves": r["orig_moves"],
                                    "tail_moves": r["tail_moves"],
                                    "rep_moves": r["rep_moves"],
                                    "elementary": r["elementary"]}
    return [best[o] for o in sorted(best, key=lambda o: int(o.split("_")[1]))]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=sorted(SOURCE), default=None)
    args = ap.parse_args(argv)
    derived = mk.build()
    rows_by_arm = {}
    for arm in ([args.arm] if args.arm else sorted(SOURCE)):
        rows = transport_arm(arm, derived)
        rows_by_arm[arm] = rows
        print(f"  wrote {os.path.relpath(write(rows, arm))} ({len(rows)} rows, "
              f"all replayed)")
    if len(rows_by_arm) == len(SOURCE):
        print()
        print("  orbit        rep                              via            "
              "orig + tail = rep_moves   elementary")
        for b in per_orbit(rows_by_arm):
            print(f"  {b['orbit']:<12} ({b['rep'][0]}, {b['rep'][1]})".ljust(48)
                  + f" {b['via']:<13}  {b['orig_moves']:>3} + {b['tail_moves']:>2} "
                    f"= {b['rep_moves']:>3}        {b['elementary']:>6,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
