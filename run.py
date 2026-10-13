"""One command for every method: ``python run.py --config configs/<name>.toml [--set key=value ...]``.

Writes ``results/<run name>/{paths.jsonl, summary.json}``; the config format is in ``acx/runner/config.py``.
Your own presentations: ``--input FILE`` (formats in ``acx/data.py``) or ``--pres "xxYYY, xyxYXY"``, repeated. They run
as ``<config name>_<file stem>`` (``<config name>_pres`` for ``--pres``), never as the config's own shipped results,
unless ``--set name=...`` says otherwise. Decode later: ``--solved-from RUN_DIR`` runs only the rows that RUN_DIR
solved, e.g. a ``path = false`` run again with ``--set path=true``. A bad config, row slice or id, input file or a
missing file ends the command with its message.
"""
import argparse
import json
import os
from pathlib import Path

from acx.core.config import parse_override
from acx.data import parse_presentation, stem_of
from acx.runner import load_config, run
from acx.runner.rundir import read_records


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
    records = {rec["id"]: rec for rec in read_records(paths)}
    for k, line in enumerate(lines):
        if str(k) in records:                                       # a row that --rows left out has no record
            rec = records[str(k)]
            fields = {"kind": rec.get("kind"), unit or "cost": rec.get("cost"), "sub_moves": rec.get("sub_moves"),
                      "elem_moves": rec.get("elem_moves"), "error": rec.get("error")}
            shown = [f"{key}={value}" for key, value in fields.items() if value is not None]
            print(k, line, "solved" if rec["solved"] else "unsolved", *shown, sep="  ")


def solved_ids(run_dir):
    """The ids that ``<run_dir>/paths.jsonl`` marks solved, in file order (``--solved-from``)."""
    paths = Path(run_dir) / "paths.jsonl"
    if not paths.is_file():
        raise SystemExit(f"{paths}: no such file (--solved-from needs the paths.jsonl of a run made here)")
    ids = [rec["id"] for rec in read_records(paths) if rec["solved"]]
    if not ids:
        raise SystemExit(f"{paths}: no solved rows")
    return ids


def own_name(config_name, input_path):
    """The run name of your own presentations: ``<config name>_<file stem>`` for ``--input`` (the file's name without
    .txt, .csv, .jsonl and .gz), ``<config name>_pres`` for ``--pres``."""
    stem = "pres" if input_path is None else stem_of(input_path)
    return f"{config_name}_{stem}"


def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="a TOML file in configs/")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a config value; dotted keys reach sections (search.budget=1000); "
                    "name=... names the run")
    mine = ap.add_mutually_exclusive_group()
    mine.add_argument("--input", metavar="PATH", help="run all rows of your own file of presentations (.txt, .csv or "
                      ".jsonl, optionally .gz; see acx/data.py) instead of the config's benchmark; the run is named "
                      "<config name>_<file stem>")
    mine.add_argument("--pres", action="append", default=[], type=presentation, metavar='"R1,R2"',
                      help='run a presentation of your own, e.g. "xxYYY, xyxYXY"; repeat for more; the run is named '
                      '<config name>_pres')
    rows = ap.add_mutually_exclusive_group()
    rows.add_argument("--rows", help='rows of the benchmark: a slice "a:b" or "a:b:c" (integers), or ids "3,17" (an id '
                      'may hold a colon, "ms:1")')
    rows.add_argument("--solved-from", metavar="RUN_DIR", help="run only the rows that RUN_DIR/paths.jsonl marks "
                      "solved, e.g. to get and verify the paths of a path=false run: --set path=true")
    ap.add_argument("--out", default="results", help="results root (default: results)")
    ap.add_argument("--fresh", action="store_true", help="discard earlier results of this run name")
    return ap.parse_args(argv)


def execute(args):
    """Run the config with the arguments' overrides, rows and own presentations; print the summary."""
    # your own presentations replace the config's benchmark, and with it the config's slice of rows
    own = ['benchmark="own"', 'rows=""'] if args.input is not None or args.pres else []
    cfg = load_config(args.config, own + args.set + ([f'rows="{args.rows}"'] if args.rows else []))
    if args.solved_from:
        cfg["rows"] = ",".join(solved_ids(args.solved_from))
    if own and not any(parse_override(item)[0] == "name" for item in args.set):
        cfg["name"] = own_name(cfg["name"], args.input)
    run_dir = Path(args.out) / cfg["name"]
    lines = [", ".join(p.strs) for p in args.pres]
    if args.input is not None:                       # ./mine.txt and mine.txt are one run; "" stays an error
        cfg["benchmark"] = os.path.normpath(args.input) if args.input else ""
    if lines:
        cfg["benchmark"] = write_input(lines, run_dir, args.fresh)
    summary = run(cfg, args.out, args.fresh)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, indent=1))
    if lines:
        report(run_dir, lines, summary.get("cost_unit", ""))


def main(argv=None):
    """The command line. A bad config, row slice or id, input file, or a file that is missing or cannot be read,
    ends it with one line."""
    try:
        execute(parse_args(argv))
    except (ValueError, KeyError) as e:              # the library raises these; a KeyError would show its repr
        raise SystemExit(e.args[0] if isinstance(e, KeyError) else str(e)) from e
    except FileNotFoundError as e:
        raise SystemExit(f"{e.filename}: no such file") from e
    except OSError as e:                             # a folder, no permission, ...
        raise SystemExit(f"{e.filename}: {e.strerror}" if e.filename else str(e)) from e


if __name__ == "__main__":
    main()
