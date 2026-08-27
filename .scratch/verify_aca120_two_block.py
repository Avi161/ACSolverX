#!/usr/bin/env python3
"""Independent exact verifier for the aca_120 two-stabilizer block descent."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WT=ROOT/'.claude/worktrees/codex-proofs'
sys.path.insert(0,str(ROOT/'.scratch'))
sys.path.insert(0,str(WT))
import search_two_block_relative_basis as b
from experiments.equivalence_classes.lib.autcanon import aut_canon,check,phi_str


def sub_generator(word,g,expr):
    images=[(1,),(2,),(3,),(4,)]
    images[g-1]=expr
    return b.red(b.apply_hom(word,tuple(images)))


def main():
    source=(b.parse('YXXXYxx'),b.parse('YYYYXyyyx'))
    u_z=b.parse('xy');u_t=b.parse('yyy')
    d_z=(-3,)+u_z;d_t=(-4,)+u_t

    r1z,n11=b.substitute(source[0],u_z,3)
    r2z,n12=b.substitute(source[1],u_z,3)
    assert (b.text(r1z),b.text(r2z),n11+n12)==('ZXXYxx','YYYZyyyx',2)

    A=r2z
    x_expr=b.parse('YYYzyyy')
    assert sub_generator(A,1,x_expr)==()
    K=sub_generator(r1z,1,x_expr)
    C0=sub_generator(d_z,1,x_expr)
    assert (b.text(K),b.text(C0))==('ZYYYZZYzzyyy','ZYYYzyyyy')

    B,n21=b.substitute(K,u_t,4)
    C,n22=b.substitute(C0,u_t,4)
    D=d_t
    assert (b.text(B),b.text(C),b.text(D),n21+n22)==('ZTZZYzzt','ZTzty','Tyyy',4)

    y_expr=b.parse('zztZTZZ')
    assert sub_generator(B,2,y_expr)==()
    C_out=b.cyc(sub_generator(C,2,y_expr))
    D_out=b.cyc(sub_generator(D,2,y_expr))
    target_pre=(C_out,D_out)
    target=tuple(tuple(a-2 if a>0 else a+2 for a in w) for w in target_pre)
    assert tuple(map(b.text,target))==('XYxyxxyXYXX','YxxyXXXYXX')

    # Three relator-Nielsen products make the displayed block non-triangular.
    Bp=b.red(B+A+A)
    Ap=b.red(A+Bp)
    counts=((b.old_count(Ap,1),b.old_count(Ap,2)),
            (b.old_count(Bp,1),b.old_count(Bp,2)))
    assert counts==((3,19),(2,13))
    # Replay the inverse relative-Nielsen certificate.
    A_recovered=b.red(Ap+b.inv(Bp))
    BA=b.red(Bp+b.inv(A_recovered))
    B_recovered=b.red(BA+b.inv(A_recovered))
    assert (A_recovered,B_recovered)==(A,B)

    source_s=tuple(map(b.text,source));target_s=tuple(map(b.text,target))
    smu,srep,sphi=aut_canon(source_s);tmu,trep,tphi=aut_canon(target_s)
    assert (smu,tmu)==(16,15)
    assert check(source_s,srep,sphi) and check(target_s,trep,tphi)
    assert srep!=trep

    one_path=ROOT/'.scratch/aca120_exhaustive_single_cov_allwords.json'
    one=json.loads(one_path.read_text())
    assert one['source_mu']==16 and one['minimum_endpoint_mu']==16
    assert one['target_orbit_hits']==0

    payload={
        'schema':'aca120-two-block-certificate-v1',
        'source':list(source_s),'source_mu':smu,'source_rep':list(srep),
        'definitions':['Zxy','Tyyy'],
        'hidden_step':('four Lemma-11 directions; witness-dependent; '
                       'no effective input-visible bound supplied'),
        'z_substitution':{'count':n11+n12,'relators':[b.text(r1z),b.text(r2z)]},
        'first_isolator':b.text(A),'x_expression':b.text(x_expr),
        'after_x_substitution':[b.text(K),b.text(C0)],
        't_substitution':{'count':n21+n22,'block':[b.text(B),b.text(C),b.text(D)]},
        'second_isolator':b.text(B),'y_expression':b.text(y_expr),
        'nontriangular_block':[b.text(Ap),b.text(Bp)],
        'old_generator_occurrence_counts':[list(x) for x in counts],
        'relative_nielsen_inverse':['A_prime <- A_prime B_prime^-1',
                                    'B_prime <- B_prime A^-1',
                                    'B_prime A^-1 <- (B_prime A^-1) A^-1'],
        'target':list(target_s),'target_mu':tmu,'target_rep':list(trep),
        'source_whitehead_phi':sphi,'target_whitehead_phi':tphi,
        'whitehead_checks':[check(source_s,srep,sphi),check(target_s,trep,tphi)],
        'single_cov_audit':{k:one[k] for k in ('cyclic_words','variant_attempts',
                            'distinct_endpoint_orbits','minimum_endpoint_mu','target_orbit_hits')},
        'single_cov_audit_sha256':hashlib.sha256(one_path.read_bytes()).hexdigest(),
    }
    out=ROOT/'.scratch/aca120_two_block_certificate.json'
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'verified':True,'source_mu':smu,'target_mu':tmu,
                      'nontriangular_counts':counts,'single_cov_audit':payload['single_cov_audit']}))


if __name__=='__main__':main()
