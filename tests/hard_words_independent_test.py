#!/usr/bin/env python3
"""
INDEPENDENT, adversarial black-box test suite for
experiments/stable_ac/one_generator/hard_words.py

This suite is written from the MATHEMATICAL SPEC of the "z=w stabilization"
Tietze move, NOT from the implementation. It builds its OWN oracle
(free_reduce / cyclic_reduce / inverse / flat<->relators, all defined below)
and compares byte-for-byte against the module under test.

Module under test (black box, public API ONLY):
    hard_words.load_target(idx)          -> 48-int flat 2-gen presentation
    hard_words.stabilize_with_word(f, w) -> 72-int flat 3-gen presentation
    hard_words.build_word_bank_for(f)    -> list of candidate word dicts
    hard_words._relhalf_for(r1, r2)      -> list of (family, word_string)

Second, independently-written oracle (sanctioned): stabilize.stabilize_flat /
stabilize.decode_z_word  -- a DIFFERENT module implementing the SAME transform
for the four named words {x, y, r1, r2}. Used to cross-check.

Spec of the transform (this is the oracle source):
  Encoding: x=1, X=x^-1=-1, y=2, Y=y^-1=-2, z=3, Z=z^-1=-3, 0=padding.
  A relator is an int list with no zeros inside. A flat n_gen presentation is a
  fixed-width int list of length n_gen*L (L=24): n_gen relators each
  left-justified in an L-wide slot, zero-padded on the right.
  z=w stabilization of <x,y | r1, r2> by word w over {+-1,+-2}:
      <x,y,z | r1, r2, cyclic_reduce([z] + inverse(w))>
  r1, r2 carried over UNCHANGED (re-padded into the wider 3-gen flat).

Run:  python tests/hard_words_independent_test.py
Exits nonzero on any failure.
"""

import os
import sys
import random

# --- wire up import path to the module under test -------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_MOD_DIR = os.path.abspath(os.path.join(_HERE, "..", "experiments", "stable_ac", "one_generator"))
if _MOD_DIR not in sys.path:
    sys.path.insert(0, _MOD_DIR)

import hard_words           # module under test (black box)
import stabilize            # sanctioned second oracle for {x,y,r1,r2}

L = 24  # max relator slot width (fixed by the spec)

# =========================================================================
# MY OWN word primitives (independent oracle -- do NOT import from the repo)
# =========================================================================

def free_reduce(w):
    """Delete adjacent inverse pairs (a followed by -a) until stable."""
    out = []
    for e in w:
        if out and out[-1] == -e:
            out.pop()
        else:
            out.append(e)
    return out


def cyclic_reduce(w):
    """Free-reduce, then also cancel matching inverse pairs wrapping the ends."""
    r = free_reduce(w)
    while len(r) >= 2 and r[0] == -r[-1]:
        r = r[1:-1]
    return r


def inverse(w):
    """Reverse the word and negate every element."""
    return [-e for e in reversed(w)]


def relators_from_flat(flat, n_gen):
    """Split a flat presentation into de-padded relators.

    A relator is left-justified and right-zero-padded with NO interior zeros.
    Also asserts that structural invariant (no nonzero after the first zero).
    """
    assert len(flat) == n_gen * L, f"flat length {len(flat)} != {n_gen*L}"
    rels = []
    for g in range(n_gen):
        chunk = list(flat[g * L:(g + 1) * L])
        # find first zero
        first_zero = L
        for i, v in enumerate(chunk):
            if v == 0:
                first_zero = i
                break
        body = chunk[:first_zero]
        tail = chunk[first_zero:]
        assert all(t == 0 for t in tail), (
            f"interior zero / non-canonical padding in relator {g}: {chunk}")
        assert all(v != 0 for v in body), f"zero inside relator body {g}: {body}"
        rels.append(body)
    return rels


def flat_from_relators(rels, n_gen):
    """Inverse of relators_from_flat: pad each relator to L and concat."""
    assert len(rels) == n_gen
    flat = []
    for r in rels:
        assert len(r) <= L, f"relator too long to pad: {r}"
        flat.extend(list(r) + [0] * (L - len(r)))
    return flat


def ref_z_relator(w):
    """My reference third relator = cyclic_reduce([z] + inverse(w))."""
    return cyclic_reduce([3] + inverse(w))


def parse_word(s):
    """Parse a word string like 'XYxyy' into ints. x=1,X=-1,y=2,Y=-2,z=3,Z=-3."""
    m = {'x': 1, 'X': -1, 'y': 2, 'Y': -2, 'z': 3, 'Z': -3}
    return [m[c] for c in s]


def is_cyclic_subword(sub, word):
    """True if `sub` occurs as a contiguous slice of `word` viewed as a ring."""
    m = len(word)
    if len(sub) == 0:
        return True
    if len(sub) > m:
        return False
    doubled = list(word) + list(word)
    for i in range(m):
        if doubled[i:i + len(sub)] == list(sub):
            return True
    return False


# =========================================================================
# Tiny self-test of MY OWN oracle primitives (guards against oracle bugs)
# =========================================================================

def _self_check_primitives(rec):
    rec.check("prim.free_reduce.basic", free_reduce([1, -1, 2]) == [2])
    rec.check("prim.free_reduce.cascade", free_reduce([1, 2, -2, -1, 2]) == [2])
    rec.check("prim.free_reduce.noop", free_reduce([1, 2, 1]) == [1, 2, 1])
    rec.check("prim.cyclic_reduce.wrap", cyclic_reduce([1, 2, -1]) == [2])
    rec.check("prim.cyclic_reduce.deep", cyclic_reduce([1, 2, 1, -2, -1]) == [1])
    rec.check("prim.inverse", inverse([1, 2, -1]) == [1, -2, -1])
    rec.check("prim.inverse.involution",
              inverse(inverse([1, 2, -2, -1, 1])) == [1, 2, -2, -1, 1])
    rec.check("prim.flat_roundtrip",
              flat_from_relators(relators_from_flat([1, -2] + [0]*22 + [2] + [0]*23, 2), 2)
              == [1, -2] + [0]*22 + [2] + [0]*23)
    rec.check("prim.parse_word", parse_word("XYxyz") == [-1, -2, 1, 2, 3])
    rec.check("prim.cyclic_subword.pos", is_cyclic_subword([1, -2], [-2, 1, -2, 3]))
    rec.check("prim.cyclic_subword.wrap", is_cyclic_subword([3, -2], [-2, 1, -2, 3]))
    rec.check("prim.cyclic_subword.neg", not is_cyclic_subword([1, 1], [-2, 1, -2, 3]))
    rec.check("prim.cyclic_subword.toolong", not is_cyclic_subword([1, 2, 3, 1, 2, 3, 1], [1, 2, 3]))


# =========================================================================
# Result recorder
# =========================================================================

class Recorder:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []
        self.notes = []

    def check(self, name, cond, detail=""):
        if cond:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append((name, detail))
            print(f"  FAIL [{name}] {detail}")

    def note(self, msg):
        self.notes.append(msg)


# =========================================================================
# A. stabilize_with_word invariants
# =========================================================================

TARGETS = [0, 1, 50, 610, 625]

# Hand-picked adversarial words over {+-1,+-2}:
HAND_WORDS = [
    [1], [2], [-1], [-2],                       # single letters
    [1, 2], [2, 1], [-1, -2], [1, -2, 1],       # short words
    [1, -1, 2],                                 # needs free reduction -> [2]
    [1, 2, -2, -1, 2],                          # free-reduces -> [2]
    [1, 2, -1],                                 # freely reduced but cyclic-reduces standalone
    [2, 1, -2],                                 # ditto
    [1, 2, 1, 2, 1, 2, 1, 2],                   # long, no reduction
    [1, 2, -1, -2, 1, 2, -1, -2, 1, 2],         # long, freely reduced
    [-2, -1, 2, 1, -2, -1, 2, 1],               # long alternating
]


def _rand_freely_reduced(rng, length):
    """Random freely-reduced word over {+-1,+-2} of given length."""
    alpha = [1, -1, 2, -2]
    w = []
    while len(w) < length:
        c = rng.choice(alpha)
        if w and w[-1] == -c:
            continue
        w.append(c)
    return w


def test_A_stabilize(rec):
    rng = random.Random(20260705)
    for idx in TARGETS:
        base = list(hard_words.load_target(idx))
        rec.check(f"A.base_len[{idx}]", len(base) == 48,
                  f"len={len(base)}")
        r1_base, r2_base = relators_from_flat(base, 2)

        words = list(HAND_WORDS)
        # add r1, r2 as words, and randoms
        words.append(list(r1_base))
        words.append(list(r2_base))
        for ln in (3, 5, 8, 11):
            words.append(_rand_freely_reduced(rng, ln))

        for w in words:
            out = hard_words.stabilize_with_word(base, w)
            tag = f"idx={idx} w={w}"

            rec.check(f"A.len[{tag}]", len(out) == 72, f"len={len(out)}")
            if len(out) != 72:
                continue

            rels = relators_from_flat(out, 3)  # also asserts no interior zeros
            r1_out, r2_out, r3_out = rels

            # r1, r2 carried over unchanged
            rec.check(f"A.r1_unchanged[{tag}]", r1_out == r1_base,
                      f"{r1_out} != {r1_base}")
            rec.check(f"A.r2_unchanged[{tag}]", r2_out == r2_base,
                      f"{r2_out} != {r2_base}")

            # r3 equals my from-spec reference
            ref = ref_z_relator(w)
            rec.check(f"A.r3_matches_ref[{tag}]", r3_out == ref,
                      f"{r3_out} != {ref}")

            # alphabet: entries in {+-1,+-2,+-3}, no interior zeros (checked above)
            rec.check(f"A.r3_alphabet[{tag}]",
                      all(e in (-3, -2, -1, 1, 2, 3) for e in r3_out),
                      f"{r3_out}")

            # z-occurrence: exactly one +-3, it is +3 at index 0 (z . w^-1)
            n_z = sum(1 for e in r3_out if abs(e) == 3)
            if free_reduce(w):  # non-degenerate: w doesn't fully cancel
                rec.check(f"A.z_count_one[{tag}]", n_z == 1, f"n_z={n_z} r3={r3_out}")
                rec.check(f"A.z_is_plus_at_0[{tag}]",
                          len(r3_out) >= 1 and r3_out[0] == 3, f"r3={r3_out}")
                # interior after z is exactly inverse(free_reduce(w))
                rec.check(f"A.z_interior[{tag}]",
                          r3_out[1:] == inverse(free_reduce(w)),
                          f"{r3_out[1:]} != {inverse(free_reduce(w))}")
            else:
                # w fully cancels: z=identity, relator is just [z]
                rec.check(f"A.degenerate_z_only[{tag}]", r3_out == [3],
                          f"r3={r3_out}")

            # decode: recover w and confirm == free_reduce(w)
            # (NOTE: the invertible target is free_reduce(w), NOT cyclic_reduce(w):
            #  the leading z guards the wrap-around so the interior is NOT
            #  cyclically reduced at its own boundary. See report.)
            if r3_out and r3_out[0] == 3:
                w_rec = inverse(r3_out[1:])
                rec.check(f"A.decode_free[{tag}]", w_rec == free_reduce(w),
                          f"decoded {w_rec} != free_reduce {free_reduce(w)}")
                # cross-check the sanctioned helper decoder (strip padding)
                try:
                    helper = stabilize.decode_z_word(list(out[48:72]), 3)
                    helper_stripped = [e for e in helper if e != 0]
                    rec.check(f"A.decode_helper_agrees[{tag}]",
                              helper_stripped == w_rec,
                              f"helper {helper_stripped} != mine {w_rec}")
                except Exception as e:  # helper is a convenience; don't hard-fail suite
                    rec.note(f"decode_z_word raised on {tag}: {type(e).__name__}: {e}")

    # cross-check against the SECOND oracle stabilize.stabilize_flat for {x,y,r1,r2}
    for idx in TARGETS:
        base = list(hard_words.load_target(idx))
        r1_base, r2_base = relators_from_flat(base, 2)
        spec_word = {"x": [1], "y": [2], "r1": list(r1_base), "r2": list(r2_base)}
        for spec, w in spec_word.items():
            mine = hard_words.stabilize_with_word(base, w)
            other = stabilize.stabilize_flat(base, spec)
            rec.check(f"A.second_oracle[idx={idx},spec={spec}]",
                      list(mine) == list(other),
                      f"stabilize_with_word({spec}) != stabilize_flat('{spec}')\n"
                      f"      mine ={list(mine)}\n      other={list(other)}")


# =========================================================================
# B. build_word_bank_for invariants
# =========================================================================

def test_B_word_bank(rec):
    for idx in TARGETS:
        base = list(hard_words.load_target(idx))
        bank1 = hard_words.build_word_bank_for(base)
        bank2 = hard_words.build_word_bank_for(base)

        rec.check(f"B.nonempty[{idx}]", len(bank1) > 0, f"size={len(bank1)}")
        # "large" bank: a stabilization word bank should offer many candidates.
        rec.check(f"B.large[{idx}]", len(bank1) >= 40, f"size={len(bank1)}")

        # deterministic: two calls give the same bank (same words, same order)
        def sig(bank):
            return [tuple(d["w_ints"]) for d in bank]
        rec.check(f"B.deterministic[{idx}]", sig(bank1) == sig(bank2),
                  "two calls differ")

        seen_free = set()
        for i, d in enumerate(bank1):
            tag = f"idx={idx} #{i} name={d.get('name')}"
            w = list(d["w_ints"])

            # non-empty
            rec.check(f"B.w_nonempty[{tag}]", len(w) > 0, f"w={w}")
            # over {+-1,+-2} only -- NO z, no padding
            rec.check(f"B.w_alphabet[{tag}]",
                      all(e in (-2, -1, 1, 2) for e in w), f"w={w}")
            # freely reduced (no adjacent inverse pair)
            rec.check(f"B.w_freely_reduced[{tag}]", free_reduce(w) == w,
                      f"w={w} free_reduce={free_reduce(w)}")

            # dedup: no two entries share the same freely-reduced word
            key = tuple(free_reduce(w))
            rec.check(f"B.dedup[{tag}]", key not in seen_free,
                      f"duplicate free-reduced word {key}")
            seen_free.add(key)

            # z_relator == my reference; z_len consistent; fits the slot
            ref = ref_z_relator(w)
            rec.check(f"B.z_relator_ref[{tag}]", list(d["z_relator"]) == ref,
                      f"{list(d['z_relator'])} != {ref}")
            rec.check(f"B.z_len[{tag}]", d["z_len"] == len(list(d["z_relator"])),
                      f"z_len={d['z_len']} vs {len(list(d['z_relator']))}")
            rec.check(f"B.z_fits[{tag}]", d["z_len"] <= L, f"z_len={d['z_len']}")
            rec.check(f"B.w_len[{tag}]", d["w_len"] == len(w),
                      f"w_len={d['w_len']} vs {len(w)}")

            # w_str decodes back to w_ints
            rec.check(f"B.w_str[{tag}]", parse_word(d["w_str"]) == w,
                      f"parse({d['w_str']})={parse_word(d['w_str'])} != {w}")

            # bank is self-consistent with the transform
            out = hard_words.stabilize_with_word(base, w)
            r3 = relators_from_flat(out, 3)[2]
            rec.check(f"B.bank_selfconsistent[{tag}]",
                      r3 == list(d["z_relator"]),
                      f"stabilize r3 {r3} != bank z_relator {list(d['z_relator'])}")


# =========================================================================
# C. _relhalf_for invariants
# =========================================================================

def test_C_relhalf(rec):
    for idx in TARGETS:
        base = list(hard_words.load_target(idx))
        r1, r2 = relators_from_flat(base, 2)
        parts = hard_words._relhalf_for(list(r1), list(r2))

        rec.check(f"C.nonempty[{idx}]", len(parts) > 0, f"parts={parts}")

        inv_r1, inv_r2 = inverse(r1), inverse(r2)
        for j, item in enumerate(parts):
            # each item is a (family_name, word_string) tuple
            rec.check(f"C.tuple_shape[idx={idx} #{j}]",
                      isinstance(item, (tuple, list)) and len(item) == 2,
                      f"item={item}")
            fam, wstr = item[0], item[1]
            rec.check(f"C.family_str[idx={idx} #{j}]", isinstance(fam, str),
                      f"family={fam!r}")
            rec.check(f"C.word_str[idx={idx} #{j}]", isinstance(wstr, str),
                      f"wstr={wstr!r}")
            w = parse_word(wstr)
            tag = f"idx={idx} #{j} '{wstr}'"

            fw = free_reduce(w)
            rec.check(f"C.nonempty_after_free[{tag}]", len(fw) > 0, f"w={w}")
            rec.check(f"C.alphabet[{tag}]",
                      all(e in (-2, -1, 1, 2) for e in w), f"w={w}")

            # genuinely a part of r1 or r2: the word (or its inverse) is a
            # contiguous cyclic subword of r1 or r2, OR is the inverse of a
            # relator.  (inverse-of-relator is subsumed by cyclic-subword of a
            # relator applied to inverse(w), but we keep both clauses explicit.)
            iw = inverse(w)
            derived = (
                is_cyclic_subword(w, r1) or is_cyclic_subword(w, r2) or
                is_cyclic_subword(iw, r1) or is_cyclic_subword(iw, r2) or
                w == inv_r1 or w == inv_r2
            )
            if not derived:
                # fallback: try the free-reduced forms (in case a part carried a
                # reducible boundary); still must trace back to a relator.
                derived = (
                    is_cyclic_subword(fw, r1) or is_cyclic_subword(fw, r2) or
                    is_cyclic_subword(free_reduce(iw), r1) or
                    is_cyclic_subword(free_reduce(iw), r2)
                )
            rec.check(f"C.derived_from_relator[{tag}]", derived,
                      f"w={w} not a cyclic subword of r1={r1} or r2={r2} "
                      f"nor inverse of a relator")


# =========================================================================
# main
# =========================================================================

def main():
    rec = Recorder()
    print("=== hard_words independent black-box test suite ===")
    print(f"module under test: {hard_words.__file__}")
    print(f"second oracle:     {stabilize.__file__}")
    print()

    print("[0] self-check of my own oracle primitives")
    _self_check_primitives(rec)
    print("[A] stabilize_with_word invariants")
    test_A_stabilize(rec)
    print("[B] build_word_bank_for invariants")
    test_B_word_bank(rec)
    print("[C] _relhalf_for invariants")
    test_C_relhalf(rec)

    print()
    print(f"targets exercised: {TARGETS}")
    print(f"checks passed: {rec.passed}")
    print(f"checks failed: {rec.failed}")
    if rec.notes:
        print("notes:")
        for n in rec.notes:
            print("  -", n)
    if rec.failed:
        print()
        print(f"RESULT: FAIL ({rec.failed} failing checks)")
        # print first few distinct failing names
        seen = set()
        for name, detail in rec.failures:
            base = name.split("[")[0]
            if base not in seen:
                seen.add(base)
                print(f"  first fail of {base}: {name}  {detail[:200]}")
        sys.exit(1)
    else:
        print()
        print("RESULT: PASS (all checks green)")
        sys.exit(0)


if __name__ == "__main__":
    main()
