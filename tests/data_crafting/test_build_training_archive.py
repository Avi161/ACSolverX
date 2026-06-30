"""Gate-style tests for Phases 3-6 of build_training_archive.py (no pytest; matches the
scripts/tests/test_phase1.py idiom).

Run from the repo root:
    ../.venv/bin/python tests/data_crafting/test_build_training_archive.py

Prints each check; exits non-zero with 'DATA-CRAFTING TESTS FAILED' on any failure, else prints
'DATA-CRAFTING TESTS PASS'. Every Phase 3-6 invariant is **re-derived independently** (own path
walker, own keep-set, own near-neighbour brute force, own region/weight recompute) rather than
trusting build_training_archive's own output. Two main() runs into project-relative .scratch dirs
exercise determinism + the emitted file; dot_archive.jsonl is hashed before/after to prove the
original is byte-unchanged.

Honesty-guard coverage (Field Advisor warm-pre, Checkpoint 1):
  - quantifies the Phase-3 drop (n_dropped + n_paths histogram of dropped classes) -- FA Finding 1;
  - reports the short_hard/named loss-mass share (~0.2%) -- FA Finding 2;
  - asserts action-space consistency via canon.get_neighbors_nj (FA d.1) and validates the
    near_neighbour proxy against a brute-force recompute (FA d.2);
  - asserts easy stays down-weighted (FA d.9) and the emit field-SET is exactly 14 (FA d.8).
"""
import os
import sys
import json
import math
import shutil
import hashlib
import random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset        # noqa: E402
from scripts.build import build_training_archive as bt  # noqa: E402

LOOKALIKE_KEY = "YXyxYx|YYYYxxx"   # canon_key("YXyxYx","xxxYYYY"); regression-pin (= test_phase1)
EXPECTED_NAMED = {
    "YXYxyx|YYYYxxx", "YXYxyx|YYYYYxxxx", "YXYxyx|YYYYYYxxxxx", "YXYxyx|YYYYYYYxxxxxx",
    "YXYxyx|YYYYYYYYxxxxxxx", "YXYxyx|YYYYYYYYYxxxxxxxx", "YYYXyyx|YXXYxxx", "YYYXyyx|YXXXyxx",
}


def _k(r):
    return f"{r['r1']}|{r['r2']}"


def _recon_keep(merged_paths, labelled_keys):
    """INDEPENDENT re-implementation of the Phase-3 walk (does not import bt._walk_paths). Returns
    (kept, key_paths, recon_min, orphans)."""
    cache = {}

    def ckey(a, b):
        kk = (a, b)
        if kk not in cache:
            cache[kk] = canon.canon_key(a, b)[0]
        return cache[kk]

    kept, key_paths, recon_min, orphans = set(), defaultdict(set), {}, 0
    with open(merged_paths) as f:
        for pidx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if not rec["solved"]:
                continue
            path, N = rec["best_path"], rec["best_path_length"]
            ei = ek = 0
            for m in range(N + 1):
                key = ckey(path[2 * m], path[2 * m + 1])
                if key not in labelled_keys:
                    orphans += 1
                key_paths[key].add(pidx)
                dot = N - m
                if key not in recon_min or dot < recon_min[key]:
                    recon_min[key] = dot
                if dot >= 11:
                    kept.add(key)
                else:
                    if ei % cfg.DIVERSITY_STRIDE == 0 and ek < cfg.PER_PATH_CAP:
                        kept.add(key)
                        ek += 1
                    ei += 1
    return kept, key_paths, recon_min, orphans


def _neigh_keys(s1, s2):
    out = set()
    for n1, n2 in canon.get_neighbors_nj(canon.str_to_arr(s1), canon.str_to_arr(s2)):
        out.add(canon.canon_key(canon.arr_to_str(n1), canon.arr_to_str(n2))[0])
    return out


def _brute_nn(row, lab_surv):
    a, b, t = row["r1"], row["r2"], row["total_len"]
    c = 0
    for o in lab_surv:
        if o is row:
            continue
        if abs(o["total_len"] - t) <= 1 and (o["r1"] in (a, b) or o["r2"] in (a, b)):
            c += 1
    return c


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def run_tests():
    failures = []
    rng = random.Random(cfg.SEED)

    def check(name, cond, detail=""):
        if cond:
            print(f"  ok   {name}")
        else:
            print(f"  FAIL {name}  {detail}")
            failures.append(name)

    labelled0, censored0 = dot_dataset.load_archive(cfg.ARCHIVE)
    labelled_keys = {_k(r) for r in labelled0}
    arch_min = {_k(r): r["min_dot"] for r in labelled0}

    # ---- run the pipeline: main() into scratch A (returns survivors), originals hashed around it ----
    print("[run pipeline -> .scratch]")
    a_dir, b_dir = os.path.join(".scratch", "dc_a"), os.path.join(".scratch", "dc_b")
    os.makedirs(a_dir, exist_ok=True)
    os.makedirs(b_dir, exist_ok=True)
    out_a, out_b = os.path.join(a_dir, "v2.jsonl"), os.path.join(b_dir, "v2.jsonl")
    pre_hash = _sha(cfg.ARCHIVE)
    try:
        survivors, stats = bt.main(out=out_a)
        survivors_b, _ = bt.main(out=out_b)
        post_hash = _sha(cfg.ARCHIVE)

        rows = {_k(r): r for r in survivors}
        lab_surv = [r for r in survivors if r["tier"] == "solved"]
        cen_surv = [r for r in survivors if r["tier"] == "censored"]
        named_surv = [r for r in survivors if r["tier"] == "named"]

        # ============ INDEPENDENT re-derivation ============
        print("[phase 3: independent re-derivation]")
        kept, key_paths, recon_min, orphans = _recon_keep(cfg.MERGED_PATHS, labelled_keys)
        check("3.1 zero orphans (1:1 path<->archive join)", orphans == 0, f"orphans={orphans}")
        check("3.1 recon min_dot == archive min_dot (0 mismatch)",
              all(recon_min.get(k) == arch_min.get(k) for k in labelled_keys),
              f"mismatches={sum(1 for k in labelled_keys if recon_min.get(k) != arch_min.get(k))}")

        # independent survivor set: labelled iff kept-or-lookalike; build must match exactly
        exp_lab = {k for k in labelled_keys if k in kept or k == LOOKALIKE_KEY}
        got_lab = {_k(r) for r in lab_surv}
        check("3.3 labelled survivors == independent keep-set", got_lab == exp_lab,
              f"sym-diff={len(got_lab ^ exp_lab)}")
        check("3.3 survivors < raw labelled (something thinned)", len(lab_surv) < len(labelled0),
              f"{len(lab_surv)} vs {len(labelled0)}")

        dropped = labelled_keys - got_lab
        check("3.2 dropped subset of easy band (every dropped class min_dot<=10)",
              all(arch_min[k] <= 10 for k in dropped),
              f"non-easy dropped={[k for k in dropped if arch_min[k] > 10][:3]}")
        check("3.2 no d-o-t>=11 class dropped (all valley/hard present)",
              all(k in got_lab for k in labelled_keys if arch_min[k] >= 11))
        # FA Finding 1: quantify + show the drop is skewed to rare single-path classes (anti-diverse)
        drop_hist = Counter(min(len(key_paths[k]), 5) for k in dropped)
        print(f"       FA1 drop quantified: n_dropped={len(dropped)}  "
              f"n_paths hist(>=5 bucketed)={dict(sorted(drop_hist.items()))}")
        check("3.x build n_dropped == independent", stats["p3"]["n_dropped"] == len(dropped),
              f"{stats['p3']['n_dropped']} vs {len(dropped)}")

        # exemptions present
        print("[phase 3: exemptions present]")
        check("look-alike present in survivors", LOOKALIKE_KEY in rows)
        check("8 named present", EXPECTED_NAMED <= set(rows), f"missing={EXPECTED_NAMED - set(rows)}")
        sh_keys = {_k(r) for r in cen_surv if r["group"] == "short_hard"}
        check("8 short_hard cousins present", len(sh_keys) == 8, f"{len(sh_keys)}")
        check("all 4954 censored present (none dropped)", len(cen_surv) == 4954, f"{len(cen_surv)}")
        check("all 8 named present (none dropped)", len(named_surv) == 8, f"{len(named_surv)}")

        # ============ phase 3.4 diagnostics ============
        print("[phase 3.4: diagnostics]")
        check("every labelled survivor n_paths>=1", all(r["n_paths"] >= 1 for r in lab_surv))
        check("build n_paths == independent (sample 500)",
              all(rows[k]["n_paths"] == len(key_paths[k]) for k in rng.sample(list(got_lab), 500)))
        check("censored+named n_paths==0", all(r["n_paths"] == 0 for r in cen_surv + named_surv))
        check("near_neighbour_count present & >=0 on every row",
              all(isinstance(r["near_neighbour_count"], int) and r["near_neighbour_count"] >= 0
                  for r in survivors))
        check("censored+named near_neighbour_count==0",
              all(r["near_neighbour_count"] == 0 for r in cen_surv + named_surv))
        # FA d.2: validate the proxy against a brute-force recompute on a sample
        nn_sample = rng.sample(lab_surv, 200)
        nn_ok = all(r["near_neighbour_count"] == _brute_nn(r, lab_surv) for r in nn_sample)
        check("3.4 near_neighbour_count == brute force (200 sampled rows)", nn_ok)
        # advisor: deterministically cover the highest-risk r1==r2 self-subtraction branch (the random
        # sample above may miss it). If 0 such rows, the check is honest that the branch is dead.
        ab = [r for r in lab_surv if r["r1"] == r["r2"]]
        check(f"3.4 near_neighbour a==b branch == brute force ({len(ab)} rows)",
              all(r["near_neighbour_count"] == _brute_nn(r, lab_surv) for r in ab))

        # FA d.1: action-space consistency -- consecutive states are true 1-S-move neighbours
        print("[phase 3: action-space consistency (get_neighbors_nj)]")
        solved_recs = [json.loads(l) for l in open(cfg.MERGED_PATHS) if l.strip()]
        solved_recs = [r for r in solved_recs if r["solved"] and r["best_path_length"] >= 1]
        seg_tot = seg_ok = 0
        for rec in rng.sample(solved_recs, 80):
            path, N = rec["best_path"], rec["best_path_length"]
            for m in range(N):
                nxt = canon.canon_key(path[2*(m+1)], path[2*(m+1)+1])[0]
                seg_tot += 1
                if nxt in _neigh_keys(path[2*m], path[2*m+1]):
                    seg_ok += 1
        check("3.1 every consecutive state is a 1-S-move neighbour", seg_ok == seg_tot,
              f"{seg_ok}/{seg_tot}")

        # ============ phase 4 ============
        print("[phase 4: loss metadata]")
        b_soft, b_hard = stats["p4"]["b_soft"], stats["p4"]["b_hard"]
        check("loss_type in {regression,hinge}",
              all(r["loss_type"] in ("regression", "hinge") for r in survivors))
        check("hinge <=> censored", all((r["loss_type"] == "hinge") == bool(r["censored"]) for r in survivors))
        check("bound_B: named->B_hard", all(r["bound_B"] == b_hard for r in named_surv))
        check("bound_B: generic censored->B_soft", all(r["bound_B"] == b_soft for r in cen_surv))
        check("bound_B: labelled->null", all(r["bound_B"] is None for r in lab_surv))
        # FA d.7: anchors survived Phase 4 with their Phase-1 loss-meta intact
        check("anchors hinge + bound_B==B_hard (Phase-4 invariance)",
              all(r["loss_type"] == "hinge" and r["bound_B"] == b_hard for r in named_surv))

        # ============ phase 5 ============
        print("[phase 5: bands & weights]")
        weights = [r["weight"] for r in survivors]
        check("mean(weight)~=1.0 +-0.01", abs(sum(weights) / len(weights) - 1.0) <= 0.01,
              f"{sum(weights)/len(weights):.5f}")
        check("every weight finite & >0", all(math.isfinite(w) and w > 0 for w in weights))

        def region(r):
            return "hard_unsolved" if r["censored"] else cfg.band_of(r["min_dot"])
        regions = [region(r) for r in survivors]
        check("every row in exactly one of 4 regions",
              set(regions) <= set(cfg.TARGET_SHARES) and all(regions))
        n = len(survivors)
        actual = {reg: sum(1 for x in regions if x == reg) / n for reg in cfg.TARGET_SHARES}
        check("FA d.9 easy still down-weighted (actual_share>target)",
              actual["easy"] > cfg.TARGET_SHARES["easy"], f"easy actual={actual['easy']:.3f}")
        total_w = sum(weights)
        band_mass = {reg: sum(r["weight"] for r, rg in zip(survivors, regions) if rg == reg) / total_w
                     for reg in cfg.TARGET_SHARES}
        for reg, tgt in cfg.TARGET_SHARES.items():
            check(f"5.x band-mass[{reg}]~={tgt} (tol 0.03)", abs(band_mass[reg] - tgt) <= 0.03,
                  f"actual={band_mass[reg]:.3f} target={tgt}")
        # FA d.4 + Finding 2: short_hard/named mass share is tiny -> report + assert the x3 *did* apply
        sh_named = [r for r in survivors if r["group"] == "short_hard" or r["tier"] == "named"]
        sh_share = sum(r["weight"] for r in sh_named) / total_w
        print(f"       FA2 short_hard+named loss-mass share = {sh_share*100:.2f}%  ({len(sh_named)} rows)")
        check("short_hard+named share < 1% (scarcity is real; not oversold)", sh_share < 0.01)
        # a short_hard/named row outweighs a same-region (hard_unsolved) generic censored row (x3 applied)
        generic_cen = next(r for r in cen_surv if r["group"] != "short_hard")
        check("short_hard/named row weight > generic censored (x3 multiplier applied)",
              all(r["weight"] > generic_cen["weight"] + 1e-9 for r in sh_named),
              f"generic_cen w={generic_cen['weight']:.3f}")

        # ============ phase 6: emit schema + file ============
        print("[phase 6: emit + schema]")
        expected_fields = set(bt.V2_FIELDS)
        check("V2_FIELDS has exactly 14 fields", len(bt.V2_FIELDS) == 14, f"{len(bt.V2_FIELDS)}")
        emitted = [json.loads(l) for l in open(out_a) if l.strip()]
        check("emitted row count == survivors", len(emitted) == len(survivors),
              f"{len(emitted)} vs {len(survivors)}")
        check("every emitted row has EXACTLY the 14-field set",
              all(set(r.keys()) == expected_fields for r in emitted))
        check("6.2(b) censored => min_dot null & n_obs 0",
              all((r["min_dot"] is None and r["n_obs"] == 0) for r in emitted if r["censored"]))
        check("6.2(d) weight finite & >0 on every emitted row",
              all(math.isfinite(r["weight"]) and r["weight"] > 0 for r in emitted))
        emit_keys = {_k(r) for r in emitted}
        check("6.2(e) 8 named + 8 cousin + look-alike all emitted",
              EXPECTED_NAMED <= emit_keys and LOOKALIKE_KEY in emit_keys
              and len({_k(r) for r in emitted if r["group"] == "short_hard"}) == 8)

        # ============ originals untouched + determinism ============
        print("[originals + determinism]")
        check("6.2(c) dot_archive.jsonl byte-unchanged (originals untouched)", pre_hash == post_hash)
        check("determinism: two runs byte-identical v2", _sha(out_a) == _sha(out_b))
        check("determinism: survivor key-order identical",
              [_k(r) for r in survivors] == [_k(r) for r in survivors_b])
    finally:
        shutil.rmtree(a_dir, ignore_errors=True)
        shutil.rmtree(b_dir, ignore_errors=True)

    # ============ focused unit: stride+cap rule on a single isolated real path ============
    print("[unit: stride+cap on one isolated path]")
    one = os.path.join(".scratch", "dc_one")
    os.makedirs(one, exist_ok=True)
    try:
        # longest solved path -> isolate it so the cross-path union can't mask the per-path rule
        longest = max((json.loads(l) for l in open(cfg.MERGED_PATHS) if l.strip()),
                      key=lambda r: r["best_path_length"] if r["solved"] else -1)
        pf = os.path.join(one, "one.jsonl")
        with open(pf, "w") as f:
            f.write(json.dumps(longest) + "\n")
        kept1, kp1, _, orph1 = _recon_keep(pf, labelled_keys)
        kept_build, _, _ = bt._walk_paths(pf, labelled_keys)
        check("unit: build._walk_paths == independent on isolated path", kept_build == kept1)
        # independently verify the rule: valley/hard all kept; easy kept iff even easy-index (& cap)
        path, N = longest["best_path"], longest["best_path_length"]
        ei = ek = 0
        exp = set()
        cache = {}
        for m in range(N + 1):
            s1, s2 = path[2*m], path[2*m+1]
            key = cache.setdefault((s1, s2), canon.canon_key(s1, s2)[0])
            dot = N - m
            if dot >= 11:
                exp.add(key)
            else:
                if ei % cfg.DIVERSITY_STRIDE == 0 and ek < cfg.PER_PATH_CAP:
                    exp.add(key)
                    ek += 1
                ei += 1
        check("unit: kept == rule(valley/hard + even-easy-index)", kept_build == exp)
        n_easy = sum(1 for m in range(N + 1) if (N - m) <= 10)
        check("cap inert: easy states on longest path < PER_PATH_CAP",
              n_easy < cfg.PER_PATH_CAP, f"easy={n_easy} cap={cfg.PER_PATH_CAP}")
    finally:
        shutil.rmtree(one, ignore_errors=True)

    print()
    if failures:
        print(f"  {len(failures)} check(s) failed: {failures}")
        raise SystemExit("DATA-CRAFTING TESTS FAILED")
    print("DATA-CRAFTING TESTS PASS")


if __name__ == "__main__":
    run_tests()
