"""ladder100: expansions LENGTH (g) and S20_MK2 (g_S) need on each presentation, by level.

Reads benchmark/ladder/ladder_default.csv; writes ladder100_levels.png in the working directory.
"""
import csv, os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
rows = list(csv.DictReader(open(os.path.join(ROOT, 'benchmark', 'ladder', 'ladder_default.csv'))))
FAIL = 3e7                        # row where a search that fails within 1e7 is drawn
BLUE, ORANGE, INK2 = '#2a78d6', '#eb6834', '#555555'
plt.rcParams.update({'font.family': 'serif', 'font.size': 8})
fig, ax = plt.subplots(figsize=(3.6, 2.9))
for lvl in range(1, 11):
    ax.axvspan(lvl - 0.5, lvl + 0.5, color='#f2f1ee' if lvl % 2 else 'white', zorder=0, lw=0)
for key, ok, off, col, mk, lab in [('greedy_nodes', 'greedy_solved', -0.17, BLUE, 'o', 'LENGTH ($g$)'),
                                   ('s20_nodes', 's20_solved', 0.17, ORANGE, 'D', 'S20_MK2 ($g_S$)')]:
    xs, ys = [], []
    for i, r in enumerate(sorted(rows, key=lambda r: (int(r['level']), r['name']))):
        j = (i % 10 - 4.5) * 0.022
        xs.append(int(r['level']) + off + j)
        ys.append(int(r[key]) if r[ok] == '1' else FAIL)
    ax.scatter(xs, ys, s=11, color=col, marker=mk, edgecolor='white', linewidth=0.4, zorder=3, label=lab)
ax.axhline(1e7, color=INK2, lw=0.6, ls='--', zorder=1)
ax.set_yscale('log'); ax.set_ylim(1, 6e7)
ax.set_yticks([1, 10, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7, FAIL])
ax.set_yticklabels(['$10^0$', '$10^1$', '$10^2$', '$10^3$', '$10^4$', '$10^5$', '$10^6$', '$10^7$', 'unsolved'])
ax.minorticks_off(); ax.set_xlim(0.5, 10.5)
ax.set_xticks(range(1, 11)); ax.set_xlabel('level'); ax.set_ylabel('expansions to solve (log scale)')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.legend(loc='lower right', frameon=True, fontsize=7, handletextpad=0.3, borderpad=0.4)
fig.tight_layout(); fig.savefig('ladder100_levels.png', dpi=300)
