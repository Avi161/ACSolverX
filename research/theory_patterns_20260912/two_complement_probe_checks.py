"""Independent replay of the bounded two-complement prototype's saved data."""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DOMAIN = 'rstu'
DENC = {g: i + 1 for i, g in enumerate(DOMAIN)}
DENC.update({g.upper(): -v for g, v in list(DENC.items())})
XENC = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}


def need(value, message):
    if not value:
        raise ValueError(message)


def decode(word, alphabet):
    inverse = {v: k for k, v in alphabet.items()}
    return ''.join(inverse[v] for v in word)


def encode(word, alphabet):
    need(isinstance(word, str) and all(c in alphabet for c in word), 'bad word')
    return tuple(alphabet[c] for c in word)


def reduce(word):
    stack = []
    for value in word:
        if stack and stack[-1] == -value:
            stack.pop()
        else:
            stack.append(value)
    return tuple(stack)


def inverse(word):
    return tuple(-v for v in reversed(word))


def apply(word, mapping):
    out = []
    for v in word:
        image = mapping[abs(v)]
        out.extend(image if v > 0 else inverse(image))
    return reduce(out)


def move(words, record):
    result = list(words)
    op = record['op']
    if op == 'permute':
        need(sorted(record['order']) == list(range(len(words))), 'bad permutation')
        return tuple(words[i] for i in record['order'])
    i = record['target']
    need(type(i) is int and 0 <= i < len(words), 'bad target')
    if op == 'invert':
        result[i] = inverse(words[i])
    else:
        need(op == 'multiply', 'non-Nielsen operation')
        j = record['donor']; sign = record['sign']; side = record['side']
        need(type(j) is int and 0 <= j < len(words) and i != j, 'bad donor')
        need(type(sign) is int and sign in (-1, 1) and side in ('left', 'right'), 'bad product')
        donor = words[j] if sign == 1 else inverse(words[j])
        result[i] = reduce(words[i] + donor if side == 'right' else donor + words[i])
    return tuple(result)


def canonical(word):
    word = reduce(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = word[1:-1]
    return min((decode(w[i:] + w[:i], XENC) for w in (word, inverse(word)) for i in range(len(w))), default='')


def pair_key(pair):
    return tuple(sorted(canonical(encode(w, XENC)) for w in pair))


def independent_full_fold(words):
    arcs, count = [], 1
    for word in words:
        values = reduce(encode(word, XENC)); source = 0
        for index, v in enumerate(values):
            target = 0 if index + 1 == len(values) else count
            if target:
                count += 1
            arcs.extend([(source, v, target), (target, -v, source)])
            source = target
    classes = [{i} for i in range(count)]
    while True:
        belongs = {v: i for i, block in enumerate(classes) for v in block}
        transitions = {}
        collision = None
        for source, letter, target in arcs:
            key, destination = (belongs[source], letter), belongs[target]
            if key in transitions and transitions[key] != destination:
                collision = transitions[key], destination
                break
            transitions[key] = destination
        if collision is None:
            return len(classes) == 1 and set(transitions) == {(0, v) for v in (1, -1, 2, -2)}
        a, b = sorted(collision)
        classes[a].update(classes[b]); classes.pop(b)


def verify_record(row):
    pair, initial = row['input'], row['initial_image_tuple']
    need(initial == [*pair, 'x', 'yy'], 'wrong fixed complements')
    full = independent_full_fold(initial)
    need(full == row['join_is_full'], 'independent full-fold result differs')
    need(sum(row['image_evaluation_counts'].values()) == row['image_evaluations'] <= row['image_limit'] <= 1000, 'shared image budget failed')
    if not full:
        need(row['status'] == 'join_not_full' and row['projected'] is None and row['image_evaluations'] == 0, 'bad join rejection')
        return {'join_rejected': True, 'basis_verified': False, 'projected_verified': False}
    search = row['search']
    images = tuple(encode(w, XENC) for w in initial)
    basis = tuple((i,) for i in range(1, 5))
    for operation in search['nielsen_row_moves']:
        images, basis = move(images, operation), move(basis, operation)
    need(list(map(lambda w: decode(w, XENC), images)) == search['images'], 'image tuple path failed')
    need(list(map(lambda w: decode(w, DENC), basis)) == search['domain_basis'], 'domain basis path failed')
    inverse_basis = tuple(encode(w, DENC) for w in search['inverse_domain_basis'])
    for i in range(4):
        need(apply(basis[i], dict(enumerate(inverse_basis, 1))) == (i + 1,), 'forward-then-backward basis failed')
        need(apply(inverse_basis[i], dict(enumerate(basis, 1))) == (i + 1,), 'backward-then-forward basis failed')
    marked = [apply(w, {i + 1: encode(initial[i], XENC) for i in range(4)}) for w in basis]
    need(marked == list(images), 'basis image marking differs')
    projected = row['projected']
    if projected is None:
        return {'join_rejected': False, 'basis_verified': True, 'projected_verified': False}
    need(search['images'] == ['', '', 'x', 'y'], 'kernel basis terminal marking differs')
    tag_words = [reduce(tuple((abs(v) - 2) * (1 if v > 0 else -1) for v in w if abs(v) > 2)) for w in basis[:2]]
    need([decode(w, XENC) for w in tag_words] == projected['pair'], 'tag projection failed')
    matrix = [[sum(1 if v == g else -1 if v == -g else 0 for v in w) for g in (1, 2)] for w in tag_words]
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    need(abs(determinant) == 1 and determinant == projected['determinant'], 'projected determinant failed')
    need(projected['total_length'] == sum(map(len, tag_words)), 'projected length failed')
    need(projected['cyclic_inverse_permutation_match'] == (pair_key(projected['pair']) == pair_key(pair)), 'exact cyclic comparison differs')
    normalization = projected.get('bounded_projected_Nielsen')
    if normalization:
        current = pair_key(projected['pair'])
        need(list(current) == normalization['start'], 'projected Nielsen start differs')
        for step in normalization['steps']:
            need(step['before'] == list(current), 'Nielsen trace discontinuity')
            mapping = {i: encode(step['images'][g], XENC) for i, g in enumerate('xy', 1)}
            backwards = {i: encode(step['inverse_images'][g], XENC) for i, g in enumerate('xy', 1)}
            for i in (1, 2):
                need(apply(mapping[i], backwards) == (i,) and apply(backwards[i], mapping) == (i,), 'rank2 Nielsen inverse failed')
            current = tuple(sorted(canonical(apply(encode(w, XENC), mapping)) for w in current))
            need(list(current) == step['after'], 'projected Nielsen endpoint differs')
        need(list(current) == normalization['endpoint'], 'bounded projected endpoint differs')
    for sweep in projected.get('complete_Whitehead_length_sweeps', []):
        need(sweep['input'] == normalization['endpoint'] and len(sweep['candidates']) == 8, 'wrong saved length sweep')
        expected = {('xy', 'y'), ('xY', 'y'), ('yx', 'y'), ('Yx', 'y'),
                    ('x', 'yx'), ('x', 'yX'), ('x', 'xy'), ('x', 'Xy')}
        need({tuple(c['images'][g] for g in 'xy') for c in sweep['candidates']} == expected, 'incomplete rank2 Nielsen map set')
        start = sum(map(len, sweep['input']))
        for candidate in sweep['candidates']:
            mapping = {i: encode(candidate['images'][g], XENC) for i, g in enumerate('xy', 1)}
            actual = tuple(sorted(canonical(apply(encode(w, XENC), mapping)) for w in sweep['input']))
            need(list(actual) == candidate['image_pair'] and sum(map(len, actual)) == candidate['total_length'] >= start, 'Whitehead length witness differs')
        need(start > sum(map(len, pair)), 'minimal-length Aut exclusion does not separate inputs')
    if 'stable_equivalence_witness' in row:
        witness = row['stable_equivalence_witness']
        need(witness['rank4_tuple'] == ['r', 's', *search['domain_basis'][:2]], 'rank4 bridge tuple differs')
        need(witness['kernel_basis'] == search['domain_basis'] and witness['inverse_basis'] == search['inverse_domain_basis'], 'bridge marking differs')
        projected_original = [reduce(tuple((abs(v) - 2) * (1 if v > 0 else -1) for v in w if abs(v) > 2)) for w in inverse_basis[:2]]
        need([decode(w, XENC) for w in projected_original] == pair == witness['P'], 'stable bridge inverse marking failed')
        need(witness['Q'] == projected['pair'] and witness['maximum_displayed_rank'] == 4 and witness['maximum_rank_using_one_helper_ambient_macro'] == 5, 'stable bridge endpoint/rank differs')
        need(witness['ordinary_equivalence_claimed'] is False, 'unsupported ordinary equivalence')
    return {'join_rejected': False, 'basis_verified': True, 'projected_verified': True}


def verify_continuation(record, projected_pair):
    need(record['input'] == projected_pair, 'continuation attached to wrong projection')
    order = {-2: 0, 2: 1, -1: 2, 1: 3}

    def canonical_word(value):
        value = reduce(value)
        while len(value) > 1 and value[0] == -value[-1]:
            value = value[1:-1]
        options = [w[i:] + w[:i] for w in (value, inverse(value)) for i in range(len(w))]
        return min(options, key=lambda w: tuple(order[v] for v in w), default=())

    def canonical_pair(pair):
        return tuple(sorted((canonical_word(w) for w in pair), key=lambda w: (len(w), tuple(order[v] for v in w))))

    current = canonical_pair([encode(w, XENC) for w in projected_pair])
    states = [[decode(w, XENC) for w in current]]
    result = record['result']
    for step in result['best_steps']:
        need(step['kind'] == 'substitution', 'continuation has an unsupported move type')
        target, sign, first_cut, second_cut = map(int, step['move'].split('_'))
        need(target in (1, 2) and sign in (-1, 1), 'invalid continuation move')
        i, j = target - 1, 2 - target
        donor = current[j] if sign == 1 else inverse(current[j])
        need(0 <= first_cut < max(1, len(current[i])) and 0 <= second_cut < max(1, len(donor)), 'continuation cut out of range')
        first = current[i][-first_cut:] + current[i][:-first_cut] if first_cut else current[i]
        second = donor[-second_cut:] + donor[:-second_cut] if second_cut else donor
        changed = list(current); changed[i] = reduce(first + second)
        current = canonical_pair(changed)
        states.append([decode(w, XENC) for w in current])
    need(states == result['best_states'], 'independent continuation replay differs')
    need(states[-1] == result['best_state'] == record['verified_endpoint'], 'continuation endpoint differs')
    minimum = min(sum(map(len, state)) for state in states)
    need(minimum == result['min_total_length_seen'] == 18, 'continuation minimum differs')
    need(record['previous_conservative_candidate_units'] == 984 and result['nodes_explored'] == record['heap_pop_budget'] == 16 and record['conservative_combined_units'] == 1000, 'continuation shared budget differs')
    return {'status': 'independently_replayed', 'ordinary_substitution_steps': len(result['best_steps']),
            'states': states, 'endpoint': states[-1], 'minimum_prefix_total_length': minimum,
            'original_input_length': record['original_u124_start_length'], 'new_original_length_gain': False,
            'combined_heterogeneous_work_units': 1000}


def main():
    started = time.process_time()
    path = HERE / 'two_complement_probe_report.json'; report = json.loads(path.read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    need(report['script_sha256'] == sha(HERE / 'two_complement_probe.py'), 'probe source hash differs')
    inventory_path = ROOT.parent / 'u124_inventory.json'; inventory = json.loads(inventory_path.read_text())
    need(report['source_inventory_sha256'] == sha(inventory_path), 'source inventory hash differs')
    need(report['panel_ids'] == [r['name'] for r in inventory['panel']['rows']], 'panel ID sequence differs')
    counters = Counter()
    for row, original in zip(report['rows'], inventory['panel']['rows']):
        need(row['name'] == original['name'] and row['input'] == [original['r1'], original['r2']], 'exact panel join differs')
        counters.update(verify_record(row))
    from two_complement_probe import probe
    controls = [(['x', 'y'], 'marked_kernel_basis_found'), (['xy', 'y'], 'marked_kernel_basis_found'),
                (['xyx', 'xy'], 'marked_kernel_basis_found'), (['xx', 'yy'], 'join_not_full')]
    for pair, expected in controls:
        record = probe(pair, known_trivial=expected == 'marked_kernel_basis_found')
        need(record['status'] == expected, 'planted control outcome differs')
        verify_record(record)
    for tiny in (0, 1, 2, 3, 4, 5, 7, 13):
        need(probe(['x', 'y'], limit=tiny)['image_evaluations'] <= tiny, 'tiny budget overflow')
    positive = next(r for r in report['rows'] if r['projected'])
    corruptions = []
    bad = copy.deepcopy(positive); bad['search']['domain_basis'][0] += 't'; corruptions.append(bad)
    bad = copy.deepcopy(positive); bad['search']['inverse_domain_basis'][0] += 't'; corruptions.append(bad)
    bad = copy.deepcopy(positive); bad['projected']['pair'][0] += 'x'; corruptions.append(bad)
    for bad in corruptions:
        try:
            verify_record(bad)
        except ValueError:
            continue
        raise AssertionError('corrupted basis certificate accepted')
    continuation_path = HERE / 'two_complement_search_continuation.json'
    if continuation_path.exists():
        continuation = json.loads(continuation_path.read_text())
        for name, expected in continuation['source_hashes'].items():
            need(sha(Path(name)) == expected, 'continuation source changed')
        replayed = verify_continuation(continuation, positive['projected']['pair'])
        report['ordinary_continuation_audit'] = {'source_report_sha256': sha(continuation_path), **replayed}
    report['independent_checks'] = {'status': 'pass', 'checker_sha256': sha(Path(__file__)),
                                   'saved_rows_replayed': len(report['rows']), **dict(counters),
                                   'planted_controls': len(controls), 'tiny_budget_controls': 8,
                                   'corruptions_rejected': len(corruptions), 'cpu_seconds': time.process_time() - started}
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['independent_checks'], indent=2))


if __name__ == '__main__':
    main()
