"""The packed-bytes state key, generalised past two relators.

``GreedyHeavySolver`` keys states by ``bytes`` instead of ``(str, str)``. That
is only sound because the packed key **sorts identically** to the string tuple:
the heap orders on ``(priority, depth, key)``, so any disagreement in key order
would reorder pops among ties and change ``nodes_explored``.

Two properties buy that:

* the 1-byte code of each symbol ascends with its character's ASCII value, so
  ``code(X)=1 < code(Y)=2 < code(x)=3 < code(y)=4``; and
* the ``0x00`` separator sorts below every symbol code, which reproduces
  Python's rule that a string sorts before any string it prefixes.

Both generalise: at ``n_gen`` generators the uppercase block takes codes
``1..n_gen`` and the lowercase block ``n_gen+1..2*n_gen``, matching
``X < Y < Z < x < y < z``.
"""

from .words import ascii_order_key

KEY_SEP = b"\x00"


def code_table(n_gen):
    """``{signed symbol: code}``, order-preserving w.r.t. the rendered characters.

    At n_gen=2 this reproduces ``greedy_baseline._CODE_TO_CHAR`` inverted:
    ``X -> 1, Y -> 2, x -> 3, y -> 4``.
    """
    symbols = [g for g in range(-n_gen, n_gen + 1) if g != 0]
    symbols.sort(key=ascii_order_key)
    return {g: i + 1 for i, g in enumerate(symbols)}


def inverse_code_table(n_gen):
    return {c: g for g, c in code_table(n_gen).items()}


def pack(relators, n_gen):
    """Relators -> the packed key. At n_rel=2 this is ``pack_key``'s output."""
    table = code_table(n_gen)
    return KEY_SEP.join(bytes(table[g] for g in r) for r in relators)


def unpack(key, n_gen, n_rel):
    table = inverse_code_table(n_gen)
    parts = key.split(KEY_SEP)
    if len(parts) != n_rel:
        raise ValueError(f"key holds {len(parts)} relators, expected {n_rel}")
    return tuple(tuple(table[c] for c in part) for part in parts)


def key_lengths(key, n_rel):
    parts = key.split(KEY_SEP)
    if len(parts) != n_rel:
        raise ValueError(f"key holds {len(parts)} relators, expected {n_rel}")
    return tuple(len(p) for p in parts)
