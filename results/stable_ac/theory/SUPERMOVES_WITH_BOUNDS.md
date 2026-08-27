# Universal, Orbit-Escaping Stable Andrews–Curtis Supermoves

Date: 2026-08-16

> **Superseded for the new-technique request.** The orbit-escaping construction below is still CoV/Lemma 11 with an endpoint filter, so it does not qualify as a new move. The genuinely new Lackenby-derived technique is [LACKENBY_DUAL_TREE_SUPERMOVE.md](LACKENBY_DUAL_TREE_SUPERMOVE.md). This file remains as background on bounds and discarded alternatives.

## Verdict

Every valid instance of Lemma 11 has a rigorous universal move bound. Computability is not required: a Busy-Beaver bound applies to every instance, without a thickenability or other class restriction.

Fix a prefix-free universal Turing machine `U`. For a Lemma 11 input `I`, compile the finite-branching stable-AC breadth-first search described below with `I` hard-wired, and let `K_U(I)` be the bit length of that compiled program. If `BB_U(k)` is the maximum running time of any halting `U`-program of length at most `k`, then

`d_SAC(P_I, P'_I) <= BB_U(K_U(I))`.

For any fixed self-delimiting serialization of length `N`, a compiler constant `c_U` can be chosen so that `K_U(I) <= 2N+c_U`. Hence the convenient input-size-only ceiling is

`d_SAC(P_I, P'_I) <= BB_U(2N+c_U)`.

This is the requested universal supermove: it has the full domain of Lemma 11 and its cost can be recorded symbolically even though the numeral cannot in general be computed.

`BB_U` eventually exceeds every total computable function, up to the fixed machine/compiler encoding. It is therefore a substantially larger kind of ceiling than any fixed or variable-height computable tower.

Endpoint novelty is a separate condition. The useful action is not the unrestricted bridge by itself, but the **orbit-escaping Lemma 11 supermove**:

`OrbitEscape(P,Q) := Lemma11Related(P,Q) and AutCanon(P) != AutCanon(Q)`.

For rank-two endpoints, `AutCanon` is the complete Whitehead canonical form of the relator pair, including the repository's finite symmetries: cyclic relator rotation, relator inversion, and relator exchange. Consequently every accepted endpoint is provably outside the source's `Aut(F_2)` orbit. Automorphic outputs may remain available in a separate reseeding channel, but they cannot exhaust or displace the orbit-escape actions.

The same construction gives three levels of power:

1. **Universal promised SAC bridge.** It transforms arbitrary presentation structure `P` to arbitrary structure `Q` whenever `P ~_SAC Q` is promised by a theorem or provenance certificate. Its bound is `BB_U` at the compiled search-program size. This is the maximal sound domain possible without assuming the stable Andrews–Curtis conjecture.

2. **Universal Lemma 11 removal.** Lemma 11 itself supplies the equivalence promise, so the bridge halts on every valid substitution-and-removal instance.

3. **Computable thickenable bridge.** If a numeric, computable input-size bound is desired, any two thickenable balanced presentations of the trivial group can be transformed into one another. For presentation lengths `p` and `q`, a valid explicit SAC bound is

   `2^(2^(2,000,000 p^2)) + 2^(2^(2,000,000 q^2))`.

   Thickenability is decidable. This is an arbitrary-structure-to-arbitrary-structure supermove on a large, topologically meaningful class.

There is also a useful **certified Morse–Lackenby reduction**. A discrete Morse matching can simultaneously eliminate many generator–relator pairs and change the whole presentation. Fernández gives a constructive `Q**` path of quadratic scale in the presentation-complex size. Once the resulting generalized path has `m` steps and intermediate presentation length at most `L`, Lackenby's compiler turns it into at most `4^(12Lm+3)` SAC moves.

The Busy-Beaver theorem is the universal answer. The Lackenby and Morse bounds remain valuable because they are computable or certificate-sensitive refinements.

## What the codebase currently implements

The main branch implements fixed-rank, rank-two substitution moves in `envs/ac_moves.py` and `envs/ac_s.py`. Its substitution action is a short composite of ordinary AC moves, represented on fixed-size padded arrays.

The stable change-of-variables pipeline is on `origin/research/w5/stable-ac-escape`, principally:

- `experiments/stable_ac/cov/cov.py`
- `experiments/stable_ac/solvern.py`
- `tests/stable_ac/test_cov.py`

Its branch operation is:

1. add `z = w(x,y)`;
2. replace occurrences of `w` by `z`;
3. isolate `x` or `y` in a relator;
4. invoke Lemma 11 to remove that generator;
5. relabel the two remaining generators.

`solvern.py` can search substitution moves at arbitrary fixed rank after an initial stabilization, but stabilization and destabilization are not themselves search actions. It also does not maintain an elementary SAC cost certificate. Therefore a discovered short generalized path can hide a very large, or presently unknown, elementary cost.

Existing one-hop change-of-variables outputs for AK(3) were separately tested for thickenability in the repository research. All 34 tested outputs were certified non-spherical/non-thickenable. Thus the theorem below is a new target and certificate mechanism, not a claim that the current AK(3) branches already enter the thickenable class.

The later research branches already contain a complete rank-two automorphism-orbit implementation:

- `experiments/equivalence_classes/lib/autcanon.py` performs Whitehead peak reduction, explores the entire minimum-length level set, returns a complete canonical orbit key, and carries a witnessing automorphism;
- `experiments/analysis/whitehead.py` is a separately written cross-check;
- `tests/equivalence_classes/test_equivalence.py` checks the partition, witnesses, and an independent Nielsen-reduction basis test;
- `tests/stable_ac/test_autcanon_fast.py` checks the optimized canonicalizer against the certified implementation on production, fuzz, and long-word corpora.

The existing 10,000-node, 66-presentation CoV artifact contains 6,722 applicable candidates. Recomputing its orbit classification gives:

| classification | count |
|---|---:|
| genuinely non-automorphic CoV targets | 847 (12.60%) |
| targets in the source's automorphism orbit | 5,875 (87.40%) |
| presentations with at least one non-automorphic target | 65 / 66 |
| non-automorphic targets per presentation | min 0, median 14, max 22 |
| distinct non-automorphic target orbits, globally | 368 |
| distinct new target orbits per presentation | min 0, median 7, max 10 |
| presentations with at least 5 distinct new target orbits | 61 / 66 |

Thus an orbit-escape restriction leaves a substantial action family. The data also says not to use the Boolean novelty flag as a quality score: within a presentation it has essentially zero correlation with solve cost. First filter for a new orbit, then rank the surviving targets by the already measured abelian-mass heuristic.

## Lemma 11 and the source of its unknown cost

Lemma 11 in Shehper et al., *What makes math problems hard for reinforcement learning: a case study*, states that

`P = <x_1,...,x_n,y | r_1,...,r_n,y^-1 w>`

is stably AC-equivalent to

`P' = <x_1,...,x_n | r'_1,...,r'_n>`,

where each `r'_i` is obtained by replacing `y` with `w` in `r_i`.

The proof first performs those substitutions. Since `P'` presents the trivial group, it then chooses a normal-generation identity

`w = product_{k=1}^m u_k (r'_{i_k})^(epsilon_k) u_k^-1`,

with `epsilon_k` equal to `+1` or `-1`. This identity converts the last relator `y^-1 w` to `y`, after which the generator–relator pair is deleted.

The minimum possible integer `m` is precisely the normal/algebraic area of `w` over `P'`. The paper explicitly observes that its proof supplies no bound on `m` and asks for a bound or an alternative proof.

Whether there is a computable uniform bound covering all balanced trivial presentations is tied to the unresolved balanced triviality/Magnus decision problem. A computable normal-area bound would allow enumeration of all generator witnesses up to that bound and hence decide whether a balanced presentation is trivial. This does not obstruct a rigorous noncomputable bound.

## Theorem 0: the universal Busy-Beaver SAC bridge

Fix canonical encodings of finite presentations and elementary moves (AC1)–(AC5). AC3 conjugates by one generator or its inverse, and a stabilization introduces the next canonical generator, so every presentation has finitely many one-step successors.

For presentations `P` and `Q`, run breadth-first search over the stable-AC move graph rooted at `P`. At depth `d`, there are only finitely many paths: rank can increase by at most `d`, and every state at that depth has finite branching. Compare canonical freely reduced presentations and halt when `Q` is reached.

If `P ~_SAC Q`, this algorithm halts and outputs an elementary path. Let `search_U(P,Q)` be the program consisting of the fixed search code plus hard-wired canonical encodings of `P` and `Q`. Then

`d_SAC(P,Q) <= runtime_U(search_U(P,Q)) <= BB_U(|search_U(P,Q)|)`.

The first inequality holds because emitting or discovering a path of length `d` takes at least `d` computation steps. The second is the definition of `BB_U` for a program known to halt.

### Exact optimal worst-case function

For encoding budget `N`, define

`F_SAC(N) = max { d_SAC(P,Q) : |encode(P,Q)| <= N and P ~_SAC Q }`.

The set is finite and every distance in it is finite, so `F_SAC(N)` is a rigorous exact maximum. It is the tightest possible uniform bound on all promised stable-equivalent pairs of size at most `N`. The machine argument gives

`F_SAC(N) <= BB_U(2N+c_U)`

after fixing a self-delimiting encoding and compiler. If the only goal is to charge a still larger symbolic cost, any iterate such as `BB_U(BB_U(2N+c_U))` is also valid, but it does not increase the move's semantic domain. The useful source of power is the promised equivalence, not artificially inflating an already valid ceiling.

### Universal Lemma 11 algorithm

Given a valid Lemma 11 input `I`:

1. compute the substituted target `P'` exactly;
2. run the stable-AC breadth-first search from `P` to `P'`;
3. return the first path found;
4. attach the symbolic cost `BB_U(K_U(I))` and the concrete discovered path as its certificate.

Lemma 11 proves `P ~_SAC P'`, so this partial bridge algorithm is total on the entire Lemma 11 domain. It may find a path much shorter than the lemma's normal-area construction because it searches all elementary proofs.

There is a second proof-search version that follows Lemma 11 literally: enumerate tuples `(m,i_k,epsilon_k,u_k)` and freely verify

`w = product_k u_k (r'_{i_k})^(epsilon_k) u_k^-1`.

That search also halts on every valid instance. If `A_11(N)` denotes the maximum minimum normal area over all valid encoded instances of size at most `N`, then the same hard-wiring argument gives

`A_11(N) <= BB_U(2N+c'_U)`.

This directly fills the paper's missing `m` with a rigorous universal bound.

## Theorem 1: the orbit-escaping Lemma 11 supermove

Let `P` be a rank-two presentation state with sound triviality provenance, and let `Q` be a same-rank output of the repository's change-of-variables construction. Require:

1. the stabilization, substitution, isolation, and removal hypotheses of Lemma 11 replay exactly;
2. `AutCanon(P) != AutCanon(Q)`.

Then:

- `P ~_SAC Q` by Lemma 11;
- no free-group automorphism carries the source relator tuple to the target tuple, modulo cyclic rotations, relator inversions, and exchange, by completeness of Whitehead's orbit algorithm;
- `d_SAC(P,Q) <= BB_U(|search_U(P,Q)|)` by Theorem 0.

Therefore every accepted action changes the automorphism orbit while retaining a rigorous elementary stable-AC bound on every valid instance.

The novelty wrapper is not specific to CoV: any same-rank ACM, Morse, or thickenable-bridge proposal may enter the main frontier only after the same exact orbit test. Lemma 11 is the strongest immediately usable instantiation because it already generates many such targets in this codebase.

### Action generator

For each proposed reduced word `w`—with no theorem-level word-length restriction—and for every legal `(iso_gen, iso_index)` branch:

1. construct and replay the exact CoV target `Q`;
2. compute the certified Whitehead keys of `P` and `Q`;
3. put `Q` in `OrbitEscape` if the keys differ;
4. otherwise put it in the optional `AutReseed` channel;
5. deduplicate `OrbitEscape` by the target Whitehead key, so the action budget buys distinct orbits rather than many representatives of one orbit;
6. rank new-orbit targets by ascending abelian mass, with a learned or random tie-break;
7. attach `BusyBeaver(|search_U(P,Q)|)` as the symbolic elementary cost and retain the compact Lemma 11 provenance.

The mathematical action schema permits every finite `w`. A practical RL policy may propose a finite subset, but this is a proposal-budget decision rather than a soundness or move-bound restriction.

Whitehead rejection is exact, not heuristic. A cheap invariant may reject obvious automorphic impossibilities early, but equality of cheap invariants must never be used to declare two targets automorphic.

## Theorem A: the thickenable bridge

Define

`B(t) = 2^(2^(2,000,000 t^2))`.

Let `P` and `Q` be thickenable balanced presentations of the trivial group, with total presentation lengths `p` and `q`. Then

`d_SAC(P,Q) <= B(p) + B(q)`.

### Proof

Lackenby's Theorem 1.2 gives an SAC path from `P` to a standard presentation with at most `B(p)` moves, and another from `Q` to a standard presentation with at most `B(q)` moves. Reverse the second path and concatenate it with the first. Stable AC moves are reversible, so the concatenation is an SAC path from `P` to `Q` with the stated bound.

This is stronger than Lemma 11 in structural scope: neither endpoint has to be obtained from the other by eliminating a single generator. Both presentations may have arbitrary relator structure and different ranks, subject to balance, triviality, and the decidable thickenability certificate.

### Constructive form

The proof is algorithmic:

1. Verify thickenability using the Neuwirth embedding/thickening criterion.
2. Triangularize the presentation using generalized stabilizations.
3. Build the corresponding triangulated 3-sphere.
4. Use the explicit Pachner-move simplification bound.
5. Translate the simplification back to supplementary presentation moves.
6. Compile supplementary moves to elementary SAC moves.

The useful machine artifact should normally be the compact generalized path plus its certificates. Expanding as many as `B(t)` elementary moves is neither necessary nor practical.

## Theorem B: an explicit Lemma 11 bound on thickenable outputs

Use the notation of Lemma 11 and suppose the substituted presentation

`P' = <X | R'>`

is thickenable. Set:

- `lambda = sum_i |r'_i|`;
- `s = |w|`;
- `E = 2^(700,000 lambda^2)`;
- `M = 12 E^2`.

Then a normal-generation identity sufficient for Lemma 11 exists with

`m <= s (2^(M+1) - 1)`,

and every conjugator in the identity can be chosen with length at most `2^M`.

### Derivation

Lackenby's Theorem 2.6 constructs a supplementary path from `P'` to the standard presentation whose number of moves and maximum intermediate length are each at most `E`. Lemma 2.4 replaces every elementary Nielsen move in such a path with at most `10L+3` moves of types `(0)`–`(4+)`. With `L <= E` and at most `E` original moves, the expanded path length is at most

`E(10E+3) <= 12E^2 = M`.

Lackenby's Lemma 2.2 then expresses every generator of `P'` as a product of at most

`2^(M+1)-1`

conjugates of the original relators, with conjugator length at most `2^M`. Substitute these identities into a freely reduced word `w` of length `s` and concatenate the factors. This gives the claimed bound on `m`.

The proof uses deliberately coarse constants. Its purpose is an auditable finite ceiling, not a practical rollout budget.

### Bounded substitution-and-removal algorithm

```text
[unverified] pseudocode; theorem and bounds were independently checked
bounded_remove(P, y, w):
    P_prime, substitution_ledger = substitute_y_by_w(P)
    thickening_certificate = verify_thickenable(P_prime)
    if no certificate:
        return NOT_IN_CERTIFIED_DOMAIN

    supplementary_path = lackenby_path_to_standard(P_prime,
                                                    thickening_certificate)
    generalized_path = expand_nielsen_moves(supplementary_path)
    normal_forms = back_propagate_generator_normal_forms(generalized_path)
    witness_for_w = concatenate(normal_forms[letter] for letter in w)
    sac_ledger = replay_lemma_11(P, witness_for_w)
    verify_every_word_identity_and_move(sac_ledger)
    return P_prime, sac_ledger
```

This answers the old paper's missing-`m` question on a decidable class. If the thickenability check fails, it says only that this certificate route is unavailable; it does not prove that the presentation is not SAC-trivial.

## Theorem C: the Morse–Lackenby structural compiler

Let `K(P)` be the barycentrically subdivided presentation complex of `P`, and let `Morse` be an acyclic matching with one critical 0-cell. Fernández's algorithm computes a Morse presentation `Q_M(P)` and a constructive `Q**` equivalence from `P` to `Q_M(P)`. If `k` is proportional to the number of cells, hence to total relator length, the reduction is computable in `O(k)` time and its elementary expansion/collapse ledger is bounded at quadratic scale in `k`.

This is a genuine global supermove: one matching may eliminate many generator–relator pairs and reorganize the entire presentation rather than substituting a single variable.

To compile a concrete Morse move to SAC:

1. record its fully expanded sequence of supplementary moves;
2. decompose presentation automorphisms into elementary Nielsen moves;
3. record the exact step count `m` and maximum intermediate presentation length `L`;
4. require a certified route from the Morse endpoint to a standard presentation, for example a thickenability certificate;
5. use Lackenby's Proposition 2.5 to obtain an SAC path of length at most

   `4^(12Lm+3)`.

The bound is certificate-dependent, but fully explicit after the generalized path is known. Without a certified endpoint route, Morse reduction is a sound structure-changing proposal rather than a proof of stable triviality.

## Other powerful moves and why they are secondary

| Move family | Structural power | Certificate/cost status |
|---|---|---|
| Ordinary substitution/S-move | Rewrites one relator using another | Finite, short, already implemented |
| Lemma 11 removal | Eliminates a generator after arbitrary substitution | Cost is the algebraic area `m`; no general effective bound |
| M-transformation / ACM move | Replaces a relator by a consequence modulo the others | AC-equivalent and witness-checkable, but the raw action family is infinite |
| Ivanov's generalized stable `CCT4` | Adds a generator tied to an arbitrary word | Very expressive, but infinite without a word-length cutoff and no uniform elementary bound |
| Lackenby's `(4+)` | Adds `x = w` with `|w| <= 2` | Finite action family; paths compile to SAC with explicit exponential bounds |
| Discrete Morse reduction | Simultaneously changes many cells/generators/relators | Constructive `Q**` path; SAC bound after an endpoint certificate is supplied |
| Thickenable bridge | Arbitrary certified endpoint to arbitrary certified endpoint | Explicit double-exponential SAC bound |

Panteleev and Ushakov prove that ACM equivalence and AC equivalence coincide, making ACM moves useful as learned or searched certificate proposals. Ivanov proves analogous stable equivalence results for cancellative transformations. Neither source supplies the input-size-only, finite-domain guarantee supplied by Lackenby for thickenable presentations.

## Recommended solver architecture

Do not add the new actions directly to the fixed-rank JAX environment. Extend the rank-`n` CPU stable solver first, because ranks and relator counts change.

Add the following typed generalized actions around `experiments/stable_ac/solvern.py`:

1. `OrbitEscapeLemma11(source, target, cov_provenance, aut_keys)` for the default new-orbit channel;
2. `AutReseed(source, target, automorphism_witness)` as a separately budgeted optional channel;
3. `StabilizeShort(target_generator, word)` implementing `(4+)`, restricted to `|word| <= 2`;
4. elementary Nielsen generator multiplication and inversion;
5. `MorseReduce(matching, certificate)`;
6. `ThickenableTerminal(certificate)`;
7. optionally `CertifiedConsequenceReplace(normal_witness)` for ACM proposals.

Every node should carry:

- the exact presentation;
- a generalized move ledger;
- cumulative generalized step count `m`;
- maximum intermediate length `L`;
- a symbolic bound AST supporting `BusyBeaver(program_bits)`, exact integers, sums, and expressions such as `4^(12Lm+3)`;
- source and target Whitehead keys plus any positive automorphism witness;
- independently replayable word, matching, and thickening certificates.

Search should rank compact generalized certificates, not evaluate Busy Beaver or expand the astronomical elementary path. Deduplicate the main frontier by Whitehead key. A separate verifier should replay CoV identities, independently validate automorphism witnesses and Whitehead keys, validate acyclic matchings, and verify the thickening/triangulation certificate before marking an edge proven.

The current unrestricted initialization `z = w` in the no-CoV experiment is more expressive per action than `(4+)`, but it is not a finite action family and records no elementary cost. It should remain a proposal mechanism whose output is compiled into short stabilizations or discharged by an explicit normal-generation witness.

## Hard boundary

An unconditional arbitrary-presentation bridge would settle the stable Andrews–Curtis conjecture by taking the second endpoint to be a standard presentation. No cited source proves that result.

Theorem 0 does not assume that conjecture. Its domain is every pair already guaranteed to be stable-equivalent. Lemma 11 provides exactly such a guarantee for every valid change-of-variables removal. On a pair outside that promised domain, the breadth-first search may run forever.

Likewise, the formulas in Theorem B do not apply merely because Lemma 11's input presents the trivial group. They require a verified thickenability certificate for `P'`. Existing AK(3) one-hop CoV outputs in this repository do not satisfy that check.

The recommended research targets are therefore:

- expose Theorem 1 as the default symbolic-cost CoV action and admit only distinct non-automorphic target keys on its main frontier;
- retain automorphic reseeds only as an explicitly capped auxiliary channel;
- search for a bounded `(0)`–`(4+)` or Morse path that reaches a thickenable endpoint;
- keep an exact `m,L` ledger;
- treat thickenability as a certified terminal basin;
- compile the resulting bridge using Lackenby's bounds.

This supplies both a universal noncomputable bound and sharper computable subdomain bounds without assuming the open stable AC conjecture.

## Primary sources

- Shehper et al., [What makes math problems hard for reinforcement learning: a case study](https://arxiv.org/abs/2408.15332), especially Lemma 11 and its proof.
- Lackenby, [The stable Andrews-Curtis conjecture and thickenable presentations of the trivial group](https://arxiv.org/abs/2606.06122), especially Proposition 2.1, Lemmas 2.2 and 2.4, Proposition 2.5, Theorems 1.2 and 2.6.
- Fernández, [Morse theory for group presentations](https://arxiv.org/abs/1912.00115), especially the Morse presentation construction and Remark 2.11.
- Panteleev and Ushakov, [Conjugacy search problem and the Andrews-Curtis conjecture](https://arxiv.org/abs/1609.00325), for ACM moves.
- Ivanov, [The Andrews-Curtis conjecture and its generalizations](https://arxiv.org/abs/1606.08196), for stable cancellative transformations.
- Day, [Full-featured peak reduction in right-angled Artin groups](https://arxiv.org/abs/1211.0078), for decidable automorphism-orbit membership of tuples of conjugacy classes; the free group is the discrete-graph special case.
- Bridson, [The complexity of balanced presentations and the Andrews-Curtis conjecture](https://arxiv.org/abs/1504.04187), for AC-trivial families with move lower bounds exceeding every fixed-height exponential tower and for the algebraic-area connection.
- Shehper et al., [The Two-Hump Problem: Bridging the Difficulty Gap in Mathematical Reinforcement Learning](https://arxiv.org/abs/2606.21611), for the current substitution environment and experiments.

## Verification record

The PDFs of the three bound-critical sources were downloaded to `tmp/pdfs/`, text-extracted, rendered, and visually inspected. In particular:

- Lemma 11 and the paragraph identifying the missing bound were checked on printed page 43 of arXiv:2408.15332v2.
- Lackenby's move definitions and bounds `4^(m+3)`, `2^(m+1)-1`, `10l+3`, `4^(12Lm+3)`, `2^(k l^2)` with `k <= 7*10^5`, and `2^(2^(c l^2))` with `c = 2*10^6` were checked against arXiv:2606.06122.
- Fernández's construction and quadratic transformation count were checked against Remark 2.11 of arXiv:1912.00115.
- The 847 / 6,722 candidate count and 368 distinct-new-orbit count were recomputed directly from `codex/proofs:results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` using its independently generated `aut_canon_orig` and `aut_canon_cov` fields.
- The complete Whitehead canonicalizer, its independent implementation, and its layered tests were read directly from the research branches.
