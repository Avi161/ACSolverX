"""Independent certificate checks for the continuation from total length2180."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'rank_unbounded_20260912'
BASELINE_FILE = PRIOR / 'all124.json'
BASELINE_SHA256 = 'fba32693f0f1da10b8a9b8bf35ed6cd0f354a6d42d3af73f3aabf86142680336'
AUDITOR_SHA256 = '6c95d91e34c4e710350575202ef343477d66eb56de32860e46f105ba8ac20c8f'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


require(sha(PRIOR / 'audit.py') == AUDITOR_SHA256, 'the frozen independent auditor changed')
spec = importlib.util.spec_from_file_location('u124_prior_independent_audit', PRIOR / 'audit.py')
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)
word = independent.word
words = independent.words
free = independent.free
invert = independent.invert
normalized = independent.normalized
size = independent.size
image = independent.image


def parse_saved_strings(strings):
    alphabet = 'xyzuvw'
    mapping = {letter: i + 1 for i, letter in enumerate(alphabet)}
    require(all(c.lower() in mapping for w in strings for c in w), 'unknown saved alphabet')
    return tuple(tuple(mapping[c.lower()] * (1 if c.islower() else -1) for c in w) for w in strings)


def load_baseline():
    require(sha(BASELINE_FILE) == BASELINE_SHA256, 'current2180 baseline changed')
    report = json.loads(BASELINE_FILE.read_text())
    prior_table = json.loads((HERE.parent / 'theory_patterns_20260912/u124_final_table.json').read_text())
    previous = {r['name']: r for r in prior_table['rows']}
    baseline = {}
    for index, row in enumerate(report['rows']):
        pointer = independent.resolve_pointer(row['witness_pointer'])
        if 'endpoint' in pointer:
            current = words(pointer['endpoint'])
        else:
            require(pointer['name'] == row['name'], 'baseline pointer selects another ID')
            current = parse_saved_strings(pointer['best_words'])
        require(independent.rendered(current) == row['best_words'], 'baseline display differs from exact endpoint')
        require(size(current) == row['best_any_rank_length'] and len(current) == row['best_rank'], 'baseline endpoint metrics differ')
        independent.check_tuple(current)
        prior = previous[row['name']]
        require(row['name'] not in baseline, 'baseline duplicate ID')
        baseline[row['name']] = {
            'name': row['name'], 'words': current, 'length': size(current), 'rank': len(current),
            'witness_pointer': row['witness_pointer'], 'baseline_sha256': BASELINE_SHA256,
            'sources': {'current_best': current,
                        'saved_rank2': parse_saved_strings(prior['starting_words']),
                        'previous_best': parse_saved_strings(prior['best_words'])},
            'source_pointers': {'current_best': '../rank_unbounded_20260912/all124.json#/rows/' + str(index),
                                'saved_rank2': prior['best_rank2_source_certificate_pointer'],
                                'previous_best': prior['source_certificate_pointer']},
            'known_triviality_basis': 'Pinned Miller–Schupp source and previously verified stable/AC witness lineage; not inferred from determinant.',
        }
    require(len(baseline) == 124 and sum(r['length'] for r in baseline.values()) == 2180, 'baseline denominator or total differs')
    return baseline


OLD_KINDS = {'defining_compression', 'ambient_whitehead', 'lemma11_removal',
             'ordinary_ac_substitution', 'relator_normalization'}
STABLE_KINDS = {'defining_compression', 'ambient_whitehead', 'lemma11_removal',
                'ambient_automorphism', 'generator_relabeling', 'defining_template_compression'}


def basis_images(raw):
    require(isinstance(raw, dict), 'basis images must be a dictionary')
    mapping = {}
    for key, value in raw.items():
        require(type(key) is int or type(key) is str and key.isdecimal() and str(int(key)) == key, 'invalid basis-map key')
        generator = int(key)
        require(generator > 0 and generator not in mapping, 'basis-map duplicate/nonpositive key')
        mapping[generator] = word(value)
    return mapping


def ambient_event(event):
    before, after = words(event['before']), words(event['after'])
    forward = basis_images(event['images'])
    backward = basis_images(event['inverse_images'])
    old_basis = {abs(x) for w in before for x in w}
    new_basis = {abs(x) for w in after for x in w}
    require(set(forward) == old_basis and set(backward) == new_basis, 'ambient map omits basis generator')
    require(len(old_basis) == len(new_basis) == len(before) == len(after), 'ambient map changes balanced rank')
    require(all(abs(x) in new_basis for w in forward.values() for x in w), 'forward image uses foreign generator')
    require(all(abs(x) in old_basis for w in backward.values() for x in w), 'inverse image uses foreign generator')
    for g in old_basis:
        require(image(forward[g], backward) == (g,), 'ambient left inverse fails')
        require(image(invert(forward[g]), backward) == (-g,), 'ambient negative inverse fails')
    for g in new_basis:
        require(image(backward[g], forward) == (g,), 'ambient right inverse fails')
    if event['kind'] == 'generator_relabeling':
        require(all(len(w) == 1 for w in (*forward.values(), *backward.values())), 'relabeling is not a signed permutation')
    raw = tuple(image(w, forward) for w in before)
    if 'raw_after' in event:
        require(words(event['raw_after']) == raw, 'ambient raw tuple differs')
    require(normalized(raw) == after, 'ambient transformation omits or changes a relator')
    if 'normalization' in event:
        independent.normalization(raw, event['normalization'], after)
    return after


def relative_dictionary_metadata(event):
    before, target = words(event['before']), event['target']
    basis = {abs(x) for w in before for x in w}
    images = basis_images(event['virtual_token_images'])
    donor_tokens = {int(k): v for k, v in event['virtual_donor_tokens'].items()}
    require(all(g > 0 and g not in basis and type(i) is int and i != target and 0 <= i < len(before) for g, i in donor_tokens.items()), 'virtual donor token invalid')
    require(set(donor_tokens.values()) == set(range(len(before))) - {target} and len(donor_tokens) == len(before) - 1, 'virtual dictionary omits or duplicates retained donors')
    require(set(images) == basis | set(donor_tokens), 'virtual dictionary uses foreign tokens')
    require(all(images[g] == (g,) for g in basis) and all(images[g] == before[i] for g, i in donor_tokens.items()), 'virtual token image differs from retained donor')
    template = word(event['relative_template'])
    require(all(abs(x) in images for x in template) and image(template, images) == before[target], 'relative template exact expansion differs')
    expected = []
    for j, token in enumerate(template):
        if abs(token) in donor_tokens:
            expected.append((donor_tokens[abs(token)], -1 if token > 0 else 1, image(template[j + 1:], images)))
    actual = [(factor['donor_index'], factor['sign'], word(factor['conjugator'])) for factor in event['factors']]
    require(actual == expected, 'relative donor deletion order, sign or suffix differs')
    require(free(tuple(x for x in template if abs(x) in basis)) == word(event['raw_target_after']), 'relative stripped target differs')
    require(event['relative_objective'] == 'old_letter_token_count_then_total_token_count', 'relative objective differs')
    require(tuple(event['relative_template_cost']) == (sum(abs(x) in basis for x in template), len(template)), 'relative objective cost differs')
    complete, saturation = event['complete_fixed_dictionary_geodesic'], event['saturation_complete']
    require(type(complete) is bool and type(saturation) is bool and (not complete or saturation), 'relative completion flag invalid')
    counts = event['work_counts']
    require(all(type(n) is int and n >= 0 for n in counts.values()) and sum(counts.values()) == event['charged_units'], 'relative work sum differs')


def normal_product_event(event):
    before = words(event['before'])
    target = event['target']
    require(type(target) is int and 0 <= target < len(before), 'invalid normal-product target')
    basis = {abs(x) for w in before for x in w}
    product_word = before[target]
    for factor in event['factors']:
        donor, sign = factor['donor_index'], factor['sign']
        require(type(donor) is int and 0 <= donor < len(before) and donor != target, 'normal-product donor must be another relator')
        require(type(sign) is int and sign in (-1, 1), 'invalid normal-product sign')
        conjugator = word(factor['conjugator'])
        require(all(abs(x) in basis for x in conjugator), 'normal-product conjugator uses foreign generator')
        signed = before[donor] if sign == 1 else invert(before[donor])
        product_word += invert(conjugator) + signed + conjugator
    replacement = word(event['raw_target_after'])
    require(free(product_word) == replacement and free(replacement) == replacement, 'normal-product exact identity fails')
    raw = before[:target] + (replacement,) + before[target + 1:]
    if 'raw_after' in event:
        require(words(event['raw_after']) == raw, 'normal-product raw tuple differs')
    after = words(event['after'])
    require(len(after) == len(before) and normalized(raw) == after, 'normal-product omitted or duplicated old relator')
    if 'normalization' in event:
        independent.normalization(raw, event['normalization'], after)
    if event.get('macro') == 'retained_donor_relative_dictionary':
        relative_dictionary_metadata(event)
    if event.get('macro') == 'retained_donor_commutator':
        sign, c = event['commutator_sign'], word(event['commutator_conjugator'])
        require(type(sign) is int and sign in (-1, 1), 'commutator sign invalid')
        require(len(event['factors']) == 2, 'commutator factor count differs')
        left, right = event['factors']
        require(left['donor_index'] == right['donor_index'] and left['sign'] == -sign and right['sign'] == sign and word(left['conjugator']) == () and word(right['conjugator']) == c, 'commutator factor metadata differs')
        require(all(before[target].count(g) - before[target].count(-g) == replacement.count(g) - replacement.count(-g) for g in basis), 'commutator changed abelianization')
    return after


def sparse_defining_event(event):
    before, defining = words(event['before']), word(event['defining'])
    basis = {abs(x) for w in before for x in w}
    helper = event['helper']
    require(type(helper) is int and helper == max(basis, default=0) + 1, 'literal helper is not fresh')
    require(defining and free(defining) == defining and all(abs(x) in basis for x in defining), 'literal definition is not reduced over the old basis')
    templates, cuts = words(event['templates']), event['cuts']
    require(len(templates) == len(cuts) == len(before), 'literal definition omits an old row')
    mapping = {g: (g,) for g in basis}
    mapping[helper] = defining
    selected = 0
    for old, template, cut in zip(before, templates, cuts):
        require(type(cut) is int and 0 <= cut < max(1, len(old)), 'literal definition cut invalid')
        require(all(abs(x) in mapping for x in template), 'literal template uses an absent generator')
        require(image(template, mapping, reduce=False) == old[cut:] + old[:cut], 'literal template expansion differs from rotation')
        require(free(template) == template, 'literal template is unreduced')
        selected += sum(abs(x) == helper for x in template)
    raw = ((-helper,) + defining,) + templates
    require(words(event['raw_after']) == raw and len(raw) == len(before) + 1, 'literal definition omits or duplicates a row')
    expected_length = size(before) + len(defining) + 1 - selected * (len(defining) - 1)
    require(selected == event['uses'] and size(raw) == expected_length == event['literal_length'], 'literal definition use or length count differs')
    after = words(event['after'])
    require(after == normalized(raw) and size(after) == event['final_length'], 'literal definition endpoint differs')
    if 'normalization' in event:
        independent.normalization(raw, event['normalization'], after)
    return after


def root_template_metadata(event):
    witness = event['root_template_witness']
    before = words(event['before'])
    index = witness['input_index']
    require(type(index) is int and 0 <= index < len(before), 'root target index invalid')
    basis = {abs(x) for w in before for x in w}
    u, v, root = (word(witness[key]) for key in ('context_u', 'context_v', 'root'))
    require(root and all(free(w) == w and all(abs(x) in basis for x in w) for w in (u, v, root)), 'root/context is not reduced over old generators')
    power = witness['power']
    require(type(power) is int and power >= 2, 'root power invalid')
    require(word(witness['before']) == before[index], 'root witness input differs')
    oriented = independent.conjugation(before[index], witness['sign'], word(witness['conjugator']))
    require(oriented == word(witness['oriented']), 'root signed orientation differs')
    test = free(oriented + invert(v) + u)
    require(word(witness['test_word']) == test == free(root * power), 'extracted root power identity fails')
    raw_definition = free(root + invert(u))
    require(word(witness['raw_defining_word']) == raw_definition, 'root raw definition differs')
    definition = min(raw_definition, invert(raw_definition))
    require(word(witness['defining_word']) == definition and words(event['defining_words']) == (definition,), 'root definition/inverse choice differs')
    helper, sign = witness['helper'], witness['helper_sign']
    require(type(helper) is int and tuple(event['helpers']) == (helper,), 'root helper differs')
    require(type(sign) is int and sign in (-1, 1), 'root helper sign invalid')
    require((definition if sign == 1 else invert(definition)) == raw_definition, 'root helper sign chooses wrong definition')
    template = ((sign * helper,) + u) * (power - 1) + (sign * helper,) + v
    require(word(witness['template']) == template, 'root repeated-helper template differs')
    for key in ('before', 'sign', 'conjugator', 'oriented', 'template'):
        require(event['rows'][index][key] == witness[key], 'forced root row differs from witness: ' + key)
    canonical = independent.representative(template)
    axes = sorted(g for g in basis if sum(abs(x) == g for x in canonical) == 1)
    require(witness['isolatable_old_generators'] == axes, 'root isolated-generator metadata differs')
    require(event['work_counts']['forced_root_template_expansions'] == 1, 'root forced-template work missing')


def cyclic_core_frame(value):
    value = free(value)
    i, j = 0, len(value)
    while j - i > 1 and value[i] == -value[j - 1]:
        i += 1
        j -= 1
    return value[i:j], value[:i]


def conjugacy_template_metadata(event):
    witness = event['conjugacy_template_witness']
    before = words(event['before'])
    index = witness['input_index']
    require(type(index) is int and 0 <= index < len(before), 'conjugacy target index invalid')
    require(word(witness['before']) == before[index], 'conjugacy target input differs')
    u, v = word(witness['context_u']), word(witness['context_v'])
    basis = {abs(x) for w in before for x in w}
    require(u and all(free(w) == w and all(abs(x) in basis for x in w) for w in (u, v)), 'conjugacy contexts invalid')
    oriented = independent.conjugation(before[index], witness['sign'], word(witness['conjugator']))
    require(oriented == word(witness['oriented']), 'conjugacy orientation differs')
    target = free(oriented + invert(v))
    coset = witness['coset']
    require(word(coset['source']) == u and word(coset['target']) == target, 'conjugacy equation differs')
    source_core, source_frame = cyclic_core_frame(u)
    target_core, target_frame = cyclic_core_frame(target)
    require(word(coset['source_core']) == source_core and word(coset['source_prefix']) == source_frame, 'conjugacy source cyclic frame differs')
    require(word(coset['target_core']) == target_core and word(coset['target_prefix']) == target_frame, 'conjugacy target cyclic frame differs')
    cut = coset['rotation_cut']
    require(type(cut) is int and 0 <= cut < len(source_core), 'conjugacy rotation cut invalid')
    require(source_core[cut:] + source_core[:cut] == target_core, 'conjugacy cyclic rotation differs')
    base = free(target_frame + invert(source_core[:cut]) + invert(source_frame))
    require(word(coset['base_conjugator']) == base and free(base + u + invert(base)) == target, 'conjugacy base conjugator differs')
    root, exponent = word(coset['centralizer_root']), coset['centralizer_exponent']
    require(root and type(exponent) is int and exponent > 0 and free(root * exponent) == u, 'conjugacy centralizer power differs')
    core, _ = cyclic_core_frame(root)
    require(all(len(core) % k or core[:len(core) // k] * k != core for k in range(2, len(core) + 1)), 'conjugacy centralizer root is a proper power')
    shift = witness['centralizer_shift']
    require(type(shift) is int, 'conjugacy centralizer shift invalid')
    raw_definition = free(base + (root if shift >= 0 else invert(root)) * abs(shift))
    require(word(witness['raw_defining_word']) == raw_definition, 'conjugacy raw definition differs')
    definition = min(raw_definition, invert(raw_definition))
    require(word(witness['defining_word']) == definition and words(event['defining_words']) == (definition,), 'conjugacy definition/inverse choice differs')
    helper, sign = witness['helper'], witness['helper_sign']
    require(type(helper) is int and tuple(event['helpers']) == (helper,), 'conjugacy helper differs')
    require(type(sign) is int and sign in (-1, 1) and (definition if sign == 1 else invert(definition)) == raw_definition, 'conjugacy helper sign differs')
    template = (sign * helper,) + u + (-sign * helper,) + v
    require(word(witness['template']) == template, 'conjugacy repeated-helper template differs')
    for key in ('before', 'sign', 'conjugator', 'oriented', 'template'):
        require(event['rows'][index][key] == witness[key], 'forced conjugacy row differs from witness: ' + key)
    canonical = independent.representative(template)
    require(witness['isolatable_old_generators'] == sorted(g for g in basis if sum(abs(x) == g for x in canonical) == 1), 'conjugacy isolated-generator metadata differs')
    require(event['work_counts']['forced_conjugacy_template_expansions'] == 1, 'conjugacy forced-template work missing')


def schreier_stage_metadata(event):
    before = words(event['before'])
    basis = {abs(x) for w in before for x in w}
    axis, index, stage, stages = (event[k] for k in ('schreier_axis', 'schreier_index', 'schreier_stage', 'schreier_stages'))
    require(type(axis) is int and axis in basis and type(index) is int and index >= 2, 'Schreier axis/index invalid')
    require(type(stage) is int and type(stages) is int and 1 <= stage <= stages, 'Schreier stage numbering invalid')
    require(len(event['helpers']) == 1 and event['helpers'][0] == max(basis) + 1, 'Schreier stage helper is not sequentially fresh')
    for row in event['rows']:
        label = row['schreier_row_label']
        require(len(label) == 2 and label[0] in ('original', 'definition') and type(label[1]) is int, 'Schreier row label invalid')
        if label[0] == 'definition':
            require(label[1] in basis and row['template'] == row['before'] and row['oriented'] == row['before'] and row['sign'] == 1 and word(row['conjugator']) == (), 'Schreier stage changes a retained earlier definition')
    counts = event['work_counts']
    if stage != 1:
        require(set(counts) == {'definitions', 'template_expansions'}, 'Schreier later stage repeats planning work')
        return
    require(stages == 1 + (index - 1) * (len(before) - 1), 'Schreier helper/rank formula differs')
    require([tuple(row['schreier_row_label']) for row in event['rows']] == [('original', i) for i in range(len(before))], 'Schreier first-stage original labels differ')
    ordered = event['schreier_triangular_definitions']
    require(len(ordered) == stages, 'Schreier triangular inventory incomplete')
    expected, cosets = [], {(0, g): g for g in basis if g != axis}
    fresh = max(basis) + 1
    require(len(word(ordered[0][1])) == index, 'Schreier power definition length differs')
    power_helper = fresh
    expected.append((fresh, (axis,) * index))
    for residue in range(1, index):
        for g in sorted(basis - {axis}):
            fresh += 1
            expected.append((fresh, (axis, cosets[residue - 1, g], -axis)))
            cosets[residue, g] = fresh
    require([(g, word(w)) for g, w in ordered] == expected, 'Schreier triangular definitions differ')
    mapping = {g: (g,) for g in basis}
    for g, definition in expected:
        mapping[g] = image(definition, mapping)
    require(basis_images(event['schreier_full_images']) == mapping, 'Schreier full helper images differ')
    rewrites = event['schreier_rewrites']
    require(len(rewrites) == len(before), 'Schreier rewrite omits an original row')
    for old, rewrite in zip(before, rewrites):
        require(word(rewrite['input_before']) == old and rewrite['axis'] == axis and rewrite['index'] == index, 'Schreier rewrite source differs')
        oriented = independent.conjugation(old, rewrite['orientation_sign'], word(rewrite['orientation_conjugator']))
        require(word(rewrite['before']) == oriented, 'Schreier original orientation differs')
        require(len(rewrite['steps']) == len(oriented), 'Schreier transition count differs')
        state, emitted, exponent = 0, (), 0
        for position, (letter, step) in enumerate(zip(oriented, rewrite['steps'])):
            require(step['position'] == position and step['letter'] == letter and step['coset_before'] == state, 'Schreier transition source differs')
            if abs(letter) == axis:
                direction = 1 if letter > 0 else -1
                token = (power_helper,) if direction > 0 and state == index - 1 else ((-power_helper,) if direction < 0 and state == 0 else ())
                next_state = (state + direction) % index
                exponent += direction
            else:
                token = (cosets[state, abs(letter)] * (1 if letter > 0 else -1),)
                next_state = state
            require(word(step['emitted']) == token and step['coset_after'] == next_state, 'Schreier emitted token/state differs')
            require(free((axis,) * state + (letter,)) == free(image(token, mapping) + (axis,) * next_state), 'Schreier local transition identity fails')
            emitted += token
            state = next_state
        negative = 2 * state > index or (2 * state == index and exponent < 0)
        residue = state - index if negative else state
        subgroup = free(emitted + ((power_helper,) if negative else ()))
        template = free(subgroup + ((axis,) if residue >= 0 else (-axis,)) * abs(residue))
        require(rewrite['axis_exponent'] == exponent and rewrite['unsigned_residue'] == state and rewrite['signed_residue'] == residue and rewrite['negative_residue_carry'] is negative, 'Schreier residue/carry metadata differs')
        require(word(rewrite['subgroup_template']) == subgroup and word(rewrite['template']) == template and image(template, mapping) == oriented, 'Schreier complete rewrite expansion fails')
    require(counts['schreier_plan_checks'] == 1 and counts['schreier_letter_transitions'] == size(before) and counts['schreier_orientation_letters'] == 2 * size(before) and counts['schreier_complete_row_expansions'] == len(before), 'Schreier initial planning charge differs')


def collection_stage_metadata(event):
    before = words(event['before'])
    basis = {abs(x) for w in before for x in w}
    axis, stage, stages = (event[k] for k in ('collection_axis', 'collection_stage', 'collection_stages'))
    require(type(axis) is int and axis in basis and type(stage) is int and type(stages) is int and 1 <= stage <= stages, 'collection axis/stage invalid')
    require(tuple(event['helpers']) == (max(basis) + 1,), 'collection helper not sequentially fresh')
    for row in event['rows']:
        label = row['collection_row_label']
        require(len(label) == 2 and label[0] in ('original', 'definition') and type(label[1]) is int, 'collection row label invalid')
        if label[0] == 'definition':
            require(label[1] in basis and row['template'] == row['before'] and row['oriented'] == row['before'] and row['sign'] == 1 and word(row['conjugator']) == (), 'collection changes a previous defining row')
    counts = event['work_counts']
    if stage != 1:
        require(set(counts) == {'definitions', 'template_expansions'}, 'collection later stage repeats planning work')
        return
    policy = event['collection_direction_policy']
    require(policy in ('cheapest', 'left', 'right'), 'collection direction policy invalid')
    require([tuple(row['collection_row_label']) for row in event['rows']] == [('original', i) for i in range(len(before))], 'collection initial labels differ')
    rewrites = event['collection_rewrites']
    require(len(rewrites) == len(before), 'collection omits an original rewrite')
    maxima, swaps = {}, 0
    for old, rewrite in zip(before, rewrites):
        require(word(rewrite['before']) == old, 'collection rewrite source differs')
        oriented = independent.conjugation(old, rewrite['orientation_sign'], word(rewrite['orientation_conjugator']))
        require(word(rewrite['oriented']) == oriented, 'collection rewrite orientation differs')
        height, letters = 0, []
        for letter in oriented:
            if abs(letter) == axis:
                height += 1 if letter > 0 else -1
            else:
                letters.append((height, letter))
        require(height == rewrite['axis_exponent'] and height >= 0, 'collection axis exponent differs')
        direction = rewrite['direction']
        require(direction in ('left', 'right') and (policy == 'cheapest' or direction == policy), 'collection row direction differs')
        shifted = [(h - (height if direction == 'left' else 0), letter) for h, letter in letters]
        require([tuple(pair) for pair in rewrite['letters_at_heights']] == shifted, 'collection heights differ')
        count = sum(2 ** abs(h) - 1 for h, _ in shifted)
        require(rewrite['collection_swaps'] == count, 'collection swap charge differs')
        swaps += count
        for h, letter in shifted:
            if h:
                key = (1 if h > 0 else -1, abs(letter))
                maxima[key] = max(maxima.get(key, 0), abs(h))
    names, expected, mapping = {}, [], {g: (g,) for g in basis}
    fresh = max(basis)
    for level in range(1, max(maxima.values(), default=0) + 1):
        for (sign, old), maximum in sorted(maxima.items()):
            if level > maximum:
                continue
            previous = old if level == 1 else names[sign, old, level - 1]
            fresh += 1
            names[sign, old, level] = fresh
            definition = (sign * axis, previous, -sign * axis, -previous)
            expected.append((fresh, definition))
            mapping[fresh] = image(definition, mapping)
    require(stages == len(expected) and [(g, word(w)) for g, w in event['collection_definitions']] == expected, 'collection triangular definition inventory differs')
    require(event['collection_helper_names'] == [[*key, value] for key, value in names.items()], 'collection helper coordinates differ')
    require(basis_images(event['collection_full_images']) == mapping, 'collection full dictionary images differ')
    for rewrite in rewrites:
        chunks = rewrite['conjugate_chunks']
        require(len(chunks) == len(rewrite['letters_at_heights']), 'collection chunk count differs')
        body = ()
        for (height, letter), chunk in zip(rewrite['letters_at_heights'], chunks):
            require(chunk['letter'] == letter and chunk['height'] == height, 'collection chunk coordinates differ')
            template = word(chunk['template'])
            power = ((axis,) if height >= 0 else (-axis,)) * abs(height)
            expanded = free(power + (letter,) + invert(power))
            require(len(template) == 2 ** abs(height) and word(chunk['expanded']) == expanded and image(template, mapping) == expanded, 'collection chunk identity differs')
            body += template
        power = (axis,) * rewrite['axis_exponent']
        template = free(power + body if rewrite['direction'] == 'left' else body + power)
        require(word(rewrite['template']) == template and image(template, mapping) == word(rewrite['oriented']), 'collection complete row identity differs')
    frames = 2 if policy == 'cheapest' else 1
    require(counts['collection_plan_checks'] == 1 and counts['collection_orientation_letters'] == 2 * size(before) * frames and counts['collection_letter_transitions'] == size(before) * frames and counts['collection_swap_steps'] == swaps and counts['collection_complete_row_expansions'] == len(before), 'collection planning work differs')


def collection_prefix_metadata(event):
    before = words(event['before'])
    basis = {abs(x) for w in before for x in w}
    axis, other = event['prefix_axis'], event['prefix_other']
    require(type(axis) is int and type(other) is int and abs(axis) in basis and abs(other) in basis and abs(axis) != abs(other), 'prefix signed axes invalid')
    helper = max(basis) + 1
    defining = (axis, other, -axis, -other)
    require(tuple(event['helpers']) == (helper,) and words(event['defining_words']) == (defining,), 'prefix commutator definition differs')
    mode, policy = event['prefix_mode'], event['prefix_direction_policy']
    aliases = event.get('method') == 'commutator_prefix_alias_collection'
    if aliases:
        require(mode == policy == 'per_row', 'alias mode/direction must be per-row')
        indices, sizes = event['alias_indices'], event['alias_catalog_sizes']
        require(len(indices) == len(sizes) == len(before) and all(type(i) is int and type(n) is int and 0 <= i < n <= 4 for i, n in zip(indices, sizes)), 'alias catalog coordinates invalid')
    else:
        require(mode in ('one_direction', 'all_heights') and policy in ('left', 'right', 'best'), 'prefix mode or direction invalid')
    mapping = {g: (g,) for g in basis} | {helper: defining}
    for row in event['rows']:
        row_mode = row['prefix_mode'] if aliases else mode
        require(row_mode in ('one_direction', 'all_heights'), 'prefix row mode invalid')
        oriented = word(row['oriented'])
        exponent, letters = 0, []
        for letter in oriented:
            if abs(letter) == abs(axis):
                exponent += 1 if letter == axis else -1
            else:
                letters.append((exponent, letter))
        direction = row['prefix_direction']
        require(direction in ('left', 'right') and (aliases or policy == 'best' or direction == policy), 'prefix row direction differs')
        require(row['prefix_axis_exponent'] == exponent and len(row['prefix_chunks']) == len(letters), 'prefix row exponent/chunk count differs')
        body = ()
        for (height, letter), chunk in zip(letters, row['prefix_chunks']):
            shifted = height - (exponent if direction == 'left' else 0)
            require(chunk['height'] == shifted and chunk['letter'] == letter, 'prefix shifted height differs')
            template = word(chunk['template'])
            power = ((axis,) if shifted >= 0 else (-axis,)) * abs(shifted)
            expanded = free(power + (letter,) + invert(power))
            require(image(template, mapping) == expanded, 'prefix chunk expansion differs')
            if abs(letter) != abs(other) or row_mode == 'one_direction' and shifted < 0:
                require(template == expanded, 'prefix fallback changed an excluded conjugate')
            body += template
        power = ((axis,) if exponent >= 0 else (-axis,)) * abs(exponent)
        template = free(power + body if direction == 'left' else body + power)
        require(word(row['template']) == template, 'prefix complete template differs from chunks')
        if aliases:
            require(word(row['alias_canonical']) == independent.representative(template), 'alias canonical template differs')
    frames = 2 if policy == 'best' else 1
    counts = event['work_counts']
    if aliases:
        require(set(counts) == {'definitions', 'template_expansions'} and event['charged_units'] == 1 + len(before), 'alias assembly work differs')
        require(type(event['independent_minimum_length']) is int and 5 <= event['independent_minimum_length'] <= size(event['after']), 'alias independent minimum bound invalid')
        alias_catalog_metadata(event)
        if 'coupled_whitehead_score' in event:
            coupled_whitehead_metadata(event)
    else:
        require(counts['prefix_plan_checks'] == 1 and counts['prefix_row_frame_checks'] == frames * len(before) and event['charged_units'] == 2 + (frames + 1) * len(before), 'prefix work accounting differs')


def alias_catalog_metadata(event):
    axis, other, helper = event['prefix_axis'], event['prefix_other'], event['helpers'][0]

    def power(letter, exponent):
        return ((letter,) if exponent >= 0 else (-letter,)) * abs(exponent)

    catalog_sizes, minimum = [], 5
    for row_number, old in enumerate(words(event['before'])):
        sign = -1 if sum(1 if x == abs(axis) else -1 if x == -abs(axis) else 0 for x in old) < 0 else 1
        signed = old if sign == 1 else invert(old)
        levels, level = [0], 0
        for letter in signed[:-1]:
            level += 1 if letter == abs(axis) else -1 if letter == -abs(axis) else 0
            levels.append(level)
        minimal_positions = [i for i, value in enumerate(levels) if value == min(levels)]
        unique = {}
        for side in ('right', 'left'):
            cut = minimal_positions[0 if side == 'right' else -1]
            oriented = signed[cut:] + signed[:cut]
            exponent = sum(1 if x == axis else -1 if x == -axis else 0 for x in oriented)
            height, letters = 0, []
            for letter in oriented:
                if abs(letter) == abs(axis):
                    height += 1 if letter == axis else -1
                else:
                    letters.append((height - (exponent if side == 'left' else 0), letter))
            for mode in ('one_direction', 'all_heights'):
                body = ()
                for h, letter in letters:
                    if abs(letter) != abs(other) or mode == 'one_direction' and h < 0:
                        chunk = free(power(axis, h) + (letter,) + power(axis, -h))
                    else:
                        chunk = (power(axis, h - 1) + (helper,) + (-axis, helper) * (h - 1) + (other,)) if h > 0 else ((power(axis, h) + (-helper,) + (axis, -helper) * (-h - 1) + (axis, other)) if h < 0 else (other,))
                        if letter != other:
                            chunk = invert(chunk)
                    body += chunk
                template = free(power(axis, exponent) + body if side == 'left' else body + power(axis, exponent))
                canonical = independent.representative(template)
                unique.setdefault(canonical, (side, mode, template, oriented, signed[:cut], canonical))
        ordered = sorted(unique.values(), key=lambda value: (len(value[-1]), sum(abs(x) != helper for x in value[-1]), value[-1]))
        catalog_sizes.append(len(ordered))
        minimum += len(ordered[0][-1])
        selected = ordered[event['alias_indices'][row_number]]
        row = event['rows'][row_number]
        require((row['prefix_direction'], row['prefix_mode'], word(row['template']), word(row['oriented']), word(row['conjugator']), word(row['alias_canonical'])) == selected and row['sign'] == sign, 'selected alias differs from exact finite catalog')
    require(tuple(event['alias_catalog_sizes']) == tuple(catalog_sizes) and event['independent_minimum_length'] == minimum, 'alias catalog size/minimum differs')


def coupled_whitehead_metadata(event):
    state = words(event['after'])
    edges = {}
    for relator in state:
        for i, letter in enumerate(relator):
            pair = tuple(sorted((letter, -relator[(i + 1) % len(relator)])))
            require(pair[0] != pair[1], 'coupled score input has cyclic cancellation')
            edges[pair] = edges.get(pair, 0) + 1
    vertices = sorted({v for pair in edges for v in pair})
    positions = {v: i for i, v in enumerate(vertices)}

    def flow_value(source):
        n = len(vertices)
        residual = [[0] * n for _ in range(n)]
        for (x, y), capacity in edges.items():
            i, j = positions[x], positions[y]
            residual[i][j] += capacity
            residual[j][i] += capacity
        start, end = positions[source], positions[-source]
        total = 0
        while True:
            parents, todo = {start: -1}, [start]
            while todo and end not in parents:
                i = todo.pop()
                for j in range(n):
                    if residual[i][j] > 0 and j not in parents:
                        parents[j] = i
                        todo.append(j)
            if end not in parents:
                return total
            route, current = [], end
            while current != start:
                route.append((parents[current], current))
                current = parents[current]
            amount = min(residual[i][j] for i, j in route)
            total += amount
            for i, j in route:
                residual[i][j] -= amount
                residual[j][i] += amount

    metadata = event['coupled_whitehead_score']
    require(metadata['complete'] is True and metadata['raw_length'] == size(state), 'coupled score completeness/raw length differs')
    rows = metadata['signed_multipliers']
    require([row['multiplier'] for row in rows] == vertices, 'coupled score omits a signed multiplier')
    deltas = []
    for row in rows:
        multiplier, side = row['multiplier'], set(row['side'])
        require(multiplier in side and -multiplier not in side and side <= set(vertices), 'coupled score cut partition invalid')
        capacity = sum(count for (x, y), count in edges.items() if (x in side) != (y in side))
        degree = sum(count for pair, count in edges.items() if multiplier in pair)
        require(capacity == row['capacity'] == flow_value(multiplier), 'coupled score is not a minimum cut')
        require(degree == row['degree'] and row['delta'] == capacity - degree, 'coupled score degree/delta differs')
        mapping = {g: ((g,) if g == abs(multiplier) else ((-multiplier,) if -g in side else ()) + (g,) + ((multiplier,) if g in side else ())) for g in {abs(v) for v in vertices}}
        actual = size(normalized(tuple(image(w, mapping) for w in state)))
        require(actual == size(state) + row['delta'], 'coupled cut length differs from exact word images')
        deltas.append(row['delta'])
    require(metadata['one_step_length'] == size(state) + min([0] + deltas), 'coupled complete one-step score differs')


def defining_template_event(event):
    before = words(event['before'])
    old_basis = {abs(x) for w in before for x in w}
    helpers = tuple(event['helpers'])
    definitions = words(event['defining_words'])
    require(helpers and len(helpers) == len(definitions) == len(set(helpers)), 'missing or duplicate template helper')
    require(all(type(g) is int and g > 0 and g not in old_basis for g in helpers), 'template helper is not fresh')
    require(all(len(w) >= 2 and free(w) == w and all(abs(x) in old_basis for x in w) for w in definitions), 'template definition is not reduced over old basis')
    defining_relators = tuple((-g,) + w for g, w in zip(helpers, definitions))
    require(words(event['defining_relators']) == defining_relators, 'new defining relator omitted or altered')
    mapping = {g: (g,) for g in old_basis}
    mapping.update(zip(helpers, definitions))
    rows = event['rows']
    require([r['input_index'] for r in rows] == list(range(len(before))), 'template compression omits or duplicates old relator')
    templates = []
    for row in rows:
        original = before[row['input_index']]
        require(word(row['before']) == original, 'template input relator differs')
        conjugator = word(row['conjugator'])
        require(all(abs(x) in old_basis for x in conjugator), 'template orientation uses a helper or foreign generator')
        oriented = independent.conjugation(original, row['sign'], conjugator)
        require(oriented == word(row['oriented']), 'template orientation identity fails')
        template = word(row['template'])
        require(all(abs(x) in mapping for x in template), 'template uses undefined generator')
        expanded = image(template, mapping)
        require(expanded == oriented == word(row['expanded']), 'freely equal template expansion fails')
        templates.append(template)
    templates = tuple(templates)
    require(words(event['templates']) == templates, 'template list differs from per-row witnesses')
    raw = defining_relators + templates
    require(words(event['raw_after']) == raw, 'template raw tuple omits a defining or original relator')
    after = words(event['after'])
    require(len(after) == len(before) + len(helpers) and after == normalized(raw), 'template final rank or normalization differs')
    independent.normalization(raw, event['normalization'], after)
    uses = {int(k): v for k, v in event['helper_uses'].items()}
    require(uses == {g: sum(abs(x) == g for w in templates for x in w) for g in helpers}, 'template helper use count differs')
    require(event['certificate_kind'] == 'theorem_backed_stable_composite' and event['required_hypothesis'] == 'known balanced presentation of the trivial group', 'template legality premise missing')
    require(event['fully_expanded_elementary_certificate'] is False, 'template expansion scope wrong')
    counts = event['work_counts']
    require(counts['template_expansions'] == len(before) and counts['definitions'] == len(helpers), 'template reserved work wrong')
    require(all(type(n) is int and n >= 0 for n in counts.values()) and event['charged_units'] == sum(counts.values()), 'template total charge wrong')
    if event.get('method') in ('weighted_free_reduction_saturation', 'weighted_neutral_alias_preference'):
        aliases = event['method'] == 'weighted_neutral_alias_preference'
        eliminated = None if aliases else event['eliminate_generator']
        require(eliminated is None or type(eliminated) is int and eliminated in old_basis, 'invalid geodesic objective generator')
        objective = 'token_length_then_old_token_count' if aliases else ('length' if eliminated is None else 'old_generator_count_then_length')
        require(event['objective'] == objective, 'geodesic objective label wrong')
        for row in rows:
            expected_cost = (len(row['template']), sum(abs(x) in old_basis for x in row['template'])) if aliases else (sum(abs(x) == eliminated for x in row['template']), len(row['template']))
            require(tuple(row['template_cost']) == expected_cost, 'geodesic template cost wrong')
            require(type(row['complete_geodesic']) is bool and (not row['complete_geodesic'] or event['saturation_complete']), 'geodesic complete flag without saturation')
        require(event['complete_all_exact_word_geodesics'] == all(row['complete_geodesic'] for row in rows), 'aggregate exact-orientation flag differs')
        if not aliases:
            require(event['automaton_states'] == 1 + sum(2 * (len(w) - 1) for w in definitions), 'dictionary automaton state count wrong')
            require(event['automaton_edges'] == 2 * len(old_basis) + 2 * sum(map(len, definitions)), 'dictionary automaton edge count wrong')
    elif event.get('method') not in ('triangular_schreier_dictionary_stage', 'iterated_commutator_collection_stage', 'commutator_prefix_collection', 'commutator_prefix_alias_collection'):
        require(counts['dictionary_macro_images'] == event['graph_macro_checks'], 'template macro check count wrong')
        require(event['graph_complete'] == (event['graph_macro_checks'] == event['graph_vertices'] * len(helpers)), 'template graph completeness accounting wrong')
        require(0 <= event['graph_macro_edges'] <= event['graph_macro_checks'] <= event['graph_vertices'] * len(helpers), 'template graph count inequalities wrong')
    if event.get('method') == 'root_derived_forced_pivot':
        root_template_metadata(event)
    if event.get('method') == 'conjugacy_derived_forced_pivot':
        conjugacy_template_metadata(event)
    if event.get('method') == 'triangular_schreier_dictionary_stage':
        schreier_stage_metadata(event)
    if event.get('method') == 'iterated_commutator_collection_stage':
        collection_stage_metadata(event)
    if event.get('method') in ('commutator_prefix_collection', 'commutator_prefix_alias_collection'):
        collection_prefix_metadata(event)
    return after


def verify_event(event, *, known_trivial=False):
    kind = event['kind']
    if kind in STABLE_KINDS:
        require(known_trivial is True, 'stable event needs known input triviality; determinant is insufficient')
    if kind == 'defining_compression':
        after = sparse_defining_event(event)
    elif kind in OLD_KINDS:
        after = independent.check_event(event)
    elif kind in ('ambient_automorphism', 'generator_relabeling'):
        after = ambient_event(event)
    elif kind == 'normal_product_substitution':
        after = normal_product_event(event)
    elif kind == 'defining_template_compression':
        after = defining_template_event(event)
    else:
        raise AssertionError('unsupported event kind: ' + kind)
    independent.check_tuple(words(event['before']))
    independent.check_tuple(after)
    if kind == 'lemma11_removal' and 'occurrence_accounting' in event:
        before, generator = words(event['before']), event['generator']
        degree = sum(abs(x) == generator for row in before for x in row)
        donor_length = len(before[event['defining_index']])
        bound = (degree - 2) * (donor_length - 2) - 2
        require(event['occurrence_accounting'] == {'generator_degree': degree, 'donor_length': donor_length, 'length_change_upper_bound': bound}, 'peeling occurrence metadata differs')
        require(size(after) - size(before) <= min(0, bound), 'peeling exceeds its bound or increases length')
    if 'length_change' in event:
        require(event['length_change'] == size(after) - size(event['before']), 'event length change differs')
    return after


def verify_record(record, baseline=None):
    baseline = load_baseline() if baseline is None else baseline
    name = record['name']
    require(name in baseline, 'candidate does not identify a known-trivial baseline presentation')
    row = baseline[name]
    require(record['baseline_sha256'] == BASELINE_SHA256, 'candidate uses another baseline')
    source_key = record.get('source_key', 'current_best')
    require(source_key in row['sources'], 'candidate source key unknown')
    initial = normalized(row['sources'][source_key])
    require(words(record['initial']) == initial, 'candidate starts from wrong source or silently relabels generators')
    if 'source_pointer' in record:
        require(record['source_pointer'] == row['source_pointers'][source_key], 'candidate source pointer differs')
    current = initial
    best, best_at = initial, 0
    boundaries = [{'events': 0, 'rank': len(current), 'length': size(current)}]
    stable = False
    for i, event in enumerate(record['events'], start=1):
        require(words(event['before']) == current, 'candidate path discontinuity')
        current = verify_event(event, known_trivial=True)
        stable |= event['kind'] in STABLE_KINDS
        boundaries.append({'events': i, 'rank': len(current), 'length': size(current)})
        if (size(current), len(current), current) < (size(best), len(best), best):
            best, best_at = current, i
    require(current == words(record['endpoint']), 'candidate endpoint differs from replay')
    if 'endpoint_length' in record:
        require(record['endpoint_length'] == size(current), 'candidate endpoint length wrong')
    if 'endpoint_rank' in record:
        require(record['endpoint_rank'] == len(current), 'candidate endpoint rank wrong')
    if 'length_gain' in record:
        require(record['length_gain'] == row['length'] - size(current), 'candidate gain not measured against current baseline')
    solved = not best or all(len(w) == 1 for w in best) and len({abs(w[0]) for w in best}) == len(best)
    return {'status': 'PASS', 'name': name, 'source_key': source_key,
            'baseline_length': row['length'], 'baseline_rank': row['rank'],
            'endpoint': current, 'endpoint_length': size(current), 'endpoint_rank': len(current),
            'endpoint_gain': row['length'] - size(current), 'boundaries': boundaries,
            'best_certified': best, 'best_prefix_event_count': best_at,
            'best_prefix_length': size(best), 'best_prefix_rank': len(best),
            'best_prefix_gain': row['length'] - size(best),
            'strict_length_improvement': size(best) < row['length'],
            'same_length_rank_improvement': size(best) == row['length'] and len(best) < row['rank'],
            'canonical_endpoint_equals_baseline': current == normalized(row['words']),
            'endpoint_misses_better_prefix': (size(best), len(best)) < (size(current), len(current)),
            'solved_at_certified_prefix': solved,
            'certificate_scope': 'theorem_backed_stable_composite' if stable else 'explicit_ordinary_AC_composite_from_selected_source',
            'fully_expanded_elementary_path': False}


def tiny_controls():
    base = load_baseline()
    before = normalized(((1,), (2,)))
    target = before.index((-1,))
    donor = before.index((-2,))
    factor = {'donor_index': donor, 'sign': -1, 'conjugator': (-1,)}
    raw_target = (-1, 1, 2, -1)
    replacement = free(raw_target)
    event = {'kind': 'normal_product_substitution', 'before': before, 'target': target,
             'factors': [factor], 'raw_target_after': replacement,
             'after': normalized(before[:target] + (replacement,) + before[target + 1:])}
    verify_event(event)
    failures = 0
    for bad in ({**event, 'raw_target_after': (1,)},
                {**event, 'factors': [{'donor_index': target, 'sign': 1, 'conjugator': ()}]},
                {**event, 'factors': [{**factor, 'sign': True}]},
                {**event, 'after': (event['after'][0],)}):
        try:
            verify_event(bad)
        except (AssertionError, ValueError):
            failures += 1
    require(failures == 4, 'normal-product corruption control accepted')
    mapping = {1: (7,), 2: (-11,)}
    reverse = {7: (1,), 11: (-2,)}
    relabeled = normalized(tuple(image(w, mapping) for w in before))
    renaming = {'kind': 'generator_relabeling', 'before': before, 'images': mapping,
                'inverse_images': reverse, 'after': relabeled}
    verify_event(renaming, known_trivial=True)
    try:
        verify_event(renaming)
    except AssertionError:
        failures += 1
    require(failures == 5, 'triviality provenance control accepted')
    records = [json.loads(line) for line in (PRIOR / 'shortening_witnesses.jsonl').read_text().splitlines()]
    selected = next(r for r in records if r['name'] == 'aca_80')
    witness = selected['witness']
    replay = verify_record({'name': 'aca_80', 'baseline_sha256': BASELINE_SHA256,
                            'source_key': 'saved_rank2', 'initial': witness['initial'],
                            'events': witness['events'], 'endpoint': witness['endpoint'],
                            'endpoint_length': 17, 'endpoint_rank': 3, 'length_gain': 0}, base)
    require(replay['endpoint_gain'] == 0, 'old gain falsely credited against2180 baseline')
    require(set(abs(x) for w in base['aca_7']['words'] for x in w) == {2, 3, 4}, 'baseline label gap lost')
    return {'status': 'PASS', 'baseline_rows': 124, 'baseline_total': 2180,
            'normal_product_positive_controls': 1, 'rejected_corruptions_or_missing_hypothesis': failures,
            'signed_relabeling_to_generator11': True, 'nonconsecutive_baseline_ids_preserved': True,
            'prior_aca80_path_gain_against_current_baseline': 0, 'presentation_searches': 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--records')
    parser.add_argument('--output', default=str(HERE / 'verification_ready.json'))
    args = parser.parse_args()
    if args.records:
        path = Path(args.records)
        data = json.loads(path.read_text()) if path.suffix != '.jsonl' else [json.loads(line) for line in path.read_text().splitlines()]
        rows = data['rows'] if isinstance(data, dict) and 'rows' in data else data if isinstance(data, list) else [data]
        baseline = load_baseline()
        require(len(rows) == len({r['name'] for r in rows}), 'duplicate candidate ID')
        results = [verify_record(row, baseline) for row in rows]
        result = {'status': 'PASS', 'source_file': str(path), 'source_sha256': sha(path), 'rows': results}
    else:
        result = tiny_controls()
    result['baseline_sha256'] = BASELINE_SHA256
    result['frozen_independent_auditor_sha256'] = AUDITOR_SHA256
    result['verifier_sha256'] = sha(Path(__file__))
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
