"""restart_planner.py -- rank CoV restart points for a hard presentation.

Turns the ``experiments/IDEAS.md`` findings into an actionable plan for a
production (Colab) run. Given a balanced trivial-group presentation, it builds the
iterated change-of-variables restart tree, filters candidates by the per-relator
cap-fit bound, dedups them by Aut(F2)-orbit, and ranks the reachable restart points
by abelianized magnitude. Feed the ranked list to the greedy at production budget,
best-first.

What this encodes (see ``experiments/IDEAS.md`` and
``literature/proofs/STABLE_AC_NEW.tex``):

- **abelianized-magnitude ranking.** The abelianized magnitude |Sx|+|Sy| of a CoV
  start predicts which candidate the greedy solves (within-presentation AUC 0.92 on
  the 66-set, length-independent). It is a solution-DEPTH proxy -- strong on shallow
  instances, WEAK on the hard residual, and blind on Bridson/Lishak-type presentations
  (near-identity abelianization, astronomical AC-distance). Treat the rank as a prior,
  not a guarantee.
- **iterated CoV.** Single-shot CoV under-explores the stable class; iterating expands
  orbit-reachability roughly geometrically (AK(3): 2 -> 12 -> 55 orbits at hop 1/2/3),
  so a depth-k tree offers far more restart points than one hop.
- **per-relator cap-fit bound** (STABLE_AC_NEW.tex, PROVEN + CHECKED 13712/0): a CoV
  output relator has length <= |K| + c_a(K)*(|m|+|n|); reject a candidate that would
  exceed the cap WITHOUT running the transform.
- **orbit escape needs n_subs>=2** (PROVEN + CHECKED): n_subs=1 CoVs never leave the
  input orbit, so they are re-seeds of the same coordinates, not new restart points.

This is NOT a solver. It plans restart points; the actual search is the user's, at
production budget. Reaching more orbits is NOT progress toward triviality -- for
AK(3) every reachable orbit sits at or above its length-13 floor, and AK(3) stable
triviality remains OPEN. CPU-only; runs no search. Reuses cov.py / word_families /
autcanon read-only (new file, per the branch's new-files-only rule).

Usage:
    python3 -m experiments.stable_ac.cov.restart_planner "xxxYYYY" "xyxYXY" --depth 2 --top 20
"""

from experiments.stable_ac.cov import cov
from experiments.stable_ac import word_families as wf
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.equivalence_classes.lib.autcanon import aut_canon

X_GEN, Y_GEN = 1, 2


def abel_magnitude(r1, r2):
    """|Sum_x| + |Sum_y| over both relators -- the depth-proxy ranking key."""
    def sig(rel, g):
        return sum(1 for s in rel if s == g) - sum(1 for s in rel if s == -g)
    return abs(sig(r1, X_GEN)) + abs(sig(r1, Y_GEN)) + abs(sig(r2, X_GEN)) + abs(sig(r2, Y_GEN))


def one_hop_candidates(r1, r2, cap):
    """Every transformed-relator subword CoV of (r1, r2) that fits ``cap`` per relator.

    Yields (out_r1, out_r2) int-tuple pairs. The cap check is the STABLE_AC_NEW.tex
    per-relator bound applied to the realized (already reduced) output, so nothing
    over-cap is emitted -- consistent with the pipeline's reject_len.
    """
    for z_word in wf.build_a2([word_to_str(r1), word_to_str(r2)]):
        zw = str_to_word(z_word)
        for iso_gen in ("x", "y"):
            for b in cov.cov_branches(r1, r2, zw, iso_gen=iso_gen):
                if max(len(b.r1), len(b.r2)) <= cap:
                    yield b.r1, b.r2


def build_restart_plan(r1_str, r2_str, depth=2, cap=24, max_nodes=400):
    """Build the depth-``depth`` iterated-CoV restart tree and rank the reachable points.

    Returns a list of dicts, ranked by (abel_magnitude, total_length) ascending
    (shallowest-by-proxy first), each: {r1, r2, abel, total_len, hop, orbit_rep}.
    Deduped by Aut(F2)-orbit (aut_canon); the input's own orbit is excluded (a restart
    point should be a genuinely different coordinate system -- orbit escape needs
    n_subs>=2, and same-orbit re-seeds are the input again up to relabelling).
    ``max_nodes`` bounds the tree so the planner stays cheap; it explores the
    lowest-abelianized-magnitude frontier first (best-first expansion).
    """
    base = str_to_word(r1_str), str_to_word(r2_str)
    base_rep = aut_canon((r1_str, r2_str))[1]
    seen = {base_rep}
    plan = {}                      # orbit_rep -> record
    frontier = [(base, 0)]         # (presentation int-tuples, hop)
    while frontier and len(seen) <= max_nodes:
        # expand the most promising frontier node first (lowest abel magnitude)
        frontier.sort(key=lambda pr: abel_magnitude(*pr[0]))
        (cur_r1, cur_r2), hop = frontier.pop(0)
        if hop >= depth:
            continue
        for out_r1, out_r2 in one_hop_candidates(cur_r1, cur_r2, cap):
            rep = aut_canon((word_to_str(out_r1), word_to_str(out_r2)))[1]
            if rep in seen:
                continue
            seen.add(rep)
            rec = {
                "r1": word_to_str(out_r1), "r2": word_to_str(out_r2),
                "abel": abel_magnitude(out_r1, out_r2),
                "total_len": len(out_r1) + len(out_r2),
                "hop": hop + 1, "orbit_rep": rep,
            }
            plan[rep] = rec
            frontier.append(((out_r1, out_r2), hop + 1))
            if len(seen) > max_nodes:
                break
    return sorted(plan.values(), key=lambda r: (r["abel"], r["total_len"]))


def _main(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Rank CoV restart points for a production run.")
    ap.add_argument("r1")
    ap.add_argument("r2")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--cap", type=int, default=24)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--max-nodes", type=int, default=400)
    args = ap.parse_args(argv)
    plan = build_restart_plan(args.r1, args.r2, args.depth, args.cap, args.max_nodes)
    print(f"# Restart plan for <x,y | {args.r1}, {args.r2}>  (depth {args.depth}, cap {args.cap})")
    print(f"# {len(plan)} distinct-orbit restart points; ranked by abel-magnitude (depth proxy -- a PRIOR, not a guarantee).")
    print(f"# Feed these to the greedy at production budget, best-first. Reachability is not solving.")
    print(f"# {'rank':>4} {'abel':>4} {'len':>4} {'hop':>3}  r1 | r2")
    for i, rec in enumerate(plan[: args.top], 1):
        print(f"  {i:>4} {rec['abel']:>4} {rec['total_len']:>4} {rec['hop']:>3}  {rec['r1']} | {rec['r2']}")


if __name__ == "__main__":
    import sys
    _main(sys.argv[1:])
