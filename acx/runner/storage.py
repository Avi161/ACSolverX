"""Output boundaries and atomic replacement shared by the runner and rank-n sweeps."""
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile


def check_name(name):
    """A run name is one directory component; the output location belongs in ``--out``."""
    if (not isinstance(name, str) or not name or name in (".", "..")
            or any(c in name for c in ("/", "\\", "\0")) or PureWindowsPath(name).drive):
        raise ValueError(f"name must be a nonempty directory name, not a path: {name!r}")
    return name


def run_directory(out, name):
    """Resolve a run beneath ``out`` without following a run-directory symlink (including with ``--fresh``)."""
    folder = Path(out) / check_name(name)
    if folder.is_symlink():
        raise ValueError(f"run directory must not be a symlink: {folder}")
    return folder


def atomic_write(path, text):
    """Replace one UTF-8 file after writing it completely, leaving the old file intact on failure."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, value):
    """Atomically replace a JSON document."""
    atomic_write(path, json.dumps(value, indent=1) + "\n")
