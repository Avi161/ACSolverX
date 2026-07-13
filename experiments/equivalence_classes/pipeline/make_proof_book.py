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

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.acmoves import canon  # noqa: E402
from experiments.equivalence_classes.lib.autinv import compose, invert  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    abelian_det, apply_hom, cyc_reduce, free_reduce, inv, rot,
)

OUT = os.path.join(ROOT, "results", "equivalence_classes")
ID = {"x": "x", "y": "y"}


def hom_str(phi):
    return f"x -> {phi['x']}, y -> {phi['y']}"


def move_str(move):
    """Definition 2.1: r_i <- rot_{k1}(r_i) . rot_{k2}(r_j^jsign). The move inverts the OTHER."""
    t, j, k1, k2 = move
    o = 3 - t
    return f"r{t} <- rot_{k1}(r{t}) . rot_{k2}(r{o}{'^-1' if j == -1 else ''})"


def norm_witness(raw, target):
    """**How** the raw pair normalises to the canonical `target` -- the step a reader cannot see.

    Substituting into a relator almost never yields the target string *literally*: canonicalisation
    then freely reduces it, may invert it, rotates it to its lex-least form, and may swap the two
    relators. Printing only the canonical result makes the claim unverifiable by hand -- the reader
    is left staring at two strings that plainly differ. So spell the normalisation out:

        for each relator of the target: which raw relator it came from, whether it was inverted,
        and by how much it was rotated.

    Each of the three is free -- none changes the presented group or the AC-triviality:
      * inverting:  a relator is a relation `r = 1`, and `r^-1 = 1` says the same thing;
      * rotating:   a cyclic rotation is a conjugate -- if `r = uv` then `vu = u^-1(uv)u`;
      * swapping:   which relator you write first is not data.
    All three are AC moves in their own right. This is exactly what `canonical_pair_nj` quotients.

    Raises if no witness exists -- which would mean the two pairs are simply not equal.
    """
    red = [cyc_reduce(w) for w in raw]
    for perm in ((0, 1), (1, 0)):
        out, ok = [], True
        for j in (0, 1):
            i = perm[j]
            w, t = red[i], target[j]
            hit = None
            if len(w) == len(t):
                for inverted in (False, True):
                    u = inv(w) if inverted else w
                    for k in range(len(u) or 1):
                        if rot(u, k) == t:
                            hit = (inverted, k)
                            break
                    if hit:
                        break
            if hit is None:
                ok = False
                break
            out.append({"to_relator": j + 1, "from_relator": i + 1, "word": raw[i],
                        "reduced": w, "inverted": hit[0], "rotate": hit[1], "result": t})
        if ok:
            return out
    raise AssertionError(f"{raw} does not normalise to {target}")


def move_detail(pair, move):
    """The two rotated pieces and their product, before any canonicalisation -- so the reader can
    concatenate the two strings themselves and see where the new relator came from."""
    t, j, k1, k2 = move
    r1, r2 = pair
    ri, rj = (r1, r2) if t == 1 else (r2, r1)
    oj = rj if j == 1 else inv(rj)
    a, b = rot(ri, k1), rot(oj, k2)
    prod = a + b
    kept = r2 if t == 1 else r1
    raw = (prod, kept) if t == 1 else (kept, prod)
    return {"piece_i": a, "piece_j": b, "product": prod,
            "reduced": free_reduce(prod), "kept": kept, "raw_pair": list(raw)}


def replay(pair, move):
    t, j, k1, k2 = move
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
    # the initial change of variables, with the normalisation spelled out
    sub0 = [free_reduce(apply_hom(w, phi0)) for w in start]
    assert canon(*sub0) == rep, f"{name}: phi0 does not land on the recorded Aut-minimal form"
    phi0_witness = norm_witness(sub0, rep)

    steps, cur = [], rep
    for mv, phi, claimed in path:
        mv = tuple(mv)
        det = move_detail(cur, mv)
        after = replay(cur, mv)
        assert canon(*det["raw_pair"]) == after, f"{name}: move_detail disagrees with the replay"
        sub = [free_reduce(apply_hom(w, phi)) for w in after]
        nxt = canon(*sub)
        assert nxt == tuple(claimed), f"{name}: regenerated {nxt}, sweep recorded {claimed}"
        steps.append({
            "move": list(mv), "move_desc": move_str(mv), "detail": det,
            "move_witness": norm_witness(det["raw_pair"], after),
            "after_move": list(after), "phi": phi,
            "phi_substituted": sub,
            "phi_witness": norm_witness(sub, nxt) if phi != ID else None,
            "state": list(nxt)})
        cur = nxt
    return {"name": name, "start": list(start), "phi0": phi0,
            "phi0_substituted": sub0, "phi0_witness": phi0_witness,
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
                sub = [free_reduce(apply_hom(w, psi)) for w in sa["start"]]
                got = canon(*sub)
                assert got == tuple(sb["start"]), f"{a}={b}: psi lands on {got}, want {sb['start']}"
                e["kind"] = "cv"
                e["subst"] = psi
                e["subst_substituted"] = sub
                # the whole point: substituting does NOT give B's strings literally. Say how it does.
                e["subst_witness"] = norm_witness(sub, tuple(sb["start"]))
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
                    # a single-letter image makes the substitution a plain case swap; a longer one
                    # does not (the inverse letter maps to a REVERSED word), so the reader must be
                    # told which kind they are looking at.
                    "cv_single_letter": sum(1 for c in classes for e in c["edges"]
                                            if e["kind"] == "cv"
                                            and len(e["subst"]["x"]) == 1
                                            and len(e["subst"]["y"]) == 1),
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
        ".venv/bin/python3 experiments/equivalence_classes/verify/verify_proofs.py",
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
        "---",
        "",
        "## How to read a proof, by hand, with no computer",
        "",
        "**Read this section once and every derivation below becomes checkable with a pencil.**",
        "",
        "### The alphabet",
        "",
        "A relator is a word in two generators. `x` and `y` are the generators; **a capital letter "
        "is an inverse** — `X` = `x⁻¹`, `Y` = `y⁻¹`. So `YYYxxyyX` means `y⁻¹y⁻¹y⁻¹xxyy x⁻¹`.",
        "",
        "### What a substitution means — and what happens to the capitals",
        "",
        "A substitution `psi: x -> …, y -> …` lists only where the **generators** go. It is a "
        "*homomorphism*, so the capitals are not free to choose — they follow automatically. Since "
        "`X` is just notation for `x⁻¹`:",
        "",
        "```",
        "psi(X) = psi(x^-1) = psi(x)^-1 = reverse psi(x), then swap the case of every letter",
        "```",
        "",
        "So **yes, `y -> Y` also means `Y -> y`** — but only because the image is a single letter, "
        "where inverting is just a case swap. When the image is longer the inverse is a *reversed* "
        "word, and reading it as a case swap gives the wrong answer:",
        "",
        "| `psi` says | so the capital must go | because |",
        "|---|---|---|",
        "| `y -> Y` | `Y -> y` | `(y⁻¹)⁻¹ = y` — here it *is* just a case swap |",
        "| `x -> xY` | `X -> yX` | reverse `xY` → `Yx`, swap case → `yX` |",
        "| `x -> xy` | `X -> YX` | reverse `xy` → `yx`, swap case → `YX` |",
        "| `x -> yx` | `X -> XY` | reverse `yx` → `xy`, swap case → `XY` |",
        "",
        f"{s['cv_single_letter']} of the {s['cv_edges']} change-of-variables edges have "
        "single-letter images, where substituting really is just swapping cases. "
        f"**{s['cv_edges'] - s['cv_single_letter']} do not** — for those, reverse first.",
        "",
        "### The one thing that trips everyone up",
        "",
        "Every presentation below is printed in **canonical form**, and canonicalisation quietly "
        "rewrites the relators. So when you substitute `y → Y` into a relator, **the string you "
        "get is almost never the target string you see printed** — you must still invert it and "
        "rotate it. That is not a gap in the proof; it is bookkeeping. But it is invisible unless "
        "it is written down, so **every derivation below writes it down**, step by step.",
        "",
        "Canonical form does exactly three things, and each is free:",
        "",
        "| | what it does | why it changes nothing |",
        "|---|---|---|",
        "| **freely reduce** | delete any `xX`, `Xx`, `yY`, `Yy` | `x x⁻¹` is the empty word |",
        "| **invert** a relator | `r ↦ r⁻¹` (reverse the word, swap every letter's case) | a relator is a *relation* `r = 1`; `r⁻¹ = 1` says the same thing. It is also one of the four AC moves. |",
        "| **rotate** a relator | move letters from the end to the front | a rotation is a conjugate: if `r = uv` then the rotation `vu = u⁻¹(uv)u = u⁻¹ r u`. Conjugating a relator is an AC move, and it does not change the group. |",
        "",
        "(It also sorts the two relators, since which one you write first is not data.) Among all "
        "the rotations of `r` and of `r⁻¹`, canonical form keeps the alphabetically least — a "
        "fingerprint, so two presentations that differ only by this bookkeeping get the same "
        "string.",
        "",
        "So a derivation line like",
        "",
        "```",
        "  r1 = YYYxxyyX",
        "       substitute y -> Y   ->  yyyxxYYX",
        "       invert             ->  xyyXXYYY",
        "       rotate by 3        ->  YYYxyyXX     = r1 of 19_50   [MATCH]",
        "```",
        "",
        "is checked with a pencil: swap the case of every `y`; then reverse the word and swap every "
        "letter's case; then move the last 3 letters to the front. The result is the printed target. "
        "**The substitution is the only mathematical content — the invert and the rotate are "
        "notation.**",
        "",
        "### The two kinds of edge",
        "",
        "#### `cv` — change of variables only",
        "",
        "A single substitution `psi` with `canon(psi(A)) == canon(B)`. **B is A with new words "
        "substituted for the generators** — no AC move at all. Every one is derived below, relator "
        "by relator, in the form just shown.",
        "",
        "#### `ac` — AC moves were needed",
        "",
        "Both presentations are driven to a common form by **Definition 2.1 moves**:",
        "",
        "```",
        "r_i  <-  rot_k1(r_i) . rot_k2(r_j^±1)          (note: the move inverts the OTHER relator)",
        "```",
        "",
        "In words: rotate relator `i` by `k1`, rotate the *other* relator by `k2` (inverting it "
        "first if the exponent is `-1`), and **concatenate them** — the product replaces relator "
        "`i`. The other relator is untouched. Every move below shows the two rotated pieces and "
        "their product, so you can concatenate the strings yourself.",
        "",
        "This proves **A and B are the same problem** — A is AC-trivial ⟺ B is. It does **not** "
        "exhibit an AC path from A to B, because a change of variables is applied between the moves.",
        "",
        f"On **{s['ac_pure_path_edges']} of the {s['ac_edges']}** the change of variables at every "
        "step is the identity, so the path is Definition 2.1 moves and nothing else. Those are "
        "flagged `pure AC path` and do give an AC path — from `A` to `psi(B)`, where `psi` is the "
        "relabelling that carried the two roots to their `Aut`-minimal forms. **Not** from A to B; "
        "no edge here proves that.",
        "",
        "---",
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


def render_norm(origin, subst, witness, phi, target_name, pad="  "):
    """The pencil-checkable core, one relator at a time:

        original --substitute--> [reduce] --> [invert] --> [rotate] --> the printed target

    Every line is a single mechanical operation a reader can do by hand. Lines that would be
    no-ops (no reduction needed, no inversion, rotate by 0) are omitted rather than printed as
    identities, so what remains is exactly the work.
    """
    out = []
    for wit in witness:
        i = wit["from_relator"] - 1
        src, sub = origin[i], subst[i]
        out.append(f"{pad}r{wit['from_relator']} = {src}")
        if phi is not None:
            out.append(f"{pad}     substitute      ->  {sub}")
        cur = wit["reduced"]
        if cur != sub:
            out.append(f"{pad}     reduce          ->  {cur}")
        if wit["inverted"]:
            cur = inv(cur)
            out.append(f"{pad}     invert          ->  {cur}")
        if wit["rotate"]:
            cur = rot(cur, wit["rotate"])
            out.append(f"{pad}     rotate by {wit['rotate']:<2}    ->  {cur}")
        where = f"r{wit['to_relator']}" + (f" of {target_name}" if target_name else "")
        out.append(f"{pad}                         = {where}"
                   + ("   [MATCH]" if target_name else ""))
    return out


def render_move(st):
    """One Definition 2.1 move: the two rotated pieces, their product, and the normalisation.

    The reader can do all of it by hand -- rotate two strings, concatenate them, cancel adjacent
    inverse pairs, then invert/rotate to the printed form.
    """
    t = st["move"][0]
    d = st["detail"]
    prod = next(w for w in st["move_witness"] if w["from_relator"] == t)
    kept = next(w for w in st["move_witness"] if w["from_relator"] != t)
    k1, k2 = st["move"][2], st["move"][3]
    sign = "^-1" if st["move"][1] == -1 else ""

    w = 17
    out = [f"    AC move:  {st['move_desc']}",
           f"        {f'rot_{k1}(r{t})':<{w}}=  {d['piece_i']}",
           f"        {f'rot_{k2}(r{3 - t}{sign})':<{w}}=  {d['piece_j']}",
           f"        {'concatenate':<{w}}=  {d['product']}"]
    if d["reduced"] != d["product"]:
        out.append(f"        {'cancel inverses':<{w}}=  {d['reduced']}")
    cur = prod["reduced"]
    if cur != d["reduced"]:
        out.append(f"        {'reduce cyclically':<{w}}=  {cur}")
    if prod["inverted"]:
        cur = inv(cur)
        out.append(f"        {'invert':<{w}}=  {cur}")
    if prod["rotate"]:
        cur = rot(cur, prod["rotate"])
        out.append(f"        {'rotate by ' + str(prod['rotate']):<{w}}=  {cur}")
    out.append(f"                            ^ the new r{prod['to_relator']}")
    note = f"        r{3 - t} is untouched by the move"
    if kept["inverted"] or kept["rotate"]:
        note += f" (renormalised to r{kept['to_relator']} = {kept['result']})"
    elif kept["to_relator"] != kept["from_relator"]:
        note += f" (it becomes r{kept['to_relator']}: the two relators sort into the other order)"
    out.append(note)
    return out


def render_side(side, tag):
    """One root's route to the meeting state, with every normalisation spelled out."""
    out = [f"  {tag} — {side['name']}", f"    start: ({side['start'][0]}, {side['start'][1]})"]
    if side["phi0"] != ID:
        out.append(f"    change of variables: {hom_str(side['phi0'])}")
        out += render_norm(side["start"], side["phi0_substituted"], side["phi0_witness"],
                           side["phi0"], None, pad="      ")
    out.append(f"    => ({side['aut_rep'][0]}, {side['aut_rep'][1]})"
               f"{'   [already Aut-minimal]' if side['phi0'] == ID else ''}")
    for st in side["steps"]:
        out += [""] + render_move(st)
        out.append(f"    => ({st['after_move'][0]}, {st['after_move'][1]})")
        if st["phi"] != ID:
            out.append(f"    change of variables: {hom_str(st['phi'])}")
            out += render_norm(st["after_move"], st["phi_substituted"], st["phi_witness"],
                               st["phi"], None, pad="      ")
            out.append(f"    => ({st['state'][0]}, {st['state'][1]})")
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
            sa, sb = e["side_a"], e["side_b"]
            L += [f"{head} — *change of variables only*", "",
                  f"Substitute `{hom_str(e['subst'])}` into **{a['name']}** "
                  f"(`{sa['start'][0]}`, `{sa['start'][1]}`), then normalise:", "", "```"]
            L += render_norm(sa["start"], e["subst_substituted"], e["subst_witness"],
                             e["subst"], b["name"], pad="  ")
            L += ["```", "",
                  f"which is exactly **{b['name']}** = (`{sb['start'][0]}`, `{sb['start'][1]}`). "
                  f"No AC move was used.", ""]
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
