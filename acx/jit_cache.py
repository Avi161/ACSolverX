"""The caches of acx's numba kernels carry a digest of acx's numba source.

numba checks a cached kernel only against its own file, not against the helpers inlined into it from other files
(``expand`` inlines ``canon_buf`` from ``kernels/words.py``), so after an edit to a helper's file alone it would keep
running the old machine code. ``stamp_caches`` adds a digest of every file that uses numba to the source stamp numba
checks, so any such edit compiles afresh; ``import acx`` calls it for acx. The caches stay where numba puts them
(``__pycache__``, or ``$NUMBA_CACHE_DIR``).
"""
import hashlib
from pathlib import Path

from numba.core.caching import CacheImpl, InTreeCacheLocator, UserProvidedCacheLocator

ROOT = Path(__file__).resolve().parent


def source_digest(root=ROOT):
    """A digest of the paths and contents of the ``.py`` files under ``root`` that mention numba."""
    digest = hashlib.sha256()
    for path in sorted(Path(root).rglob("*.py")):
        text = path.read_bytes()
        if b"numba" in text:
            digest.update(path.relative_to(root).as_posix().encode() + b"\0" + text + b"\0")
    return digest.hexdigest()[:16]


def stamp_caches(root=ROOT):
    """Stamp the caches of the kernels defined under ``root`` with ``source_digest(root)`` (call before they are)."""
    root = Path(root).resolve()
    digest = source_digest(root)

    class Stamped:
        def get_source_stamp(self):
            return super().get_source_stamp(), digest

        @classmethod
        def from_function(cls, py_func, py_file):
            if not Path(py_file).resolve().is_relative_to(root):
                return None
            return super().from_function(py_func, py_file)

    CacheImpl._locator_classes[:0] = [type("StampedUserDir", (Stamped, UserProvidedCacheLocator), {}),
                                      type("StampedInTree", (Stamped, InTreeCacheLocator), {})]
