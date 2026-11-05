"""Ryan Zang's CoV-gate best-first search with the full change-of-variables image family as its CoV move.

The search is cov_gates_cpu.search (heap order, canonical form, dedup, the six gates, no length cap). Only the CoV
move at a gate opening changes, by ``mode``:

    ryan    Ryan's CoV moves only (one window of one relator substituted once; always an automorphism of F2).
    union   Ryan's CoV moves, then every image of ``acx.cov`` family ``suballpxyb8`` (default).
    full    the ``suballpxyb8`` images only.

``suballpxyb8`` (acx/cov/family.py): z := w for every cyclic subword w of length 2 to |r| - 1, every set of
non-overlapping occurrences of w^{+-1} in both relators substituted, x or y eliminated through either relator, one
image per class up to relator order, rotation, inversion and the 8 signed permutations, no length limit. Ryan's
one-letter windows are not in it (a one-letter z is a relabelling once every occurrence is substituted); ``union``
keeps them through Ryan's own moves, so its move set contains Ryan's.

Units: one per pop, plus one per gate opening when ``charge`` (the CoV expansion of the state is a second
expansion). Ryan's code charges pops only (``charge=False``). The search never depends on the budget, so a solve
within budget B is a solve whose ``units`` is at most B.

A solve is tagged ``ac_path`` when every CoV step on the path keeps the state in its Aut(F2) orbit, else
``stable_cert`` (a step of Lemma 11 outside the orbit proves only stable AC-triviality). verify_full.py replays
every step independently.
"""
from __future__ import annotations

import heapq
import sys
import time
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import cov_gates_cpu as C  # noqa: E402
from acx.aut import orbit_key  # noqa: E402
from acx.core.words import Presentation, canonical_rels  # noqa: E402
from acx.cov.states import cov_states  # noqa: E402

C.set_caps(None, None)
MODES = ("ryan", "union", "full")
FAMILY = "suballpxyb8"


def images(key):
    """``[(child_key, image)]``: every CoV state of ``key`` (``acx.cov.states.cov_states``), in the family's order."""
    return [(C.canonical_key(*im.pres.rels), im) for im in cov_states(*key[1])]


def automorphic(a, b):
    """The states ``a``, ``b`` (canonical keys) lie in one Aut(F2) orbit; None if the orbit search hits its cap."""
    try:
        return orbit_key(Presentation(2, canonical_rels(a[1])), "fast") == \
            orbit_key(Presentation(2, canonical_rels(b[1])), "fast")
    except RuntimeError:
        return None


def children(key, mode, cov):
    """The children of ``key`` in expansion order, as ``(kind, action, image or None)``: substitutions, then (when
    ``cov``) Ryan's CoV moves and/or the images. The index in this list is what the search stores per state."""
    out = [("sub", a, None) for a in C.substitution_actions(key)]
    if cov:
        if mode in ("ryan", "union"):
            out += [("cov", a, None) for a in C.cov_actions(key)]
        if mode in ("union", "full"):
            out += [("img", None, im) for _, im in images(key)]
    return out


def search(start, gate, max_units, mode="union", charge=True):
    """Best-first search from the canonical key ``start``; returns a record (cov_gates_cpu schema plus units)."""
    if mode not in MODES:
        raise ValueError(mode)
    t0 = time.monotonic()
    enc0 = C.encode(start)
    ids, blobs = {enc0: 0}, [enc0]
    parent, via, opened = array("q", [-1]), array("l", [-1]), array("b", [0])
    queue = [C._pack(C.total_length(start), 0, 0)]
    seq = pops = openings = units = 0
    n_sub = n_cov = n_img = img_states_new = 0
    img_seconds = 0.0
    best = C.total_length(start)
    last_improved = 0
    max_gen_rel = max(len(w) for w in start[1])

    def push(child, depth, pid, idx):
        nonlocal seq, max_gen_rel
        blob = C.encode(child)
        if blob in ids:
            return False
        seq += 1
        ids[blob] = seq
        blobs.append(blob)
        parent.append(pid)
        via.append(idx)
        opened.append(0)
        heapq.heappush(queue, C._pack(C.total_length(child), depth + 1, seq))
        m = max(len(child[1][0]), len(child[1][1]))
        if m > max_gen_rel:
            max_gen_rel = m
        return True

    while queue and units < max_units:
        length, depth, sid = C._unpack(heapq.heappop(queue))
        key = C.decode(blobs[sid])
        pops += 1
        units += 1
        if C.is_trivial(key):
            return _record(True, "solved", locals_=dict(
                pops=pops, openings=openings, units=units, states=len(ids), n_sub=n_sub, n_cov=n_cov, n_img=n_img,
                img_new=img_states_new, img_seconds=img_seconds, best=best, max_gen_rel=max_gen_rel, t0=t0),
                path=_path(sid, blobs, parent, via, opened, mode))
        if length < best:
            best, last_improved = length, pops
        current = C.total_length(key)
        shorter = False
        subs = C.substitution_actions(key)
        for idx, a in enumerate(subs):
            nxt = C.apply_substitution(key, a)
            if nxt is None or nxt == key:
                continue
            n_sub += 1
            if C.total_length(nxt) < current:
                shorter = True
            push(nxt, depth, sid, idx)
        lens = (len(key[1][0]), len(key[1][1]))
        should_open = {
            "no_short_sub": not shorter,
            "short_relator": min(lens) <= 3,
            "unbalanced": max(lens) >= 2 * min(lens),
            "long_presentation": length >= 16,
            "plateau100": pops - last_improved >= 100,
            "periodic10": pops % 10 == 0,
        }[gate]
        if not should_open:
            continue
        openings += 1
        opened[sid] = 1
        if charge:
            units += 1
        base = len(subs)
        if mode in ("ryan", "union"):
            covs = C.cov_actions(key)
            for j, a in enumerate(covs):
                nxt = C.apply_cov(key, a)
                if nxt is None or nxt == key:
                    continue
                n_cov += 1
                push(nxt, depth, sid, base + j)
            base += len(covs)
        if mode in ("union", "full"):
            t = time.perf_counter()
            imgs = images(key)
            img_seconds += time.perf_counter() - t
            for j, (nxt, _) in enumerate(imgs):
                if nxt == key:
                    continue
                n_img += 1
                img_states_new += push(nxt, depth, sid, base + j)
    return _record(False, "budget" if queue else "frontier_exhausted", locals_=dict(
        pops=pops, openings=openings, units=units, states=len(ids), n_sub=n_sub, n_cov=n_cov, n_img=n_img,
        img_new=img_states_new, img_seconds=img_seconds, best=best, max_gen_rel=max_gen_rel, t0=t0), path=None)


def _path(sid, blobs, parent, via, opened, mode):
    """The solution path as step dicts, each child re-derived from its parent's expansion list."""
    chain = []
    cur = sid
    while cur != -1:
        chain.append(cur)
        cur = parent[cur]
    chain.reverse()
    steps = [{"state": C._payload(C.decode(blobs[chain[0]]))}]
    for prev, cur in zip(chain, chain[1:]):
        pkey, ckey = C.decode(blobs[prev]), C.decode(blobs[cur])
        kind, action, image = children(pkey, mode, bool(opened[prev]))[via[cur]]
        got = C.apply_substitution(pkey, action) if kind == "sub" else (
            C.apply_cov(pkey, action) if kind == "cov" else C.canonical_key(*image.pres.rels))
        if got != ckey:
            raise RuntimeError(f"path step does not re-derive: {kind} {action}")
        step = {"kind": kind, "state": C._payload(ckey)}
        if action is not None:
            step["action"] = list(action)
        if image is not None:
            step["cov"] = {"steps": [_jsonable(s) for s in image.steps], "tag": image.tag, "n_subs": image.n_subs,
                           "automorphic": automorphic(pkey, ckey)}
        steps.append(step)
    return steps


def _jsonable(step):
    """A CoV step dict with tuples turned into lists."""
    out = {}
    for k, v in step.items():
        if isinstance(v, tuple):
            v = [list(x) if isinstance(x, tuple) else x for x in v]
        out[k] = v
    return out


def _record(solved, reason, locals_, path):
    d = locals_
    rec = {"solved": solved, "termination": reason, "units": d["units"], "nodes_visited": d["pops"],
           "gate_openings": d["openings"], "states_seen": d["states"],
           "children_sub": d["n_sub"], "children_cov": d["n_cov"], "children_img": d["n_img"],
           "img_states_new": d["img_new"], "img_seconds": round(d["img_seconds"], 3),
           "elapsed_sec": round(time.monotonic() - d["t0"], 3), "best_popped_length": d["best"],
           "max_relator_len_generated": d["max_gen_rel"]}
    if solved:
        kinds = [s["kind"] for s in path[1:]]
        img = [s["cov"] for s in path[1:] if s["kind"] == "img"]
        stable = sum(1 for c in img if c["automorphic"] is not True)
        rec.update(kind="stable_cert" if stable else "ac_path", path_img_non_aut=stable,
                   path_length=len(kinds), path_sub_moves=kinds.count("sub"), path_cov_moves=kinds.count("cov"),
                   path_img_moves=kinds.count("img"),
                   path_img_max_subs=max((c["n_subs"] for c in img), default=0),
                   max_relator_len=max(max(len(w) for w in s["state"]["relators"]) for s in path), path=path)
    else:
        rec.update(kind=None, path_length=None, path=[])
    return rec
