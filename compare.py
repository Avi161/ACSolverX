"""Compare finished runs: ``python compare.py results/A results/B ... [--html FILE] [--common]``.

Prints one markdown table (solve rate, cost per solved row, moves, CPU per row and per pop/unit). ``--html`` also
writes one self-contained page with the table and three bar charts. The code is in ``acx/report/``.
"""
import argparse

from acx.report import html_page, load_run, markdown


def main(argv=None):
    ap = argparse.ArgumentParser(description="Compare finished runs in one markdown table, and in charts with --html.")
    ap.add_argument("runs", nargs="+", metavar="RUN", help="a results folder written by run.py (paths.jsonl)")
    ap.add_argument("--common", action="store_true", help="average only the rows every run solved")
    ap.add_argument("--html", metavar="FILE", help="also write a self-contained HTML page with three bar charts")
    args = ap.parse_args(argv)
    runs = [load_run(folder) for folder in args.runs]
    print(markdown(runs, args.common))
    if args.html:
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(html_page(runs, args.common))


if __name__ == "__main__":
    main()
