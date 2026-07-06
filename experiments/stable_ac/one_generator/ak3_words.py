"""AK(3) "wormhole" word bank + explicit-word stabilization.

For the 3-generator ``z = w(x,y)`` stabilization, ``w`` is a FREE choice. This module builds
~100 literature-grounded candidate words ``w`` (int-encoded over ``{+-1,+-2}``: x->1, X->-1,
y->2, Y->-2) to throw at AK(3), and provides ``stabilize_with_word`` — the generalization of
``stabilize.stabilize_flat`` from the 4 named specs {x,y,r1,r2} to an arbitrary int word, built
ONLY from the shipped, validated ``stabilize.py`` primitives (so the transform is identical to the
one already in use; a differential gate in ``main`` pins that).

Families (priority = escalation order for the 1M tier; 1 = strongest theory prior), grounded in
``literature/txt/{change_of_variables_stable_ac,math_ml_paper_2408.15332,mentor_email_stable_ac_ideas}``:
  1 relhalf  — relator sides of AK(3) ⟨x,y|xyx=yxy, x^3=y^4⟩ + rotations/inverses (Fagan z=xyx & alts)
  2 wk       — y^-k · x^-1 y x y  for k in [-8,8]  (paper Thm 6/7: exact valid isolations of x)
  3 wstar    — y^-1 x y x^-1  + automorphism images  (paper Thm 3: collapses an MS family)
  4 conj     — g·x·g^-1, g·y·g^-1 for short g  (Wirtinger/Remark 17: conjugation relators isolate)
  5 comm     — commutators [x,y],[y,x],... + short double commutators  (App F bridge is commutator-heavy)
  6 brute    — all freely-reduced words of length <=3 (cheap breadth probes; mentor's dumb family)
  7 ms       — MS(n,w) library w-values (w1 = y^-1 x^-1 y x y, Prop 5, etc.)
  (control r1/r2 words are FORM-dependent and added by the driver, family "control".)

Encoding note: the z-relator is ``[z] ++ inverse(w)`` free+cyclically reduced; z=3 never cancels a
letter of w (w is over +-1,+-2), so ``|z-relator| = 1 + |free_reduce(w)|`` and dedup on the
freely-reduced ``w`` sequence == dedup on distinct z-relators. Words are dropped if they reduce to
empty (that is the trivial-z dead end) or exceed the length cap ``1+|w| <= L=24``.

Pure Python (imports only ``stabilize``; no numba/JAX). ``python ak3_words.py`` dumps
``word_bank.json`` and runs the differential + round-trip gates.
"""
import json
import os

import stabilize as stab

L = stab.L                      # 24
Z = 3                           # new generator id (x=1, y=2, z=3)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_DIR = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "ak_3_test")

_CH2INT = {"x": 1, "X": -1, "y": 2, "Y": -2}
_INT2CH = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}


# ---- word <-> string (X = x^-1, Y = y^-1) ----------------------------------

def parse(s):
    return [_CH2INT[c] for c in s]


def to_str(w):
    return "".join(_INT2CH[a] for a in w)


def inv_str(s):
    return to_str(stab.inverse(parse(s)))


# ---- AK(3), two forms (both are AK(3)) -------------------------------------

def _flat2(r1_str, r2_str):
    return stab.relators_to_flat([parse(r1_str), parse(r2_str)], n_gen=2, half=L)


# textbook: <x,y | xyx=yxy, x^3=y^4>  — where the theory's words are provably isolatable
AK3_TEXTBOOK = _flat2("xyxYXY", "xxxYYYY")
# dataset rep 13_1 = ms_reps_unsolved.txt idx 0 — the exact object in the dataset
AK3_REP = _flat2("YXyXYx", "YYYXXXX")

FORMS = {"textbook": AK3_TEXTBOOK, "rep": AK3_REP}


# ---- the explicit-word stabilization (mirrors stabilize.stabilize_flat) ------

def stabilize_with_word(flat, w, old_n_gen=2, new_n_gen=3, half=L):
    """``<x,y|r1,r2> -> <x,y,z|r1,r2, z·w^-1>`` for an arbitrary int word ``w`` (list over
    +-1,+-2). Built from stabilize.py primitives so it is byte-identical to ``stabilize_flat``
    when ``w`` equals a named spec's word (pinned by the differential gate in ``main``)."""
    rels = stab.flat_to_relators(flat, old_n_gen, half)
    z_relator = stab.cyclic_reduce([new_n_gen] + stab.inverse(list(w)))
    return stab.relators_to_flat(rels + [z_relator], new_n_gen, half)


def z_relator_for(w, new_n_gen=3):
    return stab.cyclic_reduce([new_n_gen] + stab.inverse(list(w)))


# ---- word families ----------------------------------------------------------

def _relhalf():
    strs = ["xyx", "yxy", "xxx", "yyyy",            # relator sides (braid + power)
            "yxx", "xxy", "xyy", "yyx",             # cyclic rotations of xyx / yxy
            "XYX", "YXY", "XXX", "YYYY",            # inverses
            "xyxY", "Yxyx",                          # Fagan's stated alt xyxy^-1 and rotation
            "xx", "yy", "yyy"]                       # short power fragments
    return [("relhalf", s) for s in strs]


def _wk():
    out = []
    for k in range(-8, 9):
        pref = ("Y" * k) if k > 0 else ("y" * (-k))   # y^-k
        out.append(("wk", pref + "Xyxy"))             # x^-1 y x y
    return out


def _wstar():
    strs = ["YxyX",         # w* = y^-1 x y x^-1
            "XyxY",         # x<->y automorphism image (x^-1 y x y^-1)
            "xYXy", "yXYx", # inverse / rotation images
            "Xyxy", "xYxY"]
    return [("wstar", s) for s in strs]


def _conj():
    gs = ["x", "y", "X", "Y", "xy", "yx", "xY", "Yx", "xx", "yy", "XY", "Xy"]
    out = []
    for g in gs:
        gi = inv_str(g)
        for base in ("x", "y"):
            out.append(("conj", g + base + gi))
    return out


def _comm():
    strs = ["XYxy", "YXyx", "xyXY", "yxYX",          # [x,y],[y,x] two conventions
            "XyXy", "xYxY",                           # [x,Y]-ish
            "yxYXx",                                   # (padding-safe short mix)
            "XYxyx", "xyXYX"]                          # short double-commutator flavored
    return [("comm", s) for s in strs]


def _brute():
    """All freely-reduced words of length 1..3 over {x,X,y,Y}."""
    letters = [1, -1, 2, -2]
    all_words, lvl = [], [[a] for a in letters]
    all_words += lvl
    for _ in range(2):                                # extend to length 2, then 3
        lvl = [w + [a] for w in lvl for a in letters if w[-1] != -a]
        all_words += lvl
    return [("brute", to_str(w)) for w in all_words]


def _ms():
    strs = ["YXyxy",        # w1 = y^-1 x^-1 y x y (Prop 5: AK(n) ≡ MS(n,w1))
            "yxyXY", "Xyxyy", "yxyx", "xyxyy"]
    return [("ms", s) for s in strs]


def _raw_families():
    # order matters: earlier family wins a dedup tie (keeps the higher-prior name)
    return _relhalf() + _wk() + _wstar() + _conj() + _comm() + _ms() + _brute()


_PRIORITY = {"relhalf": 1, "wk": 2, "wstar": 3, "conj": 4, "comm": 5, "ms": 7, "brute": 6,
             "control": 8}


def build_word_bank():
    """-> list of dicts, deduped by the freely-reduced word (== distinct z-relator), length-capped.
    Fields: name, family, priority, w_str, w_ints, w_len, z_relator, z_len."""
    seen = set()
    bank = []
    for family, s in _raw_families():
        w = stab.free_reduce(parse(s))
        if len(w) == 0:                               # trivial z=1 dead end
            continue
        key = tuple(w)
        if key in seen:
            continue
        zrel = z_relator_for(w)
        if len(zrel) > L:                             # z-relator must fit L=24
            continue
        seen.add(key)
        bank.append({
            "name": to_str(w),
            "family": family,
            "priority": _PRIORITY[family],
            "w_str": to_str(w),
            "w_ints": list(w),
            "w_len": len(w),
            "z_relator": list(zrel),
            "z_len": len(zrel),
        })
    return bank


# ---- gates + dump -----------------------------------------------------------

def _differential_gate():
    """stabilize_with_word == shipped stabilize_flat on the named relator specs, both forms."""
    for form, flat in FORMS.items():
        rels = stab.flat_to_relators(flat, 2, L)
        for spec, ridx in (("r1", 0), ("r2", 1)):
            got = stabilize_with_word(flat, list(rels[ridx]))
            exp = stab.stabilize_flat(flat, spec)
            assert got == exp, f"{form}/{spec}: stabilize_with_word != stabilize_flat"
            # decode round-trip: z-relator decodes back to w (up to reduction)
            zrel = stab.flat_to_relators(got, 3, L)[-1]
            dec = stab.cyclic_reduce(stab.decode_z_word(list(zrel), Z))
            assert dec == stab.cyclic_reduce(list(rels[ridx])), f"{form}/{spec}: z decode mismatch"


def main():
    # rep form must match the dataset object exactly
    import ast
    rep_line = open(os.path.join(ROOT, "data", "ms_unsolved_reps",
                                 "ms_reps_unsolved.txt")).readline()
    assert AK3_REP == ast.literal_eval(rep_line), "AK3_REP != ms_reps_unsolved idx 0"

    _differential_gate()

    bank = build_word_bank()
    n = len(bank)
    by_fam = {}
    for e in bank:
        by_fam[e["family"]] = by_fam.get(e["family"], 0) + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "word_bank.json")
    with open(out, "w") as f:
        json.dump({"n_words": n, "by_family": by_fam,
                   "forms": {k: list(v) for k, v in FORMS.items()},
                   "max_w_len": max(e["w_len"] for e in bank),
                   "max_z_len": max(e["z_len"] for e in bank),
                   "words": bank}, f, indent=1)

    print(f"[ak3_words] built {n} unique words  (max |w|={max(e['w_len'] for e in bank)}, "
          f"max |z-rel|={max(e['z_len'] for e in bank)} <= L={L})")
    print(f"[ak3_words] by family: {by_fam}")
    print(f"[ak3_words] differential + round-trip gates PASS; wrote {os.path.relpath(out, ROOT)}")
    assert n >= 90, f"word bank too small: {n} < 90"
    assert max(e["z_len"] for e in bank) <= L
    print("[ak3_words] Phase 0 gate PASS (>=90 words, z-relator <= L).")


if __name__ == "__main__":
    main()
