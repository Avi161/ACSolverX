"""W3a: does AK(3)'s AC component close at ceilings 18/19 under 1,000 pops?

The certified ceiling-17 component of AK(3) under the full Definition-2.1
move set closes at exactly 1,000 canonical states (scan_ak3_component.py,
schema ak3-component-thickenability-v1). Raising the ceiling destroys that
closure unless the larger component still fits under the hard 1,000-pop
law. This probe re-implements the ~30-line BFS with the ceiling and the
per-relator cap as explicit parameters (both raised together: cap =
ceiling - 1, matching the certified run's convention) and reports, per
ceiling, either

  CLOSED  n_states (n <= 1,000; queue exhausted; closure replay passed)
  EXCEEDS (the 1,001st pop would be needed; no sample is reported —
           a truncated BFS is not a frontier, per the advisor review)

Schema: ak3-component-ceiling-probe-v1 records (ceiling, per-relator cap,
pop cap, verdict, state count). This probe makes no thickenability claim;
a CLOSED verdict feeds the separate certified planarity dispatch.
"""
from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.equivalence_classes.lib.acmoves import canon, children

AK3 = ("xxxYYYY", "xyxYXY")
POP_CAP = 1_000


def probe(ceiling):
    cap = ceiling - 1
    root = canon(*AK3, cyclic=True)
    assert canon(*root, cyclic=True) == root
    seen = {root}
    queue = deque([root])
    pops = 0
    while queue:
        if pops >= POP_CAP:
            return {"schema": "ak3-component-ceiling-probe-v1",
                    "ceiling": ceiling, "cap": cap, "pop_cap": POP_CAP,
                    "verdict": "EXCEEDS", "states_at_cutoff": len(seen)}
        state = queue.popleft()
        pops += 1
        for child in children(state[0], state[1], cap=cap, cyclic=True,
                              seam_only=False):
            assert canon(*child, cyclic=True) == child
            if len(child[0]) + len(child[1]) > ceiling:
                continue
            if child not in seen:
                seen.add(child)
                queue.append(child)
    # closure replay: no in-ceiling child of any seen state escapes seen
    for state in seen:
        for child in children(state[0], state[1], cap=cap, cyclic=True,
                              seam_only=False):
            if len(child[0]) + len(child[1]) <= ceiling:
                assert child in seen, ("closure violation", state, child)
    return {"schema": "ak3-component-ceiling-probe-v1",
            "ceiling": ceiling, "cap": cap, "pop_cap": POP_CAP,
            "verdict": "CLOSED", "states": len(seen), "pops": pops}


def main():
    for ceiling in [int(a) for a in sys.argv[1:]] or [17, 18]:
        print(json.dumps(probe(ceiling)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
