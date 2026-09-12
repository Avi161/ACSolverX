# Alternating boundary compiler: proved scope and verified outcome

The compiler implements Astra's two exact source-restored identities using only relator inversion, right multiplication by the other relator, and conjugation by one signed generator. It performs no heap search, simultaneous ambient automorphism, basis enumeration, or JIT compilation. The original `xXyY` alphabet and relator positions are preserved until the terminal relator interchange, which itself is expanded into six ordinary AC operations.

The 351 checks pass. On the exact preselected 20-row development panel there are **0 solves and 0 strict ordinary-length improvements**, with 394 total charges. Extending the same frozen policy to all **124 exact saved best-state inputs** gives **0 solves and 0 strict ordinary-length improvements**, with 2,929 total charges. The full archive is `boundary_compiler_report.json`, including exact input words, output words, every elementary certificate, and every failed checkpoint. The 124 inputs are retained components of a bounded AC/Aut computation, an upper bound on distinct unresolved problems; they are not 124 proved distinct AC classes.

## API and resource semantics

`boundary_compiler.py` exports:

- `compile_pair(pair, stable='x', source_index=0, boundary_order=('lower','upper'), limits=Limits())`: the alternating conditional procedure in one literal Magnus frame. The nominated source has stable exponent ±1 and the other relator has stable exponent zero. The pair must be unimodular. A negative nominated source is normalized by an explicitly recorded inversion.
- `compile_boundary_pass(pair, stable='x', source_index=0, side='lower', q=None, limits=Limits())`: one stable-source boundary-transport pass. Unimodularity is unnecessary. A negative source is normalized only in the indexed calculation, so its exact supplied free-reduced word is restored even when a resource limit interrupts the pass. `q` can be any integer satisfying the proved interval; its default is the interval's lower endpoint.
- `Limits(budget=1000, max_word_length=4096, max_indexed_length=2048, max_moves=100000)`: independent explicit bounds. The budget cannot exceed 1,000.

Inputs and limits are validated before recognition, including malformed words behind an over-cap first relator. Each result contains `reason`, `status`, `final_pair`, its strict `moves`, `best_pair`, its independently replayed `best_moves`, completed `passes`, the exact `failed_checkpoint`, and counters. `verified=True` means both streams replay to their specified endpoints; it does not mean a partial result is solved. Only `status='solved'` asserts the exact ordered endpoint `(x,y)`.

Charges count frame/checkpoint recognition, boundary-candidate recognition, proposed block rewrites, source-relation uses, normalization/terminal unary operations, and any optional conjugations used to certify an improved cyclic-core checkpoint. Emitted elementary conjugations and donor-restoration inversions are counted separately in `elementary_moves`. Thus a charge is an algebraic work unit, not a search pop or a constant-cost machine operation. `relation_uses_committed` counts committed AC2 multiplications, including the terminal interchange. Attempted relation uses can be charged without being committed if a resource guard rejects their transactional block.

Every replacement block is built on a bounded temporary `Trace`. Each emitted elementary state is checked against the word and certificate caps. The whole block is committed only after its predicted free word agrees and its source is restored. A resource stop therefore returns the last certified source-restored prefix, rather than a half-conjugated donor. A whole-boundary pass may be partly completed when the next block is rejected; only fully completed passes appear in `passes`. `word_limit`, `indexed_word_limit`, `certificate_limit`, and `work_limit` are implementation bounds, not failures of the mathematical criterion.

`best_pair` is the shortest total cyclic-core length observed at committed block boundaries, with a charged explicit conjugation witness when needed. It is not an exhaustive minimum over the AC class. The numerical span monitor and ordinary relator length are reported separately.

## Exact transport identity and its compiler

Write the two literal generators as `t,z`, and define `z_i=t^i z t^-i`. Magnus collection is an exact free-group identity, not quotient reduction. If the current retained source is `R0` with stable exponent `e=±1`, let `R0^e=F t`. The target has stable exponent zero and indexed spelling `G`.

Assume nonempty supports `support(F)=[a,b]`, `support(G)=[c,d]` with `b-a<d-c`. Choose

    c+1-a <= q <= d-b,
    D = t^q R0^e t^-q = F_q t.

Let `T` shift every indexed generator by one. Direct multiplication gives

    D H D^-1 = F_q T(H) F_q^-1,
    D^-1 H D = T^-1(F_q)^-1 T^-1(H) T^-1(F_q).

For lower removal use `H=z_c^k` and the first identity; for upper removal use `H=z_d^k` and the second, where `k` is the signed exponent of a current maximal boundary run. For lower removal every replacement index lies in `[c+1,d]`; for upper removal every replacement index lies in `[c,d-1]`. There is no uniqueness, monicity, sign, or multiplicity assumption on either boundary's appearances in `F` or `G`.

For the exact current target factorization `S=P H Q` and direction `s=+1` (lower) or `s=-1` (upper), set `S'=P D^s H D^-s Q`. Then

    S^-1 S' = (c1^-1 R0^(e*s) c1) (c2^-1 R0^(-e*s) c2),
    c1 = t^-q H Q,
    c2 = t^-q Q.

For example, the first conjugate expands to `Q^-1 H^-1 D^s H Q`, the second to `Q^-1 D^-s Q`; their middle `Q Q^-1` cancels and their product is exactly `S^-1 S'`. Each factor is emitted by temporarily orienting and conjugating the source, multiplying the target, and restoring the source. Conjugators are freely reduced before elementary expansion.

The current target is recollected after every committed block. Thus later suffixes are never taken from stale offsets. A replacement introduces no letter at the removed index, so the number of letters at that index strictly decreases. After finitely many blocks that endpoint disappears, and the target span strictly decreases. This proof bounds neither ordinary relator growth nor elementary certificate length.

## Unique extreme-power rule

Now the retained source is the zero-stable-exponent relator `S=G`, and the changed relator is `R=F t`. Require `span(G)<=span(F)`, a chosen boundary of `G` in exactly one **literal maximal indexed run**, and divisibility of every corresponding extreme run of `F` by its absolute exponent `m>0`.

Choose `e=±1` so that this source run is positive in `S^e`. Shift to align the selected endpoint of `G` with that of `F`, and cut

    D=t^q S^e t^-q = C A E,
    A=z_boundary^m,
    B=C^-1 E^-1.

All letters of `B` lie strictly away from the selected recipient endpoint and remain inside the recipient's old support interval. The exact errors are

    A^-1 B = E D^-1 E^-1,
    A B^-1 = C^-1 D C.

For `R=U A^eta V t`, the factor relative to the original current source `S` is

    eta=+1: sign -e, conjugator t^-q E^-1 V t;
    eta=-1: sign +e, conjugator t^-q C V t.

One source-restored multiplication replaces each copy of `A` or `A^-1`. The initial divisibility check covers every selected extreme run. Replacing a copy removes exactly `m` boundary letters before any additional cancellation and introduces none. If adjacent residual boundary runs merge after cancellation, each has exponent divisible by `m`, so the divisibility invariant survives. Finitely many replacements remove the endpoint and strictly decrease `span(F)`.

The test concerns literal indexed runs. A donor whose first and last indexed letters could be joined by a separately certified cyclic cut can fail this recognizer. Such a failure excludes the implemented sufficient syntax only. The compiler does not silently rotate the indexed donor or replace a nondivisible run by a remainder.

## Conditional termination and terminal cleanup

At a normalized unimodular checkpoint, `exp_t(R)=1` and `exp_t(S)=0`. Consequently `exp_z(S)=±1`. This remains true: power elimination leaves `S` unchanged, and stable-source transport changes `S` only by conjugating selected subwords, preserving its exponent sums.

For nonempty indexed words set `span(W)=max(index)-min(index)`; assign empty `F` span zero and immediately enter terminal cleanup. Empty `G` is incompatible with the required exponent ±1 and is rejected before the unimodular theorem can be applied.

The deterministic checkpoint rule is:

1. If `F` is empty or `span(G)=0`, perform terminal cleanup.
2. If `span(G)>span(F)`, perform stable-source transport in the first requested boundary direction.
3. Otherwise, test the requested boundary directions in order. Apply the first unique-run/divisibility candidate. If none exists, return `criterion_failed` with both recorded reasons.

Each completed nonterminal pass strictly decreases the natural number

    Phi = span(F) + span(G).

Inside each pass, the number of selected endpoint letters strictly decreases. These are separate well-founded measures: endpoint count proves the pass finishes, and `Phi` bounds the number of completed passes by its initial value. This claim does not apply to an interrupted partial pass, which is reported separately. If the explicitly tested step-3 hypothesis holds whenever it is reached, and software resource limits are removed, the algorithm must reach a terminal condition after finitely many ordinary AC operations. It does not assert that every unimodular input satisfies these checkpoints.

When `F` is empty, the normalized relator is exactly `t`. Delete each `t` or `T` occurrence from the other relator using this generator donor; a current word `P t^eta Q` is changed to `P Q` by the factor `Q^-1 t^-eta Q`. The resulting word is `z^±1`, because its z-exponent is ±1. Normalize its sign.

When `span(G)=0`, its reduced indexed word is `z_i^±1`. Conjugation by `t^i` exposes `z^±1`; normalize its sign, then delete all `z` and `Z` occurrences from `R`. Its stable exponent one forces the result to be exactly `t`. If the relator positions now contain `(y,x)`, the sequence `I1, M2, I2, M1, I1, M2` interchanges them using AC1 and AC2 alone. All terminal cases, signs, axes, and relator positions are exercised by the tests.

## Planted sufficient family and independent checks

For every integer `m>=2` and sign `eta=±1`, one planted lower-first family is

    S = z_0^m z_1^-(m+1),
    R = z_0^(eta*m) z_2^(m+1) t.

The lower power rule of modulus `m` changes `F` to `z_1^(eta*(m+1)) z_2^(m+1)`. Its lower boundary is now nondivisible by `m`, but the upper power rule of modulus `m+1` changes it to `z_1^(eta*(m+1)+m)`, which is nonempty and has span zero. Stable-source transport then makes the zero-exponent relator's span zero, and terminal cleanup solves the pair. The reflected upper-first version is tested as well. This family is a constructive stress case for alternation and non-monic elimination, not a claim of new census coverage or a disjoint mathematical classification.

The 351 finite checks comprise:

| Check | Cases |
|---|---:|
| Non-monic alternating solves, `m=2,3,5`, both endpoint directions, recipient signs, generator axes, relator positions, and input relator inversions | 192 |
| Stable-source transport with repeated extreme visits, all signs/axes/roles | 32 |
| Empty-F or span-zero-G terminal cleanup, positive/negative/zero indices, all signs/axes/roles | 96 |
| Explicit nonunique-boundary and nondivisible-boundary failure | 2 |
| Every budget from 0 through 13 preserves the source and a valid prefix | 14 |
| Word, indexed-word, and certificate resource guards, including atomic rollback | 3 |
| Empty zero fibre rejected from the unimodular theorem | 1 |
| Malformed API/input/limit rejection | 11 |

Every stored final and best prefix is replayed by the compiler's independent integer stack, a separate repeated-string-cancellation implementation, and the unchanged AST-extracted `replay_elementary` body from `research/supermoves_20260908/certificate_decoder.py`. The legacy module itself is never imported, avoiding JIT initialization. Source hashes are recorded in the JSON artifact.

## Exact best-state U124 outcome

The screen tries both literal stable generators, both source roles, and both fixed boundary orders. Each row shares a budget of 1,000 across its eight attempts. It uses maximum expanded relator length 512, indexed length 256, and 12,000 elementary moves per attempt. All malformed-frame attempts cost one recognition charge. The exact20 panel was run first; its records were reused for the full124 archive.

| Quantity | Exact20 panel | Full124 |
|---|---:|---:|
| Solved inputs | 0 | 0 |
| Strict ordinary-length improvements from the exact saved best input | 0 | 0 |
| Aggregate charges | 394 | 2,929 |
| Largest per-input charge | 42 | 63 |
| Completed stable-source boundary passes | 20 | 149 |
| Completed extreme-power passes | 4 | 48 |
| Recognized frame/order attempts ending `criterion_failed` | 30 | 230 |
| Frame/order attempts outside the literal stable-exponent frame | 130 | 762 |
| Resource-stopped attempts | 0 | 0 |

All 48 full124 power passes have `m=1`; no non-monic power pass was admitted on this cohort. There are 62 inputs with at least one completed pass. Failed boundary candidates split into 260 nonunique extreme-run conditions and 200 nondivisible recipient-run conditions. An attempt may contribute two boundary failures, so these numbers are not input counts. Across all attempts, the largest certificate contains 408 elementary moves and the largest committed elementary-state relator length is 141.

The final validation run took approximately 0.300 seconds wall and 0.299 seconds CPU for planted checks, compiler execution, and the repeated independent replays, before writing the JSON artifact. These are implementation timings for this tiny symbolic check, not a comparison with a search engine or a complexity claim. The main result is exact certificate validity and the negative coverage result; span reduction must not be presented as an ordinary-length improvement.

Run from the outer checkout:

    .venv/bin/python .scratch/theory_3h_20260912/worktree/research/theory_patterns_20260912/boundary_compiler_checks.py --inventory .scratch/theory_3h_20260912/u124_inventory.json --legacy-replay-source .scratch/theory_3h_20260912/worktree/research/supermoves_20260908/certificate_decoder.py --all-u124

Only the four assigned compiler/check/report files were intentionally changed. Astra's source notes, shared word kernel, frozen data, and prior results were not modified. No advisor tool was exposed in this worker session; the exact proofs, finite checks, and artifacts are saved for the root's independent review.
