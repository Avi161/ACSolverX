"""Deterministic algebra and certificate checks; no heap search."""

import hashlib
import json
import random
from pathlib import Path
from time import perf_counter, process_time

from .ac_words import Factor, Trace, expand_factors, exponent, inv, red, replay
from .critical_pairs import (
    complete, critical_word, normalize, orient, reduce_pair, seed_rules,
    verify_rule,
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def finish_generator(pair):
    trace = Trace(pair)
    donor = next(i for i in (0, 1) if len(trace.pair[i]) == 1)
    if trace.pair[donor].isupper():
        trace.invert(donor)
    letter = trace.pair[donor]
    target = 1 - donor
    while any(c.lower() == letter for c in trace.pair[target]):
        word = trace.pair[target]
        i = max(k for k, c in enumerate(word) if c.lower() == letter)
        trace.append_factors(target, (Factor(-1 if word[i].islower() else 1, word[i + 1:]),))
    require(len(trace.pair[target]) == 1, "unimodular generator cleanup failed")
    if trace.pair[target].isupper():
        trace.invert(target)
    if trace.pair == ['y', 'x']:
        trace.multiply(0)
        trace.invert(0)
        trace.multiply(1)
        trace.invert(0)
        trace.conjugate(0, 'y')
        trace.multiply(0)
        trace.invert(1)
    require(trace.pair == ['x', 'y'], "bad terminal basis")
    require(replay(pair, trace.moves) == trace.pair, "cleanup replay mismatch")
    return trace


def run():
    started, cpu = perf_counter(), process_time()
    rng = random.Random(20260912)
    checked_rules = contexts = overlaps = replayed = 0
    donors = ['yxYXX', 'YXXXyxx', 'YXYxyx', 'YYXXXyx', 'x', 'xyXYx']
    for donor in donors:
        rules, _ = complete(donor, max_critical=250, cpu_seconds=2)
        for rule in rules:
            verify_rule(donor, rule)
            checked_rules += 1
        for _ in range(32):
            word = red(''.join(rng.choice('xXyY') for _ in range(14)))
            result, ledger, _, _ = normalize(word, rules, max_steps=64)
            require(red(inv(word) + result) == expand_factors(donor, ledger), "context defect")
            trace = Trace([donor, word])
            trace.append_factors(1, ledger)
            require(replay([donor, word], trace.moves) == [donor, result], "context replay")
            contexts += 1
            replayed += 1
        for first in rules[:10]:
            for second in rules[:10]:
                for offset in range(len(first.lhs)):
                    critical = critical_word(first, second, offset)
                    if critical is None:
                        continue
                    word, u, v, a, b = critical
                    require(red(inv(word) + u) == expand_factors(donor, a), "first overlap")
                    require(red(inv(word) + v) == expand_factors(donor, b), "second overlap")
                    overlaps += 1

    donor, companion = 'YXYxyx', 'XYXyy'
    det = exponent(donor, 'x') * exponent(companion, 'y') - exponent(donor, 'y') * exponent(companion, 'x')
    require(abs(det) == 1, "planted example must be unimodular")
    seeds = seed_rules(donor)
    require(reduce_pair([donor, companion], 0, seeds)['pair'][1] == companion, "seed-only control changed")
    rules, stats = complete(donor, max_critical=400, cpu_seconds=2)
    reduction = reduce_pair([donor, companion], 0, rules)
    require(reduction['pair'] == [donor, 'X'], "overlap example did not expose generator")
    tail = finish_generator(reduction['pair'])
    moves = reduction['moves'] + tail.moves
    require(replay([donor, companion], moves) == ['x', 'y'], "full positive certificate")
    replayed += 1

    for max_critical in (0, 1, 5):
        rules, stats_limit = complete(donor, max_critical=max_critical, cpu_seconds=2)
        require(stats_limit['critical_pairs'] <= max_critical, "critical work cap")
        result = reduce_pair([donor, companion], 0, rules, max_steps=0)
        require(replay([donor, companion], result['moves']) == result['pair'], "partial path")
        replayed += 1
    bad = orient('xxx', 'y', (Factor(1, ''),))
    try:
        verify_rule('x', bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid rule accepted")
    return {
        'passed': True, 'heap_nodes': 0, 'checked_rules': checked_rules,
        'contexts': contexts, 'overlap_branches': overlaps, 'replayed_paths': replayed,
        'cpu_seconds': process_time() - cpu, 'wall_seconds': perf_counter() - started,
        'positive_example': {'input': [donor, companion], 'seed_only_target': companion,
                             'derived_rules_stats': stats, 'generator_prefix_moves': len(reduction['moves']),
                             'elementary_moves': len(moves), 'moves': moves, 'endpoint': ['x', 'y']},
    }


if __name__ == '__main__':
    report = run()
    here = Path(__file__).resolve().parent
    report['source_sha256'] = {
        name: hashlib.sha256((here / name).read_bytes()).hexdigest()
        for name in ('ac_words.py', 'critical_pairs.py', 'check_critical_pairs.py')
    }
    (here / 'critical_pairs_checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print({k: v for k, v in report.items() if k not in ('positive_example', 'source_sha256')})
