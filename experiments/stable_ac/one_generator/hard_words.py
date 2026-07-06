"""Hard-but-solvable "wormhole" word bank — z=w(x,y) sweep on a chosen MS(1190) presentation.

Sibling of ``ak3_words.py``. AK(3) gave a *negative* result (0 solved, plateau 13), so it can't
tell us which word family is most useful. This module points the SAME breadth of z=w candidate
words at a presentation the plain 2-generator greedy DID solve, but only after many nodes and a long
path — a controlled study of "which kind of word solves a given hard problem best".

Targets (both from ``data/1190MS.txt``, both solved by the 2-gen baseline; built-in n=3 dumb-word
controls already on disk under ``results/.../ms640/``):
  idx 625 (MS n=7): r1=Xy^7xY^8 (len17), r2=YYXYxyX (len7). 2-gen: 77,385 nodes / 663 moves.
                    z=r1 ✅77k, z=r2 ✅80k, z=x ❌, z=y ❌.
  idx 610 (MS n=6): r1=Xy^6xY^7 (len15), r2=YYYxYXyx (len8). 2-gen: 61,066 nodes / 307 moves.
                    z=r1 ✅61k, z=r2 ❌, z=x ❌, z=y ❌ (strictest — only r1 works among dumb words).

Word families reuse ``ak3_words``' generic builders verbatim (wk/wstar/conj/comm/ms/brute — the
"different kinds of words" breadth). The one AK(3)-specific family, ``relhalf`` (literal xyx/yxy/x^3/
y^4), is REPLACED here by ``_relhalf_for(r1,r2)`` — the actual relator sides/subwords of the chosen
target, so relhalf stays grounded in *this* presentation's relators.

Pure Python (imports ``stabilize`` + ``ak3_words``; no numba/JAX). ``python hard_words.py`` dumps
``word_bank_ms625.json`` / ``word_bank_ms610.json`` and runs the differential + round-trip gates.
"""
import ast
import json
import os

import stabilize as stab
import ak3_words as aw
from ak3_words import (parse, to_str, inv_str, stabilize_with_word, z_relator_for,
                       _wk, _wstar, _conj, _comm, _ms, _brute, _PRIORITY, L, Z)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(ROOT, "data", "1190MS.txt")
OUT_DIR = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "hard_solved_test")

TARGETS = [625, 610]              # hardest (n=7) + moderately hard (n=6); user-locked


# ---- target loader ----------------------------------------------------------

def load_target(idx, path=DATA):
    """Return the flat 2*L-int base presentation at line ``idx`` (0-indexed) of 1190MS.txt.
    The file is one Python-literal flat list per line, already length-2*L."""
    with open(path) as f:
        for i, line in enumerate(f):
            if i == idx:
                flat = ast.literal_eval(line)
                if len(flat) != 2 * L:
                    raise ValueError(f"idx {idx}: expected flat len {2 * L}, got {len(flat)}")
                return flat
    raise IndexError(f"idx {idx} beyond end of {path}")


def relators_of(flat):
    """The two de-padded relators (int lists) of a 2-gen flat presentation."""
    r1, r2 = stab.flat_to_relators(flat, 2, L)
    return list(r1), list(r2)


# ---- target-specific relator-halves family (replaces AK(3)'s literal _relhalf) ----

def _maximal_runs(w):
    """Maximal same-letter runs of length >=2 (e.g. y^n, Y^{n+1} in an MS relator)."""
    runs, i, n = [], 0, len(w)
    while i < n:
        j = i
        while j < n and w[j] == w[i]:
            j += 1
        if j - i >= 2:
            runs.append(list(w[i:j]))
        i = j
    return runs


def _cyclic_halves(w):
    """Two contiguous halves of the relator read as a cyclic word (splice-flavored subwords)."""
    n = len(w)
    if n < 2:
        return []
    h = n // 2
    return [list(w[:h]), list(w[h:])]


def _relhalf_for(r1, r2):
    """Relator *parts* of the ACTUAL target relators: the relator's inverse, its maximal pure-power
    runs (y^n / Y^{n+1} / ...), and its two cyclic halves. The WHOLE relators are deliberately left
    out — those are the driver's ``r1``/``r2`` control words (avoids running z=r1/z=r2 twice under
    two names). Deduped downstream."""
    out = []
    for r in (list(r1), list(r2)):
        out.append(("relhalf", inv_str(to_str(r))))
        for run in _maximal_runs(r):
            out.append(("relhalf", to_str(run)))
        for half in _cyclic_halves(r):
            out.append(("relhalf", to_str(half)))
    return out


# ---- assemble the bank (mirrors ak3_words.build_word_bank; target relhalf swapped in) ----

def build_word_bank_for(base_flat):
    """-> list of word dicts for a specific base presentation, deduped by freely-reduced word
    (== distinct z-relator), length-capped to |z-relator| <= L. Same schema as
    ak3_words.build_word_bank. The generic families are reused verbatim; only ``relhalf`` is
    re-derived from ``base_flat``'s relators."""
    r1, r2 = relators_of(base_flat)
    raw = _relhalf_for(r1, r2) + _wk() + _wstar() + _conj() + _comm() + _ms() + _brute()
    seen, bank = set(), []
    for family, s in raw:
        w = stab.free_reduce(parse(s))
        if len(w) == 0:                                   # trivial z=1 dead end
            continue
        key = tuple(w)
        if key in seen:
            continue
        zrel = z_relator_for(w)
        if len(zrel) > L:                                 # z-relator must fit L=24
            continue
        seen.add(key)
        bank.append({
            "name": to_str(w), "family": family, "priority": _PRIORITY[family],
            "w_str": to_str(w), "w_ints": list(w), "w_len": len(w),
            "z_relator": list(zrel), "z_len": len(zrel),
        })
    return bank


# ---- gates + dump -----------------------------------------------------------

def _differential_gate(base_flat):
    """stabilize_with_word == shipped stabilize_flat on THIS target's own r1/r2 (the transform is
    identical to the one that produced the on-disk baselines), plus z-relator decode round-trip."""
    r1, r2 = relators_of(base_flat)
    for spec, r in (("r1", r1), ("r2", r2)):
        got = stabilize_with_word(base_flat, list(r))
        exp = stab.stabilize_flat(base_flat, spec)
        assert got == exp, f"{spec}: stabilize_with_word != stabilize_flat"
        zrel = stab.flat_to_relators(got, 3, L)[-1]
        dec = stab.cyclic_reduce(stab.decode_z_word(list(zrel), Z))
        assert dec == stab.cyclic_reduce(list(r)), f"{spec}: z decode mismatch"


def build_and_dump(idx):
    base_flat = load_target(idx)
    _differential_gate(base_flat)
    bank = build_word_bank_for(base_flat)
    n = len(bank)
    by_fam = {}
    for e in bank:
        by_fam[e["family"]] = by_fam.get(e["family"], 0) + 1
    r1, r2 = relators_of(base_flat)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"word_bank_ms{idx}.json")
    with open(out, "w") as f:
        json.dump({"idx": idx, "n_words": n, "by_family": by_fam,
                   "base_flat": list(base_flat),
                   "r1": to_str(r1), "r2": to_str(r2),
                   "max_w_len": max(e["w_len"] for e in bank),
                   "max_z_len": max(e["z_len"] for e in bank),
                   "words": bank}, f, indent=1)
    # HARD gates
    assert n >= 85, f"idx {idx}: word bank too small: {n} < 85"
    assert max(e["z_len"] for e in bank) <= L, f"idx {idx}: z-relator exceeds L"
    # relhalf words must be reduced subwords derived from the target (sanity: non-empty, over x,y)
    for e in bank:
        assert all(a in (1, -1, 2, -2) for a in e["w_ints"]), f"{e['name']}: word not over x,y"
    print(f"[hard_words] idx {idx}: r1={to_str(r1)} r2={to_str(r2)}")
    print(f"[hard_words] idx {idx}: built {n} unique words  by family: {by_fam}")
    print(f"[hard_words] idx {idx}: differential + round-trip + dedup gates PASS; "
          f"wrote {os.path.relpath(out, ROOT)}")
    return bank


def main():
    for idx in TARGETS:
        build_and_dump(idx)
    print("[hard_words] Phase 0.5 gate PASS (>=85 words each, z-relator <= L, transform pinned).")


if __name__ == "__main__":
    main()
