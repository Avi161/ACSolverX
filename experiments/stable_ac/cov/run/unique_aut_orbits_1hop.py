"""One-hop unique Aut(F2) orbit census over the 113 solved + 124 unsolved seeds.

Loads the solved Aut-orbit table and the unsolved ACA class reps, inserts each
as a seed orbit, then expands every seed by one subword-CoV hop. Pure relabels
(``aut_canon`` unchanged) are dropped; **every** moved CoV is kept as an edge
(no first-wins on Aut-orbit). Orbit rows are still unique by Aut-rep.
Seed-to-seed landings are alerted live (especially unsolved->solved).

Also asserts the ``n_subs=1 => relabel`` fact: zero ``n_subs=1`` CoVs may leave
the parent Aut-orbit (see ``AUTOMORPHISMS_COV.md``).

Outputs under ``data/cov/unique_aut_orbits_1hop/``:

* ``unique_aut_orbits_1hop.csv`` — primary table: one row per unique Aut orbit (PK ``orbit_id``)

Companion tables under ``related/``:

* ``unique_aut_orbits_1hop_classes.csv`` — seed classes (PK ``class_id``; holds ``example``)
* ``unique_aut_orbits_1hop_parents.csv`` — which classes reach each orbit
  (FK ``orbit_id``, FK ``parent_class``)
* ``unique_aut_orbits_1hop_edges.csv`` — every moved CoV recipe (parent, z, …)
* ``unique_aut_orbits_1hop_seed_hits.csv`` — CoVs that land on another seed
* ``unique_aut_orbits_1hop_summary.json`` — counts + ``n_subs`` histograms
* ``n_subs_histogram.csv`` — ``n_subs`` × (all / relabel / moved) table
* ``moved_orbits_by_source_side.csv`` — new orbits from solved vs unsolved seeds

CLI::

    .venv/bin/python3 -m experiments.stable_ac.cov.run.unique_aut_orbits_1hop
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time


def _repo_root(start=None):
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (experiments/ + data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.stable_ac.cov import cov  # noqa: E402
from experiments.stable_ac.cov.ladder import mu_ladder_big as mlb  # noqa: E402

SOLVED_CSV = os.path.join(
    ROOT, "results/equivalence_classes/ms1190_tables/solved_640_aut_orbits.csv")
UNSOLVED_CSV = os.path.join(ROOT, "data/ms_unsolved_reps/aca_124.csv")
OUT_DIR = os.path.join(ROOT, "data/cov/unique_aut_orbits_1hop")
RELATED_DIR = os.path.join(OUT_DIR, "related")
CAP = 24
SPOT_CHECK = 20

ORBIT_COLS = [
    "orbit_id", "kind", "source_side", "rep_r1", "rep_r2", "mu", "n_parents",
    "L", "K", "MK", "S", "xyimb",
]
CLASS_COLS = ["class_id", "side", "example"]
PARENT_COLS = ["orbit_id", "parent_class"]
EDGE_COLS = [
    "from_class", "from_side", "parent_r1", "parent_r2",
    "z", "iso_gen", "iso_index", "n_subs", "out_r1", "out_r2",
    "to_orbit_id", "to_rep_r1", "to_rep_r2", "to_mu", "category",
]
HIT_COLS = [
    "category", "from_class", "from_side", "to_class", "to_side",
    "z", "iso_gen", "iso_index", "n_subs", "out_r1", "out_r2",
    "to_rep_r1", "to_rep_r2",
]


def _feat(r1, r2):
    v = phi(r1, r2)
    idx = {f: i for i, f in enumerate(FEATURES)}
    return {
        "L": v[idx["L"]],
        "K": v[idx["K"]],
        "MK": v[idx["MK"]],
        "S": v[idx["S"]],
        "xyimb": v[idx["xyimb"]],
    }


def _load_seeds():
    seeds = []
    with open(SOLVED_CSV) as f:
        for r in csv.DictReader(f):
            example = (r["cells"].split()[0] if r.get("cells") else r["aut_id"])
            seeds.append({
                "class_id": r["aut_id"],
                "side": "solved",
                "r1": r["rep_r1"],
                "r2": r["rep_r2"],
                "example": example,
            })
    with open(UNSOLVED_CSV) as f:
        for r in csv.DictReader(f):
            example = (r["members"].split()[0] if r.get("members") else r["name"])
            seeds.append({
                "class_id": r["name"],
                "side": "unsolved",
                "r1": r["r1"],
                "r2": r["r2"],
                "example": example,
            })
    n_sol = sum(1 for s in seeds if s["side"] == "solved")
    n_uns = sum(1 for s in seeds if s["side"] == "unsolved")
    if (n_sol, n_uns) != (113, 124):
        raise RuntimeError(f"expected 113+124 seeds, got {n_sol}+{n_uns}")
    return seeds


def _hit_category(from_side, to_side):
    return f"{from_side}_to_{to_side}"


def _alert(hit):
    cat = hit["category"]
    tag = ("*** UNSOLVED->SOLVED ***" if cat == "unsolved_to_solved"
           else "*** SOLVED->UNSOLVED ***" if cat == "solved_to_unsolved"
           else "*** SEED HIT ***")
    print(f"{tag} {hit['from_class']} --[{hit['z']}|{hit['iso_gen']}|"
          f"{hit['iso_index']}]--> {hit['to_class']} ({cat})", flush=True)


def run(cap=CAP):
    t0 = time.monotonic()
    if mlb._FAST_AVAILABLE:
        mlb.FAST_CANON = True
        mlb._warm_canon()
    else:
        mlb.FAST_CANON = False

    seeds = _load_seeds()
    memo = {}
    seed_by_rep = {}
    seed_meta = {}  # class_id -> seed dict
    orbits = {}     # rep -> orbit record (pre-id)

    # ---- insert seeds -------------------------------------------------------
    for s in seeds:
        mu, rep = mlb._orbit_memo((s["r1"], s["r2"]), memo)
        # rep must be the Aut-minimal form of the seed strings
        if rep != (s["r1"], s["r2"]):
            # still accept: store under true Aut-rep, keep seed strings as parent
            pass
        if rep in seed_by_rep:
            raise RuntimeError(
                f"duplicate seed Aut-rep: {seed_by_rep[rep]['class_id']} and "
                f"{s['class_id']}")
        seed_by_rep[rep] = s
        seed_meta[s["class_id"]] = s
        feats = _feat(rep[0], rep[1])
        orbits[rep] = {
            "kind": "seed",
            "mu": mu,
            "rep": rep,
            "parents": {s["class_id"]: s["example"]},
            "sides": {s["side"]},
            **feats,
        }

    # ---- expand one hop -----------------------------------------------------
    # Every moved CoV from enumerate_cov is kept as an edge (no first-wins on
    # Aut-orbit). Orbit table is one row per Aut-rep only — CoV recipes live
    # in edges.csv / seed_hits.csv.
    edges = []
    seed_hits = []
    n_cov_total = 0
    n_relabel = 0
    n_moved_cov = 0
    n_subs1_total = 0
    n_subs1_moved = 0          # must stay 0 (AUTOMORPHISMS_COV.md)
    n_subs_hist_all = {}       # n_subs -> count over every CoV
    n_subs_hist_relabel = {}
    n_subs_hist_moved = {}

    class_to_rep = {ss["class_id"]: r for r, ss in seed_by_rep.items()}

    for i, s in enumerate(seeds):
        parent_rep = class_to_rep[s["class_id"]]
        all_cov = cov.enumerate_cov(
            str_to_word(s["r1"]), str_to_word(s["r2"]),
            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
            reject_len=cov.REJECT_LEN)
        n_cov_total += len(all_cov)

        for c in all_cov:
            o1, o2 = word_to_str(c.r1), word_to_str(c.r2)
            mu, crep = mlb._orbit_memo((o1, o2), memo)
            z = word_to_str(c.z_word)
            ns = int(c.n_subs)
            n_subs_hist_all[ns] = n_subs_hist_all.get(ns, 0) + 1
            if ns == 1:
                n_subs1_total += 1

            if crep == parent_rep:
                n_relabel += 1
                n_subs_hist_relabel[ns] = n_subs_hist_relabel.get(ns, 0) + 1
                continue

            # moved
            n_moved_cov += 1
            n_subs_hist_moved[ns] = n_subs_hist_moved.get(ns, 0) + 1
            if ns == 1:
                n_subs1_moved += 1
                print(f"*** VIOLATION n_subs=1 moved *** "
                      f"{s['class_id']} z={z} iso={c.iso_gen}/{c.iso_index} "
                      f"-> {crep}", flush=True)

            category = ""
            if crep in seed_by_rep and seed_by_rep[crep]["class_id"] != s["class_id"]:
                tgt = seed_by_rep[crep]
                category = _hit_category(s["side"], tgt["side"])
                hit = {
                    "category": category,
                    "from_class": s["class_id"],
                    "from_side": s["side"],
                    "to_class": tgt["class_id"],
                    "to_side": tgt["side"],
                    "z": z,
                    "iso_gen": c.iso_gen,
                    "iso_index": c.iso_index,
                    "n_subs": ns,
                    "out_r1": o1,
                    "out_r2": o2,
                    "to_rep_r1": crep[0],
                    "to_rep_r2": crep[1],
                }
                seed_hits.append(hit)
                _alert(hit)

            if crep not in orbits:
                feats = _feat(crep[0], crep[1])
                orbits[crep] = {
                    "kind": "moved_cov",
                    "mu": mu,
                    "rep": crep,
                    "parents": {},
                    "sides": set(),
                    **feats,
                }
            rec = orbits[crep]
            rec["parents"][s["class_id"]] = s["example"]
            rec["sides"].add(s["side"])

            edges.append({
                "from_class": s["class_id"],
                "from_side": s["side"],
                "parent_r1": s["r1"],
                "parent_r2": s["r2"],
                "z": z,
                "iso_gen": c.iso_gen,
                "iso_index": c.iso_index,
                "n_subs": ns,
                "out_r1": o1,
                "out_r2": o2,
                "to_rep": crep,
                "to_mu": mu,
                "category": category,
            })

        if (i + 1) % 20 == 0 or i + 1 == len(seeds):
            print(f"  [{i+1}/{len(seeds)}] {s['class_id']}  "
                  f"orbits={len(orbits)} edges={len(edges)} "
                  f"seed_hits={len(seed_hits)}", flush=True)

    if n_subs1_moved != 0:
        raise RuntimeError(
            f"n_subs=1 produced {n_subs1_moved} moved CoVs "
            f"(expected 0 — every n_subs=1 must be a relabel)")

    # ---- assign orbit ids; parents / classes as FK tables --------------------
    ordered = sorted(orbits.items(),
                     key=lambda kv: (kv[1]["mu"], kv[0][0], kv[0][1]))
    rep_to_id = {}
    orbit_rows = []
    parent_rows = []
    for i, (rep, rec) in enumerate(ordered):
        oid = f"orb_{i:04d}"
        rep_to_id[rep] = oid
        sides = rec["sides"]
        if sides == {"solved"}:
            source_side = "solved"
        elif sides == {"unsolved"}:
            source_side = "unsolved"
        else:
            source_side = "both"
        orbit_rows.append({
            "orbit_id": oid,
            "kind": rec["kind"],
            "source_side": source_side,
            "rep_r1": rep[0],
            "rep_r2": rep[1],
            "mu": rec["mu"],
            "n_parents": len(rec["parents"]),
            "L": rec["L"],
            "K": rec["K"],
            "MK": rec["MK"],
            "S": rec["S"],
            "xyimb": rec["xyimb"],
        })
        for class_id in sorted(rec["parents"]):
            parent_rows.append({
                "orbit_id": oid,
                "parent_class": class_id,
            })

    class_rows = [
        {
            "class_id": s["class_id"],
            "side": s["side"],
            "example": s["example"],
        }
        for s in sorted(seeds, key=lambda x: x["class_id"])
    ]

    edge_rows = []
    for e in edges:
        edge_rows.append({
            "from_class": e["from_class"],
            "from_side": e["from_side"],
            "parent_r1": e["parent_r1"],
            "parent_r2": e["parent_r2"],
            "z": e["z"],
            "iso_gen": e["iso_gen"],
            "iso_index": e["iso_index"],
            "n_subs": e["n_subs"],
            "out_r1": e["out_r1"],
            "out_r2": e["out_r2"],
            "to_orbit_id": rep_to_id[e["to_rep"]],
            "to_rep_r1": e["to_rep"][0],
            "to_rep_r2": e["to_rep"][1],
            "to_mu": e["to_mu"],
            "category": e["category"],
        })

    # ---- spot-check: slow aut_canon + edge replay ---------------------------
    slow_ok = 0
    for row in orbit_rows[:SPOT_CHECK]:
        t, rep, _ = aut_canon((row["rep_r1"], row["rep_r2"]))
        if rep != (row["rep_r1"], row["rep_r2"]) or t != int(row["mu"]):
            raise RuntimeError(
                f"slow aut_canon mismatch on {row['orbit_id']}: "
                f"fast={(row['mu'], (row['rep_r1'], row['rep_r2']))} "
                f"slow={(t, rep)}")
        slow_ok += 1

    replay_ok = 0
    for e in edge_rows[:SPOT_CHECK]:
        branches = cov.cov_branches(
            str_to_word(e["parent_r1"]), str_to_word(e["parent_r2"]),
            str_to_word(e["z"]), iso_gen=e["iso_gen"],
            default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
            reject_len=cov.REJECT_LEN)
        match = [b for b in branches if b.iso_index == int(e["iso_index"])]
        if not match:
            raise RuntimeError(f"no branch for edge {e['from_class']} z={e['z']}")
        got = (word_to_str(match[0].r1), word_to_str(match[0].r2))
        want = (e["out_r1"], e["out_r2"])
        if got != want:
            raise RuntimeError(
                f"replay mismatch {e['from_class']} z={e['z']}: "
                f"got={got} want={want}")
        replay_ok += 1

    # ---- asserts ------------------------------------------------------------
    reps = [(r["rep_r1"], r["rep_r2"]) for r in orbit_rows]
    if len(reps) != len(set(reps)):
        raise RuntimeError("duplicate Aut-reps in orbit table")
    seed_ids = {s["class_id"] for s in seeds}
    seed_rows = [r for r in orbit_rows if r["kind"] == "seed"]
    if len(seed_rows) != 237:
        raise RuntimeError(f"expected 237 seed orbits, got {len(seed_rows)}")
    seed_oid = {r["orbit_id"] for r in seed_rows}
    covered = {p["parent_class"] for p in parent_rows
               if p["orbit_id"] in seed_oid}
    if covered != seed_ids:
        raise RuntimeError(f"seed coverage mismatch: missing "
                           f"{seed_ids - covered} extra {covered - seed_ids}")
    class_ids = {c["class_id"] for c in class_rows}
    if class_ids != seed_ids:
        raise RuntimeError("classes table does not match seed set")
    orphan_parents = {p["parent_class"] for p in parent_rows} - class_ids
    if orphan_parents:
        raise RuntimeError(f"parent_class FK orphans: {orphan_parents}")
    orphan_orbits = {p["orbit_id"] for p in parent_rows} - {
        r["orbit_id"] for r in orbit_rows}
    if orphan_orbits:
        raise RuntimeError(f"orbit_id FK orphans in parents: {orphan_orbits}")
    for e in edge_rows:
        if not e["z"]:
            raise RuntimeError(f"edge from {e['from_class']} missing z")

    hit_counts = {
        "unsolved_to_solved": 0,
        "solved_to_unsolved": 0,
        "solved_to_solved": 0,
        "unsolved_to_unsolved": 0,
    }
    for h in seed_hits:
        hit_counts[h["category"]] = hit_counts.get(h["category"], 0) + 1

    n_seed_orbits = sum(1 for r in orbit_rows if r["kind"] == "seed")
    n_moved_orbits = sum(1 for r in orbit_rows if r["kind"] == "moved_cov")
    side_counts = {"solved": 0, "unsolved": 0, "both": 0}
    for r in orbit_rows:
        side_counts[r["source_side"]] += 1

    wall = time.monotonic() - t0
    summary = {
        "n_seeds": 237,
        "n_seeds_solved": 113,
        "n_seeds_unsolved": 124,
        "n_cov_total": n_cov_total,
        "n_relabels_dropped": n_relabel,
        "n_moved_cov_applications": n_moved_cov,
        "n_unique_orbits": len(orbit_rows),
        "n_seed_orbits": n_seed_orbits,
        "n_moved_orbits": n_moved_orbits,
        "n_edges": len(edge_rows),
        "n_seed_hits": len(seed_hits),
        "seed_hit_counts": hit_counts,
        "source_side_counts": side_counts,
        "moved_orbits_by_source_side": {
            "solved_seeds_only": sum(
                1 for r in orbit_rows
                if r["kind"] == "moved_cov" and r["source_side"] == "solved"),
            "unsolved_seeds_only": sum(
                1 for r in orbit_rows
                if r["kind"] == "moved_cov" and r["source_side"] == "unsolved"),
            "both": sum(
                1 for r in orbit_rows
                if r["kind"] == "moved_cov" and r["source_side"] == "both"),
        },
        "n_subs1_total": n_subs1_total,
        "n_subs1_moved": n_subs1_moved,
        "n_subs1_all_relabel": n_subs1_moved == 0,
        "n_subs_hist_all": {str(k): n_subs_hist_all[k]
                            for k in sorted(n_subs_hist_all)},
        "n_subs_hist_relabel": {str(k): n_subs_hist_relabel[k]
                                for k in sorted(n_subs_hist_relabel)},
        "n_subs_hist_moved": {str(k): n_subs_hist_moved[k]
                              for k in sorted(n_subs_hist_moved)},
        "cap": cap,
        "family": cov.SUBWORD_FAMILY_TAG,
        "fast_canon": bool(mlb.FAST_CANON),
        "slow_aut_canon_spot_check": slow_ok,
        "edge_replay_spot_check": replay_ok,
        "wall_seconds": round(wall, 2),
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(RELATED_DIR, exist_ok=True)
    orbit_path = os.path.join(OUT_DIR, "unique_aut_orbits_1hop.csv")
    class_path = os.path.join(RELATED_DIR, "unique_aut_orbits_1hop_classes.csv")
    parent_path = os.path.join(RELATED_DIR, "unique_aut_orbits_1hop_parents.csv")
    edge_path = os.path.join(RELATED_DIR, "unique_aut_orbits_1hop_edges.csv")
    hit_path = os.path.join(RELATED_DIR, "unique_aut_orbits_1hop_seed_hits.csv")
    sum_path = os.path.join(RELATED_DIR, "unique_aut_orbits_1hop_summary.json")
    hist_path = os.path.join(RELATED_DIR, "n_subs_histogram.csv")
    side_path = os.path.join(RELATED_DIR, "moved_orbits_by_source_side.csv")

    with open(orbit_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ORBIT_COLS)
        w.writeheader()
        w.writerows(orbit_rows)
    with open(class_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CLASS_COLS)
        w.writeheader()
        w.writerows(class_rows)
    with open(parent_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PARENT_COLS)
        w.writeheader()
        w.writerows(parent_rows)
    with open(edge_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=EDGE_COLS)
        w.writeheader()
        w.writerows(edge_rows)
    with open(hit_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HIT_COLS)
        w.writeheader()
        w.writerows(seed_hits)
    with open(sum_path, "w") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    with open(hist_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n_subs", "all_covs", "relabel", "moved"])
        w.writeheader()
        for k in sorted(set(n_subs_hist_all) | set(n_subs_hist_relabel)
                        | set(n_subs_hist_moved)):
            w.writerow({
                "n_subs": k,
                "all_covs": n_subs_hist_all.get(k, 0),
                "relabel": n_subs_hist_relabel.get(k, 0),
                "moved": n_subs_hist_moved.get(k, 0),
            })
    with open(side_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["came_from", "count"])
        w.writeheader()
        for key in ("solved_seeds_only", "unsolved_seeds_only", "both"):
            w.writerow({
                "came_from": key,
                "count": summary["moved_orbits_by_source_side"][key],
            })

    print("\n=== unique Aut orbits 1-hop census ===", flush=True)
    print(f"unique orbits: {summary['n_unique_orbits']} "
          f"(seeds {n_seed_orbits} + moved {n_moved_orbits})", flush=True)
    print(f"edges (every moved CoV): {summary['n_edges']}  "
          f"CoVs total: {n_cov_total}  relabels dropped: {n_relabel}",
          flush=True)
    print(f"parent links: {len(parent_rows)}  classes: {len(class_rows)}",
          flush=True)
    print(f"source_side: {side_counts}", flush=True)
    print("seed hits by category:", flush=True)
    for cat in ("unsolved_to_solved", "solved_to_unsolved",
                "solved_to_solved", "unsolved_to_unsolved"):
        print(f"  {cat}: {hit_counts[cat]}", flush=True)
    print(f"n_subs=1: total={n_subs1_total}  moved={n_subs1_moved}  "
          f"(must be 0 moved)", flush=True)
    print("n_subs histogram (all / relabel / moved):", flush=True)
    all_keys = sorted(set(n_subs_hist_all) | set(n_subs_hist_relabel)
                      | set(n_subs_hist_moved))
    for k in all_keys:
        print(f"  n_subs={k}: all={n_subs_hist_all.get(k, 0)}  "
              f"relabel={n_subs_hist_relabel.get(k, 0)}  "
              f"moved={n_subs_hist_moved.get(k, 0)}", flush=True)
    print(f"spot-check: slow aut_canon {slow_ok}/{SPOT_CHECK}, "
          f"edge replay {replay_ok}/{SPOT_CHECK}", flush=True)
    print(f"wall: {wall:.1f}s", flush=True)
    print(f"wrote {orbit_path}", flush=True)
    print(f"wrote {class_path}", flush=True)
    print(f"wrote {parent_path}", flush=True)
    print(f"wrote {edge_path}", flush=True)
    print(f"wrote {hit_path}", flush=True)
    print(f"wrote {sum_path}", flush=True)
    print(f"wrote {hist_path}", flush=True)
    print(f"wrote {side_path}", flush=True)
    return summary


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cap", type=int, default=CAP)
    args = p.parse_args(argv)
    run(cap=args.cap)


if __name__ == "__main__":
    main()
