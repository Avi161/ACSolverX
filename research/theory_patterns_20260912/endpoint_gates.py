"""Cheap terminal hypotheses on saved theorem endpoints after basis descent."""

from collections import Counter
import json
from pathlib import Path
import re
import time

from experiments.equivalence_classes.lib.words import canon_pair
from research.supermoves_20260908.cheap_gates import bs_gate, canonical_two_block_gate
from research.supermoves_20260908.christoffel_primitive_gate import recognize_canonical
from research.supermoves_20260908.consecutive_bs import collapse
from research.supermoves_20260908.stable_power_Q import _recognize as q_recognize
from .ms_family_verify import R, canon, cyclic_variants
from .check_complement import sha256

HERE = Path(__file__).resolve().parent


def ms_matches(pair):
    matches = []
    for donor_index in (0, 1):
        for base in "xXyY":
            for stable in "xXyY":
                if base.lower() == stable.lower():
                    continue
                mapping = str.maketrans({base: "y", base.swapcase(): "Y",
                                        stable: "x", stable.swapcase(): "X"})
                donor = pair[donor_index].translate(mapping)
                n = (len(donor) - 3) // 2
                if n < 1 or canon(donor) != canon(R(n)):
                    continue
                companion = pair[1 - donor_index].translate(mapping)
                for word in cyclic_variants(companion):
                    match = re.fullmatch("X([yY]*)X([yY]*)x([yY]*)", word)
                    if match is None:
                        continue
                    a, r, s = (w.count("y") - w.count("Y") for w in match.groups())
                    terminal = r % n == 0 or s % (n + 1) == 0 or any(
                        (r - sign) % n == 0 and (s + sign) % (n + 1) == 0 for sign in (-1, 1))
                    matches.append({"donor_index": donor_index, "base": base, "stable": stable,
                                    "n": n, "k": -a, "r": r, "s": s, "terminal": terminal})
    return matches


def main():
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    source_path = HERE / "endpoint_nielsen.jsonl"
    rows, global_seen, counts = [], set(), Counter()
    with source_path.open() as source:
        for line in source:
            row = json.loads(line)
            seen, matches, bs_charges = set(), [], 0
            for index, state in enumerate(row["states"]):
                pair = canon_pair(*state["best_pair"])
                if pair in seen:
                    continue
                seen.add(pair)
                global_seen.add(pair)
                hits = {}
                primitive = [i for i, word in enumerate(pair) if recognize_canonical(word)]
                if primitive:
                    hits["primitive"] = primitive
                if canonical_two_block_gate(pair):
                    hits["two_block"] = True
                q = q_recognize(pair)
                if q:
                    hits["stable_power_Q"] = q
                ms = ms_matches(pair)
                if ms:
                    hits["ms_residue"] = ms
                bs = bs_gate(pair, general=True)
                if bs:
                    counts["consecutive_bs_matches"] += 1
                    if bs_charges < 1000:
                        result = collapse(pair, budget=1000 - bs_charges, intermediate_cap=512)
                        bs_charges += result["nodes_explored"]
                        counts["consecutive_bs_" + result["reason"]] += 1
                        if result["solved"]:
                            hits["consecutive_bs_solved"] = result
                if hits:
                    matches.append({"pair": pair, "endpoint_state_index": index, "hits": hits})
            counts["endpoint_rows"] += len(seen)
            counts["bs_charges"] += bs_charges
            rows.append({"name": row["name"], "distinct_pairs_checked": len(seen),
                         "bs_charges": bs_charges, "matches": matches})
    result = {"status": "recognition_screen_complete", "source_sha256": sha256(source_path),
              "script_sha256": sha256(Path(__file__)), "rows": rows, "counts": dict(counts),
              "globally_distinct_pairs": len(global_seen),
              "terminal_candidate_ids": [r["name"] for r in rows if any(
                  any(key in m["hits"] for key in ("primitive", "two_block", "stable_power_Q", "consecutive_bs_solved"))
                  or any(h["terminal"] for h in m["hits"].get("ms_residue", [])) for m in r["matches"])],
              "scope": "Existing sufficient terminal gates plus new MS residue theorem, on saved strict-Nielsen endpoints. Gates alone are not counted as new certificates. Consecutive BS collapse has a shared 1000 rewrite-unit cap per input and cap512.",
              "cpu_seconds": time.process_time() - started_cpu,
              "wall_seconds": time.perf_counter() - started_wall}
    (HERE / "endpoint_gates.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
