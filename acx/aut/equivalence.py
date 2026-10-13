"""Checker for ``data/equivalence_classes/certificates.json``: the 124 U124 classes and the edges joining their members.

An edge joins two presentations by chains ``start --phi0--> aut_rep --(S-move, then phi)*--> end`` meeting at one
canonical presentation (a ``cv`` edge has no S-moves, an ``ac`` edge has Definition 2.1 S-moves between
automorphisms); every ``phi`` must be an automorphism (``is_automorphism``: Whitehead descent reaches a basis).
"""
import json

from ..core.moves import apply_raw, from_legacy, seam_cancels
from ..core.words import Presentation, parse, reduce
from .autos import AUTOS, DESCENT, apply


def is_automorphism(img):
    """``x -> img[0], y -> img[1]`` is an automorphism: Whitehead descent on the images ends at two distinct letters."""
    cur = tuple(reduce(w, cyclic=False) for w in img)
    while True:
        best = min((tuple(apply(w, AUTOS[k]) for w in cur) for k in DESCENT), key=lambda t: sum(map(len, t)))
        if sum(map(len, best)) >= sum(map(len, cur)):
            return all(len(w) == 1 for w in cur) and abs(cur[0][0]) != abs(cur[1][0])
        cur = best


def canon(rels):
    """Reduced canonical form of relators given as strings or words."""
    return Presentation(2, tuple(parse(r) if isinstance(r, str) else r for r in rels)).reduced().canonical()


def _image(rels, phi):
    """``rels`` under the automorphism ``phi`` (``{"x": word, "y": word}``); raises if ``phi`` is not one."""
    img = (parse(phi["x"]), parse(phi["y"]))
    if not is_automorphism(img):
        raise ValueError(f"{phi} is not an automorphism of F2")
    return tuple(apply(parse(r), img) for r in rels)


def check_side(side):
    """The canonical end of one side's chain; raises ``ValueError`` on any step that does not hold."""
    if canon(_image(side["start"], side["phi0"])) != canon(side["aut_rep"]):
        raise ValueError(f"{side['name']}: phi0(start) is not aut_rep")
    cur = side["aut_rep"]
    for st in side["steps"]:
        rels, m = tuple(map(parse, cur)), from_legacy(*st["move"])
        if not seam_cancels(rels, m):
            raise ValueError(f"{side['name']}: move {st['move']} is not a Definition 2.1 move of {cur}")
        if canon(apply_raw(rels, m)) != canon(st["after_move"]):
            raise ValueError(f"{side['name']}: move {st['move']} does not give {st['after_move']}")
        if canon(_image(st["after_move"], st["phi"])) != canon(st["state"]):
            raise ValueError(f"{side['name']}: phi(after_move) is not the next state")
        cur = st["state"]
    if canon(cur) != canon(side["end"]):
        raise ValueError(f"{side['name']}: the chain does not end at {side['end']}")
    return canon(cur)


IDENTITY = {"x": "x", "y": "y"}


def check_edge(edge, members):
    """Check one edge against its class's ``members`` (name -> relators); return ``True`` if it is a pure-AC edge."""
    a, b = edge["side_a"], edge["side_b"]
    if (tuple(a["start"]), tuple(b["start"])) != (members[edge["a"]["name"]], members[edge["b"]["name"]]):
        raise ValueError(f"edge {edge['claim']!r} does not start at its members")
    if not check_side(a) == check_side(b) == canon(edge["meet"]):
        raise ValueError(f"edge {edge['claim']!r}: the sides do not meet")
    if edge["kind"] == "cv" and canon(_image(a["start"], edge["subst"])) != canon(b["start"]):
        raise ValueError(f"edge {edge['claim']!r}: subst(a) is not b")
    steps = [st for side in (a, b) for st in side["steps"]]
    pure = edge["kind"] == "ac" and all(st["phi"] == IDENTITY for st in steps)
    if pure != bool(edge.get("pure_ac_path")):
        raise ValueError(f"edge {edge['claim']!r}: pure_ac_path is {edge.get('pure_ac_path')}, the steps say {pure}")
    return pure


def check_class(cls, counts):
    """Check one class: its member count, every edge, and that the edges join all its members; update ``counts``."""
    members = {m["name"]: (m["r1"], m["r2"]) for m in cls["members"]}
    if len(members) != cls["size"]:
        raise ValueError(f"class {cls['class_id']} lists {len(members)} members, not {cls['size']}")
    counts["presentations"] += len(members)
    parent = {name: name for name in members}              # union-find over the member names

    def find(name):
        while parent[name] != name:
            name = parent[name]
        return name

    for edge in cls["edges"]:
        counts["pure_ac"] += check_edge(edge, members)
        counts[edge["kind"]] += 1
        parent[find(edge["a"]["name"])] = find(edge["b"]["name"])
    if len({find(name) for name in members}) != 1:
        raise ValueError(f"class {cls['class_id']}: its edges do not connect its {len(members)} members")


def check(path):
    """Check every edge of the file and that each class's edges join all its members into one component.

    Returns counts (classes, presentations, edges by kind, ``pure_ac``: ``ac`` edges whose S-moves are never
    interleaved with a non-identity automorphism, derived from the steps and required to match the file's flag).
    """
    with open(path) as f:
        classes = json.load(f)["classes"]
    counts = dict(classes=len(classes), presentations=0, cv=0, ac=0, pure_ac=0)
    for cls in classes:
        check_class(cls, counts)
    return counts
