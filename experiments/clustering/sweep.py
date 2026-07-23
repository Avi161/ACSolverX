"""Clustering algorithms, agreement metrics, the permutation null, and the supervised ceiling.

numpy + scipy only. This branch is deliberately dependency-light and sklearn is not installed;
everything here is short enough to write directly, which also means the scoring is auditable
rather than inherited.

Three things in here exist to stop the sweep from lying, and they matter more than the sweep:

1. **The permutation null.** Sweeping ~1700 (representation x preprocessing x algorithm x k)
   combinations and reporting the best one is a garden of forking paths: some combination will
   look good on pure noise. The statistic that means anything is therefore not "best observed"
   but "best observed vs the distribution of best-over-the-same-grid under permuted labels".
   Note the labels are used *only* for scoring -- the clustering never sees them -- so a
   permutation costs a re-score, not a re-cluster.

2. **The shape control.** ``shape (control)`` is lengths alone. The solved and unsolved
   populations differ in mean total length (15.5 vs 19.7), so a representation that separates no
   better than lengths-only has discovered length, not structure.

3. **The supervised ceiling.** A cross-validated classifier that is *shown* the labels is an
   upper bound on what any unsupervised method can recover. If the ceiling is at chance, a
   clustering that appears to separate is an artifact, full stop.

``balanced accuracy`` for a clustering is computed by giving every cluster to its majority class,
which is optimistic and grows with k by construction. It is reported because it is the
interpretable number; ARI is the primary statistic, and the null is what calibrates both.
"""
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.cluster.vq import kmeans2
from scipy.spatial.distance import pdist, squareform

# --------------------------------------------------------------------------------- agreement

def _contingency(a, b):
    a = np.asarray(a); b = np.asarray(b)
    ua, ia = np.unique(a, return_inverse=True)
    ub, ib = np.unique(b, return_inverse=True)
    m = np.zeros((len(ua), len(ub)), dtype=np.int64)
    np.add.at(m, (ia, ib), 1)
    return m


def adjusted_rand(a, b):
    m = _contingency(a, b)
    n = m.sum()
    if n < 2:
        return 0.0
    comb2 = lambda x: x * (x - 1) / 2.0
    sij = comb2(m).sum()
    si = comb2(m.sum(1)).sum()
    sj = comb2(m.sum(0)).sum()
    exp = si * sj / comb2(n)
    mx = (si + sj) / 2.0
    return 0.0 if mx == exp else float((sij - exp) / (mx - exp))


def nmi(a, b):
    m = _contingency(a, b).astype(float)
    n = m.sum()
    pij = m / n
    pi = pij.sum(1, keepdims=True)
    pj = pij.sum(0, keepdims=True)
    nz = pij > 0
    mi = (pij[nz] * np.log(pij[nz] / (pi @ pj)[nz])).sum()
    h = lambda p: -(p[p > 0] * np.log(p[p > 0])).sum()
    d = (h(pi.ravel()) + h(pj.ravel())) / 2.0
    return 0.0 if d <= 0 else float(mi / d)


def balanced_accuracy(clusters, labels):
    """Majority-vote each cluster to a class, then average per-class recall."""
    clusters = np.asarray(clusters); labels = np.asarray(labels)
    pred = np.empty_like(labels)
    for c in np.unique(clusters):
        msk = clusters == c
        vals, cnt = np.unique(labels[msk], return_counts=True)
        pred[msk] = vals[cnt.argmax()]
    recalls = [(pred[labels == u] == u).mean() for u in np.unique(labels)]
    return float(np.mean(recalls))


# ------------------------------------------------------------------------------ preprocessing

def zscore(X):
    s = X.std(0)
    s[s == 0] = 1.0
    return (X - X.mean(0)) / s


def pca(X, k):
    Xc = X - X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:min(k, Vt.shape[0])].T


def residualize(X, z):
    """Least-squares removal of ``z`` (total length) from every column of X."""
    A = np.column_stack([np.ones(len(z)), z])
    beta, *_ = np.linalg.lstsq(A, X, rcond=None)
    return X - A @ beta


PREPROC = {
    "z":            lambda X, ln: zscore(X),
    "z+pca10":      lambda X, ln: pca(zscore(X), 10),
    "z-length":     lambda X, ln: zscore(residualize(zscore(X), ln)),
}


# --------------------------------------------------------------------------------- algorithms

def _kmeans(X, k, seed):
    best, best_in = None, np.inf
    for s in range(4):
        c, lab = kmeans2(X, k, minit="++", seed=seed * 17 + s, missing="warn")
        if len(np.unique(lab)) < k:
            continue
        inertia = sum(((X[lab == j] - c[j]) ** 2).sum() for j in range(k))
        if inertia < best_in:
            best, best_in = lab, inertia
    return best if best is not None else np.zeros(len(X), dtype=int)


def _linkage(D, method, k):
    Z = linkage(squareform(D, checks=False), method=method)
    return fcluster(Z, k, criterion="maxclust")


def _spectral(D, k, seed):
    sig = np.median(D[D > 0]) if (D > 0).any() else 1.0
    W = np.exp(-(D ** 2) / (2 * sig ** 2))
    np.fill_diagonal(W, 0.0)
    d = W.sum(1)
    d[d <= 0] = 1e-12
    Dm = 1.0 / np.sqrt(d)
    Lsym = np.eye(len(W)) - (Dm[:, None] * W * Dm[None, :])
    vals, vecs = np.linalg.eigh(Lsym)
    U = vecs[:, :k]
    nrm = np.linalg.norm(U, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return _kmeans(U / nrm, k, seed)


def _dbscan(D, eps, min_samples=4):
    n = len(D)
    nbrs = [np.flatnonzero(D[i] <= eps) for i in range(n)]
    core = np.array([len(v) >= min_samples for v in nbrs])
    lab = np.full(n, -1)
    cid = 0
    for i in range(n):
        if lab[i] != -1 or not core[i]:
            continue
        stack, lab[i] = [i], cid
        while stack:
            p = stack.pop()
            for q in nbrs[p]:
                if lab[q] == -1:
                    lab[q] = cid
                    if core[q]:
                        stack.append(q)
        cid += 1
    return lab


def cluster_all(X, D, ks, seed=0):
    """{(algorithm, k): labels} for every algorithm family on one preprocessed matrix."""
    out = {}
    for k in ks:
        out[("kmeans", k)] = _kmeans(X, k, seed)
        for m in ("ward", "average", "complete", "single"):
            out[(m, k)] = _linkage(D, m, k)
        out[("spectral", k)] = _spectral(D, k, seed)
    finite = D[np.isfinite(D) & (D > 0)]
    for q in (5, 10, 20):
        eps = float(np.percentile(finite, q))
        lab = _dbscan(D, eps)
        out[(f"dbscan_q{q}", len(np.unique(lab)))] = lab
    return out


# ---------------------------------------------------------------------- supervised ceiling

def _folds(y, nfold, rng):
    idx = np.arange(len(y))
    out = [[] for _ in range(nfold)]
    for u in np.unique(y):
        v = rng.permutation(idx[y == u])
        for i, j in enumerate(v):
            out[i % nfold].append(j)
    return [np.array(sorted(f)) for f in out]


def knn_cv(X, y, k, nfold=5, seed=0, metric="euclidean"):
    rng = np.random.default_rng(seed)
    D = squareform(pdist(X, metric=metric))
    np.fill_diagonal(D, np.inf)
    pred = np.empty_like(y)
    for te in _folds(y, nfold, rng):
        tr = np.setdiff1d(np.arange(len(y)), te)
        sub = D[np.ix_(te, tr)]
        nn = np.argsort(sub, axis=1)[:, :k]
        for i, row in enumerate(nn):
            vals, cnt = np.unique(y[tr][row], return_counts=True)
            pred[te[i]] = vals[cnt.argmax()]
    return balanced_accuracy(pred, y)


def logreg_cv(X, y, nfold=5, seed=0, lam=1.0, iters=400):
    """L2-regularised logistic regression by plain gradient descent -- enough for a ceiling."""
    rng = np.random.default_rng(seed)
    yy = (y == y.max()).astype(float)
    pred = np.zeros(len(y))
    for te in _folds(y, nfold, rng):
        tr = np.setdiff1d(np.arange(len(y)), te)
        Xt = np.column_stack([np.ones(len(tr)), X[tr]])
        Xe = np.column_stack([np.ones(len(te)), X[te]])
        w = np.zeros(Xt.shape[1])
        for _ in range(iters):
            p = 1.0 / (1.0 + np.exp(-np.clip(Xt @ w, -30, 30)))
            g = Xt.T @ (p - yy[tr]) / len(tr) + lam * np.r_[0.0, w[1:]] / len(tr)
            w -= 0.5 * g
        pred[te] = (Xe @ w > 0).astype(float)
    lo, hi = y.min(), y.max()
    return balanced_accuracy(np.where(pred > 0, hi, lo), y)
