"""The verification pipeline: re-prove every class in `certificates.json` from the raw data.

Reads exactly two things -- `results/equivalence_classes/certificates.json` and the original
`data/ms_unsolved_reps/ms_reps_unsolved.csv` -- and re-derives every claim by string substitution.
It does not import the search, the union-find, Whitehead's algorithm, or ``autinv``. If a
certificate does not verify here, the class it belongs to is not proved.

    .venv/bin/python3 experiments/equivalence_classes/verify/verify_proofs.py

What is checked, per edge
-------------------------
  * both endpoints exist in the CSV at the ``pres_id`` the certificate names, **and** the words
    stored in the certificate are the CSV's words -- a wrong id cannot slip through by carrying
    the right words, nor the reverse;
  * every ``phi`` (the initial change of variables, and every one inside a path) really is an
    automorphism of F2, by **Nielsen reduction** -- an independent decision procedure for "is
    (u, v) a basis", sharing nothing with the Whitehead code that produced phi;
  * every Definition 2.1 move is in range and, replayed by substitution, lands on exactly the
    state the certificate records;
  * both sides of an edge end on the same state, and it is the recorded meeting point;
  * ``cv`` edges: the single substitution really does carry A onto B -- ``canon(psi(A)) ==
    canon(B)``. (This equality is asserted for ``cv`` and **only** for ``cv``. On an ``ac`` edge
    the two sides differ by the AC moves, so the analogous equality is false *by construction*
    and asserting it would fail a correct certificate. There, ``endpoint_subst`` is checked for
    being an automorphism and nothing more.)
  * ``pure_ac_path`` is not taken on trust: the flag is recomputed from the steps.

And, per class
--------------
  * ``|det|`` of the exponent-sum matrix -- an AC-invariant that a change of variables also
    preserves -- is constant. The search never computes it, so a wrong merge would show here.
  * the edges span the class: they must form a tree on exactly its members.

And once, globally -- **the number itself**
-------------------------------------------
Verifying every edge is a different claim from verifying the count. The partition is rebuilt from
the verified edges alone and required to equal the reported classes exactly. Only then is
"126 classes" a result rather than a number the search printed.

Canonicalisation goes through the repo's numba ``canonical_pair_nj`` (via ``acmoves.canon``),
never ``words.canon_pair``: the search used the latter, and a shared bug would be invisible.
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
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    abelian_det, apply_hom, cyc_reduce, free_reduce, inv, rot,
)

ID = {"x": "x", "y": "y"}


def is_basis(u, v):
    """True iff (u, v) is a basis of F2 -- classical Nielsen reduction on a 2-tuple."""
    u, v = free_reduce(u), free_reduce(v)
    changed = True
    while changed:
        changed = False
        if not u or not v:
            return False
        for a_is_u, (a, b) in ((True, (u, v)), (False, (v, u))):
            for cand in (free_reduce(a + b), free_reduce(a + inv(b)),
                         free_reduce(inv(b) + a), free_reduce(b + a)):
                if len(cand) < len(a):
                    if a_is_u:
                        u = cand
                    else:
                        v = cand
                    changed = True
                    break
            if changed:
                break
    return len(u) == 1 and len(v) == 1 and u.lower() != v.lower()


def replay(pair, move):
    """One Definition 2.1 move:  r_i <- rot_k1(r_i) . rot_k2(r_j^jsign)."""
    t, j, k1, k2 = move
    r1, r2 = pair
    ri, rj = (r1, r2) if t == 1 else (r2, r1)
    oj = rj if j == 1 else inv(rj)
    piece = rot(ri, k1) + rot(oj, k2)
    return canon(piece, r2) if t == 1 else canon(r1, piece)


class Checker:
    def __init__(self):
        self.errs = []

    def bad(self, msg):
        """Record a failure. Returns None, so `return self.bad(...)` is always a clean abort --
        a checker that returns a falsy *value* instead of None leaks it into the caller's
        arithmetic and crashes there instead of reporting. (It did: `list(False)`.)"""
        self.errs.append(msg)
        return None

    def phi(self, phi, where):
        """True iff `phi` is an automorphism of F2."""
        if set(phi) != {"x", "y"}:
            self.bad(f"{where}: malformed substitution {phi}")
            return False
        if not is_basis(phi["x"], phi["y"]):
            self.bad(f"{where}: x->{phi['x']}, y->{phi['y']} is NOT an automorphism of F2")
            return False
        return True

    def witness(self, raw, target, wit, where):
        """Re-do the normalisation **the way the proof book prints it, by hand**.

        The book tells a reader: take this relator, reduce it, invert it, rotate it by k, and you
        get that one. Those printed steps are the proof a human actually reads, so they must be
        the steps a machine actually checks -- otherwise the human is auditing prose while the
        machine audits something else. Here each witness is replayed literally: cyclically reduce,
        invert if it says so, rotate by exactly k, and require the printed result.

        Also requires the witness to be a bijection {r1, r2} -> {r1, r2}: a relator may swap slots,
        but two of them cannot land in the same one.
        """
        if wit is None:
            return True
        if len(wit) != 2 or {w["from_relator"] for w in wit} != {1, 2} \
                or {w["to_relator"] for w in wit} != {1, 2}:
            self.bad(f"{where}: the normalisation is not a bijection on the two relators")
            return False
        for w in wit:
            src = raw[w["from_relator"] - 1]
            red = cyc_reduce(src)
            if red != w["reduced"]:
                self.bad(f"{where}: r{w['from_relator']} = {src} reduces to {red}, "
                         f"the book prints {w['reduced']}")
                return False
            cur = inv(red) if w["inverted"] else red
            cur = rot(cur, w["rotate"])
            if cur != w["result"] or cur != target[w["to_relator"] - 1]:
                self.bad(f"{where}: r{w['from_relator']}"
                         f"{' inverted' if w['inverted'] else ''} rotated by {w['rotate']} gives "
                         f"{cur}, but the book prints {w['result']} and the state has "
                         f"{target[w['to_relator'] - 1]}")
                return False
        return True

    def side(self, side, words, where):
        """raw presentation -> phi0 -> Aut-minimal rep -> (move, phi)* -> end. Every step.

        Returns the end state, or None if anything failed.
        """
        start = canon(*words)
        if tuple(side["start"]) != start:
            return self.bad(f"{where}: start {side['start']} is not canon{words} = {list(start)}")
        if not self.phi(side["phi0"], f"{where}.phi0"):
            return None
        sub0 = [free_reduce(apply_hom(w, side["phi0"])) for w in start]
        if sub0 != side["phi0_substituted"]:
            return self.bad(f"{where}: substituting phi0 gives {sub0}, the book prints "
                            f"{side['phi0_substituted']}")
        got = canon(*sub0)
        if got != tuple(side["aut_rep"]):
            return self.bad(f"{where}: phi0 lands on {list(got)}, certificate says "
                            f"{side['aut_rep']}")
        if not self.witness(sub0, side["aut_rep"], side["phi0_witness"], f"{where}.phi0"):
            return None
        cur = tuple(side["aut_rep"])
        for i, st in enumerate(side["steps"]):
            if len(st["move"]) != 4:
                return self.bad(f"{where}[{i}]: malformed move {st['move']}")
            t, j, k1, k2 = st["move"]
            if t not in (1, 2) or j not in (1, -1):
                return self.bad(f"{where}[{i}]: malformed move {st['move']}")
            ri, rj = (cur[0], cur[1]) if t == 1 else (cur[1], cur[0])
            if not (0 <= k1 < max(len(ri), 1)) or not (0 <= k2 < max(len(rj), 1)):
                return self.bad(f"{where}[{i}]: rotation out of range in {st['move']} on "
                                f"{list(cur)}")
            # the two rotated pieces and their product, exactly as the book prints them
            d = st["detail"]
            ri, rj = (cur[0], cur[1]) if t == 1 else (cur[1], cur[0])
            oj = rj if j == 1 else inv(rj)
            pi, pj = rot(ri, k1), rot(oj, k2)
            if pi != d["piece_i"] or pj != d["piece_j"]:
                return self.bad(f"{where}[{i}]: the rotated pieces are {pi} and {pj}, the book "
                                f"prints {d['piece_i']} and {d['piece_j']}")
            if pi + pj != d["product"] or free_reduce(pi + pj) != d["reduced"]:
                return self.bad(f"{where}[{i}]: the product does not match what the book prints")
            raw_pair = [d["product"], cur[1]] if t == 1 else [cur[0], d["product"]]
            if raw_pair != d["raw_pair"]:
                return self.bad(f"{where}[{i}]: raw_pair {d['raw_pair']} is not the pair after "
                                f"the move ({raw_pair})")

            after = replay(cur, st["move"])
            if after != tuple(st["after_move"]):
                return self.bad(f"{where}[{i}]: the move lands on {list(after)}, certificate "
                                f"says {st['after_move']}")
            if not self.witness(raw_pair, st["after_move"], st["move_witness"],
                                f"{where}[{i}].move"):
                return None
            if not self.phi(st["phi"], f"{where}[{i}].phi"):
                return None
            sub = [free_reduce(apply_hom(w, st["phi"])) for w in after]
            if sub != st["phi_substituted"]:
                return self.bad(f"{where}[{i}]: substituting phi gives {sub}, the book prints "
                                f"{st['phi_substituted']}")
            nxt = canon(*sub)
            if nxt != tuple(st["state"]):
                return self.bad(f"{where}[{i}]: after the change of variables the state is "
                                f"{list(nxt)}, certificate says {st['state']}")
            if st["phi"] != ID and not self.witness(sub, st["state"], st["phi_witness"],
                                                    f"{where}[{i}].phi"):
                return None
            cur = nxt
        if cur != tuple(side["end"]):
            return self.bad(f"{where}: path ends at {list(cur)}, certificate says {side['end']}")
        return cur


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "results", "equivalence_classes", "certificates.json")
    cert = json.load(open(path))
    ck = Checker()

    # --- the ONLY other input: the original presentations, by row number ---------------
    rows = list(csv.DictReader(open(
        os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv"))))
    csv_words = {i: (r["name"], r["r1"], r["r2"]) for i, r in enumerate(rows)}

    words, seen = {}, {}
    for c in cert["classes"]:
        for m in c["members"]:
            row = csv_words.get(m["pres_id"])
            if row is None:
                ck.bad(f"pres_id {m['pres_id']} is not a row of the CSV")
                continue
            if row[0] != m["name"] or row[1] != m["r1"] or row[2] != m["r2"]:
                ck.bad(f"pres_id {m['pres_id']}: certificate says {m['name']} "
                       f"({m['r1']}, {m['r2']}), CSV row says {row[0]} ({row[1]}, {row[2]})")
                continue
            if m["name"] in seen:
                ck.bad(f"{m['name']} appears in two classes: {seen[m['name']]} and "
                       f"{c['class_id']}")
            seen[m["name"]] = c["class_id"]
            words[m["name"]] = (m["r1"], m["r2"])

    if len(seen) != len(rows):
        ck.bad(f"the classes cover {len(seen)} presentations, the CSV has {len(rows)}")

    # --- every edge --------------------------------------------------------------------
    n_cv = n_ac = n_pure = 0
    verified = []
    for c in cert["classes"]:
        for e in c["edges"]:
            a, b = e["a"]["name"], e["b"]["name"]
            w = f"class {c['class_id']} edge {a}={b}"
            if a not in words or b not in words:
                ck.bad(f"{w}: endpoint not among the classes' members")
                continue
            ea = ck.side(e["side_a"], words[a], f"{w}.left")
            eb = ck.side(e["side_b"], words[b], f"{w}.right")
            if ea is None or eb is None:
                continue
            if ea != eb:
                ck.bad(f"{w}: the two sides end at different states, {list(ea)} vs {list(eb)}")
                continue
            if ea != tuple(e["meet"]):
                ck.bad(f"{w}: the sides meet at {list(ea)}, certificate says {e['meet']}")
                continue

            n_moves = len(e["side_a"]["steps"]) + len(e["side_b"]["steps"])
            if e["kind"] == "cv":
                if n_moves:
                    ck.bad(f"{w}: claims 'change of variables only' but uses {n_moves} AC moves")
                    continue
                if not ck.phi(e["subst"], f"{w}.psi"):
                    continue
                A, B = canon(*words[a]), canon(*words[b])
                sub = [free_reduce(apply_hom(r, e["subst"])) for r in A]
                if sub != e["subst_substituted"]:
                    ck.bad(f"{w}: substituting psi gives {sub}, the book prints "
                           f"{e['subst_substituted']}")
                    continue
                got = canon(*sub)
                if got != B:
                    ck.bad(f"{w}: psi carries {a} to {list(got)}, but canon({b}) is {list(B)}")
                    continue
                # and the pencil-steps the book prints for it
                if not ck.witness(sub, list(B), e["subst_witness"], f"{w}.psi"):
                    continue
                n_cv += 1
            else:
                if not n_moves:
                    ck.bad(f"{w}: claims AC moves but the paths are empty")
                    continue
                if not ck.phi(e["endpoint_subst"], f"{w}.endpoint_psi"):
                    continue
                # never trust the flag -- recompute it
                pure = all(s["phi"] == ID
                           for s in e["side_a"]["steps"] + e["side_b"]["steps"])
                if pure != e["pure_ac_path"]:
                    ck.bad(f"{w}: pure_ac_path={e['pure_ac_path']} but the steps say {pure}")
                    continue
                n_ac += 1
                n_pure += pure
            verified.append((a, b))

        # an AC-invariant the search never computes; a change of variables preserves it too
        dets = {abs(abelian_det(*words[m["name"]])) for m in c["members"] if m["name"] in words}
        if len(dets) > 1:
            ck.bad(f"class {c['class_id']}: |det| is not constant: {dets}")

    # --- THE NUMBER: rebuild the partition from the verified edges alone -----------------
    parent = {n: n for n in words}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in verified:
        ra, rb = find(a), find(b)
        if ra == rb:
            ck.bad(f"edge {a}={b} is redundant -- the merges should be a spanning forest")
        parent[rb] = ra

    rebuilt = {}
    for n in words:
        rebuilt.setdefault(find(n), set()).add(n)
    got = {frozenset(v) for v in rebuilt.values()}
    want = {frozenset(m["name"] for m in c["members"]) for c in cert["classes"]}
    if got != want:
        ck.bad(f"PARTITION MISMATCH: {len(got)} classes rebuilt from the verified edges, "
               f"{len(want)} reported")

    s = cert["summary"]
    for k, v in (("classes", len(want)), ("cv_edges", n_cv), ("ac_edges", n_ac),
                 ("ac_pure_path_edges", n_pure), ("presentations", len(words))):
        if s.get(k) != v:
            ck.bad(f"summary says {k}={s.get(k)}, verification counted {v}")

    print(f"presentations re-read from the CSV : {len(words)}")
    print(f"change-of-variables edges verified : {n_cv}   (one substitution, canon(psi(A)) "
          f"== canon(B))")
    print(f"AC-move edges verified             : {n_ac}   ({n_pure} of them a pure AC path)")
    print(f"partition rebuilt from verified edges alone: {len(got)} classes == "
          f"the {len(want)} reported")
    if ck.errs:
        print(f"\nFAILED: {len(ck.errs)} problems")
        for e in ck.errs[:25]:
            print("  -", e)
        sys.exit(1)
    print(f"\nALL {n_cv + n_ac} EDGES VERIFY. The 261 presentations are {len(want)} distinct "
          f"problems.")


if __name__ == "__main__":
    main()
