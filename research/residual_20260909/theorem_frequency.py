"""Frequency audit of the completion rules used by the frozen AC19 census.

Streams the 74 published certificate shards of
``results/heuristic_search/ac19_final_policy_full_1k`` and classifies every
solved row by the terminal (completion theorem) that actually closed it, then
computes route-level diagnostics and cheap-gate statistics on the residual.

Read-only: nothing under research/supermoves_20260908, results/ or data/ is
written or modified.  One thread; a few minutes end to end.

    PYTHONPATH=. python3 research/residual_20260909/theorem_frequency.py

Classification rule (exact, not heuristic, for the frozen policy):

  The runner stores ``states``/``steps`` for every solve and stores the key
  ``elementary_tail`` exactly when ``mid_search.complete`` returned a winner
  that carried one, i.e. ``middle_two_block`` or ``middle_primitive``
  (``terminal`` and ``middle_bs`` never carry a tail; ``middle_bs_escape``
  inherits the tail of its inner winner).  So:

  * tail present -> two_block if ``two_block.solve(states[-1])`` reproduces the
    stored tail byte for byte, else primitive one-occurrence (checked against
    ``cheap_gates.one_occurrence_donor``);
  * tail absent -> the last state is a pair of distinct single letters.  It is
    a consecutive-BS collapse iff some index ``i`` has an all-substitution
    suffix ``steps[i:]``, ``cheap_gates.bs_gate(states[i], general=True)``
    non-None, ``bs_preflight.preflight(states[i])['status'] == 'accept'`` and
    ``consecutive_bs.collapse(states[i]).states == states[i:]`` exactly.
    Otherwise the search itself reached (x, y): an ordinary terminal.
"""
from __future__ import annotations

import collections
import json
import math
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import abelian_det, apply_pair, canon_pair
from research.supermoves_20260908.bs_preflight import preflight
from research.supermoves_20260908.cheap_gates import (
    bs_gate, canonical_two_block_gate, one_occurrence_donor, two_block_gate)
from research.supermoves_20260908.christoffel_primitive_gate import (
    is_christoffel_primitive_canonical)
from research.supermoves_20260908.consecutive_bs import collapse as bs_collapse
from research.supermoves_20260908.DONOR_NORMALIZED_BS import inspect as donor_inspect
from research.supermoves_20260908.mid_search import bs_escape_feature, mixed_search
from research.supermoves_20260908.splice_power_family import canonical_family_gate
from research.supermoves_20260908.stable_power import canonical_donor_gate
from research.supermoves_20260908.strict_donor_route_fast import match as donor_match
from research.supermoves_20260908.two_block import solve as two_block_solve

CENSUS = ROOT / "results/heuristic_search/ac19_final_policy_full_1k"
OUT = Path(__file__).resolve().parent / "theorem_frequency.json"


# ---------------------------------------------------------------- word shape

def cyclic_runs(word):
    """Maximal cyclic runs of a freely+cyclically reduced word: [(letter, n)]."""
    if not word:
        return []
    runs = []
    for letter in word:
        if runs and runs[-1][0] == letter:
            runs[-1][1] += 1
        else:
            runs.append([letter, 1])
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0][1] += runs.pop()[1]
    return [(letter, n) for letter, n in runs]


def bs_donor_shape(word):
    """Recognize any HNN/Baumslag-Solitar donor  b^-1 a^p b a^q  (4 cyclic runs).

    Returns a dict with the unordered magnitudes {m, n}, whether the two
    a-runs have opposite signs (the *positive* BS(m,n) with b^-1 a^m b = a^n
    that ``consecutive_bs`` targets) or equal signs (a BS(m,-n) shape), or
    None when the word is not of that form.
    """
    runs = cyclic_runs(word)
    if len(runs) != 4:
        return None
    letters = [letter.lower() for letter, _ in runs]
    if letters[0] != letters[2] or letters[1] != letters[3] or letters[0] == letters[1]:
        return None
    for stable in (0, 1):
        b0, b1 = runs[stable], runs[(stable + 2) % 4]
        if b0[1] != 1 or b1[1] != 1 or b0[0] == b1[0]:
            continue  # stable letter must appear once with each sign
        a0, a1 = runs[(stable + 1) % 4], runs[(stable + 3) % 4]
        e0 = a0[1] if a0[0].islower() else -a0[1]
        e1 = a1[1] if a1[0].islower() else -a1[1]
        positive = (e0 > 0) != (e1 > 0)
        m, n = abs(e0), abs(e1)
        return {"m": min(m, n), "n": max(m, n), "positive_bs": positive,
                "consecutive": abs(m - n) == 1, "gcd": math.gcd(m, n)}
    return None


def stable_exponent_pm1(word, donor_shape_word):
    """Exponent of the donor's stable generator in ``word`` is +/-1?"""
    runs = cyclic_runs(donor_shape_word)
    letters = [letter.lower() for letter, _ in runs]
    for stable in (0, 1):
        b0, b1 = runs[stable], runs[(stable + 2) % 4]
        if b0[1] != 1 or b1[1] != 1 or b0[0] == b1[0]:
            continue
        g = letters[stable]
        exponent = sum(1 if c == g else -1 for c in word if c.lower() == g)
        return abs(exponent) == 1
    return False


# --------------------------------------------------------------- terminals

def bs_terminal_index(states, steps):
    """Largest i whose all-substitution suffix is exactly a BS collapse."""
    for i in range(len(states) - 2, -1, -1):
        if steps[i]["kind"] != "substitution":
            break
        gate = bs_gate(states[i], general=True)
        if gate is None:
            continue
        if preflight(states[i])["status"] != "accept":
            continue
        macro = bs_collapse(list(states[i]), budget=10000, intermediate_cap=None)
        if macro["solved"] and [tuple(s) for s in macro["states"]] == list(states[i:]):
            return i, gate
    return None, None


def bs_state_on_path(states):
    """(any general BS gate, any BS(1,2) gate, any preflight-accepting state)."""
    general = special = accept = False
    for state in states:
        gate = bs_gate(state, general=True)
        if gate is None:
            continue
        general = True
        if gate[4] == 1:
            special = True
        if not accept and preflight(state)["status"] == "accept":
            accept = True
    return general, special, accept


def hnn_donor_shape(word):
    """Coarser 4-run classification: b^-s a^p b^s a^q, any s >= 1, any signs."""
    runs = cyclic_runs(word)
    if len(runs) != 4:
        return None
    letters = [letter.lower() for letter, _ in runs]
    if letters[0] != letters[2] or letters[1] != letters[3] or letters[0] == letters[1]:
        return None
    for stable in (0, 1):
        b0, b1 = runs[stable], runs[(stable + 2) % 4]
        if b0[0] == b1[0] or b0[1] != b1[1]:
            continue
        a0, a1 = runs[(stable + 1) % 4], runs[(stable + 3) % 4]
        e0 = a0[1] if a0[0].islower() else -a0[1]
        e1 = a1[1] if a1[0].islower() else -a1[1]
        return {"stable_run": b0[1], "m": min(abs(e0), abs(e1)),
                "n": max(abs(e0), abs(e1)),
                "positive_bs": (e0 > 0) != (e1 > 0)}
    return None


# ------------------------------------------------- stage-1 prepass replay

def strict_donor_replay(pair, prepass_cap=250, budget=1000):
    """Replay ``final_policy.search`` stage 1 exactly, including the tail search.

    Returns ``(depth, gates, endpoint, tail)`` for the attempt that actually
    solved, or ``None``.  This is a faithful re-execution of the frozen policy
    (same charging, same evaluation caps, same terminal set), so the returned
    attempt is the one the census used -- no prefix guessing.
    """
    root = list(canon_pair(*pair))
    limit = min(prepass_cap, max(0, budget - 1))
    charged = 0
    for index in range(len(root)):
        if charged >= limit:
            return None
        route = donor_match(root[index], evaluation_cap=min(64, limit - charged))
        charged += route["input_analysis"]["evaluations"]
        if route["status"] != "match":
            continue
        if charged + len(route["maps"]) >= limit:
            continue
        states = [root]
        limited = False
        for image in route["maps"]:
            if sum(len(image[c.lower()]) for word in states[-1] for c in word) > 100_000:
                limited = True
                break
            states.append(list(apply_pair(states[-1], image)))
            charged += 1
        if limited:
            continue
        gates, _cost = donor_inspect(tuple(states[-1]))
        if not (gates["two_block"] or gates["one_occurrence_relators"]
                or (gates["bs_preflight"] or {}).get("status") == "accept"):
            continue
        tail = mixed_search(states[-1], "s20", budget=limit - charged, cap=None,
                            use_bs=True, general_bs=True, use_two_block=True,
                            use_primitive=True, use_bs_preflight=True)
        charged += tail["nodes_explored"]
        if tail["solved"]:
            return len(route["maps"]), gates, states, tail
    return None


# ------------------------------------------------------------------- main

def main(shard_limit=None, out=OUT):
    started = time.time()
    shards = sorted(CENSUS.glob("rows_*.jsonl"))
    if len(shards) != 74:
        raise SystemExit(f"expected 74 shards, found {len(shards)}")
    if shard_limit:
        shards = shards[:shard_limit]

    terminal = collections.Counter()
    terminal_by_route = collections.Counter()
    ordinary_detail = collections.Counter()
    units = collections.defaultdict(int)
    moves = collections.defaultdict(int)
    nodes_by_terminal = collections.defaultdict(list)
    bs_m_hist = collections.Counter()
    bs_pathonly = collections.Counter()
    root_bs = collections.Counter()
    bs_missed = collections.Counter()
    root_bs_by_terminal = collections.Counter()
    ambiguous = collections.Counter()

    strict_gate = collections.Counter()
    strict_depth = collections.Counter()
    strict_gate_by_terminal = collections.Counter()
    strict_depth_by_gate = collections.Counter()
    strict_winner = collections.Counter()
    strict_extra = collections.Counter()
    strict_mismatch = 0
    strict_replay_state_mismatch = 0

    plain_nodes = []
    plain_charges_list = []
    inc_nodes = {"s20_ordinary_T": [], "aut_edges": []}
    inc_arm = collections.Counter()

    residual = []
    route_nodes = collections.defaultdict(list)
    route_moves = collections.defaultdict(int)
    rows = solved = 0

    for shard in shards:
        with shard.open() as stream:
            for line in stream:
                row = json.loads(line)
                rows += 1
                route = row["route"]
                if not row["solved"]:
                    residual.append(row)
                    route_nodes[route + "|unsolved"].append(row["nodes_explored"])
                    continue
                solved += 1
                route_nodes[route + "|solved"].append(row["nodes_explored"])
                route_moves[route] += row.get("elementary_count", 0)
                states = [tuple(s) for s in row["states"]]
                steps = row["steps"]
                last = states[-1]
                has_tail = "elementary_tail" in row
                n_aut = sum(1 for s in steps if s["kind"] == "automorphism")
                single = (len(last[0]) == 1 and len(last[1]) == 1
                          and last[0].lower() != last[1].lower())

                # --- which theorem closed the row
                if has_tail:
                    kind = None
                    if canonical_two_block_gate(last):
                        certificate = two_block_solve(list(last))
                        if (certificate["solved"]
                                and certificate["elementary_moves"] == row["elementary_tail"]):
                            kind = "two_block"
                    if kind is None:
                        if any(one_occurrence_donor(w) for w in last):
                            kind = "primitive_one_occurrence"
                            if canonical_two_block_gate(last):
                                ambiguous["tail_row_two_block_gate_but_primitive"] += 1
                        else:
                            kind = "tail_unclassified"
                            ambiguous["tail_unclassified"] += 1
                else:
                    if not single:
                        ambiguous["no_tail_last_state_not_single_letters"] += 1
                    index, gate = bs_terminal_index(states, steps)
                    if index is not None and route != "plain_s20":
                        kind = "consecutive_bs"
                        bs_m_hist[gate[4]] += 1
                    else:
                        kind = "ordinary_terminal"
                        if index is not None:
                            # plain_search_fast has no completion macros at all,
                            # so this is the greedy search independently walking
                            # the deterministic BS collapse path.
                            ambiguous["plain_s20_path_matches_bs_collapse"] += 1

                terminal[kind] += 1
                terminal_by_route[(kind, route)] += 1
                units[kind] += row["nodes_explored"]
                moves[kind] += row.get("elementary_count", 0)
                nodes_by_terminal[kind].append(row["nodes_explored"])
                if kind == "ordinary_terminal":
                    ordinary_detail[(route, "aut" if n_aut else "no_aut")] += 1

                # --- BS donors seen anywhere on the certified path
                general, special, accept = bs_state_on_path(states)
                bs_pathonly["any_general_bs_state"] += general
                bs_pathonly["any_bs12_state"] += special
                bs_pathonly["any_bs_preflight_accept_state"] += accept
                if general and not special:
                    bs_pathonly["general_bs_but_never_m1"] += 1
                if accept and kind != "consecutive_bs":
                    bs_missed[(kind, route)] += 1
                rgate = bs_gate(states[0], general=True)
                root_bs["root_general_bs"] += rgate is not None
                if rgate is not None:
                    root_bs["root_bs_m_%d" % rgate[4]] += 1
                    root_bs["root_bs12"] += rgate[4] == 1
                    root_bs_by_terminal[("m1" if rgate[4] == 1 else "m>1", kind)] += 1

                # --- route diagnostics
                if route == "plain_s20":
                    plain_nodes.append(row["nodes_explored"])
                    plain_charges_list.append(row.get("plain_charges", 0))
                elif route == "incumbent_restart":
                    value, _check = bs_escape_feature(canon_pair(*row["pair"]))
                    arm = "s20_ordinary_T" if value > 0 else "aut_edges"
                    inc_arm[(arm, "solved")] += 1
                    inc_nodes[arm].append(row["nodes_explored"])
                elif route == "strict_donor":
                    picked = strict_donor_replay(row["pair"])
                    if picked is None:
                        strict_mismatch += 1
                    else:
                        depth, gates, pstates, tail = picked
                        replayed = [tuple(w) for w in pstates] + \
                                   [tuple(w) for w in tail["states"][1:]]
                        if replayed != states:
                            strict_replay_state_mismatch += 1
                        flags = []
                        if gates["two_block"]:
                            flags.append("two_block")
                        if gates["one_occurrence_relators"]:
                            flags.append("one_occurrence")
                        if (gates["bs_preflight"] or {}).get("status") == "accept":
                            flags.append("bs_preflight_accept")
                        label = "+".join(flags)
                        strict_gate[label] += 1
                        strict_depth[depth] += 1
                        strict_depth_by_gate[(label, depth)] += 1
                        strict_gate_by_terminal[(label, kind)] += 1
                        strict_winner[tail.get("winner", "?")] += 1
                        if len(states) == depth + 1:
                            strict_extra["tail_added_no_states|" + kind] += 1
                        strict_extra["endpoint_min_relator_len_%d|%s" % (
                            min(map(len, pstates[-1])), kind)] += 1

    # unsolved rows: incumbent arm + cheap gates on the root
    residual_gates = collections.Counter()
    residual_bs = collections.Counter()
    residual_blocks = collections.Counter()
    residual_lengths = []
    for row in residual:
        route = row["route"]
        rootpair = canon_pair(*row["pair"])
        if route == "incumbent_restart":
            value, _check = bs_escape_feature(rootpair)
            arm = "s20_ordinary_T" if value > 0 else "aut_edges"
            inc_arm[(arm, "unsolved")] += 1
            inc_nodes[arm].append(row["nodes_explored"])
        residual_gates["rows"] += 1
        residual_gates["route_" + route] += 1
        residual_gates["abelian_det_pm1"] += abs(abelian_det(*rootpair)) == 1
        residual_gates["two_block_gate"] += bool(two_block_gate(rootpair))
        residual_gates["canonical_two_block_gate"] += bool(canonical_two_block_gate(rootpair))
        residual_gates["one_occurrence_donor"] += any(one_occurrence_donor(w) for w in rootpair)
        gate = bs_gate(rootpair, general=True)
        residual_gates["bs_gate_general"] += gate is not None
        residual_gates["bs_gate_bs12"] += bs_gate(rootpair, general=False) is not None
        if gate is not None:
            check = preflight(rootpair)
            status = check["status"]
            residual_gates["bs_preflight_" + status] += 1
            residual_gates["bs_gate_route_" + route] += 1
            residual_bs["recognized_m_%d" % gate[4]] += 1
            if status == "reject":
                residual_bs["reject_stable_letters_%d" % check.get("stable_letters", -1)] += 1
            else:
                residual_bs["accept_predicted_rewrites_%d" % (
                    check["pinches"] + 2 + abs(check["base_exponent"]))] += 1
                residual_bs["accept_route_" + route] += 1
        residual_gates["stable_power_gate"] += bool(canonical_donor_gate(rootpair))
        residual_gates["splice_power_gate"] += bool(canonical_family_gate(rootpair))
        residual_gates["christoffel_primitive"] += any(
            is_christoffel_primitive_canonical(w) for w in rootpair)

        # generalized BS donor shape at the root (independent of the recognizer)
        shapes = [(i, bs_donor_shape(w)) for i, w in enumerate(rootpair)]
        shapes = [(i, s) for i, s in shapes if s is not None]
        if shapes:
            residual_bs["any_bs_donor_shape"] += 1
            best = shapes[0][1]
            residual_bs["positive_bs" if best["positive_bs"] else "negative_bs"] += 1
            residual_bs["mn_%d_%d" % (best["m"], best["n"])] += 1
            if best["positive_bs"]:
                residual_bs["consecutive" if best["consecutive"] else "nonconsecutive"] += 1
                if not best["consecutive"] or best["gcd"] > 1:
                    residual_bs["blocked_by_consecutivity_or_gcd"] += 1
                companion = rootpair[1 - shapes[0][0]]
                if stable_exponent_pm1(companion, rootpair[shapes[0][0]]):
                    residual_bs["companion_stable_exponent_pm1"] += 1
        for word in rootpair:
            shape = hnn_donor_shape(word)
            if shape is None:
                continue
            residual_bs["hnn4_stable_run_%d_%s" % (
                shape["stable_run"],
                "pos" if shape["positive_bs"] else "neg")] += 1
            if shape["stable_run"] == 1 and shape["positive_bs"]:
                residual_bs["hnn4_consec" if abs(shape["m"] - shape["n"]) == 1
                            else "hnn4_nonconsec"] += 1
                if math.gcd(shape["m"], shape["n"]) > 1:
                    residual_bs["hnn4_gcd_gt_1"] += 1
        residual_lengths.append(sum(map(len, rootpair)))
        blocks = tuple(sorted(len(cyclic_runs(w)) for w in rootpair))
        residual_blocks["blocks_%d_%d" % blocks] += 1
        residual_blocks["some_relator_4_blocks"] += 4 in blocks
        residual_blocks["both_relators_le_4_blocks"] += max(blocks) <= 4
        residual_blocks["some_relator_le_2_blocks"] += min(blocks) <= 2

    def describe(values):
        if not values:
            return {}
        values = sorted(values)
        return {"count": len(values), "min": values[0], "max": values[-1],
                "mean": round(statistics.fmean(values), 2),
                "median": values[len(values) // 2],
                "p90": values[int(0.9 * (len(values) - 1))],
                "sum": sum(values),
                "at_budget_1000": sum(1 for v in values if v >= 1000)}

    report = {
        "census": str(CENSUS.relative_to(ROOT)),
        "rows": rows,
        "solved": solved,
        "unsolved": len(residual),
        "terminals": dict(terminal),
        "terminal_units": {k: units[k] for k in terminal},
        "terminal_elementary_moves": {k: moves[k] for k in terminal},
        "terminal_nodes_distribution": {k: describe(v) for k, v in nodes_by_terminal.items()},
        "route_nodes": {k: describe(v) for k, v in sorted(route_nodes.items())},
        "route_elementary_moves": dict(sorted(route_moves.items())),
        "terminal_by_route": {f"{k}|{r}": v for (k, r), v in sorted(terminal_by_route.items())},
        "ordinary_terminal_detail": {f"{r}|{a}": v for (r, a), v in sorted(ordinary_detail.items())},
        "consecutive_bs_m_histogram": dict(sorted(bs_m_hist.items())),
        "bs_donors_on_solved_paths": dict(bs_pathonly),
        "bs_donors_at_solved_root": dict(sorted(root_bs.items())),
        "bs_root_by_terminal": {f"{m}|{k}": v for (m, k), v in sorted(root_bs_by_terminal.items())},
        "bs_accepting_state_on_path_but_other_terminal": {
            f"{k}|{r}": v for (k, r), v in sorted(bs_missed.items())},
        "ambiguous": dict(ambiguous),
        "strict_donor": {
            "admitting_gate": dict(strict_gate),
            "descent_depth": dict(sorted(strict_depth.items())),
            "gate_by_terminal": {f"{g}|{t}": v for (g, t), v in sorted(strict_gate_by_terminal.items())},
            "depth_by_gate": {f"{g}|{d}": v for (g, d), v in sorted(strict_depth_by_gate.items())},
            "mid_search_winner": dict(strict_winner),
            "endpoint_shape": dict(sorted(strict_extra.items())),
            "unreplayed_rows": strict_mismatch,
            "replay_state_mismatch": strict_replay_state_mismatch,
        },
        "plain_s20": {
            "total_nodes": describe(plain_nodes),
            "plain_stage_charges": describe(plain_charges_list),
        },
        "incumbent_restart": {
            "arm": {f"{a}|{s}": v for (a, s), v in sorted(inc_arm.items())},
            "nodes": {a: describe(v) for a, v in inc_nodes.items()},
        },
        "residual": {
            "gates": dict(residual_gates),
            "bs_shape": dict(sorted(residual_bs.items())),
            "block_shape": dict(sorted(residual_blocks.items())),
            "total_length": describe(residual_lengths),
        },
        "elapsed_seconds": round(time.time() - started, 1),
    }
    out.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("rows", "solved", "unsolved", "terminals", "ambiguous",
                       "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    main(limit, target)
