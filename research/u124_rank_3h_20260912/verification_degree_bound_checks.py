"""Small word-accounting controls, not presentation search."""
from collections import Counter
from itertools import combinations_with_replacement, product
import json
from pathlib import Path

from verification_preparer_checks import isolate
import verify


HERE = Path(__file__).resolve().parent


def main():
    alphabet = (2, -2, 5, -5)
    representatives = set()
    for length in range(1, 5):
        for value in product(alphabet, repeat=length):
            if verify.free(value) == value and verify.independent.representative(value) == value:
                representatives.add(value)
    tuple_checks, removal_checks, degree_one, degree_two = 0, 0, 0, 0
    irreducible_strict, irreducible_nonstrict = [], []
    for before in combinations_with_replacement(sorted(representatives), 2):
        matrix = [[w.count(g) - w.count(-g) for g in (2, 5)] for w in before]
        if abs(matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) != 1:
            continue
        degree = Counter(abs(x) for w in before for x in w)
        deltas = []
        for i, donor in enumerate(before):
            for g in degree:
                if sum(abs(x) == g for x in donor) != 1:
                    continue
                definition = isolate(donor, g)
                mapping = {h: (h,) for h in degree}
                mapping[g] = definition
                after = verify.normalized(tuple(verify.image(w, mapping) for j, w in enumerate(before) if j != i))
                delta = verify.size(after) - verify.size(before)
                bound = (degree[g] - 2) * (len(donor) - 2) - 2
                verify.require(delta <= bound, 'single-occurrence elimination exceeds degree/length bound')
                if degree[g] == 1:
                    verify.require(delta <= -len(donor), 'degree-one removal is not strict')
                    degree_one += 1
                if degree[g] == 2:
                    verify.require(delta <= -2, 'degree-two removal loses claimed gain')
                    degree_two += 1
                deltas.append(delta)
                removal_checks += 1
        for g, d in degree.items():
            if d == 2:
                verify.require(all(sum(abs(x) == g for x in row) <= 1 for row in before), 'unimodular degree-two column lies in one row')
        if not any(delta < 0 for delta in deltas):
            verify.require(verify.size(before) >= 7, 'strict local irreducibility violates3r+1 bound')
            irreducible_strict.append(before)
        if not any(delta <= 0 for delta in deltas):
            verify.require(verify.size(before) >= 8, 'nonstrict local irreducibility violates3r+2 bound')
            irreducible_nonstrict.append(before)
        tuple_checks += 1
    for singleton in ((2,), (-2,)):
        verify.require(isolate(singleton, 2) == () and verify.size(()) - len(singleton) == -1, 'rank1 singleton boundary differs')
    unreduced = (2, 2, -2)
    verify.require(unreduced.count(2) - unreduced.count(-2) == 1 and len(unreduced) == 3 and verify.free(unreduced) == (2,), 'missing-normalization counterexample differs')
    result = {'status': 'PASS', 'normalized_unimodular_rank2_tuples_checked': tuple_checks,
              'symbolic_eliminations_checked': removal_checks, 'degree1_controls': degree_one, 'degree2_controls': degree_two,
              'strictly_irreducible_in_control_set': len(irreducible_strict), 'nonincreasing_irreducible_in_control_set': len(irreducible_nonstrict),
              'rank1_singletons_checked': 2, 'unnormalized_counterexample': unreduced,
              'empty_tuple': 'Excluded from both positive-rank statements; its rank and length are0.',
              'scope': 'Algebraic substitution-length check only; unimodularity is not asserted to imply group triviality or stable-AC legality.',
              'census_searches': 0, 'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
    (HERE / 'verification_degree_bound.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'normalized_unimodular_rank2_tuples_checked', 'symbolic_eliminations_checked', 'degree1_controls', 'degree2_controls')}, indent=2))


if __name__ == '__main__':
    main()
