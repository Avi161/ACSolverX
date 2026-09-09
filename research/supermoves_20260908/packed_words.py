"""Fast decoding for trusted canonical two-relator packed keys.

The research heap codec is ``1:X, 2:Y, 3:x, 4:y`` with one zero separator.
Callers must supply a valid key emitted by ``heuristic_1k.pack`` or the same
search engine; this helper intentionally does not validate arbitrary bytes.
"""

# bytes.translate uses this complete static 256-byte lookup table in C.
_DECODE = bytes.maketrans(bytes(range(5)), b"\0XYxy")


def unpack_canonical_key(key: bytes) -> tuple[str, str]:
    """Decode one trusted packed canonical pair, preserving empty relators."""
    left, right = key.translate(_DECODE).decode("ascii").split("\0")
    return left, right
