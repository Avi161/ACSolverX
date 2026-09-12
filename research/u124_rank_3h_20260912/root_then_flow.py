"""Keep a proper-power helper, expose its base, then apply exact corridor rules."""
import theory_flow_exact
import theory_primitive_root


def probe(words, remaining):
    prepared, charged = theory_primitive_root.probe(words, min(300, remaining))
    out = list(prepared)
    for index, (state, prefix) in enumerate(prepared):
        allowance = (remaining - charged) // (len(prepared) - index)
        candidates, cost = theory_flow_exact.probe(state, allowance)
        charged += cost
        out.extend((after, prefix + events) for after, events in candidates)
    return out, charged
