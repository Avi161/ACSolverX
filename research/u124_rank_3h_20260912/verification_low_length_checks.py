"""Independent count, sign, and saved-substitution audit of the low-length proofs."""
import itertools
import json
from collections import Counter
from pathlib import Path

import verify as v

HERE = Path(__file__).resolve().parent


def determinant(rows, basis):
    a = [[sum((x == g) - (x == -g) for x in row) for g in basis] for row in rows]
    return sum((-1) ** (sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))) *
               a[0][p[0]] * a[1][p[1]] * a[2][p[2]] for p in itertools.permutations(range(3)))


def main():
    saved = json.loads((HERE / 'rank3_low_length.json').read_text())
    basis = saved['basis']
    replayed = []
    for witness in saved['witnesses']:
        rows = v.words(witness['before'])
        v.require(abs(determinant(rows, basis)) == 1, 'saved residual is not unimodular')
        v.require(all(v.free(w) == w and w[0] != -w[-1] for w in rows), 'residual is not reduced')
        index, g = witness['defining_index'], witness['generator']
        donor = rows[index]
        v.require(sum(abs(x) == g for x in donor) == 1, 'pivot is not singleton')
        pos = next(i for i, x in enumerate(donor) if abs(x) == g)
        left, right = donor[:pos], donor[pos + 1:]
        replacement = v.free(v.invert(left) + v.invert(right) if donor[pos] > 0 else right + left)
        mapping = {old: replacement if old == g else (old,) for old in basis}
        after = v.normalized(tuple(v.image(row, mapping) for i, row in enumerate(rows) if i != index))
        v.require(replacement == v.word(witness['isolating_word']) and after == v.words(witness['after']), 'saved substitution differs')
        v.require(v.size(after) <= v.size(rows) == witness['before_length'] and v.size(after) == witness['after_length'], 'saved length differs')
        replayed.append({'before_length': v.size(rows), 'after_length': v.size(after)})
    v.require(len(replayed) == saved['unimodular_presentations'] == 76, 'residual count differs')

    raw_counts, final_counts = [], []
    for degrees in ((6, 3, 3), (5, 3, 4), (5, 4, 3)):
        outside = tuple(d - n for d, n in zip(degrees, (1, 2, 0)))
        for four in itertools.product(range(5), repeat=3):
            if sum(four) != 4 or any(c > n for c, n in zip(four, outside)):
                continue
            if all(c % 2 == 0 for c in four):
                continue
            if any(c == 1 and d <= 3 for c, d in zip(four, degrees)):
                continue
            five = tuple(n - c for n, c in zip(outside, four))
            entry = [list(degrees), list(four), list(five)]
            raw_counts.append(entry)
            if degrees == (5, 4, 3) and four[2] == 3:
                continue
            final_counts.append(entry)
    expected = [[p['degrees'], p['four_counts'], p['five_counts']] for p in saved['patterns']]
    v.require(sorted(final_counts) == sorted(expected) and len(final_counts) == 5, 'five residual patterns are incomplete')

    scalar_checks = 0
    for eps, tau, sigma, odd in itertools.product((-1, 1), (-1, 1), (-1, 1), (-3, -1, 1, 3)):
        v.require(abs(2 * sigma - tau - 6 * eps * odd) >= 3, 'case B1 determinant exclusion fails')
        if abs(6 * odd - 3 * tau - 2 * eps * sigma) == 1:
            v.require(odd == tau == eps * sigma, 'case B2 forced signs fail')
        scalar_checks += 2
    for delta, sigma, odd, tau in itertools.product((-1, 1), (-1, 1), (-3, -1, 1, 3), (-1, 1)):
        if abs((delta - 2) * sigma + 4 * odd - 2 * tau) == 1:
            v.require(odd == tau == sigma, 'case C2 forced signs fail')
        scalar_checks += 1
    triple_checks = 0
    for other_position in range(4):
        for signs in itertools.product((-1, 1), repeat=4):
            row = tuple(signs[i] * (2 if i == other_position else 1) for i in range(4))
            if v.free(row) != row or row[0] == -row[-1]:
                continue
            v.require(abs(sum(x for x in row if abs(x) == 1)) == 3, 'cyclic triple can have mixed signs')
            triple_checks += 1
    explicit_shapes = []
    for eps in (-1, 1):
        g, h, k = 101, 307, 10 ** 20
        for donor in ((g, g, h, -g, eps * k), (g, g, eps * k, -g, h)):
            pos = donor.index(h)
            repl = v.free(v.invert(donor[:pos]) + v.invert(donor[pos + 1:]))
            output = v.normalized((v.image((g, h, h), {g: (g,), h: repl, k: (k,)}),))[0]
            v.require(len(output) == 3, 'forced three-letter cancellation fails')
            explicit_shapes.append({'donor': donor, 'replacement': repl, 'image': output})

    inequalities = 0
    for rank in range(1, 13):
        for p in range(rank + 1):
            for q in range(rank - p + 1):
                degree_lower, row_lower = 3 * rank + 2 * p + q, 5 * rank - 2 * p - q
                v.require(degree_lower + row_lower == 8 * rank, 'combined bound differs')
                inequalities += 1
    output = {'status': 'PASS', 'rank3_theorem': 'L <= 12 implies a nonincreasing singleton removal',
              'general_theorem': 'No nonincreasing singleton removal implies L >= 4r',
              'hypotheses': 'Nonempty freely and cyclically reduced balanced tuple on its occurring basis; exponent matrix determinant +/-1.',
              'raw_residual_count_patterns': raw_counts, 'five_residual_patterns': final_counts,
              'saved_unimodular_witnesses_replayed': len(replayed), 'scalar_sign_checks': scalar_checks,
              'cyclic_triple_checks': triple_checks, 'forced_cancellation_shapes': explicit_shapes,
              'combined_inequality_controls': inequalities, 'census_searches': 0,
              'sources': {name: v.sha(HERE / name) for name in ('rank3_low_length.md', 'rank3_low_length.py', 'rank3_low_length.json')},
              'script_sha256': v.sha(Path(__file__)),
              'scope': 'Proof review establishes count-case completeness. Saved finite controls supplement it and do not establish known triviality or sharpness.'}
    (HERE / 'verification_low_length.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('status', 'saved_unimodular_witnesses_replayed', 'scalar_sign_checks', 'cyclic_triple_checks')}))


if __name__ == '__main__':
    main()
