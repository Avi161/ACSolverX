"""Independent sharp rank-four local-minimum and ordinary escape audit."""
import itertools
import json
from collections import Counter
from pathlib import Path
import verify as v

HERE = Path(__file__).resolve().parent


def main():
    path = HERE / 'exchange_rank4_sharp.json'
    saved = json.loads(path.read_text())
    rows, basis = v.words(saved['initial']), saved['basis']
    matrix = [[sum((x == g) - (x == -g) for x in row) for g in basis] for row in rows]
    det = sum((-1) ** sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)) *
              matrix[0][p[0]] * matrix[1][p[1]] * matrix[2][p[2]] * matrix[3][p[3]] for p in itertools.permutations(range(4)))
    v.require(matrix == saved['exponent_matrix'] and det == saved['determinant'] == 1, 'sharp example determinant differs')
    found = []
    for index, donor in enumerate(rows):
        for generator, degree in Counter(map(abs, donor)).items():
            if degree != 1:
                continue
            pos = next(i for i, x in enumerate(donor) if abs(x) == generator)
            left, right = donor[:pos], donor[pos + 1:]
            replacement = v.free(v.invert(left) + v.invert(right) if donor[pos] > 0 else right + left)
            mapping = {g: replacement if g == generator else (g,) for g in basis}
            after = v.normalized(tuple(v.image(row, mapping) for i, row in enumerate(rows) if i != index))
            v.require(v.size(after) == 17, 'sharp example has nonincreasing removal')
            found.append((index, generator, after))
    expected = {(w['defining_index'], w['generator']): v.words(w['after']) for w in saved['all_single_occurrence_checks']}
    v.require(len(found) == 4 and {(i, g): after for i, g, after in found} == expected, 'not all sharp example pivots were checked')
    g, h, u, root_v = basis
    commutator = (g, h, -g, -h)
    v.require(rows == ((g, u, u), (h, root_v, root_v), (u,) + v.invert(commutator), (root_v,) + commutator), 'sharp example group proof frame differs')
    cursor, boundaries = rows, [[4, 16]]
    for event in saved['events']:
        v.require(v.words(event['before']) == cursor, 'sharp escape is discontinuous')
        cursor = v.verify_event(event, known_trivial=True)
        boundaries.append([len(cursor), v.size(cursor)])
    v.require(cursor == () and boundaries == saved['rank_length_boundaries'], 'sharp escape boundaries differ')
    v.require(v.verify_event(saved['events'][0], known_trivial=False) == v.words(saved['events'][0]['after']), 'sharp escape first move needs an unnecessary stable premise')
    output = {'status': 'PASS', 'rank': 4, 'initial_length': 16, 'determinant': 1,
              'all_singleton_removals_checked': 4, 'every_removal_length': 17, 'escape_boundaries': boundaries,
              'known_triviality_proof': 'Put C=[g,h]. The last rows give u=C and v=C^-1; the first rows give g=u^-2 and h=u^2. Thus C=[u^-2,u^2]=1 and every generator is trivial.',
              'ordinary_escape_identity': 'For R=u C^-1 and donor D=v C, R (v^-1 D v)=u v.',
              'extension': 'Disjoint-basis copies give sharp examples at every positive rank divisible by4; all singleton removals act within one copy and increase total length by1.',
              'scope': 'Sharpness for irreducibility under nonincreasing singleton removal, not under ordinary AC and not an AC counterexample.',
              'source_sha256': v.sha(path), 'census_searches': 0}
    (HERE / 'verification_sharp_rank4.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
