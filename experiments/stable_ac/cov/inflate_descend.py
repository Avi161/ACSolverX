"""Inflate-and-descend: uphill greedy + non-automorphic CoV splits (NB6).

Hypothesis under test: the 124 hard classes are stuck because search never
visits VERY long states — the escape may only open at per-relator lengths
~100-300, far above the measured-inert 24/48 caps. Pure uphill-then-downhill
would collapse back into the same basin, so at length thresholds the state is
scrambled with CoVs that are provably NOT renames, and the descent runs in
genuinely new coordinates.

The ladder, per presentation: tiers = per-relator caps (e.g. 48, 100, ...,
300). A SEED SCRAMBLE at the short original rep picks up to beam-1
non-rename CoVs — each seeds a branch with its own coordinate system (the
seed sits where CoVs actually apply: measured at climbed snapshots, even the
unbounded subword family yields ~0-1 applicable n_subs>=2 CoVs, because
isolation needs a transformed relator with EXACTLY ONE residual ±x or ±y and
fat words are too dense; at short reps there are dozens). Per tier, each
branch CLIMBS its coordinates (best-first on -total, the ``greedy_until``
state model with the sign flipped) until cap-saturation (``climb_plateau``
pops with no new max — the tier label is never trusted; rows record the
achieved ``snapshot_total``), then the snapshot SPLITS: a descend arm runs
now, and the SAME snapshot continues climbing to the next tier. Fat-state
CoVs are still tried at every snapshot (opportunistic arm "cov", up to
``fanout``) — rare but logged, and gold when one fires.

CoV candidate gate (cheap and exact, at any length): n_subs <= 1 is always a
rename (PROOFS.tex / test_n_subs_one_is_an_automorphism_for_any_w_length), so
require n_subs >= 2; then build the substitution map psi (eliminated
generator -> expr, relabel) and EXCLUDE the candidate when
``is_automorphism(psi)`` holds AND the output equals psi(input) up to order/
rotation/inversion — a proven relabel, wasted action space. Kept candidates
log ``orbit_motion``: ``psi_non_aut`` (certified genuine substitution) or
``psi_aut_no_identity`` (ambiguous, kept). Candidates rank FATTEST-first
(-out_total, abel, strings): descent depth is measured against each arm's OWN
start, never the original total (ranking thin-first would select outputs
already below the original and fake hump-crossings).

CHILD_CAP makes every search here a BEAM: each pop pushes only the best
``child_cap`` children by reduced total (neighbor count is O(L^2) per pop —
the real wall at L=300). The search is therefore INCOMPLETE — "unsolved" is
doubly non-evidence (budget AND beam). Certificates are unaffected: pruning
loses solutions, never invents them.

Certificate: MULTI-JUNCTION SEGMENTED — segments = [moves, junction, moves,
..., moves]; every junction is applied at the CONCRETE search state (never a
canonical rep, so the representative-sensitive chain trap does not arise) and
carries (z_word, iso_gen, iso_index, tier) — iso_index is KEY (apply_cov_once
is first-wins without it). ``verify_segments`` replays through
``experiments/greedy_tests/spec`` + ``cov.apply_cov_once`` only. A solved
cov-arm row certifies STABLE AC-triviality; a solved plain-arm row is a FLAT
AC path (bigger claim). aca_115 = AK(3)'s class: any solve there is presumed
a BUG until independently reproduced.

CLI (budgets/climbs > 1000 need ACSOLVERX_ALLOW_BIG=1; Colab sets it):
    .venv/bin/python3 -m experiments.stable_ac.cov.inflate_descend \
        --bench aca_124 --budget 50 --tiers 48 75 --fanout 1 --beam 1 \
        --climb-max-pops 300 --row-limit 2
"""

import argparse
import heapq
import json
import os
import time

from experiments.equivalence_classes.lib.autcanon import is_automorphism
from experiments.greedy_tests.spec.words import (
    inverse,
    reduce_word,
    rotate,
    str_to_word,
    word_to_str,
)
from experiments.search.greedy_baseline import (
    arr_to_str,
    canonical_pair_nj,
    get_neighbors_with_moves_nj,
    reduce_relator_nj,
    str_to_arr,
)
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude
from experiments.stable_ac.cov.stall_escape import _canon_key

HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_TIERS = (48, 100, 150, 200, 250, 300)
DEFAULT_WMAX = 8
DEFAULT_FAMILY_CAP = 600
DEFAULT_FANOUT = 2
DEFAULT_BEAM = 3
DEFAULT_CLIMB_PLATEAU = 50
DEFAULT_CLIMB_MAX_POPS = 2000
DEFAULT_CHILD_CAP = 512


# ── search (one loop, both directions) ──────────────────────────────────────

def search_until(r1s, r2s, budget, cap, up=False, plateau_k=None,
                 child_cap=DEFAULT_CHILD_CAP):
    """Best-first search; ``up=True`` maximises total length (the climb).

    Returns status 'solved' (down only) | 'plateau' | 'budget' | 'exhausted',
    pops, moves (solved: full legacy list, else None), incumbent (best popped
    pair: min-total going down, MAX-total going up), incumbent_moves,
    best_total, max_popped_total. State store is string-keys-only (arrays are
    re-parsed on pop — at L=300 an array cache is the memory, not the time).
    ``child_cap`` bounds pushes per pop (beam; None = complete).
    """
    key, _ = _canon_key(r1s, r2s)
    sgn = -1 if up else 1
    pq = [(sgn * (len(key[0]) + len(key[1])), 0, key)]
    visited = {key: None}
    move_in = {}
    pops = 0
    best_total = -1 if up else 10 ** 9
    best_key, since_best = key, 0
    max_popped = 0

    def path_to(k):
        mv = []
        while visited[k] is not None:
            mv.append(move_in[k])
            k = visited[k]
        return mv[::-1]

    while pq and pops < budget:
        _, d, k = heapq.heappop(pq)
        pops += 1
        a1, a2 = str_to_arr(k[0]), str_to_arr(k[1])
        total = len(a1) + len(a2)
        max_popped = max(max_popped, total)
        if not up and len(a1) == 1 and len(a2) == 1:
            mv = path_to(k)
            return {"status": "solved", "pops": pops, "moves": mv,
                    "incumbent": k, "incumbent_moves": mv, "best_total": 2,
                    "max_popped_total": max_popped}
        if (total > best_total) if up else (total < best_total):
            best_total, best_key, since_best = total, k, 0
        else:
            since_best += 1
            if plateau_k is not None and since_best >= plateau_k:
                return {"status": "plateau", "pops": pops, "moves": None,
                        "incumbent": best_key,
                        "incumbent_moves": path_to(best_key),
                        "best_total": best_total,
                        "max_popped_total": max_popped}
        kids = []
        for n1, n2, t, js, k1, k2 in get_neighbors_with_moves_nj(a1, a2):
            n1 = reduce_relator_nj(n1, True)
            n2 = reduce_relator_nj(n2, True)
            if len(n1) > cap or len(n2) > cap:
                continue
            kids.append((len(n1) + len(n2), n1, n2,
                         (int(t), int(js), int(k1), int(k2))))
        if child_cap is not None and len(kids) > child_cap:
            kids.sort(key=lambda c: sgn * c[0])   # stable: ties keep gen order
            kids = kids[:child_cap]
        for tot, n1, n2, mv in kids:
            c1, c2 = canonical_pair_nj(n1, n2)
            nk = (arr_to_str(c1), arr_to_str(c2))
            if nk in visited:
                continue
            visited[nk] = k
            move_in[nk] = mv
            heapq.heappush(pq, (sgn * tot, d + 1, nk))
    return {"status": "budget" if pq else "exhausted", "pops": pops,
            "moves": None, "incumbent": best_key,
            "incumbent_moves": path_to(best_key), "best_total": best_total,
            "max_popped_total": max_popped}


# ── CoV scramble: bounded family + rename gate ──────────────────────────────

def bounded_family(r1, r2, wmax=DEFAULT_WMAX, family_cap=DEFAULT_FAMILY_CAP,
                   min_len=cov.SUBWORD_MIN_LEN,
                   min_transformed_len=cov.MIN_TRANSFORMED_LEN):
    """Subwords of length ``min_len..wmax`` off the doubled cyclic relators,
    canonical ``max(w, w^-1)``, with the CROSS-RELATOR no-collapse gate
    RE-APPLIED (``enumerate_cov(family=...)`` bypasses ``subword_candidates``'
    gate), deterministically stride-sampled down to ``family_cap``. A
    bounded-|w| family is a different family — its files carry the wmax tag
    and never share a resume file with the unbounded subnc2 sweep."""
    r1, r2 = tuple(r1), tuple(r2)
    seen = set()
    for rel in (r1, r2):
        cyc = reduce_word(rel, cyclic=True)
        n = len(cyc)
        doubled = cyc + cyc
        for length in range(min_len, min(wmax, n) + 1):
            for i in range(n):
                w = doubled[i:i + length]
                seen.add(max(w, inverse(w)))
    kept = []
    for w in seen:
        collapses = False
        for rel in (r1, r2):
            sub, n_subs = cov.substitute_word(rel, w)
            if n_subs and len(sub) < min_transformed_len:
                collapses = True
                break
        if not collapses:
            kept.append(w)
    kept.sort(key=lambda w: (len(w), w))
    if len(kept) > family_cap:
        step = len(kept) / family_cap
        kept = [kept[int(i * step)] for i in range(family_cap)]
    return tuple(kept)


def _canon_cyc(w):
    w = reduce_word(tuple(w), cyclic=True)
    if not w:
        return ()
    return min(rotate(u, -k) for u in (w, inverse(w)) for k in range(len(u)))


def _canon_pair_w(a, b):
    return tuple(sorted((_canon_cyc(a), _canon_cyc(b))))


def rename_kind(res, r1w, r2w):
    """Classify a CoV: 'relabel' (proven rename — psi is an automorphism AND
    output == psi(input) up to order/rotation/inversion; excluded from the
    action space), 'psi_non_aut' (certified genuine substitution), or
    'psi_aut_no_identity' (psi automorphic but output is not its image —
    ambiguous, kept). psi is built exactly as in
    test_n_subs_one_is_an_automorphism_for_any_w_length; the automorphism
    check is autcanon.is_automorphism (abelian det + peak reduction — cheap at
    any length, and instant on the det short-circuit for most non-auts)."""
    a = cov.X_GEN if res.iso_gen == "x" else cov.Y_GEN

    def psi(w):
        return cov.relabel(cov.substitute_generator(tuple(w), a, res.expr),
                           res.iso_gen)

    phi = {"x": word_to_str(psi((cov.X_GEN,))),
           "y": word_to_str(psi((cov.Y_GEN,)))}
    if not is_automorphism(phi):
        return "psi_non_aut"
    pred = _canon_pair_w(psi(reduce_word(r1w, cyclic=True)),
                         psi(reduce_word(r2w, cyclic=True)))
    if pred == _canon_pair_w(res.r1, res.r2):
        return "relabel"
    return "psi_aut_no_identity"


def scramble_candidates(s1, s2, tier, wmax=DEFAULT_WMAX,
                        family_cap=DEFAULT_FAMILY_CAP, max_kept=6):
    """Gated CoV candidates of a snapshot, fattest-first.

    Pipeline: bounded family -> enumerate_cov (reject_len raised to
    tier+headroom — 239 is a fast-solver ceiling, irrelevant here) ->
    n_subs >= 2 -> dedupe by output pair -> rank (-out_total, abel, strings;
    string tiebreak makes cov_idx resume-stable) -> walk down running the
    rename gate lazily until ``max_kept`` survive. Returns (kept, stats);
    kept entries are (out_total, abel, (o1, o2), CoVResult, orbit_motion).
    """
    r1w, r2w = str_to_word(s1), str_to_word(s2)
    fam = bounded_family(r1w, r2w, wmax, family_cap)
    pool, seen, n_low = [], set(), 0
    for res in cov.enumerate_cov(r1w, r2w, family=fam, default_cap=tier,
                                 reject_len=tier + cov.CAP_HEADROOM):
        if res.n_subs < 2:
            n_low += 1
            continue
        o = (word_to_str(res.r1), word_to_str(res.r2))
        if o in seen:
            continue
        seen.add(o)
        pool.append((len(o[0]) + len(o[1]),
                     abel_magnitude(res.r1, res.r2), o, res))
    pool.sort(key=lambda t: (-t[0], t[1], t[2]))
    kept, n_renames, n_scanned = [], 0, 0
    for tot, ab, o, res in pool:
        if len(kept) >= max_kept:
            break
        n_scanned += 1
        kind = rename_kind(res, r1w, r2w)
        if kind == "relabel":
            n_renames += 1
            continue
        kept.append((tot, ab, o, res, kind))
    stats = {"n_family": len(fam), "n_pool": len(pool), "n_nsubs_low": n_low,
             "n_rename_scanned": n_scanned, "n_renames": n_renames,
             "n_kept": len(kept)}
    return kept, stats


def _junction(res, o, kind, tier):
    return {"z_word": word_to_str(res.z_word), "iso_gen": res.iso_gen,
            "iso_index": res.iso_index, "n_subs": res.n_subs,
            "escape_start": list(o), "escape_cap": res.cap,
            "orbit_motion": kind, "tier": tier}


# ── the ladder driver ───────────────────────────────────────────────────────

def ladder_one(pres_id, r1, r2, cfg, done):
    """Yield fresh result rows for one presentation (skips keys in ``done``;
    climbs/scrambles re-run deterministically on resume — only descends,
    the expensive part, are skipped).

    Coordinate diversity is decided by a SEED SCRAMBLE at the short original
    rep, where CoVs actually apply: MEASURED at climbed snapshots, even the
    unbounded subword family yields ~0-1 applicable n_subs>=2 CoVs (isolation
    needs a transformed relator with EXACTLY ONE residual ±x or ±y — fat
    words are too dense), vs dozens at short reps. So: root branch (no CoV) +
    up to beam-1 seed-CoV branches, each climbing ITS OWN coordinates tier by
    tier. At every tier each branch's snapshot splits: a descend arm now, and
    the same snapshot continues climbing to the next tier. Fat-state CoVs
    stay in as an OPPORTUNISTIC fork: tried at every snapshot (arm "cov",
    up to ``fanout``), logged in scr_* stats, gold when one fires."""
    canon0, _ = _canon_key(r1, r2)
    seeds, seed_stats = scramble_candidates(
        canon0[0], canon0[1], cfg["tiers"][0], cfg["wmax"],
        cfg["family_cap"], max_kept=max(cfg["beam"] - 1, 0))
    branches = [{"id": "r", "pair": canon0, "segs": (), "climb_pops": 0,
                 "junctions": ()}]
    for j, (tot, _, o, res, kind) in enumerate(seeds):
        jn = _junction(res, o, kind, cfg["tiers"][0])
        # the empty moves segment canonicalises the raw start on replay,
        # landing exactly on canon0 where this junction was derived
        branches.append({"id": f"r.s{j}", "pair": o,
                         "segs": ({"moves": []}, {"junction": jn}),
                         "climb_pops": 0, "junctions": (jn,)})
    for ti, tier in enumerate(cfg["tiers"]):
        last = ti == len(cfg["tiers"]) - 1
        nxt = []
        for br in branches:
            s1, s2 = br["pair"]
            cap_t = max(tier, len(s1), len(s2))
            cl = search_until(s1, s2, cfg["climb_max_pops"], cap_t, up=True,
                              plateau_k=cfg["climb_plateau"],
                              child_cap=cfg["child_cap"])
            snap = cl["incumbent"]
            segs = br["segs"] + ({"moves": cl["incumbent_moves"]},)
            climb_pops = br["climb_pops"] + cl["pops"]
            snap_total = len(snap[0]) + len(snap[1])
            kept, stats = scramble_candidates(
                snap[0], snap[1], tier, cfg["wmax"], cfg["family_cap"],
                max_kept=cfg["fanout"])
            base = {"pres_id": pres_id, "tier": tier, "branch_id": br["id"],
                    "snapshot": list(snap), "snapshot_total": snap_total,
                    "climb_status": cl["status"],
                    "climb_max_popped_total": cl["max_popped_total"],
                    "climb_pops_tier": cl["pops"],
                    "climb_pops_cum": climb_pops,
                    "seed_n_kept": seed_stats["n_kept"],
                    **{"scr_" + k: v for k, v in stats.items()}}
            jobs = [("plain", -1, snap, None, cap_t)]
            for j in range(len(kept)):
                _, _, o, res, kind = kept[j]
                jobs.append(("cov", j, o, _junction(res, o, kind, tier),
                             max(cap_t, res.cap)))
            for arm, cidx, start, junc, dcap in jobs:
                if (pres_id, tier, br["id"], arm, cidx) in done:
                    continue
                yield _descend_row(base, arm, cidx, start, junc, segs,
                                   br["junctions"], dcap + cov.CAP_HEADROOM,
                                   cfg)
            if not last:   # the same snapshot keeps climbing (user's fork)
                nxt.append({"id": br["id"], "pair": snap, "segs": segs,
                            "climb_pops": climb_pops,
                            "junctions": br["junctions"],
                            "_total": snap_total})
        if not last:
            nxt.sort(key=lambda b: (-b["_total"], b["id"]))
            branches = nxt[:cfg["beam"]]


def _descend_row(base, arm, cidx, start, junc, segs, lineage, dcap, cfg):
    t0 = time.monotonic()
    de = search_until(start[0], start[1], cfg["budget"], dcap, up=False,
                      plateau_k=None, child_cap=cfg["child_cap"])
    solved = de["status"] == "solved"
    # EVERY CoV on this row's path, oldest first (earlier-tier continue
    # junctions + this arm's own) — the flat z_word/n_subs are the arm's own.
    juncs = list(lineage) + ([junc] if junc is not None else [])
    row = dict(base)
    row.update({"arm": arm, "cov_idx": cidx, "cap": dcap,
                "start_arm": list(start),
                "start_total_arm": len(start[0]) + len(start[1]),
                "descend_pops": de["pops"], "nodes_explored": de["pops"],
                "descend_status": de["status"],
                "min_total_reached": de["best_total"],
                "min_relator_length": de["best_total"],
                "max_relator_length": de["max_popped_total"],
                "descend_max_popped_total": de["max_popped_total"],
                "solved": solved, "junctions": juncs,
                "z_words": [j["z_word"] for j in juncs],
                "n_junctions": len(juncs)})
    if junc is not None:
        row.update({"z_word": junc["z_word"], "n_subs": junc["n_subs"],
                    "iso_gen": junc["iso_gen"], "iso_index": junc["iso_index"],
                    "orbit_motion": junc["orbit_motion"]})
    if solved:
        full = list(segs)
        if junc is not None:
            full.append({"junction": junc})
        full.append({"moves": de["moves"]})
        row["segments"] = full
        n_moves = sum(len(s["moves"]) for s in full if "moves" in s)
        row["path_length"] = n_moves
        if not juncs:      # zero junctions => a genuine FLAT legacy path
            row["path_moves"] = [m for s in full for m in s["moves"]]
    row["elapsed_s"] = round(time.monotonic() - t0, 2)
    return row


# ── independent verification (spec + cov only — never this module's search) ─

def verify_segments(r1s, r2s, segments):
    """Replay a solved row's multi-junction certificate. Returns (ok, why).

    Moves segments replay through the spec; each junction re-derives via
    ``cov.apply_cov_once`` at the REPLAYED concrete state with the recorded
    (z_word, iso_gen, iso_index) and the enumeration-time caps (tier), and
    must reproduce the recorded escape_start exactly.
    """
    from experiments.greedy_tests.spec.moves import legacy_to_move
    from experiments.greedy_tests.spec.presentation import Presentation
    from experiments.greedy_tests.spec.search import replay

    cur = (r1s, r2s)
    for i, seg in enumerate(segments):
        if "moves" in seg:
            pres = Presentation(2, tuple(str_to_word(s) for s in cur))
            mvs = [legacy_to_move(t, js, k1, k2)
                   for t, js, k1, k2 in seg["moves"]]
            end = replay(pres, mvs, cyclic=True)[-1]
            cur = tuple(word_to_str(r) for r in end.relators)
        else:
            j = seg["junction"]
            res = cov.apply_cov_once(
                str_to_word(cur[0]), str_to_word(cur[1]),
                str_to_word(j["z_word"]), default_cap=j["tier"],
                reject_len=j["tier"] + cov.CAP_HEADROOM,
                iso_gen=j["iso_gen"], iso_index=j["iso_index"])
            if res is None:
                return False, f"segment {i}: junction CoV not applicable"
            got = sorted([word_to_str(res.r1), word_to_str(res.r2)])
            if got != sorted(j["escape_start"]):
                return False, f"segment {i}: junction mismatch"
            cur = tuple(j["escape_start"])
    ok = all(len(s) == 1 for s in cur)
    return ok, ("segmented certificate verifies" if ok
                else "final state not trivial")


# ── runner ──────────────────────────────────────────────────────────────────

def _require_allowed(n):
    if n > 1000 and os.environ.get("ACSOLVERX_ALLOW_BIG") != "1":
        raise SystemExit(f"budget {n} > 1000 needs ACSOLVERX_ALLOW_BIG=1")


def _out_name(bench, budget, cfg, shard):
    t = "-".join(str(x) for x in cfg["tiers"])
    s = f"_{shard}" if shard else ""
    return (f"inflate_{bench}_{budget}_t{t}_w{cfg['wmax']}"
            f"fc{cfg['family_cap']}_f{cfg['fanout']}_b{cfg['beam']}"
            f"_k{cfg['child_cap']}_cp{cfg['climb_plateau']}"
            f"-{cfg['climb_max_pops']}{s}.jsonl")


def run_inflate(bench="aca_124", budget=50, tiers=DEFAULT_TIERS,
                wmax=DEFAULT_WMAX, family_cap=DEFAULT_FAMILY_CAP,
                fanout=DEFAULT_FANOUT, beam=DEFAULT_BEAM,
                climb_plateau=DEFAULT_CLIMB_PLATEAU,
                climb_max_pops=DEFAULT_CLIMB_MAX_POPS,
                child_cap=DEFAULT_CHILD_CAP, names=None, row_limit=None,
                shard="", out_dir="results/stable_ac/inflate"):
    from experiments import run_baseline
    from experiments.run_baseline import _repair_jsonl
    from experiments.stable_ac.cov.run_cov import _claim_out_path, _git_commit
    from experiments.stable_ac.idea_bench import harness

    _require_allowed(max(budget, climb_max_pops))
    cfg = {"budget": budget, "tiers": tuple(tiers), "wmax": wmax,
           "family_cap": family_cap, "fanout": fanout, "beam": beam,
           "climb_plateau": climb_plateau, "climb_max_pops": climb_max_pops,
           "child_cap": child_cap}
    root = harness.find_repo_root(HERE)
    od = out_dir if os.path.isabs(out_dir) else os.path.join(root, out_dir)
    os.makedirs(od, exist_ok=True)
    out = os.path.join(od, _out_name(bench, budget, cfg, shard))
    _claim_out_path(out)
    _repair_jsonl(out)
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
                done.add((r["pres_id"], r["tier"], r["branch_id"],
                          r["arm"], r["cov_idx"]))
            except (ValueError, KeyError):
                continue
    rows = harness.load_bench(bench)
    if names:
        keep = set(names)
        rows = [p for p in rows if p["pres_id"] in keep]
    if row_limit:
        rows = rows[:row_limit]
    commit = _git_commit()
    common = {"bench": bench, "budget": budget, "git_commit": commit, **cfg}
    common.pop("tiers")
    print(f"{len(rows)} presentations, tiers {list(cfg['tiers'])}, budget "
          f"{budget} -> {os.path.basename(out)} ({len(done)} rows done)",
          flush=True)
    t_run = time.monotonic()
    n_rows_run, n_solved_run, pops_run = 0, 0, 0
    with open(out, "a") as f:

        def _emit(row, p):
            nonlocal n_rows_run, n_solved_run, pops_run
            # heartbeat accounting: each branch-tier climb is attributed to
            # its (unique) plain-arm row, so climbs count exactly once
            pops_run += row.get("descend_pops", 0)
            if row.get("arm") == "plain":
                pops_run += row.get("climb_pops_tier", 0)
            n_rows_run += 1
            n_solved_run += bool(row.get("solved"))
            rate = pops_run / max(time.monotonic() - t_run, 1e-9)
            print(f"    [{p['pres_id']}] t{row['tier']} "
                  f"{row.get('branch_id', '-')} {row['arm']}/"
                  f"{row['cov_idx']} {row['start_total_arm']}->"
                  f"{row['min_total_reached']} pops={row['descend_pops']} "
                  f"({rate:.0f} pops/s run-avg)"
                  f"{' SOLVED' if row.get('solved') else ''}", flush=True)
            row.update({"r1_orig": p["r1"], "r2_orig": p["r2"], **common})
            if row.get("solved"):
                ok, why = verify_segments(p["r1"], p["r2"], row["segments"])
                row["verify_ok"], row["verify_why"] = ok, why
                kind = ("FLAT-AC" if row.get("n_junctions", 0) == 0
                        else "STABLE-AC")
                bug = (" [aca_115 = AK(3)-class: PRESUMED BUG until "
                       "independently reproduced]"
                       if p["pres_id"] == "aca_115" else "")
                print(f"  *** {kind} SOLVE LEAD {p['pres_id']} t{row['tier']} "
                      f"{row['arm']}/{row['cov_idx']} verify={ok} — "
                      f"verification bar applies{bug}", flush=True)
            f.write(json.dumps(row) + "\n")
            f.flush()

        n_pres_done = 0
        for p in rows:
            t0 = time.monotonic()
            n_new = 0
            ckey = (p["pres_id"], 0, "-", "control", -1)
            if ckey not in done:
                c = run_baseline.greedy_search(
                    p["r1"], p["r2"], budget, max_relator_length=24,
                    cyclic_reduce=True)
                crow = {"pres_id": p["pres_id"], "tier": 0, "branch_id": "-",
                        "arm": "control", "cov_idx": -1, "cap": 24,
                        "start_arm": [p["r1"], p["r2"]],
                        "start_total_arm": len(p["r1"]) + len(p["r2"]),
                        "descend_pops": c["nodes_explored"],
                        "nodes_explored": c["nodes_explored"],
                        "min_total_reached": c["min_relator_length"],
                        "min_relator_length": c["min_relator_length"],
                        "max_relator_length": c["max_relator_length"],
                        "solved": bool(c["solved"]),
                        "junctions": [], "z_words": [], "n_junctions": 0,
                        "elapsed_s": round(time.monotonic() - t0, 2)}
                if c["solved"]:
                    crow["segments"] = [{"moves": c["path_moves"]}]
                    crow["path_moves"] = c["path_moves"]
                    crow["path_length"] = len(c["path_moves"] or [])
                _emit(crow, p)
                n_new += 1
            for row in ladder_one(p["pres_id"], p["r1"], p["r2"], cfg, done):
                _emit(row, p)
                n_new += 1
            n_pres_done += 1
            el = time.monotonic() - t_run
            eta_h = (el / n_pres_done * (len(rows) - n_pres_done)) / 3600
            print(f"  {p['pres_id']}: {n_new} rows "
                  f"({round(time.monotonic() - t0, 1)}s) | "
                  f"{n_pres_done}/{len(rows)} pres, {n_solved_run} solved "
                  f"rows, {pops_run / 1000:.1f}k pops, ETA ~{eta_h:.1f}h",
                  flush=True)
    print(f"written: {out}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(
        description="Inflate-and-descend ladder on the 124.")
    ap.add_argument("--bench", default="aca_124")
    ap.add_argument("--budget", type=int, default=50)
    ap.add_argument("--tiers", type=int, nargs="+", default=list(DEFAULT_TIERS))
    ap.add_argument("--wmax", type=int, default=DEFAULT_WMAX)
    ap.add_argument("--family-cap", type=int, default=DEFAULT_FAMILY_CAP)
    ap.add_argument("--fanout", type=int, default=DEFAULT_FANOUT)
    ap.add_argument("--beam", type=int, default=DEFAULT_BEAM)
    ap.add_argument("--climb-plateau", type=int, default=DEFAULT_CLIMB_PLATEAU)
    ap.add_argument("--climb-max-pops", type=int,
                    default=DEFAULT_CLIMB_MAX_POPS)
    ap.add_argument("--child-cap", type=int, default=DEFAULT_CHILD_CAP)
    ap.add_argument("--names", nargs="*", default=None)
    ap.add_argument("--row-limit", type=int, default=None)
    ap.add_argument("--shard", default="")
    args = ap.parse_args()
    run_inflate(bench=args.bench, budget=args.budget, tiers=args.tiers,
                wmax=args.wmax, family_cap=args.family_cap,
                fanout=args.fanout, beam=args.beam,
                climb_plateau=args.climb_plateau,
                climb_max_pops=args.climb_max_pops, child_cap=args.child_cap,
                names=args.names, row_limit=args.row_limit, shard=args.shard)


if __name__ == "__main__":
    main()
