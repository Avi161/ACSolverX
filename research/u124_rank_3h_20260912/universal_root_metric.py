"""Optimize a retained power helper without requiring a Baumslag--Solitar donor."""
import theory_corridor as corridor
import theory_root_metric as single
from theory_corridor import lemma11
from search import length


def compile_metric(words, root, exponent):
    current, root, event = single._shear(words, root, exponent)
    events = [event]
    pending = [i for i in range(len(current)) if i != root.donor]
    while pending:
        selected = pending.pop(0)
        current, event = single._cyclic_pack(current, selected, root)
        positions = {row['input_index']: i for i, row in enumerate(event['normalization'])}
        pending = [positions[i] for i in pending]
        root = corridor.Root(positions[root.donor], root.helper, root.base, root.exponent,
                             [dict(f, donor_index=positions[f['donor_index']]) for f in root.factors])
        events.append(event)
    return current, events


def probe(words, remaining, *, audits=None):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    candidates, charged = [], 0
    for root in corridor.roots(words):
        if charged == remaining:
            break
        charged += 1
        cores = []
        for i, word in enumerate(words):
            if i == root.donor:
                continue
            expanded, _ = corridor.expand_helper(word, root)
            core, _ = lemma11.canonical_witness(expanded)
            cores.append(core)
        nonbase = sum(abs(x) != root.base for core in cores for x in core)
        ceiling = length(words) - nonbase - 1
        plans = []
        complete = True
        for denomination in range(1, ceiling + 1):
            if charged == remaining:
                complete = False
                break
            charged += 1
            exponent = denomination if root.exponent > 0 else -denomination
            metric = corridor.Root(root.donor, root.helper, root.base, exponent, [])
            predicted = denomination + 1 + sum(len(corridor.pack_powers(core, metric)) for core in cores)
            if predicted <= length(words):
                plans.append((predicted, exponent))
        metadata = {'root_donor': root.donor, 'root_helper': root.helper,
                    'root_base': root.base, 'old_exponent': root.exponent,
                    'expanded_nonbase_letters': nonbase, 'finite_denomination_ceiling': ceiling,
                    'all_costs_evaluated': complete, 'nonincreasing_plans': plans}
        if audits is not None:
            audits.append(metadata)
        for predicted, exponent in sorted(plans):
            if charged + len(words) > remaining:
                return candidates, charged
            charged += len(words)
            after, events = compile_metric(words, root, exponent)
            if length(after) != predicted:
                raise AssertionError('universal root-metric cost prediction differs')
            if after != words:
                events[-1]['universal_root_metric_audit'] = metadata
                candidates.append((after, events))
    return candidates, charged
