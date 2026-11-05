"""Figure stable_ranks_split.png: naive stable search at rank 3 on MS640, budget 10^3.

Reads the rank-3 brute-force arrays of branch rank3/brute-force-baseline
(results/stable_ac/rank3_bf/: rank3_bf_ms640_b1000_cap24_L{1..10}.npz, and the rank-2 control from
rankn_bf_ms640_b1000_cap24_r4.npz, field base) from the directory given as the first argument, and
writes the figure to the second. For each word length it plots the share of the (presentation, word)
searches that solve, with the presentations grouped by the units LENGTH needs on P.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
ctl = np.load(f"{src}/rankn_bf_ms640_b1000_cap24_r4.npz")
base = ctl["base"]
csol, cn = base[:, 0] == 1, base[:, 1]
Ls = list(range(1, 11))
P = []
for i in Ls:
    d = np.load(f"{src}/rank3_bf_ms640_b1000_cap24_L{i}.npz")
    assert (d["pres_ids"] == ctl["pres_ids"]).all()
    P.append(d["path_len"] >= 0)
groups = [
    ("1 to 9 units", csol & (cn >= 1) & (cn <= 9), "#9ecae1", "o"),
    ("10 to 99 units", csol & (cn >= 10) & (cn <= 99), "#3182bd", "s"),
    ("100 to 999 units", csol & (cn >= 100) & (cn <= 999), "#08306b", "^"),
    ("not solved by rank 2", ~csol, "#a63603", "D"),
]
fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
for lab, m, c, mk in groups:
    vals = [100 * p[m].mean() for p in P]
    ax.plot(Ls, vals, marker=mk, ms=4, lw=1.4, color=c, label=f"{lab} ({int(m.sum())} presentations)")
ax.set_xticks(Ls)
ax.set_xlabel("word length $|w|$", fontsize=9)
ax.set_ylabel("words that solve within $10^3$ (%)", fontsize=9)
ax.set_ylim(-3, 105)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=7.5, frameon=False, loc="center right", title="units LENGTH needs on $P$", title_fontsize=7.5)
fig.tight_layout()
fig.savefig(out, facecolor="white")
