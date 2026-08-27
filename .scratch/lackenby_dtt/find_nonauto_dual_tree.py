import argparse
import json

import regina

from explore_dual_tree import (
    canonical_primal_tree,
    dual_spanning_trees,
    exponent_determinant,
    make_triangulation,
    presentation,
    whitehead_minimum,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--height", type=int, default=1)
    parser.add_argument("--trees", type=int, default=80)
    parser.add_argument("--max-triangulations", type=int, default=1000)
    args = parser.parse_args()

    start = make_triangulation("three", 1, 0)
    checked = 0
    answer = None

    def visit(signature, tri):
        nonlocal checked, answer
        checked += 1
        if checked > args.max_triangulations:
            return True
        tri = regina.Triangulation3.fromIsoSig(tri.isoSig())
        primal = canonical_primal_tree(tri)
        rank = tri.countEdges() - tri.countVertices() + 1
        by_minimum = {}
        for dual in dual_spanning_trees(tri, args.trees):
            relators, generators, kept = presentation(tri, primal, dual)
            determinant = exponent_determinant(relators)
            if abs(determinant) != 1:
                raise AssertionError((tri.isoSig(), dual, relators, determinant))
            minimum = whitehead_minimum(relators)
            by_minimum.setdefault(minimum, {
                "dual_tree": sorted(dual),
                "kept_faces": kept,
                "relators": relators,
                "generators": generators,
                "exponent_determinant": determinant,
            })
            if len(by_minimum) > 1:
                answer = {
                    "signature": signature,
                    "iso_sig": tri.isoSig(),
                    "f_vector": [tri.countVertices(), tri.countEdges(),
                                 tri.countTriangles(), tri.size()],
                    "rank": rank,
                    "primal_tree": sorted(primal),
                    "by_whitehead_minimum": by_minimum,
                }
                return True
        return False

    stopped = start.retriangulate(args.height, 1, visit)
    print(json.dumps({
        "regina": regina.versionString(),
        "start": start.isoSig(),
        "checked_triangulations": checked,
        "stopped": stopped,
        "answer": answer,
    }, indent=2))


if __name__ == "__main__":
    main()
