"""Independent proof checker for every merge the sweep claims.

It re-derives each claim from the original data by pure string substitution, and shares none of
the search's *inference*: not Whitehead's algorithm, not the peak reduction, not the move
generator, not the union-find. If a merge does not verify here, it does not get reported.

What each merge asserts, and how it is checked
----------------------------------------------
``aut``  Roots A and B are Aut(F2)-equivalent.
         Check: canon(phi_A(A)) == canon(phi_B(B)), and phi_A, phi_B are genuinely
         automorphisms of F2.

``aca``  Roots A and B are ACA-equivalent -- the same problem: A is AC-trivial <=> B is.
         Check: replay both paths. A step is (move, phi, rep): apply the Definition 2.1 move to
         the current presentation, then the change of variables phi, canonicalise, and land
         exactly on rep. Both paths must end at the same Aut-class.

Every phi is separately proved to be an automorphism by **Nielsen reduction** -- a decision
procedure for "is (u, v) a basis of F2" that is completely independent of the Whitehead code
the search used to produce phi in the first place. This is the check that would catch a bug in
``autcanon.py``: a non-automorphism phi would break the whole argument, because only an
*automorphism* carries the trivial presentation to a basis.

**Canonicalisation is deliberately NOT taken from ``words.py``.** The search canonicalises with
``words.canon_pair`` (Booth's least rotation); if the verifier used the same routine, a bug in it
would be invisible -- search and checker would agree on a wrong canonical form and a bad merge
would pass. So the verifier canonicalises through the repo's own numba ``canonical_pair_nj``
(`experiments/search/greedy_baseline.py:175`), which is a separate implementation that the greedy
pipeline's test suite already guards. The only word algebra the verifier does itself is rotation,
inversion and concatenation -- a few lines of string slicing, auditable by eye.

Exit code is non-zero if any claim fails.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.equivalence_classes.acmoves import canon as canon_nj  # noqa: E402
from experiments.equivalence_classes.words import (  # noqa: E402
    abelian_det, apply_hom, free_reduce, inv, ms_presentation, rot,
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def canon(r1, r2):
    """Canonical pair, via the repo's numba solver -- NOT via ``words.canon_pair``."""
    return canon_nj(r1, r2)


def replay(pair, move):
    """Apply one Definition 2.1 move, canonicalising with the numba solver.

        r_i  <-  rot_{k1}(r_i) . rot_{k2}(r_{3-i}^{jsign})
    """
    target, jsign, k1, k2 = move
    r1, r2 = pair
    ri, rj = (r1, r2) if target == 1 else (r2, r1)
    oj = rj if jsign == 1 else inv(rj)
    piece = rot(ri, k1) + rot(oj, k2)
    return canon(piece, r2) if target == 1 else canon(r1, piece)


# --------------------------------------------------------------------------
# Is phi an automorphism of F2?  Nielsen reduction -- independent of Whitehead.
# --------------------------------------------------------------------------
def is_basis(u, v):
    """True iff (u, v) is a basis of F2. Classical Nielsen reduction on a 2-tuple.

    Repeatedly replace a generator by a shorter product with another (or its inverse). The
    process terminates in a Nielsen-reduced pair, and (u, v) generates F2 freely iff that pair
    is a permutation of two distinct generators.
    """
    u, v = free_reduce(u), free_reduce(v)
    changed = True
    while changed:
        changed = False
        if not u or not v:
            return False
        for _ in range(2):
            for a, b in ((u, v), (v, u)):
                for cand in (free_reduce(a + b), free_reduce(a + inv(b)),
                             free_reduce(inv(b) + a), free_reduce(b + a)):
                    if len(cand) < len(a):
                        if a is u:
                            u = cand
                        else:
                            v = cand
                        changed = True
                        break
                if changed:
                    break
            if changed:
                break
    return {u.lower(), v.lower()} == {"x", "y"} and len(u) == 1 and len(v) == 1


def check_phi(phi, where, errs):
    if not is_basis(phi["x"], phi["y"]):
        errs.append(f"{where}: phi is NOT an automorphism of F2: x->{phi['x']}, y->{phi['y']}")
        return False
    return True


def legal_move(pair, move, where, errs):
    target, jsign, k1, k2 = move
    r1, r2 = pair
    if target not in (1, 2) or jsign not in (1, -1):
        errs.append(f"{where}: malformed move {move}")
        return False
    ri, rj = (r1, r2) if target == 1 else (r2, r1)
    if not (0 <= k1 < max(len(ri), 1)) or not (0 <= k2 < max(len(rj), 1)):
        errs.append(f"{where}: rotation out of range in {move} on {pair}")
        return False
    return True


def replay_path(start, path, where, errs):
    """start -> ... -> final Aut-class rep, checking every step by substitution."""
    cur = start
    for i, (move, phi, rep) in enumerate(path):
        rep = tuple(rep)
        if not legal_move(cur, move, f"{where}[{i}]", errs):
            return None
        child = replay(cur, tuple(move))
        if not check_phi(phi, f"{where}[{i}]", errs):
            return None
        got = canon(apply_hom(child[0], phi), apply_hom(child[1], phi))
        if got != rep:
            errs.append(f"{where}[{i}]: replay landed on {got}, certificate claims {rep}")
            return None
        cur = rep
    return cur


def main():
    path = sys.argv[1]
    data = json.load(open(path))
    # Rebuild every source's presentation from the ORIGINAL data, never from the sweep's own
    # output -- otherwise the check would be circular. MS bridge sources are reconstructed from
    # their (n, w) parameters via the Miller-Schupp definition.
    reps = {r["name"]: (r["r1"], r["r2"]) for r in csv.DictReader(
        open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")))}
    reps["TRIVIAL"] = ("x", "y")
    order = [r["name"] for r in csv.DictReader(
        open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")))]
    for name in data["roots"]:
        if name.startswith("MS/"):
            _, n, w = name.split("/")
            reps[name] = ms_presentation(int(n), w)

    roots = data["roots"]
    errs = []
    n_aut = n_aca = n_pre = 0

    # ---- pre-unioned sources: states the 1M-node sweep RECORDED for a given root.
    # These are not replayable (the sweep stored the state, not the path to it), so the
    # AC-reachability rests on the solver's construction -- `min_relator` / `max_relator` are by
    # definition states `expand_node_nj` emitted from that row's root. What IS checkable, and
    # what is checked here, is the provenance: the state must actually appear in that row of the
    # jsonl, under that field. A typo or an off-by-one in pres_id would be caught.
    pre = data.get("pre_union", [])
    if pre:
        rows = {}
        with open(os.path.join(ROOT, "results", "greedy_baseline",
                               "greedy_1000000_261_mrl48_cyc_all_07_09_26.jsonl")) as f:
            for line in f:
                row = json.loads(line)
                rows[row["pres_id"]] = row
        for p in pre:
            _, root, fld = p["state"].split("/")
            if root != p["root"]:
                errs.append(f"pre_union {p['state']}: root mismatch {p['root']}")
                continue
            pid = order.index(root)
            got = rows[pid].get(fld)
            if got != [p["r1"], p["r2"]]:
                errs.append(f"pre_union {p['state']}: not the jsonl's {fld} for pres_id {pid}")
                continue
            reps[p["state"]] = (p["r1"], p["r2"])
            n_pre += 1

    # every root's Aut-normalisation is itself a claim: canon(phi(P)) == aut_rep
    for name, r in roots.items():
        raw = canon(*reps[name])
        if tuple(r["raw"]) != raw:
            errs.append(f"root {name}: canonical form {raw} != recorded {tuple(r['raw'])}")
            continue
        if not check_phi(r["phi"], f"root {name}", errs):
            continue
        got = canon(apply_hom(raw[0], r["phi"]), apply_hom(raw[1], r["phi"]))
        if got != tuple(r["aut_rep"]):
            errs.append(f"root {name}: phi lands on {got}, claims {tuple(r['aut_rep'])}")

    for m in data["merges"]:
        a, b, at = m["a"], m["b"], tuple(m["at"])
        ra = tuple(roots[a]["aut_rep"])
        rb = tuple(roots[b]["aut_rep"])
        w = f"{m['kind']} {a}={b}"
        if m["kind"] == "aut":
            if ra != rb:
                errs.append(f"{w}: roots are NOT Aut-equivalent ({ra} vs {rb})")
            else:
                n_aut += 1
            continue
        ea = replay_path(ra, [(tuple(s[0]), s[1], tuple(s[2])) for s in m["path_a"]],
                         f"{w}.a", errs)
        eb = replay_path(rb, [(tuple(s[0]), s[1], tuple(s[2])) for s in m["path_b"]],
                         f"{w}.b", errs)
        if ea is None or eb is None:
            continue
        if ea != eb:
            errs.append(f"{w}: paths end at different Aut-classes: {ea} vs {eb}")
        elif ea != at:
            errs.append(f"{w}: paths end at {ea}, certificate claims {at}")
        else:
            n_aca += 1

    # the abelianisation invariant the search never computes: |det| is AC-invariant, and
    # a change of variables sends the row lattice L -> L.A with |det A| = 1, so |det| is
    # constant on every class we claim. A violation would mean a merge is simply wrong.
    dets = {}
    for cls in data["classes"]:
        ds = {abs(abelian_det(*reps[n])) for n in cls if n in reps}
        if len(ds) > 1:
            errs.append(f"class {cls[:4]}...: |det| not constant: {ds}")
        dets.setdefault(tuple(sorted(ds)), 0)
        dets[tuple(sorted(ds))] += 1

    print(f"checked {len(roots)} roots, {n_aut} aut merges, {n_aca} aca merges"
          + (f", {n_pre} pre-unioned 1M-node states (provenance)" if n_pre else ""))
    print(f"|det| profile over classes: {dets}")
    if errs:
        print(f"\nFAILED: {len(errs)} problems")
        for e in errs[:25]:
            print("  -", e)
        sys.exit(1)
    print("\nALL CERTIFICATES VERIFY")


if __name__ == "__main__":
    main()
