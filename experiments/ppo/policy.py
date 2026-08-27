"""`RelativeDualRingActorCritic` in PyTorch.

A port of `network.py`'s flax module, structured so the shipped
`ppo_checkpoints/610model` weights transplant into it one-for-one (see
`transplant.py`). Details that decide whether parity holds at 1e-5:

- flax `LayerNorm` defaults to `epsilon=1e-6`; torch defaults to `1e-5`.
- flax `nn.gelu` is the **tanh approximation** by default; torch's default is
  the exact erf form, so every activation here passes `approximate="tanh"`.
- masking is `-1e9`, not `-inf`, and the `/ sqrt(head_dim)` scaling is applied
  *after* masking. Both are copied rather than tidied: a fully-masked attention
  row must come out uniform, not NaN, exactly as it does upstream.
- flax `Dense` kernels are `(in, out)`; torch `Linear` weights are `(out, in)`.

Two structural deviations, both float-noise level and both deliberate:

- The relative-position term is computed as `einsum(q, rel_emb)` followed by a
  gather over the distance, instead of gathering a `[B, H, L, L, Dh]` embedding
  tensor and contracting it. Identical arithmetic; the upstream form allocates
  `B * 18432` floats per ring per layer, which at a 28,560-row minibatch is
  several GB of nothing.
- The actor head's `Dense(128)` is applied separably -- `x1 @ W[:32] + x2 @ W[32:]
  + b`, broadcast into the outer-product grid -- rather than materialising the
  `[B, L, L, 64]` concatenation first. Same value up to summation order.

From-scratch initialisation follows flax's defaults (`lecun_normal` for
unspecified kernels, `orthogonal(gain)` where `network.py` names one). It cannot
match JAX's RNG stream, so a from-scratch torch run reproduces the *distribution*
of upstream results, never a specific seed's trajectory.
"""

import math

import torch
import torch.nn.functional as F
from torch import nn


def gelu(x):
    return F.gelu(x, approximate="tanh")


def _lecun_normal_(w, fan_in):
    """flax `lecun_normal()`: truncated normal, stddev corrected for truncation."""
    std = math.sqrt(1.0 / fan_in) / 0.8796256610342398
    with torch.no_grad():
        nn.init.trunc_normal_(w, std=std, a=-2 * std, b=2 * std)


def _dense(in_dim, out_dim, gain=None):
    lin = nn.Linear(in_dim, out_dim)
    with torch.no_grad():
        if gain is None:
            _lecun_normal_(lin.weight, in_dim)
        else:
            nn.init.orthogonal_(lin.weight, gain=gain)
        lin.bias.zero_()
    return lin


def _layer_norm(dim):
    return nn.LayerNorm(dim, eps=1e-6)


class RelativeSelfAttention(nn.Module):
    """`network.py:RelativeSelfAttention` -- cyclic relative-position attention.

    Distances are taken modulo each row's *true* relator length, so the two
    relators are treated as rings whose circumference is the word length rather
    than the padded width.
    """

    def __init__(self, d_model, num_heads, head_dim, max_len):
        super().__init__()
        self.h, self.dh, self.max_len = num_heads, head_dim, max_len
        self.qkv = _dense(d_model, 3 * num_heads * head_dim)
        self.rel_emb = nn.Parameter(torch.empty(num_heads, max_len, head_dim).normal_(std=0.02))
        self.out = _dense(num_heads * head_dim, d_model)
        pos = torch.arange(max_len)
        self.register_buffer("base_rel_dist", pos[None, :] - pos[:, None], persistent=False)

    def forward(self, x, mask):
        B, L, _ = x.shape
        H, Dh = self.h, self.dh
        q, k, v = self.qkv(x).reshape(B, L, 3, H, Dh).unbind(2)
        q, k, v = (t.permute(0, 2, 1, 3) for t in (q, k, v))

        content = q @ k.transpose(-1, -2)
        lengths = mask.sum(-1).clamp(min=1)
        rel_dist = self.base_rel_dist.unsqueeze(0) % lengths.view(B, 1, 1)
        rel_all = torch.einsum("bhid,hmd->bhim", q, self.rel_emb)
        rel = torch.gather(rel_all, 3, rel_dist.unsqueeze(1).expand(B, H, L, L))

        scores = (content + rel).masked_fill(~mask[:, None, None, :], -1e9)
        attn = torch.softmax(scores / math.sqrt(Dh), dim=-1)
        out = (attn @ v).permute(0, 2, 1, 3).reshape(B, L, H * Dh)
        return self.out(out)


class RelativeCrossAttention(nn.Module):
    """`network.py:RelativeCrossAttention` -- plain dot-product, no relative bias."""

    def __init__(self, d_model, num_heads, head_dim):
        super().__init__()
        self.h, self.dh = num_heads, head_dim
        self.q = _dense(d_model, num_heads * head_dim)
        self.kv = _dense(d_model, 2 * num_heads * head_dim)
        self.out = _dense(num_heads * head_dim, d_model)

    def forward(self, q_seq, kv_seq, q_mask, kv_mask):
        B, Lq, _ = q_seq.shape
        Lv = kv_seq.shape[1]
        H, Dh = self.h, self.dh
        q = self.q(q_seq).reshape(B, Lq, H, Dh).permute(0, 2, 1, 3)
        k, v = self.kv(kv_seq).reshape(B, Lv, 2, H, Dh).unbind(2)
        k, v = k.permute(0, 2, 1, 3), v.permute(0, 2, 1, 3)

        scores = q @ k.transpose(-1, -2)
        scores = scores.masked_fill(~kv_mask[:, None, None, :], -1e9)
        scores = scores.masked_fill(~q_mask[:, None, :, None], -1e9)
        attn = torch.softmax(scores / math.sqrt(Dh), dim=-1)
        out = (attn @ v).permute(0, 2, 1, 3).reshape(B, Lq, H * Dh)
        return self.out(out)


class RelativeDualRingBlock(nn.Module):
    """`network.py:RelativeDualRingBlock`. Submodule order fixes the flax names."""

    def __init__(self, d_model, num_heads, head_dim, mlp_dim, max_len):
        super().__init__()
        self.ln0, self.ln1 = _layer_norm(d_model), _layer_norm(d_model)
        self.sa0 = RelativeSelfAttention(d_model, num_heads, head_dim, max_len)
        self.sa1 = RelativeSelfAttention(d_model, num_heads, head_dim, max_len)
        self.ln2, self.ln3 = _layer_norm(d_model), _layer_norm(d_model)
        self.ca0 = RelativeCrossAttention(d_model, num_heads, head_dim)
        self.ca1 = RelativeCrossAttention(d_model, num_heads, head_dim)
        self.ln4, self.mlp0_in, self.mlp0_out = _layer_norm(d_model), _dense(d_model, mlp_dim), _dense(mlp_dim, d_model)
        self.ln5, self.mlp1_in, self.mlp1_out = _layer_norm(d_model), _dense(d_model, mlp_dim), _dense(mlp_dim, d_model)

    def forward(self, x1, x2, mask1, mask2):
        x1 = x1 + self.sa0(self.ln0(x1), mask1)
        x2 = x2 + self.sa1(self.ln1(x2), mask2)

        n1, n2 = self.ln2(x1), self.ln3(x2)
        x1 = x1 + self.ca0(n1, n2, mask1, mask2)
        x2 = x2 + self.ca1(n2, n1, mask2, mask1)

        x1 = x1 + self.mlp0_out(gelu(self.mlp0_in(self.ln4(x1))))
        x2 = x2 + self.mlp1_out(gelu(self.mlp1_in(self.ln5(x2))))
        return x1, x2


class RelativeDualRingActorCritic(nn.Module):
    """`network.py:RelativeDualRingActorCritic`.

    `forward(obs)` takes the flat `(B, 2L)` presentation and returns
    `(logits, value)` with `logits` already masked to legal actions.
    """

    def __init__(self, num_layers=2, num_heads=4, head_dim=8, mlp_dim=32,
                 vocab_size=5, max_len=24, activation="gelu"):
        super().__init__()
        d = num_heads * head_dim
        self.d_model, self.max_len = d, max_len
        self.act = gelu if activation == "gelu" else torch.tanh
        self.embed = nn.Embedding(vocab_size, d)
        with torch.no_grad():
            self.embed.weight.normal_(std=math.sqrt(1.0 / d))
        self.blocks = nn.ModuleList(
            RelativeDualRingBlock(d, num_heads, head_dim, mlp_dim, max_len) for _ in range(num_layers))
        self.critic0 = _dense(2 * d, 256, gain=math.sqrt(2))
        self.critic1 = _dense(256, 256, gain=math.sqrt(2))
        self.critic2 = _dense(256, 1, gain=1.0)
        self.actor0 = _dense(2 * d, 128, gain=math.sqrt(2))
        self.actor1 = _dense(128, 4, gain=0.01)

    @staticmethod
    def action_mask(obs, max_len):
        """Legal `(k1-1, k2, j)` triples: the seam letter must cancel.

        `j = 0` pairs `r1[a]` with the inverse of `r2[b]`, `j = 1` with `r2[b]`
        itself; both positions must be non-pad. The mask is independent of `i`,
        so it is broadcast across the two `i` values -- which is what makes the
        flat action space 2304 rather than 1152.
        """
        B = obs.shape[0]
        r1, r2 = obs[:, :max_len], obs[:, max_len:]
        pad = (r1 != 0)[:, :, None] & (r2 != 0)[:, None, :]
        semantic = torch.stack([r1[:, :, None] == -r2[:, None, :],
                                r1[:, :, None] == r2[:, None, :]], dim=-1)
        base = semantic & pad[..., None]                       # [B, L, L, 2] over (a, b, j)
        return base[:, :, :, None, :].expand(B, max_len, max_len, 2, 2).reshape(B, -1)

    def forward(self, obs):
        B = obs.shape[0]
        L = self.max_len
        obs = obs.to(torch.long)
        r1, r2 = obs[:, :L], obs[:, L:]
        mask1, mask2 = r1 != 0, r2 != 0
        final_mask = self.action_mask(obs, L)

        x1, x2 = self.embed(r1 + 2), self.embed(r2 + 2)
        for blk in self.blocks:
            x1, x2 = blk(x1, x2, mask1, mask2)

        def masked_mean(x, m):
            mf = m.to(x.dtype)
            return (x * mf[:, :, None]).sum(1) / (mf.sum(1, keepdim=True) + 1e-6)

        joint = torch.cat([masked_mean(x1, mask1), masked_mean(x2, mask2)], dim=-1)
        value = self.critic2(self.act(self.critic1(self.act(self.critic0(joint))))).squeeze(-1)

        d = self.d_model
        w = self.actor0.weight                                 # [128, 2d]
        a = x1 @ w[:, :d].t()                                  # [B, L, 128]
        b = x2 @ w[:, d:].t()
        h = self.act(a[:, :, None, :] + b[:, None, :, :] + self.actor0.bias)
        logits = self.actor1(h).reshape(B, -1)
        return logits.masked_fill(~final_mask, -1e9), value


def action_stats(logits, actions):
    """`log_prob` and `entropy` of the masked Categorical, as distrax computes them."""
    logp_all = torch.log_softmax(logits, dim=-1)
    log_prob = logp_all.gather(1, actions.unsqueeze(1).to(torch.long)).squeeze(1)
    entropy = -(logp_all.exp() * logp_all).sum(-1)
    return log_prob, entropy


def sample_actions(logits, generator=None):
    """One draw per row from the masked Categorical."""
    probs = torch.softmax(logits, dim=-1)
    return torch.multinomial(probs, 1, generator=generator).squeeze(1)
