"""One command for every method: ``python run.py --config configs/<name>.toml [--set key=value ...]``.

Writes ``results/<run name>/{paths.jsonl, summary.json}``; the config format is in ``acx/runner/config.py``.
"""
import argparse
import json

from acx.runner import load_config, run


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", required=True, help="a TOML file in configs/")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a config value; dotted keys reach sections (search.budget=1000)")
    ap.add_argument("--rows", help='a slice "a:b" or ids "3,17" of the benchmark')
    ap.add_argument("--out", default="results", help="results root (default: results)")
    ap.add_argument("--fresh", action="store_true", help="discard earlier results of this run name")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, args.set + ([f'rows="{args.rows}"'] if args.rows else []))
    summary = run(cfg, args.out, args.fresh)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, indent=1))


if __name__ == "__main__":
    main()
