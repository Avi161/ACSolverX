"""Compile captured ordinary substitution prefixes into AC1/AC2/AC3 moves."""
from . import ac_words as ac


def swap_rows(trace):
    old_first = trace.pair[0]
    expected = list(reversed(trace.pair))
    trace.multiply(0)
    trace.invert(0)
    trace.multiply(1)
    trace.invert(0)
    trace.multiply(0)
    trace.conjugate(0, old_first)
    trace.invert(1)
    if trace.pair != expected:
        raise ValueError("ordinary row swap failed")


def orient(trace, target, expected):
    core, prefix = ac.cyclic(trace.pair[target])
    trace.conjugate(target, prefix)
    for sign in (1, -1):
        word = core if sign == 1 else ac.inv(core)
        for cut in range(max(1, len(word))):
            if word[cut:] + word[:cut] == expected:
                if sign == -1:
                    trace.invert(target)
                trace.conjugate(target, word[:cut])
                if trace.pair[target] != expected:
                    raise ValueError("orientation witness failed")
                return
    raise ValueError("expected word is outside the relator cyclic/inverse class")


def align(trace, expected):
    if len(expected) != 2:
        raise ValueError("two expected relators required")
    if ac.canon(trace.pair[0]) != ac.canon(expected[0]):
        swap_rows(trace)
    for target in (0, 1):
        orient(trace, target, expected[target])
    if trace.pair != list(expected):
        raise ValueError("pair alignment failed")


def compile_prefix(pair, states, steps):
    if not states or len(states) != len(steps) + 1:
        raise ValueError("invalid prefix record length")
    trace = ac.Trace(pair)
    align(trace, states[0])
    boundaries = [{"move_count": len(trace.moves), "pair": list(trace.pair)}]
    for step, expected in zip(steps, states[1:]):
        if step.get("kind") != "substitution":
            raise ValueError("only ordinary substitution paths accepted")
        values = step["move"].split("_")
        if len(values) != 4:
            raise ValueError("invalid substitution encoding")
        target, sign, first_cut, second_cut = map(int, values)
        if target not in (1, 2) or sign not in (-1, 1):
            raise ValueError("invalid target or sign")
        target -= 1
        donor = 1 - target
        before_donor = trace.pair[donor]
        target_word = trace.pair[target]
        if not target_word or not before_donor:
            raise ValueError("empty input to a captured substitution")
        if not 0 <= first_cut < len(target_word) or not 0 <= second_cut < len(before_donor):
            raise ValueError("cut outside canonical word")
        trace.conjugate(target, target_word[:(-first_cut) % len(target_word)])
        if sign == -1:
            trace.invert(donor)
        prefix = trace.pair[donor][:(-second_cut) % len(before_donor)]
        trace.conjugate(donor, prefix)
        trace.multiply(target)
        trace.conjugate(donor, ac.inv(prefix))
        if sign == -1:
            trace.invert(donor)
        if trace.pair[donor] != before_donor:
            raise ValueError("substitution donor was not restored")
        align(trace, expected)
        boundaries.append({"move_count": len(trace.moves), "pair": list(trace.pair)})
    replayed = ac.replay(pair, trace.moves)
    if replayed != trace.pair:
        raise ValueError("independent elementary replay failed")
    return {"input": list(pair), "endpoint": replayed, "moves": trace.moves,
            "elementary_move_count": len(trace.moves), "substitution_count": len(steps),
            "boundaries": boundaries, "total_length": sum(map(len, replayed)),
            "certificate_kind": "independently_replayed_ordinary_elementary_prefix"}
