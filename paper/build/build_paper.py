#!/usr/bin/env python3
"""Compile paper.tex with tectonic and report errors/undefined refs.

Usage: python paper/build/build_paper.py   (from the repo root or paper/)
Exit code 0 only if the PDF is produced with no LaTeX errors and no
undefined references/citations.
"""
import re
import subprocess
import sys
from pathlib import Path

PAPER_DIR = Path(__file__).resolve().parent.parent


def main() -> int:
    tex = PAPER_DIR / "paper.tex"
    if not tex.exists():
        print(f"missing {tex}", file=sys.stderr)
        return 2

    missing = [
        m.group(1)
        for m in re.finditer(r"\\input\{([^}]+)\}", tex.read_text())
        if not (PAPER_DIR / (m.group(1) + ".tex")).exists()
        and not (PAPER_DIR / m.group(1)).exists()
    ]
    if missing:
        print("missing \\input targets:", ", ".join(missing), file=sys.stderr)
        return 2

    proc = subprocess.run(
        ["tectonic", "--keep-logs", "paper.tex"],
        cwd=PAPER_DIR,
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    print(out)

    problems = []
    if proc.returncode != 0:
        problems.append(f"tectonic exit code {proc.returncode}")
    for pat, label in [
        (r"undefined references", "undefined references"),
        (r"Citation .* undefined", "undefined citation"),
        (r"Reference .* undefined", "undefined reference"),
        (r"^!", "LaTeX error"),
    ]:
        if re.search(pat, out, re.MULTILINE | re.IGNORECASE):
            problems.append(label)

    pdf = PAPER_DIR / "paper.pdf"
    if not pdf.exists():
        problems.append("paper.pdf not produced")

    if problems:
        print("BUILD PROBLEMS:", "; ".join(sorted(set(problems))), file=sys.stderr)
        return 1
    print(f"OK: {pdf} ({pdf.stat().st_size // 1024} KiB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
