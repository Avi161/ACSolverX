"""Exhaust the cut/sign choices on five small ordinary-prefix fixtures."""
import hashlib
import itertools
import json
from pathlib import Path
import time

from experiments.equivalence_classes.lib.words import canon_pair, replay_move
from .compile_search_prefix import compile_prefix

HERE = Path(__file__).resolve().parent


def main():
    cpu = time.process_time()
    fixtures = [("xyXXY", "YXyx"), ("x", "y"), ("xyx", "yxx"),
                ("xyXY", "xxY"), ("xyX", "YYxx")]
    checked = 0
    for pair in fixtures:
        start = canon_pair(*pair)
        for target, sign in itertools.product((1, 2), (1, -1)):
            for first, second in itertools.product(range(len(start[target-1])), range(len(start[2-target]))):
                move = (target, sign, first, second)
                expected = replay_move(start, move)
                certificate = compile_prefix(pair, [start, expected],
                                             [{"kind": "substitution", "move": "_".join(map(str, move))}])
                if certificate["endpoint"] != list(expected):
                    raise ValueError("independent oracle endpoint mismatch")
                checked += 1
    bad = [{"kind": "automorphism", "move": "1_1_0_0"},
           {"kind": "substitution", "move": "3_1_0_0"},
           {"kind": "substitution", "move": "1_0_0_0"},
           {"kind": "substitution", "move": "1_1_2_0"}]
    for step in bad:
        try:
            compile_prefix(("x", "y"), [("X", "Y"), ("X", "Y")], [step])
        except ValueError:
            continue
        raise ValueError("corrupt step accepted")
    report = {"status": "pass", "cut_sign_target_cases": checked, "rejected_corruptions": len(bad),
              "cpu_seconds": time.process_time()-cpu,
              "hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (Path(__file__), HERE / "compile_search_prefix.py", HERE / "ac_words.py")},
              "scope": "Different solver and research canonical alphabets bridged by explicit witnesses. Every generator-level stream is replayed by ac_words.replay and compared with the separate pure-Python substitution oracle."}
    (HERE / "compile_search_prefix_checks.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
