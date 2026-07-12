"""Turn a sweep artifact into a per-class proof book: `certificates.json` + `PROOFS.md`.

The sweep records *why* it merged two presentations, but in the search's own idiom (root tables,
path steps keyed by internal state ids). This flattens that into one self-contained derivation per
class, so a reader -- or ``verify_proofs.py``, which shares no inference with the search -- can
audit any class without the sweep, the union-find, or Whitehead's algorithm.

The 135 merges form a **spanning forest** over the 262 sources (262 - 126 classes - 1 for TRIVIAL,
alone = 135 edges), so the merges inside a class are already a tree: every member is joined to
every other by a unique chain of edges, and no cycle has to be reconciled.

Two kinds of edge, and the distinction is the whole point
--------------------------------------------------------
``cv``  **Change of variables only.** One substitution psi in Aut(F2) with

            canon(psi(A)) == canon(B)

        i.e. *B is literally A with new words substituted for the generators*. No AC move is
        used. This is the strongest and cleanest kind, and it is 93 of the 135.

        The sweep stores two substitutions (each root to a shared Aut-minimal form). The single
        psi = phi_B^-1 . phi_A is recovered here via ``autinv`` and shipped, because "substitute
        this and you get that" is the statement a reader can check by hand.

``ac``  **AC moves were needed.** Both roots are driven, by Definition 2.1 moves, to a common
        Aut-class. Each step is (AC move, change of variables) and every intermediate state is
        recorded. What this proves is that A and B are the **same problem** -- A is AC-trivial
        <=> B is -- and *not* that an AC path joins them, because a change of variables is
        applied along the way.

        A refinement, flagged ``pure_ac_path``: on 6 of the 42, every step's change of variables
        is the identity, so the path is Definition 2.1 moves and nothing else. Those do give an
        AC path -- but between A and psi(B), not between A and B, because the two roots still had
        to be carried to their Aut-minimal forms first. Stated that way and no stronger.
        ``endpoint_subst`` is that psi. It is emitted for reading, and checked only for *being an
        automorphism*: ``canon(psi(B)) != canon(A)`` on these edges, necessarily -- the two sides
        differ by the AC moves. Asserting that equality would fail a correct certificate.

Usage:  make_proof_book.py [sweep.json]
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.equivalence_classes.acmoves import canon  # noqa: E402
from experiments.equivalence_classes.autinv import compose, invert  # noqa: E402
from experiments.equivalence_classes.words import abelian_det, apply_hom  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "results", "equivalence_classes")
ID = {"x": "x", "y": "y"}


def hom_str(phi):
    return f"x -> {phi['x']}, y -> {phi['y']}"


def move_str(move):
    """Definition 2.1: r_i <- rot_{k1}(r_i) . rot_{k2}(r_j^jsign). The move inverts the OTHER."""
    t, j, k1, k2 = move
    o = 3 - t
    return f"r{t} <- rot_{k1}(r{t}) . rot_{k2}(r{o}{'^-1' if j == -1 else ''})"


def replay(pair, move):
    t, j, k1, k2 = move
    from experiments.equivalence_classes.words import inv, rot
    r1, r2 = pair
    ri, rj = (r1, r2) if t == 1 else (r2, r1)
    oj = rj if j == 1 else inv(rj)
    piece = rot(ri, k1) + rot(oj, k2)
    return canon(piece, r2) if t == 1 else canon(r1, piece)


def build_side(name, raw, root, path):
    """One root's route to the meeting state, every intermediate state made explicit."""
    start = canon(*raw)
    phi0 = root["phi"]
    rep = tuple(root["aut_rep"])
    steps, cur = [], rep
    for mv, phi, claimed in path:
        mv = tuple(mv)
        after = replay(cur, mv)
        nxt = canon(apply_hom(after[0], phi), apply_hom(after[1], phi))
        assert nxt == tuple(claimed), f"{name}: regenerated {nxt}, sweep recorded {claimed}"
        steps.append({"move": list(mv), "move_desc": move_str(mv),
                      "after_move": list(after), "phi": phi, "state": list(nxt)})
        cur = nxt
    return {"name": name, "start": list(start), "phi0": phi0,
            "aut_rep": list(rep), "steps": steps, "end": list(cur)}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUT, "sweep_seam_28_250.json")
    data = json.load(open(src))
    roots = data["roots"]

    rows = list(csv.DictReader(open(
        os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv"))))
    raw = {r["name"]: (r["r1"], r["r2"]) for r in rows}
    pid = {r["name"]: i for i, r in enumerate(rows)}
    raw["TRIVIAL"] = ("x", "y")

    # the merges are a spanning forest: group them by the class they live in
    parent = {n: n for n in roots}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for m in data["merges"]:
        ra, rb = find(m["a"]), find(m["b"])
        assert ra != rb, f"merge {m['a']}={m['b']} closes a cycle -- not a spanning forest"
        parent[rb] = ra

    edges_of, members_of = {}, {}
    for m in data["merges"]:
        edges_of.setdefault(find(m["a"]), []).append(m)
    for n in roots:
        members_of.setdefault(find(n), []).append(n)

    classes, n_cv, n_ac, n_pure = [], 0, 0, 0
    for r, mem in members_of.items():
        mem = sorted((n for n in mem if n in pid), key=lambda n: pid[n])
        if not mem:                       # the TRIVIAL-only component
            continue
        out_edges = []
        for m in edges_of.get(r, []):
            a, b = m["a"], m["b"]
            sa = build_side(a, raw[a], roots[a], m["path_a"])
            sb = build_side(b, raw[b], roots[b], m["path_b"])
            assert sa["end"] == sb["end"] == list(m["at"]), f"{a}={b}: sides do not meet"

            e = {"a": {"pres_id": pid[a], "name": a},
                 "b": {"pres_id": pid[b], "name": b},
                 "side_a": sa, "side_b": sb, "meet": list(m["at"])}

            if m["kind"] == "aut":
                # one substitution carries A onto B outright.  psi = phi_B^-1 . phi_A
                psi = compose(invert(roots[b]["phi"]), roots[a]["phi"])
                got = canon(apply_hom(sa["start"][0], psi), apply_hom(sa["start"][1], psi))
                assert got == tuple(sb["start"]), f"{a}={b}: psi lands on {got}, want {sb['start']}"
                e["kind"] = "cv"
                e["subst"] = psi
                e["claim"] = (f"canon(psi({a})) == canon({b}) with psi: {hom_str(psi)} -- "
                              f"a change of variables, no AC move")
                n_cv += 1
            else:
                pure = all(s["phi"] == ID for s in sa["steps"] + sb["steps"])
                # psi relates the ENDS of the AC path, so canon(psi(B)) != canon(A) here: the two
                # sides differ by exactly the AC moves. Emitted to read, never asserted equal.
                psi = compose(invert(roots[a]["phi"]), roots[b]["phi"])
                e["kind"] = "ac"
                e["pure_ac_path"] = pure
                e["endpoint_subst"] = psi
                e["n_moves_a"] = len(sa["steps"])
                e["n_moves_b"] = len(sb["steps"])
                e["claim"] = (
                    f"{a} ~AC psi({b}) with psi: {hom_str(psi)} -- an AC path, "
                    f"{len(sa['steps'])} + {len(sb['steps'])} Definition 2.1 moves"
                    if pure else
                    f"{a} and {b} are the same problem (ACA): {len(sa['steps'])} + "
                    f"{len(sb['steps'])} AC moves, with a change of variables between them")
                n_ac += 1
                n_pure += pure
            out_edges.append(e)

        dets = {abs(abelian_det(*raw[n])) for n in mem}
        assert len(dets) == 1, f"class {mem[:3]}: |det| not constant: {dets}"
        classes.append({"size": len(mem), "abelian_det": dets.pop(),
                        "members": [{"pres_id": pid[n], "name": n,
                                     "r1": raw[n][0], "r2": raw[n][1]} for n in mem],
                        "edges": out_edges})

    classes.sort(key=lambda c: (-c["size"], c["members"][0]["pres_id"]))
    for i, c in enumerate(classes, 1):
        c["class_id"] = i

    cert = {
        "generated_from": os.path.relpath(src, ROOT),
        "config": data["config"],
        "summary": {"presentations": sum(c["size"] for c in classes),
                    "classes": len(classes), "edges": n_cv + n_ac,
                    "cv_edges": n_cv, "ac_edges": n_ac, "ac_pure_path_edges": n_pure,
                    "singletons": sum(1 for c in classes if c["size"] == 1),
                    "largest_class": max(c["size"] for c in classes)},
        "classes": classes,
    }
    p = os.path.join(OUT, "certificates.json")
    json.dump(cert, open(p, "w"), indent=1)
    print(f"wrote {p}")
    print(f"  {cert['summary']}")

    p = os.path.join(OUT, "PROOFS.md")
    open(p, "w").write(render(cert))
    print(f"wrote {p}")


# --------------------------------------------------------------------------- markdown
def render(cert):
    s = cert["summary"]
    L = [
        "# Proof book — how the 261 unsolved Miller–Schupp reps collapse to "
        f"{s['classes']} classes",
        "",
        f"Generated from `{cert['generated_from']}` by `experiments/equivalence_classes/"
        "make_proof_book.py`.",
        "",
        "**Re-check every line of this file:**",
        "",
        "```bash",
        ".venv/bin/python3 experiments/equivalence_classes/verify_proofs.py",
        "```",
        "",
        "That reads `certificates.json` and the raw presentation CSV and *nothing else* — it "
        "replays every AC move by string substitution, re-proves every change of variables is an "
        "automorphism by Nielsen reduction, and rebuilds the partition from the verified edges "
        "alone. It shares no inference with the search that produced them.",
        "",
        "## What is proved",
        "",
        f"| | count |",
        "|---|---|",
        f"| presentations | {s['presentations']} |",
        f"| **distinct problems (classes)** | **{s['classes']}** |",
        f"| edges proving them equivalent | {s['edges']} |",
        f"| — change of variables only (`cv`) | {s['cv_edges']} |",
        f"| — needed AC moves (`ac`) | {s['ac_edges']} |",
        f"| singleton classes | {s['singletons']} |",
        f"| largest class | {s['largest_class']} |",
        "",
        "Every class below is a tree of edges: each member is joined to the rest by a chain of "
        "the edges listed under it. Two kinds, and they prove different things.",
        "",
        "### `cv` — change of variables only",
        "",
        "A single substitution `psi` in `Aut(F₂)` with `canon(psi(A)) == canon(B)`. **B is A with "
        "new words substituted for the generators**, full stop — no AC move is involved. Check it "
        "by hand: substitute and compare canonical forms.",
        "",
        "### `ac` — AC moves were needed",
        "",
        "Both presentations are driven by Definition 2.1 moves",
        "",
        "```",
        "r_i  <-  rot_k1(r_i) . rot_k2(r_j^±1)          (the move inverts the OTHER relator)",
        "```",
        "",
        "to a common `Aut(F₂)`-class. This proves **A and B are the same problem** — A is "
        "AC-trivial ⟺ B is. It does **not** exhibit an AC path from A to B, because a change of "
        "variables is applied between the moves.",
        "",
        f"On **{s['ac_pure_path_edges']} of the {s['ac_edges']}** the change of variables at every "
        "step is the identity, so the path is Definition 2.1 moves and nothing else. Those are "
        "flagged `pure AC path` and do give an AC path — from `A` to `psi(B)`, where `psi` is the "
        "relabelling that carried the two roots to their `Aut`-minimal forms. **Not** from A to B; "
        "no edge here proves that.",
        "",
        "## Index",
        "",
        "| class | size | members |",
        "|---|---|---|",
    ]
    for c in cert["classes"]:
        mem = " ".join(f"{m['pres_id']}({m['name']})" for m in c["members"])
        L.append(f"| [{c['class_id']:03d}](#class-{c['class_id']:03d}) | {c['size']} | {mem} |")
    L.append("")
    L.append("---")
    L.append("")
    for c in cert["classes"]:
        L += render_class(c)
    return "\n".join(L) + "\n"


def render_side(side, tag):
    out = [f"  {tag} — {side['name']}"]
    w = 34
    out.append(f"    {'P':<{w}} = ({side['start'][0]}, {side['start'][1]})")
    out.append(f"    {hom_str(side['phi0']):<{w}} = ({side['aut_rep'][0]}, {side['aut_rep'][1]})"
               "   [to the Aut-minimal form]")
    for i, st in enumerate(side["steps"], 1):
        out.append(f"    {st['move_desc']:<{w}} = ({st['after_move'][0]}, {st['after_move'][1]})"
                   "   [AC move]")
        if st["phi"] != ID:
            out.append(f"    {hom_str(st['phi']):<{w}} = ({st['state'][0]}, {st['state'][1]})"
                       "   [change of variables]")
    return out


def render_class(c):
    L = [f"## Class {c['class_id']:03d}", "",
         f"**{c['size']} presentation{'s' if c['size'] > 1 else ''}**, "
         f"`|det| = {c['abelian_det']}`", "",
         "| pres_id | name | r1 | r2 |", "|---|---|---|---|"]
    for m in c["members"]:
        L.append(f"| {m['pres_id']} | {m['name']} | `{m['r1']}` | `{m['r2']}` |")
    L.append("")
    if not c["edges"]:
        L += ["No other presentation of the 261 is known to be equivalent to it: neither a change "
              "of variables nor any AC move the sweep reached connects it to another class.", "",
              "---", ""]
        return L
    L.append(f"### Why they are the same problem — {len(c['edges'])} edge"
             f"{'s' if len(c['edges']) > 1 else ''}")
    L.append("")
    for e in c["edges"]:
        a, b = e["a"], e["b"]
        head = f"**{a['pres_id']} ({a['name']})  ≡  {b['pres_id']} ({b['name']})**"
        if e["kind"] == "cv":
            L += [f"{head} — *change of variables only*", "",
                  f"Substitute `{hom_str(e['subst'])}` into `{a['name']}`:", "", "```"]
            sa, sb = e["side_a"], e["side_b"]
            L += [f"    ({sa['start'][0]}, {sa['start'][1]})",
                  f"      ==>  ({sb['start'][0]}, {sb['start'][1]})   "
                  f"= the canonical form of {b['name']}   [MATCH]",
                  "```", ""]
        else:
            kind = ("*pure AC path*" if e["pure_ac_path"]
                    else "*AC moves + change of variables*")
            L += [f"{head} — {kind}, {e['n_moves_a']} + {e['n_moves_b']} AC moves", "", "```"]
            L += render_side(e["side_a"], "left ")
            L += render_side(e["side_b"], "right")
            L += [f"    both meet at ({e['meet'][0]}, {e['meet'][1]})", "```", ""]
            if e["pure_ac_path"]:
                L += [f"Every step is an AC move — no change of variables inside the path. So "
                      f"`{a['name']} ~AC psi({b['name']})` with `psi: {hom_str(e['endpoint_subst'])}`"
                      f" (the relabelling to the Aut-minimal forms). This is an AC path to a "
                      f"*relabelled* `{b['name']}`, not to `{b['name']}` itself.", ""]
    L += ["---", ""]
    return L


if __name__ == "__main__":
    main()
