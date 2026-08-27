"""Turn a CoV sweep jsonl into a feature table for "is this z worth running?".

The question this file sets up: a presentation has ~100 applicable changes of variables and we
can only afford to search a few. Which ones are worth the nodes? Everything here is computable
BEFORE the search runs — the transformed relators, the substituted word, and the Aut-canonical
form of both sides (autcanon_fast, milliseconds). Nothing reads nodes_explored, path_length or
solved except the label builders at the bottom.

Grouping is by Aut(F2)-orbit of the ORIGINAL presentation (`aut_canon_orig`), not by pres_id:
the 66-row benchmark holds only 51 distinct orbits, so a pres_id split would put a presentation's
own relabelled twin in the training fold and read as generalisation.

    from cov_features import load_dataset
    ds = load_dataset(path)           # ds.X, ds.names, ds.group, ds.solved, ds.nodes, ...
"""
import json
import os
import re
from dataclasses import dataclass

import numpy as np

INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


# ---------------------------------------------------------------- word-level primitives

def exp_sums(w):
    """(sum of x-exponents, sum of y-exponents) — the abelianisation of the word."""
    return (w.count("x") - w.count("X"), w.count("y") - w.count("Y"))


def n_syllables(w):
    """Maximal runs of the same letter. A proxy for how 'mixed' the word is."""
    return len(re.findall(r"(.)\1*", w)) if w else 0


def n_switches(w):
    """Adjacent positions where the generator changes (x-ish <-> y-ish)."""
    g = [c.lower() for c in w]
    return sum(1 for a, b in zip(g, g[1:]) if a != b)


def n_inverse_pairs(w):
    """Adjacent a·a^-1 that a cyclic reduction would already have removed — should be 0,
    so a nonzero value flags a word the pipeline handed us unreduced."""
    return sum(1 for a, b in zip(w, w[1:]) if INV.get(a) == b)


def word_feats(w, prefix):
    ex, ey = exp_sums(w)
    n = len(w) or 1
    return {
        prefix + "len": len(w),
        prefix + "expx": ex,
        prefix + "expy": ey,
        prefix + "abs_expx": abs(ex),
        prefix + "abs_expy": abs(ey),
        prefix + "exp_l1": abs(ex) + abs(ey),
        prefix + "syll": n_syllables(w),
        prefix + "switches": n_switches(w),
        prefix + "switch_rate": n_switches(w) / n,
        prefix + "xfrac": (w.count("x") + w.count("X")) / n,
        prefix + "invfrac": (w.count("X") + w.count("Y")) / n,
        prefix + "unreduced": n_inverse_pairs(w),
    }


def pair_feats(r1, r2, prefix):
    """Features of a presentation <r1, r2>, symmetric in the two relators where it makes sense."""
    f = {}
    f.update(word_feats(r1, prefix + "r1_"))
    f.update(word_feats(r2, prefix + "r2_"))
    L1, L2 = len(r1), len(r2)
    f[prefix + "total_len"] = L1 + L2
    f[prefix + "max_len"] = max(L1, L2)
    f[prefix + "min_len"] = min(L1, L2)
    f[prefix + "len_gap"] = abs(L1 - L2)
    f[prefix + "len_ratio"] = max(L1, L2) / max(1, min(L1, L2))
    # |det| of the exponent-sum matrix: an AC invariant, and the one number the search never
    # computes. A presentation of the trivial group has |det| = 1.
    a, b = exp_sums(r1)
    c, d = exp_sums(r2)
    f[prefix + "abdet"] = abs(a * d - b * c)
    return f


# ---------------------------------------------------------------- per-row features

def row_features(r):
    """Everything knowable about one CoV row before its search starts."""
    z = r["z_word"]
    f = {}
    f.update(pair_feats(r["r1"], r["r2"], "cov_"))
    f.update(pair_feats(r["r1_orig"], r["r2_orig"], "orig_"))
    f.update(word_feats(z, "z_"))

    # what the substitution DID — the deltas are the part that varies within a presentation
    f["d_total_len"] = f["cov_total_len"] - f["orig_total_len"]
    f["d_max_len"] = f["cov_max_len"] - f["orig_max_len"]
    f["d_min_len"] = f["cov_min_len"] - f["orig_min_len"]
    f["r_total_len"] = f["cov_total_len"] / max(1, f["orig_total_len"])
    f["d_syll"] = (f["cov_r1_syll"] + f["cov_r2_syll"]) - (f["orig_r1_syll"] + f["orig_r2_syll"])
    f["d_switches"] = (f["cov_r1_switches"] + f["cov_r2_switches"]) - \
                      (f["orig_r1_switches"] + f["orig_r2_switches"])
    f["d_exp_l1"] = (f["cov_r1_exp_l1"] + f["cov_r2_exp_l1"]) - \
                    (f["orig_r1_exp_l1"] + f["orig_r2_exp_l1"])

    f["n_subs"] = r["n_subs"]
    f["z_len_frac"] = len(z) / max(1, f["orig_total_len"])
    f["iso_gen_y"] = 1.0 if r["iso_gen"] == "y" else 0.0
    f["iso_index"] = float(r["iso_index"])
    f["cap"] = r["max_relator_length_cap"]
    f["cap_headroom"] = r["max_relator_length_cap"] - f["cov_max_len"]
    # relabel vs moved: aut_canon of both sides, cheap next to a search
    f["is_relabel"] = 1.0 if r["aut_canon_orig"] == r["aut_canon_cov"] else 0.0
    # Aut-canonical form of the RESULT — its length is a search-free lower-bound-ish signal
    f["autcanon_cov_len"] = len(r["aut_canon_cov"].replace(",", ""))
    f["d_autcanon_len"] = f["autcanon_cov_len"] - len(r["aut_canon_orig"].replace(",", ""))
    return f


# ---------------------------------------------------------------- dataset

@dataclass
class Dataset:
    X: np.ndarray            # (n_rows, n_feat) float64
    names: list              # feature names, len == X.shape[1]
    group: np.ndarray        # Aut-orbit id of the original presentation (the CV grouping)
    pres: np.ndarray         # pres_id
    solved: np.ndarray       # bool — did this CoV solve within the budget
    nodes: np.ndarray        # nodes explored (== budget when unsolved)
    path: np.ndarray         # path length, -1 when unsolved
    base_solved: np.ndarray  # did the presentation's own control (no CoV) solve
    base_nodes: np.ndarray   # control nodes, -1 when the control did not solve
    budget: int

    def __len__(self):
        return self.X.shape[0]


def load_rows(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def load_dataset(path):
    rows = load_rows(path)
    ctrl = {r["pres_id"]: r for r in rows if r["z_word"] is None}
    cov = [r for r in rows if r["z_word"] is not None]

    orbit_id = {}
    for r in cov:
        orbit_id.setdefault(r["aut_canon_orig"], len(orbit_id))

    feats = [row_features(r) for r in cov]
    names = sorted(feats[0])
    X = np.array([[f[n] for n in names] for f in feats], dtype=np.float64)

    budget = cov[0]["node_budget"]
    b_solved = np.array([bool(ctrl[r["pres_id"]]["solved"]) for r in cov])
    b_nodes = np.array([ctrl[r["pres_id"]]["nodes_explored"] if ctrl[r["pres_id"]]["solved"]
                        else -1 for r in cov], dtype=np.float64)
    return Dataset(
        X=X, names=names,
        group=np.array([orbit_id[r["aut_canon_orig"]] for r in cov]),
        pres=np.array([r["pres_id"] for r in cov]),
        solved=np.array([bool(r["solved"]) for r in cov]),
        nodes=np.array([r["nodes_explored"] for r in cov], dtype=np.float64),
        path=np.array([r["path_length"] if r["solved"] else -1 for r in cov], dtype=np.float64),
        base_solved=b_solved, base_nodes=b_nodes, budget=budget,
    )


def cost(ds):
    """The rankable cost of one CoV start: nodes if it solved, else the budget it burned.

    Unsolved rows are not missing data — they cost a full budget and returned nothing, which is
    exactly the worst outcome. Censoring them (train on solved only) would teach the model that
    the rows it must learn to avoid do not exist.
    """
    return np.where(ds.solved, ds.nodes, float(ds.budget))


def default_path():
    here = os.path.dirname(os.path.abspath(__file__))
    acs = here
    while not (os.path.isdir(os.path.join(acs, "experiments")) and
               os.path.isdir(os.path.join(acs, "data"))):
        parent = os.path.dirname(acs)
        if parent == acs:
            raise RuntimeError("could not find the ACSolverX root")
        acs = parent
    return os.path.join(acs, "results", "stable_ac", "cov",
                        "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")


if __name__ == "__main__":
    ds = load_dataset(default_path())
    print(f"{len(ds)} CoV rows · {len(set(ds.pres))} presentations · "
          f"{len(set(ds.group))} Aut-orbits · budget {ds.budget:,}")
    print(f"{len(ds.names)} features")
    print(f"solved {ds.solved.sum()} ({100 * ds.solved.mean():.1f}%)")
    for n in ds.names:
        i = ds.names.index(n)
        print(f"  {n:24s} min {ds.X[:, i].min():10.3f}  max {ds.X[:, i].max():10.3f}")
