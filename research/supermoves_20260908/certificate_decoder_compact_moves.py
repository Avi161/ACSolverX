"""Streaming unary-block compression for the trusted fast decoder."""
from types import FunctionType
from research.supermoves_20260908 import certificate_decoder_fast as base

_INV={'x':'X','X':'x','y':'Y','Y':'y'}


class _CompactTrace(base._ElementaryTrace):
    def __init__(self,pair):
        super().__init__(pair);self.perm=[0,1];self.sign=[1,1];self.conj=[[],[]]

    @property
    def moves(self):
        if hasattr(self,'perm'):self._flush()
        return self._moves

    @moves.setter
    def moves(self,value):self._moves=value

    def _flush(self):
        if self.perm==[1,0]:self._moves.append({'op':'swap'})
        elif self.perm!=[0,1]:raise AssertionError('invalid unary permutation')
        for target in (1,2):
            i=target-1
            if self.sign[i]<0:self._moves.append({'op':'invert','target':target})
            self._moves.extend({'op':'conjugate','target':target,'by':letter}
                               for letter in self.conj[i])
        self.perm=[0,1];self.sign=[1,1];self.conj=[[],[]]

    def _record(self,move):
        op=move['op']
        if op=='multiply':self._flush();self._moves.append(move)
        elif op=='swap':self.perm.reverse();self.sign.reverse();self.conj.reverse()
        elif op=='invert':self.sign[move['target']-1]*=-1
        elif op=='conjugate':self._append(move['target'],move['by'])
        else:raise ValueError(op)

    def _append(self,target,word):
        stack=self.conj[target-1]
        for letter in word:
            if stack and stack[-1]==_INV[letter]:stack.pop()
            else:stack.append(letter)

    def conjugate_word(self,target,word):
        if any(letter not in 'xXyY' for letter in word):
            raise ValueError(f'conjugation word is outside F2: {word!r}')
        i=target-1
        self.pair[i]=base.free_reduce(base.inv(word)+self.pair[i]+word)
        self._append(target,word)

    def finish(self):self._flush();return self._moves


_globals=dict(base.decode_elementary.__globals__)
_globals['_ElementaryTrace']=_CompactTrace
_decode_impl=FunctionType(base.decode_elementary.__code__,_globals,
                          name='decode_elementary',
                          argdefs=base.decode_elementary.__defaults__)


def decode_elementary(pair,states,steps,elementary_tail=None):
    """Decode while compacting unary blocks; preserves trusted frame checks."""
    return _decode_impl(pair,states,steps,elementary_tail)
