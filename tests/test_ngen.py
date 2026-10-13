"""acx.ngen: the SAC transform, its replayable lift to elementary stable moves, n-generator search."""
import importlib
import inspect
import os
import pkgutil
import random

import pytest
from conftest import ROOT

import acx.ngen
from acx.aut.autos import apply_table
from acx.core.config import SearchConfig
from acx.core.words import Presentation, canonical_word, inverse, parse, reduce
from acx.ngen import NGenConfig, check, define, lift, solve, triangulate, verify
from acx.ngen.sac import Sac
from acx.search import PARITY_STATS, search
from acx.verify import ReplayError, replay
from acx.verify.replay import abs_det

FAST = SearchConfig(backend="fast", budget=3000)
EXPECTED_SAMPLE_SOLVES = 10    # of 40 (rank two solves 34 of the same 40 at budget 1,000)
ROWS = [0, 32, 96, 128, 224, 256]      # MS640 rows whose triangle root solves within 3,000 pops


def test_triangulate_ms640(ms640):
    for pres in ms640[::16]:
        sac = triangulate(pres)
        assert check(sac) and sac.source == pres.reduced()
        assert sac.rank == pres.n_gen + len(sac.digrams)
        assert all(len(r) <= 3 for r in sac.root.rels) and len(sac.root.rels) == sac.rank
        assert abs_det(sac.root) == 1


# digrams and root of the reference triangulation on rows whose
# tie-breaks depend on orienting each relator as its canonical form (roots in acx letters)
SOURCE = {252: (((-2, -2), (-1, -1), (1, -2), (-5, 3), (-5, 4)), ["DBa", "Daz", "CBz", "CzX", "BxY", "AXX", "ZYY"]),
          285: (((-2, -2), (-1, -1), (-3, 1), (-5, -4), (-5, 1)), ["DBx", "DYz", "CBA", "CAY", "BZx", "AXX", "ZYY"]),
          458: (((-2, -2), (-3, -3), (-2, 1), (-5, 4), (-6, -3)), ["DCZ", "DxA", "CBa", "B", "BYx", "AZZ", "ZYY"])}


@pytest.mark.parametrize("pid", sorted(SOURCE))
def test_triangulate_matches_the_source(ms640, pid):
    digrams, root = SOURCE[pid]
    sac = triangulate(ms640[pid])
    assert sac.digrams == digrams
    assert sorted(canonical_word(r) for r in sac.root.rels) == sorted(canonical_word(parse(r)) for r in root)


def test_triangulate_is_a_noop_on_short_relators():
    sac = triangulate(Presentation.parse("xy", "Yxy"))
    assert sac.digrams == () and sac.root == sac.source


def test_check_rejects_a_forged_root():
    sac = triangulate(Presentation.parse("YYXyx", "Yx"))
    forged = type(sac)(sac.source, sac.digrams[:-1], sac.root)
    assert not check(forged)


def test_define_keeps_the_group_element():
    """Substituting ``h -> d`` in a rewritten relator gives back a conjugate of the original."""
    rng = random.Random(7)
    for _ in range(200):
        w = reduce(tuple(rng.choice([1, -1, 2, -2]) for _ in range(rng.randint(2, 14))))
        if len(w) < 2:
            continue
        k = rng.randrange(len(w))
        d = (w[k], w[(k + 1) % len(w)])
        out = define(Presentation(2, (w, (1,))), d)
        assert out.rels[-1] == inverse(d) + (3,)
        tab = {1: (1,), -1: (-1,), 2: (2,), -2: (-2,), 3: d, -3: inverse(d)}
        assert canonical_word(reduce(apply_table(out.rels[0], tab))) == canonical_word(w)
        assert len(out.rels[0]) < len(w)


@pytest.mark.parametrize("pid", ROWS)
def test_lift_replays_on_the_source(ms640, pid):
    pres = ms640[pid]
    res = solve(pres, NGenConfig(FAST))
    assert res.solved and res.kind == "stable_cert"
    m = len(res.sac.digrams)
    ops = [mv["op"] for mv in res.moves]
    assert ops.count("stabilize") == ops.count("destabilize") == m and set(ops) <= {
        "stabilize", "destabilize", "conjugate", "multiply", "invert", "swap"}
    states = verify(pres, res)
    assert states[-1].is_trivial() and states[-1].n_gen == 2
    assert max(s.n_gen for s in states) == pres.n_gen + m


def test_lift_rejects_a_tampered_certificate(ms640):
    res = solve(ms640[32], NGenConfig(FAST))
    first = next(i for i, mv in enumerate(res.moves) if mv["op"] == "multiply")
    with pytest.raises(ReplayError):
        replay(ms640[32], res.moves[:first] + res.moves[first + 1:], normalize=False)
    with pytest.raises(ReplayError):
        replay(ms640[32], res.moves[:len(res.moves) // 2], normalize=False)


def test_lift_from_unreduced_and_three_generator_sources(ms640):
    base = ms640[32]
    conj = Presentation(2, ((-1,) + base.rels[0] + (1,), base.rels[1] + (2, -2)))
    assert conj.rels != conj.reduced().rels
    stab = Presentation(3, base.rels + ((3,),))
    for pres in (conj, stab):
        res = solve(pres, NGenConfig(FAST))
        assert res.solved and res.kind == "stable_cert"
        assert verify(pres, res)[-1].is_trivial()


def test_lift_needs_a_path_that_solves(ms640):
    sac = triangulate(ms640[32])
    res = search(sac.root, FAST)
    with pytest.raises(ReplayError):
        lift(ms640[32], sac, res.path[:-1], res.start)


@pytest.mark.parametrize("cap", [24, 5, None])
@pytest.mark.parametrize("pid", [0, 96, 224, 64])
def test_fast_matches_spec_past_two_generators(ms640, pid, cap):
    root = triangulate(ms640[pid]).root
    cfg = SearchConfig(cap=cap, budget=300, trace=True)
    a, b = search(root, cfg), search(root, cfg.replace(backend="fast"))
    assert root.n_gen > 2 and (a.solved or cap != 5 or a.stats["cap_dropped"] > 0)
    assert (a.solved, a.pops, a.path, a.end, a.trace) == (b.solved, b.pops, b.path, b.end, b.trace)
    assert {k: a.stats[k] for k in PARITY_STATS} == {k: b.stats[k] for k in PARITY_STATS}


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("rels", [("YYXXyxxyy", "XXXyxx"), ("XyX", "YYxy")])
def test_solve_replays_without_cyclic_reduction(rels, backend):
    """B1 (ngen side): with cyclic = false the canonical start is not a fixed point of reduce + canonical. Without a
    definition the search must run on the input itself, so the ac_path it returns replays on the input."""
    pres = Presentation.parse(*rels)
    res = solve(pres, NGenConfig(SearchConfig(backend=backend, budget=800, cyclic=False)))
    assert res.solved and res.kind == "ac_path"
    assert verify(pres, res, cyclic=False)[-1].is_trivial()


def test_lift_from_the_normal_start_at_cyclic_false():
    """At cyclic = false the input is not its own normal form; lift takes the search's start (``Result.start``, the
    normal form) and returns moves that replay on the input. Pins ``Presentation.normal`` as the replayed state."""
    pres = Presentation.parse("xyX", "yXyy")
    res = search(pres, SearchConfig(backend="spec", budget=400, cyclic=False))
    assert res.solved and res.start == res.start.normal(False) and pres.normal(False) == res.start
    moves = lift(pres, Sac(pres.reduced(), (), pres), res.path, res.start, cyclic=False)
    assert replay(pres, moves, cyclic=False, normalize=False)[-1].is_trivial()


def test_solve_without_sac_is_an_ac_path(ms640):
    stab = Presentation(3, ms640[32].rels + ((3,),))
    res = solve(stab, NGenConfig(FAST, sac=False))
    assert res.solved and res.kind == "ac_path" and res.sac is None and res.rank == 3
    assert verify(stab, res)[-1].is_trivial()


def test_solve_short_relators_need_no_definition():
    res = solve(Presentation.parse("xy", "Yxy"), NGenConfig(FAST))
    assert res.kind == "ac_path" and res.sac.digrams == () and verify(Presentation.parse("xy", "Yxy"), res)


def test_sac_relators_are_at_most_length_3(ms640):
    """T15: each definition adds a relator ``d^-1 h`` of length 3, and the root has none longer than 3."""
    for pres in ms640[::40]:
        sac = triangulate(pres)
        cur = sac.source
        for d in sac.digrams:
            cur = define(cur, d)
            assert len(cur.rels[-1]) == 3
        assert cur == sac.root and max(map(len, cur.rels)) <= 3


def test_lift_flag_off_returns_the_stable_certificate(ms640):
    """T15: ``lift = false`` still reports the solve as a ``stable_cert``, with no elementary moves."""
    res = solve(ms640[32], NGenConfig(FAST, lift=False))
    assert res.solved and res.kind == "stable_cert" and res.moves is None


@pytest.mark.parametrize("pid, digrams", [(32, 4), (96, 3), (0, 2)])
def test_cyclic_false_ngen_replays(ms640, pid, digrams):
    """T15: with cyclic reduction off the SAC path still solves, lifts and replays on the source."""
    res = solve(ms640[pid], NGenConfig(FAST.replace(cyclic=False)))
    assert res.solved and res.kind == "stable_cert" and len(res.sac.digrams) == digrams
    assert verify(ms640[pid], res, cyclic=False)[-1].is_trivial()


def test_the_package_exports_the_result_type(ms640):
    """``acx.ngen.NGenResult`` is the type ``solve`` returns, solved or not (``docs/ARCHITECTURE.md`` lists it)."""
    from acx.ngen import NGenResult
    assert "NGenResult" in acx.ngen.__all__
    assert isinstance(solve(ms640[0], NGenConfig(FAST)), NGenResult)
    assert isinstance(solve(ms640[64], NGenConfig(FAST.replace(budget=5))), NGenResult)


def test_solve_unsolved_and_guard(ms640):
    res = solve(ms640[64], NGenConfig(FAST.replace(budget=5)))
    assert not res.solved and res.kind is None and res.moves is None
    rank3 = Presentation(3, ms640[64].rels + ((3,),))
    with pytest.raises(ValueError, match="length"):          # rank above two without SAC: s20_mk2 is refused
        solve(rank3, NGenConfig(SearchConfig(priority="s20_mk2"), sac=False))
    rank2 = solve(ms640[64], NGenConfig(SearchConfig(priority="s20_mk2", budget=5), sac=False))   # rank two: allowed
    assert rank2.search.pops <= 5


def test_sac_needs_the_length_priority_when_the_config_is_built():
    """B8: SAC past two generators needs LENGTH; the error comes from the config, before any search or file."""
    with pytest.raises(ValueError, match="length"):
        NGenConfig(SearchConfig(priority="s20_mk2"))
    assert NGenConfig(SearchConfig(priority="s20_mk2"), sac=False).sac is False


def test_ngen_config_refused_at_runner_load_before_anything_is_written():
    """B8 through the runner: ``run.py`` loads (and refuses) the config before it creates results/<name>/."""
    from acx.runner import load_config, method_config
    with pytest.raises(ValueError, match="length"):
        load_config(os.path.join(ROOT, "configs", "ngen_sac.toml"), ["search.priority=s20_mk2"])
    with pytest.raises(ValueError, match="length"):
        method_config({"method": "ngen", "benchmark": "bench60", "search": {"priority": "s20_mk2"}})
    assert method_config({"method": "ngen", "benchmark": "bench60", "search": {"priority": "s20_mk2"},
                          "ngen": {"sac": False}}).sac is False


def rand_word(n, rng):
    """A freely reduced word of length ``n`` (the B6 repro draws its relators this way, seed 3)."""
    w = []
    while len(w) < n:
        g = rng.choice([1, 2, -1, -2])
        if not w or w[-1] != -g:
            w.append(g)
    return tuple(w)


@pytest.mark.parametrize("backend", ["spec", "fast"])
def test_a_root_past_26_generators_is_searched(backend):
    """B6, F5: ``fmt`` names the generators past z ``g27`` and ``parse`` reads them back, so a row whose SAC root has
    57 generators is searched (it was refused up front, and the row that raised ended the whole run)."""
    rng = random.Random(3)
    p = Presentation(2, (rand_word(70, rng), rand_word(70, rng)))          # SAC root has rank 57
    res = solve(p, NGenConfig(SearchConfig(budget=3, backend=backend)))
    assert not res.solved and res.rank == 57 and res.search.pops == 3


@pytest.mark.parametrize("n", [26, 27, 127])
def test_up_to_127_generators_are_searched(n):
    """The old limit was 26 letters; the one-byte letter code of the fast backend allows 127."""
    res = solve(Presentation(n, tuple((i,) for i in range(1, n + 1))), NGenConfig(FAST, sac=False))
    assert res.solved and res.rank == n and res.moves == ()


def test_more_than_127_generators_are_refused_before_the_search():
    """A letter code is one byte in the fast backend and the cap counters' keys: 128 generators are refused up front."""
    with pytest.raises(ValueError, match="127"):
        solve(Presentation(128, tuple((i,) for i in range(1, 129))), NGenConfig(sac=False))


def test_ms640_sample_solves_in_n_generator_form(ms640):
    """Every 16th MS640 row at budget 3,000 on the fast backend: each solve replays on its source."""
    n = 0
    for pres in ms640[::16]:
        res = solve(pres, NGenConfig(FAST))
        if res.solved:
            n += 1
            assert verify(pres, res)[-1].is_trivial()
    assert n == EXPECTED_SAMPLE_SOLVES


@pytest.mark.slow
def test_ngen_sac_config_result_is_unchanged(tmp_path):
    """configs/ngen_sac.toml on bench60 at budget 10,000: 8 solved, 531,923 pops, 147 sub-moves, 8,152 elementary
    moves."""
    from acx.runner import load_config, run
    s = run(load_config(os.path.join(ROOT, "configs", "ngen_sac.toml")), str(tmp_path), log=lambda *a: None)
    assert (s["solved"], s["cost"]["total"], s["cost"]["on_solved"]) == (8, 531923, 11923)
    sc = s["path_length"]["stable_cert"]
    assert (sc["sub_moves"]["sum"], sc["elem_moves"]["sum"]) == (147, 8152)


def test_each_module_of_the_package_is_its_attribute():
    """``acx.ngen.<name>`` is the module ``<name>.py``: the exported functions ``lift`` and ``solve`` live in
    ``lifting.py`` and ``solver.py``, so neither hides its module."""
    names = {info.name for info in pkgutil.iter_modules(acx.ngen.__path__)}
    assert {"lifting", "solver"} <= names
    for name in sorted(names):
        module = importlib.import_module(f"acx.ngen.{name}")
        assert inspect.ismodule(module) and getattr(acx.ngen, name) is module
