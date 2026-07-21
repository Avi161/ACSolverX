"""Same-orbit automorphic re-seeds (IMPLEMENTATION_IDEAS.md idea 11).

Generates many automorphic images of the presentation WITHIN its own
Aut(F2)-orbit — compositions of the 20 Whitehead automorphisms up to
``DEPTH`` — and offers them as solve-enabling start re-seeds. The
mechanism this harvests is the idea_bench ms634 finding: an ``n_subs=1``
CoV output with the identical Aut-canonical form solved in 39 nodes
where baseline failed at 1000, and the controls proved the 8 signed
relabels and all rotations never reach such representatives. Candidates
are deduped by ``canon_pair`` (the solver canonicalises its start, so
rotation/inversion/order variants are the SAME search — only genuinely
different strings survive), ranked by the ``(abel, total_len,
max_relator)`` lex key like ``cov_abel_len_lex``.

Distinct from orbit-escape strategies: same orbit by construction, so
this is a search-representation lever, not a new coordinate system —
powerless where the orbit itself is the wall (AK(3)), aimed at the 124.
"""

from experiments.equivalence_classes.lib.autcanon import AUTOS
from experiments.equivalence_classes.lib.words import apply_hom, canon_pair
from experiments.greedy_tests.spec.words import str_to_word
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.restart_planner import abel_magnitude
from experiments.stable_ac.idea_bench.strategies._helpers import ranked

NAME = "reseed_orbit"
KIND = "transform"

DEPTH = 3          # composition depth over the 20 Whitehead autos
MAX_ENUM = 3000    # enumeration bound before ranking (ranked() caps at 60 after)


def candidates(r1, r2, cap):
    start = canon_pair(r1, r2)
    len_bound = 2 * cap    # drop giants: useless and they explode the BFS
    seen = {start}
    frontier = [start]
    for _ in range(DEPTH):
        nxt = []
        for a, b in frontier:
            for phi in AUTOS:
                p = canon_pair(apply_hom(a, phi), apply_hom(b, phi))
                if p in seen or max(len(p[0]), len(p[1])) > len_bound:
                    continue
                seen.add(p)
                nxt.append(p)
            if len(seen) > MAX_ENUM:
                break
        if len(seen) > MAX_ENUM:
            break
        frontier = nxt
    out = []
    for a, b in sorted(seen - {start}):
        ccap = max(cap, max(len(a), len(b)) + cov.CAP_HEADROOM)
        out.append((a, b, ccap, abel_magnitude(str_to_word(a), str_to_word(b))))
    return ranked(out, key=lambda t: (t[3], len(t[0]) + len(t[1]),
                                      max(len(t[0]), len(t[1]))))
