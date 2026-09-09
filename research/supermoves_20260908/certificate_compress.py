"""Compress unary elementary blocks between multiply boundaries."""
_ALPHABET=frozenset('xXyY')
_INVERSE={'x':'X','X':'x','y':'Y','Y':'y'}


def _validate(move):
    if not isinstance(move,dict) or move.get('op') not in {'invert','conjugate','swap','multiply'}:
        raise ValueError('invalid elementary move')
    if move['op'] in {'invert','conjugate','multiply'} and (type(move.get('target')) is not int or move['target'] not in (1,2)):
        raise ValueError('invalid target')
    if move['op']=='multiply' and (type(move.get('source')) is not int or
            move['source'] not in (1,2) or move['source']==move['target']):
        raise ValueError('invalid source')
    if move['op']=='conjugate' and (not isinstance(move.get('by'),str) or set(move['by'])-_ALPHABET):
        raise ValueError('invalid conjugator')


def compress(moves):
    """Return an equivalent list, agreeing at every multiply boundary.

    Conjugation records may contain words. The nonincrease guarantee concerns
    weighted elementary cost (word length), so record count can increase.
    """
    if not isinstance(moves,(tuple,list)):raise ValueError('moves must be a sequence')
    out=[];perm=[0,1];sign=[1,1];conj=[[],[]]
    def flush():
        nonlocal perm,sign,conj
        if perm==[1,0]:out.append({'op':'swap'})
        elif perm!=[0,1]:raise AssertionError('bad permutation')
        for target in (1,2):
            i=target-1
            if sign[i]<0:out.append({'op':'invert','target':target})
            for letter in conj[i]:out.append({'op':'conjugate','target':target,'by':letter})
        perm=[0,1];sign=[1,1];conj=[[],[]]
    original_unary_cost=0
    for move in moves:
        _validate(move);op=move['op']
        if op=='multiply':
            flush();out.append(dict(move));continue
        if op=='swap':
            original_unary_cost+=1;perm.reverse();sign.reverse();conj.reverse()
        else:
            i=move['target']-1
            if op=='invert':original_unary_cost+=1;sign[i]*=-1
            else:
                original_unary_cost+=len(move['by'])
                for letter in move['by']:
                    if conj[i] and conj[i][-1]==_INVERSE[letter]:conj[i].pop()
                    else:conj[i].append(letter)
    flush()
    output_unary_cost=sum(1 if m['op'] in {'invert','swap'} else len(m.get('by',''))
                          for m in out if m['op']!='multiply')
    if output_unary_cost>original_unary_cost:raise AssertionError('unary cost increased')
    return {'moves':out,'input_move_records':len(moves),'output_move_records':len(out),
            'input_unary_cost':original_unary_cost,'output_unary_cost':output_unary_cost}
