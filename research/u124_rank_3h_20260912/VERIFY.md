# Independent continuation verifier

`verify.py` is ready. Its tiny controls pass; no presentation search has run.
It imports the frozen independent word checker from the previous investigation
read-only, pinned to SHA-256. It never imports a new search implementation to
decide whether that implementation's proposed word identities are true.

The current source is `../rank_unbounded_20260912/all124.json`, SHA-256
`fba32693f0f1da10b8a9b8bf35ed6cd0f354a6d42d3af73f3aabf86142680336`.
It contains124 retained presentations with complete total length2180. The
known-triviality premise comes from the pinned Miller–Schupp presentations and
their already verified AC/stable witness lineage. Unimodular determinants are
checked as an invariant and are never substituted for that premise.

## Reusable API

- `load_baseline()` returns a dictionary keyed by presentation name. Each entry
  has exact integer `words`, `length`, `rank`, `sources`, `source_pointers` and
  `baseline_sha256`. `sources` accepts `current_best`, `saved_rank2` or
  `previous_best`. Prefer these exact integer tuples to reparsing display text.
- `verify_event(event, known_trivial=True)` independently checks one event.
  The known-triviality flag is required for rank-changing and ambient-basis
  composites; standalone determinant checks do not grant it.
- `verify_record(record, baseline=None)` anchors a complete path to a pinned
  source and checks every event. It returns the replayed endpoint, complete
  boundary lengths/ranks, the best certified prefix, its event count and gain,
  and whether the reported endpoint missed an earlier better prefix.

A candidate record has `name`, `baseline_sha256`, `source_key`, `initial`,
`events` and `endpoint`. `initial` is the normalized selected source using the
exact generator IDs. Optional `source_pointer`, `endpoint_length`,
`endpoint_rank` and `length_gain` are checked. `length_gain` always compares
against the current retained baseline for that ID, regardless of the chosen
path source. The original `aca_80` certificate therefore has new gain zero.

The existing event kinds are accepted unchanged: `defining_compression`,
`ambient_whitehead`, `lemma11_removal`, `ordinary_ac_substitution` and
`relator_normalization`. Additional kinds are:

1. `normal_product_substitution`: `before`, `target`, `factors`,
   `raw_target_after`, `after`. Each factor has `donor_index`, exact integer
   `sign` in `{-1,1}` and a signed-integer `conjugator`. The checked convention is

   `new = freely_reduce(old_target * product(c^-1 * donor^sign * c))`.

   Every donor must be another original relator. Donors are restored after use;
   all nontarget relators are retained. `raw_target_after` is freely reduced,
   and `after` is the normalized full tuple. Optional `raw_after` and complete
   normalization witnesses are checked when supplied. This is an explicit
   finite ordinary-AC composite ledger; its elementary expansion is not emitted.
2. `ambient_automorphism`: `before`, `images`, `inverse_images`, `after`, with
   optional `raw_after` and normalization witnesses. The dictionaries cover
   every positive generator ID in the old/new bases. Both inverse compositions
   are checked, including negative letters, and the forward map is applied to
   every relator. Different old/new generator labels are permitted.
3. `generator_relabeling`: the same schema, additionally requiring every image
   and inverse image to have length one, hence an exact signed permutation.
4. `defining_template_compression`: `before`, fresh `helpers`, old-generator
   `defining_words`, exact `defining_relators`, per-original-row `rows`,
   `templates`, `raw_after`, `normalization` and `after`. Each row contains its
   input index, original word, signed conjugation, `oriented` word, `template`
   and freely reduced `expanded` word. The verifier checks the signed orientation
   and complete expansion independently, retains every new defining relator and
   one template per old relator, then checks the normalization witnesses. The
   definitions in this schema use only the old basis; coordinated new helpers
   do not depend on each other. Helper-use counts, reserved expansion/definition
   work and reported macro-check sums are checked as well.

The template construction is a finite stable composite: add the definitions,
orient an original relator, then reverse expansion of its freely equal template
using the retained defining donors. It does not invoke arbitrary Tietze moves.
`verification_templates.json` independently replays the planted
`(abbAB,aabAB)` example through a commutator definition and three Lemma11
removals to the empty presentation. The known-triviality proof is explicit in
that output. A second control introduces helpers12 and13 with old labels2,5,11;
four deliberate witness corruptions are rejected. No census search was run.

Run the small controls with the parent checkout's Python, or pass saved paths:

```
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B research/u124_rank_3h_20260912/verify.py
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B research/u124_rank_3h_20260912/verify.py --records candidates.jsonl --output research/u124_rank_3h_20260912/verification_candidates.json
```

JSON input can be a single record, a list, or an object with `rows`. The
verification output pins the source file, source baseline, frozen auditor and
current verifier. A file that fails raises before writing a PASS report.

## Metric and provenance traps to avoid

- Some final stable tuples retain gaps in generator IDs. `aca_7`, for example,
  uses IDs2,3,4. The old `search.parse_words` compacts used letters, so reparsing
  its displayed tuple silently changes basis labels. Resolve the actual source
  witness or emit a checked relabeling event.
- Reaching a different tuple, orientation, generator labeling or larger rank
  does not itself improve the objective. Credit strict total-length gains and
  same-length rank reductions separately. The checker reports both explicitly.
- Compare with2180, not the earlier2191 baseline. An alternative seed can be
  longer than the incumbent, and shortening that seed may still yield no new gain.
- Inspect every certified `after` boundary, including those before a later
  removal or basis change lengthens the tuple. Prefix verification returns the
  exact truncation point of a better attained state.
- Count every relator, including all defining relators and singleton donors.
  Removing a defining row requires a valid Lemma11 event or a checked strict
  destabilization represented by that event; it is never free bookkeeping.
- Rank is the number of surviving generator IDs and relators, not the maximum
  generator label. Both counts must agree even when labels have gaps.
- A terminal collection of distinct signed singleton relators is an explicit
  solve boundary. A determinant of±1, a unit exponent or a low tuple length is
  not such a boundary.
- An ordinary composite segment beginning at a saved stable source does not
  by itself establish an ordinary rank-two certificate from the original input.
  Keep that upstream provenance and unexpanded stable realization explicit.

For the donor-prefix rewrite `P A Q -> P B^-1 Q`, if the signed donor rotation
is `S=t^-1 D^eps t=A B`, the right correction is the conjugate of `D^-eps`
by `c=t A Q`. For several disjoint replacements, original suffixes remain
valid when applied left-to-right; other orders require updated suffixes.
The normal-product checker verifies the whole resulting identity either way.
