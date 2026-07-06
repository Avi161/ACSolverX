"""Independent, adversarial black-box tests for `ak3_words.py`.

`ak3_words.py` is treated strictly as a BLACK BOX here: this file only calls its
public functions (`parse`, `to_str`, `stabilize_with_word`, `z_relator_for`,
`build_word_bank`, `AK3_TEXTBOOK`, `AK3_REP`) and never reads or mirrors its
internal logic.

Independence ladder used below (each test says which rung it sits on):
  (a) MY OWN oracle -- `my_inverse` / `my_free_reduce` / `my_cyclic_reduce` /
      `my_z_relator`, written here from scratch against the math contract in
      the task spec (z-relator = `z * w^-1`, freely + cyclically reduced).
  (b) differential vs `stabilize.py` -- a second, independent, pre-existing
      implementation of the SAME transform (shipped for the four named specs
      x/y/r1/r2). Used both as a source to confirm the sign/direction
      convention and as a byte-for-byte differential oracle.
  (c) structural/invariant checks that hold by the math regardless of any
      particular implementation (leading `z` can never cancel, output must
      already be reduced, length cap, etc).

Run:
    cd <repo root>
    PYTHONPATH="experiments/stable_ac/one_generator" python3 -m pytest \
        tests/ak3_words_independent_test.py -q

or, if pytest isn't installed (it wasn't, in this environment):
    PYTHONPATH="experiments/stable_ac/one_generator" python3 \
        tests/ak3_words_independent_test.py
"""
import ast
import os
import random
import sys

_ONE_GEN_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "experiments", "stable_ac", "one_generator",
)
if _ONE_GEN_DIR not in sys.path:
    sys.path.insert(0, _ONE_GEN_DIR)

import ak3_words as ak3   # noqa: E402  -- module under test, BLACK BOX
import stabilize as ship  # noqa: E402  -- independent, pre-existing reference impl

L = 24
ALPHABET = (1, -1, 2, -2)
CHAR_OF = {1: "x", -1: "X", 2: "y", -2: "Y"}
INT_OF = {v: k for k, v in CHAR_OF.items()}


# ==========================================================================
# MY OWN oracle -- from scratch, from the math contract. Deliberately does
# NOT import anything from ak3_words.
# ==========================================================================

def my_parse(s):
    return [INT_OF[c] for c in s]


def my_to_str(w):
    return "".join(CHAR_OF[a] for a in w)


def my_inverse(w):
    return [-a for a in reversed(w)]


def my_free_reduce(w):
    out = []
    for a in w:
        if out and out[-1] == -a:
            out.pop()
        else:
            out.append(a)
    return out


def my_cyclic_reduce(w):
    w = my_free_reduce(w)
    i, j = 0, len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return w[i:j + 1]


def my_z_relator(w, k=3):
    """z * w^-1, freely + cyclically reduced -- the Lemma-11 stabilization relator."""
    return my_cyclic_reduce([k] + my_inverse(w))


def my_decode_z_word(z_relator, k=3):
    if not z_relator or z_relator[0] != k:
        raise ValueError(f"z-relator does not start with z={k}: {z_relator}")
    return my_inverse(z_relator[1:])


def is_freely_reduced(w):
    return all(w[i] != -w[i + 1] for i in range(len(w) - 1))


def strip_zeros(relator_slice):
    return [a for a in relator_slice if a != 0]


def random_reduced_word(rng, length):
    """A freely-reduced random word over {x,X,y,Y} of exactly `length` letters."""
    w = []
    while len(w) < length:
        a = rng.choice(ALPHABET)
        if w and w[-1] == -a:
            continue
        w.append(a)
    return w


def relator_ints(flat, which, half=L):
    start = which * half
    return [a for a in flat[start:start + half] if a != 0]


# ==========================================================================
# 1. Encoding round-trip
# ==========================================================================

def test_1_encoding_roundtrip_property():
    rng = random.Random(20260705)
    for _ in range(500):
        length = rng.randint(0, 30)
        w = random_reduced_word(rng, length)
        s = my_to_str(w)
        assert ak3.to_str(w) == s, (w, s, ak3.to_str(w))
        assert ak3.parse(s) == w, (s, w, ak3.parse(s))
        assert ak3.parse(s) == my_parse(s), s


def test_1_encoding_explicit_cases():
    assert ak3.parse("") == []
    assert ak3.to_str([]) == ""
    assert ak3.parse("xyxYXY") == [1, 2, 1, -2, -1, -2]
    assert ak3.to_str([1, 2, 1, -2, -1, -2]) == "xyxYXY"
    # parse is a pure char<->int bijection, NOT a reducer: unreduced input
    # round-trips unreduced too (documented behavior, not a bug).
    assert ak3.parse("xX") == [1, -1]
    assert ak3.to_str(ak3.parse("xX")) == "xX"


# ==========================================================================
# 2. Prefix invariant: r1/r2 (the original flat) must survive untouched.
# ==========================================================================

def test_2_prefix_invariant():
    rng = random.Random(1)
    for flat in (ak3.AK3_TEXTBOOK, ak3.AK3_REP):
        for _ in range(150):
            w = random_reduced_word(rng, rng.randint(1, 8))  # stay well under cap
            out = ak3.stabilize_with_word(flat, w)
            assert len(out) == 72
            assert out[:48] == flat, (w, out[:48], flat)


# ==========================================================================
# 3. z-relator correctness -- rung (a): MY OWN oracle.
# ==========================================================================

def test_3_z_relator_matches_own_oracle_property():
    rng = random.Random(2)
    for _ in range(500):
        length = rng.randint(1, 20)
        w = random_reduced_word(rng, length)
        expected = my_z_relator(w)
        got = ak3.z_relator_for(w)
        assert got == expected, (w, expected, got)


def test_3_z_relator_edge_cases_own_oracle():
    cases = [
        [1],                       # length-1 word
        [-1],
        [2],
        [-2],
        [1, 2, 1, -2],             # ends in a letter that could tempt interaction w/ z=3
        [1, -1, 2],                # already contains a cancelling pair
        [2, 2, 1, -1, -1],         # multiple internal cancellations
        [1, 1, 2, -2, -1, -1],     # nested cancellation: reduces all the way to []
        [1] * 20,                  # long, non-cancelling (z-len 21, under cap)
        [1, 2, -2, -1, 1, 2],      # reduces a lot (bare word -> [1, 2])
    ]
    for w in cases:
        expected = my_z_relator(w)
        got = ak3.z_relator_for(w)
        assert got == expected, (w, expected, got)


def test_3_z_relator_matches_shipped_reducer_too():
    """Second, independent rung: cross-check with stabilize.py's free/cyclic
    reducers (a pre-existing, separately-authored implementation) that
    ak3.z_relator_for(w) is exactly `cyclic_reduce([3] + inverse(w))` and is
    already in canonical (idempotent) reduced form."""
    rng = random.Random(7)
    for _ in range(300):
        w = random_reduced_word(rng, rng.randint(0, 20))
        z = ak3.z_relator_for(w)
        assert ship.cyclic_reduce(z) == z, (w, z)
        assert ship.free_reduce(z) == z, (w, z)
        assert ship.cyclic_reduce([3] + ship.inverse(w)) == z, (w, z)


# ==========================================================================
# 4. Round-trip decode: dropping leading z and inverting recovers w (up to
#    free/cyclic reduction). Cross-checked against MY OWN decoder and
#    stabilize.decode_z_word.
# ==========================================================================

def test_4_decode_recovers_w_up_to_reduction_property():
    rng = random.Random(3)
    for _ in range(300):
        w = random_reduced_word(rng, rng.randint(1, 15))
        z = ak3.z_relator_for(w)
        assert z[0] == 3, (w, z)
        expected = my_cyclic_reduce(w)
        decoded_mine = my_cyclic_reduce(my_decode_z_word(z))
        decoded_ship = ship.cyclic_reduce(ship.decode_z_word(z, 3))
        assert decoded_mine == expected, (w, z, decoded_mine, expected)
        assert decoded_ship == expected, (w, z, decoded_ship, expected)


def test_4_decode_via_stabilize_with_word_tail():
    rng = random.Random(4)
    for _ in range(150):
        w = random_reduced_word(rng, rng.randint(1, 10))
        out = ak3.stabilize_with_word(ak3.AK3_TEXTBOOK, w)
        z = strip_zeros(out[48:])
        assert z == ak3.z_relator_for(w), (w, z)
        decoded = ship.cyclic_reduce(ship.decode_z_word(z, 3))
        assert decoded == my_cyclic_reduce(w), (w, z, decoded)


# ==========================================================================
# 5. Differential vs shipped reference (strongest rung): for w = the
#    presentation's own r1/r2, stabilize_with_word must byte-equal
#    stabilize.stabilize_flat(..., "r1"/"r2").
# ==========================================================================

def test_5_differential_vs_shipped_r1_r2():
    for flat in (ak3.AK3_TEXTBOOK, ak3.AK3_REP):
        r1 = relator_ints(flat, 0)
        r2 = relator_ints(flat, 1)
        for spec, w in (("r1", r1), ("r2", r2)):
            got = ak3.stabilize_with_word(flat, w)
            want = ship.stabilize_flat(flat, spec)
            assert got == want, (spec, flat, got, want)
            assert len(got) == 72


# ==========================================================================
# 6. Length cap: no unpadded overflow, ever, in what actually ships (the
#    word bank); and stabilize_with_word must refuse to silently truncate.
# ==========================================================================

def test_6_length_cap_word_bank():
    bank = ak3.build_word_bank()
    assert len(bank) > 0
    for d in bank:
        assert len(d["z_relator"]) <= L, d
        assert d["z_len"] == len(d["z_relator"]), d


def test_6_length_cap_boundary_property():
    rng = random.Random(5)
    for _ in range(300):
        length = rng.randint(1, 30)
        w = random_reduced_word(rng, length)
        true_len = len(my_z_relator(w))
        if true_len <= L:
            out = ak3.stabilize_with_word(ak3.AK3_TEXTBOOK, w)
            assert len(strip_zeros(out[48:])) == true_len, (w, true_len)
        else:
            try:
                ak3.stabilize_with_word(ak3.AK3_TEXTBOOK, w)
                raise AssertionError(
                    f"expected ValueError for overflow w={w} (z-len {true_len} > {L})"
                )
            except ValueError:
                pass


# ==========================================================================
# 7. Word-bank invariants.
# ==========================================================================

def test_7_word_bank_invariants():
    bank = ak3.build_word_bank()
    seen_words = set()
    seen_z = set()
    for d in bank:
        w = d["w_ints"]
        assert len(w) > 0, d
        assert all(a in ALPHABET for a in w), d
        assert is_freely_reduced(w), ("word not freely reduced", d)
        assert d["w_len"] == len(w), d
        assert d["w_str"] == my_to_str(w), d
        assert d["name"] == d["w_str"], d
        assert ak3.to_str(w) == d["w_str"], d
        assert ak3.parse(d["w_str"]) == w, d
        expected_z = my_z_relator(w)
        assert d["z_relator"] == expected_z, (d, expected_z)
        assert d["z_len"] == len(expected_z) <= L, d

        wkey = tuple(w)
        assert wkey not in seen_words, ("duplicate w_ints in word bank", d)
        seen_words.add(wkey)

        zkey = tuple(d["z_relator"])
        assert zkey not in seen_z, ("duplicate z_relator in word bank", d)
        seen_z.add(zkey)


# ==========================================================================
# 8. Form identity.
# ==========================================================================

def test_8_form_identity():
    def decode_flat(flat):
        r1 = strip_zeros(flat[:L])
        r2 = strip_zeros(flat[L:2 * L])
        return my_to_str(r1), my_to_str(r2)

    assert decode_flat(ak3.AK3_REP) == ("YXyXYx", "YYYXXXX"), decode_flat(ak3.AK3_REP)
    assert decode_flat(ak3.AK3_TEXTBOOK) == ("xyxYXY", "xxxYYYY"), decode_flat(ak3.AK3_TEXTBOOK)


def test_8_ak3_rep_matches_dataset_line0():
    data_path = os.path.join(
        _ONE_GEN_DIR, "..", "..", "..", "data", "ms_unsolved_reps", "ms_reps_unsolved.txt"
    )
    data_path = os.path.abspath(data_path)
    with open(data_path) as f:
        first_line = f.readline().strip()
    first_flat = ast.literal_eval(first_line)
    assert first_flat == ak3.AK3_REP, (first_flat, ak3.AK3_REP)


# ==========================================================================
# 9. Adversarial hunt.
# ==========================================================================

def test_9_overflow_word_stabilize_raises_but_raw_helper_does_not():
    """A word that would push the z-relator past L=24.

    Documents an asymmetry (not necessarily a bug): `stabilize_with_word`
    enforces the L=24 cap and raises ValueError; the raw `z_relator_for`
    helper does not enforce any cap by itself (build_word_bank is what
    length-filters, per its own docstring)."""
    w = [1] * 24  # non-cancelling -> z-relator length 25 > L
    z = ak3.z_relator_for(w)
    assert len(z) == 25 == len(my_z_relator(w))
    try:
        ak3.stabilize_with_word(ak3.AK3_TEXTBOOK, w)
        raise AssertionError("expected ValueError: stabilize_with_word must enforce L=24 cap")
    except ValueError:
        pass


def test_9_leading_z_can_never_cancel_and_output_is_reduced():
    rng = random.Random(6)
    words = [[], [1], [-1], [2], [-2]]
    words += [random_reduced_word(rng, rng.randint(0, 25)) for _ in range(500)]
    for w in words:
        z = ak3.z_relator_for(w)
        assert z, (w, z)
        assert z[0] == 3, ("leading z was cancelled away!", w, z)
        assert is_freely_reduced(z), ("z-relator not freely reduced", w, z)
        if len(z) > 1:
            # cyclic reduction: front/back must not be inverses of each other.
            # Structurally guaranteed since w only uses +-1/+-2, so -3 can
            # never appear in z -- this asserts that guarantee holds.
            assert z[0] != -z[-1], ("z-relator not cyclically reduced", w, z)


def test_9_non_reduced_input_word_still_yields_reduced_output():
    """w itself need not be freely reduced -- verify the transform still
    produces a canonical (fully reduced) z-relator, including a word that
    free-reduces all the way down to the empty word."""
    cases = [
        [1, -1, 2],
        [1, 1, 2, -2, -1, -1],   # free_reduce(w) == [] entirely
        [2, -2, 1, -1],          # free_reduce(w) == [] entirely
        [1, 2, -2, -1, 1, 2],
    ]
    for w in cases:
        z = ak3.z_relator_for(w)
        assert is_freely_reduced(z), (w, z)
        assert z == my_z_relator(w), (w, z, my_z_relator(w))
        assert z == ship.cyclic_reduce([3] + ship.inverse(w)), (w, z)


def test_9_empty_word_degenerate_behavior():
    """w = [] : z * w^-1 collapses to the bare new generator z=3.
    Documents this rather than asserting it's forbidden -- an empty word is
    a degenerate ("z is trivial") case, distinct from the discarded trivial
    z that the docstring in stabilize.py explicitly wants to avoid; here it
    only matters if it's ever accidentally selected as a word-bank entry
    (test_7 already asserts every w_ints is nonempty)."""
    assert ak3.z_relator_for([]) == [3]
    out = ak3.stabilize_with_word(ak3.AK3_TEXTBOOK, [])
    assert strip_zeros(out[48:]) == [3]
    assert out[:48] == ak3.AK3_TEXTBOOK
    assert ak3.parse("") == []
    assert ak3.to_str([]) == ""


# ==========================================================================
# Runner (works with or without pytest).
# ==========================================================================

def _all_tests():
    return [
        (name, obj) for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]


if __name__ == "__main__":
    passed = 0
    failed = []
    for name, fn in _all_tests():
        try:
            fn()
            passed += 1
            print(f"PASS  {name}")
        except AssertionError as e:
            failed.append((name, e))
            print(f"FAIL  {name}: {e}")
        except Exception as e:  # noqa: BLE001
            failed.append((name, e))
            print(f"ERROR {name}: {type(e).__name__}: {e}")

    total = passed + len(failed)
    print(f"\n{passed}/{total} passed")
    if failed:
        print("\nFailures:")
        for name, e in failed:
            print(f"  {name}: {e}")
        sys.exit(1)
