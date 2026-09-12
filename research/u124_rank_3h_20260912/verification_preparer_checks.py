"""Independent retained-root preparation and signed metric-rebase controls."""
from itertools import product
import json
from pathlib import Path

import theory_primitive_root as primitive
import theory_root_metric as metric
import theory_corridor as corridor
import verify


HERE = Path(__file__).resolve().parent


def replay(initial, endpoint, events):
    current = initial
    for event in events:
        verify.require(verify.words(event['before']) == current, 'preparer path discontinuity')
        current = verify.verify_event(json.loads(json.dumps(event)), known_trivial=True)
    verify.require(current == verify.words(endpoint), 'preparer endpoint differs')
    return current


def power(g, n):
    return (g if n >= 0 else -g,) * abs(n)


def isolate(value, helper):
    positions = [i for i, x in enumerate(value) if abs(x) == helper]
    verify.require(len(positions) == 1, 'independent helper isolation requires singleton occurrence')
    i = positions[0]
    p, q = value[:i], value[i + 1:]
    return verify.free(q + p if value[i] < 0 else verify.invert(p) + verify.invert(q))


def primitive_controls():
    counts, events_checked, exposed = 0, 0, 0
    for a, b, h in ((2, 5, 11), (101, 307, 10**25)):
        for definition in ((a, b) * 2, (b,) + (a, b) * 3 + (-b,), (a, b, -a, -b) * 2):
            initial = verify.normalized(((-h,) + definition, (a,), (b,)))
            candidates, charge = primitive.probe(initial, 100)
            verify.require(charge <= 100, 'primitive probe budget exceeded')
            is_commutator = definition == (a, b, -a, -b) * 2
            for endpoint, events in candidates:
                replay(initial, endpoint, events)
                for event in events:
                    if event.get('objective') == 'canonicalize_retained_helper_definition':
                        before_value = isolate(verify.words(event['before'])[event['defining_relator_before']], event['helper'])
                        after_value = isolate(verify.words(event['after'])[event['defining_relator_after']], event['helper'])
                        verify.require(before_value == verify.word(event['definition_before']) and after_value == verify.word(event['definition_after']), 'helper-frame definition metadata differs')
                        w = event['definition_canonical_witness']
                        verify.require(verify.independent.conjugation(before_value, w['sign'], verify.word(w['conjugator'])) == after_value, 'helper-frame canonical identity differs')
                    if event.get('objective') == 'minimize_retained_definition_root':
                        mapping = verify.basis_images(event['images'])
                        helper = event['helper']
                        verify.require(mapping[helper] == (helper,), 'relative Whitehead moved retained helper')
                        root_before = verify.word(event['selected_root_before'])
                        raw_root = verify.image(root_before, mapping)
                        root_after = verify.independent.representative(raw_root)
                        verify.require(raw_root == verify.word(event['raw_root_after']) and root_after == verify.word(event['canonical_root_after']), 'root image metadata differs')
                        verify.require(event['root_length_change'] == len(root_after) - len(root_before) < 0, 'root descent is not strict')
                    events_checked += 1
                final = events[-1]
                final_definition = isolate(verify.words(endpoint)[final['final_defining_relator']], final['helper'])
                pure = len({abs(x) for x in final_definition}) == 1
                verify.require(final['proper_power_root_exposed'] == pure, 'primitive recognition flag differs')
                verify.require(not is_commutator or not pure, 'commutator root falsely promoted to primitive')
                exposed += pure
            counts += 1
    return {'status': 'PASS', 'known_triviality_proof': 'The two old generators occur as singleton relators; the retained helper definition then kills the helper.',
            'plants': counts, 'events_checked': events_checked, 'pure_power_endpoints': exposed,
            'source_sha256': verify.sha(HERE / 'theory_primitive_root.py')}


def metric_controls():
    records = []
    for old in (-2, 2):
        a, x, h, m, n, e = 2, 5, 11, 4, 5, 11
        initial = verify.normalized(((-h,) + power(a, old), (x,) + power(a, m) + (-x,) + power(a, -n), (x,) + power(a, e)))
        root = next(r for r in corridor.roots(initial) if r.helper == h and r.base == a and r.exponent == old)
        donor = next(i for i, w in enumerate(initial) if sum(abs(t) == x for t in w) == 2)
        target = next(i for i in range(3) if i not in (root.donor, donor))
        model = corridor.bs_model(initial, root, donor)
        verify.require(model is not None, 'metric plant BS model absent')
        for new, q in product((-3, 3), (-1, 0, 1)):
            endpoint, events = metric.compile_rebase(initial, root, model, target, (q,), new)
            replay(initial, endpoint, events)
            verify.require(len(events) == 4 and [event['kind'] for event in events] == ['normal_product_substitution', 'ambient_automorphism', 'normal_product_substitution', 'normal_product_substitution'], 'metric compile order differs')
            shear = events[1]
            verify.require(verify.basis_images(shear['images'])[h] == power(a, old - new) + (h,), 'metric shear image differs')
            roots = [isolate(w, h) for w in endpoint if sum(abs(t) == h for t in w) == 1]
            verify.require(power(a, new) in roots, 'new denomination not retained')
            records.append({'old': old, 'new': new, 'flow': q, 'before_length': verify.size(initial), 'after_length': verify.size(endpoint)})
    initial = verify.normalized(((-11, 2, 2), (5, 2, 2, 2, 2, -5, -2, -2, -2, -2, -2), (5,) + (2,) * 11))
    candidates, charged = metric.probe(initial, 1000)
    verify.require(charged <= 1000 and candidates, 'metric tiny probe failed or over budget')
    for endpoint, events in candidates:
        replay(initial, endpoint, events)
        verify.require(verify.size(endpoint) < verify.size(initial), 'predicted strict metric gain not realized')
    return {'status': 'PASS', 'known_triviality_proof': 'Target x a^11=1 gives x=a^-11; the BS(4,5) donor becomes a^4=a^5, forcing a=x=h=1.',
            'signed_rebases_checked': records, 'single_planted_probe_candidates': len(candidates), 'single_planted_probe_units': charged,
            'source_sha256': verify.sha(HERE / 'theory_root_metric.py')}


def main():
    for name, controls in [('primitive_root', primitive_controls()), ('root_metric', metric_controls())]:
        result = {'status': 'PASS', 'controls': controls, 'census_searches': 0,
                  'verifier_sha256': verify.sha(HERE / 'verify.py'), 'script_sha256': verify.sha(Path(__file__))}
        (HERE / ('verification_' + name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'module': name, 'controls': controls}, indent=2))


if __name__ == '__main__':
    main()
