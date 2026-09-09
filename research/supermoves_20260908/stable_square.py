"""Stable-square pinches followed by the proved Q_N donor-changing bridge."""
from experiments.equivalence_classes.lib.words import (
    canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot, apply_pair,
    apply_hom, SIGNED_PERMS,
)
from experiments.search.bs_collapse import bs_collapse


DONOR = 'YYXXyxx'
DONOR_KEY = canon_rel(DONOR)
DONOR_TRANSFORMS = {}
for _label, _images in SIGNED_PERMS:
    _inverse = {image.lower(): letter if image.islower() else letter.upper()
                for letter, image in _images.items()}
    DONOR_TRANSFORMS.setdefault(canon_rel(apply_hom(DONOR, _images)), _inverse)


def forward_pinch(word):
    for oriented in (word, inv(word)):
        for cut in range(len(oriented)):
            candidate = oriented[cut:] + oriented[:cut]
            if not candidate.startswith('XX') or len(candidate) < 5:
                continue
            if candidate[2] not in 'yY':
                continue
            letter = candidate[2]
            end = 2
            while end < len(candidate) and candidate[end] == letter:
                end += 1
            if candidate[end:end + 2] == 'xx':
                return candidate, 'XX' + letter, letter * 2 + 'XX'
    return None


def collapse(pair, budget=1000):
    if type(budget) is not int or not 1 <= budget <= 10000:
        raise ValueError('budget must be an integer in 1..10000')
    state = canon_pair(*pair)
    states, steps = [list(state)], []
    peak = max(map(len, state))
    pinch_steps = 0

    def result(solved, reason):
        return dict(solved=solved, reason=reason, states=states, steps=steps,
                    rewrites=len(steps), nodes_explored=len(steps) + 1,
                    pinch_steps=pinch_steps, max_intermediate_relator_length=peak)

    def append(child, step):
        nonlocal state, peak
        state = tuple(child)
        steps.append(step)
        states.append(list(state))
        peak = max(peak, max(map(len, state)))

    # This is the verified local replacement-to-offset convention from bs_collapse.
    def rewrite(word, lhs, rhs):
        target_key = canon_rel(word)
        target = 0 if state[0] == target_key else 1
        if state[target] != target_key or state[1 - target] != DONOR_KEY:
            raise AssertionError('tracked stable-square pair differs from state')
        desired = cyc_reduce(free_reduce(rhs + word[len(lhs):]))
        wanted = canon_pair(DONOR, desired)
        actual = state[target]
        shift = (word + word).find(actual)
        local_lhs, local_rhs = lhs, rhs
        if 0 <= shift < len(word):
            start = -shift % len(word)
        else:
            inverted = inv(word)
            shift = (inverted + inverted).find(actual)
            if not 0 <= shift < len(word):
                raise AssertionError('target is not a cyclic orientation')
            start = (len(word) - len(lhs) - shift) % len(word)
            local_lhs, local_rhs = inv(lhs), inv(rhs)
        needed = free_reduce(inv(local_lhs) + local_rhs)
        donor_move = None
        for sign in (1, -1):
            oriented = state[1 - target] if sign == 1 else inv(state[1 - target])
            for cut in range(len(oriented)):
                if rot(oriented, cut) == needed:
                    donor_move = sign, cut
                    break
            if donor_move is not None:
                break
        if donor_move is None:
            raise AssertionError('pinch is not a donor substitution')
        sign, cut = donor_move
        move = (target + 1, sign, -(start + len(local_lhs)) % len(actual), cut)
        child = replay_move(state, move)
        if child != wanted:
            raise AssertionError('stable-square rewrite replay failed')
        append(child, {'kind': 'substitution', 'move': '_'.join(map(str, move))})

    if DONOR_KEY not in state:
        transform = next((DONOR_TRANSFORMS[word] for word in state
                          if word in DONOR_TRANSFORMS), None)
        if transform is None:
            return result(False, 'donor_not_recognized')
        if budget < 2:
            return result(False, 'budget')
        append(apply_pair(state, transform), {'kind': 'automorphism', 'images': transform})
        if DONOR_KEY not in state:
            raise AssertionError('signed donor normalization failed')
    while 1 + len(steps) < budget:
        index = state.index(DONOR_KEY)
        companion = state[1 - index]
        n = len(companion) - 4
        direct = n >= 5 and canon_rel('Y' * n + 'xYXX') == companion
        flip_y = n >= 5 and canon_rel('y' * n + 'xyXX') == companion
        if direct or flip_y:
            if len(steps) + 4 + int(not direct) >= budget:
                return result(False, 'bridge_budget')
            if not direct:
                transform = {'x': 'x', 'y': 'Y'}
                append(apply_pair(state, transform), {'kind': 'automorphism', 'images': transform})
            transform = {'x': 'xy', 'y': 'y'}
            append(apply_pair(state, transform), {'kind': 'automorphism', 'images': transform})
            for move in ((1, -1, 4, 0), (1, -1, 0, 0)):
                append(replay_move(state, move),
                       {'kind': 'substitution', 'move': '_'.join(map(str, move))})
            expected = canon_pair('YYXyx', 'Y' * (n + 1) + 'xyXYX')
            if state != expected:
                raise AssertionError('symbolic Q_N bridge replay failed')
            terminal = bs_collapse(state, budget=budget - len(steps), intermediate_cap=None)
            for child, step in zip(terminal['states'][1:], terminal['steps']):
                append(child, step)
            return result(terminal['solved'], 'stable_square_Q_N' if terminal['solved'] else terminal['reason'])
        pinch = forward_pinch(companion)
        if pinch is None:
            return result(False, 'pinch_stalled')
        rewrite(*pinch)
        pinch_steps += 1
    return result(False, 'budget')
