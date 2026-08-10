"""Pure-Python transliteration of `envs/ac_moves.py:booth_lex_min_rotation_masked`.

Test support only -- nothing in the training path imports this. It exists so
`lex_min_rotation_index` (the O(L^2) brute force the torch env actually uses)
can be checked against the JAX routine it replaces **without installing JAX**,
line for line rather than in spirit.

The transliteration is exact and needs no bounds guards: the JAX version's
dynamic indices are provably in range (`i - k - 1 >= 0` because `k <= i`, and
`k + j + 1 <= i` because `f[m] <= m`), and `f[j]` is only read inside the loop
body, which the loop condition guarantees is reached with `j != -1`.
"""


def booth_lex_min_rotation_masked(s):
    """Index of the lex-smallest rotation of the non-zero prefix of `s`."""
    l_full = len(s)
    length = sum(1 for v in s if v != 0)
    s2 = list(s) + list(s)
    f = [-1] * (2 * l_full)
    k = 0

    for i in range(1, 2 * l_full):
        j = f[i - k - 1]
        while True:
            ijk = k + j + 1
            valid = (i < length) and (ijk < length)
            neq = (s2[i] != s2[ijk]) or (not valid)
            if not (j != -1 and neq):
                break
            k = (i - j - 1) if (ijk >= length or s2[i] < s2[ijk]) else k
            j = f[j]

        neq = (s2[i] != s2[k]) or (i >= length) or (k >= length)
        f[i - k] = -1 if (j == -1 and neq) else j + 1

        if j == -1 and neq:
            k = i if (s2[i] < s2[k] or k >= length) else k

    return k


def lex_min_rotation_index_ref(s):
    """Independent brute-force oracle: smallest index attaining the min rotation."""
    length = sum(1 for v in s if v != 0)
    if length == 0:
        return 0
    w = list(s[:length])
    best, best_k = None, 0
    for k in range(length):
        rot = w[k:] + w[:k]
        if best is None or rot < best:
            best, best_k = rot, k
    return best_k
