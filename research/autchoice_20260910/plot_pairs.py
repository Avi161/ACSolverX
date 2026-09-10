"""Reproduce "The same AC moves, seen from both starting points" for the 40 committed pairs.

Inputs are read with ``git show`` at the leftover-branch commit ``dab82a84`` (never copied
into the tree; their sha256s go into the JSON):

    unsolved_10m_orig_baseline.csv     name, r1, r2, orbit, rep_r1, rep_r2   (40 originals)
    ac19_orig_10m_greedy_b10000000_mrl64.jsonl   the originals' plain-greedy certificates
                                       at 10M / cap 64: nodes_explored, path (states), path_moves

For every pair the panel shows three series of total relator length:

    blue          along the original's certificate ``path`` (checked: replaying ``path_moves``
                  through ``words.replay_move`` reproduces every state)
    orange        the SAME states mapped through ``phi``, the automorphism that sends the
                  original to its aut-min representative -- since AC moves commute with
                  automorphisms this is a genuine AC path from the representative to the
                  basis pair ``(phi(x), phi(y))``
    dashed tail   an AC-move descent from ``(phi(x), phi(y))`` to ``(x, y)``: the greedy
                  strict-length descent of ``orbit.greedy_descent`` (Nielsen moves on a
                  basis pair); if that stalls, the plain greedy engine's certificate at 10k
                  pops is used instead and the panel says so.  Annotated ``+k`` = its length
                  in moves.

``phi`` comes from ``autcanon.peak_reduce`` + ``level_min``; it is checked to land on the
committed ``rep_r1, rep_r2`` exactly (composed with the signed permutation that matches,
if the level-set lex-min differs by one); if it does not, the radius-3 ball of the original
is searched for the rep.  Every panel carries the original's node count and phi.

    PYTHONPATH=. python3 -m research.autchoice_20260910.plot_pairs
        -> pairs_length_profiles.png, pairs_length_profiles.json
"""
import csv
import hashlib
import io
import json
import math
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import check, compose, level_min, peak_reduce  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom, apply_pair, canon_pair, relabel_key, replay_move,
)
from research.autchoice_20260910.engine import cost, is_trivial  # noqa: E402
from research.autchoice_20260910.orbit import ball, find_relabel, greedy_descent  # noqa: E402

HERE = Path(__file__).resolve().parent
LEFTOVER = 'dab82a8412b007f23cffd35bee2727d977510de0'
PAIRS_CSV = 'results/heuristic_search/ac19_autmin_screen/unsolved_10m_orig_baseline.csv'
CERTS = 'results/heuristic_search/ac19_orig_10m/ac19_orig_10m_greedy_b10000000_mrl64.jsonl'


def git_show(path):
    data = subprocess.run(['git', 'show', f'{LEFTOVER}:{path}'], cwd=ROOT, capture_output=True,
                          check=True).stdout
    return data, hashlib.sha256(data).hexdigest()


def total(pair):
    return len(pair[0]) + len(pair[1])


def map_state(state, phi):
    return canon_pair(apply_hom(state[0], phi), apply_hom(state[1], phi))


def phi_to_rep(orig, rep):
    """An automorphism with canon_pair(phi(orig)) == rep exactly, and how it was found."""
    _, red, phi = peak_reduce(orig)
    lm_rep, phi = level_min(red, phi)
    img = map_state(orig, phi)
    if img == rep:
        return phi, 'peak_reduce+level_min'
    sigma = find_relabel(img, rep)
    if sigma is not None:
        phi = compose(sigma, phi)
        assert map_state(orig, phi) == rep
        return phi, 'peak_reduce+level_min+relabel'
    for node in ball(orig, 3, cap=64):
        if relabel_key((node['r1'], node['r2'])) == relabel_key(rep):
            sigma = find_relabel((node['r1'], node['r2']), rep)
            phi = compose(sigma, node['phi'])
            assert map_state(orig, phi) == rep
            return phi, f'ball3 seq={node["seq"]}'
    raise RuntimeError(f'no automorphism found from {orig} to {rep}')


def tail_from_basis(basis):
    """AC-move descent from the basis pair to (x, y): (states, method)."""
    states, moves = greedy_descent(basis)
    if is_trivial(states[-1]):
        return states, 'greedy_descent'
    r = cost(basis, 10000, cap=64, config=None)
    if not r['solved']:
        return states, 'greedy_descent(stalled)'
    st = [canon_pair(*basis)]
    for m in r['path_moves']:
        st.append(replay_move(st[-1], tuple(int(v) for v in m.split('_'))))
    assert is_trivial(st[-1])
    return st, f'engine_greedy@{r["nodes"]}'


def build_series():
    pairs_blob, pairs_sha = git_show(PAIRS_CSV)
    certs_blob, certs_sha = git_show(CERTS)
    pairs = list(csv.DictReader(io.StringIO(pairs_blob.decode())))
    certs = {}
    for line in certs_blob.decode().splitlines():
        if line.strip():
            d = json.loads(line)
            certs[d['name']] = d
    series = []
    for p in sorted(pairs, key=lambda r: (r['orbit'], r['name'])):
        c = certs[p['name']]
        orig = canon_pair(p['r1'], p['r2'])
        rep = canon_pair(p['rep_r1'], p['rep_r2'])
        assert c['solved'] and orig == canon_pair(c['r1'], c['r2'])
        path = [tuple(s) for s in c['path']]
        st = orig
        assert st == path[0]
        for i, m in enumerate(c['path_moves']):
            st = replay_move(st, tuple(int(v) for v in m.split('_')))
            assert st == path[i + 1], (p['name'], i)
        assert is_trivial(st)
        phi, how = phi_to_rep(orig, rep)
        assert check(orig, rep, phi)
        mapped = [map_state(s, phi) for s in path]
        assert mapped[0] == rep
        basis = mapped[-1]
        assert basis == canon_pair(phi['x'], phi['y'])
        tail, method = tail_from_basis(basis)
        series.append({
            'name': p['name'], 'orbit': p['orbit'], 'orig': list(orig), 'rep': list(rep),
            'nodes': int(c['nodes_explored']), 'phi': phi, 'phi_found_by': how,
            'orig_lengths': [total(s) for s in path],
            'mapped_lengths': [total(s) for s in mapped],
            'mapped_states': [list(s) for s in mapped],
            'tail_lengths': [total(s) for s in tail], 'tail_method': method,
            'tail_moves': len(tail) - 1,
        })
        print(f"{p['name']:>13} {p['orbit']:>11} nodes={c['nodes_explored']:>9} moves={len(path) - 1:>3} "
              f"orig peak {max(series[-1]['orig_lengths'])} rep-side peak "
              f"{max(series[-1]['mapped_lengths'])} tail +{series[-1]['tail_moves']} ({method}; phi by {how})",
              flush=True)
    return series, {'pairs_csv': pairs_sha, 'certs_jsonl': certs_sha}


def plot(series, out_png):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    n = len(series)
    ncol = 5
    nrow = math.ceil(n / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.6 * ncol, 2.6 * nrow), sharey=False)
    axes = axes.ravel()
    for ax, s in zip(axes, series):
        k = len(s['orig_lengths'])
        ax.plot(range(k), s['orig_lengths'], color='tab:blue', lw=1.4,
                label='original (blue)')
        ax.plot(range(k), s['mapped_lengths'], color='tab:orange', lw=1.4,
                label='rep = phi(original)')
        t = s['tail_lengths']
        ax.plot(range(k - 1, k - 1 + len(t)), t, color='tab:orange', lw=1.2, ls='--')
        ax.annotate(f"+{s['tail_moves']}", (k - 1 + len(t) - 1, t[-1]), textcoords='offset points',
                    xytext=(-2, 6), fontsize=7, color='tab:orange', ha='right')
        ax.set_title(f"{s['name']} -> {s['orbit']}", fontsize=8)
        ax.text(0.02, 0.96, f"{s['nodes']:,} nodes\nrep peak {max(s['mapped_lengths'])}, "
                f"orig peak {max(s['orig_lengths'])}", transform=ax.transAxes, fontsize=6.5,
                va='top')
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.25)
    for ax in axes[n:]:
        ax.axis('off')
    axes[0].legend(fontsize=6.5, loc='upper right')
    fig.suptitle('The same AC moves, seen from both starting points: total relator length along the '
                 "original's 10M-greedy certificate (blue) and along its image under phi, starting at "
                 'the aut-min representative (orange; dashed = descent from (phi(x), phi(y)) to (x, y))',
                 fontsize=9)
    fig.supxlabel('AC move index', fontsize=8)
    fig.supylabel('total relator length', fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_png, dpi=130)


def main():
    series, shas = build_series()
    json.dump({'source_commit': LEFTOVER, 'inputs': {PAIRS_CSV: shas['pairs_csv'], CERTS: shas['certs_jsonl']},
               'pairs': series}, open(HERE / 'pairs_length_profiles.json', 'w'), indent=1)
    plot(series, HERE / 'pairs_length_profiles.png')
    from statistics import median
    peaks_o = [max(s['orig_lengths']) - s['orig_lengths'][0] for s in series]
    peaks_r = [max(s['mapped_lengths']) - s['mapped_lengths'][0] for s in series]
    over48 = sum(1 for s in series if max(s['mapped_lengths']) > 48)
    over64 = sum(1 for s in series if max(s['mapped_lengths']) > 64)
    print(f'{len(series)} pairs; hump above start: original median {median(peaks_o)}, rep-side median '
          f'{median(peaks_r)}; peak total length median original {median(max(s["orig_lengths"]) for s in series)}, '
          f'rep-side {median(max(s["mapped_lengths"]) for s in series)}; rep-side peak above cap 48 on {over48}/{len(series)} '
          f'pairs, above 64 on {over64}; tail methods {sorted({s["tail_method"].split("@")[0] for s in series})}')


if __name__ == '__main__':
    main()
