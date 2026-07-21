"""Tests for the inflate-and-descend ladder (NB6, inflate_descend.py).

All budgets <= 1000 (repo hard rule). Everything here is deterministic:
set iteration feeds only dedup membership, never ordering (both family and
candidate lists are sorted with full string tiebreaks).
"""

from experiments.greedy_tests.spec.moves import legacy_to_move
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.search import replay
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov import inflate_descend as inf

AK3 = ("xxxYYYY", "xyxYXY")

SMALL_CFG = {"budget": 60, "tiers": (16, 20), "wmax": 4, "family_cap": 100,
             "fanout": 1, "beam": 3, "climb_plateau": 10,
             "climb_max_pops": 60, "child_cap": 64}


def _replay_strs(start, moves):
    pres = Presentation(2, tuple(str_to_word(s) for s in start))
    mvs = [legacy_to_move(t, js, k1, k2) for t, js, k1, k2 in moves]
    end = replay(pres, mvs, cyclic=True)[-1]
    return tuple(word_to_str(r) for r in end.relators)


def test_climb_reaches_fat_states_and_its_path_replays():
    cl = inf.search_until(*AK3, 200, 24, up=True, plateau_k=30, child_cap=64)
    start_total = len(AK3[0]) + len(AK3[1])
    assert cl["best_total"] > start_total
    assert cl["max_popped_total"] >= cl["best_total"]
    inc = cl["incumbent"]
    assert len(inc[0]) + len(inc[1]) == cl["best_total"]
    end = _replay_strs(AK3, cl["incumbent_moves"])
    assert inf._canon_pair_w(str_to_word(end[0]), str_to_word(end[1])) == \
        inf._canon_pair_w(str_to_word(inc[0]), str_to_word(inc[1]))


def test_child_cap_none_equals_huge_and_runs_are_deterministic():
    a = inf.search_until(*AK3, 150, 24, up=False, child_cap=None)
    b = inf.search_until(*AK3, 150, 24, up=False, child_cap=10 ** 9)
    c = inf.search_until(*AK3, 150, 24, up=False, child_cap=10 ** 9)
    for k in ("status", "pops", "incumbent", "best_total",
              "max_popped_total"):
        assert a[k] == b[k] == c[k]


def test_bounded_family_reapplies_the_cross_relator_no_collapse_gate():
    # the documented case: w=yxx is an interior subword of r1 but collapses
    # r2 (yxxy -> zy, length 2) — subword_candidates rejects it, and the
    # bounded builder must too (enumerate_cov(family=...) has no gate).
    r1, r2 = str_to_word("xyxxy"), str_to_word("yxxy")
    fam = inf.bounded_family(r1, r2, wmax=8, family_cap=10 ** 9)
    w = str_to_word("yxx")
    assert max(w, cov.inverse(w)) not in fam
    assert all(2 <= len(x) <= 8 for x in fam)
    assert all(x == max(x, cov.inverse(x)) for x in fam)
    # with the length bound lifted the bounded family IS subword_candidates
    full = inf.bounded_family(r1, r2, wmax=100, family_cap=10 ** 9)
    assert set(full) == set(cov.subword_candidates(r1, r2))


def test_rename_gate_flags_every_n_subs_one_cov_as_a_relabel():
    r1w, r2w = str_to_word(AK3[0]), str_to_word(AK3[1])
    n = 0
    for res in cov.enumerate_cov(r1w, r2w):
        if res.n_subs == 1:
            assert inf.rename_kind(res, r1w, r2w) == "relabel"
            n += 1
    assert n, "no n_subs==1 rows — the gate test proves nothing"


def test_scramble_candidates_gated_ranked_and_deterministic():
    kept, stats = inf.scramble_candidates(*AK3, 24, wmax=4, family_cap=200,
                                          max_kept=8)
    assert kept and stats["n_kept"] == len(kept)
    tots = [t[0] for t in kept]
    assert tots == sorted(tots, reverse=True)          # fattest-first
    for tot, ab, o, res, kind in kept:
        assert res.n_subs >= 2
        assert kind in ("psi_non_aut", "psi_aut_no_identity")
        assert tot == len(o[0]) + len(o[1])
    again, _ = inf.scramble_candidates(*AK3, 24, wmax=4, family_cap=200,
                                       max_kept=8)
    assert [(t[0], t[2]) for t in kept] == [(t[0], t[2]) for t in again]


def test_ladder_rows_schema_junction_lineage_and_resume():
    rows = list(inf.ladder_one("t1", *AK3, SMALL_CFG, set()))
    assert rows
    need = {"pres_id", "tier", "branch_id", "arm", "cov_idx", "cap",
            "snapshot", "snapshot_total", "climb_status", "climb_pops_cum",
            "climb_max_popped_total", "start_arm", "start_total_arm",
            "descend_pops", "nodes_explored", "min_total_reached",
            "min_relator_length", "max_relator_length", "solved",
            "junctions", "z_words", "n_junctions", "elapsed_s"}
    for r in rows:
        assert need <= set(r)
        assert r["start_total_arm"] == sum(len(s) for s in r["start_arm"])
        assert r["n_junctions"] == len(r["junctions"]) == len(r["z_words"])
        if r["arm"] == "plain":
            assert r["cov_idx"] == -1 and "z_word" not in r
        else:
            assert r["z_word"] == r["junctions"][-1]["z_word"]
            assert r["orbit_motion"] in ("psi_non_aut", "psi_aut_no_identity")
            assert r["junctions"][-1]["iso_index"] is not None
        for j in r["junctions"]:
            assert j["orbit_motion"] != "relabel"
    # AK(3) has non-rename seed CoVs, so seeded branches must exist and their
    # rows must carry the seed junction lineage in every tier
    seeded = [r for r in rows if r["branch_id"].startswith("r.s")]
    assert seeded and all(r["n_junctions"] >= 1 for r in seeded)
    assert {r["tier"] for r in seeded} == set(SMALL_CFG["tiers"])
    done = {(r["pres_id"], r["tier"], r["branch_id"], r["arm"], r["cov_idx"])
            for r in rows}
    assert list(inf.ladder_one("t1", *AK3, SMALL_CFG, done)) == []


def test_solved_plain_row_verifies_and_tamper_fails():
    cfg = dict(SMALL_CFG, tiers=(8,), budget=400, fanout=0, climb_plateau=15,
               climb_max_pops=80)
    rows = list(inf.ladder_one("triv", "x", "y", cfg, set()))
    solved = [r for r in rows if r["solved"]]
    assert solved, "descending an inflated trivial pair must solve"
    r = solved[0]
    assert r["n_junctions"] == 0 and "path_moves" in r
    assert r["path_length"] == len(r["path_moves"])
    ok, why = inf.verify_segments("x", "y", r["segments"])
    assert ok, why
    bad = [dict(s) for s in r["segments"]]
    bad[-1] = {"moves": bad[-1]["moves"][:-1]}
    if r["path_length"]:                       # tampered path must not verify
        ok2, _ = inf.verify_segments("x", "y", bad)
        assert not ok2


def test_verify_rederives_junctions_and_rejects_a_tampered_iso_index():
    # junctions are always derived at CANONICAL search states — replaying a
    # moves segment lands on the canonical form, so the test must too
    canon, _ = inf._canon_key(*AK3)
    kept, _ = inf.scramble_candidates(*canon, 24, wmax=4, family_cap=200,
                                      max_kept=4)
    tot, ab, o, res, kind = kept[0]
    j = inf._junction(res, o, kind, 24)
    segs = [{"moves": []}, {"junction": j}, {"moves": []}]
    ok, why = inf.verify_segments(*canon, segs)
    assert not ok and why == "final state not trivial"   # junction leg passed
    other = [b.iso_index for b in
             cov.cov_branches(str_to_word(canon[0]), str_to_word(canon[1]),
                              res.z_word, default_cap=24, reject_len=40,
                              iso_gen=res.iso_gen)]
    bad_idx = 1 - j["iso_index"] if (1 - j["iso_index"]) in other else 2
    bad = [{"moves": []}, {"junction": dict(j, iso_index=bad_idx)},
           {"moves": []}]
    ok2, why2 = inf.verify_segments(*canon, bad)
    assert not ok2 and "junction" in why2


def test_fused_expansion_matches_the_reference_child_path():
    """The fused expand_node_nj path must reproduce the reference expansion
    (get_neighbors -> reduce -> cap-prune -> canonicalise) child-for-child,
    in generation order — this equality is what keeps rows written by the
    pre-fused code resume-compatible with the fused code."""
    from experiments.search.greedy_baseline import (
        arr_to_str, canonical_pair_nj, expand_node_nj,
        get_neighbors_with_moves_nj, reduce_relator_nj, str_to_arr)

    states = [AK3, ("YYYYXyyyx", "YYYYxxyX")]
    fat = inf.search_until(*AK3, 60, 30, up=True, plateau_k=10, child_cap=64)
    states.append(fat["incumbent"])            # a fat state, cap-prune active
    n_pruned_cases = 0
    for s in states:
        for cap in (18, 30):
            a1, a2 = str_to_arr(s[0]), str_to_arr(s[1])
            ref = []
            for n1, n2, t, js, k1, k2 in get_neighbors_with_moves_nj(a1, a2):
                n1 = reduce_relator_nj(n1, True)
                n2 = reduce_relator_nj(n2, True)
                if len(n1) > cap or len(n2) > cap:
                    continue
                c1, c2 = canonical_pair_nj(n1, n2)
                ref.append(((arr_to_str(c1), arr_to_str(c2)),
                            (int(t), int(js), int(k1), int(k2))))
            codes, lens, mvs, count = expand_node_nj(a1, a2, cap, True)
            fused = [(inf._decode_child(codes, lens, i),
                      (int(mvs[i, 0]), int(mvs[i, 1]),
                       int(mvs[i, 2]), int(mvs[i, 3])))
                     for i in range(count)]
            assert fused == ref
            raw = len(get_neighbors_with_moves_nj(a1, a2))
            n_pruned_cases += (count < raw)
    assert n_pruned_cases, "no case exercised the cap prune — test is weak"


def test_timed_heartbeat_fires_and_is_wall_clock_gated(capsys):
    inf.search_until(*AK3, 30, 24, up=True, plateau_k=None, child_cap=64,
                     hb_label="hb-test", hb_every_s=0.0)
    outp = capsys.readouterr().out
    assert "hb hb-test:" in outp and "pops/s" in outp and "heap=" in outp
    # default cadence (60 s) prints nothing in a sub-second search
    inf.search_until(*AK3, 30, 24, up=True, plateau_k=None, child_cap=64,
                     hb_label="hb-test")
    assert "hb " not in capsys.readouterr().out


def test_out_name_encodes_every_result_changing_knob():
    cfg = dict(SMALL_CFG)
    a = inf._out_name("aca_124", 50, cfg, "")
    for k, v in (("tiers", (16,)), ("wmax", 6), ("family_cap", 99),
                 ("fanout", 3), ("beam", 4), ("child_cap", 128),
                 ("climb_plateau", 20), ("climb_max_pops", 99)):
        assert a != inf._out_name("aca_124", 50, dict(cfg, **{k: v}), "")
    assert a != inf._out_name("aca_124", 51, cfg, "")
    assert a != inf._out_name("aca_124", 50, cfg, "s1")
