"""Machine checks for FAMILY_THEORY.md.

Everything this script prints as ``ok`` is re-derived here, not quoted from the
document.  Certificates are checked twice: once by replaying every stored state
with ``experiments/equivalence_classes/lib/words`` (``replay_move`` /
``apply_pair``), and once by decoding the mixed path to elementary AC moves with
``certificate_decoder_compact_moves.decode_elementary`` and replaying *those*
with ``certificate_decoder.replay_elementary``, requiring the literal terminal
``['x', 'y']`` -- the census's own contract.

    PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py
        A  orbit keys and the well-definedness of the families
        B  the W-move algebra (Lemma W1)
        C  Rule W-TRANSPORT: build and replay a certificate for every residual
           row whose R-preserving ball reaches a solved census row
        D  the bounded refutation: every ball, everything it meets, and the
           R-preserving components of the residual (C and D share one survey)
        F  the Magnus frames of the 19 family relators
        G  the gate audit behind Observation W6

    PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py --corpus
        + section E: Rule TRAIL -- the certificate-corpus terminal, run over the
          41 unsolved census rows (needs tables/ball_cap12_aut and ~1.5 GB)

    PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py --all
    PYTHONPATH=. python3 research/residual_20260909/theory/FAMILY_verify.py --all --matrix
        --matrix makes section E run the whole FAMILY_DATA.md section 8 table
        (two tables x four arms x two budgets; about 10 minutes on one thread)
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

for _var in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_var, '1')

sys.path.insert(0, str(Path(__file__).resolve().parent))

from experiments.search.heuristic_1k import pack as _pack
from experiments.equivalence_classes.lib.words import (
    SIGNED_PERMS, apply_hom, apply_pair, canon_pair, canon_rel, cyc_reduce,
    exp_sums, free_reduce, inv, relabel_key, replay_move, rot,
)
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary

import FAMILY_mine as FM

HERE = Path(__file__).resolve().parent
OUT = HERE / 'FAMILY_verify.json'
W_SLACK = 4          # the R-preserving ball's length allowance over the root
W_DEPTH = 4          # and its depth


# ---------------------------------------------------------------------------
# A. orbit keys and families
# ---------------------------------------------------------------------------
def section_a():
    """``orbit_key`` is constant on the rotation / inversion / signed-permutation
    orbit and separates the 19 residual families."""
    census = FM.load_census()
    unsolved = FM.load_unsolved()
    words = [row['r1'] for row in unsolved] + [row['r2'] for row in unsolved]
    words += [row['r1'] for row in census[::997]]
    failures = []
    for word in words:
        key = FM.orbit_key(word)
        for _label, img in SIGNED_PERMS:
            image = apply_hom(word, img)
            for variant in (image, inv(image)):
                for k in range(len(variant)):
                    if FM.orbit_key(rot(cyc_reduce(variant), k)) != key:
                        failures.append((word, _label, k))
    families = {FM.orbit_key(row['r1']) for row in unsolved}
    result = dict(words_checked=len(words), symmetry_images_per_word='8 perms x 2 x |R| rotations',
                  failures=len(failures), families=len(families))
    print(f"A. orbit key invariance: {len(words)} words x 8 signed permutations x "
          f"inversion x every rotation -> {len(failures)} failures; "
          f"{len(families)} distinct residual families")
    assert not failures
    return result


# ---------------------------------------------------------------------------
# B. the W-move (R-preserving move) algebra
# ---------------------------------------------------------------------------
def section_b():
    """Lemma W1.  An R-preserving Definition 2.1 move sends the companion to

        W'  =  rot_{k1}(W) . rot_{k2}(R^s)  =  (C W C^-1) . (B R^s B^-1)

    with ``C`` the length-``k1`` suffix of ``W`` and ``B`` the length-``k2``
    suffix of ``R^s``; both factors are explicit conjugates, so ``[W']`` and
    ``[W]`` are conjugate in ``G = <x, y | R>``.
    """
    unsolved = FM.load_unsolved()
    checked = rot_id = 0
    failures = []
    for row in unsolved:
        pair = canon_pair(row['r1'], row['r2'])
        cap = max(map(len, pair)) + W_SLACK
        for target in (1, 2):
            companion, donor = pair[target - 1], pair[2 - target]
            for jsign in (1, -1):
                signed = donor if jsign == 1 else inv(donor)
                for k1 in range(len(companion)):
                    tail = companion[len(companion) - k1:] if k1 else ''
                    if free_reduce(rot(companion, k1)) != free_reduce(tail + companion + inv(tail)):
                        failures.append(('W-conjugate', row['name'], k1))
                    rot_id += 1
                    for k2 in range(len(signed)):
                        stem = signed[len(signed) - k2:] if k2 else ''
                        if free_reduce(rot(signed, k2)) != free_reduce(stem + signed + inv(stem)):
                            failures.append(('R-conjugate', row['name'], k2))
                        child = replay_move(pair, (target, jsign, k1, k2))
                        if canon_rel(donor) not in child or max(map(len, child)) > cap:
                            continue
                        checked += 1
                        # the engine's child is the canonicalisation of that product
                        product = canon_rel(rot(companion, k1) + rot(signed, k2))
                        if canon_pair(donor, product) != child:
                            failures.append(('product', row['name'], (target, jsign, k1, k2)))
                        # and the product is (conj of W) * (conj of R^s) letter for letter
                        tailc = companion[len(companion) - k1:] if k1 else ''
                        stemc = signed[len(signed) - k2:] if k2 else ''
                        lhs = free_reduce(rot(companion, k1) + rot(signed, k2))
                        rhs = free_reduce(tailc + companion + inv(tailc)
                                          + stemc + signed + inv(stemc))
                        if lhs != rhs:
                            failures.append(('factorisation', row['name'], (target, jsign, k1, k2)))
    print(f'B. W-move algebra: {rot_id} rotation-as-conjugation identities and '
          f'{checked} R-preserving children of the 41 roots -> {len(failures)} failures')
    assert not failures
    return dict(rotation_identities=rot_id, r_preserving_children=checked, failures=len(failures))


# ---------------------------------------------------------------------------
# C / D. the R-preserving survey, Rule W-TRANSPORT, and the bounded refutation
# ---------------------------------------------------------------------------
def w_survey(slack=W_SLACK, depth=W_DEPTH, verbose=True):
    """One R-preserving BFS per residual row.

    For each of the 41 rows: expand the ball of canonical pairs reachable by
    Definition 2.1 moves that never touch one relator, with every relator kept
    at ``root max + slack`` and at most ``depth`` moves; record which census
    rows (solved or unsolved) the ball meets, and the move sequence that gets
    there.  Returns ``{name: {...}}``.
    """
    census = FM.load_census()
    unsolved = FM.load_unsolved()
    unsolved_names = {row['name'] for row in unsolved}
    keys = {}
    for row in census:
        keys.setdefault(relabel_key((row['r1'], row['r2'])), row['name'])
    survey = {}
    for row in unsolved:
        started = time.time()
        pair = canon_pair(row['r1'], row['r2'])
        cap = max(map(len, pair)) + slack
        parent = FM.w_ball(pair, cap, depth)
        met = {}
        for state in parent:
            name = keys.get(relabel_key(state))
            if name is None or name == row['name'] or name in met:
                continue
            states, moves = FM.w_path(parent, state)
            met[name] = dict(hub=list(state), moves=[list(m) for m in moves], depth=len(moves))
        survey[row['name']] = dict(
            pair=list(pair), cap=cap, depth=depth, ball=len(parent),
            solved_met={k: v for k, v in met.items() if k not in unsolved_names},
            unsolved_met={k: v for k, v in met.items() if k in unsolved_names},
            wall=time.time() - started)
        if verbose:
            entry = survey[row['name']]
            print(f"D. {row['name']:12s} |B_W| = {entry['ball']:6d} (cap {cap}, depth {depth})  "
                  f"solved census rows met: {sorted(entry['solved_met']) or '-'}  "
                  f"unsolved met: {sorted(n.replace('ac19_', '') for n in entry['unsolved_met'])}")
    return survey


def transport_chains(survey):
    """Shortest chain of R-preserving hops from each residual row to a row whose
    ball already meets a *solved* census row.  ``[]`` when none exists."""
    seeds = {name for name, entry in survey.items() if entry['solved_met']}
    chains = {}
    for name in survey:
        if name in seeds:
            chains[name] = []
            continue
        seen = {name}
        queue = [(name, [])]
        found = None
        while queue and found is None:
            current, path = queue.pop(0)
            for nxt in sorted(survey[current]['unsolved_met']):
                if nxt in seen:
                    continue
                seen.add(nxt)
                step = path + [(current, nxt)]
                if nxt in seeds:
                    found = step
                    break
                queue.append((nxt, step))
        chains[name] = found
    return chains


def _append_hop(pair, states, steps, state, moves, target_pair):
    """Extend a certificate by the R-preserving ``moves`` and, if needed, the
    signed permutation that lands exactly on ``target_pair``."""
    for move in moves:
        state = replay_move(state, tuple(move))
        states.append(list(state))
        steps.append(dict(kind='substitution', move='_'.join(str(int(v)) for v in move)))
    if tuple(state) != tuple(target_pair):
        images = next((img for _label, img in SIGNED_PERMS
                       if apply_pair(state, img) == tuple(target_pair)), None)
        if images is None:
            raise ValueError(f'no signed permutation carries {state} to {target_pair}')
        state = apply_pair(state, images)
        states.append(list(state))
        steps.append(dict(kind='automorphism', images=images))
    return state


def replay_with_words(pair, states, steps):
    state = canon_pair(*pair)
    if list(state) != states[0]:
        return False
    for i, step in enumerate(steps):
        state = (apply_pair(state, step['images']) if step.get('kind') == 'automorphism'
                 else replay_move(state, tuple(int(v) for v in step['move'].split('_'))))
        if list(state) != states[i + 1]:
            return False
    return True


def section_cd(survey=None, verbose=True):
    unsolved = FM.load_unsolved()
    by_name = {row['name']: row for row in unsolved}
    survey = w_survey(verbose=verbose) if survey is None else survey
    chains = transport_chains(survey)
    sources = {}
    for name, entry in survey.items():
        if entry['solved_met']:
            sources[name] = min(entry['solved_met'].items(), key=lambda kv: kv[1]['depth'])
    records = FM.load_records([src for src, _ in sources.values()])
    results = []
    for name in sorted(survey):
        chain = chains[name]
        if chain is None:
            continue
        row = by_name[name]
        pair = (row['r1'], row['r2'])
        state = canon_pair(*pair)
        states, steps = [list(state)], []
        hops = 0
        try:
            for current, nxt in chain:                       # residual -> residual hops
                hop = survey[current]['unsolved_met'][nxt]
                state = _append_hop(pair, states, steps, state, hop['moves'],
                                    canon_pair(by_name[nxt]['r1'], by_name[nxt]['r2']))
                hops += hop['depth']
            seed = chain[-1][1] if chain else name
            source, hop = sources[seed]
            record = records[source]
            if record.get('elementary_tail'):
                results.append(dict(name=name, skipped='source certificate has a packed tail'))
                continue
            state = _append_hop(pair, states, steps, state, hop['moves'],
                                tuple(record['states'][0]))
            hops += hop['depth']
        except ValueError as exc:
            results.append(dict(name=name, skipped=str(exc)))
            continue
        states += [list(word) for word in record['states'][1:]]
        steps += record['steps']
        words_ok = replay_with_words(pair, states, steps)
        moves = decode_elementary(pair, states, steps, None)
        replayed = replay_elementary(pair, moves)
        verified = sorted(word.lower() for word in replayed) == ['x', 'y']
        results.append(dict(name=name, r_preserving_moves=hops, chain=[list(c) for c in chain],
                            source=source, source_route=record['policy_route'],
                            mixed_steps=len(steps), elementary=len(moves),
                            words_replay=words_ok, terminal=list(replayed), verified=verified))
        if verbose:
            print(f"C. {name:12s} {hops} R-preserving move(s)"
                  f"{' via ' + '->'.join(c[1] for c in chain) if chain else ''} -> {source:12s} "
                  f"({record['policy_route']}); mixed steps {len(steps):3d}; elementary "
                  f"{len(moves):5d}; words-replay {words_ok}; terminal {replayed}")
    good = [r for r in results if r.get('verified')]
    assert all(r.get('verified') for r in results if 'skipped' not in r)
    # components of the residual under the "meets" relation
    parent = {name: name for name in survey}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for name, entry in survey.items():
        for other in entry['unsolved_met']:
            ra, rb = find(name), find(other)
            if ra != rb:
                parent[ra] = rb
    comps = defaultdict(list)
    for name in survey:
        comps[find(name)].append(name)
    comps = sorted((sorted(v) for v in comps.values()), key=lambda v: (-len(v), v))
    print(f'C. Rule W-TRANSPORT certifies {len(good)} / {len(survey)} residual rows '
          f'(R-preserving ball: depth <= {W_DEPTH}, relator cap = root max + {W_SLACK})')
    print(f'D. residual splits into {len(comps)} R-preserving components '
          f'{[len(c) for c in comps]}; '
          f'{sum(1 for e in survey.values() if e["solved_met"])} rows have a solved census '
          f'row in their ball, {sum(1 for e in survey.values() if not e["solved_met"])} do not')
    return dict(certified=[r['name'] for r in good], details=results, components=comps,
                survey={k: {kk: vv for kk, vv in v.items() if kk != 'wall'}
                        for k, v in survey.items()})


# ---------------------------------------------------------------------------
# F. Magnus frames
# ---------------------------------------------------------------------------
def section_f():
    """The Magnus rewriting of every family relator, re-expanded and compared
    with the transported relator, plus the two explicit base groups quoted in
    FAMILY_THEORY.md section 5."""
    unsolved = FM.load_unsolved()
    keys = []
    for row in unsolved:
        key = FM.orbit_key(row['r1'])
        if key not in keys:
            keys.append(key)
    rows, failures = [], []
    for key in keys:
        frame = FM.magnus_frame(key)
        if frame is None:
            rows.append(dict(family=key, frame=None))
            continue
        round_trip = canon_rel(FM.magnus_word(frame)) == canon_rel(frame['relator'])
        if not round_trip:
            failures.append(key)
        once_mu, once_nu = frame['extremes_once']
        kind = ('mapping torus F_%d x| Z' % (frame['nu'] - frame['mu']) if once_mu and once_nu
                else 'ascending HNN of F_%d' % (frame['nu'] - frame['mu']) if once_mu or once_nu
                else 'one-relator base')
        rows.append(dict(family=key, stable=frame['stable'], shear=frame['images'],
                         transported=frame['relator'], mu=frame['mu'], nu=frame['nu'],
                         counts=frame['counts'], kind=kind, round_trip=round_trip))
    # the base of the YXyXYXyxx frame is the trefoil group <b, c | b^3 = c^2>:
    # r* = a^-1 b^-1 a^-1 b^2 with a = x_-1, b = x_0; the free-basis change
    # c = a b (a = c b^-1) carries it to b^3 c^-2.  (a, b) are encoded (x, y).
    trefoil = canon_rel(apply_hom('XYXyy', {'x': 'xY', 'y': 'y'})) == canon_rel('yyyXX')
    # the base of the YXYXyXXYXyX frame is free on y_1..y_5 with
    # y_0 = y_5^-1 y_4 y_2^-1 y_1, which is r* = y_0^-1 y_5^-1 y_4 y_2^-1 y_1 solved for y_0
    frame = FM.magnus_frame('YXYXyXXYXyX')
    shift = (frame['star'] == [(0, -1), (5, -1), (4, 1), (2, -1), (1, 1)])
    print(f'F. Magnus frames: {sum(1 for r in rows if r.get("frame", True) is not None)} of '
          f'{len(rows)} families admit a single-shear frame, all round-trip '
          f'({len(failures)} failures); trefoil base identity {trefoil}; '
          f'F_5 monodromy relator as stated {shift}')
    assert not failures and trefoil and shift
    return dict(frames=rows, trefoil_base=trefoil, f5_star=shift)


# ---------------------------------------------------------------------------
# E. Rule TRAIL -- the certificate-corpus terminal
# ---------------------------------------------------------------------------
def section_g():
    """Observation W6's gate audit: which of the 41 residual roots pass any of
    the census terminal recognisers, and which carry a BS-DEMOTE label."""
    from research.supermoves_20260908.DONOR_NORMALIZED_BS import inspect as donor_inspect
    from research.residual_20260909 import bs_demote_gate
    two_block = one_occurrence = bs_donor = bs_accept = 0
    labels = []
    for row in FM.load_unsolved():
        pair = list(canon_pair(row['r1'], row['r2']))
        gates, _work = donor_inspect(pair)
        two_block += bool(gates['two_block'])
        one_occurrence += bool(gates['one_occurrence_relators'])
        preflight = gates.get('bs_preflight')
        bs_donor += bool(preflight)
        bs_accept += (preflight or {}).get('status') == 'accept'
        label = bs_demote_gate.recognize(tuple(pair))
        if label is not None:
            labels.append((row['name'], list(label), bool(bs_demote_gate.demotable(label))))
    print(f'G. gate audit of the 41 roots: two_block {two_block}, one_occurrence '
          f'{one_occurrence}, consecutive-BS donor recognised {bs_donor}, preflight accept '
          f'{bs_accept}, BS-DEMOTE labels {labels}')
    assert two_block == 0 and one_occurrence == 0 and bs_accept == 0
    assert all(not demotable for _name, _label, demotable in labels)
    return dict(two_block=two_block, one_occurrence=one_occurrence, bs_donor=bs_donor,
                bs_preflight_accept=bs_accept, bs_demote_labels=labels)


def _arms(table):
    """The four search configurations of FAMILY_DATA.md section 8, on ``table``."""
    from research.residual_20260909 import final_policy_ball, mid_search_ball, plain_search_ball

    def cascade(pair, budget):
        return dict(final_policy_ball.search(
            pair, budget=budget, prepass_cap=250, plain_prefix=300,
            certified_overrun=True, use_bs_demote=True, table=table))

    def plain(pair, budget):
        return dict(plain_search_ball.mixed_search(
            pair, 's20', budget=budget, cap=None, s_weight=20., mk_weight=2., w_weight=0.,
            table=table), policy_route='plain_s20')

    def aut_edges(pair, budget):
        return dict(mid_search_ball.mixed_search(
            pair, 'aut_edges', budget=budget, cap=None, w_weight=1.5, s_weight=20.,
            mk_weight=2., use_bs=True, general_bs=True, use_two_block=True,
            probe_when='generated', use_bs_preflight=True, table=table),
            policy_route='aut_edges')

    def ordinary_t(pair, budget):
        return dict(mid_search_ball.mixed_search(
            pair, 's20', budget=budget, cap=None, w_weight=1.5, s_weight=20., mk_weight=2.,
            use_bs=True, general_bs=True, use_two_block=True, probe_when='generated',
            use_bs_preflight=True, bs_escape_weight=4., table=table),
            policy_route='ordinary_T')

    return dict(cascade=cascade, plain=plain, aut_edges=aut_edges, ordinary_T=ordinary_t)


def section_e(budgets=(1000, 5000), matrix=False):
    """Rule TRAIL: build the certificate corpus, layer it over the ball, and run
    the 41 residual rows.  ``matrix=True`` runs the whole
    FAMILY_DATA.md section 8 table (both tables x four arms x two budgets)."""
    from research.residual_20260909.harness import run_row
    ball = FM.load_ball()
    provenance = {}
    started = time.time()
    corpus = FM.build_corpus(FM.iter_records(), base=ball, provenance=provenance)
    print(f'E. corpus: {len(corpus)} certified states outside the cap-12 ball '
          f'(built in {time.time() - started:.0f} s from the published census certificates)')
    unsolved = FM.load_unsolved()
    roots_in_corpus = [row['name'] for row in unsolved
                       if _pack(canon_pair(row['r1'], row['r2'])) in corpus]
    print(f'E. residual roots already inside the corpus: {roots_in_corpus or "none"}')
    assert not roots_in_corpus
    layered = FM.LayeredTable(corpus, ball)
    tables = [('ball+corpus', layered)] if not matrix else [('ball', ball), ('ball+corpus', layered)]
    arms = ('cascade', 'ordinary_T') if not matrix else ('cascade', 'plain', 'aut_edges', 'ordinary_T')
    out = {}
    for table_name, table in tables:
        built = _arms(table)
        for arm in arms:
            fn = built[arm]
            run_row(fn, 'warmup', ('YYXyX', 'YXXyx'), 50)
            for budget in budgets:
                records = [run_row(fn, row['name'], (row['r1'], row['r2']), budget)
                           for row in unsolved]
                solved = [r for r in records if r['solved']]
                assert all(r['verified'] for r in solved)
                key = f'{table_name}/{arm}@{budget}'
                out[key] = dict(
                    solved=len(solved), verified=sum(r['verified'] for r in solved),
                    units=sum(r['nodes_explored'] for r in records),
                    unsolved=[r['name'] for r in records if not r['solved']],
                    per_row={r['name']: r['nodes_explored'] for r in records})
                print(f'E. {key:34s}: {len(solved):2d}/41 solved, all verified, '
                      f"{out[key]['units']:6d} units; unsolved {out[key]['unsolved']}")
    return dict(corpus_states=len(corpus), ball_states=len(ball), runs=out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--corpus', action='store_true', help='also run section E')
    parser.add_argument('--matrix', action='store_true',
                        help='section E runs the full arm x table x budget matrix')
    parser.add_argument('--all', action='store_true', help='run every section')
    args = parser.parse_args(argv)
    report = dict(A=section_a(), B=section_b())
    report['CD'] = section_cd()
    report['F'] = section_f()
    report['G'] = section_g()
    if args.corpus or args.all:
        report['E'] = section_e(matrix=args.matrix)
    with open(OUT, 'w') as stream:
        json.dump(report, stream, indent=1)
    print(f'wrote {OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
