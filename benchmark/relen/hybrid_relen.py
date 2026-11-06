"""Longest relator on each hybrid solution, measured on its AC path: the stored certificate (S-moves and Nielsen
maps) is rewritten as elementary AC moves on the original presentation (``elementary``), replayed with
``acx.verify.replay`` on freely reduced words, and the longest relator over every state is taken (``max_rel``; ``max_rel_cyclic`` after cyclic
reduction of each relator, the measure the S-move searches use; ``max_rel_search`` over the hybrid's own search states, before the
rewrite).

    python benchmark/relen/hybrid_relen.py results/relen_ms640_hybrid/paths.jsonl results/relen/ms640_hybrid.jsonl
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from acx.data import parse_presentation  # noqa: E402
from acx.verify.pack import unpack  # noqa: E402
from acx.verify.replay import replay  # noqa: E402
from acx.core.words import canonical_rels, reduce  # noqa: E402
from acx.core.moves import Move  # noqa: E402
from acx.hybrid.steps import aut_child, move_child  # noqa: E402


def search_states_max(pres, steps):
    """Longest relator over the hybrid's own states (the canonical pair after each S-move or Nielsen map; at a
    higher rank, the stored words)."""
    cur = canonical_rels(tuple(reduce(r) for r in pres.rels))
    best = max(map(len, cur))
    for st in steps:
        if isinstance(st, dict) and "aut" in st:
            cur = aut_child(cur, st["aut"])
        elif isinstance(st, dict):
            after = [tuple(w) for w in st["after"]]
            best = max(best, max(map(len, after), default=0))
            if len(after) == 2:
                cur = canonical_rels(tuple(after))
            continue
        else:
            cur = move_child(cur, Move(*st))
        best = max(best, max(map(len, cur)))
    return best


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(dst, "w") as f:
        for line in open(src):
            r = json.loads(line)
            if not r["solved"]:
                f.write(json.dumps(dict(id=r["id"], solved=False)) + "\n")
                continue
            p = parse_presentation(r["pres"])
            states = replay(p, unpack(r["elementary"]), cyclic=False, normalize=False)
            f.write(json.dumps(dict(id=r["id"], solved=True, units=r["cost"], steps=len(r["steps"]),
                                    elem_moves=len(r["elementary"]), start_max_rel=max(map(len, p.rels)),
                                    max_rel=max(max(map(len, s.rels)) for s in states),
                                    max_total=max(sum(map(len, s.rels)) for s in states),
                                    max_rel_cyclic=max(len(reduce(w)) for s in states for w in s.rels),
                                    max_rel_search=search_states_max(p, r["steps"]))) + "\n")


if __name__ == "__main__":
    main()
