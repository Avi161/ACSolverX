"""Gate-style tests for Phase 1 -- anchors (no pytest; matches scripts/test_phase0.py idiom).

Run from the repo root:
    python scripts/test_phase1.py

Prints each check; exits non-zero with 'PHASE1 TESTS FAILED' on any failure, else prints
'PHASE1 TESTS PASS'. Checks re-derive everything independently from canon + the real archive (they
do not trust build_anchors' own output blindly). The determinism check runs main() into two scratch
dirs and diffs them (self-contained -- no dependency on the data-dir artifacts existing).

The expected canonical keys below regression-pin the current dot_archive.jsonl / canon.py.
"""
import os
import sys
import json
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon              # noqa: E402
import dot_config as cfg  # noqa: E402
import dot_dataset        # noqa: E402
import build_anchors as ba  # noqa: E402

EXPECTED_NAMED = {
    "AK(3)": "YXYxyx|YYYYxxx",
    "AK(4)": "YXYxyx|YYYYYxxxx",
    "AK(5)": "YXYxyx|YYYYYYxxxxx",
    "AK(6)": "YXYxyx|YYYYYYYxxxxxx",
    "AK(7)": "YXYxyx|YYYYYYYYxxxxxxx",
    "AK(8)": "YXYxyx|YYYYYYYYYxxxxxxxx",
    "Length 14 #1": "YYYXyyx|YXXYxxx",
    "Length 14 #2": "YYYXyyx|YXXXyxx",
}
EXPECTED_COUSINS = {
    "YXXYx|YYYYXyX", "YXXYx|YYYXyxyX", "YXXYx|YYYYYXXX", "YXYXyX|YYXXXXX",
    "YXYxyx|YXXYxxx", "YXYxyx|YXyXYxx", "YXYxyx|YYYxxxx", "YYxxyX|YYXyxxx",
}
LOOKALIKE_KEY = "YXyxYx|YYYYxxx"  # solved look-alike, distinct from AK(3)


def run_tests():
    failures = []

    def check(name, cond, detail=""):
        if cond:
            print(f"  ok   {name}")
        else:
            print(f"  FAIL {name}  {detail}")
            failures.append(name)

    labelled, censored = dot_dataset.load_archive(cfg.ARCHIVE)
    arch_keys = set(f"{r['r1']}|{r['r2']}" for r in (labelled + censored))
    with open(cfg.PERCENTILES_JSON) as f:
        b_hard = int(json.load(f)["B_hard"])

    # ---- anchors file ----
    print("[anchors]")
    check("anchors.jsonl exists", os.path.exists(cfg.ANCHORS_JSONL))
    rows = []
    if os.path.exists(cfg.ANCHORS_JSONL):
        with open(cfg.ANCHORS_JSONL) as f:
            rows = [json.loads(line) for line in f if line.strip()]
    check("8 anchor rows", len(rows) == 8, f"got {len(rows)}")
    for r in rows:
        tag = f"{r.get('r1')}|{r.get('r2')}"
        ok = (r.get("censored") is True and r.get("min_dot") is None and r.get("n_obs") == 0
              and r.get("sources") == [] and r.get("tier") == "named"
              and r.get("loss_type") == "hinge" and r.get("bound_B") == b_hard
              and r.get("group") == "named")
        check(f"row schema {tag}", ok, f"{r}")
    anchor_keys = {f"{r['r1']}|{r['r2']}" for r in rows}
    check("anchor keys == expected named set", anchor_keys == set(EXPECTED_NAMED.values()),
          f"{anchor_keys ^ set(EXPECTED_NAMED.values())}")

    # ---- named keys re-derived from canon match expected + are absent ----
    print("[named / absent]")
    _, label_to_key = ba.build_named_rows(b_hard)
    check("canon re-derivation == expected named", label_to_key == EXPECTED_NAMED,
          f"{label_to_key}")
    for label, k in label_to_key.items():
        check(f"{label} absent from archive", k not in arch_keys, k)
    # total_len: AK(n) -> 2n+1+6, L14 -> 14
    for n in range(cfg.AK_MIN, cfg.AK_MAX + 1):
        row = next(r for r in rows if f"{r['r1']}|{r['r2']}" == EXPECTED_NAMED[f"AK({n})"])
        check(f"AK({n}) total_len == {2*n+1+6}", row["total_len"] == 2 * n + 1 + 6, f"{row['total_len']}")
    for label in ("Length 14 #1", "Length 14 #2"):
        row = next(r for r in rows if f"{r['r1']}|{r['r2']}" == EXPECTED_NAMED[label])
        check(f"{label} total_len == 14", row["total_len"] == 14, f"{row['total_len']}")

    # ---- trap-set ----
    print("[trap-set]")
    trap = {}
    if os.path.exists(cfg.TRAP_SET_JSON):
        with open(cfg.TRAP_SET_JSON) as f:
            trap = json.load(f)
    check("trap-set 16 keys", len(trap.get("keys", [])) == 16, f"{len(trap.get('keys', []))}")
    named_grp = trap.get("groups", {}).get("named", {})
    short_grp = trap.get("groups", {}).get("short_hard", [])
    check("named group is dict of 8", isinstance(named_grp, dict) and len(named_grp) == 8,
          f"{type(named_grp).__name__} len {len(named_grp)}")
    check("named group == expected", named_grp == EXPECTED_NAMED)
    check("short_hard group has 8", len(short_grp) == 8, f"{len(short_grp)}")
    check("named ∩ short_hard == empty",
          set(named_grp.values()).isdisjoint(set(short_grp)))
    check("union == keys",
          sorted(set(named_grp.values()) | set(short_grp)) == sorted(trap.get("keys", [])))

    # ---- cousins independently recomputed ----
    print("[cousins]")
    recomputed = set(ba.find_cousins(censored))
    check("cousins (censored, len<=13) count == 8", len(recomputed) == 8, f"{len(recomputed)}")
    check("cousins == expected set", recomputed == EXPECTED_COUSINS, f"{recomputed ^ EXPECTED_COUSINS}")
    check("short_hard group == recomputed cousins", set(short_grp) == recomputed)

    # ---- Finding-2 trap ----
    print("[Finding-2]")
    ak3 = EXPECTED_NAMED["AK(3)"]
    check("AK(3) != look-alike", ak3 != LOOKALIKE_KEY)
    check("look-alike in archive", LOOKALIKE_KEY in arch_keys)
    check("AK(3) NOT in archive", ak3 not in arch_keys)
    check("look-alike canon matches", canon.canon_key("YXyxYx", "xxxYYYY")[0] == LOOKALIKE_KEY)

    # ---- Phase-0 coupling ----
    check("anchor bound_B == percentiles B_hard", all(r["bound_B"] == b_hard for r in rows))

    # ---- determinism (self-contained: two scratch runs diffed against each other) ----
    print("[determinism]")
    a, b = os.path.join(".scratch", "phase1_a"), os.path.join(".scratch", "phase1_b")
    try:
        outs = []
        for d in (a, b):
            os.makedirs(d, exist_ok=True)
            aj = os.path.join(d, "anchors.jsonl")
            tj = os.path.join(d, "ak_trap_set.json")
            ba.main(archive=cfg.ARCHIVE, percentiles_json=cfg.PERCENTILES_JSON,
                    anchors_out=aj, trap_out=tj)
            with open(aj, "rb") as f:
                ab = f.read()
            with open(tj) as f:
                tobj = json.load(f)
            with open(tj, "rb") as f:
                tb = f.read()
            outs.append((ab, tb, tobj))
        check("anchors.jsonl byte-identical across runs", outs[0][0] == outs[1][0])
        check("ak_trap_set.json byte-identical across runs", outs[0][1] == outs[1][1])
        check("scratch trap-set re-parses to 16 keys", len(outs[0][2].get("keys", [])) == 16)
    finally:
        shutil.rmtree(a, ignore_errors=True)
        shutil.rmtree(b, ignore_errors=True)

    print()
    if failures:
        print(f"  {len(failures)} check(s) failed: {failures}")
        raise SystemExit("PHASE1 TESTS FAILED")
    print("PHASE1 TESTS PASS")


if __name__ == "__main__":
    run_tests()
