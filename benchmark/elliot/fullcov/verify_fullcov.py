"""Independent replay of every solved path of a full-CoV results folder.

    python -m benchmark.elliot.fullcov.verify_fullcov <results folder> [<out.json>]

Per row: the path starts at the start's canonical form and ends at a pair of one-letter relators, and the move count
is ``path_length``. Per step, in code that does not call the search:

- S-move: the new pair keeps one relator and replaces the other by a cyclically reduced product of a rotation of it
  and a rotation of the kept relator or its inverse, cancelling at the seam (own loop, compared up to rotation,
  inversion and order with ``acx.core.words.canonical_rels``);
- auto CoV: the named map x -> x y^k or y -> y x^k applied to both relators gives the new pair;
- full CoV: ``acx.cov.apply_steps`` redoes define / substitute / eliminate from the logged data on the previous pair
  (it checks every hypothesis of Lemma 11 and |det| = 1) and must give the new pair. The step is called an
  automorphism only if its elimination is ``t = s^a z^e s^b`` with ``e = +-1`` (so ``t -> expr`` is an automorphism
  psi of F2) and ``zeta^-1 w`` is a conjugate of the isolating relator ``R`` or of ``R^-1``, where ``z = zeta`` solves
  ``t = expr``. Then psi^-1 of the image is (the other relator with each w replaced by zeta, zeta^-1 w), which differs
  from the start by multiplying by conjugates of R: AC moves. So the row is an AC path when every CoV step passes
  this test, and otherwise a stable AC certificate. The verdict must equal the one the search logged.
"""
import json
import sys
from pathlib import Path

from acx.core.words import canonical_rels, canonical_word, inverse, parse, reduce
from acx.core.words import Presentation
from acx.cov import apply_steps

from .run_fullcov import read_jsonl

INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def cw(w):
    return canonical_word(reduce(parse(w)))


def canon(pair):
    return canonical_rels(tuple(reduce(parse(r)) for r in pair))


def rot(w, k):
    return w[k:] + w[:k]


def s_move_ok(fr, to):
    tc = canon(to)
    for i in (0, 1):
        ri, rj = fr[i], fr[1 - i]
        keep = cw(rj)
        if keep not in tc:
            continue
        target = tc[1] if keep == tc[0] else tc[0]
        for oj in (rj, "".join(INV[c] for c in reversed(rj))):
            for k1 in range(len(ri)):
                a = rot(ri, k1)
                for k2 in range(len(oj)):
                    b = rot(oj, k2)
                    if INV[a[-1]] == b[0] and canonical_word(reduce(parse(a + b))) == target:
                        return True
    return False


def auto_ok(fr, to, name):
    gen, k = name.split("_right_")
    k, other = int(k), "y" if gen == "x" else "x"
    img = gen + (other * k if k > 0 else INV[other] * -k)
    rep = {gen: img, INV[gen]: "".join(INV[c] for c in reversed(img))}
    return canon(tuple("".join(rep.get(c, c) for c in r) for r in fr)) == canon(to)


def cyclic_class(w):
    w = reduce(tuple(w))
    return min(canonical_word(w), canonical_word(inverse(w)))


def is_automorphic_step(pres, m):
    """The test of the module docstring on a logged full-CoV step from ``pres``."""
    g, i, expr = m["gen"], m["iso_index"], tuple(m["expr"])
    s = 3 - g
    zs = [k for k, a in enumerate(expr) if abs(a) == 3]
    if len(zs) != 1 or any(abs(a) not in (s, 3) for a in expr):
        return False
    pre, e, post = expr[:zs[0]], expr[zs[0]] // 3, expr[zs[0] + 1:]
    if any(abs(a) != s for a in pre + post):
        return False
    core = reduce(inverse(pre) + (g,) + inverse(post), False)       # z^e = s^-a t s^-b
    zeta = core if e == 1 else inverse(core)
    w = tuple(m["w_ints"])
    return cyclic_class(inverse(zeta) + w) == cyclic_class(pres.rels[i])


def check_row(rec):
    errs = []
    path = rec["path"]
    if canon(path[0]) != canon((rec["r1"], rec["r2"])):
        errs.append("start")
    if not all(len(r) == 1 for r in path[-1]):
        errs.append("end")
    if len(path) - 1 != rec["path_length"] or len(rec["moves"]) != rec["path_length"]:
        errs.append("length")
    covs = iter(rec.get("cov_used") or [])
    verdict_aut = True
    for k, kind in enumerate(rec["moves"]):
        fr, to = path[k], path[k + 1]
        if kind == "standard_substitution":
            if not s_move_ok(fr, to):
                errs.append(f"s-move {k}")
            continue
        m = next(covs)
        if [m["from"], m["to"]] != [fr, to]:
            errs.append(f"cov log {k}")
        if kind == "auto_cov":
            if not auto_ok(fr, to, m["automorphism"]):
                errs.append(f"auto {k}")
            continue
        pres = Presentation(2, tuple(reduce(parse(r)) for r in fr))
        w = parse(m["w"])
        steps = ({"op": "define", "word": w}, {"op": "substitute", "rels": m["substituted"]},
                 {"op": "eliminate", "gen": m["gen"], "target": m["iso_index"] + 1, "expr": m["expr"]})
        try:
            image = apply_steps(pres, steps)
        except Exception as exc:
            errs.append(f"cov {k}: {exc}")
            continue
        if canonical_rels(tuple(reduce(r) for r in image.rels)) != canon(to):
            errs.append(f"cov image {k}")
        aut = is_automorphic_step(pres, dict(m, w_ints=w))
        if aut != m["aut"]:
            errs.append(f"cov aut flag {k}")
        verdict_aut &= aut
    if ("ac_path" if verdict_aut else "stable_cert") != rec["kind"]:
        errs.append("kind")
    return errs


def main(folder, outp=None):
    report, bad = {}, []
    for f in sorted(Path(folder).glob("*.jsonl")):
        rows = [r for r in read_jsonl(f) if r.get("solved")]
        n_bad = 0
        for r in rows:
            e = check_row(r)
            if e:
                n_bad += 1
                bad.append((f.name, r["id"], e[:5]))
        report[f.name] = {"solved": len(rows), "failed": n_bad,
                          "stable_cert": sum(r["kind"] == "stable_cert" for r in rows)}
    out = {"files": report, "all_pass": not bad, "failures": bad[:50]}
    print(json.dumps(out, indent=1))
    if outp:
        Path(outp).write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:])
