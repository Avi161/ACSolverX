# A folded boundary-preserving lift

This is a positive free-group boundary lift certificate. It supplies neither
an Andrews–Curtis move sequence nor a stable AK3 solution. The construction
is checked factorwise in `tests/stable_ac/test_ak3_folded_boundary_lift.py`;
the large total automorphism is not expanded.

## Conventions and statement

Write `[x,y]=xyx^-1y^-1` and `Inn(g)(x)=gxg^-1`. Composition acts
rightmost first. Uppercase letters in literal tests denote inverses.
Let `F=F(p,q,u,v)` and set

    H = [p,q^-1][u,v],
    rho(p)=p, rho(q)=q, rho(u)=q^-1, rho(v)=p,
    phi(p)=q, phi(q)=p^-1 q,
    w=q^-1 p q^-1 p^-1 q p^-1,
    psi=Inn(w^-1) compose phi.

There is an explicitly factored automorphism `Phi` of `F` such that
`Phi(H)=H` literally and `rho compose Phi=psi compose rho`.
The formulas below give its inverse as well.

## Folded coordinates

Put `(a,b,c,d)=(p,q^-1,u,v)` and `K0=[a,c]`. Define

    r=a K0^-1,        s=K0 b c^-1 K0^-1,
    l=a c a^-1,       m=d a^-1.

These are free coordinates, with inverse substitutions

    a=l^-1 r l,       c=a^-1 l a,
    b=K0^-1 s K0 c,   d=m a,

where `K0=[a,c]` is evaluated using the preceding expressions.
Direct reduction gives `H=[r,s][l,m]` and `rho(s)=rho(m)=1`.
Moreover `rho(r),rho(l)` form a basis of `F(p,q)`: its inverse is
`p=a=l^-1 r l`, `q=(a^-1 l a)^-1` in the quotient.

## Boundary-preserving factors

In coordinates `(r,s,l,m)`, set `K=[l,m]` and `L=K^-1 s`.
The following tuples list images in that order:

    T=(r K, K^-1 s K, L l L^-1, L m L^-1),
    T^-1=(r s^-1 K^-1 s,
          s^-1 K s K^-1 s,
          s^-1 K l K^-1 s,
          s^-1 K m K^-1 s).

Let `tau` fix `r,l,m` and send `s` to `sr`; its inverse sends `s` to
`sr^-1`. These maps fix `H`. Set

    F_r=T compose tau compose T^-1 compose tau^-1.

Reduction on the four generators proves
`rho compose F_r=Inn(rho(r)^-1) compose rho`.
In particular this is an equality of homomorphisms, not just an equality
on one selected relator.

Define, with `J=[r,s]`,

    S=(l,m,K^-1 r K,K^-1 s K),
    S^-1=(J l J^-1,J m J^-1,r,s),
    F_l=S compose F_r compose S^-1.

Both `S` and its displayed inverse fix `H`. The corresponding generator
check gives `rho compose F_l=Inn(rho(l)^-1) compose rho`.
The inverses of `F_r,F_l` are obtained by reversing their factors and
inverting each factor; their projections have the opposite conjugator sign.

## Antihomomorphic assembly

Define `P` on `F(r,l)` by

    P(r)=F_r, P(l)=F_l,
    P(g^-1)=P(g)^-1,
    P(gh)=P(h) compose P(g).

Inverse adjacent letters give inverse adjacent factors, so this is
well-defined on reduced words. Every factor fixes `H`; therefore every
`P(g)` fixes `H`. The projection identities imply, for every word `g`,

    rho compose P(g)=Inn(rho(g)^-1) compose rho.

Indeed the two prefixes for `gh` multiply in the order
`rho(h)^-1 rho(g)^-1=rho(gh)^-1`. This explains why the assembly is
antihomomorphic; reversing that order gives a different map in general.

Take the word

    W=u p u p^-1 u^-1 p^-1.

After the displayed coordinate substitution it lies in `F(r,l)`, since
both `p=a` and `u=c` use only `r,l`. Also `rho(W)=w` literally.
In original coordinates put

    Phi0=(q,p^-1 q,u v,u^-1),
    Phi0^-1=(p q^-1,p,v^-1,v u).

The two tuples are inverse, fix `H`, and satisfy
`rho compose Phi0=phi compose rho` by substitution on the generators.
Consequently

    Phi=P(W) compose Phi0,
    Phi^-1=Phi0^-1 compose P(W^-1),

with `P(W)` translated back from folded coordinates, has the asserted
boundary and projection properties. This deduction uses the universal
composition identities above; expanding the complete `Phi` is unnecessary.

## Certificate scope

The tests check both coordinate inverse orders, the boundary identities,
the quotient basis, `T`, `tau`, `S` and their inverses, both push factors,
and `Phi0`. They check the induced composition for `W` using only the
rank-two projected maps, with wrong-sign and wrong-order controls.
They do not enumerate powers or classify orbits.

The defining adjunction rows `uq` and `vp^-1` alone delete back to the
original presentation. No balanced AC replacement of
`(psi(p)p^-1,psi(q)q^-1,uq,vp^-1)` by four `Phi` fixed-point rows is
supplied here. No geometric attaching curves, cancellation certificate,
or stable AK3 conclusion is supplied. The positive result is precisely
the boundary-preserving free-group lift stated above.

## The independent kernel-row replacement fails for this lift

Let `N=Ncl(s,m)` in `F(r,s,l,m)`. Its relation module `N_ab` is free
over `Z[F(r,l)]` with basis `s,m`. Use image columns and derivative rows
`s,m`, and specialize coefficients to `Z[R^±1,L^±1]` by abelianizing
the quotient `F(r,l)`. The assembled `N`-preserving push factors give

    Kr = [[1,0],[(L-1)/R,1/R]],
    Kl = [[1/L,(R-1)/L],[0,1]],
    K0 = [[1,1/L],[-L,0]].

Here `K0` is the matrix of folded `Phi0`, not the earlier word `[a,c]`.
The chain rule is used only for the assembled `N`-preserving factors,
never for intermediate `T` or `tau`. Push factors act trivially on the
abelianized quotient. Since `W=LRlrlR`, the total image-column matrix is

    K = Kr^-1 Kl Kr Kl Kr^-1 Kl^-1 K0,
    det(K-I) = -L^-2+L^-1-1+L+R/L-RL+R^2 L.

The seven distinct monomials make this a nonunit despite augmentation
one. The two fixed-point rows `Phi(s)s^-1`, `Phi(m)m^-1` have relation
module coefficient columns `J-I` before specialization, and `K-I` after
specialization. If these rows independently normally generated `N` in
the ambient free group, their coefficient map would be onto `N_ab`.
Specialization preserves surjectivity; a square matrix onto a free module
over this commutative Laurent ring has unit determinant. Thus these two
rows do not independently normally generate `N` for this specific lift.

`test_ak3_folded_kernel_replacement.py` checks the displayed matrices,
their chain rule against a literal two-factor composition, and the exact
determinant using independent direct and full-then-specialized Fox
gradients. Its untwisted control is `det(K0-I)=1`; this is only a
coefficient control, not a normal-generation theorem. This independent
replacement step is frozen. The positive boundary lift remains valid;
the exclusion concerns neither coupled base-row moves, other lift
families, nor AK3 itself, and creates no further residual ledger.
