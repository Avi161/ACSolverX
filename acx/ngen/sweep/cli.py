"""The command line of the sweep: ``python -m acx.ngen.sweep``."""
import argparse
import json
import os

from .check import verify
from .driver import run


def main(argv=None):
    """Run a rank-n config (the runner's TOML), print the summary, optionally verify the result."""
    parser = argparse.ArgumentParser(
        prog="python -m acx.ngen.sweep", description="rank-n brute-force sweep (the config is the runner's TOML, method 'rankn')")
    parser.add_argument("--config", required=True)
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--rows")
    parser.add_argument("--out", default="results")
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--verify", type=int, metavar="N",
                        help="after the run, re-run N random cells on both backends")
    args = parser.parse_args(argv)

    from ...runner import load_config
    overrides = args.set + ([f'rows="{args.rows}"'] if args.rows else [])
    cfg = load_config(args.config, overrides)
    summary = run(cfg, args.out, args.fresh)
    print(json.dumps({k: v for k, v in summary.items() if k != "buckets"}, indent=1))
    if args.verify is not None:
        failures = verify(os.path.join(args.out, cfg["name"]), recheck=args.verify)
        if failures:
            raise SystemExit("\n".join(failures[:20]))
