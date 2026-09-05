"""Independent replay verifier for mu_ladder_big provenance files.

Every accepted orbit in a ``*_orbits.jsonl`` is re-derived from its recorded
CONCRETE parent pair (never from a canonical rep — chains are representative-
sensitive, lesson: cov-chains-junction-at-canonical-reps): the recorded
``(z, iso_gen, iso_index)`` branch is re-applied with ``cov.cov_branches``
and must reproduce the recorded output pair exactly; at ``--level full`` the
pair's ``aut_canon`` must reproduce the recorded ``(mu, rep)`` too. The
summary row's ``best_rep``/``best_mu``/``best_chain``/``n_orbits_seen``/
``is_ak3_orbit`` are all re-derived from the tree, so a summary claim cannot
outrun its provenance.

CLI:
    .venv/bin/python3 -m experiments.stable_ac.cov.verify_mu_ladder \
        results/stable_ac/mu_scan/mu_ladder_big_...jsonl [--level replay|full]

Exit 0 = every class verifies; non-zero otherwise.
"""

import argparse
import json
import os
import sys

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.mu_ladder_big import AK3


def _replay_hop(parent_pair, orb, cap):
    """The recorded branch, re-applied from the recorded parent pair. Returns
    an error string or None."""
    branches = cov.cov_branches(str_to_word(parent_pair[0]),
                                str_to_word(parent_pair[1]),
                                str_to_word(orb["z"]),
                                default_cap=cap,
                                cap_headroom=cov.CAP_HEADROOM,
                                reject_len=cov.REJECT_LEN,
                                iso_gen=orb["iso_gen"])
    hit = [b for b in branches if b.iso_index == orb["iso_index"]]
    if not hit:
        return (f"no branch (z={orb['z']}, iso_gen={orb['iso_gen']}, "
                f"iso_index={orb['iso_index']}) from parent {parent_pair}")
    got = [word_to_str(hit[0].r1), word_to_str(hit[0].r2)]
    if got != orb["pair"]:
        return f"branch output {got} != recorded pair {orb['pair']}"
    if hit[0].n_subs != orb["n_subs"]:
        return f"n_subs {hit[0].n_subs} != recorded {orb['n_subs']}"
    return None


def verify_class(row, orbit_rows, level="full"):
    """All errors for one class ('' list = verified)."""
    errs = []
    pid = row["pres_id"]
    cap = row.get("cfg", {}).get("cap", cov.DEFAULT_CAP)
    tree = {}
    roots = [o for o in orbit_rows if o["parent_rep"] is None]
    if len(roots) != 1:
        return [f"{pid}: {len(roots)} root rows (want 1)"]
    for o in orbit_rows:
        key = tuple(o["rep"])
        if key in tree:
            errs.append(f"{pid}: duplicate rep {key}")
        tree[key] = o

    root = roots[0]
    mu0, rep0, _ = aut_canon((row["r1_orig"], row["r2_orig"]))
    if root["pair"] != [row["r1_orig"], row["r2_orig"]]:
        errs.append(f"{pid}: root pair != (r1_orig, r2_orig)")
    if (mu0, list(rep0)) != (root["mu"], root["rep"]) \
            or mu0 != row["mu_in"]:
        errs.append(f"{pid}: root aut_canon ({mu0}, {rep0}) != recorded "
                    f"({root['mu']}, {root['rep']}, mu_in {row['mu_in']})")

    for o in orbit_rows:
        if o["parent_rep"] is None:
            continue
        parent = tree.get(tuple(o["parent_rep"]))
        if parent is None:
            errs.append(f"{pid}: parent_rep {o['parent_rep']} not in tree")
            continue
        err = _replay_hop(parent["pair"], o, cap)
        if err:
            errs.append(f"{pid}: rung {o['rung']} z={o['z']}: {err}")
            continue
        if level == "full":
            mu, rep, _ = aut_canon(tuple(o["pair"]))
            if (mu, list(rep)) != (o["mu"], o["rep"]):
                errs.append(f"{pid}: rung {o['rung']} aut_canon "
                            f"({mu}, {rep}) != recorded "
                            f"({o['mu']}, {o['rep']})")

    if row["n_orbits_seen"] != len(orbit_rows):
        errs.append(f"{pid}: n_orbits_seen {row['n_orbits_seen']} != "
                    f"{len(orbit_rows)} orbit rows")
    best = tree.get(tuple(row["best_rep"]))
    if best is None:
        errs.append(f"{pid}: best_rep not in tree")
    else:
        if best["mu"] != row["best_mu"]:
            errs.append(f"{pid}: best node mu {best['mu']} != best_mu "
                        f"{row['best_mu']}")
        chain, node = [], best
        while node["parent_rep"] is not None:
            chain.append(node["z"])
            node = tree.get(tuple(node["parent_rep"]))
            if node is None:
                errs.append(f"{pid}: broken parent walk from best_rep")
                break
        else:
            if list(reversed(chain)) != row["best_chain"]:
                errs.append(f"{pid}: parent walk {list(reversed(chain))} != "
                            f"best_chain {row['best_chain']}")
    if any(o["mu"] < row["best_mu"] for o in orbit_rows):
        errs.append(f"{pid}: an orbit row undercuts best_mu {row['best_mu']}")
    _, ak3_rep, _ = aut_canon(AK3)
    if row["is_ak3_orbit"] != (tuple(row["best_rep"]) == ak3_rep):
        errs.append(f"{pid}: is_ak3_orbit flag inconsistent")
    return errs


def verify_files(summary_path, orbits_path=None, level="full", names=None):
    """(n_classes_checked, [errors])."""
    if orbits_path is None:
        orbits_path = summary_path[:-len(".jsonl")] + "_orbits.jsonl"
    orbits = {}
    for ln in open(orbits_path):
        if ln.strip():
            o = json.loads(ln)
            orbits.setdefault(o["pres_id"], []).append(o)
    errs, n = [], 0
    for ln in open(summary_path):
        if not ln.strip():
            continue
        row = json.loads(ln)
        if names and row["pres_id"] not in names:
            continue
        n += 1
        e = verify_class(row, orbits.get(row["pres_id"], []), level=level)
        errs.extend(e)
        print(f"  {row['pres_id']}: "
              f"{'OK' if not e else f'{len(e)} ERROR(S)'} "
              f"({len(orbits.get(row['pres_id'], []))} orbits)", flush=True)
    return n, errs


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("summary", help="mu_ladder_big summary jsonl")
    ap.add_argument("--orbits", default=None,
                    help="orbits jsonl (default: <summary>_orbits.jsonl)")
    ap.add_argument("--level", choices=("replay", "full"), default="full",
                    help="replay = branch replay only; full = + aut_canon")
    ap.add_argument("--names", nargs="*", default=None)
    a = ap.parse_args()
    n, errs = verify_files(a.summary, a.orbits, level=a.level,
                           names=set(a.names) if a.names else None)
    if errs:
        for e in errs:
            print(f"FAIL {e}", flush=True)
        print(f"{len(errs)} error(s) across {n} classes", flush=True)
        sys.exit(1)
    print(f"ALL {n} CLASSES VERIFY ({os.path.basename(a.summary)}, "
          f"level={a.level})", flush=True)


if __name__ == "__main__":
    main()
