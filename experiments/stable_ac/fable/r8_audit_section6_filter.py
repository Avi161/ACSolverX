"""ADVERSARIAL AUDIT of R8 section 6: re-count the length-profile and sharp-profile hits
in the four harvested corpora with an independently written filter.  NEW FILE.

The document's table claims:
    AK(3) classical class          124,296 members,     0 pass L=3n,     0 sharp
    AK(3)+z stable class           171,842 members,     0 pass L=3n,     0 sharp
    AK(2) classical class (control) 13,040 members,     12 pass L=3n,    8 sharp
    AK(2)+z stable class (control)  27,350 members,  5,880 pass L=3n,   48 sharp

`n` is ambiguous in "L = 3n" (number of relators vs number of generators actually
occurring), so both readings are reported.  Members are read from the `canonical` field
(the full presentation), falling back to `pair`, exactly as `certified_targets.py` does.

Usage: python3 experiments/stable_ac/fable/r8_audit_section6_filter.py
"""

from __future__ import annotations

import gzip
import json
import os
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

SOURCES = (
    ("AK(3) classical class", "results/stable_ac/fable/ak3_matched_members.jsonl.gz"),
    ("AK(3)+z stable class",
     "results/stable_ac/fable/stable_contrast_ak3z_members.jsonl.gz"),
    ("AK(2) classical class (control)", "results/stable_ac/fable/ak2_members.jsonl"),
    ("AK(2)+z stable class (control)",
     "results/stable_ac/fable/stable_contrast_ak2z_members.jsonl.gz"),
)


def main():
    print(f"{'corpus':34s} {'members':>9s} {'L=3*nrel':>9s} {'L=3*nlet':>9s} "
          f"{'sharp':>7s} {'sharp+bal':>10s}")
    grand = Counter()
    for name, rel in SOURCES:
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            print(f"{name:34s} MISSING")
            continue
        opener = gzip.open(path, "rt", encoding="utf-8") if path.endswith(".gz") \
            else open(path, encoding="utf-8")
        members = len3rel = len3let = sharp = sharpbal = 0
        examples = []
        with opener as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                words = row.get("canonical") or row.get("pair")
                if not isinstance(words, list) or not words:
                    continue
                words = [w for w in words if w]
                members += 1
                occ = Counter(c.lower() for w in words for c in w)
                nrel = len(words)
                nlet = len(occ)
                L = sum(len(w) for w in words)
                a = L == 3 * nrel
                b = L == 3 * nlet
                if a:
                    len3rel += 1
                if b:
                    len3let += 1
                if b and all(v == 3 for v in occ.values()):
                    sharp += 1
                    if nrel == nlet:
                        sharpbal += 1
                        if len(examples) < 4:
                            examples.append(words)
        print(f"{name:34s} {members:9d} {len3rel:9d} {len3let:9d} {sharp:7d} "
              f"{sharpbal:10d}")
        for ex in examples:
            print(f"{'':34s}   sharp example: {ex}")
        grand[name] = members
    print(f"total AK(3)-class members: "
          f"{grand['AK(3) classical class'] + grand['AK(3)+z stable class']}")


if __name__ == "__main__":
    main()
