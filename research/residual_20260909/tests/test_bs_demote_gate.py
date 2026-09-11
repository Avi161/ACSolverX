"""Tests for research/residual_20260909/bs_demote_gate.py.

Run with:
    PYTHONPATH=. python3 -m pytest research/residual_20260909/tests/test_bs_demote_gate.py -q

Every planted positive is decoded with
``certificate_decoder_compact_moves.decode_elementary`` and replayed with
``certificate_decoder.replay_elementary`` to literal ``['x', 'y']``.
Only *solved* census rows and the dev row ac19_102 are named; every other
input is planted, so the hidden val/test panels are never touched.
"""
import pytest

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_pair, canon_pair, canon_rel, inv, rot,
)
from research.residual_20260909.bs_demote_gate import (
    complete, demotable, is_doomed_bs_state, normalise, predicted_work, recognize,
)
from research.residual_20260909.theory.bs_normal_form import word_from
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary


def relator(m):
    """The consecutive-BS donor b^-1 a^m b a^-(m+1) with (a, b) = (x, y)."""
    return canon_rel("Y" + "x" * m + "y" + "X" * (m + 1))


def companion(eps, gaps):
    return canon_rel(word_from([eps, eps, -eps], list(gaps), "x", "y"))


def planted(m, eps, gaps, swap=False):
    words = (relator(m), companion(eps, gaps))
    return canon_pair(*(reversed(words) if swap else words))


def moduli(m, eps):
    return (m + 1, m) if eps == 1 else (m, m + 1)


# (m, eps, gaps) triples in the demotable class (m, 1, m-1), all genuinely
# stalled.  The two gap triples (0, 1, -1) and (0, -1, 1) are excluded on
# purpose: those companions ARE the BS(1,2) relator, so the frozen
# bs_gate + bs_preflight terminal already accepts them and the gate correctly
# declines (ALREADY_ACCEPTED below).
POSITIVES = []
for _m in (2, 3, 4, 5, 6, 7):
    for _eps in (1, -1):
        _Mv, _Mw = moduli(_m, _eps)
        POSITIVES.append((_m, _eps, (0, 1 + _Mv, -1)))              # one carry away in v
        POSITIVES.append((_m, _eps, (0, 1, -1 - _Mw)))              # one carry away in w
        POSITIVES.append((_m, _eps, (2, 1 - _Mv, _Mw - 1)))         # u shifted, other rep
        POSITIVES.append((_m, _eps, (-1, 1, -1)))                   # u = -1
        POSITIVES.append((_m, _eps, (0, -1 - _Mv, 1)))              # the mirror class

ALREADY_ACCEPTED = [(m, eps, gaps)
                    for m in (2, 3, 5) for eps in (1, -1)
                    for gaps in ((0, 1, -1), (0, -1, 1))]

# labels outside (m, 1, m-1), stalled but not demotable ---------------------
NEGATIVE_CLASSES = [
    (3, 1, (0, 2, 1)), (4, 1, (0, 2, 2)), (4, 1, (0, 1, 2)), (5, 1, (0, 2, 3)),
    (5, 1, (0, 4, 1)), (5, -1, (0, 2, 4)), (6, 1, (0, 3, 4)), (7, 1, (0, 3, 3)),
    (7, -1, (0, 5, 2)), (5, 1, (0, -2, 1)),
]

# wider stalled necklaces: s_red = 5 and s_red = 7 -------------------------
# Both s = 5 necklaces and both s = 7 necklaces over m = 2, each verified
# below to be stalled with the full stable count (so the necklace obstruction
# of STALLED_BS_THEORY.md 5.5 is what makes the gate decline, not a pinch).
def _wide(signs, gaps, m=2):
    return canon_pair(relator(m), canon_rel(word_from(signs, list(gaps), "x", "y")))


WIDE_NECKLACES = [
    ("s5_a", _wide([1, 1, -1, 1, -1], (-2, -2, -1, -2, -1)), 5),
    ("s5_b", _wide([1, 1, 1, -1, -1], (-2, -2, -2, -2, -1)), 5),
    ("s7_a", _wide([1, 1, -1, 1, -1, 1, -1], (-2, -2, -1, -2, -1, -2, -1)), 7),
    ("s7_b", _wide([1, 1, 1, -1, 1, -1, -1], (-2, -2, -2, -1, -2, -2, -1)), 7),
]

# near misses --------------------------------------------------------------
NEAR_MISSES = [
    # stable exponent +/-2: the BS gate itself refuses
    ("exp2", canon_pair(relator(3), canon_rel("yyxYYxxx"))),
    # exponent 0
    ("exp0", canon_pair(relator(3), canon_rel("yxYxxx"))),
    # pinchable companion (v divisible by M_v): not stalled at all
    ("pinchable_v", planted(3, 1, (0, 4, 1))),
    ("pinchable_w", planted(3, 1, (0, 1, 3))),
    # m = 1 has no stalled class
    ("m1", planted(1, 1, (0, 1, 1))),
    # no consecutive-BS relator at all
    ("no_bs", canon_pair("xyxYXY", "xxyy")),
    ("two_block", canon_pair("xxy", "xyy")),
]


# --------------------------------------------------------------------------
# recognition
# --------------------------------------------------------------------------

@pytest.mark.parametrize("m,eps,gaps", POSITIVES)
def test_recognize_positive_label(m, eps, gaps):
    label = recognize(planted(m, eps, gaps))
    assert label == (m, 1, m - 1)
    assert demotable(label)


@pytest.mark.parametrize("m,eps,gaps", POSITIVES[:12])
def test_recognition_is_order_invariant(m, eps, gaps):
    assert recognize(planted(m, eps, gaps)) == recognize(planted(m, eps, gaps, swap=True))


@pytest.mark.parametrize("m,eps,gaps", POSITIVES[:12] + NEGATIVE_CLASSES[:6])
def test_recognition_is_rotation_inversion_swap_invariant(m, eps, gaps):
    base = planted(m, eps, gaps)
    expected = recognize(base)
    r1, r2 = base
    for k1 in range(len(r1)):
        for k2 in range(len(r2)):
            for first in (rot(r1, k1), inv(rot(r1, k1))):
                for second in (rot(r2, k2), inv(rot(r2, k2))):
                    assert recognize(canon_pair(first, second)) == expected
                    assert recognize(canon_pair(second, first)) == expected


@pytest.mark.parametrize("m,eps,gaps", POSITIVES[:10] + NEGATIVE_CLASSES[:4])
def test_label_is_constant_on_the_relabelling_orbit(m, eps, gaps):
    base = planted(m, eps, gaps)
    expected = recognize(base)
    for _name, image in SIGNED_PERMS:
        assert recognize(apply_pair(base, image)) == expected


@pytest.mark.parametrize("m,eps,gaps", NEGATIVE_CLASSES)
def test_recognize_negative_class_is_labelled_but_not_demotable(m, eps, gaps):
    label = recognize(planted(m, eps, gaps))
    assert label is not None and label[0] == m
    assert not demotable(label)


@pytest.mark.parametrize("name,pair,expected",
                         WIDE_NECKLACES + [(n, p, None) for n, p in NEAR_MISSES])
def test_recognize_returns_none_off_the_s3_family(name, pair, expected):
    from research.supermoves_20260908.bs_preflight import preflight
    assert recognize(pair) is None
    if expected is not None:
        check = preflight(pair)
        assert check["status"] == "reject" and check["stable_letters"] == expected


@pytest.mark.parametrize("m,eps,gaps", ALREADY_ACCEPTED)
def test_demotion_word_is_already_a_frozen_terminal(m, eps, gaps):
    """The gate declines the BS(1,2) companion: bs_preflight already accepts."""
    from research.supermoves_20260908.bs_preflight import preflight
    pair = planted(m, eps, gaps)
    assert preflight(pair)["status"] == "accept"
    assert recognize(pair) is None
    result = complete(pair, budget=100_000)
    assert result["solved"] is False and result["work"] <= 2


def test_dev_row_ac19_102_is_recognised_but_not_demotable():
    label = recognize(canon_pair("YYXXyx", "YXXXXXXyxxxxx"))
    assert label == (5, 2, 4)
    assert not demotable(label)


# --------------------------------------------------------------------------
# completion: positives
# --------------------------------------------------------------------------

def _check_certificate(pair, result):
    assert result["solved"] is True
    states, steps = result["states"], result["steps"]
    assert states[0] == list(canon_pair(*pair))
    assert len(states) == len(steps) + 1
    assert all(step["kind"] == "substitution" for step in steps)
    terminal = states[-1]
    assert len(terminal[0]) == len(terminal[1]) == 1
    assert terminal[0].lower() != terminal[1].lower()
    moves = decode_elementary(list(pair), states, steps, result["elementary_tail"])
    assert replay_elementary(list(pair), moves) == ["x", "y"]
    return len(moves)


@pytest.mark.parametrize("m,eps,gaps", POSITIVES)
@pytest.mark.parametrize("swap", (False, True))
def test_complete_certifies_and_replays(m, eps, gaps, swap):
    pair = planted(m, eps, gaps, swap=swap)
    result = complete(pair, budget=100_000)
    elementary = _check_certificate(pair, result)
    assert result["work"] == predicted_work(pair)
    assert result["collapse_rewrites"] == 1 << (m + 1)
    assert elementary > 0


@pytest.mark.parametrize("pair", [
    canon_pair("YYXXyx", "YXXXyxx"),        # solved census row ac19_42, class (2,1,1)
    canon_pair("YYXXXyxx", "YXXXXyxxx"),    # solved census row ac19_73, class (3,1,2)
])
def test_complete_on_solved_census_rows(pair):
    result = complete(pair, budget=100_000)
    _check_certificate(pair, result)


def test_work_is_exactly_the_number_of_emitted_moves_plus_two():
    pair = planted(4, 1, (0, 1, 3))
    result = complete(pair, budget=100_000)
    assert result["work"] == 2 + len(result["steps"])
    assert result["work"] == (2 + result["pinch_carries"] + result["transport_carries"]
                              + result["collapse_rewrites"])


# --------------------------------------------------------------------------
# completion: negatives all cost at most 2 units
# --------------------------------------------------------------------------

@pytest.mark.parametrize("m,eps,gaps", NEGATIVE_CLASSES)
def test_complete_refuses_wrong_class_cheaply(m, eps, gaps):
    result = complete(planted(m, eps, gaps), budget=100_000)
    assert result["solved"] is False
    assert result["work"] <= 2
    assert result["reason"] == "class_not_demotable"
    assert "states" not in result


@pytest.mark.parametrize("name,pair", [(n, p) for n, p, _s in WIDE_NECKLACES]
                                      + NEAR_MISSES)
def test_complete_refuses_off_family_cheaply(name, pair):
    result = complete(pair, budget=100_000)
    assert result["solved"] is False
    assert result["work"] <= 2
    assert result["reason"] == "not_recognized"


def test_complete_refuses_the_dev_row_cheaply():
    result = complete(canon_pair("YYXXyx", "YXXXXXXyxxxxx"), budget=100_000)
    assert result["solved"] is False and result["work"] <= 2


# --------------------------------------------------------------------------
# budget discipline
# --------------------------------------------------------------------------

@pytest.mark.parametrize("m,eps,gaps", POSITIVES[:10])
def test_small_budget_refuses_without_emitting(m, eps, gaps):
    pair = planted(m, eps, gaps)
    needed = predicted_work(pair)
    result = complete(pair, budget=needed - 1)
    assert result["solved"] is False
    assert result["work"] <= 2
    assert result["reason"] == "budget"
    assert complete(pair, budget=needed)["solved"] is True


def test_budget_never_exceeded():
    pair = planted(5, 1, (0, 1, 4))
    for budget in range(1, 90):
        result = complete(pair, budget=budget)
        assert result["work"] <= budget


@pytest.mark.parametrize("budget", (0, -1, 2.5, True))
def test_bad_budget_rejected(budget):
    with pytest.raises(ValueError):
        complete(planted(2, 1, (0, 1, 1)), budget=budget)


# --------------------------------------------------------------------------
# BS-NORMALISE
# --------------------------------------------------------------------------

@pytest.mark.parametrize("m,eps,gaps", POSITIVES[:10] + NEGATIVE_CLASSES[:6])
def test_normalise_is_a_valid_ac_prefix(m, eps, gaps):
    from experiments.equivalence_classes.lib.words import replay_move
    pair = planted(m, eps, gaps)
    built = normalise(pair, budget=100_000)
    assert built["applicable"] is True
    state = tuple(built["states"][0])
    assert list(state) == list(canon_pair(*pair))
    for step, nxt in zip(built["steps"], built["states"][1:]):
        state = replay_move(state, tuple(int(v) for v in step["move"].split("_")))
        assert list(state) == list(nxt)
    assert list(state) == built["normal_state"]
    # the normal form is in the same class; for the demotable classes with a
    # short representative it IS the BS(1,2) word, which the frozen terminal
    # already accepts and which the gate therefore no longer calls "stalled".
    from research.supermoves_20260908.bs_preflight import preflight
    normal = tuple(built["normal_state"])
    assert (recognize(normal) == built["label"]
            or preflight(normal)["status"] == "accept")


def test_same_label_reaches_a_common_normal_form():
    """ac19_102 (dev) and a planted partner in class (5,2,4)."""
    dev = canon_pair("YYXXyx", "YXXXXXXyxxxxx")
    label = recognize(dev)
    goal = tuple(normalise(dev, budget=100_000)["normal_state"])
    partner = planted(5, 1, (3, label[1] + 6, label[2] + 5))
    hits = []
    for name, image in SIGNED_PERMS:
        moved = apply_pair(partner, image)
        if recognize(moved) != label:
            continue
        if tuple(normalise(moved, budget=100_000)["normal_state"]) == goal:
            hits.append(name)
    assert hits, "no relabelling carries the partner onto the dev normal form"


def test_normalise_never_lengthens_the_companion():
    for m, eps, gaps in POSITIVES[:10] + NEGATIVE_CLASSES:
        pair = planted(m, eps, gaps)
        built = normalise(pair, budget=100_000)
        assert sum(map(len, built["normal_state"])) <= sum(map(len, pair))


# --------------------------------------------------------------------------
# is_doomed_bs_state
# --------------------------------------------------------------------------

def test_is_doomed_on_w_only_descendants():
    from experiments.equivalence_classes.lib.words import replay_move
    from research.supermoves_20260908.bs_preflight import preflight
    root = planted(5, 1, (0, 2, 3))          # stalled, class (5,2,3)
    assert is_doomed_bs_state(root, root)
    assert preflight(root)["status"] == "reject"
    built = normalise(root, budget=100_000)
    for state in built["states"]:
        assert is_doomed_bs_state(root, tuple(state))
        assert preflight(tuple(state))["status"] == "reject"
    # every single W-move child of the root is doomed, and preflight agrees
    donor_index = 0 if len(root[0]) > len(root[1]) else 1
    target = 2 - donor_index
    seen = 0
    for jsign in (1, -1):
        for k1 in range(len(root[target - 1])):
            for k2 in range(len(root[2 - target])):
                child = replay_move(root, (target, jsign, k1, k2))
                if is_doomed_bs_state(root, child):
                    assert preflight(child)["status"] == "reject"
                    seen += 1
    assert seen > 0


def test_is_doomed_requires_the_w_only_hypothesis():
    root = planted(5, 1, (0, 2, 3))
    assert is_doomed_bs_state(root, root, w_only=False) is False


def test_is_doomed_false_off_the_stalled_family():
    pinchable = planted(3, 1, (0, 4, 1))
    assert is_doomed_bs_state(pinchable, pinchable) is False
    assert is_doomed_bs_state(canon_pair("xxy", "xyy"), canon_pair("xxy", "xyy")) is False


def test_is_doomed_false_once_the_root_relator_is_gone():
    root = planted(5, 1, (0, 2, 3))
    assert is_doomed_bs_state(root, canon_pair("xxy", "xyy")) is False
