"""acx.cov: the family, the certificate checker, CoV-then-search and its typed outcomes.

The reference numbers of the family (AK(3): 34 images; the worked example) are those
of ``origin/cov/all-subsets-sweep:experiments/stable_ac/cov``. The bench60 numbers
are a golden regression (fast backend, so the test is skipped without it); the same
numbers on spec follow from the spec/fast parity of ``tests/test_fast.py``.
"""
import json

import pytest

from acx import data
from acx.aut import orbit_key
from acx.core.config import SearchConfig
from acx.core.moves import decode_path, encode_path
from acx.core.words import Presentation, parse
from acx.cov import CoVConfig, ReplayError, apply_steps, check_cert, enumerate_images, verify
from acx.cov.cov import Z, relabel, subwords, substitute
from acx.cov.run import run
from acx.search import BackendUnavailable, search
from acx.search.engine import backend as load_backend
from acx.verify import replay

AK3 = Presentation.parse("xyxYXY", "xxxYYYY")
# Planted: built from the trivial T = <x, y | xYX, xYxYX> by running a CoV backwards (T is the image of
# P under z = Xyy, eliminating x), so P has an image that a search solves in 3 pops. T is not in P's Aut orbit.
PLANTED = Presentation.parse("xxYYxYX", "yyxYYxYXY")
PLANTED_IMAGE = Presentation.parse("xYX", "xYxYX")


def fast_available():
    try:
        load_backend("fast")
        return True
    except BackendUnavailable:
        return False


needs_fast = pytest.mark.skipif(not fast_available(), reason="fast backend not available")


def test_substitute():
    assert substitute(parse("yxxy"), parse("yy")) == ((Z, 1, 1), 1)          # only the seam match
    assert substitute(parse("yxxy"), parse("xy")) == ((2, 1, Z), 1)          # linear hit; the seam yy is no w
    assert substitute(parse("xxYX"), parse("xy")) == ((1, 1, -Z), 1)         # w^-1 gives Z^-1
    assert substitute(parse("xy"), parse("xyx")) == (parse("xy"), 0)         # w longer than the word


def test_ak3_family_and_worked_example():
    """Source PIPELINE.md: 38 z-words, 34 images, 30 of them in AK(3)'s Aut orbit, 2 orbits in all."""
    images = enumerate_images(AK3)
    assert len(subwords(*AK3.rels)) == 38 and len(images) == 34
    assert [i for i in images if i.tag == "xyx/x/0"][0].pres.strs == ("XyXXyXXyXXXXX", "YXyXyX")
    keys = [orbit_key(i.pres) for i in images]
    assert keys.count(orbit_key(AK3)) == 30 and len(set(keys)) == 2
    assert all(k == orbit_key(AK3) for i, k in zip(images, keys) if i.n_subs == 1)


def test_relabel():
    assert relabel((2, 3, -3, -2), 1) == (1, 2, -2, -1) and relabel((1, 3, -1), 2) == (1, 2, -1)


def test_every_image_replays_from_its_steps():
    for pres in (AK3, PLANTED):
        for img in enumerate_images(pres):
            assert apply_steps(pres, img.steps) == img.pres


def test_planted_case_stable_cert():
    want = PLANTED_IMAGE.reduced().canonical()
    img = next(i for i in enumerate_images(PLANTED) if i.pres.reduced().canonical() == want)
    res = search(img.pres, SearchConfig(budget=100))
    assert res.solved and res.pops <= 5
    assert check_cert(PLANTED, img.steps, res.path) == img.pres
    out = run(PLANTED, CoVConfig(total_budget=2000, control=False))
    assert out.solved and out.ac_path is None and out.stable_cert.kind == "stable_cert"
    verify(PLANTED, out.stable_cert)


def test_planted_case_row_itself_is_an_ac_path():
    out = run(PLANTED, CoVConfig(until="ac_path"))
    assert [o.kind for o in out.outcomes] == ["ac_path"] and out.stable_cert is None
    assert out.ac_path.image is None and isinstance(out.ac_path.path[0], tuple)


def test_until_ac_path_keeps_going_past_a_stable_cert():
    cfg = CoVConfig(search=SearchConfig(budget=200), total_budget=2000, control=False)
    first = run(PLANTED, cfg)
    more = run(PLANTED, cfg.replace(until="ac_path"))
    ids = lambda r: [(o.kind, o.image.tag, o.path) for o in r.outcomes]
    assert ids(more)[:len(ids(first))] == ids(first) and len(more.outcomes) > len(first.outcomes)
    assert more.pops >= first.pops


def test_config_cyclic_and_capture_path():
    """Outcomes carry the search's reduction, and paths are captured whatever the search config says."""
    cfg = CoVConfig.from_dict({"search": {"budget": 40, "cyclic": False, "capture_path": False}, "total_budget": 400})
    assert cfg.search.budget == 40 and not cfg.search.cyclic
    solved = 0
    for r in data.load_csv("bench60")[:6]:
        for o in run(r.pres, cfg.replace(until="ac_path")).outcomes:
            assert o.path is not None and not o.cyclic
            verify(r.pres, o)
            solved += 1
    assert solved


def test_image_cap_is_the_written_length_plus_headroom():
    """The source's per-image cap: max(cap, longest relator of the image as written + headroom).

    The first solved image of PLANTED is xYXX, YXY (cyclically reduced: YX, YXY), so the cap is 4 + 30.
    """
    out = run(PLANTED, CoVConfig(total_budget=2000, control=False, cap_headroom=30))
    assert out.stable_cert.image.pres.strs == ("xYXX", "YXY") and out.stable_cert.cap == 34
    assert run(PLANTED, CoVConfig(total_budget=2000, control=False, cap_headroom=None)).stable_cert.cap == 24


def test_budget_is_total_and_deterministic():
    cfg = CoVConfig(search=SearchConfig(budget=50), total_budget=120, control=False)
    a, b = run(AK3, cfg), run(AK3, cfg)
    assert a.pops == b.pops <= 120 and a.stats["tried"] == 3 and not a.solved
    assert {k: v for k, v in a.stats.items() if k != "seconds"} == {k: v for k, v in b.stats.items() if k != "seconds"}


def test_checker_rejects_tampering():
    img = next(i for i in enumerate_images(PLANTED) if i.pres.reduced().canonical() == PLANTED_IMAGE.reduced().canonical())
    res = search(img.pres, SearchConfig(budget=100))
    define, sub, elim = img.steps
    bad = [
        (define, {**sub, "rels": (sub["rels"][0] + (1, -1, 2), sub["rels"][1])}, elim),         # not the same relator
        (define, sub, {**elim, "expr": elim["expr"] + (2, -2, 2)}),                                # g != expr
        (define, sub, {**elim, "gen": 3 - elim["gen"]}),
        ({**define, "word": define["word"][::-1]}, sub, elim),
        (sub, define, elim),
        (define, sub, {**elim, "op": "teleport"}),
    ]
    for steps in bad:
        with pytest.raises(ReplayError):
            check_cert(PLANTED, steps, res.path)
    with pytest.raises(ReplayError):
        check_cert(PLANTED, img.steps, res.path[:-1])                                              # the leg must end trivial
    with pytest.raises(ReplayError):
        check_cert(Presentation.parse("xx", "yy"), img.steps, res.path)                            # |det| != 1


def test_certificates_on_bench60():
    """Every image of 24 bench60 rows replays from its steps; every solve of a short run has a JSON-round-tripped, valid certificate."""
    rows = data.load_csv("bench60")[:24]
    n_images = 0
    for r in rows:
        for img in enumerate_images(r.pres):
            assert apply_steps(r.pres, img.steps) == img.pres
            n_images += 1
    assert n_images > 1000
    kinds = []
    for r in rows:
        out = run(r.pres, CoVConfig(search=SearchConfig(budget=40, backend="fast" if fast_available() else "spec"),
                                    total_budget=400, control=False))
        for o in out.outcomes:
            verify(r.pres, o)
            path = decode_path(json.loads(json.dumps(encode_path(o.path))))
            if o.kind == "stable_cert":
                check_cert(r.pres, json.loads(json.dumps(o.image.steps)), path)
            else:
                replay(r.pres, path, normalize=False)
            kinds.append(o.kind)
    assert kinds.count("stable_cert") >= 5 and kinds.count("ac_path") >= 1, kinds


def test_aut_related_image_gives_an_ac_path_on_the_row():
    """An image in the row's Aut(F2) orbit is carried back by transport: elementary moves that replay on the row."""
    for r in data.load_csv("bench60")[:24]:
        out = run(r.pres, CoVConfig(search=SearchConfig(budget=40), total_budget=400, control=False))
        o = out.ac_path
        if o is not None:
            assert o.image is not None and isinstance(o.path[0], dict)
            verify(r.pres, o)
            return
    pytest.fail("no aut-related image solved")


@needs_fast
@pytest.mark.parametrize("pid, cap", [(0, 24), (4, 24), (11, 24), (15, 24), (24, 24), (27, 24), (50, 24), (55, 24),
                                      (50, None), (59, None)])
def test_spec_and_fast_runs_agree(pid, cap):
    """Rows chosen to cover a first-image ac_path and stable_cert, multi-image runs (11, 15, 24, 27), cap-rejected
    children (50), a duplicate image (55), and uncapped search."""
    row = data.load_csv("bench60")[pid]
    cfg = CoVConfig(search=SearchConfig(budget=60, cap=cap), total_budget=500, control=False)
    a = run(row.pres, cfg)
    b = run(row.pres, cfg.replace(search=cfg.search.replace(backend="fast")))
    assert a.pops == b.pops and [(o.kind, o.path, o.cap) for o in a.outcomes] == [(o.kind, o.path, o.cap) for o in b.outcomes]
    assert {k: a.stats[k] for k in ("tried", "duplicates", "cap_rejected")} == {k: b.stats[k] for k in ("tried", "duplicates", "cap_rejected")}


@needs_fast
def test_bench60_against_plain_greedy():
    """Total budget 1,000 pops (100 per image, no control) against plain greedy at 1,000 pops, cap 24: 29 and 29 of 60."""
    rows = data.load_csv("bench60")
    plain = sum(search(r.pres, SearchConfig(budget=1000, backend="fast")).solved for r in rows)
    cfg = CoVConfig(search=SearchConfig(budget=100, backend="fast"), total_budget=1000, control=False)
    outs = [run(r.pres, cfg) for r in rows]
    kinds = [o.outcomes[0].kind for o in outs if o.solved]
    assert (plain, len(kinds), kinds.count("ac_path"), kinds.count("stable_cert")) == (29, 29, 7, 22)
