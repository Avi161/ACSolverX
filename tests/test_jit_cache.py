"""numba's caches of acx's kernels carry a digest of acx's numba source (``acx.jit_cache``)."""
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from acx.jit_cache import source_digest

ROOT = Path(__file__).resolve().parents[1]


def write(path, text):
    path.write_text(textwrap.dedent(text))


def test_digest_follows_the_files_that_use_numba(tmp_path):
    write(tmp_path / "kern.py", "from numba import njit\n")
    write(tmp_path / "plain.py", "x = 1\n")
    before = source_digest(tmp_path)
    write(tmp_path / "plain.py", "x = 2\n")
    assert source_digest(tmp_path) == before
    write(tmp_path / "kern.py", "from numba import njit\n# edited\n")
    assert source_digest(tmp_path) != before


def test_acx_kernels_carry_the_digest():
    from acx.search.fast.dedup import rehash
    assert rehash._cache._impl.locator.get_source_stamp()[1] == source_digest()


@pytest.mark.parametrize("stamped", [True, False])
def test_editing_only_an_inlined_helper_recompiles(tmp_path, stamped):
    """A cached kernel inlines a helper from another file, and only the helper's file is edited: with the stamp the
    kernel is recompiled; without it numba would keep the old machine code (the case the stamp exists for)."""
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    write(pkg / "helper.py", """\
        from numba import njit

        @njit(inline="always")
        def value():
            return 1
    """)
    write(pkg / "kernel.py", """\
        from numba import njit
        from helper import value

        @njit(cache=True)
        def run():
            return value()
    """)
    script = textwrap.dedent(f"""\
        import sys
        sys.path[:0] = [{str(ROOT)!r}, {str(pkg)!r}]
        from acx.jit_cache import stamp_caches
        if {stamped}:
            stamp_caches({str(pkg)!r})
        import kernel
        print(kernel.run())
    """)

    def run():                        # -B: no .pyc, which a same-size edit in the same second would leave stale
        return subprocess.run([sys.executable, "-B", "-c", script], capture_output=True, text=True, check=True).stdout

    assert run() == "1\n"
    write(pkg / "helper.py", (pkg / "helper.py").read_text().replace("return 1", "return 2"))
    assert run() == ("2\n" if stamped else "1\n")
