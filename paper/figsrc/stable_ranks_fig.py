"""Figure stable_ranks_split.png: naive stable search at ranks 3, 4 and 5 on MS640, budget 10^3.

Reads the rank-n brute-force arrays of branch rank3/brute-force-baseline
(results/stable_ac/rank3_bf/: rank3_bf_ms640_b1000_cap24_L{1,2,3}.npz, rankn_bf_ms640_b1000_cap24_r{4,5}.npz)
from the directory given as the first argument, and writes the figure to the second.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], sys.argv[2]
r4 = np.load(f"{src}/rankn_bf_ms640_b1000_cap24_r4.npz")
r5 = np.load(f"{src}/rankn_bf_ms640_b1000_cap24_r5.npz")
L = [np.load(f"{src}/rank3_bf_ms640_b1000_cap24_L{i}.npz") for i in (1, 2, 3)]
base = r4["base"]
csol, cn = base[:, 0] == 1, base[:, 1]
p3 = np.concatenate([l["path_len"] for l in L], 1)
methods = [
    ("rank 3, $|w|\\leq2$ (8 starts)", p3[:, :8]),
    ("rank 5, $|w|\\leq2$ (120 starts)", r5["path_len"]),
    ("rank 3, $|w|\\leq3$ (26 starts)", p3),
    ("rank 4, $|w|\\leq3$ (351 starts)", r4["path_len"]),
]
groups = [("1 to 9", 1, 9), ("10 to 99", 10, 99), ("100 to 999", 100, 999)]
colors = ["#9ecae1", "#08519c", "#fdae6b", "#a63603"]

fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
w = 0.2
for k, (lab, pl) in enumerate(methods):
    vals = []
    for _, lo, hi in groups:
        m = csol & (cn >= lo) & (cn <= hi)
        vals.append(100 * (pl[m] >= 0).mean(axis=1).mean())
    x = np.arange(len(groups)) + (k - 1.5) * w
    bars = ax.bar(x, vals, w, label=lab, color=colors[k])
    for xi, v in zip(x, vals):
        ax.text(xi, v + 1.5, f"{v:.0f}", ha="center", va="bottom", fontsize=7)
ns = [int((csol & (cn >= lo) & (cn <= hi)).sum()) for _, lo, hi in groups]
ax.set_xticks(range(len(groups)))
ax.set_xticklabels([f"{g[0]}\n({n} presentations)" for g, n in zip(groups, ns)], fontsize=8)
ax.set_xlabel("expansions LENGTH needs on $P$ (rank 2)", fontsize=9)
ax.set_ylabel("starts that solve within $10^3$ (%)", fontsize=9)
ax.set_ylim(0, 112)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper right")
fig.tight_layout()
fig.savefig(out, facecolor="white")
