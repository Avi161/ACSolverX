"""Bounded marked Nielsen feasibility for the fixed complements x and y^2."""
from __future__ import annotations

from collections import Counter
import heapq
import itertools
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from research.theory_patterns_20260912.rankn_complement import graph, rose

DOMAIN = 'rstu'


def inv(word):
    return word.swapcase()[::-1]


def red(word):
    stack = []
    for c in word:
        if stack and stack[-1] == c.swapcase():
            stack.pop()
        else:
            stack.append(c)
    return ''.join(stack)


def substitute(word, mapping):
    return red(''.join(mapping[c] if c in mapping else inv(mapping[c.swapcase()]) for c in word))


def row_move(words, move):
    words = list(words)
    if move['op'] == 'invert':
        words[move['target']] = inv(words[move['target']])
    elif move['op'] == 'permute':
        words = [words[i] for i in move['order']]
    elif move['op'] == 'multiply':
        i, j = move['target'], move['donor']
        donor = words[j] if move['sign'] == 1 else inv(words[j])
        words[i] = red(words[i] + donor if move['side'] == 'right' else donor + words[i])
    else:
        raise ValueError('unknown Nielsen row operation')
    return tuple(words)


def inverse_move(move):
    move = dict(move)
    if move['op'] == 'multiply':
        move['sign'] *= -1
    elif move['op'] == 'permute':
        move['order'] = [move['order'].index(i) for i in range(len(move['order']))]
    return move


class Budget:
    def __init__(self, limit):
        if type(limit) is not int or not 0 <= limit <= 1000:
            raise ValueError('image limit must be an integer in 0..1000')
        self.limit, self.counts = limit, Counter()

    @property
    def used(self):
        return sum(self.counts.values())

    def charge(self, kind, count=1):
        if self.used + count > self.limit:
            return False
        self.counts[kind] += count
        return True


def normalize(images, basis, path, budget, changed=None):
    images, basis, path = list(images), list(basis), list(path)
    for i in range(4) if changed is None else (changed,):
        if not budget.charge('row_inverse_images'):
            return None
        opposite = inv(images[i])
        if opposite < images[i]:
            move = {'op': 'invert', 'target': i}
            images[i], basis[i] = opposite, inv(basis[i])
            path.append(move)
    order = sorted(range(4), key=lambda i: (len(images[i]), images[i], i))
    if order != list(range(4)):
        move = {'op': 'permute', 'order': order}
        images, basis = [images[i] for i in order], [basis[i] for i in order]
        path.append(move)
    return tuple(images), tuple(basis), path


def goal(images):
    return len([w for w in images if not w]) == 2 and sorted(w.lower() for w in images if w) == ['x', 'y']


def verify_basis(initial, images, basis, path):
    replay_images, replay_basis = tuple(initial), tuple(DOMAIN)
    for move in path:
        replay_images = row_move(replay_images, move)
        replay_basis = row_move(replay_basis, move)
    if replay_images != tuple(images) or replay_basis != tuple(basis):
        raise ValueError('marked row path does not replay')
    backwards = tuple(DOMAIN)
    for move in reversed(path):
        backwards = row_move(backwards, inverse_move(move))
    forward_map, backward_map = dict(zip(DOMAIN, basis)), dict(zip(DOMAIN, backwards))
    for g in DOMAIN:
        if substitute(forward_map[g], backward_map) != g or substitute(backward_map[g], forward_map) != g:
            raise ValueError('marked domain basis inverse failed')
    if [substitute(w, dict(zip(DOMAIN, initial))) for w in basis] != list(images):
        raise ValueError('basis image marking failed')
    return {'domain_basis': list(basis), 'inverse_domain_basis': list(backwards),
            'images': list(images), 'nielsen_row_moves': path, 'verified': True}


def nielsen(initial, budget, image_cap=128, domain_cap=2048):
    state = normalize(initial, tuple(DOMAIN), [], budget)
    if state is None:
        return {'status': 'image_budget_before_initial_normalization', 'best_image_length': sum(map(len, initial))}
    images, basis, path = state
    heap = [(sum(map(len, images)), images, 0, basis, path)]
    seen = {images}
    serial, popped, generated, best, guards = 0, 0, 0, state, Counter()
    while heap:
        total, images, _, basis, path = heapq.heappop(heap)
        popped += 1
        if total < sum(map(len, best[0])):
            best = images, basis, path
        if goal(images):
            images, basis, path = list(images), list(basis), list(path)
            for i, image in enumerate(images):
                if image in ('X', 'Y'):
                    if not budget.charge('terminal_marking_inverse_images'):
                        return {'status': 'image_budget_before_terminal_marking', **verify_basis(initial, images, basis, path)}
                    move = {'op': 'invert', 'target': i}
                    images, basis = row_move(images, move), row_move(basis, move)
                    path.append(move)
            order = sorted(range(4), key=lambda i: (bool(images[i]), images[i]))
            if order != list(range(4)):
                move = {'op': 'permute', 'order': order}
                images, basis = row_move(images, move), row_move(basis, move)
                path.append(move)
            return {'status': 'marked_kernel_basis_found', **verify_basis(initial, images, basis, path),
                    'popped_states': popped, 'generated_candidates': generated, 'seen_image_tuples': len(seen),
                    'guards': dict(guards), 'best_image_length': 2}
        for i, j, sign, side in itertools.product(range(4), range(4), (1, -1), ('left', 'right')):
            if i == j or not images[j] or not images[i]:
                continue
            if budget.limit - budget.used < 2:
                return {'status': 'image_budget', **verify_basis(initial, *best),
                        'popped_states': popped, 'generated_candidates': generated, 'seen_image_tuples': len(seen),
                        'guards': dict(guards), 'best_image_length': sum(map(len, best[0]))}
            budget.charge('multiplication_candidate_images')
            move = {'op': 'multiply', 'target': i, 'donor': j, 'sign': sign, 'side': side}
            child_images = row_move(images, move)
            generated += 1
            if len(child_images[i]) > image_cap:
                guards['image_cap'] += 1
                continue
            child_basis = row_move(basis, move)
            if max(map(len, child_basis)) > domain_cap:
                guards['domain_basis_cap'] += 1
                continue
            child = normalize(child_images, child_basis, path + [move], budget, changed=i)
            if child is None:
                raise AssertionError('reserved normalization image missing')
            ci, cb, cp = child
            if sum(map(len, ci)) < sum(map(len, best[0])):
                best = child
            if ci in seen:
                continue
            seen.add(ci); serial += 1
            heapq.heappush(heap, (sum(map(len, ci)), ci, serial, cb, cp))
    return {'status': 'finite_frontier_exhausted', **verify_basis(initial, *best),
            'popped_states': popped, 'generated_candidates': generated, 'seen_image_tuples': len(seen),
            'guards': dict(guards), 'best_image_length': sum(map(len, best[0]))}


def canon(word):
    word = red(word)
    while len(word) > 1 and word[0] == word[-1].swapcase():
        word = word[1:-1]
    return min((w[i:] + w[:i] for w in (word, inv(word)) for i in range(len(w))), default='')


def pair_key(pair):
    return tuple(sorted(canon(w) for w in pair))


def determinant(pair):
    vectors = [(w.count('x') - w.count('X'), w.count('y') - w.count('Y')) for w in pair]
    return vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]


def projected_checks(pair, projected, budget):
    if abs(determinant(projected)) != 1:
        raise ValueError('projected kernel pair is not unimodular')
    result = {'pair': projected, 'total_length': sum(map(len, projected)), 'determinant': determinant(projected),
              'exact_pair_match': projected == list(pair), 'cyclic_inverse_permutation_match': pair_key(projected) == pair_key(pair),
              'aut_comparison': 'unknown_outside_checked_signed_permutations', 'aut_witness': None,
              'terminal_macro': None, 'solve_implication_verified': False,
              'length_is_not_an_admissible_stable_minimum': True}
    for a, b in itertools.product('xXyY', repeat=2):
        if a.lower() == b.lower():
            continue
        if not budget.charge('signed_permutation_comparison_word_images', 2):
            break
        mapping = {'x': a, 'y': b}
        image = [substitute(w, mapping) for w in projected]
        if pair_key(image) == pair_key(pair):
            result['aut_comparison'], result['aut_witness'] = 'verified_same_Aut_orbit', mapping
            break
    for i in (0, 1):
        if len(canon(projected[i])) == 1:
            # A cyclic conjugate of a basis letter is primitive; unimodularity
            # forces the companion to exponent +/-1 after this row is cleared.
            result['terminal_macro'] = {'kind': 'literal_cyclic_generator_row', 'row': i,
                                        'generator': canon(projected[i]), 'theorem': 'ordinary primitive-row clearing'}
            result['solve_implication_verified'] = True
            break
    return result


def continue_projected(original, result, budget):
    maps = (('xy', 'y'), ('xY', 'y'), ('yx', 'y'), ('Yx', 'y'),
            ('x', 'yx'), ('x', 'yX'), ('x', 'xy'), ('x', 'Xy'))
    inverse_indices = (1, 0, 3, 2, 5, 4, 7, 6)
    current, steps, sweeps = pair_key(result['pair']), [], []
    complete = False
    while budget.limit - budget.used >= 32 and len(steps) < 3:
        candidates = []
        for index, images in enumerate(maps):
            if not budget.charge('projected_Nielsen_word_images', 2):
                raise AssertionError('reserved projected images missing')
            transformed = pair_key(substitute(w, dict(zip('xy', images))) for w in current)
            candidates.append((sum(map(len, transformed)), transformed, index))
        total, endpoint, index = min(candidates)
        if total >= sum(map(len, current)):
            complete = True
            sweeps.append({'input': list(current), 'candidates': [
                {'images': dict(zip('xy', maps[index])), 'image_pair': list(image), 'total_length': length}
                for length, image, index in candidates]})
            break
        steps.append({'before': list(current), 'after': list(endpoint), 'images': dict(zip('xy', maps[index])),
                      'inverse_images': dict(zip('xy', maps[inverse_indices[index]]))})
        current = endpoint
    result['bounded_projected_Nielsen'] = {'start': list(pair_key(result['pair'])), 'endpoint': list(current),
                                           'total_length': sum(map(len, current)), 'steps': steps,
                                           'strict_descent_exhausted': complete}
    result['complete_Whitehead_length_sweeps'] = sweeps
    for a, b in itertools.product('xXyY', repeat=2):
        if a.lower() == b.lower():
            continue
        if not budget.charge('post_Nielsen_signed_permutation_word_images', 2):
            break
        mapping = {'x': a, 'y': b}
        image = [substitute(w, mapping) for w in current]
        if pair_key(image) == pair_key(original):
            result['aut_comparison'] = 'verified_same_Aut_orbit_after_bounded_Nielsen'
            result['aut_witness'] = {'Nielsen_steps': steps, 'final_signed_permutation': mapping}
            break
    for i in (0, 1):
        if len(current[i]) == 1:
            result['terminal_macro'] = {'kind': 'literal_cyclic_generator_row_after_bounded_Nielsen',
                                        'row': i, 'generator': current[i]}
            result['solve_implication_verified'] = True
            break
    if complete and sum(map(len, current)) > sum(map(len, original)):
        result['aut_comparison'] = 'verified_distinct_Aut_orbits_by_rank2_Whitehead_minimum'
        result['aut_minimum_length'] = sum(map(len, current))


def stable_equivalence_witness(pair, search):
    basis, backwards = search['domain_basis'], search['inverse_domain_basis']
    if search['images'] != ['', '', 'x', 'y']:
        raise ValueError('marked kernel basis required')
    project = lambda w: red(''.join(c for c in w if c.lower() in 'tu')).translate(str.maketrans('tTuU', 'xXyY'))
    if [project(w) for w in backwards[:2]] != list(pair):
        raise ValueError('inverse marking does not recover original pair')
    return {'rank4_tuple': ['r', 's', *basis[:2]], 'kernel_basis': basis, 'inverse_basis': backwards,
            'Q': [project(w) for w in basis[:2]], 'P': list(pair),
            'theta_old_generator_images_in_coordinates_R_S_x_y': [w.translate(str.maketrans('rRsStTuU', 'rRsSxXyY')) for w in backwards],
            'theta_r_s_after_killing_kernel_coordinates': [project(w) for w in backwards[:2]],
            'projected_pair_to_rank4': 'stabilize unit r,s; restore-donor-correct projected Wi to full Wi',
            'rank4_to_original': 'change marked ambient basis; unit kernel coordinates clear remaining rows and destabilize',
            'maximum_displayed_rank': 4, 'maximum_rank_using_one_helper_ambient_macro': 5,
            'kind': 'known_trivial_group_theorem_backed_stable_AC_equivalence', 'ordinary_equivalence_claimed': False,
            'projected_target_shorter_than_original': sum(len(project(w)) for w in basis[:2]) < sum(map(len, pair))}


def probe(pair, limit=1000, known_trivial=False):
    if len(pair) != 2 or any(set(w) - set('xXyY') or red(w) != w for w in pair):
        raise ValueError('two reduced old relators required')
    initial = [*pair, 'x', 'yy']
    budget = Budget(limit)
    folded = graph(initial, 'xy')
    result = {'input': list(pair), 'input_length': sum(map(len, pair)), 'complements': ['x', 'yy'],
              'initial_image_tuple': initial, 'full_fold_graph': folded, 'join_is_full': folded == rose('xy'),
              'image_limit': limit, 'projected': None}
    if not result['join_is_full']:
        result['status'] = 'join_not_full'
    else:
        search = nielsen(initial, budget)
        result['search'] = search
        result['status'] = search['status']
        if search['status'] == 'marked_kernel_basis_found':
            if not budget.charge('kernel_projection_word_images', 2):
                result['status'] = 'image_budget_before_projection'
            else:
                kernel = search['domain_basis'][:2]
                projected = [red(''.join(c for c in w if c.lower() in 'tu')).translate(str.maketrans('tTuU', 'xXyY')) for w in kernel]
                result['projected'] = projected_checks(pair, projected, budget)
                if not result['projected']['solve_implication_verified']:
                    continue_projected(pair, result['projected'], budget)
                if known_trivial:
                    result['stable_equivalence_witness'] = stable_equivalence_witness(pair, search)
                    result['projected']['stable_equivalence_verified'] = True
                    result['projected']['length_is_not_an_admissible_stable_minimum'] = False
    result['image_evaluations'] = budget.used
    result['image_evaluation_counts'] = dict(budget.counts)
    return result


def main():
    import hashlib
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    path = ROOT.parent / 'u124_inventory.json'
    inventory = json.loads(path.read_text())
    panel = inventory['panel']['rows']
    if len(panel) != 20 or len({r['name'] for r in panel}) != 20:
        raise ValueError('exact20 panel invalid')
    cpu, wall = time.process_time(), time.perf_counter()
    rows = []
    for row in panel:
        result = probe([row['r1'], row['r2']], known_trivial=True)
        result['name'] = row['name']; rows.append(result)
        time.sleep(.05)
    report = {'status': 'bounded_two_complement_feasibility_complete', 'rows': rows,
              'source_inventory_sha256': sha(path), 'script_sha256': sha(Path(__file__)),
              'source_graph_script_sha256': sha(HERE / 'rankn_complement.py'),
              'panel_ids': [r['name'] for r in rows], 'counts': dict(Counter(r['status'] for r in rows)),
              'total_image_evaluations': sum(r['image_evaluations'] for r in rows),
              'maximum_image_evaluations': max(r['image_evaluations'] for r in rows),
              'projected_pair_ids': [r['name'] for r in rows if r['projected']],
              'terminal_candidate_ids': [r['name'] for r in rows if r['projected'] and r['projected']['solve_implication_verified']],
              'new_solve_ids': [], 'certified_length_gain_ids': [],
              'cpu_seconds': time.process_time() - cpu, 'wall_seconds_including_cooling': time.perf_counter() - wall,
              'method': 'Fixed complements x,y^2; full fold first; total noncyclic-image-length heap of marked Nielsen row moves. Image tuples deduplicated modulo recorded row inversions/permutations. No ambient or cyclic conjugation during Nielsen search. Empty donors/targets skipped as a bounded heuristic.',
              'budget': 'At most1000 evaluated candidate word images per original input including candidate multiplication, inversion normalization, terminal signs, kernel projections and signed-permutation comparisons. Graph folds and symbolic domain-certificate/inverse verification are outside the candidate-word-image unit. No y^3 followup.',
              'scope': 'Known-trivial inputs with a marked kernel basis have a theorem-backed stable equivalence through a rank4 tuple, potentially rank5 internally. No ordinary equivalence follows. A complete rank2 Whitehead minimum may distinguish the projected Aut orbit; otherwise nonmatching signed-permutation comparisons leave it unknown. No solve is admitted without an independent endpoint certificate.'}
    (HERE / 'two_complement_probe_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
