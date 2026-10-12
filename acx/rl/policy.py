"""``RelativeDualRingActorCritic`` in PyTorch, plus the shipped step-1000 weights (``checkpoint/610model_1000.pt``).

Details that decide parity with the trained network: LayerNorm ``eps=1e-6``; tanh GELU; masking with ``-1e9``, never
``-inf``, and the ``1/sqrt(head_dim)`` scale after masking (a fully masked attention row stays uniform); the relator is a
ring, so relative distances are taken modulo its TRUE length with one learned ``rel_emb[H, L, Dh]`` per head; the actor
``Dense(128)`` over the outer product of the two rings is applied separably. ``forward(obs)`` takes ``(B, 2L)`` ints and
returns ``(logits, value)``: logits over the ``4 L^2`` flat actions of ``acx.rl.moves``, illegal ones at ``-1e9``.
"""
import math
import os

import torch
import torch.nn.functional as F
from torch import nn

CHECKPOINT = os.path.join(os.path.dirname(__file__), "checkpoint", "610model_1000.pt")


def gelu(x):
    """The tanh form of GELU."""
    return F.gelu(x, approximate="tanh")


def _dense(i, o, gain=None):
    """``nn.Linear(i, o)`` with flax ``lecun_normal`` weights, or orthogonal ones of ``gain``; zero bias."""
    lin = nn.Linear(i, o)
    with torch.no_grad():
        if gain is None:                     # flax lecun_normal (truncated normal)
            std = math.sqrt(1.0 / i) / 0.8796256610342398
            nn.init.trunc_normal_(lin.weight, std=std, a=-2 * std, b=2 * std)
        else:
            nn.init.orthogonal_(lin.weight, gain=gain)
        lin.bias.zero_()
    return lin


def _norm(d):
    """LayerNorm with the network's ``eps``."""
    return nn.LayerNorm(d, eps=1e-6)


class SelfAttention(nn.Module):
    """Self-attention over one ring with learned relative-position embeddings."""

    def __init__(self, d, heads, dh, L):
        super().__init__()
        self.h, self.dh = heads, dh
        self.qkv, self.out = _dense(d, 3 * heads * dh), _dense(heads * dh, d)
        self.rel_emb = nn.Parameter(torch.empty(heads, L, dh).normal_(std=0.02))
        pos = torch.arange(L)
        self.register_buffer("dist", pos[None, :] - pos[:, None], persistent=False)

    def forward(self, x, mask):
        """``x`` (B, L, d) with the validity ``mask`` (B, L) -> attended features."""
        B, L, _ = x.shape
        q, k, v = (t.permute(0, 2, 1, 3) for t in self.qkv(x).reshape(B, L, 3, self.h, self.dh).unbind(2))
        n = mask.sum(-1).clamp(min=1).view(B, 1, 1)
        rel = torch.gather(torch.einsum("bhid,hmd->bhim", q, self.rel_emb), 3,
                           (self.dist[None] % n).unsqueeze(1).expand(B, self.h, L, L))
        scores = (q @ k.transpose(-1, -2) + rel).masked_fill(~mask[:, None, None, :], -1e9)
        att = torch.softmax(scores / math.sqrt(self.dh), -1)
        return self.out((att @ v).permute(0, 2, 1, 3).reshape(B, L, -1))


class CrossAttention(nn.Module):
    """Attention from one ring to the other."""

    def __init__(self, d, heads, dh):
        super().__init__()
        self.h, self.dh = heads, dh
        self.q, self.kv, self.out = _dense(d, heads * dh), _dense(d, 2 * heads * dh), _dense(heads * dh, d)

    def forward(self, qs, kvs, qmask, kvmask):
        """Queries ``qs`` attend to ``kvs``; the masks mark the real (non-padding) letters."""
        B, Lq, _ = qs.shape
        q = self.q(qs).reshape(B, Lq, self.h, self.dh).permute(0, 2, 1, 3)
        k, v = (t.permute(0, 2, 1, 3) for t in self.kv(kvs).reshape(B, kvs.shape[1], 2, self.h, self.dh).unbind(2))
        s = (q @ k.transpose(-1, -2)).masked_fill(~kvmask[:, None, None, :], -1e9)
        s = s.masked_fill(~qmask[:, None, :, None], -1e9)
        return self.out((torch.softmax(s / math.sqrt(self.dh), -1) @ v).permute(0, 2, 1, 3).reshape(B, Lq, -1))


class Block(nn.Module):
    """Submodule names fix the flax parameter mapping in ``acx.rl.convert``."""

    def __init__(self, d, heads, dh, mlp, L):
        super().__init__()
        self.ln0, self.ln1, self.ln2, self.ln3, self.ln4, self.ln5 = (_norm(d) for _ in range(6))
        self.sa0, self.sa1 = SelfAttention(d, heads, dh, L), SelfAttention(d, heads, dh, L)
        self.ca0, self.ca1 = CrossAttention(d, heads, dh), CrossAttention(d, heads, dh)
        self.mlp0_in, self.mlp0_out, self.mlp1_in, self.mlp1_out = _dense(d, mlp), _dense(mlp, d), _dense(d, mlp), _dense(mlp, d)

    def forward(self, x1, x2, m1, m2):
        """Self-attend each ring, cross-attend them, then a per-ring MLP, all residual."""
        x1 = x1 + self.sa0(self.ln0(x1), m1)
        x2 = x2 + self.sa1(self.ln1(x2), m2)
        n1, n2 = self.ln2(x1), self.ln3(x2)
        x1 = x1 + self.ca0(n1, n2, m1, m2)
        x2 = x2 + self.ca1(n2, n1, m2, m1)
        x1 = x1 + self.mlp0_out(gelu(self.mlp0_in(self.ln4(x1))))
        x2 = x2 + self.mlp1_out(gelu(self.mlp1_in(self.ln5(x2))))
        return x1, x2


class ActorCritic(nn.Module):
    """The two-ring network: ``forward(obs) -> (logits, value)``."""

    def __init__(self, layers=2, heads=4, dh=8, mlp=32, vocab=5, L=24):
        super().__init__()
        d = heads * dh
        self.d, self.L = d, L
        self.embed = nn.Embedding(vocab, d)
        nn.init.normal_(self.embed.weight, std=math.sqrt(1.0 / d))
        self.blocks = nn.ModuleList(Block(d, heads, dh, mlp, L) for _ in range(layers))
        g = math.sqrt(2)
        self.critic0, self.critic1, self.critic2 = _dense(2 * d, 256, g), _dense(256, 256, g), _dense(256, 1, 1.0)
        self.actor0, self.actor1 = _dense(2 * d, 128, g), _dense(128, 4, 0.01)

    def action_mask(self, obs):
        """Legal ``(k1-1, k2, r)`` for either target ``i``: the seam letters cancel, both non-padding."""
        r1, r2 = obs[:, :self.L], obs[:, self.L:]
        pad = (r1 != 0)[:, :, None] & (r2 != 0)[:, None, :]
        legal = torch.stack([r1[:, :, None] == -r2[:, None, :], r1[:, :, None] == r2[:, None, :]], -1) & pad[..., None]
        return legal[:, :, :, None, :].expand(-1, self.L, self.L, 2, 2).reshape(obs.shape[0], -1)

    def forward(self, obs):
        """``(B, 2L)`` observations -> ``((B, 4 L^2)`` masked logits, ``(B,)`` values)."""
        B, L, d = obs.shape[0], self.L, self.d
        obs = obs.to(torch.long)
        r1, r2 = obs[:, :L], obs[:, L:]
        m1, m2 = r1 != 0, r2 != 0
        x1, x2 = self.embed(r1 + 2), self.embed(r2 + 2)
        for blk in self.blocks:
            x1, x2 = blk(x1, x2, m1, m2)
        pool = lambda x, m: (x * m[..., None]).sum(1) / (m.sum(1, keepdim=True) + 1e-6)
        joint = torch.cat([pool(x1, m1), pool(x2, m2)], -1)
        value = self.critic2(gelu(self.critic1(gelu(self.critic0(joint))))).squeeze(-1)
        w = self.actor0.weight
        h = gelu((x1 @ w[:, :d].t())[:, :, None] + (x2 @ w[:, d:].t())[:, None] + self.actor0.bias)
        return self.actor1(h).reshape(B, -1).masked_fill(~self.action_mask(obs), -1e9), value


def log_prob_entropy(logits, actions):
    """Log-probability of ``actions`` and the entropy of each row."""
    lp = torch.log_softmax(logits, -1)
    return lp.gather(1, actions[:, None]).squeeze(1), -(lp.exp() * lp).sum(-1)


def pretrained(path=CHECKPOINT):
    """The step-1000 610model policy, in eval mode."""
    model = ActorCritic()
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    return model.eval()
