"""Mine the saved AC19 census certificates for consecutive-BS macro patterns.

Reads results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl (read-only)
and analyses three groups of solved rows:

  * every solved row with route == 'incumbent_restart'                 (612),
  * the 300 solved plain_s20 rows with the largest nodes_explored,
  * every solved row whose ROOT already carries a *stalled* consecutive-BS
    core - bs_gate(general=True) accepts and bs_preflight rejects with more
    than one stable letter                                             (584).

The third group is the one the residual 727 lives in; the first two turn out to
contain no consecutive-BS root at all, which is itself a reported result.

Writes, next to this file:
  path_mining_rows.jsonl        one record per analysed row
  unsolved_stalled_roots.json   AGGREGATE class counts for the stalled-BS roots
                                the census failed on (no row identities: the
                                val/test panels are hidden)

Usage:  PYTHONPATH=. python3 research/residual_20260909/theory/path_mining.py
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, exp_sums, inv, replay_move,
)
from research.supermoves_20260908.bs_preflight import donor_orientations, preflight
from research.supermoves_20260908.cheap_gates import (
    bs_gate, canonical_two_block_gate, one_occurrence_donor,
)
from research.supermoves_20260908.mid_search import bs_escape_feature

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bs_normal_form import analyse_pair as bs_class_of  # noqa: E402

ROWS_GLOB = "results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "path_mining_rows.jsonl")


# --------------------------------------------------------------------------
# consecutive-BS structure of a single state
# --------------------------------------------------------------------------

def bs_shapes(state):
    """[(relator index, m)] for every relator that is a BS(m, m+1) relator."""
    return [(i, donor_orientations(w)[0][2])
            for i, w in enumerate(state) if donor_orientations(w)]


def britton_data(donor, companion):
    """Signed stable-letter pattern of ``companion`` relative to a BS donor.

    Returns (signs, gaps, m) where ``signs[i]`` is the sign of the i-th stable
    letter read cyclically and ``gaps[i]`` the a-exponent between stable letter
    i and stable letter i+1 (cyclically).  ``None`` when ``donor`` is not a
    consecutive-BS relator.
    """
    orientations = donor_orientations(donor)
    if not orientations:
        return None
    a, b, m, n = orientations[0]
    positions = [i for i, c in enumerate(companion) if c.lower() == b.lower()]
    if not positions:
        return ([], [], m)
    signs = [1 if companion[i] == b else -1 for i in positions]
    gaps = []
    for j, start in enumerate(positions):
        end = positions[(j + 1) % len(positions)]
        between = companion[start + 1:end] if end > start else companion[start + 1:] + companion[:end]
        gaps.append(between.count(a) - between.count(inv(a)))
    return (signs, gaps, m)


def one_occurrence_certified(state):
    for donor in state:
        if not one_occurrence_donor(donor):
            continue
        (ax, ay), (bx, by) = exp_sums(state[0]), exp_sums(state[1])
        if abs(ax * by - ay * bx) == 1:
            return True
    return False


def classify_state(state):
    """The certified terminal family (if any) that closes at this state."""
    if len(state[0]) == 1 and len(state[1]) == 1 and state[0].lower() != state[1].lower():
        return "trivial"
    if canonical_two_block_gate(state):
        return "two_block_det1"
    if bs_gate(state, general=True) is not None and preflight(state).get("status") == "accept":
        return "bs_preflight_accept"
    if one_occurrence_certified(state):
        return "one_occurrence_det1"
    return None


# --------------------------------------------------------------------------
# step descriptors
# --------------------------------------------------------------------------

def step_descriptor(before, after, step, R0):
    """One saved mixed step, described relative to the ROOT BS relator R0."""
    if step["kind"] == "automorphism":
        images = step["images"]
        name = ",".join(f"{k}->{v}" for k, v in sorted(images.items()) if v != k)
        return {"kind": "aut", "name": name or "id",
                "dL": sum(map(len, after)) - sum(map(len, before))}
    target, jsign, k1, k2 = (int(v) for v in step["move"].split("_"))
    target_word = before[target - 1]
    role = "?" if R0 is None else ("R0" if target_word == R0 else "W")
    return {"kind": "sub", "target": target, "jsign": jsign, "role": role,
            "target_len": len(target_word), "donor_len": len(before[2 - target]),
            "dL": sum(map(len, after)) - sum(map(len, before)), "move": step["move"]}


def macro_signature(descriptors):
    parts = []
    for d in descriptors:
        parts.append("A[%s]" % d["name"] if d["kind"] == "aut"
                     else "S[%s%s]" % (d["role"], "+" if d["jsign"] == 1 else "-"))
    return " ".join(parts)


# --------------------------------------------------------------------------
# per-row analysis
# --------------------------------------------------------------------------

def analyse(row):
    pair = tuple(canon_pair(*row["pair"]))
    states = [tuple(s) for s in row["states"]]
    steps = row["steps"]
    assert states[0] == pair, (states[0], pair)

    gate = bs_gate(pair, general=True)
    check = preflight(pair)
    T, _ = bs_escape_feature(pair)
    klass = bs_class_of(pair) or {}

    R0 = W0 = None
    m0 = s0 = eps0 = None
    root_gaps = root_signs = None
    if gate is not None:
        a, b, relation, _companion, m0, _n = gate
        donor_index = 0 if canon_rel(relation) == pair[0] else 1
        R0, W0 = pair[donor_index], pair[1 - donor_index]
        data = britton_data(R0, W0)
        root_signs, root_gaps, _ = data
        s0 = len(root_signs)
        eps0 = sum(root_signs)

    descriptors = [step_descriptor(states[i], states[i + 1], steps[i], R0)
                   for i in range(len(steps))]

    certs = [classify_state(s) for s in states]
    first_cert = next((i for i, c in enumerate(certs) if c is not None), None)

    # --- root-anchored Britton trace: valid while R0 is still in the state ---
    anchored = []
    for i, state in enumerate(states):
        if R0 is None or R0 not in state:
            break
        other = state[1 - list(state).index(R0)] if state[0] != state[1] else state[0]
        other = state[0] if state[1] == R0 else state[1]
        entry = {"i": i, "other_len": len(other),
                 "stable_letters_raw": len(britton_data(R0, other)[0])}
        pf = preflight(state)
        entry["preflight"] = pf.get("status")
        entry["preflight_stable"] = pf.get("stable_letters")
        g = bs_gate(state, general=True)
        entry["gate_donor_is_R0"] = (g is not None
                                     and canon_rel(g[2]) == R0)
        anchored.append(entry)

    first_R_gone = next((i for i in range(1, len(states)) if R0 is not None
                         and R0 not in states[i]), None)
    first_R_gone_kind = (descriptors[first_R_gone - 1]["kind"] if first_R_gone else None)
    if first_R_gone and descriptors[first_R_gone - 1]["kind"] == "sub":
        first_R_gone_kind = "sub_" + descriptors[first_R_gone - 1]["role"]
    first_sub_on_R0 = next((i for i, d in enumerate(descriptors)
                            if d["kind"] == "sub" and d["role"] == "R0"), None)

    # --- how the first certified state is reached ---
    escape = None
    if first_cert is not None:
        state = states[first_cert]
        escape = {"index": first_cert, "class": certs[first_cert],
                  "state": list(state), "R0_present": R0 is not None and R0 in state}
        if certs[first_cert] == "bs_preflight_accept":
            g = bs_gate(state, general=True)
            escape["donor_is_R0"] = canon_rel(g[2]) == R0
            escape["donor_m"] = g[4]
        if first_cert > 0:
            escape["step"] = descriptors[first_cert - 1]
            escape["previous"] = list(states[first_cert - 1])

    return {
        "name": row["name"], "index": row["index"], "pair": list(pair),
        "route": row["route"], "nodes_explored": row["nodes_explored"],
        "elementary_count": row.get("elementary_count"),
        "n_steps": len(steps),
        "n_aut": sum(1 for d in descriptors if d["kind"] == "aut"),
        "n_sub": sum(1 for d in descriptors if d["kind"] == "sub"),
        "n_sub_on_R0": sum(1 for d in descriptors if d["kind"] == "sub" and d["role"] == "R0"),
        "aut_names": [d["name"] for d in descriptors if d["kind"] == "aut"],
        "root_bs_gate": gate is not None,
        "root_R": R0, "root_W": W0, "root_m": m0,
        "root_s": s0, "root_eps": eps0,
        "root_signs": root_signs, "root_gaps": root_gaps,
        "bs_label": klass.get("label"),
        "bs_reduced_s": klass.get("s"),
        "bs_eps": klass.get("eps"),
        "bs_alpha": klass.get("alpha"),
        "bs_beta": klass.get("beta"),
        "bs_reduced_signs": klass.get("reduced_signs"),
        "bs_reduced_gaps": klass.get("reduced_gaps"),
        "root_preflight": check.get("status"),
        "root_preflight_stable": check.get("stable_letters"),
        "root_T": T,
        "root_stalled": bool(gate is not None and check.get("status") == "reject"
                             and check.get("stable_letters", 0) > 1),
        "L0": sum(map(len, pair)), "L_trace": [sum(map(len, s)) for s in states],
        "bs_shapes_trace": [bs_shapes(s) for s in states],
        "anchored": anchored,
        "first_R_gone": first_R_gone, "first_R_gone_kind": first_R_gone_kind,
        "first_sub_on_R0": first_sub_on_R0,
        "first_certified": first_cert,
        "first_certified_class": certs[first_cert] if first_cert is not None else None,
        "escape": escape,
        "terminal_state": list(states[-1]), "terminal_class": certs[-1],
        "macro_prefix": macro_signature(descriptors[:5]),
        "macro_to_cert": (macro_signature(descriptors[:first_cert])
                          if first_cert is not None else None),
        "descriptors": descriptors,
        "states": [list(s) for s in states],
    }


# --------------------------------------------------------------------------
# loading / verification
# --------------------------------------------------------------------------

def root_is_stalled(pair):
    if bs_gate(pair, general=True) is None:
        return False
    check = preflight(pair)
    return check.get("status") == "reject" and check.get("stable_letters", 0) > 1


def load_rows():
    incumbent, plain, stalled, unsolved_stalled = [], [], [], []
    for path in sorted(glob.glob(ROWS_GLOB)):
        with open(path) as handle:
            for line in handle:
                row = json.loads(line)
                stalled_root = root_is_stalled(tuple(row["pair"]))
                if not row["solved"]:
                    if stalled_root:
                        unsolved_stalled.append(row)
                    continue
                if stalled_root:
                    stalled.append(row)
                if row["route"] == "incumbent_restart":
                    incumbent.append(row)
                elif row["route"] == "plain_s20":
                    plain.append(row)
    plain.sort(key=lambda r: (-r["nodes_explored"], r["index"]))
    return incumbent, plain[:300], stalled, unsolved_stalled


def verify_paths(records, limit=60):
    """Independently replay every substitution step of a sample of paths."""
    checked = failures = 0
    for record in records[:limit]:
        state = tuple(record["states"][0])
        ok = True
        for descriptor, nxt in zip(record["descriptors"], record["states"][1:]):
            if descriptor["kind"] != "sub":
                state = tuple(nxt)
                continue
            state = replay_move(state, tuple(int(v) for v in descriptor["move"].split("_")))
            if state != tuple(nxt):
                ok = False
                break
        checked += 1
        failures += not ok
    return checked, failures


def main():
    incumbent, plain, stalled, unsolved_stalled = load_rows()
    print(f"incumbent_restart solves {len(incumbent)}  plain_s20 top300 {len(plain)}  "
          f"stalled-BS-root solves {len(stalled)}  stalled-BS-root unsolved "
          f"{len(unsolved_stalled)}", file=sys.stderr)
    records, by_name = [], {}
    for group, rows in (("incumbent_restart", incumbent),
                        ("plain_s20_top300", plain),
                        ("stalled_bs_root", stalled)):
        for row in rows:
            if row["name"] in by_name:
                by_name[row["name"]]["group"] += "+" + group
                continue
            record = analyse(row)
            record["group"] = group
            by_name[row["name"]] = record
            records.append(record)
    with open(OUT, "w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    labels, necklaces = Counter(), Counter()
    for row in unsolved_stalled:
        info = bs_class_of(tuple(row["pair"])) or {}
        if info.get("label"):
            labels[str(tuple(info["label"]))] += 1
        else:
            necklaces["m=%d, s_red=%d, necklace=%s"
                      % (info.get("m"), info.get("s"),
                         tuple(info.get("reduced_signs", ())))] += 1
    with open(os.path.join(HERE, "unsolved_stalled_roots.json"), "w") as handle:
        json.dump({"note": "Aggregate only. Row identities are withheld because "
                           "the val/test panels are hidden.",
                   "stalled_bs_roots_unsolved_by_the_frozen_1k_policy":
                       len(unsolved_stalled),
                   "by_s3_class_label": dict(sorted(labels.items())),
                   "by_wide_necklace": dict(sorted(necklaces.items()))},
                  handle, indent=1)
    checked, failures = verify_paths([r for r in records if "stalled" in r["group"]])
    print(f"replayed substitutions of {checked} stalled-root paths, {failures} mismatches",
          file=sys.stderr)
    for key, value in sorted(Counter(r["group"] for r in records).items()):
        print(key, value, file=sys.stderr)
    print(f"wrote {OUT} ({len(records)} records)", file=sys.stderr)


if __name__ == "__main__":
    main()
