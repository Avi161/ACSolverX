"""covmeet: the resume contract, merge detection, drop tracking, and determinism.

Everything here runs on tiny seed pairs with ``max_expanded`` in the single digits —
covmeet does zero greedy-search nodes (it is pure CoV enumeration + Aut-min), so the
1,000-node budget rule is satisfied trivially, and each run() call is well under a
second of real expansion work.

The load-bearing contract, in order of what a failure would cost:

1. **Resume == uninterrupted.** A run stopped after k expansions and resumed to n must
   leave the exact store a straight run to n leaves. This is what lets a vast.ai box
   die at any instant and lose nothing.
2. **A torn trailing line is repaired before the first append** — the crash mode a
   preempted spot instance actually produces (lesson: run-baseline-two-known-bugs).
3. **A merge is detected** when two seeds' cones touch, and the classes count drops.
4. **A drop is detected** when a cone reaches below its seed's aut-min (the user's
   second deliverable), and replay re-derives it identically.
5. **Determinism**: same config, fresh dir, twice -> byte-identical event rows (meta
   rows carry a session timestamp and are excluded).
6. **Serial == parallel**: workers=0 and workers=2 produce the same store.
"""

import csv
import json
import os

import pytest

from experiments.stable_ac.cov.meet import covmeet
from experiments.stable_ac.cov.meet.covmeet import (
    Store, _expand_chunk, load, run, run_paths, save_snapshot, snap_paths,
)

# Two short, freely+cyclically reduced pairs (aca_0 and aca_1's raw reps — used here
# as arbitrary small inputs, not as a claim about those classes).
P0 = ("YXXyxYx", "YYYYYYXyxyX")
P1 = ("YYXXyxx", "YYYxyXyX")

SEEDS_AB = [("t_a", *P0), ("t_b", *P1)]


def _run(tmp, seeds, n, tag="testAB", **kw):
    kw.setdefault("workers", 0)
    kw.setdefault("wave", 3)
    kw.setdefault("chunk", 2)
    kw.setdefault("mem_guard_gb", 0)          # never trip on a busy CI host
    kw.setdefault("log", lambda *a: None)
    return run(str(tmp), seed_set=tag, seeds_override=seeds, max_expanded=n, **kw)


def _store(tmp, n_seeds, tag="testAB"):
    store, header = load(str(tmp), tag, n_seeds, expect_family=covmeet.FAMILY,
                         log=lambda *a: None)
    assert header is not None
    return store


def _fingerprint(store):
    return (sorted(store.mask.items()), sorted(store.expanded),
            sorted((k, sorted(v)) for k, v in store.frontier.items()),
            store.merges, store.drops, sorted(store.best_mu.items()))


# ------------------------------------------------------------------- 1. resume

def test_resume_equals_uninterrupted(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _run(a, SEEDS_AB, 5)                              # straight run to 5
    _run(b, SEEDS_AB, 2)                              # crash after 2...
    _run(b, SEEDS_AB, 3)                              # ...resume for 3 more
    sa, sb = _store(a, 2), _store(b, 2)
    assert _fingerprint(sa) == _fingerprint(sb)
    assert len(sa.expanded) == 5


def test_resume_is_replay_not_reseed(tmp_path):
    _run(tmp_path, SEEDS_AB, 2)
    _run(tmp_path, SEEDS_AB, 1)
    events, _ = run_paths(str(tmp_path), "testAB")
    rows = [json.loads(l) for l in open(events)]
    assert sum(1 for r in rows if r["t"] == "seed") == 2      # seeded exactly once
    assert sum(1 for r in rows if r["t"] == "meta") == 2      # one meta per session


def test_certs_hold_results_only_and_disk_is_bounded(tmp_path):
    """The v3 size contract: the certs jsonl carries ONLY meta/seed/merge/drop rows —
    per-expansion work writes nothing there — and the on-disk footprint is the
    snapshot pair, whose size tracks the store, not the runtime."""
    _run(tmp_path, SEEDS_AB, 2)
    certs, _ = run_paths(str(tmp_path), "testAB")
    rows_before = sum(1 for _ in open(certs))
    _run(tmp_path, SEEDS_AB, 3)                              # more work, no merges
    rows = [json.loads(l) for l in open(certs)]
    assert {r["t"] for r in rows} <= {"meta", "seed", "merge", "drop"}
    # only the second session's meta row was added — expansions wrote nothing
    assert len(rows) == rows_before + 1
    snap, prev = snap_paths(str(tmp_path), "testAB")
    assert os.path.exists(snap) and os.path.exists(prev)


def test_summary_written_and_matches_replay(tmp_path):
    _run(tmp_path, SEEDS_AB, 3)
    events, summary_path = run_paths(str(tmp_path), "testAB")
    with open(summary_path) as f:
        written = json.load(f)
    store = _store(tmp_path, 2)
    live = covmeet.summarise(store, SEEDS_AB)
    for k in ("classes_remaining", "merges_found", "expanded", "discovered",
              "raw_cov_enumerated", "n_improved"):
        assert written[k] == live[k], k


# ------------------------------------------------------------- 2. torn tail

def test_torn_trailing_line_repaired_before_append(tmp_path):
    _run(tmp_path, SEEDS_AB, 2)
    events, _ = run_paths(str(tmp_path), "testAB")
    before = _store(tmp_path, 2)
    with open(events, "a") as f:
        f.write('{"t":"drop","name":"zz","chain":["xy')   # the crash artifact
    _run(tmp_path, SEEDS_AB, 1)                          # must repair, then resume
    after = _store(tmp_path, 2)
    assert len(after.expanded) == len(before.expanded) + 1
    for line in open(events):
        json.loads(line)                                 # every line parses again


def test_torn_tail_without_newline_only_loses_the_torn_row(tmp_path):
    _run(tmp_path, SEEDS_AB, 2)
    events, _ = run_paths(str(tmp_path), "testAB")
    n_rows = sum(1 for _ in open(events))
    with open(events, "a") as f:
        f.write('{"t":"x","rep":["a","b"],"nc')
    cut = covmeet._repair_torn_tail(events)
    assert cut > 0
    assert sum(1 for _ in open(events)) == n_rows


# ------------------------------------------------------------- 3. merges

def _first_child(pair):
    (_, _, children), = _expand_chunk([pair])
    assert children, "expansion produced no non-self-loop orbit"
    return children[0][0], children[0][1]                # (rep, mu)


def test_merge_via_common_child(tmp_path):
    """Seed B placed AT one of A's depth-1 orbits: expanding A must merge them."""
    crep, _ = _first_child(P0)
    seeds = [("t_a", *P0), ("t_planted", *crep)]
    summary = _run(tmp_path, seeds, 4, tag="testMG")
    assert summary["merges_found"] >= 1
    assert summary["classes_remaining"] == 1
    store = _store(tmp_path, 2, tag="testMG")
    assert store.uf.find(0) == store.uf.find(1)
    events, _ = run_paths(str(tmp_path), "testMG")
    merges = [json.loads(l) for l in open(events) if '"merge"' in l]
    assert merges and merges[0]["remaining"] == 1
    # the certificate: two chains, both ending at the recorded meeting orbit,
    # every segment replaying through the real transform + aut_min
    from experiments.stable_ac.cov.meet import verify_covmeet as vc
    ch_a, ch_b = merges[0]["chains"]
    for ch in (ch_a, ch_b):
        ok, nseg, trunc = vc.verify_chain(ch)
        assert ok and not trunc
    assert ch_a[-1]["rep"] == ch_b[-1]["rep"] == merges[0]["rep"]


def test_no_merge_between_disjoint_shallow_cones(tmp_path):
    summary = _run(tmp_path, SEEDS_AB, 2, tag="testNM")   # one expansion each
    assert summary["merges_found"] == 0
    assert summary["classes_remaining"] == 2


# ------------------------------------------------------------- 4. drops

def test_drop_logged_when_cone_descends_below_seed(tmp_path):
    """Plant a seed at a depth-1 orbit whose expansion contains an orbit SHORTER
    than itself; the engine must log the descent for that class. Constructed, not
    assumed: we search A's shallow cone for such a parent first."""
    (_, _, kids), = _expand_chunk([P0])
    planted = None
    for rep, mu, *_ in kids:
        (_, _, grand), = _expand_chunk([rep])
        if any(gmu < mu for _, gmu, *_ in grand):
            planted = rep
            break
    if planted is None:
        pytest.skip("no depth-2 descent under this start — probe deeper offline")
    summary = _run(tmp_path, [("t_p", *planted)], 1, tag="testDR", wave=1)
    assert summary["n_improved"] == 1
    row = summary["improved_below_seed"][0]
    assert row["best_mu"] < row["seed_mu"]
    store = _store(tmp_path, 1, tag="testDR")
    assert store.drops and store.drops[-1][1] == row["best_mu"]
    mus = [mu for _, mu, _ in store.drops]                # successive strict descents
    assert mus == sorted(mus, reverse=True) and len(set(mus)) == len(mus)
    events, _ = run_paths(str(tmp_path), "testDR")
    drops = [json.loads(l) for l in open(events) if json.loads(l)["t"] == "drop"]
    assert drops
    from experiments.stable_ac.cov.meet import verify_covmeet as vc
    ok, nseg, trunc = vc.verify_chain(drops[-1]["chain"])
    assert ok and not trunc and nseg >= 1
    assert drops[-1]["chain"][-1]["rep"] == drops[-1]["rep"]


def test_seed_mu_is_not_a_drop(tmp_path):
    _run(tmp_path, SEEDS_AB, 1)
    store = _store(tmp_path, 2)
    assert store.drops == [] or all(
        mu < store.seed_mu[i] for i, mu, _ in store.drops)


# ------------------------------------------------------------- 5. determinism

def test_same_config_twice_is_byte_identical_minus_meta(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    _run(a, SEEDS_AB, 4)
    _run(b, SEEDS_AB, 4)
    ea, _ = run_paths(str(a), "testAB")
    eb, _ = run_paths(str(b), "testAB")
    rows = lambda p: [l for l in open(p) if '"meta"' not in l.split(",")[0]]
    assert rows(ea) == rows(eb)
    sa, _ = snap_paths(str(a), "testAB")
    sb, _ = snap_paths(str(b), "testAB")
    assert open(sa, "rb").read() == open(sb, "rb").read()    # snapshots byte-equal


def test_event_rows_carry_no_timestamps(tmp_path):
    _run(tmp_path, SEEDS_AB, 2)
    events, _ = run_paths(str(tmp_path), "testAB")
    for line in open(events):
        ev = json.loads(line)
        if ev["t"] != "meta":
            assert "utc" not in json.dumps(ev).lower()


# ------------------------------------------------------------- 6. parallel parity

def test_serial_equals_parallel(tmp_path):
    a, b = tmp_path / "ser", tmp_path / "par"
    _run(a, SEEDS_AB, 4)
    _run(b, SEEDS_AB, 4, workers=2)
    assert _fingerprint(_store(a, 2)) == _fingerprint(_store(b, 2))


# ------------------------------------------------------------- guards & identity

def test_family_mismatch_refuses_to_resume(tmp_path):
    _run(tmp_path, SEEDS_AB, 1)
    with pytest.raises(RuntimeError, match="family"):
        load(str(tmp_path), "testAB", 2, expect_family="someotherfamily",
             log=lambda *a: None)


def test_corrupt_snapshot_falls_back_to_previous_and_redoes(tmp_path):
    """A hard crash mid-checkpoint: the main snapshot is garbage, the previous one
    loads, and the deterministic re-do lands on the same store as a straight run."""
    a, b = tmp_path / "a", tmp_path / "b"
    _run(a, SEEDS_AB, 4)                                  # straight run to 4
    _run(b, SEEDS_AB, 2)                                  # snap S2
    _run(b, SEEDS_AB, 2)                                  # snap S4, prev = S2
    snap, prev = snap_paths(str(b), "testAB")
    with open(snap, "r+b") as f:                          # corrupt the newest
        f.seek(20)
        f.write(b"garbagegarbage")
    store, header = load(str(b), "testAB", 2, expect_family=covmeet.FAMILY,
                         log=lambda *a: None)
    assert header is not None and len(store.expanded) == 2   # fell back to S2
    _run(b, SEEDS_AB, 2)                                  # re-do the lost interval
    assert _fingerprint(_store(b, 2)) == _fingerprint(_store(a, 2))


def test_filename_carries_engine_seed_set_and_family_only(tmp_path):
    events, summary = run_paths("/x", "all124")
    assert os.path.basename(events) == f"covmeet3_all124_{covmeet.FAMILY}_certs.jsonl"
    for knob in ("wave", "chunk", "worker", "2026"):
        assert knob not in os.path.basename(events)


def test_load_seeds_all124_uses_reduced_reps():
    seeds = covmeet.load_seeds("all124")
    assert len(seeds) == 124
    byname = {n: (a, b) for n, a, b in seeds}
    # aca_2 is a reduced row: its seed must be the mu-ladder rep, not the raw rep
    assert byname["aca_2"] != ("YXXYxyxyy", "YYxYxxYxy")
    assert len(covmeet.load_seeds("reduced39")) == 39
    with pytest.raises(ValueError):
        covmeet.load_seeds("everything")


def test_expand_chunk_census_and_no_self_loop():
    (rep, ncov, children), = _expand_chunk([P0])
    assert rep == P0 and ncov >= len(children) >= 1
    assert all(c[0] != P0 for c in children)             # self-loop never emitted
    assert sum(c[5] for c in children) <= ncov           # multiplicities are a census
    assert children == sorted(children)                  # deterministic order


# ------------------------------------------------------- the open set is not a beam

def test_take_wave_never_discards():
    """WAVE bounds a batch, never membership: what a wave doesn't pop stays queued."""
    st = Store(1)
    reps = [(f"x{i}y", "xy") for i in range(5)]
    for r in reps:
        st.reach(r, 4, 1)
    got = st.take_wave(2)
    assert len(got) == 2 and st.frontier_size() == 3
    rest = st.take_wave(99)
    assert sorted(got + rest) == sorted(reps)            # every rep popped exactly once
    assert st.take_wave(99) == [] and st.frontier_size() == 0


def test_all_duplicate_children_do_not_stop_the_run(tmp_path, monkeypatch):
    """The user's bug class: a wave whose children ALL dedup into known orbits (here:
    every expansion 'discovers' only seed 0's rep) must not end the run — the loop may
    stop only when every state in the open set has been popped and expanded. Merges
    must not stop it either."""
    seeds = [(f"t_{i}", f"xxx{'y' * (i + 1)}", "xyxY") for i in range(4)]
    import experiments.stable_ac.cov.meet.covmeet as cm
    from experiments.stable_ac.cov.ladder import autcanon_fast as af
    target = af.aut_min((seeds[0][1], seeds[0][2]))[1]

    def fake_expand(pairs):
        return [((a, b), 1,
                 [] if (a, b) == target else [(target, 8, "xy", "x", 0, 1)])
                for a, b in pairs]

    monkeypatch.setattr(cm, "_expand_chunk", fake_expand)
    summary = run(str(tmp_path), seed_set="testDUP", seeds_override=seeds,
                  workers=0, wave=1, chunk=1, mem_guard_gb=0, log=lambda *a: None)
    assert "exhausted" in summary["stopped"]             # ran the open set DRY
    assert summary["expanded"] == len(seeds)             # EVERY seed rep was popped
    store = _store(tmp_path, 4, tag="testDUP")
    assert store.frontier_size() == 0                    # nothing left unpopped
    assert len(store.expanded) == len(store.mask)        # every discovered orbit popped
    assert summary["merges_found"] >= 1                  # merges happened mid-run...
    assert summary["classes_remaining"] == 1             # ...and the run kept going


# ------------------------------------------------------------- v2 word codec

def test_word_codec_roundtrips_and_only_packs_long_words():
    from experiments.stable_ac.cov.meet.covmeet import _dec_word, _enc_word
    short = "xYxxyXY"
    assert _enc_word(short) == short                     # readable below threshold
    long_w = "xy" * 100                                  # 200 letters, freely reduced
    enc = _enc_word(long_w)
    assert enc.startswith("~200:") and len(enc) < len(long_w)
    assert _dec_word(enc) == long_w
    assert _dec_word(short) == short
    for w in ("x", "Xy", "xyX" * 41, "Y" + "xy" * 80):   # boundary + odd lengths
        assert _dec_word(_enc_word(w)) == w


def test_long_rep_survives_disk_roundtrip(tmp_path):
    """A >threshold relator must pack on disk and replay to the identical store."""
    long_pair = ("xy" * 80, "xY")                        # 160-letter relator
    seeds = [("t_long", *long_pair), ("t_b", *P1)]
    _run(tmp_path, seeds, 2, tag="testLP", wave=1)
    store = _store(tmp_path, 2, tag="testLP")
    from experiments.stable_ac.cov.ladder import autcanon_fast as af
    mu, rep = af.aut_min(long_pair)
    assert store.mask.get(rep, 0) & 1                    # the seed bit survived


# ------------------------------------------------------------- orbit memo (speed)

def test_orbit_memo_is_result_neutral():
    """Cold memo vs warm memo must give identical expansions — the memo is a
    speedup, never a result change. Measured: aut_min is 89% of per-state cost and
    relabel groups collapse ~66 children to ~21 keys."""
    covmeet._ORBIT_MEMO.clear()
    cold = _expand_chunk([P0, P1])
    warm = _expand_chunk([P0, P1])                        # memo now populated
    assert cold == warm
    assert len(covmeet._ORBIT_MEMO) > 0                   # it actually memoised
    # and against the raw function, orbit by orbit
    from experiments.stable_ac.cov.ladder import autcanon_fast as af
    for (_, _, children) in cold:
        for rep, mu, *_ in children:
            assert af.aut_min(rep) == (mu, rep)


def test_orbit_memo_cap_clears_not_grows(monkeypatch):
    monkeypatch.setattr(covmeet, "_ORBIT_MEMO_CAP", 5)
    covmeet._ORBIT_MEMO.clear()
    _expand_chunk([P0])
    assert len(covmeet._ORBIT_MEMO) <= 5 + 1              # clear fired at the cap


# ------------------------------------------------- the user's two explicit scenarios

def test_two_arbitrary_presentations_merge_is_collected_end_to_end(tmp_path):
    """Two seeds whose cones meet at depth 2 — not planted on a direct child — must
    produce: a merge in the summary, a union in the store, a certificate row whose
    two chains BOTH replay segment-by-segment to the same meeting orbit, and a
    classes count that drops to 1. The full collection path, nothing mocked."""
    (_, _, kids), = _expand_chunk([P0])
    mid = kids[0][0]
    (_, _, grand), = _expand_chunk([mid])
    deep = next(g[0] for g in grand if g[0] != mid)       # depth-2 orbit of P0
    seeds = [("t_a", *P0), ("t_deep", *deep)]
    summary = _run(tmp_path, seeds, 30, tag="testE2E", wave=4)
    assert summary["merges_found"] >= 1
    assert summary["classes_remaining"] == 1
    store = _store(tmp_path, 2, tag="testE2E")
    assert store.uf.find(0) == store.uf.find(1)
    events, _ = run_paths(str(tmp_path), "testE2E")
    merges = [json.loads(l) for l in open(events) if '"merge"' in l]
    assert len(merges) == 1
    from experiments.stable_ac.cov.meet import verify_covmeet as vc
    ends = []
    for ch in merges[0]["chains"]:
        ok, nseg, trunc = vc.verify_chain(ch)
        assert ok and not trunc
        ends.append(ch[-1]["rep"])
    assert ends[0] == ends[1] == merges[0]["rep"]


def test_cov_cycle_terminates_each_orbit_expanded_exactly_once(tmp_path, monkeypatch):
    """The infinite-loop scenario: a CoV graph that is a pure cycle A->B->C->A plus
    self-loops. The visited/expanded set must make the run TERMINATE by exhaustion
    with each orbit expanded exactly once — no requeue, no spin."""
    import experiments.stable_ac.cov.meet.covmeet as cm
    from experiments.stable_ac.cov.ladder import autcanon_fast as af
    trip = [af.aut_min((f"xxx{'y' * (i + 1)}", "xyxY"))[1] for i in range(3)]
    nxt = {trip[0]: trip[1], trip[1]: trip[2], trip[2]: trip[0]}

    def fake_expand(pairs):
        out = []
        for a, b in pairs:
            child = nxt[(a, b)]
            out.append((((a, b)), 2,
                        [(child, len(child[0]) + len(child[1]), "xy", "x", 0, 1)]))
        return out

    monkeypatch.setattr(cm, "_expand_chunk", fake_expand)
    seeds = [("t_cyc", *trip[0])]
    summary = run(str(tmp_path), seed_set="testCYC", seeds_override=seeds,
                  workers=0, wave=1, chunk=1, mem_guard_gb=0, log=lambda *a: None)
    assert "exhausted" in summary["stopped"]              # terminated, not looping
    store = _store(tmp_path, 1, tag="testCYC")
    assert len(store.expanded) == 3 == len(store.mask)    # each orbit exactly once
    assert store.frontier_size() == 0
    assert sorted(store.census.values()) == [(2, 1)] * 3  # one census per orbit, once


def test_expanded_orbit_is_never_requeued_on_re_reach(tmp_path):
    """Real data: after several waves, no expanded orbit may sit in the frontier,
    no orbit index repeats, and a resume expands strictly NEW orbits — the visited
    set does its job across sessions too."""
    _run(tmp_path, SEEDS_AB, 6)
    s1 = _store(tmp_path, 2)
    assert not (s1.expanded & set().union(*s1.frontier.values())
                if s1.frontier else set())
    assert len(s1.reps) == len(set(s1.reps))              # no orbit stored twice
    first = set(s1.expanded)
    _run(tmp_path, SEEDS_AB, 4)                           # resume
    s2 = _store(tmp_path, 2)
    assert first < s2.expanded                            # strictly grew...
    grown = len(s2.expanded) - len(first)
    assert 4 <= grown <= 4 + 2                            # budget, checked per wave
    assert not (s2.expanded & (set().union(*s2.frontier.values())
                               if s2.frontier else set()))


def test_snapshot_interval_adapts_to_write_cost():
    """The cadence must keep checkpoint overhead ~10%: a cheap write keeps the base
    interval, an expensive one stretches it to 10x its own cost."""
    assert covmeet._next_snap_interval(300, 0.5) == 300
    assert covmeet._next_snap_interval(300, 60) == 600
    assert covmeet._next_snap_interval(300, 1440) == 14400


# ------------------------------------------------------------- report generator

def test_report_refuses_unverified_and_writes_consistent_results(tmp_path):
    """report_covmeet is the ingestion gate: it must refuse a corrupt run and, on a
    good one, write per-class rows and a census that match the store exactly."""
    from experiments.stable_ac.cov.meet import report_covmeet
    out = tmp_path / "out"
    res = tmp_path / "res"
    _run(out, SEEDS_AB, 4)
    rc = report_covmeet.main([str(out), "--seed-set", "testAB",
                              "--results-dir", str(res), "--sample", "50"],
                             seeds_override=SEEDS_AB)
    assert rc == 0
    store = _store(out, 2)
    rows = list(csv.DictReader(open(res / "covmeet_classes.csv")))
    assert [r["name"] for r in rows] == ["t_a", "t_b"]
    for i, r in enumerate(rows):
        assert int(r["seed_mu"]) == store.seed_mu[i]
        assert int(r["best_mu"]) == store.best_mu[i]
    census = list(csv.DictReader(open(res / "covmeet_census.csv")))
    assert len(census) == len(store.expanded)
    md = open(res / "COVMEET.md").read()
    assert f"**2 / 2**" in md                             # classes remaining
    # corrupt both snapshots -> the verifier fails -> the report must refuse
    for p in snap_paths(str(out), "testAB"):
        with open(p, "r+b") as f:
            f.seek(10)
            f.write(b"garbage")
    rc = report_covmeet.main([str(out), "--seed-set", "testAB",
                              "--results-dir", str(tmp_path / "res2")],
                             seeds_override=SEEDS_AB)
    assert rc != 0
    assert not (tmp_path / "res2").exists()               # nothing written
