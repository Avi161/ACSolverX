# Scope of the short power-complement construction

This note records exact subgroup obstructions and word identities, with no new heap search. The frozen prototype report has SHA256 `2fcdcbc1368e508c6f85174488eb233b8740734cefee7e894935190833ade3f0`; the q3 continuation report has SHA256 `b5b72fb511bf8c3f96ccc1f7cc3e18fbca95f2420497ee48f691ccd69da61491`.

## Which joins can change

The five proper joins for complements `(x,y^2)` are exactly `aca_115`, `aca_13`, `aca_59`, `aca_79`, `aca_108`. Changing q from 2 to -2 cannot change any join, since the generated cyclic subgroup is unchanged. This is a subgroup statement; independently chosen kernel markings need not produce identical projected words.

For q=3, `aca_115` and `aca_59` have full joins. Their second words are `y^-4 x^n`, with n=3 and n=7 respectively. The presence of x supplies y^4, and y^3 supplies y by Bézout. More generally, if y^d belongs to `<R,S,x>` and gcd(d,q)=1, then `<R,S,x,y^q>=F(x,y)`. This is a sufficient condition, not a necessary condition stated solely in terms of that one power.

The other three joins remain proper for q=3. The following finite permutations give independently checked exact certificates for these three claims, and also for all five q=2 rejections. An array lists the images of 0,...,N-1. Read a word from left to right, using inverse permutations for uppercase letters. Every listed pair is bijective; R,S,x,y^q all fix 0, while y moves 0. Therefore the join lies inside the proper stabilizer of 0.

| Input | q | x permutation | y permutation |
|---|---:|---|---|
| aca_115 | 2 | `[0, 2, 1]` | `[1, 0, 2]` |
| aca_13 | 2 | `[0, 4, 1, 2, 3]` | `[1, 0, 2, 4, 3]` |
| aca_13 | 3 | `[0, 3, 4, 5, 1, 2]` | `[1, 2, 0, 3, 4, 5]` |
| aca_59 | 2 | `[0, 3, 1, 2]` | `[1, 0, 2, 3]` |
| aca_79 | 2 | `[0, 5, 1, 2, 3, 6, 4]` | `[1, 0, 2, 4, 5, 3, 6]` |
| aca_79 | 3 | `[0, 3, 6, 4, 1, 2, 8, 5, 9, 7]` | `[1, 2, 0, 4, 5, 6, 3, 7, 8, 9]` |
| aca_108 | 2 | `[0, 2, 3, 1, 6, 7, 4, 5]` | `[1, 0, 4, 5, 2, 3, 7, 6]` |
| aca_108 | 3 | `[0, 3, 4, 1, 5, 2, 6, 9, 10, 7, 8]` | `[1, 2, 0, 6, 7, 8, 4, 3, 5, 10, 9]` |

These are **not** nontrivial quotients of the presented trivial groups: the relators fix the distinguished point but need not act trivially on every point. Confusing a based subgroup-membership certificate with a normal-closure quotient would give a false contradiction.

## The q=d-1 natural marking is an ambient return

Let `P=(R(x,y),y^-d x^n)`, d>=2 and n any integer, and choose complements `(x,y^(d-1))`. Put

    phi(x)=x,       phi(y)=x^n Y,
    alpha(x)=x,     alpha(y)=Y x^n.

Direct substitution gives both inverse compositions equal to the identity. The natural marked-kernel construction in the q3 records projects to

    Q=(R(x,x^n Y), (y x^-n)^(d-1) y)=phi(P).

Indeed phi(y^-d x^n)=(y x^-n)^d x^n, and the last powers cancel. Thus alpha(Q)=P exactly. A full join in this family is not evidence that this particular marking escapes the input's ambient orbit. This statement does not classify all possible kernel markings for those complements.

For the two saved q3 examples, the raw identities were checked letter by letter:

| Input | Original P | Exact phi(P) |
|---|---|---|
| aca_115 | `(YXYxyx,YYYYxxx)` | `(yXXXXyxYx,yXXXyXXXyXXXy)` |
| aca_59 | `(YXXYxxyxx,YYYYxxxxxxx)` | `(yXXXXXXXXXyxxYxx,yXXXXXXXyXXXXXXXyXXXXXXXy)` |

The root's saved ordinary endpoints are also explicit ambient returns after independent cyclic conjugations:

* For aca_115, substitute x->Y,y->x in P, obtaining `(XyXYxY,XXXXYYY)`; rotate the rows at cuts 5 and 4 to obtain `(YXyXYx,YYYXXXX)`, total13.
* For aca_59, substitute x->X,y->y in P, obtaining `(YxxYXXyXX,YYYYXXXXXXX)`; rotate the first row at cut3 to obtain `(YXXyXXYxx,YYYYXXXXXXX)`, total20.

All four substitutions and rotations were directly verified. This note does not replay the root's S20 move paths; it independently classifies the displayed endpoints. There is no new minimum or solved presentation here.

## A finite marked-kernel algorithm when a join is full

There is a deterministic alternative to a bounded Nielsen heap for producing some marked basis. Start with the subdivided bouquet whose four petals read R,S,C,D and retain the domain marking. Fold equal-labelled outgoing edges until the map to the two-petal rose is an immersion. This is the finite graph-folding procedure of [Stallings, Topology of finite graphs (1983)](https://link.springer.com/article/10.1007/BF02095993). The following basis-transport argument explains the required marking, rather than inferring it from a quotient alone.

An open fold identifies edges with different terminal vertices. It is a graph homotopy equivalence: one can lift the merged vertex through either preimage and join the alternatives by the path consisting of the inverse of the first folded edge followed by the second. Spanning-tree bases and these paths give an explicit inverse on fundamental groups. A closed fold identifies parallel edges with the same endpoints. Deleting one of those edges leaves a connected graph representing the quotient. A spanning tree in that graph exhibits the original fundamental group as its free product with one extra cyclic factor. If the folded edges are a,b and p joins the basepoint to their initial vertex, the primitive kernel generator is `p a b^-1 p^-1`. This also covers parallel loops.

Each fold removes one edge. Open folds preserve rank, closed folds lower rank by one, and pruning hanging trees preserves rank. If the join is full, the terminal core is the rank2 rose. Beginning at rank4, exactly two closed folds therefore occur. Reverse the recorded operations starting with the marked terminal generators x,y, transporting the basis through open folds and adjoining the displayed primitive kernel generator at each closed fold. The result is a domain free basis `(W1,W2,Vx,Vy)` with images `(1,1,x,y)`.

This gives a finite constructive algorithm on every full join. The number of folds is at most the initial number of subdivided edges; it does not bound the lengths of the transported words, inverse-basis words, or expanded stable certificate. An implementation must keep based paths and check both inverse compositions; it must not discard the domain marking merely because two image tuples coincide. No implementation or new numerical result from this general algorithm is claimed here.

Once the original presentation is known trivial, the exact marked basis gives the finite stable bridge proved in `two_complement_independent_theory.md`: the rank4 tuple `(r,s,W1,W2)` is known trivial, its two marked unit eliminations yield the original and projected pairs, and its ambient basis change is a theorem-backed finite stable composite. A temporary fifth generator may be required. This does not give ordinary AC equivalence or an elementary intermediate length bound.
