"""Experimental decoder word backend; the original Python algebra stays the oracle."""
import numpy as np
from numba import njit
from experiments.equivalence_classes.lib.words import (
    free_reduce as python_free_reduce,inv,SIGNED_PERMS,_least_rotation,_TO_ORD,_FROM_ORD,
)

MIN_NUMBA_LENGTH=64
_TO_BYTES=bytes.maketrans(b'YyXx',bytes((0,1,2,3)))
_FROM_BYTES=bytes.maketrans(bytes((0,1,2,3)),b'YyXx')


@njit(cache=True)
def _rotation_index(word):
    n=len(word);a=0;b=1;k=0
    while a<n and b<n and k<n:
        left=word[(a+k)%n];right=word[(b+k)%n]
        if left==right:
            k+=1
        else:
            if left>right:
                a+=k+1
                if a==b:a+=1
            else:
                b+=k+1
                if a==b:b+=1
            k=0
    return min(a,b)


@njit(cache=True)
def _canonical_codes(word):
    n=len(word);inverse=np.empty(n,dtype=np.uint8)
    for i in range(n):inverse[i]=word[n-1-i]^1
    a=_rotation_index(word);b=_rotation_index(inverse);use_inverse=False
    for i in range(n):
        left=word[(a+i)%n];right=inverse[(b+i)%n]
        if left!=right:
            use_inverse=right<left
            break
    result=np.empty(n,dtype=np.uint8)
    for i in range(n):
        result[i]=inverse[(b+i)%n]if use_inverse else word[(a+i)%n]
    return result


@njit(cache=True)
def _reduce_ascii(symbols):
    out=np.empty(len(symbols),dtype=np.uint8)
    size=0
    for symbol in symbols:
        value=int(symbol)
        inverse=value+32 if 65<=value<=90 else value-32 if 97<=value<=122 else value
        if size and out[size-1]==inverse:
            size-=1
        else:
            out[size]=symbol
            size+=1
    return out[:size]


def free_reduce(word):
    if len(word)<MIN_NUMBA_LENGTH:
        return python_free_reduce(word)
    try:
        symbols=np.frombuffer(word.encode('ascii'),dtype=np.uint8)
    except UnicodeEncodeError:
        return python_free_reduce(word)
    return _reduce_ascii(symbols).tobytes().decode('ascii')


def cyc_reduce(word):
    word=free_reduce(word)
    left,right=0,len(word)
    # A substring of a freely reduced word is already freely reduced.
    while right-left>=2 and word[left]==word[right-1].swapcase():
        left+=1;right-=1
    return word[left:right]


def canon_rel(word):
    word=cyc_reduce(word)
    if not word:return ''
    if len(word)>=MIN_NUMBA_LENGTH:
        codes=np.frombuffer(word.encode('ascii').translate(_TO_BYTES),dtype=np.uint8)
        return _canonical_codes(codes).tobytes().translate(_FROM_BYTES).decode('ascii')
    a=_least_rotation(word.translate(_TO_ORD))
    b=_least_rotation(inv(word).translate(_TO_ORD))
    return min(a,b).translate(_FROM_ORD)


def canon_pair(a,b):
    a,b=canon_rel(a),canon_rel(b)
    if (len(a),a.translate(_TO_ORD))>(len(b),b.translate(_TO_ORD)):a,b=b,a
    return a,b


def apply_hom(word,images):
    expanded={}
    for generator,image in images.items():
        expanded[generator]=image
        expanded[generator.upper()]=inv(image)
    return free_reduce(''.join(expanded[c]for c in word))


def apply_pair(pair,images):
    return canon_pair(apply_hom(pair[0],images),apply_hom(pair[1],images))
