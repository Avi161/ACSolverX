"""Cancellation-aware defining templates with exact stable-composite witnesses."""
from __future__ import annotations

from collections import Counter, deque
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))
import lemma11
import search
import whitehead


def _orientations(word):
    if not word:
        return [((), 1, ())]
    return [(base[k:] + base[:k], sign, base[:k])
            for sign, base in ((1, word), (-1, search.inverse(word)))
            for k in range(len(base))]


def _expand(word, replacements):
    return search.reduced(y for x in word for y in
                          (replacements[abs(x)] if x > 0 else search.inverse(replacements[abs(x)])))


def _prefix_graph(words, defining_words):
    vertices = {()}
    orientations = [_orientations(w) for w in words]
    endpoints = [oriented for choices in orientations for oriented, _, _ in choices]
    endpoints.extend(w for defining in defining_words for w in (defining, search.inverse(defining)))
    for word in endpoints:
        vertices.update(word[:k] for k in range(1, len(word) + 1))
    neighbors = {word: [] for word in vertices}
    for word in vertices:
        if word:
            parent, letter = word[:-1], word[-1]
            neighbors[parent].append((letter, word))
            neighbors[word].append((-letter, parent))
    return orientations, vertices, neighbors


def compress_dictionary(words, defining_words, remaining):
    """Return ``(after, event, charged)`` or ``(None, None, 0)`` if too little work.

    Each tested macro edge costs one unit, each checked old-row expansion one,
    and each defining row one. The finite prefix graph is an explicit candidate
    generator, not a claim of globally shortest dictionary representations.
    """
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    words = tuple(tuple(w) for w in words)
    if search.normalize(words) != words:
        raise ValueError('compress_dictionary requires normalized input')
    defining_words = tuple(tuple(w) for w in defining_words)
    if not defining_words:
        raise ValueError('at least one defining word is required')
    basis = {abs(x) for w in words for x in w}
    for word in defining_words:
        if len(word) < 2 or search.reduced(word) != word or not {abs(x) for x in word} <= basis:
            raise ValueError('definitions must be reduced words in the current generators of length at least two')
    reserved = len(words) + len(defining_words)
    if remaining < reserved:
        return None, None, 0
    first = 1 + max(basis, default=0)
    helpers = tuple(first + k for k in range(len(defining_words)))
    orientations, vertices, neighbors = _prefix_graph(words, defining_words)
    ordered = sorted(vertices, key=lambda w: (len(w), w))
    tested, edges = 0, 0
    for vertex in ordered:
        for helper, defining in zip(helpers, defining_words):
            if tested + reserved == remaining:
                break
            target = search.reduced(vertex + defining)
            tested += 1
            if target in vertices:
                neighbors[vertex].append((helper, target))
                neighbors[target].append((-helper, vertex))
                edges += 1
        if tested + reserved == remaining:
            break
    paths, queue = {(): ()}, deque([()])
    while queue:
        word = queue.popleft()
        for letter, target in sorted(neighbors[word]):
            if target not in paths:
                paths[target] = paths[word] + (letter,)
                queue.append(target)
    replacements = {g: (g,) for g in basis}
    replacements.update(zip(helpers, defining_words))
    templates, rows = [], []
    for i, choices in enumerate(orientations):
        selected = min((len(paths[oriented]), paths[oriented], oriented, sign, conjugator)
                       for oriented, sign, conjugator in choices)
        _, template, oriented, sign, conjugator = selected
        expanded = _expand(template, replacements)
        if expanded != oriented or search.reduced(search.inverse(conjugator) +
                (words[i] if sign == 1 else search.inverse(words[i])) + conjugator) != oriented:
            raise AssertionError('dictionary template does not expand to the oriented row')
        templates.append(template)
        rows.append({'input_index': i, 'before': words[i], 'sign': sign,
                     'conjugator': conjugator, 'oriented': oriented,
                     'template': template, 'expanded': expanded})
    definitions = tuple((-helper,) + word for helper, word in zip(helpers, defining_words))
    raw_after = definitions + tuple(templates)
    after, normalization = lemma11.normalize_witness(raw_after)
    event = {'kind': 'defining_template_compression', 'before': words,
             'certificate_kind': 'theorem_backed_stable_composite',
             'required_hypothesis': 'known balanced presentation of the trivial group',
             'helpers': helpers, 'defining_words': defining_words, 'defining_relators': definitions,
             'rows': rows, 'templates': tuple(templates), 'raw_after': raw_after,
             'normalization': normalization, 'after': after,
             'helper_uses': {g: sum(sum(abs(x) == g for x in w) for w in templates) for g in helpers},
             'length_change': search.length(after) - search.length(words),
             'graph_vertices': len(vertices), 'graph_macro_edges': edges,
             'graph_macro_checks': tested, 'graph_complete': tested == len(vertices) * len(helpers),
             'work_counts': {'dictionary_macro_images': tested, 'template_expansions': len(words),
                             'definitions': len(defining_words)},
             'charged_units': tested + reserved, 'fully_expanded_elementary_certificate': False}
    replay(event)
    return after, event, tested + reserved


def replay(event):
    before = tuple(tuple(w) for w in event['before'])
    helpers = tuple(event['helpers'])
    definitions = tuple(tuple(w) for w in event['defining_words'])
    old = {abs(x) for w in before for x in w}
    if len(set(helpers)) != len(helpers) or old.intersection(helpers) or any(
            type(g) is not int or g <= 0 for g in helpers):
        raise AssertionError('dictionary helper is not fresh')
    if len(definitions) != len(helpers) or any(not {abs(x) for x in w} <= old for w in definitions):
        raise AssertionError('definition depends on a new or absent generator')
    expected_definitions = tuple((-g,) + w for g, w in zip(helpers, definitions))
    if tuple(tuple(w) for w in event['defining_relators']) != expected_definitions:
        raise AssertionError('defining row differs')
    images = {g: (g,) for g in old}
    images.update(zip(helpers, definitions))
    if [row['input_index'] for row in event['rows']] != list(range(len(before))):
        raise AssertionError('an original row was omitted or duplicated')
    templates = []
    for row in event['rows']:
        original = before[row['input_index']]
        template, oriented = tuple(row['template']), tuple(row['oriented'])
        sign, conjugator = row['sign'], tuple(row['conjugator'])
        if type(sign) is not int or sign not in (-1, 1) or tuple(row['before']) != original:
            raise AssertionError('invalid row orientation')
        if search.reduced(search.inverse(conjugator) +
                (original if sign == 1 else search.inverse(original)) + conjugator) != oriented:
            raise AssertionError('row conjugation differs')
        expanded = []
        for x in template:
            image = images[abs(x)]
            expanded.extend(image if x > 0 else search.inverse(image))
        if search.reduced(expanded) != oriented or tuple(row['expanded']) != oriented:
            raise AssertionError('template expansion differs')
        templates.append(template)
    raw_after = expected_definitions + tuple(templates)
    if tuple(tuple(w) for w in event['templates']) != tuple(templates) or tuple(
            tuple(w) for w in event['raw_after']) != raw_after:
        raise AssertionError('raw dictionary endpoint differs')
    after = tuple(tuple(w) for w in event['after'])
    if search.normalize(raw_after) != after or len(after) != len(before) + len(helpers):
        raise AssertionError('normalized dictionary endpoint differs')
    if search.length(after) - search.length(before) != event['length_change']:
        raise AssertionError('dictionary length differs')
    return after


def plans(words, maximum=4):
    basis = sorted({abs(x) for w in words for x in w})
    commutators = [search.reduced((a, b, -a, -b))
                   for a, positive in combinations(basis, 2) for b in (positive, -positive)]
    repeated = search.definitions(words)
    candidates = []
    if repeated:
        candidates.append((repeated[0],))
    candidates.extend((w,) for w in commutators)
    if len(repeated) >= 2:
        candidates.append((repeated[0], repeated[1]))
    candidates.extend((w,) for w in repeated[1:])
    unique = []
    for plan in candidates:
        if plan not in unique:
            unique.append(plan)
    return unique[:maximum]


def probe(words, remaining, *, maximum_plans=4):
    """Return ``(candidates, charged)`` for dictionary-plus-removal exchanges.

    A selected dictionary has one or two new definitions, with no bound on
    current rank or relator length. Work, not a length ceiling, truncates each
    finite graph scan. Every returned prefix has exact expansion witnesses.
    """
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in 0..1000')
    if type(maximum_plans) is not int or maximum_plans <= 0:
        raise ValueError('maximum_plans must be positive')
    before = tuple(tuple(w) for w in words)
    current, normalization = lemma11.normalize_witness(before)
    prefix = [] if before == current else [{'kind': 'relator_normalization', 'before': before,
                                           'after': current, 'normalization': normalization}]
    options, candidates, charged = plans(current, maximum_plans), [], 0
    for position, defining_words in enumerate(options):
        if charged == remaining:
            break
        allowance = (remaining - charged) // (len(options) - position)
        dictionary_allowance = max(len(current) + len(defining_words), allowance * 2 // 3)
        dictionary_allowance = min(dictionary_allowance, allowance)
        after, event, cost = compress_dictionary(current, defining_words, dictionary_allowance)
        charged += cost
        if event is None or not any(event['helper_uses'].values()):
            continue
        initial_events = prefix + [event]
        candidates.append((after, initial_events))
        local_remaining = allowance - cost
        descended, descent, cost, complete = whitehead.descend(after, local_remaining // 3)
        charged += cost
        local_remaining -= cost
        if descent:
            candidates.append((descended, initial_events + descent))
        removals, cost = lemma11.generate_removals(descended, local_remaining, expose_primitives=True)
        charged += cost
        candidates.extend((endpoint, initial_events + descent + events) for endpoint, events in removals)
    if charged > remaining:
        raise AssertionError('dictionary exchange exceeded work budget')
    unique = {}
    for after, events in candidates:
        if after not in unique or len(events) < len(unique[after]):
            unique[after] = events
    return sorted(unique.items(), key=lambda item: (search.length(item[0]), len(item[0]), item[0])), charged
