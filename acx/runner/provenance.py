"""Source/runtime identity and invocation history for reproducible experiments.

The resume guard uses file content and dependency versions, so a new commit with identical source can resume,
but a changed solver cannot silently append results from another implementation. Old runs remain readable and
resumable; their missing history is explicitly recorded instead of attributed to the current source.
"""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
from datetime import datetime, timezone

from .storage import write_json

ROOT = Path(__file__).resolve().parents[2]


def _digest(paths, root):
    """Hash file names and contents, in order, without loading large files into memory."""
    digest = hashlib.sha256()
    for path in paths:
        digest.update(str(path.relative_to(root)).encode() + b"\0")
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def _git(*args):
    """Optional checkout metadata; source hashes work in an unpacked source tree too."""
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], stderr=subprocess.DEVNULL,
                                       text=True, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def snapshot(method):
    """Identity needed to resume and context needed to interpret timings; never read credentials or all env vars."""
    files = sorted((ROOT / "acx").rglob("*.py"))
    files += [p for name in ("run.py", "compare.py", "pyproject.toml") if (p := ROOT / name).is_file()]
    dependencies = ["numpy", "numba", "llvmlite"]
    if method == "rl":
        dependencies.append("torch")
        files += sorted((ROOT / "acx" / "rl" / "checkpoint").glob("*.pt"))
    versions = {}
    for package in dependencies:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    dirty = _git("status", "--porcelain", "--", "acx", "run.py", "compare.py", "pyproject.toml")
    return {
        "identity": {"source_sha256": _digest(files, ROOT), "python": platform.python_version(),
                     "dependencies": versions},
        "source": {"git_commit": _git("rev-parse", "HEAD"), "dirty": None if dirty is None else bool(dirty)},
        "host": {"platform": platform.platform(), "machine": platform.machine(), "cpu_count": os.cpu_count(),
                 "threads": {key: os.environ.get(key) for key in
                             ("NUMBA_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")}},
    }


def prepare_provenance(run_dir, cfg, fresh=False):
    """Build the next manifest without writing; refuse source/runtime drift before a run changes result files."""
    folder = Path(run_dir)
    path = folder / "provenance.json"
    if path.is_symlink():
        raise ValueError(f"run output must not be a symlink: {path}")
    current = snapshot(cfg["method"])
    prior = None
    if path.exists() and not fresh:
        prior = json.loads(path.read_text(encoding="utf-8"))
        if prior.get("schema") != 1 or prior.get("identity") != current["identity"]:
            raise ValueError(f"{folder} holds results from another source or runtime: use --fresh or another name")
    unknown_history = not fresh and prior is None and any(
        (folder / name).exists() for name in ("paths.jsonl", "summary.json", "rows"))
    invocation = {
        "started_utc": datetime.now(timezone.utc).isoformat(), "rows": cfg.get("rows"),
        "workers": cfg.get("workers", 1), "benchmark": cfg["benchmark"],
        "backend": ("rl-beam" if cfg["method"] == "rl" else
                    cfg.get("hybrid" if cfg["method"] == "hybrid" else "search", {}).get("backend", "fast")),
        "source": current["source"], "host": current["host"],
    }
    return {"schema": 1, "identity": current["identity"],
            "prior_results_untracked": prior["prior_results_untracked"] if prior else unknown_history,
            "invocations": [*(prior["invocations"] if prior else []), invocation]}


def write_provenance(run_dir, manifest):
    """Persist the prepared manifest atomically after the config and input guards have passed."""
    write_json(Path(run_dir) / "provenance.json", manifest)
