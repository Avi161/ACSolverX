"""Meet-in-the-middle: expand the certified stably-trivial targets backward, then
intersect with every class member this project has already harvested.

`certified_targets.py` supplies ~5,400 presentations that are stably AC-trivial (via
the Fagan-Qiu-Wang complexity < 6 theorem; flags recorded there).  A direct hash join
against our corpora found only the expected positive-control hits, which is
unsurprising: the targets are SHORT (total length 3V+3) and our harvests live at
length 13-25.  The two sets have to be grown toward each other.

AC moves are reversible, so a bounded backward expansion of the targets is the exact
mirror of a forward search from AK(3), and every state it produces is still stably
AC-trivial.  If any expanded target coincides with a harvested member of AK(3)'s class
(classical or stable), then AK(3) is stably AC-equivalent to a stably-trivial
presentation -- i.e. AK(3) is STABLY AC-TRIVIAL, the session's headline sub-goal.  Such
a coincidence is a CANDIDATE requiring the full replay protocol, never a claim.

This is bounded neighbourhood enumeration (every target expanded exhaustively to a
fixed depth), not a best-first search, so no search node budget is consumed; the
enumeration bound is recorded in the report.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter, deque

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ac_words import cyclic_reduce, inverse                     # noqa: E402
from certified_targets import (REPO_ROOT, TARGETS_JSON, canon_multi,  # noqa: E402
                               relabel_canon)

DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "target_meet.json")
CORPORA = (
    ("AK(3) classical class", "results/stable_ac/fable/ak3_matched_members.jsonl.gz"),
    ("AK(3)+z stable class",
     "results/stable_ac/fable/stable_contrast_ak3z_members.jsonl.gz"),
    ("AK(2) classical class (positive control)",
     "results/stable_ac/fable/ak2_members.jsonl"),
    ("AK(2)+z stable class (positive control)",
     "results/stable_ac/fable/stable_contrast_ak2z_members.jsonl.gz"),
)

MAX_RANK = 4              # expand only targets with at most this many generators
LENGTH_CAP = 26           # backward images longer than this are dropped
STATE_CAP = 400_000       # hard ceiling on the expanded set (reported if reached)


def rotations(word: str):
    return [word[i:] + word[:i] for i in range(len(word))]


def neighbours(state, length_cap: int):
    """Every AC2 graft image (all rotations, both signs, both directions), reduced.

    AC1 (inversion) and AC3 (conjugation) are absorbed by the canonical key, and
    AC4/AC5 change the rank, which the corpus comparison handles by matching each rank
    separately.
    """
    out = set()
    n = len(state)
    for host in range(n):
        for guest in range(n):
            if host == guest:
                continue
            for hw in rotations(state[host]):
                for gw in rotations(state[guest]):
                    for word in (gw, inverse(gw)):
                        merged = cyclic_reduce(hw + word)
                        if not merged:
                            continue
                        image = list(state)
                        image[host] = merged
                        if sum(len(w) for w in image) <= length_cap:
                            out.add(tuple(image))
    return out


def expand_targets(entries, depth: int, length_cap: int = LENGTH_CAP,
                   max_rank: int = MAX_RANK, state_cap: int = STATE_CAP) -> dict:
    """Backward closure of the low-rank targets to a bounded depth."""
    index = {}
    truncated = False
    frontier = deque()
    seeded = 0
    for entry in entries:
        relators = tuple(cyclic_reduce(w) for w in entry["relators"])
        relators = tuple(w for w in relators if w)
        generators = {c.lower() for w in relators for c in w}
        if len(generators) > max_rank:
            continue
        seeded += 1
        key = canon_multi(relators)
        if key not in index:
            index[key] = {"depth": 0, "target": entry, "state": list(relators)}
            frontier.append((relators, 0))
    print(f"[meet] seeded {seeded} targets of rank <= {max_rank}", flush=True)

    while frontier:
        state, d = frontier.popleft()
        if d >= depth:
            continue
        for image in neighbours(state, length_cap):
            key = canon_multi(image)
            if key in index:
                continue
            if len(index) >= state_cap:
                truncated = True
                frontier.clear()
                break
            index[key] = {"depth": d + 1, "target": None, "state": list(image)}
            frontier.append((image, d + 1))
        if len(index) % 50_000 == 0:
            print(f"[meet]   expanded {len(index)} states", flush=True)
    print(f"[meet] backward set: {len(index)} states (depth <= {depth}"
          f"{', TRUNCATED at cap' if truncated else ''})", flush=True)
    return {"index": index, "truncated": truncated, "seeded": seeded}


def _iter_members(path: str):
    opener = gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") \
        else open(path, encoding="utf-8")
    with opener as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            words = row.get("canonical") or row.get("pair")
            if isinstance(words, list) and words:
                yield tuple(words), row


def run(depth: int = 1, out_path: str = DEFAULT_OUT,
        targets_path: str = TARGETS_JSON) -> dict:
    with open(targets_path, encoding="utf-8") as handle:
        payload = json.load(handle)
    expansion = expand_targets(payload["targets"], depth)
    backward = expansion["index"]
    relabel_view = {}
    for key, value in backward.items():
        rkey = relabel_canon(value["state"])
        if rkey is not None:
            relabel_view.setdefault(rkey, value)

    report = {"record": "target_meet", "depth": depth,
              "length_cap": LENGTH_CAP, "max_rank": MAX_RANK,
              "state_cap": STATE_CAP, "backward_states": len(backward),
              "backward_truncated": expansion["truncated"],
              "targets_seeded": expansion["seeded"],
              "targets_meta": payload["meta"], "sources": [], "hits": []}

    for name, rel in CORPORA:
        path = os.path.join(REPO_ROOT, rel)
        if not os.path.exists(path):
            report["sources"].append({"name": name, "status": "MISSING"})
            continue
        checked = 0
        kinds: Counter = Counter()
        status = "OK"
        try:
            for words, _row in _iter_members(path):
                checked += 1
                hit = backward.get(canon_multi(words))
                kind = "exact"
                if hit is None:
                    rkey = relabel_canon(words)
                    hit = relabel_view.get(rkey) if rkey is not None else None
                    kind = "up_to_generator_relabelling"
                if hit is not None:
                    kinds[kind] += 1
                    report["hits"].append({
                        "source": name, "member": list(words), "match_kind": kind,
                        "backward_depth": hit["depth"],
                        "backward_state": hit["state"],
                        "seed_target": hit["target"],
                        "replay_required": ("CANDIDATE: reconstruct and replay the "
                                            "full AC path before any claim")})
        except (EOFError, OSError, json.JSONDecodeError) as exc:
            status = f"PARTIAL ({type(exc).__name__}: file still being written)"
        report["sources"].append({"name": name, "status": status,
                                  "members_checked": checked,
                                  "matches": dict(kinds)})
        print(f"[meet] {name}: {checked} members, {sum(kinds.values())} matches",
              flush=True)

    report["total_hits"] = len(report["hits"])
    report["LOUD_HIT_ALERT"] = any(h["source"].startswith("AK(3)")
                                   for h in report["hits"])
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[meet] wrote {out_path}; hits {report['total_hits']}; "
          f"AK(3)-side alert {report['LOUD_HIT_ALERT']}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--depth", type=int, default=1)
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    run(args.depth, args.out)


if __name__ == "__main__":
    main()
