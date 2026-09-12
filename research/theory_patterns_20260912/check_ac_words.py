"""Bounded independent algebra and elementary replay audit; no search or JIT."""

from __future__ import annotations

import argparse
import ast
from collections import Counter, deque
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time

sys.dont_write_bytecode = True
import ac_words as subject


ALPHABET = "xXyY"
INVERSE = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def inverse(word):
    return "".join(INVERSE[c] for c in reversed(word))


def reduce_word(word):
    if not isinstance(word, str) or any(c not in ALPHABET for c in word):
        raise ValueError("invalid free word")
    while True:
        shorter = word
        for pair in ("xX", "Xx", "yY", "Yy"):
            shorter = shorter.replace(pair, "")
        if shorter == word:
            return word
        word = shorter


def canonical(word):
    word = reduce_word(word)
    while len(word) > 1 and INVERSE[word[0]] == word[-1]:
        word = word[1:-1]
    if not word:
        return ""
    candidates = []
    for base in (word, inverse(word)):
        candidates.extend(base[k:] + base[:k] for k in range(len(base)))
    return min(candidates)


def free_words(max_length):
    return ["".join(c) for n in range(max_length + 1)
            for c in itertools.product(ALPHABET, repeat=n)
            if all(INVERSE[a] != b for a, b in zip(c, c[1:]))]


def product(donor, factors):
    pieces = []
    for factor in factors:
        if type(factor.sign) is not int or factor.sign not in (-1, 1):
            raise ValueError("invalid sign")
        pieces.extend((inverse(factor.conjugator),
                       donor if factor.sign == 1 else inverse(donor),
                       factor.conjugator))
    return reduce_word("".join(pieces))


def independent_replay(pair, moves):
    if len(pair) != 2:
        raise ValueError("wrong relator count")
    current = [reduce_word(w) for w in pair]
    for move in moves:
        op = move["op"]
        target = move["target"]
        if type(target) is not int or target not in (1, 2):
            raise ValueError("invalid target")
        i = target - 1
        if op == "invert":
            current[i] = inverse(current[i])
        elif op == "multiply":
            source = move["source"]
            if type(source) is not int or source != 3 - target:
                raise ValueError("invalid source")
            current[i] = reduce_word(current[i] + current[source - 1])
        elif op == "conjugate":
            by = move["by"]
            if not isinstance(by, str) or len(by) != 1 or by not in ALPHABET:
                raise ValueError("invalid elementary conjugator")
            current[i] = reduce_word(INVERSE[by] + current[i] + by)
        else:
            raise ValueError("unsupported operation")
    return current


def legacy_replayer(path):
    source = path.read_text()
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == "replay_elementary")
    namespace = {"deque": deque, "free_reduce": reduce_word}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), namespace)
    return namespace["replay_elementary"], hashlib.sha256(source.encode()).hexdigest()


def run(legacy_path=None):
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    counts, failures = Counter(), []
    legacy, legacy_hash = legacy_replayer(legacy_path) if legacy_path else (None, None)
    words, contexts = free_words(4), free_words(2)
    samples = []
    sample_groups = Counter()

    def require(group, condition, detail=None):
        counts[group] += 1
        if not condition:
            failures.append({"group": group, "detail": detail})

    def rejected(group, fn, detail):
        try:
            fn()
        except (ValueError, TypeError, KeyError, IndexError):
            require(group, True)
        else:
            require(group, False, detail)

    def verify_trace(pair, trace, expected, label):
        require("trace_state", trace.pair == expected, label)
        require("strict_replay", subject.replay(pair, trace.moves) == expected, label)
        require("independent_replay", independent_replay(pair, trace.moves) == expected, label)
        require("emitted_operation_alphabet",
                all(m["op"] in {"invert", "multiply", "conjugate"}
                    and (m["op"] != "conjugate" or len(m["by"]) == 1)
                    for m in trace.moves), label)
        if legacy and sample_groups[label[0]] < 8 and trace.moves:
            require("legacy_replay", legacy(pair, trace.moves) == expected, label)
            sample_groups[label[0]] += 1
            samples.append({"pair": list(pair), "moves": trace.moves, "expected": expected})

    for word in words:
        require("free_reduced_word", subject.red(word) == word, word)
        require("inverse", subject.inv(word) == inverse(word), word)
        core, prefix = subject.cyclic(word)
        require("cyclic_witness", reduce_word(prefix + core + inverse(prefix)) == word, word)
        require("canonical_word", subject.canon(word) == canonical(word), word)
        for target in (0, 1):
            pair = ["xyX", "Yxy"]
            pair[target] = word
            trace = subject.Trace(pair)
            trace.canonicalize(target)
            expected = [reduce_word(w) for w in pair]
            expected[target] = canonical(word)
            verify_trace(pair, trace, expected, ["canonicalize", word, target])
        for right in words:
            raw = word + right
            require("all_short_products", subject.red(raw) == reduce_word(raw), raw)

    for n in range(5):
        for letters in itertools.product(ALPHABET, repeat=n):
            word = "".join(letters)
            require("all_raw_short_reductions", subject.red(word) == reduce_word(word), word)
            require("all_raw_short_canonicalizations", subject.canon(word) == canonical(word), word)

    for donor in words:
        for conjugator in contexts:
            for sign in (-1, 1):
                factors = (subject.Factor(sign, conjugator),)
                expanded = product(donor, factors)
                require("single_factor_expansion", subject.expand_factors(donor, factors) == expanded,
                        [donor, sign, conjugator])
                for target in (0, 1):
                    pair = ["xY", "xY"]
                    pair[1 - target] = donor
                    expected = pair.copy()
                    expected[target] = reduce_word(pair[target] + expanded)
                    trace = subject.Trace(pair)
                    trace.append_factors(target, factors)
                    verify_trace(pair, trace, expected, ["factor", donor, sign, conjugator, target])

    rng = random.Random(20260912)
    for case in range(512):
        donor, initial, context, suffix = (rng.choice(words) for _ in range(4))
        factors = tuple(subject.Factor(rng.choice((-1, 1)), rng.choice(words))
                        for _ in range(rng.randrange(7)))
        expanded = product(donor, factors)
        require("random_factor_product", subject.expand_factors(donor, factors) == expanded, case)
        require("factor_inverse",
                product(donor, subject.inverse_factors(factors)) == inverse(expanded), case)
        require("factor_context_conjugation",
                product(donor, subject.conjugate_factors(factors, context))
                == reduce_word(inverse(context) + expanded + context), case)
        require("factor_simplification",
                product(donor, subject.simplify_factors(factors)) == expanded, case)
        cancelling = factors + subject.inverse_factors(factors)
        require("factor_inverse_cancellation", subject.simplify_factors(cancelling) == (), case)
        target = case % 2
        pair = [initial, initial]
        pair[1 - target] = donor
        trace = subject.Trace(pair)
        trace.append_factors(target, factors)
        expected = pair.copy()
        expected[target] = reduce_word(initial + expanded)
        verify_trace(pair, trace, expected, ["random", case])
        trace.canonicalize(target)
        expected[target] = canonical(expected[target])
        verify_trace(pair, trace, expected, ["random_canonicalized", case])
        require("suffix_factor_transport",
                product(donor, subject.conjugate_factors(factors, inverse(suffix)))
                == reduce_word(suffix + expanded + inverse(suffix)), case)

        w, a, b, c, d = (rng.choice(words) for _ in range(5))
        u, v = reduce_word(w + a), reduce_word(w + b)
        upper_u, upper_v = reduce_word(u + c), reduce_word(v + d)
        require("critical_pair_ledger",
                reduce_word(inverse(upper_u) + upper_v)
                == reduce_word(inverse(c) + inverse(a) + b + d), case)
        u_prime, v_prime = rng.choice(words), rng.choice(words)
        upper_u, upper_v = reduce_word(u_prime + suffix), reduce_word(v_prime + suffix)
        require("common_suffix_ledger",
                reduce_word(inverse(u_prime) + v_prime)
                == reduce_word(suffix + inverse(upper_u) + upper_v + inverse(suffix)), case)

    for bad_sign in (0, 2, -2, True, False, 1.0, -1.0, "1", None):
        rejected("invalid_factor_sign", lambda s=bad_sign: subject.Factor(s, ""), repr(bad_sign))
    for bad_word in ("z", "xz", " ", "x2", None, 1, True):
        rejected("invalid_factor_conjugator", lambda w=bad_word: subject.Factor(1, w), repr(bad_word))
    for method in ("invert", "multiply", "canonicalize", "conjugate", "append_factors"):
        for bad_target in (-1, 2, True, False, 0.0, "0", None):
            def bad_trace_call(name=method, target=bad_target):
                trace = subject.Trace(("x", "y"))
                args = (target, "x") if name == "conjugate" else ((target, ()) if name == "append_factors" else (target,))
                getattr(trace, name)(*args)
            rejected("invalid_trace_target", bad_trace_call, [method, repr(bad_target)])
    for pair in ([], ["x"], ["x", "y", "x"], ["z", "y"]):
        rejected("invalid_replay_pair", lambda p=pair: subject.replay(p, []), pair)
    invalid_moves = [
        {"op": "swap", "target": 1},
        {"op": "automorphism", "target": 1, "images": {"x": "xy", "y": "y"}},
        {"op": "rotate", "target": 1, "by": 1},
        {"op": "normalize", "target": 1},
        {"op": "conjugate_word", "target": 1, "by": "xy"},
        {"op": "multiply", "target": 1, "source": 1},
        {"op": "multiply", "target": 2, "source": 2},
        {"op": "multiply", "target": 1, "source": True},
        {"op": "multiply", "target": 1, "source": 2.0},
    ]
    invalid_moves += [{"op": "invert", "target": value} for value in (0, 3, -1, True, 1.0, "1", None)]
    invalid_moves += [{"op": "conjugate", "target": 1, "by": value} for value in ("", "xy", "xX", "z", 1, None, [], {})]
    invalid_moves += [{}, {"op": "invert"}, {"target": 1}, {"op": "multiply", "target": 1}, {"op": "conjugate", "target": 1}]
    for move in invalid_moves:
        rejected("invalid_elementary_operation", lambda m=move: subject.replay(("x", "y"), [m]), move)

    source = Path(subject.__file__)
    return {
        "status": "pass" if not failures else "fail",
        "subject": str(source.resolve()),
        "subject_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "audit_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seed": 20260912,
        "freely_reduced_words_through_length_4": len(words),
        "conjugators_through_length_2": len(contexts),
        "random_factor_cases": 512,
        "checks": dict(sorted(counts.items())),
        "total_checks": sum(counts.values()),
        "failures": failures,
        "legacy_source": str(legacy_path) if legacy_path else None,
        "legacy_source_sha256": legacy_hash,
        "legacy_method": "AST-extracted replay_elementary, unchanged body; independent reducer injected for initial normalization; no module import or JIT",
        "legacy_sample_count": len(samples),
        "legacy_sample_groups": dict(sample_groups),
        "python_optimization": sys.flags.optimize,
        "corrected_audit_findings": [
            "Factor(0, '') expanded as donor inverse but appended as donor; strict constructor validation now rejects it, booleans, and noninteger signs.",
            "Trace methods accepted some negative or boolean targets; every operation now checks integer target 0 or 1.",
            "replay([], []) accepted zero relators; replay now requires exactly two.",
        ],
        "critical_pair_proof": "u=wA; v=wB; U=uC=wAC; V=vD=wBD. Thus U^-1 V=C^-1 A^-1 B D.",
        "suffix_transport_proof": "For U=U' s and V=V' s, U'^-1 V'=s(U^-1 V)s^-1. Each c^-1 R^e c becomes (c s^-1)^-1 R^e(c s^-1).",
        "runtime_seconds": {"wall": time.perf_counter() - started_wall, "cpu": time.process_time() - started_cpu},
        "scope": "Finite bounded verification and elementary free-group derivations; no presentation search, census experiment, or performance conclusion.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy-replay-source", type=Path)
    args = parser.parse_args()
    report = run(args.legacy_replay_source)
    directory = Path(__file__).resolve().parent
    (directory / "ac_words_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# AC word kernel independent audit", "", f"Status: **{report['status']}**.", "",
             f"Subject SHA-256: `{report['subject_sha256']}`.", "",
             f"{report['total_checks']:,} deterministic checks; 161 freely reduced words through length four, all 25,921 short-word products, and 512 seeded factor products.", "",
             "The independent oracle removes inverse adjacent pairs by repeated string replacement; it does not call the subject's word helpers. Emitted moves are replayed independently and must use only inversion, right multiplication by the other relator, and single-generator conjugation.", "",
             "## Ledger derivations", "", report["critical_pair_proof"], "", report["suffix_transport_proof"], "",
             "## Coverage", "", "| Check | Count |", "|---|---:|"]
    lines.extend(f"| {name} | {count} |" for name, count in report["checks"].items())
    lines += ["", f"Legacy cross-check: {report['legacy_sample_count']} emitted streams, using the unchanged AST-extracted `replay_elementary` body and an independent reducer for initial normalization. No legacy module imports or JIT.", "",
              f"Measured audit wall/CPU: {report['runtime_seconds']['wall']:.6f}/{report['runtime_seconds']['cpu']:.6f} seconds.", "",
              "## Findings", ""]
    lines += ([json.dumps(f, sort_keys=True) for f in report["failures"]] or ["No failures in the declared checks."])
    lines += ["", "Audit findings corrected by the implementation owner before this final run:", ""]
    lines.extend(f"- {finding}" for finding in report["corrected_audit_findings"])
    lines += ["", report["scope"], ""]
    (directory / "ac_words_audit.md").write_text("\n".join(lines))
    print(json.dumps({k: report[k] for k in ("status", "total_checks", "failures", "runtime_seconds")}))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
