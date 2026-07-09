"""Abelianization invariants: the independent oracle for the move machinery.

The solver never computes an exponent sum, so these quantities share no code
and no concepts with it. That is the whole point -- a spec that re-derives the
implementation catches typos, but an invariant the implementation cannot see
catches *design* errors.

Why they are invariant. Let ``M[i][g]`` be the exponent sum of generator ``g``
in relator ``i``. Rotation and free/cyclic reduction leave every exponent sum
untouched, and inverting a word negates its row. So the substitution move
``r_i <- rot(r_i) . rot(r_j ** s)`` sets ``row_i <- row_i + s * row_j``: an
elementary row operation, which preserves ``det`` exactly. Canonicalisation may
invert a relator (negating a row) or reorder relators (permuting rows), each of
which only flips the sign. Hence ``abs(det)`` is preserved by every canonical
neighbour the search generates.

AC4 borders ``M`` with a fresh unit row and column, so ``abs(det)`` survives
stabilization too. The trivial presentation has ``M = I``, so **every**
AC-trivial balanced presentation satisfies ``abs(det) == 1``. A search that
manufactures a state with a different ``abs(det)`` has an unsound move.
"""


def exponent_sum_matrix(pres):
    """``M[i][g-1]`` = exponent sum of generator ``g`` in relator ``i``."""
    m = [[0] * pres.n_gen for _ in range(pres.n_rel)]
    for i, r in enumerate(pres.relators):
        for sym in r:
            m[i][abs(sym) - 1] += 1 if sym > 0 else -1
    return m


def det_int(m):
    """Exact integer determinant (fraction-free Bareiss). Square matrices only."""
    n = len(m)
    if n == 0:
        return 1
    if any(len(row) != n for row in m):
        raise ValueError("determinant of a non-square matrix")

    a = [row[:] for row in m]
    sign = 1
    prev = 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((r for r in range(k + 1, n) if a[r][k] != 0), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]) // prev
        prev = a[k][k]
    return sign * a[n - 1][n - 1]


def abs_det(pres):
    """The AC-invariant. Requires a balanced presentation."""
    if not pres.is_balanced:
        raise ValueError("abs_det needs n_rel == n_gen")
    return abs(det_int(exponent_sum_matrix(pres)))


def smith_normal_form(m):
    """Invariant factors ``d_1 | d_2 | ...`` of the integer matrix ``m``.

    The abelianization of the presented group is ``Z^k + sum Z/d_i``. For a
    balanced presentation of a group with trivial abelianization every ``d_i``
    is 1, which for a square matrix is equivalent to ``abs(det) == 1``; the
    general routine is kept because it stays meaningful when ``n_rel != n_gen``.
    """
    a = [row[:] for row in m]
    rows, cols = len(a), (len(a[0]) if a else 0)
    res = []
    t = 0
    while t < min(rows, cols):
        pivot = None
        for i in range(t, rows):
            for j in range(t, cols):
                if a[i][j] != 0 and (
                    pivot is None or abs(a[i][j]) < abs(a[pivot[0]][pivot[1]])
                ):
                    pivot = (i, j)
        if pivot is None:
            break
        pi, pj = pivot
        a[t], a[pi] = a[pi], a[t]
        for row in a:
            row[t], row[pj] = row[pj], row[t]

        done = False
        while not done:
            done = True
            for i in range(t + 1, rows):
                if a[i][t]:
                    q = a[i][t] // a[t][t]
                    for j in range(t, cols):
                        a[i][j] -= q * a[t][j]
                    if a[i][t]:
                        a[t], a[i] = a[i], a[t]
                        done = False
            for j in range(t + 1, cols):
                if a[t][j]:
                    q = a[t][j] // a[t][t]
                    for i in range(t, rows):
                        a[i][j] -= q * a[i][t]
                    if a[t][j]:
                        for row in a:
                            row[t], row[j] = row[j], row[t]
                        done = False
        res.append(abs(a[t][t]))
        t += 1

    for i in range(len(res)):
        for j in range(i + 1, len(res)):
            if res[i] and res[j] % res[i]:
                g = _gcd(res[i], res[j])
                res[i], res[j] = g, res[i] * res[j] // g
    return res


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def is_perfect_abelianization(pres):
    """SNF is the identity, i.e. the abelianization of the group is trivial."""
    snf = smith_normal_form(exponent_sum_matrix(pres))
    return len(snf) == min(pres.n_rel, pres.n_gen) and all(d == 1 for d in snf)
