# FLZ preflight: power-product equality loci in \(C_2 * \mathbb Z\)

## Primary source audited

- Michael Figelius, Markus Lohrey, Georg Zetzsche, *Closure properties of knapsack semilinear groups*, [arXiv record](https://arxiv.org/abs/1911.12857), [version-pinned arXiv PDF](https://arxiv.org/pdf/1911.12857v2), arXiv:1911.12857v2 [math.GR], 26 Nov 2024. The audit below uses the actual 36-page v2 PDF, not the abstract or a secondary summary. Page numbers are the paper's printed page numbers (the same ordinal pages in this PDF).

## Fit to the target locus

Fix \(G=C_2*\mathbb Z\cong\langle a,t\mid a^2=1\rangle\). If words \(u_i\) represent \(g_i\in G\), then
\[
S(g_1,\ldots,g_k)=\{(n_1,\ldots,n_k)\in\mathbb N^k:g_1^{n_1}\cdots g_k^{n_k}=1\}
\]
is exactly \(\operatorname{sol}_G(e)\) for the knapsack expression \(e=u_1^{x_1}\cdots u_k^{x_k}\) (all intervening \(v_i\) empty). This is the paper's formal setup in Section 4, pp. 5–6: an exponent expression is \(u_1^{x_1}v_1\cdots u_k^{x_k}v_k\), a *knapsack expression* has no repeated variable, and \(\operatorname{sol}_G(e)\) is the set of valuations making \(e=1\) in \(G\). Its length is \(\lVert e\rVert=\sum_i(|u_i|+|v_i|)\), and its degree is the number of powered factors (Section 4, p. 5).

## Exact evidence chain

1. **What the algorithm must output.** Section 3, pp. 4–5 defines a linear set as \(L(b,P)=b+P\mathbb N^r\subseteq\mathbb N^d\), a semilinear set as a finite union of such linear sets, and a semilinear representation as the finite tuple \((b_1,P_1,\ldots,b_s,P_s)\). Thus the relevant output is an explicit finite list of base vectors and period-vector matrices, not only a decision or an existential Presburger formula. The *magnitude* is the least possible maximum entry among all such representations (p. 5).

2. **Effectiveness is part of the definition.** Section 4.1, p. 6 defines \(G\) to be *knapsack-semilinear* iff, for every knapsack expression \(e\), \(\operatorname{sol}_G(e)\) is semilinear **and a semilinear representation can be effectively computed from \(e\)**. The same paragraph explains how repeated-variable exponent expressions are reduced effectively to knapsack expressions using intersection and coordinate restriction. Remark 4.1 (p. 6) emphasizes that bare semilinearity is insufficient and gives a torsion-group/undecidable-word-problem counterexample to effectiveness.

3. **Base factors.** The introduction, pp. 2–3 (especially p. 3), states that every finitely generated abelian group is semilinear because its solution sets are Presburger-definable. Hence the paper treats both \(C_2\) and \(\mathbb Z\) as base examples for its knapsack-semilinear closure theorem. There is no separately numbered abelian-base theorem in this paper; the assertion is made in the introductory discussion, while the formal Section 4.1 definition includes computability.

4. **Direct theorem for \(C_2*\mathbb Z\).** **Theorem 5.25** (Section 5.6, pp. 23–24) states: if \(G_1,G_2\) are knapsack-semilinear, then \(G_1*G_2\) is knapsack-semilinear. With \(K(n,m)=\max(K_{G_1,\Sigma_1}(n,m),K_{G_2,\Sigma_2}(n,m))\), it gives
\[
K_{G_1*G_2,\Sigma}(n,m)\le \max\{K(6mn,m),\ O(mn^4)\}.
\]
Taking \(G_1=C_2\) and \(G_2=\mathbb Z\) yields effective semilinearity of every target locus \(S(g_1,\ldots,g_k)\).

5. **Constructive content of Theorem 5.25.** At the end of its proof (p. 24), the authors say they have obtained a semilinear representation of \(\operatorname{sol}_G(e)\), with magnitude bounded by the displayed theorem bound after preprocessing. **Remark 5.27** (pp. 24–25) makes the construction more explicit:
\[
\operatorname{sol}_{G_1*G_2}(e)
=\bigcup_{i=1}^{p}\left(\bigoplus_{j=1}^{q_i}\operatorname{sol}_{H_{i,j}}(e_{i,j})\oplus L_i\right),
\]
where each \(H_{i,j}\) is one factor, each \(e_{i,j}\) is a factor-group knapsack expression, their variable sets partition the atomic-period variables, \(\lVert e_{i,j}\rVert\le 6m\lVert e\rVert\), \(\deg(e_{i,j})\le m\), and \(L_i\) has magnitude \(O(mn^4)\). For a fixed branch \(i\), the \(e_{i,j}\) and a semilinear representation of \(L_i\) are computable in polynomial time.

6. **No fixed-\(k\) hypothesis.** Section 4 allows every \(k\ge1\), and Theorem 5.25 is uniform in \(m=\deg(e)\); \(m\) appears as a parameter in its bound rather than as a constant hypothesis. Therefore \(k\) may be part of the input and unbounded. The introduction's comment that *fixing* the number of variables improves certain graph-product magnitude bounds (p. 3) is a complexity observation, not a condition for semilinearity or effectiveness. For the target expression, \(m=k\).

7. **Complexity caveat.** Theorem 5.25 proves effective construction and bounds the entries in a representation; it does **not** state that the entire semilinear representation has polynomial output size or can be fully enumerated in polynomial time. The number of branches/linear components is not polynomially bounded there. **Theorem 5.28** (p. 25) is instead a decision result: knapsack for \(G_1*G_2\) is nondeterministically polynomial-time reducible to knapsack for the factors. It should not be cited as the representation-producing theorem.

## Bottom line

For fixed \(G=C_2*\mathbb Z\), FLZ gives a uniform algorithm that, from arbitrary word inputs \(g_1,\ldots,g_k\) with arbitrary input-dependent \(k\), computes a finite semilinear representation of \(\{n\in\mathbb N^k:g_1^{n_1}\cdots g_k^{n_k}=1\}\). The sharp directly applicable citation is **Definition/Section 4.1 + Theorem 5.25**, with **Remark 5.27** for the constructive decomposition. The result is effective, but the paper does not promise polynomial time or polynomial total size for the full semilinear output.

## Direct references mentioned but not needed/audited

- [38] Lohrey, *Knapsack in hyperbolic groups* supplies an alternate route via hyperbolicity, but it is unnecessary for \(C_2*\mathbb Z\) because Theorem 5.25 applies directly.
- [22] Ginsburg–Spanier is cited for semilinear sets = Presburger-definable sets; [42] Lohrey–Zetzsche is cited in Remark 5.26 for an earlier polynomial magnitude result. Neither is needed to identify the FLZ theorem or its stated output, and neither was audited here.
