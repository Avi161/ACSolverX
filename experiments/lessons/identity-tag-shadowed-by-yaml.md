# [2026-07-15] Identity tag shadowed by a yaml copy [TRAP]

5cb9471 bumped `cov.Z_FAMILY_TAG` zf1 → zf2 (the zf2 family change) but
`experiments/stable_ac/cov/config_cov.yaml` still carried its own
`z_family: zf1`. `run_cov.load_config` applies the yaml **over**
`COV_DEFAULTS`, so any yaml-driven `mode: cov` run would have written
`cov_..._zf1_...` files while actually running the zf2 family — and resumed
old zf1 rows into them: exactly the mixed-family corruption the tag exists to
prevent. Nothing caught it, because the prefix tests build their config from
`COV_DEFAULTS`, never from the shipped yaml.

Found 2026-07-15 while chasing a different regression (PIPELINE.md's
y-isolation section reverted by working-session commit 47fe3c3).

**Rule:** a result-identity constant (family tag, schema version) exists in
exactly one code constant; a config file must not carry a copy, because the
config merge order silently prefers the stale copy on the next bump. Where a
shipped config exists, pin `load_config(shipped_yaml)` against the code
constant in a test (`test_shipped_yaml_cannot_shadow_the_family_tag`).
