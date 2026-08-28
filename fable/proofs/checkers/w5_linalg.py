"""Integer linear algebra for the W5 probes: GL_n(Z) elementary factorisation
and exact solving of M x = c over Z.  No external dependencies."""

from __future__ import annotations

from fractions import Fraction

Mat = list[list[int]]


def eye(n: int) -> Mat:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def matmul(P: Mat, Q: Mat) -> Mat:
    n, m, k = len(P), len(Q[0]), len(Q)
    return [[sum(P[i][t] * Q[t][j] for t in range(k)) for j in range(m)] for i in range(n)]


def det3(M: Mat) -> int:
    a, b, c = M[0]
    d, e, f = M[1]
    g, h, i = M[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


# Elementary row operations, expressed in the two forms an AC move realises:
#   ("add", i, j, k)  : row_i += k * row_j       (AC2 with trivial conjugator, |k| times)
#   ("neg", i)        : row_i *= -1              (AC1)


def apply_ops_to_matrix(M: Mat, ops: list[tuple]) -> Mat:
    R = [row[:] for row in M]
    for op in ops:
        if op[0] == "add":
            _, i, j, k = op
            R[i] = [R[i][t] + k * R[j][t] for t in range(len(R[i]))]
        elif op[0] == "neg":
            _, i = op
            R[i] = [-v for v in R[i]]
        else:
            raise ValueError(op)
    return R


def _swap_ops(i: int, j: int) -> list[tuple]:
    """row swap as adds+negation: (a,b)->(a+b,b)->(a+b,-a)->(b,-a)->(b,a)."""
    return [("add", i, j, 1), ("add", j, i, -1), ("add", i, j, 1), ("neg", j)]


def reduce_to_identity(M: Mat) -> list[tuple] | None:
    """Return elementary ops (adds/negations only) carrying M to the identity,
    or None when M is not in GL_n(Z)."""
    n = len(M)
    R = [row[:] for row in M]
    ops: list[tuple] = []

    def do(op: tuple) -> None:
        ops.append(op)
        if op[0] == "add":
            _, i, j, k = op
            R[i] = [R[i][t] + k * R[j][t] for t in range(n)]
        else:
            _, i = op
            R[i] = [-v for v in R[i]]

    for col in range(n):
        # Euclid on column `col` among rows >= col
        while True:
            nz = [r for r in range(col, n) if R[r][col] != 0]
            if not nz:
                return None
            piv = min(nz, key=lambda r: abs(R[r][col]))
            if piv != col:
                for op in _swap_ops(col, piv):
                    do(op)
            changed = False
            for r in range(col + 1, n):
                if R[r][col] != 0:
                    q = R[r][col] // R[col][col]
                    if q:
                        do(("add", r, col, -q))
                    if R[r][col] != 0:
                        changed = True
            if not changed:
                break
        if R[col][col] < 0:
            do(("neg", col))
        if R[col][col] != 1:
            return None
        for r in range(col):
            if R[r][col]:
                do(("add", r, col, -R[r][col]))
    # back-substitute above the diagonal
    for col in range(n - 1, -1, -1):
        for r in range(col):
            if R[r][col]:
                do(("add", r, col, -R[r][col]))
    return ops if R == eye(n) else None


def invert_ops(ops: list[tuple]) -> list[tuple]:
    out: list[tuple] = []
    for op in reversed(ops):
        if op[0] == "add":
            _, i, j, k = op
            out.append(("add", i, j, -k))
        else:
            out.append(op)
    return out


def solve_int(M: list[list[int]], c: list[int]) -> list[int] | None:
    """Exact integer solution of M x = c (M is rows x cols), or None.

    Column-style Hermite reduction: track the unimodular column transform.
    """
    rows, cols = len(M), len(M[0])
    Acols = [[M[r][j] for r in range(rows)] for j in range(cols)]   # columns
    T = eye(cols)                                                    # x = T * y
    target = c[:]
    pivots: list[tuple[int, int]] = []
    r = 0
    used = [False] * cols
    for r in range(rows):
        # find a column with nonzero entry in row r among unused ones
        while True:
            cand = [j for j in range(cols) if not used[j] and Acols[j][r] != 0]
            if not cand:
                break
            p = min(cand, key=lambda j: abs(Acols[j][r]))
            done = True
            for j in cand:
                if j == p:
                    continue
                q = Acols[j][r] // Acols[p][r]
                if q:
                    Acols[j] = [Acols[j][t] - q * Acols[p][t] for t in range(rows)]
                    T[j] = [T[j][t] - q * T[p][t] for t in range(cols)]
                if Acols[j][r] != 0:
                    done = False
            if done:
                used[p] = True
                pivots.append((r, p))
                break
    # forward solve
    y = [0] * cols
    resid = target[:]
    for (rr, p) in pivots:
        v = Acols[p][rr]
        if resid[rr] % v != 0:
            return None
        k = resid[rr] // v
        y[p] = k
        resid = [resid[t] - k * Acols[p][t] for t in range(rows)]
    if any(resid):
        return None
    # x = sum_j y_j * T[j]
    x = [0] * cols
    for j in range(cols):
        if y[j]:
            for t in range(cols):
                x[t] += y[j] * T[j][t]
    # verify
    for rr in range(rows):
        if sum(M[rr][t] * x[t] for t in range(cols)) != c[rr]:
            return None
    return x
