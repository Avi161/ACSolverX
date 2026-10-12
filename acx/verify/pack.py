"""The compact JSON form of elementary moves: ``pack`` and its inverse ``unpack``."""

_FIELDS = {"invert": ("target",), "swap": ("a", "b"), "conjugate": ("target", "by"),
           "multiply": ("target", "source"), "stabilize": (), "destabilize": ()}
_CODE = dict(zip(_FIELDS, "ISCMZD"))
_OP = {code: op for op, code in _CODE.items()}


def pack(moves):
    """Compact JSON form (``decode_ac_jsonl``'s): ``["I", t]``, ``["S", a, b]`` (``["S"]``: swap 1 and 2),
    ``["C", t, letter]``, ``["M", t, s]``, ``["Z"]``, ``["D"]``."""
    return [[_CODE[m["op"]], *(m[k] for k in _FIELDS[m["op"]] if k in m)] for m in moves]


def unpack(items):
    """Inverse of ``pack``."""
    return [{"op": _OP[code], **dict(zip(_FIELDS[_OP[code]], args))} for code, *args in items]
