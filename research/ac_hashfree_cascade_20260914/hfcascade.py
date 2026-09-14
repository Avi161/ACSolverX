"""A hash-free, table-free deterministic cascade for balanced two-generator presentations.

Every decision is taken from the structure of the current pair of words.  There is
no visited set, no hash map, no heap keyed by state identity and no pattern table:
the four Nielsen maps are the move alphabet of a free-group automorphism, the
substitution moves are enumerated from the current words, and the only memory is
the certificate path itself (a list that is only ever appended to or truncated).

Stages, run in order until the pair is (g, h) with g, h distinct generators:

  A. pair Whitehead descent      strictly shorten the total cyclic length with a
                                 Nielsen map (x->xy, x->xY, y->yx, y->yX);
  B. primitive-relator deletion  strictly shorten ONE relator with Nielsen maps
                                 (companion carried along); a relator that reaches
                                 length 1 is a primitive donor, its letter is
                                 deleted from the companion one substitution at a
                                 time, and abelianisation forces the residue to
                                 be the other generator;
  C. structural pinch cascade    a relator of the cyclic shape g^a h^p g^-a h^q
                                 (a generator with exactly two syllables of
                                 opposite exponent) defines four rewriting rules;
                                 they pinch the companion's g-syllables away
                                 (Britton reduction) whenever the enclosed
                                 h-exponent is divisible, one substitution move
                                 per rule use; a companion reduced to g^s h^r with
                                 |s| = 1 or |r| = 1 is primitive and finishes by B;
  D. beam descent                width-w level-synchronous descent on a score that
                                 is a function of the state (total length, or the
                                 repository's S20_MK2 = L + 20 S + 2 MK); children
                                 are all seam-cancelling rotation products; a level
                                 is deduplicated by sorting (comparison, not
                                 hashing); no closed set; the gates of B and C are
                                 tried on every generated child.

Work units (the "budget"): one per Nielsen image evaluation, one per accepted
automorphism, one per substitution move applied, one per state expanded in D.
Gate inspections (syllable parses, letter counts, divisibility preflights) are
not charged, exactly as the AC19 census policy did not charge its gate scans.

Certificates use the repository's mixed-step contract: steps of kind
'automorphism' carry one of the four Nielsen image maps, steps of kind
'substitution' carry a Definition-2.1 move string 'target_jsign_k1_k2', and the
recorded state after every step is the canonical pair.  `verify.py` replays them
independently.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom, canon_pair, canon_rel, cyc_reduce, free_reduce, inv, replay_move, rot,
)

NIELSEN = ({'x': 'xy', 'y': 'y'}, {'x': 'xY', 'y': 'y'},
           {'x': 'x', 'y': 'yx'}, {'x': 'x', 'y': 'yX'})
_ORDER = {'Y': 0, 'y': 1, 'X': 2, 'x': 3}
SIGNED_PERMS = tuple({'x': fx, 'y': fy} for fx in 'xXyY' for fy in 'xXyY' if fx.lower() != fy.lower())
IDENTITY = {'x': 'x', 'y': 'y'}


def perm_canonical(state):
    """The least canonical pair over the eight signed generator permutations, and the
    permutation that reaches it (None when the state is already least)."""
    best, best_img = state, None
    for img in SIGNED_PERMS:
        cand = canon_pair(apply_hom(state[0], img), apply_hom(state[1], img))
        if (len(cand[0]) + len(cand[1]), _key(cand[0]), _key(cand[1])) < (len(best[0]) + len(best[1]), _key(best[0]), _key(best[1])):
            best, best_img = cand, img
    return best, best_img


class Budget(Exception):
    pass


# --------------------------------------------------------------------------- words
def syllables(word):
    """Cyclic syllable list [(generator, signed exponent), ...] with the seam merged."""
    out = []
    for c in word:
        g = c.lower()
        e = 1 if c.islower() else -1
        if out and out[-1][0] == g:
            out[-1][1] += e
        else:
            out.append([g, e])
    if len(out) > 1 and out[0][0] == out[-1][0]:
        out[0][1] += out[-1][1]
        out.pop()
    return [(g, e) for g, e in out]


def power(g, e):
    return (g if e > 0 else g.upper()) * abs(e)


def from_syllables(syl):
    return ''.join(power(g, e) for g, e in syl)


def is_terminal(state):
    a, b = state
    return len(a) == 1 and len(b) == 1 and a.lower() != b.lower()


def total_length(state):
    return len(state[0]) + len(state[1])


def features(state):
    """(L, S, MK) with the repository's rotation-invariant definitions."""
    runs = [syllables(w) for w in state]
    L = total_length(state)
    nx = ny = sx = sy = 0
    knots = []
    for syl in runs:
        kx = sum(1 for g, _ in syl if g == 'x')
        ky = len(syl) - kx
        knots.append(0 if kx == 0 or ky == 0 else max(kx, ky))
        nx += kx
        ny += ky
        sx += sum(abs(e) for g, e in syl if g == 'x')
        sy += sum(abs(e) for g, e in syl if g == 'y')
    if nx == 0 or ny == 0:
        smb = (sx / nx) if nx else ((sy / ny) if ny else 0.0)
    else:
        smb = min(sx / nx, sy / ny)
    return L, smb, max(knots)


def score_s20(state):
    L, S, MK = features(state)
    return L + 20.0 * S + 2.0 * MK


def score_length(state):
    return float(total_length(state))


SCORES = {'length': score_length, 's20': score_s20}


def _ordered(a, b):
    """The canonical pair of two already-canonical relators (the repository's order)."""
    return (a, b) if (len(a), _key(a)) <= (len(b), _key(b)) else (b, a)


def children(state):
    """All seam-cancelling rotation products, canonical, with their moves (no dedup)."""
    out = []
    r1, r2 = state
    for target in (1, 2):
        ri, rj = (r1, r2) if target == 1 else (r2, r1)
        for jsign in (1, -1):
            oj = rj if jsign == 1 else inv(rj)
            n = len(oj)
            by_first = {}
            for k2 in range(n):
                b = oj[-k2:] + oj[:-k2] if k2 else oj
                by_first.setdefault(b[0], []).append((k2, b))
            for k1 in range(len(ri)):
                a = ri[-k1:] + ri[:-k1] if k1 else ri
                for k2, b in by_first.get(a[-1].swapcase(), ()):
                    piece = canon_rel(a + b)
                    child = _ordered(piece, r2) if target == 1 else _ordered(r1, piece)
                    out.append((child, (target, jsign, k1, k2)))
    return out


# --------------------------------------------------------------------------- the run
class Run:
    """A certificate under construction: the state, the path, the work units."""

    def __init__(self, pair, budget):
        self.budget = budget
        self.units = 0
        self.evaluations = 0
        self.state = canon_pair(*pair)
        self.states = [list(self.state)]
        self.steps = []
        self.stages = []

    def charge(self, n=1):
        self.units += n
        if self.units > self.budget:
            raise Budget()

    def mark(self):
        return len(self.steps), self.state

    def rollback(self, mark):
        n, state = mark
        del self.steps[n:]
        del self.states[n + 1:]
        self.state = state

    def apply_aut(self, img, charge=True):
        if charge:
            self.charge()
        self.state = canon_pair(apply_hom(self.state[0], img), apply_hom(self.state[1], img))
        self.steps.append({'kind': 'automorphism', 'images': dict(img)})
        self.states.append(list(self.state))

    def apply_move(self, move, charge=True):
        if charge:
            self.charge()
        self.state = replay_move(self.state, move)
        self.steps.append({'kind': 'substitution', 'move': '_'.join(map(str, move))})
        self.states.append(list(self.state))

    def find_move(self, target_index, desired):
        """The (target, jsign, k1, k2) whose product turns relator target_index into
        the cyclic word `desired` (the other relator untouched), found by scanning the
        seam-cancelling rotation products of the current words; None if there is none."""
        r1, r2 = self.state
        want = canon_pair(desired, r2) if target_index == 0 else canon_pair(r1, desired)
        ri, rj = (r1, r2) if target_index == 0 else (r2, r1)
        for jsign in (1, -1):
            oj = rj if jsign == 1 else inv(rj)
            for k1 in range(len(ri)):
                a = rot(ri, k1)
                last = a[-1].swapcase()
                for k2 in range(len(oj)):
                    if rot(oj, k2)[0] != last:
                        continue
                    move = (target_index + 1, jsign, k1, k2)
                    if replay_move(self.state, move) == want:
                        return move
        return None

    def rewrite(self, target_index, desired):
        move = self.find_move(target_index, desired)
        if move is None:
            raise AssertionError('rewrite is not a single rotation product')
        self.apply_move(move)


# --------------------------------------------------------------------------- stage A
def stage_pair_descent(run):
    """Apply, while one exists, the Nielsen map that most reduces the total cyclic length."""
    accepted = 0
    while True:
        best = None
        for img in NIELSEN:
            run.charge()
            run.evaluations += 1
            cand = canon_pair(apply_hom(run.state[0], img), apply_hom(run.state[1], img))
            gain = total_length(run.state) - total_length(cand)
            if gain > 0 and (best is None or gain > best[0]):
                best = (gain, img)
        if best is None:
            return accepted
        run.apply_aut(best[1])
        accepted += 1


# --------------------------------------------------------------------------- stage B
def _relator_descent(run, index):
    """Strictly shorten relator `index` with Nielsen maps, carrying the companion.
    Returns the index of the tracked relator in the current state, or None if it stalls
    above length 1."""
    donor = run.state[index]
    while len(donor) > 1:
        best = None
        for img in NIELSEN:
            run.charge()
            run.evaluations += 1
            cand = canon_rel(apply_hom(donor, img))
            if len(cand) < len(donor) and (best is None or (len(cand), _key(cand)) < best[0]):
                best = ((len(cand), _key(cand)), img, cand)
        if best is None:
            return None
        run.apply_aut(best[1])
        donor = best[2]
        if donor not in run.state:
            raise AssertionError('tracked donor absent after an accepted map')
    return run.state.index(donor)


def _key(word):
    return [_ORDER[c] for c in word]


def _delete_letters(run, donor_index):
    """The donor is one letter g; delete every g^{+-1} of the companion by one product each."""
    g = run.state[donor_index]
    if len(g) != 1:
        raise AssertionError('deletion needs a one-letter donor')
    while True:
        r1, r2 = run.state
        donor_index = 0 if r1 == g else 1 if r2 == g else None
        if donor_index is None:
            raise AssertionError('one-letter donor lost')
        comp_index = 1 - donor_index
        comp = run.state[comp_index]
        if g.lower() not in comp.lower():
            break
        k1 = next(k for k in range(len(comp)) if rot(comp, k)[-1].lower() == g.lower())
        letter = rot(comp, k1)[-1]
        jsign = 1 if g == letter.swapcase() else -1
        run.apply_move((comp_index + 1, jsign, k1, 0))
    return is_terminal(run.state)


def stage_primitive(run, index):
    """True when relator `index` is primitive and the pair has been finished from it."""
    mark = run.mark()
    donor_index = _relator_descent(run, index)
    if donor_index is None:
        run.rollback(mark)
        return False
    if _delete_letters(run, donor_index):
        return True
    run.rollback(mark)          # abelianisation obstruction: not a trivial-group pair
    return False


def one_occurrence(word):
    lower = word.lower()
    return lower.count('x') == 1 or lower.count('y') == 1


# --------------------------------------------------------------------------- stage C
def conjugation_forms(word):
    """Every reading of the cyclic word as g^a h^p g^-a h^q with a > 0 and p, q != 0."""
    syl = syllables(word)
    if len(syl) != 4:
        return []
    forms = []
    for off in range(4):
        g, a = syl[off]
        h, p = syl[(off + 1) % 4]
        g2, b = syl[(off + 2) % 4]
        h2, q = syl[(off + 3) % 4]
        if g == g2 and h == h2 and a > 0 and a + b == 0:
            forms.append((g, a, h, p, q))
    return forms


def _bracket(syl, g, a, p, q):
    """First cyclically adjacent pair of g-syllables (e1, m, e2) of opposite sign, both of
    size >= a, whose enclosed h-exponent m is a nonzero multiple of p (e1 > 0) or q (e1 < 0).
    Returns (position of e1, divisor) or None.  Positions index the syllable list."""
    n = len(syl)
    for i in range(n):
        if syl[i][0] != g:
            continue
        j = (i + 2) % n
        if n < 4 or syl[j][0] != g or syl[(i + 1) % n][0] == g:
            continue
        e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[j][1]
        if e1 * e2 >= 0 or abs(e1) < a or abs(e2) < a:
            continue
        d = p if e1 > 0 else q
        if m % d == 0:
            return i, d
    return None


def _pinch_once(syl, i, g, a, h, p, q):
    """One rule use on the bracket at syllable i: returns the new syllable list.

    Rules of R = g^a h^p g^-a h^q:  (i) g^a h^p -> h^-q g^a,  (ii) g^-a h^-q -> h^p g^-a,
    (iii) h^-p g^-a -> g^-a h^q,  (iv) h^q g^a -> g^a h^-p.  A bracket g^e1 h^m g^e2 with
    e1 > 0 uses (i) at its left end when m has the sign of p and (iii) at its right end
    otherwise; with e1 < 0 it uses (ii) when m has the sign of -q and (iv) otherwise."""
    n = len(syl)
    e1, m, e2 = syl[i][1], syl[(i + 1) % n][1], syl[(i + 2) % n][1]
    if e1 > 0:
        left = (m > 0) == (p > 0)
        if left:
            new_mid = [(g, e1 - a), (h, -q), (g, a), (h, m - p)]
        else:
            new_mid = [(g, e1), (h, m + p), (g, -a), (h, q), (g, e2 + a)]
    else:
        left = (m > 0) == (q < 0)
        if left:
            new_mid = [(g, e1 + a), (h, p), (g, -a), (h, m + q)]
        else:
            new_mid = [(g, e1), (h, m - q), (g, a), (h, -p), (g, e2 - a)]
    first = 2 if left else 3
    rest = [syl[(i + k) % n] for k in range(first, n)]
    return _merge(new_mid + rest)


def _merge(syl):
    out = []
    for g, e in syl:
        if e == 0:
            continue
        if out and out[-1][0] == g:
            out[-1] = (g, out[-1][1] + e)
            if out[-1][1] == 0:
                out.pop()
        else:
            out.append((g, e))
    while len(out) > 1 and out[0][0] == out[-1][0]:
        g, e = out[0]
        out[0] = (g, e + out[-1][1])
        out.pop()
        if out[0][1] == 0:
            out.pop(0)
    return out


def pinch_preflight(form, companion, max_rules=400):
    """Simulate the pinch cascade on syllables; returns the number of rule uses when the
    companion reaches one g-syllable or fewer and is then primitive, else None."""
    g, a, h, p, q = form
    syl = syllables(companion)
    rules = 0
    while sum(1 for s in syl if s[0] == g) > 1:
        b = _bracket(syl, g, a, p, q)
        if b is None:
            return None
        syl = _pinch_once(syl, b[0], g, a, h, p, q)
        rules += 1
        if rules > max_rules:
            return None
    if len(syl) == 2 and (abs(syl[0][1]) == 1 or abs(syl[1][1]) == 1):
        return rules
    if len(syl) == 1 and abs(syl[0][1]) == 1:
        return rules
    return None


def stage_pinch(run, donor_index, form):
    """Execute the cascade certified by `pinch_preflight`; True when the pair is finished."""
    g, a, h, p, q = form
    mark = run.mark()
    donor = run.state[donor_index]
    try:
        while True:
            comp_index = 1 - run.state.index(donor)
            comp = run.state[comp_index]
            syl = syllables(comp)
            if sum(1 for s in syl if s[0] == g) <= 1:
                break
            b = _bracket(syl, g, a, p, q)
            if b is None:
                run.rollback(mark)
                return False
            new = from_syllables(_pinch_once(syl, b[0], g, a, h, p, q))
            run.rewrite(comp_index, new)
        comp_index = 1 - run.state.index(donor)
        if stage_primitive(run, comp_index):
            return True
    except Budget:
        raise
    run.rollback(mark)
    return False


def try_pinch_gates(run):
    """Every relator with a conjugation form whose preflight succeeds is executed."""
    for index in range(2):
        for form in conjugation_forms(run.state[index]):
            if pinch_preflight(form, run.state[1 - index]) is None:
                continue
            if stage_pinch(run, index, form):
                return True
    return False


def gate_applicable(state):
    """Free structural preflight: does some certified finishing procedure apply here?"""
    if is_terminal(state):
        return True
    for index in range(2):
        if one_occurrence(state[index]):
            return True
        for form in conjugation_forms(state[index]):
            if pinch_preflight(form, state[1 - index]) is not None:
                return True
    return False


def run_gates(run):
    if is_terminal(run.state):
        return True
    for index in range(2):
        if one_occurrence(run.state[index]) and stage_primitive(run, index):
            return True
    return try_pinch_gates(run)


# --------------------------------------------------------------------------- stage D
def stage_beam(run, width, score, gates=True, max_levels=None, ancestors=0):
    """Level-synchronous beam descent with no closed set.  Each level expands at most
    `width` states (one unit each), sorts the children by (score, state), tries the
    finishing gates on every distinct child in that order (free preflight, charged
    execution) and keeps the best `width` distinct children for the next level.  The
    path is a chain of parent references."""
    root = (run.state, None, None)          # (state, parent node, move)
    level = [root]
    levels = 0
    while level:
        levels += 1
        if max_levels is not None and levels > max_levels:
            return False
        generated = []
        for node in level:
            run.charge()
            for child, move in children(node[0]):
                if ancestors and _on_ancestors(child, node, ancestors):
                    continue
                generated.append((score(child), child, move, node))
        generated.sort(key=lambda t: (t[0], t[1]))
        distinct = []
        previous = None
        for item in generated:
            if item[1] == previous:
                continue
            previous = item[1]
            distinct.append(item)
        if not distinct:
            return False
        for _, child, move, parent in distinct:
            node = (child, parent, move)
            if gates:
                if not gate_applicable(child):
                    continue
                mark = run.mark()
                _commit_path(run, node)
                if run_gates(run):
                    return True
                run.rollback(mark)
            elif is_terminal(child):
                _commit_path(run, node)
                return True
        level = [(child, parent, move) for _, child, move, parent in distinct[:width]]
    return False


def _commit_path(run, node):
    chain = []
    while node[1] is not None:
        chain.append(node)
        node = node[1]
    for state, parent, step in reversed(chain):
        perm = None
        if isinstance(step, tuple) and len(step) == 2 and isinstance(step[1], (dict, type(None))):
            step, perm = step
        if isinstance(step, dict):
            run.apply_aut(step, charge=False)
        else:
            run.apply_move(step, charge=False)
        if perm is not None:
            run.apply_aut(perm, charge=False)
        if run.state != state:
            raise AssertionError('search child does not replay')


def nielsen_children(state):
    """The four Nielsen images of the pair, as (child, images) — automorphism edges."""
    out = []
    for img in NIELSEN:
        out.append((canon_pair(apply_hom(state[0], img), apply_hom(state[1], img)), img))
    return out


def _on_ancestors(child, node, depth):
    """True when `child` equals one of the last `depth` states on the chain ending at node."""
    while depth > 0 and node is not None:
        if node[0] == child:
            return True
        node = node[1]
        depth -= 1
    return False


def stage_bestfirst(run, score, gates=True, ancestors=0, closed_set=False, frontier_dedup=False,
                    nielsen=False, perms=False):
    """Best-first descent.  The default keeps NO closed set: a state reached by several
    routes is pushed (and may be popped) several times; the only memory is the chain of
    parent references.  Options, all comparison-based unless marked:

      ancestors=k       skip a child equal to one of its k nearest ancestors (k large =
                        the whole chain; a cycle check, not a visited set);
      frontier_dedup    keep the open list as a sorted array (bisect) and drop a child
                        already waiting in it; a popped state is forgotten;
      closed_set='sorted'   remember every generated state in a sorted array searched
                        by bisection (memory, but no hashing);
      closed_set='hash' the ordinary hashed visited set: the CONTROL, not the method.
    """
    import bisect
    import heapq
    root = (run.state, None, None)
    counter = 0
    if closed_set == 'hash':
        seen = {run.state}
    elif closed_set == 'sorted':
        seen = [run.state]
    elif closed_set:
        raise ValueError(closed_set)
    if frontier_dedup:
        # ascending by (-score, state): the minimum score sits at the END (O(1) pop)
        frontier = [((-score(run.state), run.state), 0, root)]
    else:
        heap = [(score(run.state), 0, 0, root)]
    while True:
        if frontier_dedup:
            if not frontier:
                return False
            (_, _), depth, node = frontier.pop()
        else:
            if not heap:
                return False
            _, depth, _, node = heapq.heappop(heap)
        run.charge()
        edges = children(node[0])
        if nielsen:
            edges = edges + nielsen_children(node[0])
        if perms:
            relabelled = []
            for child, move in edges:
                rep, img = perm_canonical(child)
                relabelled.append((rep, (move, img)))
            edges = relabelled
        for child, move in edges:
            if ancestors and _on_ancestors(child, node, ancestors):
                continue
            if closed_set == 'hash':
                if child in seen:
                    continue
                seen.add(child)
            elif closed_set == 'sorted':
                i = bisect.bisect_left(seen, child)
                if i < len(seen) and seen[i] == child:
                    continue
                seen.insert(i, child)
            cnode = (child, node, move)
            if gates:
                if gate_applicable(child):
                    mark = run.mark()
                    _commit_path(run, cnode)
                    if run_gates(run):
                        return True
                    run.rollback(mark)
            elif is_terminal(child):
                _commit_path(run, cnode)
                return True
            counter += 1
            if frontier_dedup:
                key = (-score(child), child)
                i = bisect.bisect_left(frontier, key, key=lambda t: t[0])
                if i < len(frontier) and frontier[i][0] == key:
                    continue
                frontier.insert(i, (key, depth + 1, cnode))
            else:
                heapq.heappush(heap, (score(child), depth + 1, counter, cnode))


# --------------------------------------------------------------------------- solve
def solve(pair, budget=1000, width=8, score='s20', gates=True, pair_descent=True,
          engine='beam', ancestors=0, closed_set=False, frontier_dedup=False, nielsen=False,
          perms=False):
    """Return dict(solved, units, steps, states, stage, ...)."""
    run = Run(pair, budget)
    scorer = SCORES[score]
    outcome = None
    try:
        if is_terminal(run.state):
            outcome = 'terminal'
        if outcome is None and pair_descent:
            n = stage_pair_descent(run)
            run.stages.append(('A', n, run.units))
            if is_terminal(run.state):
                outcome = 'A'
        if outcome is None:
            for index in range(2):
                if stage_primitive(run, index):
                    outcome = 'B'
                    break
            run.stages.append(('B', outcome == 'B', run.units))
        if outcome is None and try_pinch_gates(run):
            outcome = 'C'
        if outcome is None:
            run.stages.append(('C', False, run.units))
            if engine == 'beam':
                found = stage_beam(run, width, scorer, gates, ancestors=ancestors)
            elif engine == 'bestfirst':
                found = stage_bestfirst(run, scorer, gates, ancestors, closed_set, frontier_dedup, nielsen, perms)
            else:
                raise ValueError(engine)
            if found:
                outcome = 'D'
            run.stages.append(('D', outcome == 'D', run.units))
    except Budget:
        outcome = None
    solved = outcome is not None and is_terminal(run.state)
    return dict(solved=solved, stage=outcome if solved else None,
                units=min(run.units, budget) if solved else budget,
                units_raw=run.units, evaluations=run.evaluations,
                steps=run.steps if solved else [], states=run.states if solved else [],
                path_length=len(run.steps) if solved else None,
                max_relator=max((len(w) for s in run.states for w in s), default=0) if solved else None,
                stages=run.stages, params=dict(budget=budget, width=width, score=score, gates=gates,
                                               engine=engine, ancestors=ancestors, closed_set=closed_set,
                                               frontier_dedup=frontier_dedup, nielsen=nielsen, perms=perms))
