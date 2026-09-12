# Coupled three-product exchange: independent audit and exact124 screen

The coupled exchange and finite support-breakpoint criterion are sound in the literal Magnus frame. `coupled_exchange.py` implements their exact ordinary-AC compiler separately from the frozen boundary and residue modules. **370 planted/API/resource checks and1,152 finite-versus-wide comparisons pass.** All candidate endpoints, accepted paths, best prefixes, and reported intermediate minimum lengths are independently checked.

On all124 exact saved best-state inputs, the screen admits **five strict donor-changing support-potential decreases**, but **no strict ordinary-length improvement and no solve**. Each accepted exchange receives one bounded frozen-boundary retry; all five retries fail their explicit checkpoint. The complete record is `coupled_exchange_report.json`.

## Exact free-group identity

Use `z_i=t^i z t^-i` in either literal generator frame `(t,z)=(x,y)` or `(y,x)`. Normalize the nominated relator by an explicit inversion when its stable exponent is-1, giving `R=F t`; the other relator is `S=G` with stable exponent zero.

For donor sign `e=±1` and integer shifts `q,k`, put

    D=t^q S^e t^-q,
    H=ired((T^q(G^e))^-1 F),
    A=H t=D^-1 R,
    B=ired(F T^-k(H^-1)).

The exact free words satisfy

    B = R t^-k A^-1 t^k.

Indeed `R=F t` and `A^-1=t^-1 H^-1`, so

    F t t^-k t^-1 H^-1 t^k = F t^-k H^-1 t^k.

The output pair is `(A,B)` in the original relator positions. These equations are identities in the free group, not deductions from exponent sums or a quotient relation.

After orienting and conjugating the donor to `D`, the compiler emits:

1. Invert `R`, right-multiply it by `D`, and invert it again. The changed source is `A=D^-1R`.
2. Right-multiply the donor `D` by `A`. This temporary donor is exactly the original normalized `R`.
3. Temporarily invert `A`, conjugate it by `t^k`, right-multiply the other relator by that word, undo the conjugation, and restore the sign of `A`.

The final source is restored to `A`, and the final donor is `R t^-k A^-1 t^k`. There are exactly three AC2 multiplications. The complete elementary count, including preorientation but excluding any initial negative-stable-exponent normalization, is

    7 + 2|k| + |q| + indicator(e=-1).

This corrects a small overhead count in the source note: `S→t^q S^e t^-q` costs **|q|** single-generator conjugations, not2|q|. Astra's existing check script already emits the correct count. The base term `7+2|k|` is correct. The implementation asserts the formula against every completed emitted exchange.

If `k=0`, the output donor is simply `D`, so the main nonterminal donor-changing arm excludes this choice. For nonempty finite `H`, a nonzero shift cannot fix `H`, and therefore `B` differs from `D`. If `H` is empty, however, `A=t` and `B=D` for every `k`; this is explicitly identified as an existing terminal checkpoint rather than a donor-changing nonterminal instance.

## Why at most twelve candidates suffice

Set `Phi=span(F)+span(G)`, where span is the maximum indexed height minus the minimum in the freely reduced literal indexed word. Empty `F` and span-zero `G` are separately handled terminal checkpoints in a unimodular pair.

Fix an orientation `G^e`. If no cancellation occurs at the seam `(T^q(G^e))^-1 | F`, then `H` contains the entire support of both words, and it ends with the last letter of `F`.

For `k=0`, `B=T^q(G^e)`, so potential cannot decrease. For `k≠0`, the seam `F | T^-k(H^-1)` cannot cancel: its endpoint indices match only for `k=0` when `H` retains that final letter of `F`. Hence `span(H)>=span(G)` and `span(B)>=span(F)`, ruling out strict decrease again.

Therefore initial seam cancellation is necessary. It forces agreement of the signs of the first indexed letters and the unique alignment

    q=index(first(F))-index(first(G^e)).

After computing this exact reduced `H`, suppose its support is `[u,v]`, while that of `F` is `[a,b]`. Cancellation at `F | T^-k(H^-1)` can occur only for

    k=index(last(H))-index(last(F)).

That special shift is tested directly. At every other shift there is no seam cancellation, and the support of `B` is the union of `[a,b]` and `[u-k,v-k]`. The minimum span of that union is attained at the endpoint alignments `k=u-a` or `k=v-b`. If the desired arm excludes zero and both alignments are zero, the best nonzero choices are the nearest integers-1 or+1.

Thus it suffices, for each of the two donor signs, to test the deduplicated set

    {0, u-a, v-b, index(last(H))-index(last(F)), -1, +1}.

The unrestricted prescription has at most12 candidates. The main nonterminal arm removes `k=0`; an empty-H terminal case needs only one nonzero representative. This is complete for existence of strict Phi descent in the specified exchange family, including all integer shifts, **in this exact literal frame**. It is not a completeness theorem for arbitrary cyclic reorientations, other coupled row operations, Nielsen changes, or AC search.

The compiler computes exact indexed words before accepting any decrease. The associated Laurent-polynomial row matrix has determinant one, but that abelianized fact is not used as evidence of noncommutative cancellation.

## Finite descent family and termination scope

A concrete nonterminal infinite family is

    H=z_0 z_1 z_0^-1 z_1^-1,
    G=z_0^2 z_m^-1,
    F=G H,
    (R,S)=(F t,G),  m>=2.

The pair is unimodular. The choice `e=1,q=0,k=-1` produces `(H t, F T(H^-1))`. The relevant seams are freely reduced. Its potential drops from`2m` to`m+1`, a strict decrease of`m-1`. Neither endpoint is asserted to be solved. The tests exercise this family at`m=2,3,5` in both generator frames, both relator positions, and every supplied relator sign combination.

A deterministic repeated procedure accepts the best tested strict decrease, ordered by new potential, ordinary endpoint length, elementary certificate length, and then its integer parameters. Every accepted exchange lowers the natural number Phi, so there are at most its initial Phi accepted exchanges. If every nonterminal checkpoint admits such a strict exchange, the uncapped logical procedure reaches an independently certified terminal rule. If a checkpoint admits none, it returns the precise family-specific failure. No universal completion claim follows.

The public bounded API also has an explicit `max_exchanges` limit. The cohort screen sets it to1, then gives the accepted endpoint exactly one bounded frozen-boundary retry. The planted checks additionally exercise repeated descent. Software work/word/certificate stops are kept separate from mathematical absence of a candidate.

## API, transactional bounds, and temporary minima

Two entry points are provided:

    compile_exchange(pair, stable='x', source_index=0,
                     donor_sign=1, q=0, k=1, limits=Limits())

compiles one specified exchange, without a unimodularity or descent claim, and

    compile_coupled(pair, stable='x', source_index=0,
                    require_donor_change=True, max_exchanges=1,
                    limits=Limits())

searches only the complete finite breakpoint family in a normalized unimodular literal frame. Both preserve the original ambient alphabet and relator positions. The result's `exchanges` are the accepted path, while `candidates` contains every tested candidate and its exact outcome or resource rejection.

The entire exchange is staged transactionally with the frozen bounded `Trace` core. Every elementary intermediate state is checked against the word/certificate bounds. Only a completed, exactly predicted, independently replayed exchange can be committed to the accepted path. A candidate's three source uses, four core inversions, optional orientation/conjugation operations, and evaluation charge are reserved against the same work budget. Rejected candidates consume their declared work. Elementary conjugation lengths remain separately counted.

Before constructing potentially enormous conjugator strings, the exact elementary count is compared with the available certificate cap. A regression using `k=10**100` proves that this resource check precedes word allocation. When a high-level checkpoint has candidate resource rejections and no accepted descent, it returns `coupled_candidate_resource_limit`, not `no_strict_coupled_descent`; the latter is reserved for a completed negative check.

The tracked trace also inspects the ordinary total length after **every** elementary operation, including while the donor temporarily equals the original source and while the changed source is inverted/conjugated. The shortest raw and cyclic-core totals are recorded per candidate. If a new best cyclic-core state is found, its exact candidate prefix and charged cyclic-conjugation cleanup are stored in `best_moves`. This prefix may come from an unselected exchange and is clearly identified in `best_origin`; it is not silently substituted into the accepted Phi-decreasing path.

Independent replay recomputes each candidate's entire sequence of raw and cyclic-core lengths and requires the reported minima to agree. Thus the negative ordinary-length result includes temporary states, not just exchange endpoints.

## Independent verification

The370 planted/API/resource cases comprise288 general exact exchanges across source/donor signs, roles, axes, positive/negative/zero shifts;48 arbitrary-width descent-family cases;4 empty-H terminal cases;20 tiny-budget prefixes;3 ordinary resource-cap cases; one bounded-candidate rejection distinguished from theorem failure; one enormous-shift preallocation guard; and5 invalid-API cases.

Separately, an independent indexed-word oracle compares the finite candidate prescription with a wider scan on every ordered pair of two-letter words whose indices are distinct and lie in`{-1,0,1}`. There are576 such pairs. The broad scan evaluates88,704 algebraic candidates over both donor signs, `q=-3..3`, and `k=-5..5`. The breakpoint scan evaluates2,864 candidates. Both unrestricted and nonzero-k existence decisions agree on every pair, producing1,152 agreements. This bounded check supports the independently written all-integer proof; the finite scan alone is not presented as proof for every integer shift.

Three distinct replayers check all stored successful candidate streams, accepted streams, best prefixes, and concatenated saved-checkpoint paths: the integer stack, independent repeated-string cancellation, and the unchanged AST-extracted legacy `replay_elementary` body. The legacy module is not imported, so no JIT initialization occurs. Source hashes are recorded and the frozen compiler/report hashes are checked before consuming saved prefixes.

## Exact124 results

The screen considers all496 literal `(stable generator, relator role)` calls on the124 inputs, plus130 distinct saved normalized failed checkpoints. It skips100 exact duplicate normalized frames. All2,929 saved prefix charges are included before additional work, and every candidate plus follow-up shares the1,000-unit per-input cap.

It tests680 breakpoint candidates, all completely evaluated. No word, indexed-word, certificate, or work cap is reached. The maximum observed candidate count in a frame is6; the theorem's general bound is12. Candidate streams contain7,234 elementary operations in total, including2,040 AC2 multiplications; the longest individual candidate contains18 elementary operations.

| Result | Count |
|---|---:|
| Exact saved best-state inputs | 124 |
| Literal calls | 496 |
| Additional distinct saved-checkpoint calls | 130 |
| Calls outside the required literal stable-exponent frame | 381 |
| Completed negative coupled-descent checks | 240 |
| Accepted strict donor-changing exchanges | 5 |
| Frozen-boundary retries | 5 |
| Retries ending `criterion_failed` | 5 |
| Strict ordinary-length improvements, including all candidate intermediates | 0/124 |
| Solved inputs | 0/124 |
| Total charges including saved prefixes | 12,127 |
| Maximum charges on one input | 397 |

The five accepted exchanges all arise at literal roots with `t=x`, stable source in the second relator position, and parameters `e=-1,q=1,k=1`. Each exchange uses11 elementary operations after any source-sign normalization:

| Input | Phi before | Phi after | Original best total length | New minimum total length |
|---|---:|---:|---:|---:|
| aca_31 | 4 | 3 | 17 | 17 |
| aca_45 | 6 | 5 | 19 | 19 |
| aca_61 | 6 | 5 | 20 | 20 |
| aca_77 | 6 | 5 | 21 | 21 |
| aca_107 | 6 | 5 | 22 | 22 |

The accepted exchange endpoint words and subsequent failed checkpoints are recorded exactly in the JSON artifact. The full test-plus-screen run took approximately0.872 seconds wall and0.871 seconds CPU, including independent replay and the wide finite algebra check, before writing the final JSON. This subsecond serial check required no cooldown. It supplies no runtime comparison with a heap search or complexity claim.

The124 inputs remain retained components of a bounded AC/Aut computation, an upper bound on distinct unresolved problems. The five new strict-Phi paths are not new solved rows, new ordinary-length minima, or evidence that the census count changes.

Run from the outer checkout:

    .venv/bin/python .scratch/theory_3h_20260912/worktree/research/theory_patterns_20260912/coupled_exchange_checks.py --legacy-replay-source .scratch/theory_3h_20260912/worktree/research/supermoves_20260908/certificate_decoder.py

Only the four assigned `coupled_exchange*` source/check/report files were changed. The frozen boundary/residue implementations, Astra's notes and probes, census data, and existing results were not modified. No advisor tool was available; this independent algebra/certificate audit and its durable artifacts are ready for the root's review.
