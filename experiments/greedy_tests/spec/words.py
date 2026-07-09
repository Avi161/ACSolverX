"""General-n word algebra: the spec that the numba solver is tested against.

A word is a tuple of nonzero ints. ``abs(g)`` names the generator and the sign
is the exponent, so ``n_gen`` is a free parameter -- which is what lets the
stable-AC extension (an extra generator and relator, per AC4) reuse every test
written here without modification.

For ``n_gen == 2`` these functions define exactly the same maps as
``experiments/search/greedy_baseline.py``, but they are written *independently*:
minimal rotation by brute force rather than Booth's algorithm, reduction
straight from the definition. Agreement between the two is therefore evidence,
not a tautology. The one place this file deliberately mirrors the
implementation line-for-line is the guarded tail of :func:`reduce_word` -- see
the note there.

Two distinct symbol orders live in this codebase and must never be conflated:

* :func:`booth_order_key` -- the order canonicalisation minimises over
  (``Y < y < X < x``). It only decides *which* representative of an orbit is
  stored.
* :func:`ascii_order_key` -- the order of the rendered characters
  (``X < Y < x < y``). The heap tie-breaks on the state key, so this is the
  order the packed-bytes key must reproduce.
"""

_GEN_CHARS = "xyz"


def max_supported_n_gen():
    """Generators renderable as characters. Beyond this, work with ints."""
    return len(_GEN_CHARS)


def booth_order_key(g):
    """Sort key for the order canonicalisation minimises over.

    ``(-abs(g), g > 0)`` yields ``Y < y < X < x`` at n_gen=2 -- exactly
    ``is_less_than`` in the solver -- and extends to ``Z < z < Y < y < X < x``.
    """
    return (-abs(g), g > 0)


def ascii_order_key(g):
    """Sort key matching the rendered characters' ASCII order.

    ``X < Y < x < y`` at n_gen=2, ``X < Y < Z < x < y < z`` at n_gen=3: the
    uppercase (inverse) block sorts below the lowercase block, and within a
    block generators ascend by index.
    """
    return (g > 0, abs(g))


def symbol_to_char(g):
    c = _GEN_CHARS[abs(g) - 1]
    return c if g > 0 else c.upper()


def char_to_symbol(c):
    g = _GEN_CHARS.index(c.lower()) + 1
    return g if c.islower() else -g


def word_to_str(w):
    return "".join(symbol_to_char(g) for g in w)


def str_to_word(s):
    return tuple(char_to_symbol(c) for c in s)


def lex_key(w, order_key=booth_order_key):
    return tuple(order_key(g) for g in w)


def inverse(w):
    return tuple(-g for g in reversed(w))


def rotate(w, k):
    """Cyclic rotation matching ``np.roll(arr, 2 * k)`` on the (n, 2) encoding.

    ``np.roll`` shifts *right*, so element ``m`` of the result is ``w[m - k]``.
    """
    n = len(w)
    if n == 0:
        return w
    k %= n
    return w[n - k:] + w[:n - k]


def rotations(w):
    return [rotate(w, k) for k in range(len(w))]


def reduce_word(w, cyclic=True):
    """Free-reduce; when ``cyclic``, also cancel across the wrap-around.

    The wrap-around tail mirrors ``reduce_relator_nj`` exactly, including its
    strict ``i < length / 2`` bound. That bound means the cyclic step can never
    empty an already free-reduced word (a length-2 free-reduced word cannot have
    ``w[0] == -w[-1]``), so the empty word only ever arises from the stack.
    """
    stack = []
    for g in w:
        if stack and stack[-1] == -g:
            stack.pop()
        else:
            stack.append(g)

    length = len(stack)
    if cyclic and length > 1 and stack[0] == -stack[-1]:
        i = 1
        half = length / 2
        while i < half and stack[i] == -stack[-1 - i]:
            i += 1
        stack = stack[i:-i]

    return tuple(stack)


def is_freely_reduced(w):
    return all(a != -b for a, b in zip(w, w[1:]))


def is_cyclically_reduced(w):
    return is_freely_reduced(w) and (len(w) < 2 or w[0] != -w[-1])


def min_rotation(w, order_key=booth_order_key):
    """Lexicographically least rotation -- brute force, independent of Booth."""
    if not w:
        return w
    return min(rotations(w), key=lambda r: lex_key(r, order_key))


def canonical_word(w, order_key=booth_order_key):
    """Least element of the orbit of ``w`` under rotation and inversion.

    This is what ``canonical_relator_nj`` computes: relators are unoriented
    cyclic words, so rotation and whole-word inversion are quotiented out.
    """
    if not w:
        return w
    a = min_rotation(w, order_key)
    b = min_rotation(inverse(w), order_key)
    return min((a, b), key=lambda r: lex_key(r, order_key))


def orbit(w):
    """Every rotation of ``w`` and of ``w**-1`` -- the class canonical_word picks from."""
    return set(rotations(w)) | set(rotations(inverse(w)))
