# Glossary of AC Moves and Stable-AC Theorems {#app:glossary}

This appendix collects, in one place and with precise statements, the move definitions and theorems that \ref{sec:methods} and \ref{sec:results} rely on.

## Elementary Andrews–Curtis moves

The Andrews–Curtis conjecture \cite{andrews1965ac} concerns *balanced* presentations $\langle x_1,\dots,x_n \mid r_1,\dots,r_n\rangle$ (equally many generators and relators). Three elementary moves act on the ordered relator tuple:

- **AC1**: replace some $r_i$ by $r_i r_j$ for $j\neq i$ (multiply one relator by another).
- **AC2**: replace some $r_i$ by $r_i^{-1}$ (invert a relator).
- **AC3**: replace some $r_i$ by $g\,r_i\,g^{-1}$, where $g$ is a generator or its inverse (conjugate a relator by a single generator).

Two presentations related by a finite sequence of AC1–AC3 are *AC-equivalent*; a presentation AC-equivalent to $\langle x_1,\dots,x_n\mid x_1,\dots,x_n\rangle$ is *AC-trivial*. The Andrews–Curtis conjecture asserts every balanced presentation is AC-trivial.

## Stable AC moves and the stable conjecture

The *stable* (or *weak*) AC conjecture permits two further moves:

- **AC4**: introduce a fresh generator together with the trivial relator equal to it: $\langle x_1,\dots,x_n \mid r_1,\dots,r_n\rangle \to \langle x_1,\dots,x_n,x_{n+1} \mid r_1,\dots,r_n,x_{n+1}\rangle$.
- **AC5**: remove a trivial relator and its corresponding generator — the inverse of AC4.

Presentations related by AC1–AC5 are *stably AC-equivalent*; a presentation stably AC-equivalent to a trivial presentation is *stably AC-trivial*. The stable conjecture asserts every balanced presentation is stably AC-trivial.

## The $z=w$ stabilization composite

The stabilization move used throughout \ref{sec:methods} packages an AC4 step with the moves realizing a definition $z=w(x,y)$ into a single composite:
$$
\langle x,y \mid r_1,r_2\rangle \ \longrightarrow\ \langle x,y,z \mid r_1,r_2,\ \mathrm{cyc\_reduce}\!\left(z\cdot w(x,y)^{-1}\right)\rangle,
$$
legal as a stable-AC move for *any* word $w$. Undoing it (destabilization) requires the target generator to occur exactly once in some relator, which is exactly the precondition Lemma 11 below formalizes.

## Lemma 11 (Substitution and Removal) — \cite{shehper2024hard}

Let $P=\langle x_1,\dots,x_n,y \mid r_1,\dots,r_n,\ y^{-1}w\rangle$ present the trivial group, where $w$ is a word in $x_1,\dots,x_n$ only. Then $P'=\langle x_1,\dots,x_n \mid r_1',\dots,r_n'\rangle$, where each $r_i'$ is $r_i$ with every occurrence of $y$ replaced by $w$, is stably AC-equivalent to $P$.

*Proof idea.* Substituting $w$ for $y$ throughout gives $\tilde P = \langle x_1,\dots,x_n,y \mid r_1',\dots,r_n',y^{-1}w\rangle$; since $r_1',\dots,r_n'$ contain no $y$, the map $x_i\mapsto x_i,\ y\mapsto w$ is a surjective homomorphism $\tilde P\to P'$, and since $\tilde P$ is trivial, so is $P'$. Triviality of $P'$ forces $w$ to be a product of conjugates of the $r_i'$; that expression is precisely an AC1–AC3 sequence turning $y^{-1}w$ into $y$, after which $y$ is deleted by AC5. $\square$

The proof gives no bound on the number of conjugate factors — equivalently, no bound on the number of elementary AC moves this supermove packages. Finding such a bound, or an alternative proof that supplies one, remains an open question noted by \cite{shehper2024hard}; every use of Lemma 11 in this paper's search is therefore a genuinely unbounded-cost supermove, not a bounded shortcut.

## The Miller–Schupp and Akbulut–Kirby families

$$
\mathrm{MS}(n,w) = \langle x,y \mid x^{-1}y^{n}x=y^{n+1},\ x=w\rangle, \qquad
\mathrm{AK}(n) = \langle x,y \mid x^{n}=y^{n+1},\ xyx=yxy\rangle.
$$

- **Theorem 2** \cite{shehper2024hard}: $\mathrm{MS}(1,w)$ is AC-trivial for every $w$.
- **Theorem 3**: $\mathrm{MS}(n,w_\star)$ is AC-trivial for every $n$, where $w_\star=y^{-1}xyx^{-1}$; the proof rewrites the defining relator and applies the automorphism $x\leftrightarrow y$ to reduce it to Theorem 2.
- **Proposition 5** (MMS02, restated in \cite{shehper2024hard}): for all $n\ge2$, $\mathrm{AK}(n)$ is AC-equivalent to $\mathrm{MS}(n,w_1)$ with $w_1=y^{-1}x^{-1}yxy$.
- **Theorems 6 and 7** \cite{shehper2024hard}: writing $w_k=y^{-k}x^{-1}yxy$ for $k\in\mathbb{Z}$, Theorem 6 shows $\mathrm{MS}(n,w_k)$ is AC-equivalent to $\mathrm{MS}(n,w_{k+1})$ for each fixed $n$, so the entire family $\{\mathrm{MS}(n,w_k)\}_{k\in\mathbb{Z}}$ is one AC-equivalence class; Theorem 7 identifies each member with $P(n,k)=\langle x,y \mid y^{n-k-1}x^{-1}yx=xyx^{-1}y^{n-k},\ x=w_k\rangle$, of total length $|k|+|n-k|+|n-k-1|+11$, minimized at $k=n-1$. These two results are the theory grounding the word bank's **wk** family (\ref{tab:wordbank}).

## The MMS02 construction (Theorem 1.4)

$$
\text{Any presentation } \langle x,y,z \mid x=z\cdot[[y^{-1},x^{-1}],z],\ y=x\cdot[[y^{-1},x^{-1}],z^{-1}]\cdot[z^{-1},x],\ w\rangle,
$$
where $w$ is a word in $x,y,z$ of exponent sum $\pm1$, was claimed by \cite{myasnikov2002ac} (MMS02) to always present the trivial group. This is the theorem whose supporting construction contains the misprint discussed in \ref{app:misprint}.

## Canonical form

Throughout the search and the certificates, a relator is canonicalized as the letter-order-minimal representative, over all cyclic rotations of the word *and* of its formal inverse, under the total order $Z<z<Y<y<X<x$ (an inverse letter precedes its generator; higher-magnitude generator id first) — encoding $x\!\to\!1,\ X\!\to\!-1,\ y\!\to\!2,\ Y\!\to\!-2,\ z\!\to\!3$. A presentation's canonical key sorts its canonicalized relators. Two states that agree up to this canonicalization *and* up to a *signed relabeling* — a bijective, sign-respecting renaming of the generator set — are treated as equal for deduplication and for cross-presentation floor comparisons (\ref{tab:floorcensus}).
