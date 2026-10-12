"""One command for every method: ``python run.py --config configs/<name>.toml [--set key=value ...]``.

Writes ``results/<run name>/{paths.jsonl, summary.json}``; the config format is in ``acx/runner/config.py``.
Your own presentations: ``--input FILE`` (formats in ``acx/data.py``) or ``--pres "xxYYY, xyxYXY"``, repeated.
"""
import argparse
import json
from pathlib import Path

from acx.data import parse_presentation
from acx.runner import load_config, run


def presentation(text):
    """The ``type`` of ``--pres``: a ``Presentation``, or an error message that names what is wrong."""
    try:
        return parse_presentation(text)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"{text!r}: {e}") from None


def write_input(lines, run_dir, fresh):
    """Write the ``--pres`` lines to ``<run_dir>/input.txt`` and return its path.

    The folder's earlier results are for the presentations in that file, so a folder with results for others is
    refused (unless ``fresh``)."""
    run_dir = Path(run_dir)
    path, text = run_dir / "input.txt", "".join(line + "\n" for line in lines)
    old = path.read_text() if path.exists() else ""
    if (run_dir / "config.json").exists() and old != text and not fresh:
        raise SystemExit(f"{run_dir} holds results for other presentations: pass --fresh or add --set name=<another name>")
    run_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return str(path)


def report(run_dir, lines, unit):
    """Print one line per presentation: its id (the position in ``lines``), the presentation, solved or unsolved, and
    the record's kind, cost (named by its ``unit``), sub_moves, elem_moves and error, for those it has."""
    paths = Path(run_dir) / "paths.jsonl"
    if not paths.exists():                                          # the rank-n sweep keeps its rows in other files
        return
    records = {rec["id"]: rec for rec in map(json.loads, paths.read_text().splitlines())}
    for k, line in enumerate(lines):
        if str(k) in records:                                       # a row that --rows left out has no record
            rec = records[str(k)]
            fields = {"kind": rec.get("kind"), unit or "cost": rec.get("cost"), "sub_moves": rec.get("sub_moves"),
                      "elem_moves": rec.get("elem_moves"), "error": rec.get("error")}
            shown = [f"{key}={value}" for key, value in fields.items() if value is not None]
            print(k, line, "solved" if rec["solved"] else "unsolved", *shown, sep="  ")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="a TOML file in configs/")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a config value; dotted keys reach sections (search.budget=1000)")
    mine = ap.add_mutually_exclusive_group()
    mine.add_argument("--input", metavar="PATH", help="run all rows of your own file of presentations (.txt, .csv or "
                      ".jsonl, optionally .gz; see acx/data.py) instead of the config's benchmark")
    mine.add_argument("--pres", action="append", default=[], type=presentation, metavar='"R1,R2"',
                      help='run a presentation of your own, e.g. "xxYYY, xyxYXY"; repeat for more')
    ap.add_argument("--rows", help='a slice "a:b" or ids "3,17" of the benchmark')
    ap.add_argument("--out", default="results", help="results root (default: results)")
    ap.add_argument("--fresh", action="store_true", help="discard earlier results of this run name")
    args = ap.parse_args(argv)
    # your own presentations replace the config's benchmark, and with it the config's slice of rows
    own = ['benchmark="own"', 'rows=""'] if args.input is not None or args.pres else []
    cfg = load_config(args.config, own + args.set + ([f'rows="{args.rows}"'] if args.rows else []))
    run_dir = Path(args.out) / cfg["name"]
    lines = [", ".join(p.strs) for p in args.pres]
    if args.input is not None:
        cfg["benchmark"] = args.input
    if lines:
        cfg["benchmark"] = write_input(lines, run_dir, args.fresh)
    summary = run(cfg, args.out, args.fresh)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, indent=1))
    if lines:
        report(run_dir, lines, summary.get("cost_unit", ""))


if __name__ == "__main__":
    main()
