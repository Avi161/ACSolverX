# S19 — the number `m` in Lemma 11 is an algebraic area

Session branch: `claude/stable-ac-conjecture-stabilization-rwo9as` (fable line; must be
merged into `fable/proof` by the user). Written 2026-08-04.
**This file only ADDS.** It edits no existing `.md` and no existing code. Its one new
script is `experiments/stable_ac/fable/s19_area_probe.py` (new file, new output path
`results/stable_ac/fable/s19_area_probe.json`).

**Which of the three claims each section is about.** Every statement below concerns the
*stable* framework (AC1–AC5). The hypothesis "presents the trivial group" is used
throughout and is sharp — nothing here is claimed for balanced presentations of nontrivial
groups. Nothing here asserts that any particular presentation is AC-trivial or stably
AC-trivial; §§1–2 are about the *cost* of one supermove that is already known to exist.

---

## 0. What this file is, and its sourcing ledger

Lemma 11 ("Substitution and Removal") of arXiv:2408.15332 says: if
`P = ⟨x₁,…,xₙ, y | r₁,…,rₙ, y⁻¹w⟩` is a presentation of the trivial group with `w` a word
in the `xᵢ`, then `P' = ⟨x₁,…,xₙ | r₁',…,rₙ'⟩` is **stably AC-equivalent** to `P`, where
`rᵢ'` is `rᵢ` with every `y` replaced by `w`.

Its proof needs `w = w₁(r'_{i₁})^{±1}w₁⁻¹ ⋯ w_m(r'_{i_m})^{±1}w_m⁻¹`, and the authors write
"**Note that `m` may be much larger than `n`**" and later state as an explicit open problem
that their proof yields **no bound on `m`**, so — unlike plain substitution, whose cost is
linear in the relator lengths — the supermove has no known move count.

This file proves that the minimal such `m` is the **algebraic area** of `w` over `P'`, works
out exactly what "bounding `m`" therefore means, and reports what is and is not thereby
obtained.

### 0.1 Sourcing

| item | status | how |
|---|---|---|
| Lemma 11 statement **and its full proof** | **VERIFIED-FROM-SOURCE, this session** | `github.com/ammedmar/ac_paper` @ `d86984d`, file `sec/stable.tex`, lines 28–33 read off disk. Clone present at the session scratchpad; re-clonable (GitHub HTTPS works from this container). |
| The authors' open-problem paragraph ("absence of a bound on `m` … would be very useful") | **VERIFIED-FROM-SOURCE, this session** | same file, line 38 (paragraph beginning "We note that, much like the substitution move…"). |
| van Kampen's lemma (algebraic area = diagram area) | **CLASSICAL, not re-verified from a source in this clone** | textbook (van Kampen 1933; Lyndon–Schupp Ch. V). §1.4 gives the construction in both directions so the file does not depend on an unread citation for its content. |
| Adian–Rabin (triviality of a finite presentation is undecidable) | **CLASSICAL, not re-verified from a source in this clone** | used **only** in Proposition 4.2, which is a side remark; Theorems 1–4 do not use it. |
| Openness of the triviality problem for *balanced* presentations ("Magnus's problem") | **RELAYED, 3 hops** | `S2_LITERATURE_HIGH_RANK.md` §1.3 → `.claude/agents/ac-advisor.md` on `origin/codex/proofs` → Lackenby arXiv:2606.06122's open-question list. Used **only** for the route verdict in §5, never inside a proof. |
| Bridson (rank ≥ 4) / Lishak (rank 2) lower bounds | **RELAYED, 3 hops, AND NOT USED** | see §3. I have not read either paper. |

### 0.2 The literature check the task demanded, run in this session

```
$ ls literature/
fake_surfaces
```

`literature/` is gitignored and this clone contains **only** `literature/fake_surfaces/`.
There is no Bridson paper, no Lishak paper, no Lackenby PDF, and no MMS02 on this disk.
Every statement attributed to those works below is marked RELAYED or UNSOURCED and is
**quarantined in §3**, which no other section depends on.
(Filed trap: `experiments/lessons/literature-absent-in-cloud-clones.md`.)

---

## 1. `m` is an algebraic area

### 1.1 Setup and conventions

Fix `X = {x₁,…,xₙ}`, `F = F(X)` the free group on `X`, and `F⁺ = F(X ∪ {y})`. Let

* `P = ⟨X, y | r₁,…,rₙ, y⁻¹w⟩` with `rᵢ ∈ F⁺` and `w ∈ F`;
* `π : F⁺ → F` the **retraction** `π(xᵢ) = xᵢ`, `π(y) = w`;
* `rᵢ' := π(rᵢ)` — this is exactly "`rᵢ` with all occurrences of `y` replaced by `w`",
  freely reduced;
* `R' := (r₁',…,rₙ')`, a tuple of *elements* of `F`; `N' := ⟨⟨R'⟩⟩_F` its normal closure;
* `P' = ⟨X | r₁',…,rₙ'⟩`.

`|v|` is the length of the freely reduced word representing `v ∈ F`.
Moves are the project numbering of `FRAMING.md` §1 (AC1 invert, AC2 multiply, AC3
conjugate, AC4 stabilize, AC5 destabilize, (0) free reduction).

**Lemma 1.1 (the authors' argument, restated through `π`).** If `P` presents the trivial
group then `P'` presents the trivial group; in particular `N' = F`.

*Proof.* `π` sends every relator of `P` into `N'`: `π(rᵢ) = rᵢ' ∈ N'` and
`π(y⁻¹w) = w⁻¹w = 1`. Hence `π` descends to a homomorphism `π̄ : G(P) → G(P')`, which is
surjective because `π` is surjective on generators. `G(P) = 1` forces `G(P') = 1`, i.e.
`N' = F`. ∎

(The paper's proof factors this through `P̃ = ⟨X, y | r₁',…,rₙ', y⁻¹w⟩` and a map
`φ(xᵢ) = xᵢ, φ(y) = w`. `π` is that `φ` applied before the substitution; using it directly
is what makes Theorem 2(b) below possible, because it also kills the relator `y⁻¹w`.)

*Side remark (consistency).* No `rᵢ'` can be trivial in `F`: if it were, `P'` would be a
presentation with `n` generators and at most `n−1` non-empty relators, so `H₁(P') ≠ 0` and
`P'` would not present the trivial group, contradicting Lemma 1.1 (for `n ≥ 1`).

### 1.2 Three quantities

**(A) The Lemma-11 number.** Let

> `M(P, w) := { m ≥ 0 : ∃ u₁,…,u_m ∈ F, i₁,…,i_m ∈ {1,…,n}, ε₁,…,ε_m ∈ {±1} with`
> `  w = u₁(r'_{i₁})^{ε₁}u₁⁻¹ ⋯ u_m(r'_{i_m})^{ε_m}u_m⁻¹  in F }`

— the set of values of `m` that a realization of the authors' proof can use. Non-empty by
Lemma 1.1.

**(B) Algebraic area (a.k.a. free-group area over the normal closure).** For `v ∈ N'`,

> `Area_{R'}(v) := min { m ≥ 0 : v = ∏_{k=1}^m u_k (r'_{i_k})^{ε_k} u_k⁻¹ in F }`.

This is a function of the *element* `v` and of the *elements* `rᵢ'` — it does not see
spellings, unreduced forms, or cyclic permutations. (Every cyclic permutation of `rᵢ'` is a
conjugate of `rᵢ'` in `F`, and conjugating a factor only changes `u_k`.)

**(C) van Kampen (diagram) area.** Let `R'^sym` be the symmetrized set: all freely reduced
cyclic permutations of `(rᵢ')^{±1}`. For `v ∈ N'`, `Area^{vK}_{R'}(v)` is the minimal number
of 2-cells in a van Kampen diagram over `⟨X | R'^sym⟩` whose boundary label, read from a
basepoint on `∂D`, is the reduced word representing `v`.

### 1.3 The identification

> **Theorem 1 (Identification).** Let `P = ⟨X, y | r₁,…,rₙ, y⁻¹w⟩` be a presentation of the
> **trivial group**, `w ∈ F(X)`, and let `P'`, `R'` be as in §1.1. Then
>
> **`min M(P, w) = Area_{R'}(w) = Area^{vK}_{R'}(w)`.**
>
> In words: the minimal `m` in the proof of Lemma 11 is exactly the algebraic area of `w`
> over the derived presentation `P'`, and equals the minimal number of 2-cells of a van
> Kampen diagram over `P'` with boundary word `w`.

*Proof.*

**(a) `min M(P, w) = Area_{R'}(w)`.** By inspection of the proof of Lemma 11 (read from
source, §0.1), the expression for `w` is used only to convert the relator `y⁻¹w` into `y`,
and the proof imposes **no** condition on `u_k, i_k, ε_k` beyond the displayed equality in
`F`. Conversely every algebraic expression is usable: `P̃ = ⟨X, y | r₁',…,rₙ', y⁻¹w⟩`
carries each `r'_{i_k}` as a relator, so AC3 supplies `u_k r'_{i_k} u_k⁻¹`, AC1 supplies the
sign, and AC2 multiplies it into the target relator. Hence `M(P, w)` is *literally* the set
of lengths of algebraic expressions for `w` over `R'`, and its minimum is `Area_{R'}(w)`.
(This half is a definitional unwinding. Its whole content is the observation that nothing
else in the proof constrains `m` — which is why the quantity is an invariant of `(P', w)`
and not of the proof.)

**(b) `Area^{vK}_{R'}(w) ≤ Area_{R'}(w)`.** Given an expression with `m` factors, build the
*wedge of lollipops*: a basepoint `∗`, and for each `k` a path labelled by the reduced word
`u_k` from `∗` followed by a loop labelled by the reduced word for `(r'_{i_k})^{ε_k}`, then
back along `u_k⁻¹`. Fill each loop with a 2-cell (its label is in `R'^sym`). The result is a
planar, simply connected 2-complex with `m` 2-cells whose boundary circuit reads the
*unreduced* word `u₁ρ₁u₁⁻¹⋯u_mρ_mu_m⁻¹`, which freely reduces to `w`. Repeatedly identifying
adjacent inverse edge pairs on the boundary (the standard folding step) removes exactly the
free cancellations and never creates a 2-cell; the result is a van Kampen diagram with
boundary label the reduced word `w` and at most `m` 2-cells. Hence `Area^{vK} ≤ m` for every
expression, so `Area^{vK} ≤ Area`.

**(c) `Area_{R'}(w) ≤ Area^{vK}_{R'}(w)`.** Let `D` be a van Kampen diagram of area `m` with
basepoint `∗ ∈ ∂D` and boundary label `w`. For each 2-cell `c_k` pick a vertex `p_k` on `∂c_k`
and a path `γ_k` in `D^{(1)}` from `∗` to `p_k`; let `ρ_k` be the label of `∂c_k` read from
`p_k` in a fixed orientation, so `ρ_k ∈ R'^sym`. The standard induction on `m` (peel off a
2-cell meeting `∂D`, or cut along an arc when `D` has a cut vertex) gives
`w = ∏_{k=1}^m γ_k ρ_k γ_k⁻¹` in `F`. Each `ρ_k` is a cyclic permutation of some
`(rᵢ')^{±1}`, hence `ρ_k = v_k (rᵢ')^{±1} v_k⁻¹` for an explicit `v_k`; absorbing `v_k` into
`γ_k` gives an expression with **exactly `m`** conjugate factors of the `(rᵢ')^{±1}`. Hence
`Area ≤ m`, so `Area ≤ Area^{vK}`. ∎

**Where the gap is, stated plainly.** Parts (b) and (c) are the two halves of van Kampen's
lemma. The constructions are given above in full outline, but the two standard technical
steps — that boundary folding does not create 2-cells, and the peeling induction in (c) —
are quoted at textbook level of detail, not re-derived from first principles. They are
classical and were **not** re-verified against a source in this clone (§0.1). Part (a), which
is the part that actually connects to Lemma 11 and is the novel content of Theorem 1, is
proved here in full and depends on nothing external.

### 1.4 Bound-direction accounting (read this before quoting Theorem 1)

`experiments/lessons/parallel-runs-and-bound-direction.md` is this line's most expensive
recurring error, and it has already recurred once in prose. So, explicitly:

* `min M(P, w) = Area_{R'}(w)` is an equality, but its two readings live on opposite sides:
  * **LOWER side.** *Every* expression has `m ≥ Area_{R'}(w)`. No cleverness in choosing the
    `u_k` can go below the area. So a **lower bound on the area is a lower bound on `m`** —
    it certifies that the supermove is genuinely expensive, for every realization.
  * **UPPER side.** The area is *attained*: some expression has `m = Area_{R'}(w)`. So an
    **upper bound on the area is an upper bound on the best achievable `m`** — this is the
    side the authors are asking for.
* Corollary of the direction rule: **any theorem that CONSTRUCTS an expression, a diagram, a
  trivialization, or a witness bounds the area from ABOVE and can never be used to say
  "`m` must be at least …".** Conversely any quotient/homological/isoperimetric obstruction
  bounds it from BELOW and can never be used to say "`m` is at most …".
* The one measurement in §4 that returns a number for a nontrivial presentation
  (`Area_{AK(2)}(x) ≥ 4`) is a **LOWER** bound. The `x^k` computation in §4 is **exact**
  (both sides proved).

---

## 2. What "bounding `m`" is, precisely

### 2.1 From area to conjugator length

> **Lemma 2.1 (conjugator normalization).** Let `v ∈ N'` with `Area_{R'}(v) = m`, let
> `L = maxᵢ |rᵢ'|`. Then there is an expression for `v` with **exactly `m`** factors and
> `|u_k| ≤ mL + |v|` for every `k`.

*Proof.* Take a van Kampen diagram `D` for `v` of area `m` (Theorem 1(c)). Iteratively delete
leaf edges of `D` that lie on no 2-cell; since the boundary word is reduced, such an edge
would force an adjacent cancelling pair in the boundary label, so after finitely many
deletions none remain and neither the area nor the boundary label has changed. Now every
edge of `D` either lies on the boundary of some 2-cell — there are at most `Σ_k |∂c_k| ≤ mL`
of those — or is traversed twice by `∂D`, of which there are at most `|v|/2`. So
`#edges(D) ≤ mL + |v|`, and the paths `γ_k` of Theorem 1(c) may be taken simple, hence of
length at most `#edges(D)`. ∎

Lemma 2.1 is what makes the whole subject *effective*: a bound on `m` alone automatically
bounds the conjugators too, so "bounded `m`" and "bounded expression" are the same
condition, and the search for an expression of area `≤ m` is a **finite** search.

### 2.2 The AC cost of the supermove, from both sides

> **Theorem 2 (two-sided cost).** Let `P = ⟨X, y | r₁,…,rₙ, y⁻¹w⟩` present the trivial
> group, and put `A := Area_{R'}(w)`, `L := maxᵢ |rᵢ'|`, `ℓ := |w|`.
>
> **(a) UPPER bound (the direction the authors want).** `P` can be carried to `P'` by
> `C_sub + 3A + 2A(AL + ℓ)` moves of type AC1–AC3 followed by a single AC5, where `C_sub` is
> the cost of the plain substitution supermove (linear in the relator lengths — the authors'
> own count). In particular the supermove costs `O(A²L + Aℓ) + C_sub` elementary moves:
> **a bound on `m` yields a bound on the number of AC moves.**
>
> **(b) LOWER bound (holds for every realization, not just the authors' proof).** Call a
> route a *single-destabilization realization* if it consists of `N` moves of type AC1, AC2,
> AC3 and (0) applied to the tuple `(r₁,…,rₙ, y⁻¹w)` inside `F⁺`, producing a tuple one of
> whose entries is a single generator letter `z ∈ X ∪ {y}`, followed by one AC5 removing `z`.
> Then
>
> `N ≥ log₂ Area_{R'}(π(z))`,  where `π(y) = w` and `π(xⱼ) = xⱼ`.
>
> In particular any single-destabilization route that removes `y` costs at least
> `log₂ Area_{R'}(w)` moves.

*Proof of (a).* First run the substitution supermove to reach
`P̃ = ⟨X, y | r₁',…,rₙ', y⁻¹w⟩` (`C_sub` moves; the paper's own construction, which is the
usual "multiply `rᵢ` by conjugates of `y⁻¹w` until every `y` is gone"). Take an optimal
expression, normalized by Lemma 2.1 so that `|u_k| ≤ AL + ℓ`. Invert `y⁻¹w` (1 AC1 move) to
get `w⁻¹y`. For `k = 1,…,A`: conjugate the relator `r'_{i_k}` by `u_k` (`|u_k|` AC3 moves),
invert it if `ε_k = −1` (1 AC1), left-multiply the target relator by it (1 AC2), then undo
the inversion and the conjugation (`1 + |u_k|` moves) so `P'`'s relators are restored. After
all `A` factors the target relator is `(∏_k u_k(r'_{i_k})^{ε_k}u_k⁻¹)·w⁻¹y = w·w⁻¹y = y`.
Since `r₁',…,rₙ'` contain no `y`, AC5 removes `y`, leaving `P'`. Total beyond `C_sub`:
`1 + Σ_k (2|u_k| + 3) ≤ 3A + 2A(AL + ℓ)` for `A ≥ 1` (absorbing the leading 1; `A = 0` means
`w = 1` and the supermove is `C_sub + 1 + `AC5). ∎

*Move-convention note.* The count above charges `|u_k|` moves for conjugating a relator by
`u_k`, i.e. it uses the **generator-only** conjugation move (Lackenby's (3), and the
conservative reading). Under `FRAMING.md`'s AC3, which conjugates by an arbitrary word in
one move, the same route costs `≤ 4A` moves beyond `C_sub` and Lemma 2.1 is not needed for
the upper bound at all. The bound as stated is therefore valid in both conventions; only the
lower bound of part (b), which is convention-independent, is used elsewhere.
`FRAMING.md` trap 5 (papers permute the move numbers) applies — check any paper's own
definitions before transporting these counts.

*Proof of (b).* Two ingredients.

*Doubling Lemma.* Fix a family `G = (g₁,…,g_N)` in a free group `Φ` and let `a_G(v)` be the
minimal number of conjugate factors of the `gⱼ^{±1}` expressing `v` (`= ∞` if none). Then
`a_G` is (i) inversion-invariant — inverting `∏_{k=1}^m u_kρ_ku_k⁻¹` reverses the product and
inverts each factor, giving `m` factors again; (ii) subadditive, `a_G(vv') ≤ a_G(v)+a_G(v')`;
(iii) conjugation-invariant, `a_G(uvu⁻¹) = a_G(v)`. Moves AC1, AC3 and (0) therefore leave
`max_i a_G(tᵢ)` unchanged over a relator tuple `(t₁,…,t_N)` — (0) because `a_G` is a function
of the group element — and AC2 at most doubles it. Since `a_G(gⱼ) = 1`, after `N` moves from
the initial tuple every entry `t` satisfies `a_G(t) ≤ 2^N`.

*The retraction.* Apply the Doubling Lemma in `Φ = F⁺` with `G = (r₁,…,rₙ, y⁻¹w)`. The final
tuple contains the word `z`, so `z = ∏_{k=1}^{M} v_k s_k^{δ_k} v_k⁻¹` in `F⁺` with `M ≤ 2^N`
and each `s_k ∈ {r₁,…,rₙ, y⁻¹w}`. Apply the homomorphism `π : F⁺ → F`. Then
`π(rᵢ) = rᵢ'` and `π(y⁻¹w) = 1`, so the factors with `s_k = y⁻¹w` disappear and

`π(z) = ∏ π(v_k) (π(s_k))^{δ_k} π(v_k)⁻¹`

exhibits `π(z)` as a product of at most `M ≤ 2^N` conjugates of the `(rᵢ')^{±1}`. Hence
`Area_{R'}(π(z)) ≤ 2^N`, i.e. `N ≥ log₂ Area_{R'}(π(z))`. ∎

**Why (b) matters.** The authors ask for "a bound on `m`, **or an alternative proof of the
lemma that establishes such a bound**". Theorem 2(b) says the second option cannot dodge the
first: the area is an obstruction to *any* single-destabilization route, not an artifact of
their argument. What (b) does **not** cover: routes that stabilize again (use AC4) partway,
or destabilize more than once. Those are outside "the supermove" as defined and are not
claimed here.

**Corollary 2.2.** `log₂ A ≤ N_min ≤ C_sub + 3A + 2A(AL + ℓ)`, where `N_min` is the least
cost of a single-destabilization realization. So `N_min` is finite iff `A` is finite, and
bounded iff `A` is bounded: **the authors correctly located the obstruction, and Theorem 1
names it.** The gap between the two sides is exponential and is not closed here.

### 2.3 The uniform statement: `m` *is* a Dehn function

For a finite presentation `Q = ⟨X | R⟩` write `|Q| = Σ_{r ∈ R} |r|` (total relator length;
generators are free). If `Q` presents the **trivial group** then every word of `F(X)` is
null-homotopic, so its Dehn function is

> `δ_Q(k) := max { Area_R(v) : v ∈ F(X), |v| ≤ k }`  (finite for every `k`; see Cor. 3.1)

with the maximum over *all* words of length `≤ k`. Define

* `D(ℓ) := max { δ_Q(ℓ) : Q balanced, presents the trivial group, |Q| ≤ ℓ }`;
* `m*(L) := max { min M(P, w) : P = ⟨X,y | r₁,…,rₙ, y⁻¹w⟩ a **balanced** presentation of the
  **trivial group** with `Σᵢ|rᵢ| + |y⁻¹w| ≤ L` }`.

> **Theorem 3 (uniform reformulation).** For all `ℓ, L ≥ 1`:
>
> `D(ℓ) ≤ m*(2ℓ + 1)`  and  `m*(L) ≤ D(L²)`.
>
> Hence **a bound on `m` uniform over balanced trivial-group presentations of total length
> `L` is exactly a bound on the Dehn functions of balanced presentations of the trivial
> group, up to squaring the length parameter** — and the two are bounded by computable
> functions simultaneously.

*Proof.* **(`D(ℓ) ≤ m*(2ℓ+1)`.)** Let `Q = ⟨X | r₁,…,rₙ⟩` be balanced, present the trivial
group, `|Q| ≤ ℓ`, and let `v ∈ F(X)` with `|v| ≤ ℓ` realize `δ_Q(ℓ)`. Put
`P = ⟨X, y | r₁,…,rₙ, y⁻¹v⟩`. `P` is balanced (`n+1` generators, `n+1` relators); it presents
the trivial group (adjoining `y` and the relation `y = v` to the trivial group `Q` leaves it
trivial); its total length is `≤ ℓ + 1 + ℓ`. No `rᵢ` contains `y`, so `rᵢ' = rᵢ` and `P' = Q`.
By Theorem 1, `min M(P, v) = Area_Q(v) = δ_Q(ℓ)`. Hence `δ_Q(ℓ) ≤ m*(2ℓ+1)`; take the max
over `Q`.

**(`m*(L) ≤ D(L²)`.)** Let `P` be admissible for `m*(L)`. By Lemma 1.1, `P'` presents the
trivial group; it is balanced; and `|rᵢ'| ≤ |rᵢ|·max(1,|w|)` since each of the `≤ |rᵢ|`
occurrences of `y^{±1}` is replaced by a word of length `|w|`, so `|P'| ≤ L·L`. Also
`|w| ≤ L ≤ L²`. By Theorem 1, `min M(P,w) = Area_{P'}(w) ≤ δ_{P'}(L²) ≤ D(L²)`. ∎

> **Corollary 3.1 (existence of a bound is trivial; the question is effectiveness).**
> `m*(L) < ∞` for every `L`.

*Proof.* In a balanced presentation of the trivial group no relator is the empty word (else
`H₁ ≠ 0`), so `n + 1 ≤ L` and the alphabet has at most `2L` letters; there are therefore
finitely many admissible `P` of total length `≤ L`, and each has a finite `min M(P,w)` by
Lemma 1.1. ∎

So the authors' open problem is **not** "does a bound exist" — it does, for trivial counting
reasons. It is "is there an *explicit / computable* bound, and how fast does it grow". Note
also that no bound in terms of `n` alone or of the number of relators can exist: §4 shows
`m = k` at rank `n = 1`. A bound must be a function of the *lengths*, which is exactly how
the authors phrase it.

### 2.4 The exact computability status

> **Theorem 4.** The following are equivalent.
> 1. There is a computable `f : ℕ → ℕ` with `m*(L) ≤ f(L)` for all `L` — i.e. the authors'
>    open problem has a positive answer in the uniform effective form they state it.
> 2. There is a computable `g` with `D(ℓ) ≤ g(ℓ)` for all `ℓ`.
> 3. The triviality problem for **balanced** finite presentations is decidable.
> 4. `L ↦ m*(L)` is a computable function.

*Proof.* (1) ⇔ (2) is Theorem 3 (`f(L) := g(L²)` and `g(ℓ) := f(2ℓ+1)` are computable when
`g`, resp. `f`, is). (4) ⇒ (1) is immediate.

**(2) ⇒ (3).** Let `Q = ⟨X | r₁,…,rₙ⟩` be balanced with `|Q| = ℓ`. Claim: `Q` presents the
trivial group iff for every generator `xⱼ` there is an expression
`xⱼ = ∏_{k≤m} u_k rᵢ_k^{±1} u_k⁻¹` with `m ≤ g(ℓ)` and `|u_k| ≤ g(ℓ)ℓ + 1`. (⇐) If all `xⱼ`
lie in `⟨⟨R⟩⟩` then `⟨⟨R⟩⟩ = F(X)` and `Q` presents the trivial group. (⇒) If `Q` presents
the trivial group then `Area_R(xⱼ) ≤ δ_Q(ℓ) ≤ g(ℓ)` — note `|xⱼ| = 1 ≤ ℓ` — and Lemma 2.1
normalizes the conjugators to length `≤ g(ℓ)·ℓ + 1`. The claim's right-hand side is a finite
search (finitely many `m`, finitely many `u_k` of bounded length, finitely many `i_k, ε_k`),
so triviality is decidable.

**(3) ⇒ (4).** Given `L`, enumerate the finitely many presentations `P` of total length `≤ L`
that are balanced and have a distinguished relator of the form `y⁻¹w`; use (3) to keep those
presenting the trivial group. For each survivor, `w ∈ N'` by Lemma 1.1, so the following
terminates: for `m = 0, 1, 2, …` search all expressions with `m` factors and `|u_k| ≤ mL' + |w|`
(`L' = maxᵢ|rᵢ'|`) — a finite search by Lemma 2.1, and by Lemma 2.1 again the first `m` for
which it succeeds is `Area_{R'}(w) = min M(P,w)`. Take the maximum. ∎

> **Proposition 4.2 (the balanced hypothesis carries the whole theorem).** There is **no**
> computable `h` such that every finite (not necessarily balanced) presentation `⟨X|R⟩` of
> the trivial group with `Σ|r| ≤ ℓ` satisfies `Area_R(xⱼ) ≤ h(ℓ)` for all `j`.

*Proof.* The argument of (2) ⇒ (3) applies verbatim without the balancedness hypothesis and
would decide triviality for arbitrary finite presentations, contradicting Adian–Rabin.
[Adian–Rabin is CLASSICAL and was not re-verified in this clone — §0.1. This proposition is a
side remark; nothing else in this file uses it.] ∎

So: in the general setting the answer to "is there a computable bound on `m`?" is a flat
**no**, and the *only* reason the balanced case is open is that Magnus's problem is open.

---

## 3. What the (unread) literature would contribute — quarantined

**This section is quarantined by design.** §§1, 2 and 4 do not cite it and survive intact if
every word of it is wrong.

### 3.1 The relay, and its hop count

`S2_LITERATURE_HIGH_RANK.md` §1.3 records, from `.claude/agents/ac-advisor.md` on
`origin/codex/proofs` (a *different* agent line's ground-truth file), which itself restates
Lackenby arXiv:2606.06122:

> **Thm 1.1** — Bridson (rank ≥ 4) and Lishak (rank 2) lower bounds: AC-trivializable
> presentations of length ≤ 24(ℓ+1) needing a tower of 2s of height log₂ ℓ; both survive
> stabilization.

That is **three hops** from Bridson and Lishak (advisor file → Lackenby → the original
papers), and `ls literature/` (§0.2) confirms none of the three artifacts is on this disk.
**I have not read Bridson. I have not read Lishak. I have not read Lackenby.** [RELAYED]

### 3.2 The direction check — and the relayed statement fails it

The relayed statement is a lower bound on **the number of AC moves** needed to trivialize.
The quantity we need bounded from below is **the area `m`**. These are different quantities,
and the Doubling Lemma of Theorem 2(b) tells us exactly which way the implication runs:

* **Area ⇒ moves (valid).** If `Area_R(xⱼ) > 2^N` for some generator, then no AC1–AC3
  sequence of length `≤ N` trivializes `⟨X|R⟩`, because the final tuple would have to contain
  the word `xⱼ` and every entry after `N` moves has area `≤ 2^N`. **An area lower bound is an
  AC-move lower bound.**
* **Moves ⇒ area (NOT valid as relayed).** A large lower bound on the number of moves says
  nothing about the area: the implication above has no converse, and nothing in the relayed
  sentence mentions area, isoperimetry, or normal-closure certificates.

Therefore, **as relayed, Lackenby's Theorem 1.1 supplies no lower bound on `m` whatsoever.**
The tempting inference — "those families need a tower of moves, so `m` is a tower" — is
exactly backwards, and is the failure mode filed in
`experiments/lessons/parallel-runs-and-bound-direction.md`. Recording it here so the next
session does not re-derive it.

### 3.3 What *would* transfer, and what would have to be checked to know

[UNSOURCED — this paragraph is a conjecture about a proof I have not read, and nothing
depends on it.] The usual mechanism for proving a lower bound on AC-trivialization length is
to lower-bound a certificate size that AC moves can only double — which is precisely our
`a_G`, i.e. an area. If Bridson's and Lishak's bounds are proved that way, then the
*primitive* object in their proofs is an isoperimetric (area) lower bound and it would
transfer to `m` verbatim, giving tower-type lower bounds on `m*(L)` and answering the
authors' question negatively in the strongest form. Two things would have to be verified
against the actual papers before any such claim is written down:

1. that the families are **balanced presentations of the trivial group** (the relay says
   "AC-trivializable presentations", which by definition are — but that is my reading of a
   third-hand sentence, not a source);
2. that the lower bound is **on an area/certificate quantity**, not only on a move count
   obtained by some other route (e.g. a counting or an invariant-theoretic argument that
   does not pass through areas).

**Verdict of §3: no lower bound on `m` is obtained from the literature in this session.**
The only lower bounds established here are the unconditional ones of §4.

---

## 4. Exact and measured values of `m`

Script: `experiments/stable_ac/fable/s19_area_probe.py` (new file).
Artifact: `results/stable_ac/fable/s19_area_probe.json` (new path; `ps -eo pid,etime,args`
checked before launching — the four concurrently running jobs are `s12_hunt`,
`s17_transition_table` and `s18_s5_chain_audit`, none of which touches this path).
Total compute: well under 4 minutes; the free-group search obeyed a 1,000-node cap.

### 4.1 Rank 1 — exact, and it already settles two things

`P = ⟨x, y | x, y⁻¹x^k⟩` is balanced, presents the trivial group, and has total length
`k + 2`. Here `r₁ = x` contains no `y`, so `P' = ⟨x | x⟩` and `w = x^k`.

> **`Area_{⟨x|x⟩}(x^k) = k`, exactly.**
> *Lower:* `F(x) = ℤ` is abelian, so `x^k = ∏_{j=1}^m u_j x^{ε_j} u_j⁻¹ = x^{Σ ε_j}` forces
> `Σ ε_j = k`, hence `m ≥ k`. *Upper:* `x^k = x·x⋯x` uses `k` factors. ∎ [PROVED]

Consequences, both unconditional:

* **`m*(L) ≥ L − 2` for all `L ≥ 3`.** An explicit, unconditional lower bound on the uniform
  quantity of Theorem 3. (Modest, but it is the only lower bound on `m*` this session
  actually establishes; contrast §3.)
* **No bound in terms of the rank can exist.** Here `n = 1` and `m = k` is unbounded. This is
  the sharp form of the authors' remark "`m` may be much larger than `n`".
* It also shows a bound cannot be a constant: the Dehn function of the *trivial group* is
  presentation-dependent and unbounded in `k` (`δ_{⟨x|x⟩}(k) = k`), consistent with
  Corollary 3.1's "finite for each `L`" and with Theorem 3.

The BFS in the script independently reproduces the upper bound `k` for `k = 1,…,8` with 3–11
nodes popped, matching the abelianization lower bound exactly. [MEASURED, agrees with PROVED]

### 4.2 Rank 2, standard presentation — exact

`P' = ⟨x, y | x, y⟩` (balanced, presents the trivial group; Todd–Coxeter completes at index
1). `w = [x,y] = xyx⁻¹y⁻¹`, i.e. the Lemma-11 datum
`P = ⟨x, y, z | x, y, z⁻¹xyx⁻¹y⁻¹⟩` (balanced, presents the trivial group, total length `1 + 1 + 5 = 7`).

> **`Area_{⟨x,y|x,y⟩}([x,y]) = 2`, exactly.**
> *Upper:* `[x,y] = x · (y x⁻¹ y⁻¹)` — two conjugate factors (`u₁ = 1, ε₁ = +1` on `x`;
> `u₂ = y, ε₂ = −1` on `x`). Verified symbolically by the script.
> *Lower:* a one-factor expression `u g^{±1} u⁻¹` is conjugate to a generator and so has
> cyclically reduced length 1, whereas `[x,y]` is cyclically reduced of length 4; the script
> also confirms exhaustively that no `u` with `|u| ≤ 6` works. ∎ [PROVED + MEASURED]

Note this is *strictly smaller* than `|w|`: area is not length, which is the whole reason
Theorem 1 is worth stating.

### 4.3 AK(2) — a genuine balanced trivial presentation; lower bound only

`P' = AK(2) = ⟨x, y | xyx(yxy)⁻¹, x²y⁻³⟩ = ⟨x,y | xyxYXY, xxYYY⟩`, total length 11.
Todd–Coxeter over the trivial subgroup completes with **index 1, 26 cosets defined**, so it
presents the trivial group. [MEASURED, this session]
Lemma-11 datum: `P = ⟨x, y, z | xyxYXY, xxYYY, z⁻¹x⟩` — balanced, presents the trivial group,
total length 13, and `P' = AK(2)`, `w = x`.

Finite-quotient lower bound (the method, and its direction): for **any** homomorphism
`φ : F(x,y) → H` with `H` finite — `φ` need not kill the relators — an expression
`w = ∏_{k≤m} u_k r_{i_k}^{ε_k} u_k⁻¹` maps to a product of `m` elements of
`S = ⋃ᵢ (class of φ(rᵢ)) ∪ (class of φ(rᵢ)⁻¹)`, so `m ≥ dist_S(1, φ(w))`, computed by BFS in
`H`. **This bounds the area from BELOW only.**

| quotient | sweep | result | method's detection ceiling |
|---|---|---|---|
| `S₄` | exhaustive, 576 homs, 5,547 BFS nodes | `Area_{AK(2)}(x) ≥ 3` | **3** |
| `S₅` | exhaustive, 14,400 homs, 709,260 BFS nodes, 52 s | `Area_{AK(2)}(x) ≥ 4` | **4** (measured on the 800-hom sample recorded in the artifact; the exhaustive sweep also returns 4) |
| `S₆` | 60-hom sample, 14,193 nodes | `≥ 2` (undersampled) | — |
| calibration: `⟨x,y|x,y⟩`, `w=[x,y]` | `S₄` exhaustive | `≥ 2` = the true value | 3 |

**Calibration, per `experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`.**
The `S₄` sweep returned **3**, and 3 is exactly the maximum value the `S₄` method could ever
return (the eccentricity of the identity in the `S`-Cayley graph, maximized over all 576
homomorphisms). The `S₅` sweep returned **4** against a sampled ceiling of **4**. In both
cases **the instrument saturated.** So:

> `Area_{AK(2)}(x) ≥ 4` is a genuine lower bound [MEASURED], but it is the method's ceiling,
> not an estimate of the truth. The real value may be far larger, and this family of
> quotients cannot tell us — a larger measurement needs a larger `H`, and the `S₆` sample was
> too thin to help within budget.

**Upper bound: NOT COMPUTED WITHIN BUDGET.** The free-group BFS (multiply on the right by
`u r^{±1} u⁻¹`, `|u| ≤ 1, 2, 3`, word-length cap 26–30) exhausted its 1,000-node ceiling
without reaching the identity, at every conjugator radius tried. Reported as such, not as
evidence of anything.

What the measurement does say, unconditionally: **for a balanced presentation of the trivial
group of total length 13, removing a stabilized generator defined by `z = x` requires at
least `m = 4` conjugate factors** — already `2n` — confirming the authors' "`m` may be much
larger than `n`" on a real, minimal-scale instance rather than an artificial one.

---

## 5. Honest scope: progress, or restatement?

**§1 (Theorem 1) is a restatement, not progress on the bound.** It renames `m` as
`Area_{P'}(w)`. It does not bound anything. Sold honestly, its value is threefold and real:

1. It converts `m` from an artifact of one proof into an **invariant of the pair `(P', w)`** —
   spelling-independent, conjugation-independent, and unchanged by which realization of the
   supermove one picks (§1.4). Before Theorem 1, "bound `m`" had no well-defined referent.
2. It imports a toolbox: van Kampen diagrams, the conjugator-normalization Lemma 2.1 (which
   is what makes the quantity *searchable*), and finite-quotient lower bounds — the last of
   which produced the only nontrivial number in §4.
3. It makes the quantity computable for any given instance (Theorem 4's (3) ⇒ (4) argument
   works instance-wise without any decidability hypothesis, because `w ∈ N'` is *given*).

**§2 is mostly restatement, with one piece of new content.** Theorem 3 is a translation.
Corollary 3.1 is a deflation (the existence of a bound was never the question). The new piece
is **Theorem 2(b)**: the lower bound `N ≥ log₂ Area_{R'}(π(z))` holds for *every*
single-destabilization realization, not only the authors' proof. The authors offered two
routes — "finding this bound, **or** discovering an alternative proof of the lemma that
establishes such a bound". Theorem 2(b) shows the second route cannot circumvent the first
within single-destabilization proofs: the area is an obstruction to the *supermove*, not to
one argument about it. That is genuine, if modest.

**Theorem 4 is more than a restatement, and it is a negative result.** The authors' problem
in the uniform effective form they state it is **equivalent** to the decidability of the
triviality problem for balanced finite presentations. Two consequences, in opposite spirits:

* *For the S-line's route portfolio:* if that problem is open — [RELAYED, §0.1: it is
  Magnus's trivial-group recognition problem, and Lackenby lists it among his open questions
  — three hops, not verified from source] — then by `FRAMING.md` §3's rule
  ("reduction of the problem to a different open problem marks a route BLOCKED"), the route
  **"obtain a uniform effective bound on `m`, then use it to bound stable AC costs" is
  BLOCKED.** It is not a stepping stone; it is a restatement of a hard open problem.
  *This verdict, and only this verdict, depends on the relayed openness claim.* If Magnus's
  problem turns out to be settled, Theorem 4 survives untouched as a proved equivalence and
  simply becomes a positive tool.
* *For what is not blocked:* Theorem 4 rules out only the **uniform, computable** form.
  Bounds for a **fixed family** — AK(n), the Miller–Schupp series, the specific stabilized
  presentations that route R4's stabilization schedules propose — are finite, concrete
  computations, are not touched by Theorem 4, and remain a legitimate target. Likewise
  Theorem 2(a) is immediately usable the moment any such family bound exists.

**Net verdict.**

| question | answer |
|---|---|
| Do §§1–2 solve the authors' open problem? | No. |
| Do they make progress on it? | Partly. Theorem 2(b) is new content (an obstruction valid for all single-destabilization realizations); Theorem 4 is new content (an exact equivalence with a named problem). Theorems 1 and 3 are clarifying restatements. |
| Is the uniform effective form of the authors' problem reduced to another open problem? | **Yes — it is *equivalent* to one.** Route BLOCKED, per `FRAMING.md` §3, conditional on the RELAYED openness of Magnus's problem. |
| Does this bear on the stable AC conjecture itself? | Only indirectly. Lemma 11 is a *tool* — stable AC-equivalence of `P` and `P'` is already a theorem; the area governs its *cost*. Nothing here makes any presentation more or less likely to be stably AC-trivial, and nothing here touches AK(3). |

---

## 6. Status table

| # | Claim | Status |
|---|---|---|
| 1 | Lemma 11's statement, proof, and the authors' open-problem paragraph, as quoted | **VERIFIED-FROM-SOURCE**: read from `ammedmar/ac_paper` @ `d86984d`, `sec/stable.tex:28–38`, this session |
| 2 | Lemma 1.1: `P` trivial ⇒ `P'` trivial ⇒ `w ∈ N'` (via the retraction `π`) | **PROVED** |
| 3 | Theorem 1(a): `min M(P,w) = Area_{R'}(w)` | **PROVED** (self-contained) |
| 4 | Theorem 1(b,c): `Area_{R'} = Area^{vK}_{R'}` | **PROVED modulo van Kampen's lemma**, which is CLASSICAL and not re-verified in this clone; both constructions are given |
| 5 | §1.4 direction accounting (area lower-bounds every `m`; area is attained) | **PROVED** |
| 6 | Lemma 2.1: conjugators normalizable to `|u_k| ≤ mL + |v|` | **PROVED** (uses Theorem 1(c)) |
| 7 | Theorem 2(a): supermove costs `≤ C_sub + 3A + 2A(AL+ℓ)` moves | **PROVED** |
| 8 | Doubling Lemma: `N` AC1–AC3+(0) moves ⇒ every entry has area `≤ 2^N` | **PROVED** |
| 9 | Theorem 2(b): `N ≥ log₂ Area_{R'}(π(z))` for every single-destabilization realization | **PROVED** |
| 10 | Theorem 3: `D(ℓ) ≤ m*(2ℓ+1)`, `m*(L) ≤ D(L²)` — "`m` is a Dehn function" | **PROVED** |
| 11 | Corollary 3.1: `m*(L) < ∞` for each `L` (existence is not the question) | **PROVED** |
| 12 | Theorem 4: (computable bound on `m`) ⟺ (triviality decidable for balanced presentations) | **PROVED** |
| 13 | Proposition 4.2: no computable bound in the unbalanced case | **PROVED modulo Adian–Rabin**, CLASSICAL, not re-verified in this clone |
| 14 | Magnus's problem (balanced triviality) is open | **RELAYED**, 3 hops (S2 §1.3 → codex `ac-advisor.md` → Lackenby's open questions); load-bearing **only** for the BLOCKED verdict in §5 |
| 15 | Lackenby Thm 1.1 / Bridson / Lishak statement as quoted in §3.1 | **RELAYED**, 3 hops; `literature/` contains only `fake_surfaces/` (§0.2) |
| 16 | §3.2: the relayed Thm 1.1 gives **no** lower bound on `m` (direction failure) | **PROVED** (given the relayed statement; the Doubling Lemma settles the direction) |
| 17 | §3.3: Bridson/Lishak bounds *would* transfer if their proofs are isoperimetric | **ASSERTED / UNSOURCED** — a conjecture about unread proofs; nothing depends on it |
| 18 | `Area_{⟨x|x⟩}(x^k) = k`; hence `m*(L) ≥ L − 2`; hence no bound in terms of rank | **PROVED** (and MEASURED for `k ≤ 8`) |
| 19 | `Area_{⟨x,y|x,y⟩}([x,y]) = 2` | **PROVED** (and MEASURED) |
| 20 | AK(2) presents the trivial group (index 1, 26 cosets) | **MEASURED** (Todd–Coxeter, this session) |
| 21 | `Area_{AK(2)}(x) ≥ 4` from an exhaustive `S₅` sweep | **MEASURED** (lower bound; **instrument saturated** — the `S₄` and `S₅` ceilings are 3 and 4) |
| 22 | `Area_{AK(2)}(x)` upper bound | **NOT COMPUTED WITHIN BUDGET** (1,000-node cap, radii 1–3) |
| 23 | The uniform-effective route is BLOCKED per `FRAMING.md` §3 | **PROVED conditional on #14** |

---

## 7. Residue for the next session

* **Do not** try to bound `m` uniformly and effectively. Theorem 4 says that is Magnus's
  problem. If a future session wants that route re-opened, it must first overturn #14.
* **Do** compute `Area` for the specific families the S-line and route R4 actually
  stabilize. That is unblocked, and Theorem 2(a) converts any such bound into an explicit AC
  move count for the supermove immediately.
* The finite-quotient lower bound in `s19_area_probe.py` is cheap and **saturates fast**
  (`S₄` ceiling 3, `S₅` ceiling 4). Anyone using it must print the ceiling beside the value —
  the function `quotient_detection_ceiling` is there for that — or the null is meaningless.
* An open, concrete question this file raises and does not answer: is `Area_{AK(2)}(x)`
  equal to 4, or much larger? A better lower-bound instrument (larger quotients; or a
  genuinely different obstruction such as an Alexander-module / Fox-calculus count over
  `ℤ[F]`) and an upper-bound search with a real budget would settle it, and AK(2) is
  AC-trivial so an upper bound certainly exists.
* Theorem 2's two sides are `log₂ A` and `O(A²L)`. Closing that exponential gap — is the
  supermove's true cost polynomial in `A`, or can it be logarithmic? — is a self-contained
  combinatorial question that does not require any literature.
