"""acx.cov: the family, the certificate checker, CoV-then-search and its typed outcomes.

The bench60 numbers are a golden regression (fast backend, so the test is skipped without it); the same numbers on
spec follow from the spec/fast parity of ``tests/test_fast.py``.
"""
import hashlib
import json

import pytest

from acx import data
from acx.aut import orbit_key
from acx.core.config import SearchConfig
from acx.core.moves import decode_path, encode_path
from acx.core.words import Presentation, fmt, inverse, parse, renumber, substitute_generator
from acx.cov import CoVConfig, ReplayError, apply_steps, check_cert, enumerate_images, verify
from acx.cov.family import FAMILIES, proper_subwords, subwords
from acx.cov.images import class_key
from acx.cov.run import run
from acx.cov.substitution import Z, isolate, occurrences, patterns, substitute, substitute_pattern
from acx.runner import method_config
from acx.search import BackendUnavailable, search
from acx.search.engine import backend as load_backend
from acx.verify import replay

CAP_KEYS = ("cap", "cap_dropped", "cap_dropped_min_total", "cap_would_pop", "cap_first_bind", "cap_needed", "cap_legs_bound")
AK3 = Presentation.parse("xyxYXY", "xxxYYYY")
# Planted: found by running CoVs backwards to the trivial T = <x, y | xYX, xYxYX>. T is the image of P under
# z = xYx, eliminating y, so P has an image that a search solves in 3 pops. T is not in P's Aut orbit.
PLANTED = Presentation.parse("XyXXy", "yyXXyXX")
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


def test_family_rules_sub_nc2_p():
    """The tag's word rules: ``sub`` (cyclic subwords, length >= 2), ``nc2`` (no relator shrinks below 3), ``p`` (powers)."""
    short = {fmt(w) for w in subwords(parse("xyxY"), parse("yy"))}
    assert short == {"xy", "yx", "yX", "Xy"}                  # nc2 drops xyx (leaves Zy) and yy (leaves z)
    powers = {fmt(w) for w in subwords(parse("xxxYY"), parse("yxY"))}
    assert {"xx", "xxx", "yy"} <= powers                      # p: pure powers are members


def test_isolate_and_eliminate_words():
    """``isolate`` needs exactly one g and a z; ``substitute_generator`` puts the expression for g and g^-1."""
    assert isolate((1, Z), 1) == (-Z,) and isolate((-1, Z), 1) == (Z,)       # x z = 1 gives x = Z (z inverse); X z = 1 gives x = z
    assert isolate((1, 2, -1, Z), 1) is None                                 # two x
    assert isolate((1, 2), 1) is None                                        # no z
    assert substitute_generator((1, 2, -1), 1, (Z,)) == (Z, 2, -Z)


def test_renumber():
    assert renumber((2, 3, -3, -2), 1) == (1, 2, -2, -1) and renumber((1, 3, -1), 2) == (1, 2, -1)


def test_enumerate_images_max_len_keeps_the_images_whose_relators_all_fit():
    """AK(3) has 34 images, the longest relator 15 letters: no limit, the family's 239 and 15 keep them all."""
    def longest(image):
        return max(map(len, image.pres.rels))

    images = enumerate_images(AK3, None)
    assert len(images) == 34 and max(map(longest, images)) == 15 and enumerate_images(AK3) == images
    counts = {}
    for limit in (15, 14, 12, 10, 8):
        kept = enumerate_images(AK3, limit)
        assert kept == tuple(image for image in images if longest(image) <= limit)
        counts[limit] = len(kept)
    assert counts == {15: 34, 14: 31, 12: 30, 10: 21, 8: 4}


def test_subwords_are_sorted_distinct_and_at_least_two():
    """The family's words ``w``: ordered by (length, word), each once (``w`` and ``w^-1`` are one), never a rename."""
    words = subwords(*AK3.rels)
    assert words == sorted(set(words), key=lambda w: (len(w), w)) and min(map(len, words)) == 2
    assert not any(inverse(w) in words for w in words)


def test_every_image_replays_from_its_steps():
    for pres in (AK3, PLANTED):
        for img in enumerate_images(pres):
            assert apply_steps(pres, img.steps) == img.pres


# The default family's images of the shipped CoV benchmarks, which the published CoV numbers were run on:
# (number of images, sha256 of every field of every image in order).
IMAGE_PINS = {
    "bench60": (6_177, "639caf309037f933b586c8c9181ef652a7377b650b81c9757a6004aafda32041"),
    "ladder60": (4_801, "8c5dfe186686a35a0bfbd5fec04935609444e017fef899bdf3a8cc1a164af23a"),
    "ladder200": (13_880, "c167c8a79df66406d5e85ced4f53652067913db8c10f90bc9480afdd48340cc9"),
    "ms640": (44_311, "99638e148636daa25e0c3b22019c3137fce8478d831fa68e5023d984f3e7e7a0"),
}


@pytest.mark.parametrize("benchmark", sorted(IMAGE_PINS))
def test_default_images_of_the_shipped_benchmarks_do_not_move(benchmark):
    digest, n_images = hashlib.sha256(), 0
    for r in data.rows(benchmark):
        for i in enumerate_images(r.pres):
            fields = (r.id, i.pres.rels, i.w, i.gen, i.iso_index, i.expr, i.substituted, i.n_subs)
            digest.update(repr(fields).encode() + b"\n")
            n_images += 1
    assert (n_images, digest.hexdigest()) == IMAGE_PINS[benchmark]


def planted_image():
    """The CoV image of PLANTED that is PLANTED_IMAGE up to rotation, inversion and order."""
    want = PLANTED_IMAGE.reduced().canonical()
    return next(i for i in enumerate_images(PLANTED) if i.pres.reduced().canonical() == want)


def test_check_cert_cap_bounds_what_the_moves_of_the_leg_produce():
    """As in the search, the cap bounds the relators each S-move produces and not the image as written (7 letters):
    the planted leg's two moves leave relators of at most 2 letters, so a cap of 2 passes and a cap of 1 does not."""
    img = planted_image()
    res = search(img.pres, SearchConfig(budget=100))
    assert max(map(len, img.pres.rels)) == 7 and res.path_length == 2
    for cap in (None, 24, 2):
        assert check_cert(PLANTED, img.steps, res.path, cap=cap) == img.pres
    with pytest.raises(ReplayError, match="exceeds cap 1"):
        check_cert(PLANTED, img.steps, res.path, cap=1)


def test_planted_case_stable_cert():
    img = planted_image()
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
    cfg = CoVConfig(search=SearchConfig(budget=40, cyclic=False, capture_path=False), total_budget=400)
    solved = 0
    for r in data.load_csv("bench60")[:6]:
        for o in run(r.pres, cfg.replace(until="ac_path")).outcomes:
            assert o.path is not None and not o.cyclic
            verify(r.pres, o)
            solved += 1
    assert solved


@needs_fast
@pytest.mark.parametrize("rid", [579, 380, 533, 538, 543, 544, 546])
def test_noncyclic_rows_replay_on_the_row(rid):
    """With ``cyclic = false`` the reduced canonical form is not a fixed point of itself. These bench60 rows raised
    ``ReplayError`` twice over: ``verify`` replayed a stable certificate from a twice-normalised image, and
    ``transport`` replayed a path from a start it had normalised again."""
    row = next(r for r in data.load_csv("bench60") if int(r.id) == rid)
    cfg = CoVConfig(search=SearchConfig(budget=300, cyclic=False, backend="fast"), total_budget=10_000, until="ac_path")
    out = run(row.pres, cfg)
    assert out.solved
    for o in out.outcomes:
        assert not o.cyclic
        verify(row.pres, o)


def test_image_cap_is_the_written_length_plus_headroom():
    """The source's per-image cap: max(cap, longest relator of the image as written + headroom).

    The first solved image of PLANTED is yxYYY, YYYx (cyclically reduced: xYY, YYYx), so the cap is 5 + 30.
    """
    out = run(PLANTED, CoVConfig(total_budget=2000, control=False, cap_headroom=30))
    assert out.stable_cert.image.pres.strs == ("yxYYY", "YYYx") and out.stable_cert.cap == 35
    assert run(PLANTED, CoVConfig(total_budget=2000, control=False, cap_headroom=None)).stable_cert.cap == 24


def test_budget_is_total_and_deterministic():
    cfg = CoVConfig(search=SearchConfig(budget=50), total_budget=120, control=False)
    a, b = run(AK3, cfg), run(AK3, cfg)
    assert a.pops == b.pops <= 120 and a.stats["tried"] == 3 and not a.solved
    assert {k: v for k, v in a.stats.items() if k != "seconds"} == {k: v for k, v in b.stats.items() if k != "seconds"}


def test_checker_rejects_tampering():
    img = planted_image()
    res = search(img.pres, SearchConfig(budget=100))
    define, sub, elim = img.steps
    bad = [
        (define, {**sub, "rels": (sub["rels"][0] + (1, -1, 2), sub["rels"][1])}, elim),         # not the same relator
        (define, sub, {**elim, "expr": elim["expr"] + (2, -2, 2)}),                                # g != expr
        (define, sub, {**elim, "gen": 3 - elim["gen"]}),
        ({**define, "word": define["word"][1:] + define["word"][:1]}, sub, elim),                 # another w
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
    assert {k: a.stats[k] for k in ("tried", "duplicates", *CAP_KEYS)} == {k: b.stats[k] for k in ("tried", "duplicates", *CAP_KEYS)}


@needs_fast
def test_bench60_against_plain_greedy():
    """Total budget 1,000 pops (100 per image, no control) against plain greedy at 1,000 pops, cap 24: 29 and 29 of 60."""
    rows = data.load_csv("bench60")
    plain = sum(search(r.pres, SearchConfig(budget=1000, backend="fast")).solved for r in rows)
    cfg = CoVConfig(search=SearchConfig(budget=100, backend="fast"), total_budget=1000, control=False)
    outs = [run(r.pres, cfg) for r in rows]
    kinds = [o.outcomes[0].kind for o in outs if o.solved]
    assert (plain, len(kinds), kinds.count("ac_path"), kinds.count("stable_cert")) == (29, 29, 7, 22)


def _legs(pres, cfg):
    """The legs ``run`` searches for ``pres`` (control first, duplicates once), with the pops spent before each."""
    s, seen, pops, out = cfg.search, set(), 0, []
    for img in ([None] if cfg.control else []) + list(enumerate_images(pres, cfg.max_len)):
        if cfg.total_budget - pops <= 0:
            break
        start = (pres if img is None else img.pres).reduced(s.cyclic).canonical()
        if start in seen:
            continue
        seen.add(start)
        cap = s.cap
        if img is not None and cap is not None and cfg.cap_headroom is not None:
            cap = max(cap, max(map(len, img.pres.rels)) + cfg.cap_headroom)
        res = search(start, s.replace(budget=min(s.budget, cfg.total_budget - pops), cap=cap, capture_path=True))
        out.append(({k: res.stats[k] for k in CAP_KEYS[:6]}, pops))
        pops += res.pops
        if res.solved:
            break
    return out


@needs_fast
@pytest.mark.parametrize("pid, cap", [(11, 10), (24, 10), (24, 14), (15, 10), (4, 10), (0, 10)])
def test_row_counters_aggregate_the_legs(pid, cap):
    """The row's counters are the legs' (sums of dropped and would-pop, minima of min-total and needed, the first
    binding leg's bind in row pops) and ``cap_legs_bound`` counts the legs that bind."""
    row = data.load_csv("bench60")[pid]
    cfg = CoVConfig(search=SearchConfig(budget=60, cap=cap, backend="fast"), total_budget=300)
    legs = _legs(row.pres, cfg)
    st = run(row.pres, cfg).stats
    recs = [r for r, _ in legs]
    want = {"cap": cap, "cap_dropped": sum(r["cap_dropped"] for r in recs), "cap_would_pop": sum(r["cap_would_pop"] for r in recs),
            "cap_legs_bound": sum(1 for r in recs if r["cap_would_pop"])}
    low = lambda k: min((r[k] for r in recs if r[k] is not None), default=None)  # noqa: E731
    want |= {"cap_dropped_min_total": low("cap_dropped_min_total"), "cap_needed": low("cap_needed"),
             "cap_first_bind": next((before + r["cap_first_bind"] for r, before in legs if r["cap_would_pop"]), None)}
    assert {k: st[k] for k in want} == want
    assert (want["cap_would_pop"] > 0) == (want["cap_first_bind"] is not None) == (want["cap_needed"] is not None)


@needs_fast
def test_row_counters_cover_every_case():
    """A binding row, a row where the cap dropped children that never mattered, a clean row and the uncapped row."""
    rows = data.load_csv("bench60")
    cfg = CoVConfig(search=SearchConfig(budget=60, cap=10, backend="fast"), total_budget=300)
    bound, loose, clean = (run(rows[i].pres, cfg).stats for i in (24, 15, 0))
    assert bound["cap_legs_bound"] >= 1 and bound["cap_would_pop"] > 0 and bound["cap_first_bind"] >= 2
    assert loose["cap_dropped"] > 0 and loose["cap_would_pop"] == 0 and loose["cap_first_bind"] is None and loose["cap_legs_bound"] == 0
    assert clean["cap_dropped"] == 0 and clean["cap_dropped_min_total"] is None
    free = run(rows[24].pres, cfg.replace(search=cfg.search.replace(cap=None))).stats
    assert free["cap"] is None and free["cap_dropped"] == free["cap_would_pop"] == free["cap_legs_bound"] == 0
    assert free["cap_first_bind"] is None and free["cap_needed"] is None


@needs_fast
def test_row_with_no_binding_leg_is_the_same_row_at_any_larger_cap():
    """``cap_would_pop == 0`` on every leg: a larger cap (every image cap follows) gives the same pops and paths."""
    rows = data.load_csv("bench60")
    zero = nonzero = 0
    for pid in (0, 4, 11, 15, 24, 27, 50, 55):
        for cap in (10, 14):
            cfg = CoVConfig(search=SearchConfig(budget=60, cap=cap, backend="fast"), total_budget=300)
            a = run(rows[pid].pres, cfg)
            if a.stats["cap_would_pop"]:
                nonzero += 1
                continue
            zero += 1
            for bigger in (cap + 6, None):
                b = run(rows[pid].pres, cfg.replace(search=cfg.search.replace(cap=bigger)))
                assert a.pops == b.pops and [(o.kind, o.path) for o in a.outcomes] == [(o.kind, o.path) for o in b.outcomes]
    assert zero >= 6 and nonzero >= 3


# The family suballpxyb8 (``CoVConfig.family``): every pattern of every proper cyclic subword, one image per class.
SWEEP_MS640_SHA256 = "1e10f931608808511df10ae319e84622b99256d684942e14344066307b5c1ae4"
SWEEP_PRES0 = {("XXy", "YXyxx"), ("XyXX", "YxyXX"), ("Xyx", "YXyxYx"), ("Xyx", "YXyxx"), ("xYx", "YxyXyX")}


@pytest.mark.parametrize("family", FAMILIES)
def test_a_relator_that_is_not_cyclically_reduced_gives_the_images_of_its_reduced_form(family):
    for conj in (Presentation.parse("xxyxYXYX", "xxxYYYY"), Presentation.parse("yxxxYYYYY", "xyxYXY")):
        assert conj.reduced() != conj
        images = enumerate_images(conj, family=family)
        assert images == enumerate_images(conj.reduced(), family=family)
        assert all(apply_steps(conj, i.steps) == i.pres for i in images)          # the certificate is the row's


def test_only_the_default_family_depends_on_the_rotation_of_a_relator():
    """MS640 row 20 with r1 rotated: the default family substitutes in one pass over the relator as written."""
    def classes(pres, family):
        return {class_key(i.pres) for i in enumerate_images(pres, family=family)}

    row = data.rows("ms640")[20].pres                                          # YYYYYx, YYXyx
    rotated = Presentation.parse("YYxYYY", "YYXyx")
    assert classes(rotated, "suballpxyb8") == classes(row, "suballpxyb8")
    assert classes(rotated, "subnc2pxysb") != classes(row, "subnc2pxysb")


def test_all_subsets_words_are_the_proper_cyclic_subwords():
    """Lengths 2 to |r| - 1, the seam included; a whole relator is dropped even when it sits inside the other one."""
    r1, r2 = parse("xyxxy"), parse("yxxy")
    words = proper_subwords(r1, r2)
    assert {len(w) for w in words} == {2, 3, 4} and parse("yxxy") not in words
    assert words == sorted(set(words), key=lambda w: (len(w), w)) and not any(inverse(w) in words for w in words)
    assert set(subwords(r1, r2)) <= set(words)
    assert "xyx" in {fmt(w) for w in proper_subwords(parse("xyxY"), parse("yy"))}                  # no nc2 gate


def test_patterns_are_every_non_overlapping_set_of_occurrences():
    """The seam is an ordinary position; partial substitution counts; the order is the sweep's."""
    cyc = parse("xxxxy")
    occs = occurrences(cyc, parse("xx"))
    assert occs == ((0, Z), (1, Z), (2, Z))
    assert [tuple(s for s, _ in p) for p in patterns(occs, 5, 2)] == [(), (2,), (1,), (0,), (0, 2)]
    assert substitute_pattern(cyc, ((1, Z),), 2) == (Z, 1, 2, 1)
    seam = occurrences(parse("yxxxy"), parse("yy"))
    assert seam == ((4, Z),) and substitute_pattern(parse("yxxxy"), seam, 2) == (Z, 1, 1, 1)
    shadowed = occurrences(parse("xxyx"), parse("xx"))                         # substitute takes position 0 only
    assert [fmt(substitute_pattern(parse("xxyx"), p, 2)) for p in patterns(shadowed, 4, 2)[1:]] == ["zxy", "zyx"]


def test_all_subsets_is_one_image_per_class_and_contains_the_default_family():
    for pres in [AK3, PLANTED] + [r.pres for r in data.rows("ms640")[::80]]:
        own = class_key(pres)
        images = enumerate_images(pres, family="suballpxyb8")
        keys = [class_key(i.pres) for i in images]
        assert len(set(keys)) == len(keys) and own not in keys
        assert {class_key(i.pres) for i in enumerate_images(pres)} - {own} <= set(keys)
        assert all(apply_steps(pres, i.steps) == i.pres for i in images)


def test_all_subsets_matches_the_sweep():
    """The sweep's class counts and, for MS640 row 0, its five starts as written (budget-100 file of the branch)."""
    rows = data.rows("ms640")
    counts = {pid: len(enumerate_images(rows[pid].pres, family="suballpxyb8")) for pid in (0, 155, 580, 634)}
    assert len(enumerate_images(AK3, family="suballpxyb8")) == 12 and counts == {0: 5, 155: 24, 580: 236, 634: 566}
    assert {i.pres.strs for i in enumerate_images(rows[0].pres, family="suballpxyb8")} == SWEEP_PRES0


@pytest.mark.slow
def test_all_subsets_is_the_sweep_on_ms640():
    """The sweep's 114,042 MS640 starts, each as written with its w, eliminated generator, isolating relator, number
    of substitutions and cap (sha256 of the sorted rows of the branch's budget-100 file)."""
    lines = sorted(f"{r.id},{i.pres.strs[0]},{i.pres.strs[1]},{fmt(i.w)},{'xy'[i.gen - 1]},{i.iso_index},{i.n_subs},"
                   f"{max(24, max(map(len, i.pres.rels)) + 16)}"
                   for r in data.rows("ms640") for i in enumerate_images(r.pres, family="suballpxyb8"))
    assert len(lines) == 114_042
    assert hashlib.sha256("\n".join(lines).encode()).hexdigest() == SWEEP_MS640_SHA256


def test_family_is_a_config_choice():
    """``[cov] family`` reaches ``CoVConfig`` through the runner; an unknown family is a ``ValueError`` everywhere."""
    assert CoVConfig().family == "subnc2pxysb"
    assert method_config({"method": "cov", "cov": {"family": "suballpxyb8"}}).family == "suballpxyb8"
    with pytest.raises(ValueError, match="family 'zf3' not in"):
        method_config({"method": "cov", "cov": {"family": "zf3"}})
    with pytest.raises(ValueError, match="family 'zf3' not in"):
        CoVConfig(family="zf3")
    with pytest.raises(ValueError, match="family 'zf3' not in"):
        enumerate_images(AK3, family="zf3")
    out = run(PLANTED, CoVConfig(total_budget=2000, control=False, family="suballpxyb8"))
    assert out.solved and out.stats["images"] == len(enumerate_images(PLANTED, family="suballpxyb8"))
    for o in out.outcomes:
        verify(PLANTED, o)
