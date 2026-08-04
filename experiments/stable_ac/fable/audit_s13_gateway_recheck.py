"""Throwaway adversarial re-check of S13 section 3a's six gamma_N = 1 gateways.

Independent of the sweep that produced them: re-runs Todd-Coxeter, the cut-scheme
solver (lower bound gamma_N >= 1) and the stored rotation witness (upper bound
gamma_N <= 1), and the exact census where the compatible family is affordable.

Audit-only.  Writes nothing outside stdout.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from experiments.stable_ac.fable.coset_enum import is_trivial_group  # noqa: E402
from experiments.stable_ac.fable.disconnected_split import decide_pair  # noqa: E402
from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n  # noqa: E402
from experiments.stable_ac.fable.witness_check_n import check_witness_n  # noqa: E402

SWEEP = "results/stable_ac/fable/u124_sweep.jsonl"
ROWS = ["aca_117", "aca_11", "aca_121", "aca_17", "aca_30", "aca_122", "aca_115"]
CENSUS_CAP = 600_000


def main() -> None:
    by_name = {}
    with open(SWEEP) as fh:
        for line in fh:
            r = json.loads(line)
            by_name[r["name"]] = r

    for name in ROWS:
        row = by_name[name]
        pair = tuple(row["pair"])
        out = {"name": name, "pair": pair,
               "total_length": sum(len(w) for w in pair)}

        tc = is_trivial_group(pair, cap=2_000_000)
        out["tc"] = (tc.get("status"), tc.get("index"), tc.get("trivial"))

        t0 = time.time()
        dec = decide_pair(pair)
        # decide_pair returns a dataclass or dict depending on version
        d = dec if isinstance(dec, dict) else getattr(dec, "__dict__", {"repr": repr(dec)})
        out["decide"] = {k: d.get(k) for k in ("verdict", "support_kind", "exhaustive")}
        if not out["decide"]["verdict"]:
            out["decide"] = {"raw": repr(dec)[:200]}
        out["decide_s"] = round(time.time() - t0, 3)

        fam = row["census_family_size"]
        out["family"] = fam
        if fam <= CENSUS_CAP:
            t0 = time.time()
            cen = gamma_N_factorial_n(pair, cap_rotations=fam + 10)
            out["census"] = {"minimum_defect": cen.get("minimum_defect"),
                             "enumerated": cen.get("enumerated_cases"),
                             "s": round(time.time() - t0, 2)}
        else:
            out["census"] = "SKIPPED (family > cap)"

        samp = row.get("sample") or {}
        wit = samp.get("witness")
        if wit:
            rot = {int(k): v for k, v in wit.items()}
            try:
                chk = check_witness_n(pair, rot)
                out["witness"] = {"ok": True, "res": str(chk)[:200]}
            except Exception as exc:  # noqa: BLE001
                out["witness"] = {"ok": False, "err": f"{type(exc).__name__}: {exc}"}
        else:
            out["witness"] = None

        print(json.dumps(out, default=str))


if __name__ == "__main__":
    main()
