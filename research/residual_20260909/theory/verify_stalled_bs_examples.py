"""Machine verification for every certificate claimed in STALLED_BS_THEORY.md.

Each positive certificate is replayed twice: once as Definition 2.1 moves with
experiments.equivalence_classes.lib.words.replay_move, and once, after the
compact elementary decoder, as ordinary invert/swap/conjugate/multiply moves
with certificate_decoder.replay_elementary, which must return literal ['x','y'].

Usage: PYTHONPATH=. python3 research/residual_20260909/theory/verify_stalled_bs_examples.py
"""
from __future__ import annotations

import json
import os
import sys

from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_pair, canon_pair, canon_rel, replay_move,
)
from research.supermoves_20260908.bs_preflight import donor_orientations, preflight
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary
from research.supermoves_20260908.cheap_gates import (
    bs_gate, canonical_two_block_gate, one_occurrence_donor,
)
from research.supermoves_20260908.consecutive_bs import collapse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bs_normal_form import (  # noqa: E402
    analyse_pair, cancel, demotion_certificate, orient, reduce_plan, run_plan,
    transport_plan, word_from,
)

FAILURES = []


def check(name, condition, detail=""):
    status = "ok " if condition else "FAIL"
    print(f"  [{status}] {name} {detail}")
    if not condition:
        FAILURES.append(name)


def relator(m, a="x", b="y"):
    from experiments.equivalence_classes.lib.words import inv
    return canon_rel(inv(b) + a * m + b + inv(a) * (m + 1))


def planted(m, eps, gaps):
    """A pair (R_m, W) with the companion described by (eps, gaps)."""
    signs = [eps, eps, -eps]
    return canon_pair(relator(m), canon_rel(word_from(signs, list(gaps), "x", "y")))


def full_certificate(pair, states, steps):
    """Replay Definition 2.1 steps, then decode and replay elementary moves."""
    state = tuple(canon_pair(*pair))
    if list(state) != list(states[0]):
        return False, "states[0] is not the canonical input"
    for step, nxt in zip(steps, states[1:]):
        if step["kind"] != "substitution":
            return False, "unexpected step kind"
        state = replay_move(state, tuple(int(v) for v in step["move"].split("_")))
        if list(state) != list(nxt):
            return False, "replay_move disagreed with the recorded state"
    if not (len(state[0]) == 1 and len(state[1]) == 1 and state[0].lower() != state[1].lower()):
        return False, f"terminal is {state}, not a pair of distinct generators"
    moves = decode_elementary(list(pair), [list(s) for s in states], steps)
    final = replay_elementary(list(pair), moves)
    return final == ["x", "y"], f"{len(moves)} elementary moves -> {final}"


def demote_and_collapse(pair):
    """Rule BS-DEMOTE end to end: carries, then the consecutive-BS compiler."""
    built = demotion_certificate(pair)
    if not built["applicable"]:
        return None, built
    tail = collapse(tuple(built["final"]), budget=10_000, intermediate_cap=None)
    if not tail["solved"]:
        return None, dict(built, tail_reason=tail["reason"])
    states = built["states"] + [list(s) for s in tail["states"][1:]]
    steps = built["steps"] + tail["steps"]
    ok, detail = full_certificate(pair, states, steps)
    built = dict(built, tail_rewrites=tail["rewrites"], total_steps=len(steps),
                 verified=ok, detail=detail)
    return ok, built


# ---------------------------------------------------------------------------

def check_label_symmetries():
    print("A. class label is invariant under the 8 signed permutations")
    samples = [("YYXXXXyX", "YXXXXXyxxxxxx"), ("YYXXyx", "YXXXXXXyxxxxx"),
               ("YYXXyxx", "YXXXXXXXXyxxxxxxx"), ("YYXXyx", "YXXXyxx"),
               ("YYXXXyx", "YXXXXXXyxxxxx")]
    for pair in samples:
        base = analyse_pair(canon_pair(*pair))["label"]
        labels = set()
        for _name, image in SIGNED_PERMS:
            moved = apply_pair(canon_pair(*pair), image)
            info = analyse_pair(moved)
            labels.add(info.get("label") if info else None)
        check(f"label{base} constant on the relabelling orbit", labels == {base},
              f"orbit={sorted(labels, key=str)}")


def check_stall_invariance():
    print("B. Britton stall invariance on every mined solved path")
    path = os.path.join(HERE, "path_mining_rows.jsonl")
    if not os.path.exists(path):
        check("path_mining_rows.jsonl present", False, "(run path_mining.py first)")
        return
    total = accepts = rows = 0
    with open(path) as handle:
        for line in handle:
            record = json.loads(line)
            if "stalled_bs_root" not in record["group"]:
                continue
            rows += 1
            for entry in record["anchored"]:
                if entry["gate_donor_is_R0"]:
                    total += 1
                    accepts += entry["preflight"] == "accept"
    check("no preflight accept while the root BS relator is still the donor",
          accepts == 0, f"{accepts} accepts in {total} such states over {rows} paths")


def check_no_terminal_while_R_fixed():
    print("C. no census terminal is reachable while R is untouched (bounded cone)")
    for m in (2, 3, 5, 7):
        R = relator(m)
        hits = []
        for eps in (1, -1):
            Mv, Mw = (m + 1, m) if eps == 1 else (m, m + 1)
            for u in range(-4, 5):
                for v in range(-3 * Mv, 3 * Mv + 1):
                    if v == 0 or v % Mv == 0:
                        continue
                    for w in range(-3 * Mw, 3 * Mw + 1):
                        if w == 0 or w % Mw == 0:
                            continue
                        word = canon_rel(word_from([eps, eps, -eps], [u, v, w], "x", "y"))
                        state = canon_pair(R, word)
                        if len(state[0]) < 2 or len(state[1]) < 2:
                            continue
                        bs_shaped = bool(donor_orientations(word))
                        certified = (canonical_two_block_gate(state)
                                     or one_occurrence_donor(word)
                                     or one_occurrence_donor(R)
                                     or (bs_gate(state, general=True) is not None
                                         and preflight(state)["status"] == "accept"))
                        if certified or bs_shaped:
                            hits.append((eps, u, v, w, word, bs_shaped, certified))
        unexpected = [h for h in hits if (h[1], abs(h[2]), abs(h[3])) != (0, 1, 1)]
        check(f"m={m}: only (u,|v|,|w|)=(0,1,1) companions certify",
              not unexpected, f"{len(hits)} hits, {len(unexpected)} unexpected")


def check_demotion_positive():
    print("D. Rule BS-DEMOTE: positive certificates, replayed to (x, y)")
    cases = [
        ("planted m=5 class (5,1,4) - the class the 1k policy fails on",
         planted(5, 1, (0, 1, 4))),
        ("census ac19_42 class (2,1,1)", ("YYXXyx", "YXXXyxx")),
        ("census ac19_73 class (3,1,2)", ("YYXXXyxx", "YXXXXyxxx")),
        ("planted m=4 class (4,1,3)", planted(4, 1, (0, 1, 3))),
        ("planted m=6 class (6,1,5)", planted(6, 1, (0, 1, 5))),
        ("planted m=8 class (8,1,7)", planted(8, -1, (2, 1, -1))),
    ]
    for name, pair in cases:
        info = analyse_pair(canon_pair(*pair))
        ok, built = demote_and_collapse(pair)
        if ok is None:
            check(name, False, f"rule refused: {built.get('reason')}")
            continue
        check(name, ok,
              f"label={info['label']} carries={built['carries']} "
              f"collapse={built['tail_rewrites']} peakL={built['max_total_length']} "
              f"{built['detail']}")


def check_demotion_negative():
    print("E. Rule BS-DEMOTE: adversarial negatives (must refuse, cheaply)")
    cases = [
        ("dev row ac19_102, class (5,2,4)", ("YYXXyx", "YXXXXXXyxxxxx")),
        ("planted class (7,2,5)", planted(7, 1, (0, 6, 2))),
        ("planted m=5 class (5,2,3)", planted(5, 1, (0, 2, 3))),
        ("planted m=7 class (7,3,3)", planted(7, 1, (0, 3, 3))),
        ("pinchable companion (not stalled)", planted(3, 1, (0, 4, 3))),
        ("non-BS pair", ("xyxYXY", "xxyy")),
    ]
    for name, pair in cases:
        built = demotion_certificate(pair)
        check(name, not built["applicable"], f"refused with reason={built['reason']}")


def normal_state(pair):
    """Deterministic carry normal form: Britton-reduce, then (u,v,w)->(0,alpha,beta)."""
    oriented = orient(pair)
    if oriented is None:
        return None
    state, R, a, b, m, _n, signs, gaps = oriented
    plan, rsigns, rgaps = reduce_plan(signs, gaps, m)
    if len(rsigns) != 3:
        return None
    ran = run_plan(state, R, a, b, signs, gaps, plan, m)
    if ran is None:
        return None
    state, _states, _steps, rsigns, rgaps = ran
    eps = 1 if sum(rsigns) > 0 else -1
    start = next(i for i in range(3) if rsigns[i] == eps and rsigns[(i + 1) % 3] == eps)
    rsigns = rsigns[start:] + rsigns[:start]
    rgaps = rgaps[start:] + rgaps[:start]
    Mv, Mw = (m + 1, m) if eps == 1 else (m, m + 1)
    found = transport_plan(m, eps, tuple(rgaps), (0, rgaps[1] % Mv, rgaps[2] % Mw))
    if found is None:
        return None
    ran = run_plan(state, R, a, b, rsigns, rgaps, found[1], m)
    return None if ran is None else tuple(ran[0])


def check_class_transport():
    print("F. same label => common normal form after one relabelling")
    for left, right, name in [
            (("YYXXyx", "YXXXXXXyxxxxx"), planted(5, 1, (0, 4 + 6, 1 + 5)),
             "dev row ac19_102 vs a planted partner, class (5,2,4)"),
            (("YYXXyx", "YXXXyxx"), ("YYXXXyX", "YXXyxxx"),
             "two class (2,1,1) census rows")]:
        labels = [analyse_pair(canon_pair(*p))["label"] for p in (left, right)]
        check(f"{name}: same label", labels[0] == labels[1], str(labels))
        goal = normal_state(right)
        hit = None
        for permutation, image in SIGNED_PERMS:
            moved = apply_pair(canon_pair(*left), image)
            if normal_state(moved) == goal:
                hit = permutation
                break
        check(f"{name}: common normal form", hit is not None,
              f"via {hit} -> {goal}")


def check_census_family():
    print("H. Rule BS-DEMOTE covers every mined census row of class (m,1,m-1)")
    path = os.path.join(HERE, "path_mining_rows.jsonl")
    if not os.path.exists(path):
        check("path_mining_rows.jsonl present", False, "(run path_mining.py first)")
        return
    rows = []
    with open(path) as handle:
        for line in handle:
            record = json.loads(line)
            if "stalled_bs_root" not in record["group"]:
                continue
            info = analyse_pair(tuple(record["pair"]))
            if info.get("label") and info["label"][1:] == (1, info["m"] - 1):
                rows.append((record["name"], tuple(record["pair"]), info["label"]))
    check("demotable rows found in the census", bool(rows), f"{len(rows)} rows")
    sample = rows[::max(1, len(rows) // 12)][:12]
    bad = []
    for name, pair, label in sample:
        ok, built = demote_and_collapse(pair)
        if ok is not True:
            bad.append((name, label, built.get("reason")))
    check("sampled demotable rows all certify", not bad,
          f"{len(sample)} sampled, {len(bad)} failures {bad[:3]}")


def check_router_certificates():
    print("G. residual classes reachable with a full 1000-unit incumbent stage")
    from research.supermoves_20260908.root_router import search as router
    cases = [("dev row ac19_102, class (5,2,4)", ("YYXXyx", "YXXXXXXyxxxxx"))]
    if "--full" in sys.argv:
        # one non-dev class representative; only run under --full so a default
        # verification never searches a row that may sit in a hidden panel.
        cases.append(("a class (7,2,5) representative",
                      ("YYXXyxx", "YXXXXXXXXyxxxxxxx")))
    for name, pair in cases:
        result = router(canon_pair(*pair), budget=1000, use_high_core_escape=True)
        if not result["solved"]:
            check(name, False, f"router did not solve within 1000 units ({result['nodes_explored']})")
            continue
        moves = decode_elementary(list(pair), result["states"], result["steps"],
                                 result.get("elementary_tail"))
        final = replay_elementary(list(pair), moves)
        check(name, final == ["x", "y"],
              f"{result['nodes_explored']} units, {len(moves)} elementary moves -> {final}")


def check_full_census_batch():
    """Compile and replay Rule BS-DEMOTE for EVERY demotable census row."""
    import glob
    print("I. full census batch (--full): every demotable stalled root")
    rows = []
    for path in sorted(glob.glob(
            "results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl")):
        with open(path) as handle:
            for line in handle:
                row = json.loads(line)
                info = analyse_pair(tuple(row["pair"]))
                if info and info.get("status") == "stalled" and info.get("label") \
                        and info["label"][1:] == (1, info["m"] - 1):
                    rows.append((row["name"], tuple(row["pair"]), row["solved"], info["m"]))
    bad = []
    for name, pair, _solved, _m in rows:
        ok, _built = demote_and_collapse(pair)
        if ok is not True:
            bad.append(name)
    unsolved = sum(1 for _n, _p, solved, _m in rows if not solved)
    check("every demotable census row certifies and replays to (x,y)", not bad,
          f"{len(rows)} rows, {len(bad)} failures; "
          f"{unsolved} of them were unsolved by the 1k policy "
          f"(row identities withheld: possible val/test members)")


def main():
    check_label_symmetries()
    check_stall_invariance()
    check_no_terminal_while_R_fixed()
    check_demotion_positive()
    check_demotion_negative()
    check_class_transport()
    check_census_family()
    check_router_certificates()
    if "--full" in sys.argv:
        check_full_census_batch()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES: {FAILURES}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
