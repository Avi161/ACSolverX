import csv, html, json, os

W = "/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/hs-docs"
T = os.path.join(W, "results/equivalence_classes/ms1190_tables")
C = os.path.join(W, "results/clustering")
DEST = "/Users/avigyapaudel/.claude/jobs/95ce2a8b/tmp/ms1190_tables.html"

solved = list(csv.DictReader(open(T + "/solved_640_aut_orbits.csv")))
unsolved = list(csv.DictReader(open(T + "/unsolved_124_aca_classes.csv")))
R = json.load(open(C + "/cluster_report.json"))
WB = json.load(open(C + "/within_bucket.json"))
RK = json.load(open(C + "/signal_ranking.json"))
HO = json.load(open(C + "/holdout_eval.json"))
HS = os.path.join(W, "results/heuristic_search")
SW = json.load(open(HS + "/sweep.json"))
T2 = json.load(open(HS + "/top2_1000.json"))
TM = json.load(open(HS + "/tune_multi.json"))
CP = json.load(open(HS + "/cost_profile.json"))
HY = json.load(open(HS + "/hyper.json"))
TA, TB = R["tables"], R["provenance-matched"]
e = html.escape


def w(word):
    return "".join(f'<i class="inv">{c.lower()}</i>' if c.isupper() else c for c in word)


def chips(items, kind):
    s = "".join(f'<span class="chip {kind}">{e(c)}</span>' for c in items[:5])
    if items[5:]:
        s += (f'<button class="more" type="button" aria-expanded="false">+{len(items[5:])}</button>'
              '<span class="hidden-chips" hidden>'
              + "".join(f'<span class="chip {kind}">{e(c)}</span>' for c in items[5:]) + "</span>")
    return s


# ------------------------------------------------------------------ svg: pca scatter
def scatter(pay, rep, w_=430, h_=310):
    pts = pay["coords"][rep]
    lab = pay["labels"]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    px = lambda v: 34 + (v - x0) / (x1 - x0 or 1) * (w_ - 52)
    py = lambda v: h_ - 30 - (v - y0) / (y1 - y0 or 1) * (h_ - 52)
    marks = ""
    for i, p in enumerate(pts):
        cx, cy = px(p[0]), py(p[1])
        if lab[i] == 0:                                   # solved -> circle
            marks += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.3" class="d0"/>'
        else:                                             # unsolved -> triangle
            marks += (f'<polygon points="{cx:.1f},{cy-4.0:.1f} {cx+3.7:.1f},{cy+2.6:.1f} '
                      f'{cx-3.7:.1f},{cy+2.6:.1f}" class="d1"/>')
    return (f'<svg viewBox="0 0 {w_} {h_}" role="img" aria-label="PCA scatter, {e(rep)}. '
            f'Circles are solved, triangles unsolved.">'
            f'<rect x="0" y="0" width="{w_}" height="{h_}" class="plotbg"/>{marks}'
            f'<text x="34" y="{h_-8}" class="axl">PC1</text>'
            f'<text x="10" y="20" class="axl">PC2</text></svg>')


# Shape carries the class independently of hue, so the legend must show the shape, not a swatch.
LEG = ('<div class="legend">'
       '<span><svg viewBox="0 0 12 12" aria-hidden="true"><circle cx="6" cy="6" r="4.2" class="d0"/></svg>'
       'solved (circle)</span>'
       '<span><svg viewBox="0 0 12 12" aria-hidden="true"><polygon points="6,1.4 10.8,10 1.2,10" class="d1"/></svg>'
       'unsolved (triangle)</span></div>')


def knot_hist_svg(pay, w_=430, h_=250):
    hs, hu = pay["knots"]["knot_hist"]["solved"], pay["knots"]["knot_hist"]["unsolved"]
    keys = sorted({int(k) for k in list(hs) + list(hu)})
    mx = max(list(hs.values()) + list(hu.values()))
    bw = (w_ - 70) / max(len(keys), 1)
    bars = ""
    for i, k in enumerate(keys):
        for j, (hh, cl) in enumerate(((hs, "ba"), (hu, "bb"))):
            v = hh.get(str(k), hh.get(k, 0))
            ht = (v / mx) * (h_ - 66)
            x = 52 + i * bw + j * (bw * 0.38) + bw * 0.06
            bars += (f'<rect x="{x:.1f}" y="{h_-36-ht:.1f}" width="{bw*0.36:.1f}" '
                     f'height="{ht:.1f}" class="{cl}"/>')
            bars += (f'<text x="{x+bw*0.14:.1f}" y="{h_-25:.1f}" class="axl">'
                     f'{"s" if j==0 else "u"}</text>')
            if v:
                bars += (f'<text x="{x+bw*0.10:.1f}" y="{h_-40-ht:.1f}" class="bl">{v}</text>')
        bars += f'<text x="{52+i*bw+bw*0.35:.1f}" y="{h_-18}" class="axl">{k}</text>'
    return (f'<svg viewBox="0 0 {w_} {h_}" role="img" aria-label="max knot histogram">'
            f'<rect width="{w_}" height="{h_}" class="plotbg"/>{bars}'
            f'<text x="{w_/2-40:.0f}" y="{h_-3}" class="axl">max knots on one relator</text></svg>')


def null_svg(pay, w_=430, h_=118):
    nl, best = pay["null"], pay["best"]["ari"]
    hi = max(best * 1.12, 0.1)
    sx = lambda v: 34 + (v / hi) * (w_ - 60)
    return (f'<svg viewBox="0 0 {w_} {h_}" role="img" aria-label="observed vs null">'
            f'<rect width="{w_}" height="{h_}" class="plotbg"/>'
            f'<rect x="{sx(0):.0f}" y="34" width="{sx(nl["max"])-sx(0):.1f}" height="17" class="bn"/>'
            f'<text x="{sx(nl["max"])+7:.0f}" y="47" class="bl">null best-of-grid, max over '
            f'{pay["n_perm"]} permutations = {nl["max"]:.3f}</text>'
            f'<rect x="{sx(0):.0f}" y="64" width="{sx(best)-sx(0):.1f}" height="17" class="bb"/>'
            f'<text x="{sx(0)+7:.0f}" y="77" class="bl2">observed {best:.3f}</text>'
            f'<text x="34" y="22" class="axl">ARI vs the solved / unsolved split</text></svg>')


def prof_rows(pay):
    return "".join(
        f'<tr><td class="id">cluster {p["cluster"]}</td><td class="num">{p["n"]}</td>'
        f'<td class="num">{p["mean_length"]:.1f}</td><td class="num">{p["mean_max_knots"]:.2f}</td>'
        f'<td class="num">{p["mean_unevenness"]:.2f}</td>'
        f'<td class="num"><span class="count {"b" if p["pct_unsolved"]>.5 else "a"}">'
        f'{p["pct_unsolved"]*100:.1f}%</span></td></tr>' for p in pay["profile"])


def top_rows(pay, n=12):
    return "".join(
        f'<tr><td class="mono sm">{e(r["representation"])}</td><td class="mono sm">{e(r["preproc"])}</td>'
        f'<td class="mono sm">{e(r["metric"])}</td><td class="mono sm">{e(r["algorithm"])}</td>'
        f'<td class="num">{r["k"]}</td><td class="num"><b>{r["ari"]:.4f}</b></td>'
        f'<td class="num">{r["bal_acc"]:.3f}</td></tr>' for r in pay["top"][:n])


def knot_rows(pay):
    out = ""
    for r in pay["knots"]["features"]:
        scale_free = r["feature"] in ("knot density", "max block / length", "max / mean block",
                                      "block CV (std/mean)")
        am = r.get("auc_matched")
        strong = abs(r["auc"] - .5) > .25
        pill = ' <span class="pill">scale-free</span>' if scale_free else ""
        am_cell = f'<td class="num">{am:.3f}</td>' if am is not None else '<td class="num">—</td>'
        out += (f'<tr class="{"sf" if scale_free else ""}"><td>{e(r["feature"])}{pill}</td>'
                f'<td class="num">{r["solved_mean"]:.2f}</td>'
                f'<td class="num">{r["unsolved_mean"]:.2f}</td>'
                f'<td class="num"><b class="{"hot" if strong else ""}">{r["auc"]:.3f}</b></td>'
                f'{am_cell}<td class="num">{r["cohens_d"]:+.2f}</td></tr>')
    return out


def rule_rows(pay):
    out = ""
    for r in pay["knots"]["rule"]:
        if r["threshold"] > 5:
            continue
        cls = "win" if r["bal_acc"] == max(x["bal_acc"] for x in pay["knots"]["rule"]) else ""
        note = ""
        if r["threshold"] == 3:
            note = ' <span class="pill">proposed</span>'
        if r["precision"] == 1.0 and r["tp"] > 0:
            note += ' <span class="pill pa">no false positives</span>'
        out += (f'<tr class="{cls}"><td class="num">&gt; {r["threshold"]}{note}</td>'
                f'<td class="num"><b>{r["bal_acc"]:.3f}</b></td>'
                f'<td class="num">{r["precision"]:.3f}</td><td class="num">{r["recall"]:.3f}</td>'
                f'<td class="num mono sm">{r["tp"]}/{r["fp"]}/{r["fn"]}/{r["tn"]}</td></tr>')
    return out


def maxknot_rows(pay):
    """max_knots -> class breakdown, with a proportion bar that reads without colour."""
    out = ""
    for r in pay["knots"]["table"]:
        n = r["n_solved"] + r["n_unsolved"]
        if n == 0:                                     # empty bucket: shown, never hidden
            out += (f'<tr class="empty"><td class="num"><b>{r["max_knots"]}</b></td>'
                    f'<td class="num">0</td><td class="num">0</td>'
                    f'<td colspan="4" class="sm" style="color:var(--ink-3)">'
                    f'empty — no presentation reaches this value</td></tr>')
            continue
        ps = r["n_solved"] / n * 100
        us = f'{r["unev_solved"]:.2f}' if r["unev_solved"] is not None else "—"
        uu = f'{r["unev_unsolved"]:.2f}' if r["unev_unsolved"] is not None else "—"
        ls = f'{r["len_solved"]:.1f}' if r["len_solved"] is not None else "—"
        lu = f'{r["len_unsolved"]:.1f}' if r["len_unsolved"] is not None else "—"
        pure = ' <span class="pill pa">no solved</span>' if r["n_solved"] == 0 else ""
        out += (f'<tr><td class="num"><b>{r["max_knots"]}</b>{pure}</td>'
                f'<td class="num">{r["n_solved"]}</td><td class="num">{r["n_unsolved"]}</td>'
                f'<td><div class="stack" title="{ps:.0f}% solved">'
                f'<i class="sa" style="width:{ps:.1f}%"></i>'
                f'<i class="sb" style="width:{100-ps:.1f}%"></i></div></td>'
                f'<td class="num"><b>{r["pct_unsolved"]*100:.1f}%</b></td>'
                f'<td class="num">{us} / {uu}</td><td class="num">{ls} / {lu}</td></tr>')
    return out


def perrel_rows(pay):
    out = ""
    for r in pay["knots"]["per_relator"]:
        n = r["n_solved"] + r["n_unsolved"]
        note = ('<span class="sm" style="color:var(--ink-3)"> — a pure power: it kills a '
                'generator outright, so nothing is squashed inside anything</span>'
                if r["knots"] == 0 else "")
        out += (f'<tr class="{"empty" if n == 0 else ""}"><td class="num"><b>{r["knots"]}</b></td>'
                f'<td class="num">{n}</td><td class="num">{r["n_solved"]}</td>'
                f'<td class="num">{r["n_unsolved"]}</td><td>{note}</td></tr>')
    return out


def minknot_rows(pay):
    out = ""
    for r in pay["knots"]["table_min"]:
        n = r["n_solved"] + r["n_unsolved"]
        if n == 0:
            out += (f'<tr class="empty"><td class="num"><b>{r["min_knots"]}</b></td>'
                    f'<td class="num">0</td><td class="num">0</td>'
                    f'<td class="sm" style="color:var(--ink-3)">empty</td></tr>')
            continue
        pure = ' <span class="pill pa">no solved</span>' if r["n_solved"] == 0 else ""
        out += (f'<tr><td class="num"><b>{r["min_knots"]}</b>{pure}</td>'
                f'<td class="num">{r["n_solved"]}</td><td class="num">{r["n_unsolved"]}</td>'
                f'<td class="num"><b>{r["pct_unsolved"]*100:.1f}%</b></td></tr>')
    return out


def rules2_rows(pay):
    return "".join(
        f'<tr><td class="mono sm">{e(r["rule"])}</td><td class="num">{r["n_solved"]}</td>'
        f'<td class="num">{r["n_unsolved"]}</td>'
        f'<td class="num"><b>{r["precision"]:.3f}</b></td>'
        f'<td class="num">{r["recall"]:.3f}</td></tr>' for r in pay["knots"]["rules2"])


def TAB(pay, v):
    """Row for a given max_knots value. Positional indexing broke once empty buckets were kept."""
    return next(r for r in pay["knots"]["table"] if r["max_knots"] == v)


def wb_rows(b):
    out = ""
    for r in WB[b]["features"]:
        dead = r["auc"] == 0.5
        cls = "win" if r.get("beats_length") and r["survives"] else ("empty" if dead else "")
        verdict = ("beats length" if r.get("beats_length") and r["survives"]
                   else ("survives null" if r["survives"] else "—"))
        out += (f'<tr class="{cls}"><td>{e(r["feature"])}</td>'
                f'<td class="num">{r["solved_mean"]:.2f}</td>'
                f'<td class="num">{r["unsolved_mean"]:.2f}</td>'
                f'<td class="num"><b>{r["auc"]:.3f}</b></td>'
                f'<td class="num">{r["auc_length_removed"]:.3f}</td>'
                f'<td class="sm">{verdict}</td></tr>')
    return out


def sig_rows(b):
    w = WB[b]["signatures"]
    rows = ""
    for tag, cl in (("solved", "a"), ("unsolved", "b")):
        for sig, n in w[tag][:4]:
            rows += (f'<tr><td><span class="count {cl}">{tag}</span></td>'
                     f'<td class="mono sm">{e(sig)}</td><td class="num">{n}</td></tr>')
    return rows


def rank_rows(pop):
    rows = RK["populations"][pop]
    yard = next(r for r in rows if r["feature"] == "total length")
    out = ""
    for r in rows:
        is_yard = r["feature"] == "total length"
        lr = "—" if r["auc_length_removed"] is None else f'{r["auc_length_removed"]:.3f}'
        beats = (not is_yard) and abs(r["auc"] - .5) > abs(yard["auc"] - .5)
        cls = "win" if r["feature"] == RK["winner"] else ("empty" if is_yard else "")
        tag = (' <span class="pill">winner</span>' if r["feature"] == RK["winner"]
               else (' <span class="pill pa">yardstick</span>' if is_yard else ""))
        out += (f'<tr class="{cls}"><td>{e(r["feature"])}{tag}</td>'
                f'<td class="num"><b>{r["auc"]:.3f}</b></td><td class="num">{lr}</td>'
                f'<td class="num">{r["auc_matched_band"]:.3f}</td>'
                f'<td class="num mono sm">&gt; {r["rule"]["threshold"]:.2f}</td>'
                f'<td class="num">{r["rule"]["bal_acc"]:.3f}</td>'
                f'<td class="sm">{"beats length" if beats else ""}</td></tr>')
    return out


MODEL_NAMES = ("ALL (logistic)", "3-feature (logistic)")


def spread(r, w_=190, h_=26):
    """min -- (mean +/- sigma) -- max on a fixed 0.45..1.0 track, so every row is comparable."""
    lo, hi = 0.45, 1.0
    X = lambda v: 6 + (min(max(v, lo), hi) - lo) / (hi - lo) * (w_ - 12)
    a, b = X(r["acc_mean"] - r["acc_std"]), X(r["acc_mean"] + r["acc_std"])
    c = "var(--b-dot)" if r["feature"] in MODEL_NAMES else "var(--a-dot)"
    return (f'<svg viewBox="0 0 {w_} {h_}" width="{w_}" height="{h_}" role="img" '
            f'aria-label="mean {r["acc_mean"]:.3f}, sd {r["acc_std"]:.3f}, range '
            f'{r["acc_min"]:.3f} to {r["acc_max"]:.3f}">'
            f'<line x1="{X(r["acc_min"]):.1f}" x2="{X(r["acc_max"]):.1f}" y1="13" y2="13" '
            f'stroke="var(--line-2)" stroke-width="1.5"/>'
            f'<rect x="{a:.1f}" y="7" width="{max(b - a, 1.5):.1f}" height="12" rx="3" fill="{c}" '
            f'opacity=".38"/>'
            f'<circle cx="{X(r["acc_mean"]):.1f}" cy="13" r="4" fill="{c}"/>'
            f'<line x1="{X(0.5):.1f}" x2="{X(0.5):.1f}" y1="4" y2="22" stroke="var(--ink-3)" '
            f'stroke-width="1" stroke-dasharray="2 2" opacity=".55"/></svg>')


def holdout_rows(pop):
    pay = HO["populations"][pop]
    base = pay["shuffle_control"]["base_rate"]
    out = ""
    for r in pay["features"]:
        is_model = r["feature"] in MODEL_NAMES
        is_yard = r["feature"] == "total length"
        cls = "win" if r["feature"] == "ALL (logistic)" else ("empty" if is_yard else "")
        tag = (' <span class="pill pb">multivariate</span>' if is_model
               else (' <span class="pill pa">yardstick</span>' if is_yard else ""))
        mt = r["modal_threshold"]
        cut = "—" if mt is None else (
            f'{"&gt;" if mt["rule"].endswith("|1") else "&#8804;"} '
            f'{mt["rule"].split("|")[0]} <span class="sm">· {mt["share"] * 100:.0f}%</span>')
        out += (f'<tr class="{cls}"><td>{e(r["feature"])}{tag}</td>'
                f'<td class="num"><b>{r["acc_mean"]:.3f}</b> '
                f'<span class="sm">± {r["acc_std"]:.3f}</span></td>'
                f'<td>{spread(r)}</td>'
                f'<td class="num sm">{r["acc_min"]:.3f}</td>'
                f'<td class="num"><b>{r["acc_max"]:.3f}</b> '
                f'<span class="sm">@{r["best_seed"]}</span></td>'
                f'<td class="num sm mono">{cut}</td></tr>')
    out += (f'<tr class="empty"><td>labels shuffled <span class="pill">control</span></td>'
            f'<td class="num">{pay["shuffle_control"]["acc_mean"]:.3f}</td><td></td>'
            f'<td colspan="3" class="sm">base rate {base:.3f} — a leak would show as a number '
            f'above this</td></tr>')
    return out


FEATURE_DEFS = [
    ("smaller mean block", "mean run length of whichever generator appears in <b>shorter</b> runs"),
    ("larger mean block", "the same for the other generator"),
    ("max_knots", "max(knots(r&#8321;), knots(r&#8322;))"),
    ("min_knots", "min(knots(r&#8321;), knots(r&#8322;))"),
    ("knot number (sum)", "knots(r&#8321;) + knots(r&#8322;)"),
    ("knot density", "knot sum &divide; total length"),
    ("max / mean block", "block unevenness — how far the longest run exceeds the average"),
    ("block CV", "standard deviation &divide; mean of the run lengths"),
    ("max block length", "longest single run"),
    ("mean block length", "mean run length over both generators"),
    ("total length", "|r&#8321;| + |r&#8322;| — the confound, and the 11th column"),
]


def feature_defs():
    out = ""
    for i, (n, d) in enumerate(FEATURE_DEFS, 1):
        yard = n == "total length"
        out += (f'<tr class="{"empty" if yard else ""}">'
                f'<td class="num sm">{"—" if yard else i}</td>'
                f'<td class="mono sm">{e(n)}'
                f'{" <span class=\'pill pa\'>yardstick</span>" if yard else ""}</td>'
                f'<td class="sm">{d}</td></tr>')
    return out


def fwd_rows(pop):
    pay = HO["populations"][pop]["forward_selection"]
    out = ""
    for st in pay["path"]:
        out += (f'<tr><td class="num sm">{st["n_features"]}</td>'
                f'<td class="mono sm">+ {e(st["added"])}</td>'
                f'<td class="num"><b>{st["acc"]:.3f}</b></td>'
                f'<td class="num sm">{st["gain"]:+.3f}</td></tr>')
    out += (f'<tr class="empty"><td></td><td class="sm">all 11 columns</td>'
            f'<td class="num">{pay["all_features"]:.3f}</td><td></td></tr>')
    return out


# --------------------------------------------------------------- heuristic search helpers

def arm_rows(split, budgets=("100", "200", "500")):
    """One row per ordering; delta against the length control at each budget."""
    pay = SW[split]
    names = [n for n in pay[budgets[-1]] if n != "length"]
    base = {b: pay[b]["length"]["solved"] for b in budgets}
    n = len(SW[{"tune": "tune_ids", "exploratory": "exploratory_ids",
                "confirm": "confirm_ids"}[split]])
    out = (f'<tr class="empty"><td>length <span class="pill pa">baseline</span></td>'
           + "".join(f'<td class="num">{base[b]}/{n}</td>' for b in budgets) + "<td></td></tr>")
    for nm in sorted(names, key=lambda k: -pay[budgets[-1]][k]["solved"]):
        cells = ""
        for b in budgets:
            r = pay[b][nm]
            d = r["solved"] - base[b]
            cls = "pos" if d > 0 else ("neg" if d < 0 else "")
            cells += (f'<td class="num"><b>{r["solved"]}</b>/{n} '
                      f'<span class="sm {cls}">{d:+d}</span></td>')
        r5 = pay[budgets[-1]][nm]
        best = r5["solved"] == max(pay[budgets[-1]][k]["solved"] for k in names)
        out += (f'<tr class="{"win" if best else ""}"><td class="mono sm">{e(nm)}</td>{cells}'
                f'<td class="sm">{len(r5["won"])}W&#8211;{len(r5["lost"])}L</td></tr>')
    return out


def t2_rows():
    res, arms = T2["results"], T2["arms"]
    out = ('<tr class="empty"><td>length <span class="pill pa">baseline</span></td>'
           f'<td class="num">{res["500"]["length"]["solved"]}/20</td>'
           f'<td class="num">{res["1000"]["length"]["solved"]}/20</td><td></td><td></td></tr>')
    for a in arms:
        r5, r1k = res["500"][a], res["1000"][a]
        nm = ("&#8212;" if r1k["nodes_both_mean"] is None else
              f'{r1k["nodes_both_mean"]:.0f} vs {r1k["nodes_both_ctrl_mean"]:.0f} '
              f'<b>&times;{r1k["nodes_both_mean"] / r1k["nodes_both_ctrl_mean"]:.2f}</b>')
        grew = r1k["net"] > r5["net"]
        out += (f'<tr class="{"win" if grew else ""}"><td class="mono sm">{e(a)}</td>'
                f'<td class="num">{r5["solved"]}/20 <span class="sm pos">{r5["net"]:+d}</span></td>'
                f'<td class="num"><b>{r1k["solved"]}</b>/20 '
                f'<span class="sm {"pos" if r1k["net"] > 0 else ""}">{r1k["net"]:+d}</span></td>'
                f'<td class="sm">{len(r1k["won"])}W&#8211;{len(r1k["lost"])}L</td>'
                f'<td class="num sm">{nm}</td></tr>')
    return out


def tm_rows():
    out = ""
    for sp in TM["splits"]:
        p = sp["params"]
        out += (f'<tr><td class="num sm">{sp["seed"]}</td>'
                f'<td class="mono sm">{p["T"]:.0f}, {p["a_knots"]:.2f}, '
                f'{p["a_maxknots"]:.2f}, <b>{p["a_smb"]:.2f}</b></td>'
                f'<td class="num sm">{sp["train_best"]}/30 <span class="sm">(base '
                f'{sp["train_baseline"]})</span></td>'
                f'<td class="num"><b>{sp["test_best"]}</b>/30 <span class="sm">(base '
                f'{sp["test_baseline"]})</span></td>'
                f'<td class="num pos"><b>{sp["test_gain"]:+d}</b></td></tr>')
    return out


def cp_rows():
    out = ""
    for r in CP["rows"]:
        dn = r["nodes_tuned"] / r["nodes_baseline"]
        dp = r["path_tuned"] - r["path_baseline"]
        out += (f'<tr><td class="num">{r["budget"]}</td>'
                f'<td class="num"><b>{r["solved_tuned"]}</b>/60 vs {r["solved_baseline"]} '
                f'<span class="sm pos">+{r["solved_tuned"] - r["solved_baseline"]}</span></td>'
                f'<td class="num">{r["nodes_tuned"]:.1f} vs {r["nodes_baseline"]:.1f} '
                f'<b class="pos">&times;{dn:.2f}</b></td>'
                f'<td class="num">{r["path_tuned"]:.2f} vs {r["path_baseline"]:.2f} '
                f'<span class="sm {"pos" if dp < 0 else ""}">{dp:+.2f}</span></td>'
                f'<td class="num sm">{r["path_tuned_all_solves"]:.2f}</td></tr>')
    return out


def hpair(v):
    return f"{v[0]}/{v[1]}"


def hyper_fullbench_rows(budget):
    out = ""
    for r in HY["fullbench"][budget]:
        is_base = r["label"].startswith("baseline")
        is_win = r["label"].startswith(f"{budget}-winner")
        cls = "empty" if is_base else ("win" if is_win else "")
        out += (f'<tr class="{cls}"><td class="mono sm">{e(r["label"])}</td>'
                f'<td class="num"><b>{hpair(r["total"])}</b></td>'
                f'<td class="num">{hpair(r["easy"])}</td>'
                f'<td class="num">{hpair(r["b4"])}</td>'
                f'<td class="num">{hpair(r["b5"])}</td>'
                f'<td class="num">{hpair(r["b6"])}</td>'
                f'<td class="num">{hpair(r["b7"])}</td>'
                f'<td class="num">{hpair(r["hump"])}</td>'
                f'<td class="num">{hpair(r["reach"])}</td></tr>')
    return out


def hyper_reco_rows():
    formulas = {
        "500": ("while total-length &gt; 16: order by  L + 8&middot;knots "
                "&minus; 6&middot;xy-imbalance;&nbsp; else: pure length"),
        "1000": ("L + 2.5&middot;knots + 6.4&middot;max-knots + 8.5&middot;smaller-block "
                 "+ 3.3&middot;xy-imbalance &nbsp;<span class=\"sm\" style=\"color:var(--ink-3)\">"
                 "— no threshold needed, applied at every length</span>"),
    }
    h = HY["headline"]
    out = ""
    for b in ("500", "1000"):
        fb = next(r for r in HY["fullbench"][b] if r["label"].startswith(f"{b}-winner"))
        tuned, base = (h["tuned_500"], h["baseline_500"]) if b == "500" else (h["tuned"], h["baseline"])
        out += (f'<tr><td class="num"><b>{b}</b></td>'
                f'<td class="mono sm">{formulas[b]}</td>'
                f'<td class="num"><b>{hpair(fb["total"])}</b></td>'
                f'<td class="num"><b>{tuned}/{h["n"]}</b> '
                f'<span class="sm">vs baseline {base}/{h["n"]}</span></td></tr>')
    return out


def hyper_feature_rows(top=6):
    out = (f'<tr class="empty"><td>length <span class="pill pa">baseline</span></td><td></td>'
           f'<td class="num">{HY["baseline_train500"]}/40</td><td class="num">0</td><td></td></tr>')
    for r in HY["feature_screen"][:top]:
        out += (f'<tr><td class="mono sm">{e(r["feature"])}</td>'
                f'<td class="num">{r["weight"]:+g}</td>'
                f'<td class="num"><b>{r["solved"]}</b>/40</td>'
                f'<td class="num">{r["net"]:+d}</td>'
                f'<td class="num">{r["p"]:.3f}</td></tr>')
    return out


def hyper_speedup_rows():
    out = ""
    for r in HY["wave2"]["speedup"]:
        out += (f'<tr><td class="mono sm">{e(r["name"])}</td>'
                f'<td class="num">{r["baseline_nodes"]:,}</td>'
                f'<td class="num"><b>{r["knot_nodes"]:,}</b></td>'
                f'<td class="num"><b>&times;{r["factor"]}</b></td></tr>')
    return out


def hyper_distinct_rows():
    dp = HY["wave2"]["distinct_problems"]
    out = ""
    for b in ("500", "1000"):
        d = dp[b]
        out += (f'<tr><td class="num"><b>{b}</b></td>'
                f'<td class="num">{d["baseline"]}/{d["n"]}<span class="sm"> &#8594; </span>'
                f'<b>{d["best"]}/{d["n"]}</b></td></tr>')
    return out


def hyper_threshold_rows():
    kt = HY["wave2"]["knot_threshold"]
    out = ""
    for stratum in ("easy", "hard"):
        d = kt[stratum]
        mx = max(d["solved"])
        cells = "".join(
            f'<td class="num">{"<b>" + str(s) + "</b>" if s == mx else s}</td>' for s in d["solved"])
        out += f'<tr><td>{e(stratum)}</td><td class="num">{d["n"]}</td>{cells}</tr>'
    return out


def hyper_negatives_list():
    items = HY["wave2"]["negatives"]
    return "<br>\n      ".join(
        f'&bull; <b>{e(r["axis"])}</b> — {e(r["result"].replace(" - ", " — "))}' for r in items)


def hyper_scaling_rows():
    out = ""
    for r in HY["wave3"]["scaling"]["rows"]:
        cls = "win" if r["tail"] == "still growing" else ""
        out += (f'<tr class="{cls}"><td class="mono sm">{e(r["ordering"])}</td>'
                f'<td class="num">{r["g500"]:+d}</td><td class="num"><b>{r["g1000"]:+d}</b></td>'
                f'<td class="sm">{e(r["tail"])}</td></tr>')
    return out


def hyper_phase_rows():
    out = ""
    for r in HY["wave3"]["threshold"]["rows"]:
        out += (f'<tr><td class="mono sm">{e(r["climb"])}</td><td class="sm">{e(r["terms"])}</td>'
                f'<td class="num">{e(r["worth"])}</td></tr>')
    return out


def hyper_portfolio_rows():
    out = ""
    for r in HY["wave3"]["portfolio"]["rows"]:
        cls = "win" if r["k"] == 1 else ""
        out += (f'<tr class="{cls}"><td class="num"><b>{r["k"]}</b></td>'
                f'<td class="num">{r["each"]:,}</td><td class="num"><b>{r["richer"]}</b></td>'
                f'<td class="num">{r["K8"]}</td><td class="num">{r["baseline"]}</td></tr>')
    return out


def ceiling_rows(pay):
    return "".join(
        f'<tr><td class="mono sm">{e(r["representation"])}</td>'
        f'<td class="num">{r["knn5"]:.3f}</td><td class="num">{r["knn15"]:.3f}</td>'
        f'<td class="num">{r["logreg"]:.3f}</td>'
        f'<td class="num"><b>{r["logreg_nolen"]:.3f}</b></td></tr>'
        for r in sorted(pay["ceiling"], key=lambda x: -x["logreg_nolen"]))


def faith_rows(pay):
    return "".join(
        f'<tr><td class="mono sm">{e(k)}</td><td class="num">{v}</td>'
        f'<td class="num">{"yes" if pay["rotation_invariance"][k] < 1e-9 else "NO"}</td></tr>'
        for k, v in sorted(pay["faithfulness"].items(), key=lambda kv: -kv[1]))


rows_a = "".join(f'''<tr data-q="{e((r['aut_id']+' '+r['rep_r1']+' '+r['rep_r2']+' '+r['cells']).lower())}">
<td class="id">{r['aut_id']}</td>
<td class="rel"><code>{w(r['rep_r1'])}</code><span class="sep">,</span><code>{w(r['rep_r2'])}</code>
<div class="witness">MS witness <code>{w(r['ms_r1'])}</code> <span class="sep">,</span> <code>{w(r['ms_r2'])}</code></div></td>
<td class="num">{r['rep_len']}</td><td class="num"><span class="count a">{r['n_cells']}</span></td>
<td class="mem">{chips(r["cells"].split(), "a")}</td></tr>''' for r in solved)

rows_b = "".join(f'''<tr data-q="{e((r['aca_id']+' '+r['r1']+' '+r['r2']+' '+r['reps']).lower())}">
<td class="id">{r['aca_id']}</td>
<td class="rel"><code>{w(r['r1'])}</code><span class="sep">,</span><code>{w(r['r2'])}</code></td>
<td class="num">{r['rep_len']}</td>
<td class="num"><span class="count b">{r['n_reps']}</span><span class="sub">{r['n_cells']}</span></td>
<td class="mem">{chips(r["reps"].split(), "b")}</td></tr>''' for r in unsolved)

CSS = """
/* Class is encoded by BLUE vs ORANGE (Okabe-Ito), which stays separable under deuteranopia,
   protanopia and tritanopia -- and never by colour alone: solved is a circle, unsolved a
   triangle, and every bar carries its own printed count and s/u letter. */
:root{--paper:#EEF1F3;--card:#FBFCFC;--ink:#141B22;--ink-2:#485866;--ink-3:#7F8E9B;
--line:#D3DBE1;--line-2:#E4EAEE;--a:#0A5C99;--a-soft:#DEEAF6;--a-line:#9CC1E0;--a-dot:#0072B2;
--b:#8A5300;--b-soft:#FAEAD1;--b-line:#DFB776;--b-dot:#E69F00;
--warn:#8E4A78;--warn-soft:#F6E5EF;--ok:#00795C;
--shadow:0 1px 2px rgba(20,27,34,.05),0 8px 24px -16px rgba(20,27,34,.28);}
@media (prefers-color-scheme:dark){:root{--paper:#10161B;--card:#171F26;--ink:#E6ECF0;--ink-2:#A0AFBB;
--ink-3:#6D7E8B;--line:#2A353E;--line-2:#212B33;--a:#72B9EC;--a-soft:#0F2739;--a-line:#2E5478;
--a-dot:#56B4E9;--b:#F0B54A;--b-soft:#33260C;--b-line:#6F5522;--b-dot:#E69F00;
--warn:#DFA3C6;--warn-soft:#2E1A26;--ok:#4FC3A1;
--shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -18px rgba(0,0,0,.8);}}
:root[data-theme="dark"]{--paper:#10161B;--card:#171F26;--ink:#E6ECF0;--ink-2:#A0AFBB;--ink-3:#6D7E8B;
--line:#2A353E;--line-2:#212B33;--a:#72B9EC;--a-soft:#0F2739;--a-line:#2E5478;--a-dot:#56B4E9;
--b:#F0B54A;--b-soft:#33260C;--b-line:#6F5522;--b-dot:#E69F00;
--warn:#DFA3C6;--warn-soft:#2E1A26;--ok:#4FC3A1;
--shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px -18px rgba(0,0,0,.8);}
:root[data-theme="light"]{--paper:#EEF1F3;--card:#FBFCFC;--ink:#141B22;--ink-2:#485866;--ink-3:#7F8E9B;
--line:#D3DBE1;--line-2:#E4EAEE;--a:#0A5C99;--a-soft:#DEEAF6;--a-line:#9CC1E0;--a-dot:#0072B2;
--b:#8A5300;--b-soft:#FAEAD1;--b-line:#DFB776;--b-dot:#E69F00;
--warn:#8E4A78;--warn-soft:#F6E5EF;--ok:#00795C;
--shadow:0 1px 2px rgba(20,27,34,.05),0 8px 24px -16px rgba(20,27,34,.28);}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
.wrap{max-width:1560px;margin:0 auto;padding:40px 28px 80px;display:flex;flex-direction:column;gap:38px}
h1{font-family:ui-serif,"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;font-weight:600;
font-size:clamp(28px,3.4vw,42px);line-height:1.12;margin:0;letter-spacing:-.015em;text-wrap:balance}
h2{font-family:ui-serif,"Iowan Old Style",Palatino,Georgia,serif;font-weight:600;font-size:26px;
margin:0 0 4px;letter-spacing:-.01em;text-wrap:balance}
h3{margin:0 0 6px;font-size:15px;font-weight:650}
.eyebrow{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600;margin-bottom:10px}
.lede{color:var(--ink-2);max-width:68ch;margin:12px 0 0}
p{max-width:72ch}
code,.mono{font-family:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace}
.sm{font-size:12px}
section{scroll-margin-top:20px}
nav{display:flex;gap:6px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:14px}
nav a{font-size:12.5px;color:var(--ink-2);text-decoration:none;padding:5px 10px;border-radius:7px;border:1px solid transparent}
nav a:hover{background:var(--card);border-color:var(--line);color:var(--ink)}
nav a:focus-visible{outline:2px solid var(--a);outline-offset:1px}
.funnel{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--line);
border:1px solid var(--line);border-radius:10px;overflow:hidden;box-shadow:var(--shadow)}
.step{background:var(--card);padding:18px 20px;display:flex;flex-direction:column;gap:3px}
.step .k{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);font-weight:600}
.step .v{font-family:ui-serif,Palatino,Georgia,serif;font-size:34px;line-height:1.05;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.step .d{font-size:12.5px;color:var(--ink-2)}
.step.sa .v{color:var(--a)}.step.sb .v{color:var(--b)}
.note{font-size:13.5px;color:var(--ink-2);border-left:2px solid var(--a-line);padding-left:13px;max-width:80ch}
.note b{color:var(--ink);font-weight:600}
.note.warn{border-color:var(--warn)}
.callout{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--a);border-radius:10px;
padding:18px 22px;box-shadow:var(--shadow);max-width:none}
.callout.b{border-left-color:var(--b)}.callout.w{border-left-color:var(--warn)}
.callout h3{font-size:16px}
.callout p{margin:8px 0 0;font-size:14px;color:var(--ink-2)}
.big{font-family:ui-serif,Palatino,Georgia,serif;font-size:40px;line-height:1;color:var(--a);
font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.big.b{color:var(--b)}
.tools{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
input[type=search]{flex:1;min-width:240px;max-width:420px;padding:9px 13px;font:inherit;font-size:14px;
background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px}
input[type=search]:focus-visible{outline:2px solid var(--a);outline-offset:1px;border-color:transparent}
.hits{font-size:13px;color:var(--ink-3);font-variant-numeric:tabular-nums}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:22px;align-items:start}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:20px;align-items:start}
.panel{background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);overflow:hidden}
.phead{padding:15px 20px;border-bottom:1px solid var(--line);display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}
.phead h2{font-size:16px;font-family:system-ui,sans-serif;font-weight:650;margin:0}
.tag{font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:3px 8px;border-radius:999px}
.tag.a{color:var(--a);background:var(--a-soft);border:1px solid var(--a-line)}
.tag.b{color:var(--b);background:var(--b-soft);border:1px solid var(--b-line)}
.tag.w{color:var(--warn);background:var(--warn-soft);border:1px solid var(--warn)}
.phead p{margin:0;flex-basis:100%;font-size:12.5px;color:var(--ink-2)}
.pbody{padding:16px 20px}
.scroll{max-height:72vh;overflow:auto}
.xscroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:13.5px}
thead th{position:sticky;top:0;z-index:2;background:var(--card);text-align:left;font-size:10.5px;
letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);font-weight:700;padding:9px 12px;
border-bottom:1px solid var(--line);white-space:nowrap}
tbody td{padding:8px 12px;border-bottom:1px solid var(--line-2);vertical-align:top}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:color-mix(in srgb,var(--paper) 55%,transparent)}
tr.sf{background:color-mix(in srgb,var(--a-soft) 40%,transparent)}
tr.win{background:color-mix(in srgb,var(--a-soft) 60%,transparent)}
tr.empty td{opacity:.5}
td.id{color:var(--ink-3);font-family:ui-monospace,Menlo,monospace;font-size:12px;white-space:nowrap;padding-top:10px}
td.rel code{font-size:13px}
td.rel .sep{color:var(--ink-3);margin:0 5px}
.inv{font-style:normal;position:relative}
.inv::after{content:"";position:absolute;left:0;right:0;top:-.18em;height:1px;background:currentColor;opacity:.85}
.witness{margin-top:3px;font-size:11px;color:var(--ink-3)}.witness code{font-size:11px}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--ink-2)}
.hot{color:var(--b)}
.count{display:inline-block;min-width:26px;padding:1px 6px;border-radius:5px;font-weight:650;font-size:12.5px}
.count.a{color:var(--a);background:var(--a-soft)}.count.b{color:var(--b);background:var(--b-soft)}
.sub{display:block;font-size:10.5px;color:var(--ink-3);margin-top:2px}
td.mem{min-width:210px}
.chip{display:inline-block;font-family:ui-monospace,Menlo,monospace;font-size:11px;padding:1px 5px;
margin:1px 3px 1px 0;border-radius:4px;border:1px solid var(--line);color:var(--ink-2)}
.chip.a{border-color:var(--a-line)}.chip.b{border-color:var(--b-line)}
.pill{font-size:10px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:1px 6px;
border-radius:999px;background:var(--a-soft);color:var(--a);border:1px solid var(--a-line)}
.pill.pa{background:var(--warn-soft);color:var(--warn);border-color:var(--warn)}
.pill.pb{background:var(--b-soft);color:var(--b);border-color:var(--b-line)}
.pos{color:var(--ok);font-weight:700}.neg{color:var(--warn)}
.more{font:inherit;font-size:11px;font-weight:650;cursor:pointer;padding:1px 6px;margin:1px 0;border-radius:4px;
border:1px dashed var(--line);background:transparent;color:var(--ink-3)}
.more:hover{color:var(--ink);border-color:var(--ink-3)}
.more:focus-visible{outline:2px solid var(--a);outline-offset:1px}
svg{display:block;width:100%;height:auto}
.plotbg{fill:transparent}
.d0{fill:var(--a-dot);opacity:.8}.d1{fill:var(--b-dot);opacity:.85}
.axl{fill:var(--ink-3);font-size:10px;font-family:system-ui,sans-serif}
.bl{fill:var(--ink-2);font-size:10.5px;font-family:system-ui,sans-serif}
.bl2{fill:#fff;font-size:10.5px;font-weight:700;font-family:system-ui,sans-serif}
rect.ba{fill:var(--a-dot)}rect.bb{fill:var(--b-dot)}rect.bn{fill:var(--ink-3);opacity:.45}
.legend{display:flex;gap:18px;font-size:12px;color:var(--ink-2);margin-top:10px;align-items:center}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:13px;height:13px;flex:none}
.stack{display:flex;height:22px;border-radius:4px;overflow:hidden;min-width:120px}
.stack i{display:block}
.stack i.sa{background:var(--a-dot)}.stack i.sb{background:var(--b-dot)}
footer{font-size:12.5px;color:var(--ink-3);border-top:1px solid var(--line);padding-top:20px}
footer code{font-size:11.5px;color:var(--ink-2)}
@media (max-width:640px){.wrap{padding:26px 16px 56px}.scroll{max-height:none}}
"""

# ------------------------------------------------------------------ held-out sweep numbers
_ha, _hb = HO["populations"]["A"], HO["populations"]["B"]
_fa = {r["feature"]: r for r in _ha["features"]}
_fb = {r["feature"]: r for r in _hb["features"]}
ho_n, ho_na, ho_nb = _ha["n_seeds"], _ha["n_test"], _hb["n_test"]
ho_rows_a, ho_rows_b = holdout_rows("A"), holdout_rows("B")
ho_hb_a = _fa["smaller mean block"]["acc_mean"]
ho_m3_a, ho_m3_b = _fa["3-feature (logistic)"]["acc_mean"], _fb["3-feature (logistic)"]["acc_mean"]
ho_mall_a = _fa["ALL (logistic)"]["acc_mean"]
ho_best_a, ho_worst_a = _fa["ALL (logistic)"]["acc_max"], _fa["ALL (logistic)"]["acc_min"]
ho_ctrl_a, ho_base_a = _ha["shuffle_control"]["acc_mean"], _ha["shuffle_control"]["base_rate"]
ho_ctrl_b, ho_base_b = _hb["shuffle_control"]["acc_mean"], _hb["shuffle_control"]["base_rate"]
hs_arms_tune, hs_arms_expl = arm_rows("tune"), arm_rows("exploratory")
hs_arms_conf, hs_t2, hs_tm, hs_cp = arm_rows("confirm"), t2_rows(), tm_rows(), cp_rows()
tm_test, tm_train = TM["mean_test_gain"], TM["mean_train_gain"]
ho_defs, ho_fwd_a, ho_fwd_b = feature_defs(), fwd_rows("A"), fwd_rows("B")
ho_f1_a = _ha["forward_selection"]["path"][0]["acc"]
ho_f2_a = _ha["forward_selection"]["path"][1]["acc"]
ho_f2_b = _fb["2-feature (logistic)"]["acc_mean"]
ho_f1s_b = _fb["smaller mean block"]["acc_mean"]
ho_se = (0.25 / ho_na) ** 0.5          # binomial se at p=0.5 -- the optimistic bound, quoted as such

# ------------------------------------------------------------------ hyperparameter search numbers
hy_b47_500, hy_b47_1000 = HY["bins47"]["500"], HY["bins47"]["1000"]
hy_full_500_base = next(r for r in HY["fullbench"]["500"] if r["label"].startswith("baseline"))["total"]
hy_full_500_win = next(r for r in HY["fullbench"]["500"] if r["label"].startswith("500-winner"))["total"]
hy_full_1000_base = next(r for r in HY["fullbench"]["1000"] if r["label"].startswith("baseline"))["total"]
hy_full_1000_win = next(r for r in HY["fullbench"]["1000"] if r["label"].startswith("1000-winner"))["total"]
hy_at15 = HY["auttest15"]
hy_path = HY["path1000"]
# hyper.json's knot_block_tie quotes a held-out tie ("7/7") measured on the same contaminated
# split as the retracted headline (see hy_corr below) - the figure itself was never re-verified
# against the 75-row replication set, so it is dropped rather than re-denominated to another guess.
hy_tie = ("The selection procedure chose a block climb (L &minus; 2&middot;max-block + 5&middot;smaller-block) "
          "at 1000; it and the knot climb both reach <b>43/66</b> on the full benchmark. The knot climb is "
          "recommended on principle; the block config's held-out tie was measured on the same contaminated "
          "split as the retracted headline above and was not re-verified against the 75-row replication set.")

# --- wave3: light typographic normalization of hyper.json's raw prose (hyphen -> em dash,
# "->" -> arrow, "10^6" -> superscript, ALL-CAPS emphasis -> <b>) to match page style; no
# content change.
hy_scaling_note = (HY["wave3"]["scaling"]["note"]
                    .replace("10^6", "10<sup>6</sup>")
                    .replace("->", "&#8594;")
                    .replace(" - ", " — "))
hy_threshold_note = (HY["wave3"]["threshold"]["note"]
                     .replace("LEAN knot-only climbs", "<b>lean</b> knot-only climbs")
                     .replace("a SINGLE weight vector", "a <b>single weight vector</b>"))
hy_portfolio_note = (HY["wave3"]["portfolio"]["note"]
                     .replace("a FIXED total budget", "a <b>fixed</b> total budget")
                     .replace("the FIRST string", "the <b>first</b> string")
                     .replace(" - ", " — "))
hy_union = HY["wave3"]["union"]
# wave2's unsolved124: the caveats panel used to describe the second hump from a 6-row sample;
# this is the exhaustive replacement (124 classes x 8 relabels x 4 orderings).
hy_u124 = HY["wave2"]["unsolved124"]
# NB: classes(124) x relabels(8) = 992, not the true start count (980) - a handful of classes
# realize fewer than 8 distinct signed-permutation relabels after dedup. Chain the multiplication
# through the measured "starts" field, not the nominal 8, so the arithmetic on the page is exact:
# starts(980) x orderings(4) = searches(3,920).
hy_u124_note = (f"The second hump was measured exhaustively, not inferred from a six-row sample: "
                f"all {hy_u124['classes']} unsolved AC-classes, each entered as up to {hy_u124['relabels']} "
                f"signed-permutation relabels ({hy_u124['starts']} realized starts after dedup), under all "
                f"{hy_u124['orderings']} best orderings — {hy_u124['starts']}&times;{hy_u124['orderings']} = "
                f"<b>{hy_u124['searches']:,}</b> searches, <b>{hy_u124['solved']}</b> solves. These classes "
                f"survived a 10<sup>6</sup>-node search; {hy_u124['budget']} nodes is three orders of "
                f"magnitude short.")

# --- round 4: headline (the leak-free, problem-counted framing), complement_cv (cross-validated
# correction to the union claim), hump_both_families (the second-hump negative, now cross-family).
hy_head = HY["headline"]
hy_head_note = hy_head["note"].replace("->", "&#8594;")
hy_cv = HY["complement_cv"]
hy_cv_note = (hy_cv["note"]
              .replace("FOR COMPLEMENTARITY", "<b>for complementarity</b>")
              .replace("320-config x 45-row", "320-config &times; 45-row")
              .replace("4x the default", "4&times; the default"))
hy_hump2 = HY["hump_both_families"]
hy_hump2_note = hy_hump2["note"].replace("bins 8-9", "bins 8&#8211;9")

# --- retraction: the page used to lead with a held-out figure contaminated by cross-slice leakage
# (see hy_corr below). headline is now the clean replacement; correction states what happened;
# retune is an independent stress-test that the (corrected) recommendation is not a training-set
# artifact.
hy_corr = HY["correction"]
# The retired label is rendered hyphenated ("1-of-6 -> 6-of-6") rather than as live "N of M" prose,
# both to read as a dead citation, not a current figure, and so it doesn't collide character-for-
# character with the live "of"-spaced numbers used everywhere else on the page.
hy_corr_note = (hy_corr["note"]
                .replace("1 of 6 -> 6 of 6", "<code>1-of-6 &#8594; 6-of-6</code>")
                .replace("a DIFFERENT slice", "a <b>different</b> slice")
                .replace("A split is only held out from the stage that actually chose the thing being scored.",
                         "<b>A split is only held out from the stage that actually chose the thing being "
                         "scored.</b>"))
hy_retune = HY["retune"]

page = f"""<title>Miller–Schupp 1190: shape of the minimal automorphic states — and a search heuristic from it</title>
<style>{CSS}</style>
<div class="wrap">
<header>
  <div class="eyebrow">Miller–Schupp benchmark · Aut(F₂) quotient · unsupervised structure · search heuristic</div>
  <h1>1190 presentations, 237 minimal automorphic states,<br>and whether their shape knows what is solved</h1>
  <p class="lede" style="font-weight:600">It does — and the same statistics, used as a <a href="#search">heap priority</a> instead of a label, take the greedy solver from <b>17/60 to 30/60</b> at a fixed budget of 100 nodes, without ever losing a presentation.</p>
  <p class="lede">Every cell is <code>MS(n,w) = ⟨x,y | x⁻¹yⁿxy⁻⁽ⁿ⁺¹⁾, x⁻¹w⟩</code> over 170 words and <code>n∈1..7</code>, split 640 trivial / 550 unsolved. Collapsing each side by its <b>minimal automorphic state</b> — Whitehead's complete Aut(F₂) invariant — leaves 113 solved orbits and 124 unsolved classes. This page asks whether <b>unsupervised</b> clustering of those states recovers the solved / unsolved split without ever being shown it. An overline marks an inverse generator. <b>Colour encoding is Okabe–Ito blue / orange and is never load-bearing on its own</b> — solved is a circle, unsolved a triangle, and every bar is labelled.</p>
</header>

<nav>
  <a href="#verdict">Verdict</a><a href="#strongest">Strongest signal</a><a href="#holdout">Held out</a><a href="#method">Representations</a><a href="#unsup">Unsupervised result</a>
  <a href="#sweep">The sweep &amp; null</a><a href="#provenance">Provenance control</a>
  <a href="#knots">Knots &amp; max_knots</a><a href="#within">Inside a bucket</a><a href="#diag">Diagnostics</a><a href="#caveats">Caveats</a>
  <a href="#hyper">The hyperparameter search</a>
  <a href="#search">→ A search heuristic</a><a href="#arms">The 25 orderings</a><a href="#tuned">Tuned blend</a><a href="#cost">What it costs</a><a href="#tables">The two tables</a>
</nav>

<section id="verdict">
  <h2>Verdict</h2>
  <div class="grid3" style="margin-top:14px">
    <div class="callout"><h3>Yes — and far beyond chance</h3>
      <div class="big">{TA['best']['ari']:.3f}</div>
      <p>Best ARI against the solved / unsolved split, from a purely unsupervised clustering. Best over the same grid on <b>{TA['n_perm']} permuted labellings</b> never exceeded <b>{TA['null']['max']:.3f}</b> — so this is {TA['best']['ari']/TA['null']['max']:.1f}× the ceiling of what the sweep can manufacture from noise. <b>p &lt; 0.001</b>.</p></div>
    <div class="callout b"><h3>One cluster is almost pure</h3>
      <div class="big b">98.1%</div>
      <p>In the provenance-matched population, a cluster of 104 states is 98.1% unsolved — found without the algorithm ever seeing a label. Its companion cluster of 71 is 86% solved.</p></div>
    <div class="callout w"><h3>It is not only length</h3>
      <div class="big" style="color:var(--warn)">2.5<span style="font-size:22px"> vs </span>2.0</div>
      <p>Mean <b>block unevenness</b> (max ÷ mean block length) for unsolved vs solved. This is scale-free by construction, holds inside the matched length band, and is the most robust discriminator found — AUC {TA['knots']['features'][8]['auc']:.2f} / {TB['knots']['features'][8]['auc']:.2f} across both populations.</p></div>
  </div>
</section>


<section id="strongest">
  <h2>The strongest single signal</h2>
  <p class="lede">Each candidate below was originally measured somewhere different — <code>max_knots</code> on the whole population, <code>smaller mean block</code> only inside one bucket, unevenness only in the matched band. Those numbers are not comparable, so picking a winner from them would be picking a winner from four different experiments. Here they are on one footing: both populations, raw AUC, AUC with total length regressed out, and AUC inside the matched length band. <b>Total length is the yardstick, not a candidate</b> — a statistic that scores below it has explained nothing new.</p>

  <div class="callout" style="margin-top:16px">
    <h3>smaller mean block — the thinner generator&#8217;s run length</h3>
    <div class="big">0.945</div>
    <p>Balanced accuracy of the single rule <code>smaller mean block &gt; 1.25</code> on all 237: <b>117 true / 6 false positives / 7 missed / 107 true negatives</b>, precision 0.951, recall 0.944. It is the only statistic that beats total length on raw AUC <i>and</i> keeps the most signal after length is regressed out <i>and</i> holds inside the matched band — on <b>both</b> populations. The same threshold, 1.25, is optimal in each independently.</p>
    <p><b>Read plainly:</b> take whichever generator appears in shorter runs and average its run length. In a solvable presentation it sits at or near 1 — that generator appears as <i>isolated single letters</i>. In an unsolvable one it climbs past 1.25 — the letters start <i>clumping into runs of two or more</i>.</p>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Population A — the two tables</h2><span class="tag a">113 + 124</span></div>
      <div class="xscroll"><table><thead><tr><th>statistic</th><th>AUC</th><th>length removed</th><th>matched band</th><th>best cut</th><th>bal acc</th><th></th></tr></thead>
      <tbody>{rank_rows("A")}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Population B — provenance-matched</h2><span class="tag b">113 + 159</span></div>
      <div class="xscroll"><table><thead><tr><th>statistic</th><th>AUC</th><th>length removed</th><th>matched band</th><th>best cut</th><th>bal acc</th><th></th></tr></thead>
      <tbody>{rank_rows("B")}</tbody></table></div></div>
  </div>

  <div class="callout w" style="margin-top:20px">
    <h3>What this demotes</h3>
    <p><b>max_knots</b> looked like the headline earlier: AUC 0.860 on population A, a clean monotone gradient, a hard ceiling at 4. But under the provenance control it falls to 0.673, and with length regressed out it reaches <b>0.490 — chance</b>. Once both sides are produced the same way, max_knots is largely a proxy for length. Its <i>rules</i> still stand (max_knots ≥ 4 and min_knots ≥ 3 each certify 14 unsolved with zero false positives) because those describe a tail, not a correlation.</p>
    <p><b>Block unevenness</b> (max ÷ mean block) is the other demotion: 0.803 / 0.820 raw, but 0.636 / 0.588 with length removed, and it collapses entirely <i>within</i> a bucket (0.689 → 0.432). It is a real between-bucket effect and not a within-bucket one.</p>
    <p><b>Total length itself is a serious confound</b> — AUC 0.809 and 0.831. Only <code>smaller mean block</code> clearly clears it on both populations.</p>
  </div>
</section>

<section id="holdout">
  <h2>Held out: refit on 70%, scored on the 30% it never saw</h2>
  <p class="lede">Every accuracy above was fitted and scored on the <i>same</i> states. That makes them upper bounds, not estimates — the threshold was chosen by scanning every value in the data, so part of the fit is the data&#8217;s own noise. Below, the cut is refit on a stratified <b>70%</b> and scored on a held-out <b>30%</b>, {ho_n} times with a different random split each time. The dashed tick on each bar is chance; the shaded band is ±1 standard deviation across splits.</p>

  <div class="grid3" style="margin-top:16px">
    <div class="callout"><h3>Nothing was lost to held-out testing</h3>
      <div class="big">{ho_hb_a:.3f}</div>
      <p>Out-of-sample accuracy of <code>smaller mean block</code> on population A — <b>identical</b> to the in-sample 0.945. The reason is in the last column: <b>1.25 is refit from all {ho_n} training halves and comes back 1.25 every time</b>. With a threshold that stable there is nothing for the training step to overfit, so the honest number and the optimistic one coincide.</p></div>
    <div class="callout b"><h3>One column is most of the model</h3>
      <div class="big b">{ho_f1_a:.3f}</div>
      <p>Held-out accuracy of <code>smaller mean block</code> <i>alone</i> inside the logistic, against {ho_mall_a:.3f} for all eleven. Adding <code>knot number</code> reaches {ho_f2_a:.3f} and everything after that is noise. <b>Block thickness enters first in both populations</b> — see the ladder below.</p></div>
    <div class="callout w"><h3>The leakage control is flat</h3>
      <div class="big" style="color:var(--warn)">{ho_ctrl_a:.3f}</div>
      <p>Same pipeline, labels shuffled. It lands on the base rate ({ho_base_a:.3f}) — as does population B ({ho_ctrl_b:.3f} against {ho_base_b:.3f}). A held-out 0.98 is a bug report until this line comes back flat, so it is run every time rather than argued about.</p></div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Population A — the two tables</h2><span class="tag a">{ho_na} held out per split</span></div>
      <div class="xscroll"><table><thead><tr><th>model</th><th>test accuracy</th><th>spread over {ho_n} seeds</th><th>worst</th><th>best</th><th>cut refit on train</th></tr></thead>
      <tbody>{ho_rows_a}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Population B — provenance-matched</h2><span class="tag b">{ho_nb} held out per split</span></div>
      <div class="xscroll"><table><thead><tr><th>model</th><th>test accuracy</th><th>spread over {ho_n} seeds</th><th>worst</th><th>best</th><th>cut refit on train</th></tr></thead>
      <tbody>{ho_rows_b}</tbody></table></div></div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>The eleven columns</h2><span class="tag a">10 candidates + the yardstick</span>
    <p>All computed on the signed-block decomposition of both relators; all rotation-invariant.</p></div>
      <div class="xscroll"><table><thead><tr><th></th><th>column</th><th>what it is</th></tr></thead>
      <tbody>{ho_defs}</tbody></table></div></div>

    <div class="panel"><div class="phead"><h2>Which columns the model actually uses</h2><span class="tag a">greedy, scored out-of-sample</span>
    <p>A weight table cannot answer this — the columns are collinear, so L2 splits a shared effect and each looks modest. Adding them one at a time prices each by what it <i>contributes</i>.</p></div>
      <div class="xscroll"><table><thead><tr><th></th><th>A — the two tables</th><th>accuracy</th><th>gain</th></tr></thead>
      <tbody>{ho_fwd_a}</tbody></table></div>
      <div class="xscroll"><table><thead><tr><th></th><th>B — provenance-matched</th><th>accuracy</th><th>gain</th></tr></thead>
      <tbody>{ho_fwd_b}</tbody></table></div></div>
  </div>

  <div class="callout w" style="margin-top:20px">
    <h3>The two-column model does not transfer — and that is the finding</h3>
    <p>On population A, <code>smaller mean block</code> + <code>knot number</code> reaches <b>{ho_f2_a:.3f}</b> against {ho_mall_a:.3f} for all eleven columns. It is also <i>exactly</i> the pairing the knot hypothesis predicts — block thickness and knot count, nothing else — which is what makes it worth stating carefully rather than celebrating.</p>
    <p>On the provenance-matched population the same two columns score <b>{ho_f2_b:.3f}</b> — <b>below <code>smaller mean block</code> on its own</b> ({ho_f1s_b:.3f}). Once both sides are produced the same way, the knot count stops carrying information independent of block thickness, and a column that adds nothing still costs variance. Forward selection run on B agrees: it picks <code>mean block length</code> second, not knots.</p>
    <p>The <b>3-column model survives both</b> ({ho_m3_a:.3f} / {ho_m3_b:.3f}). A feature selection run on one population is a hypothesis about the other, never a result for it — so both small models stay in the table, because the gap between them is what carries the lesson.</p>
  </div>

  <div class="callout w" style="margin-top:20px">
    <h3>The winning seed is not a result</h3>
    <p>The best of {ho_n} seeds on population A reaches <b>{ho_best_a:.3f}</b> against a mean of {ho_mall_a:.3f} and a worst split of {ho_worst_a:.3f}. That maximum is not a better model — it is the best <i>draw</i>. With {ho_na} test points a single split&#8217;s standard error is about {ho_se:.2f}, so the maximum of {ho_n} draws sits roughly 2σ above the truth <b>by construction</b>; it is the same garden-of-forking-paths that the unsupervised sweep on this page corrects with a permutation null.</p>
    <p>A seed is a property of the <i>split</i>, not of the model. Refitting on the lucky seed buys nothing on the next 30% you have not seen. <b>The mean is the estimate and the spread is the error bar</b> — which is why the table reports the whole distribution and prints the winning seed beside it rather than instead of it.</p>
  </div>
</section>

<section id="method">
  <h2>How a presentation is represented</h2>
  <p class="lede">A relator is a <b>ring</b>, not a string. Any feature that can see where the canonicaliser happened to cut the ring is measuring the tie-break, not the mathematics — so every one of the {len(TA['faithfulness'])} representations below is rotation-invariant, and that is enforced as a hard gate, not assumed.</p>

  <div class="grid" style="margin-top:16px">
    <div class="panel"><div class="phead"><h2>The dual-ring analogue</h2><span class="tag a">headline representation</span>
    <p>Training-free counterpart of the Two-Hump paper's Dual-Ring Transformer.</p></div>
    <div class="pbody">
      <p style="margin-top:0;font-size:14px;color:var(--ink-2)">The paper's architecture rests on the observation that "relators are cyclic sequences, not linear ones", and gives its attention a <b>cyclic relative positional encoding</b>: tokens at positions <code>i, j</code> interact through the cyclic distance <code>d(i,j) = (i−j) mod L</code>. Where the network <i>learns</i> weights over that distance, we simply <b>tabulate the empirical distribution</b> over it:</p>
      <p style="font-size:14px;color:var(--ink-2)"><code>A[a,b,d] = #{{ i : w[i]=a and w[(i+d) mod L]=b }}</code></p>
      <p style="font-size:14px;color:var(--ink-2)">— "how often does letter <code>a</code> sit at cyclic distance <code>d</code> from letter <code>b</code>". Rotating the ring multiplies every letter channel's DFT by the <i>same</i> phase, so the cross-power <code>Ŝ<sub>a</sub>[k]·conj(Ŝ<sub>b</sub>[k])</code> has its phases cancel — invariant, and its inverse transform is exactly the table above.</p>
      <p style="font-size:14px;color:var(--ink-2)"><b>The constraint this imposes:</b> the cross-<i>ring</i> product <code>Ŝ¹<sub>a</sub>·conj(Ŝ²<sub>b</sub>)</code> is <b>not</b> invariant, because the two rings rotate independently and their phases do not cancel. A cross-ring feature may therefore only combine per-ring magnitudes. Lags are binned by <code>d/L</code>, so relators of different lengths stay comparable.</p>
    </div></div>

    <div class="panel"><div class="phead"><h2>Two gates, run before any clustering</h2><span class="tag a">all pass</span></div>
      <div class="xscroll" style="max-height:420px;overflow-y:auto"><table>
        <thead><tr><th>representation</th><th>distinct / 237</th><th>rotation-invariant</th></tr></thead>
        <tbody>{faith_rows(TA)}</tbody></table></div>
      <div class="pbody" style="border-top:1px solid var(--line)">
        <p style="margin:0;font-size:13px;color:var(--ink-2)"><b>Faithfulness</b> — does the representation even tell the 237 distinct orbits apart? Several standard choices do not: the Whitehead graph, the most mathematically native object here, collapses 133 of them. <b>Rotation invariance</b> — measured by re-featurising randomly rotated rings; max deviation across all representations was {max(TA['rotation_invariance'].values()):.0e}.</p></div>
    </div>
  </div>
</section>

<section id="unsup">
  <h2>What the clustering found, on its own terms</h2>
  <p class="lede">Described by intrinsic quantities only. The rightmost column is the single post-hoc line — it is <b>not</b> what the split was built from, and the algorithm never saw it.</p>
  <div class="grid" style="margin-top:16px">
    <div class="panel"><div class="phead"><h2>Population A — the two tables</h2><span class="tag a">k=2, Ward on ring autocorrelation</span></div>
      <div class="xscroll"><table><thead><tr><th>cluster</th><th>n</th><th>mean length</th><th>mean max-knots</th><th>unevenness</th><th>unsolved (post-hoc)</th></tr></thead>
      <tbody>{prof_rows(TA)}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Population B — provenance-matched</h2><span class="tag b">k=4</span></div>
      <div class="xscroll"><table><thead><tr><th>cluster</th><th>n</th><th>mean length</th><th>mean max-knots</th><th>unevenness</th><th>unsolved (post-hoc)</th></tr></thead>
      <tbody>{prof_rows(TB)}</tbody></table></div></div>
  </div>
  <div class="note" style="margin-top:16px"><b>The same axis appears in both.</b> Clusters made of longer words with more uneven block structure are the unsolved-rich ones; clusters of shorter words with even blocks are solved-rich. Nothing in the clustering was told which is which.</div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Population A · PCA of ring autocorrelation</h2></div>
      <div class="pbody">{scatter(TA,'ring_autocorr')}
      {LEG}</div></div>
    <div class="panel"><div class="phead"><h2>Population B · PCA of ring autocorrelation</h2></div>
      <div class="pbody">{scatter(TB,'ring_autocorr')}
      {LEG}</div></div>
  </div>
</section>

<section id="sweep">
  <h2>The sweep, and the null that calibrates it</h2>
  <p class="lede">{TA['n_clusterings']} clusterings were scored: {len(TA['faithfulness'])} representations × 3 preprocessings × 3 distance metrics × 8 algorithm families (k-means, Ward / average / complete / single linkage, spectral, DBSCAN at three densities) × k = 2..6. Reporting the best of that many is a garden of forking paths, so the statistic that means anything is <b>best-observed versus best-under-permuted-labels on the identical grid</b>.</p>
  <div class="grid" style="margin-top:16px">
    <div class="panel"><div class="phead"><h2>Observed vs the permutation null</h2><span class="tag a">p &lt; 0.001</span></div>
      <div class="pbody">{null_svg(TA)}
      <p style="font-size:13px;color:var(--ink-2);margin:6px 0 0">Across {TA['n_perm']} permutations the best-of-grid ARI averaged {TA['null']['mean']:.4f} and never exceeded {TA['null']['max']:.4f}. The observed {TA['best']['ari']:.4f} is not reachable by the sweep's own flexibility.</p></div></div>
    <div class="panel"><div class="phead"><h2>Top 12 of {TA['n_clusterings']}</h2><span class="tag a">population A</span></div>
      <div class="xscroll"><table><thead><tr><th>representation</th><th>preproc</th><th>metric</th><th>algorithm</th><th>k</th><th>ARI</th><th>bal. acc</th></tr></thead>
      <tbody>{top_rows(TA)}</tbody></table></div></div>
  </div>
</section>

<section id="provenance">
  <h2>The provenance control</h2>
  <div class="callout w" style="margin-top:14px">
    <h3>The confound this rules out</h3>
    <p>The two sides of population A were <b>manufactured by different processes</b>. The solved representatives are raw MS cells pushed to Aut-minimal form. The unsolved ones are raw MS cells that an upstream bounded AC reduction had <i>already rewritten</i> — <code>EQUIVALENCE_FINDING.md</code> §1 records that the 261 reps are local minima of somebody else's search, on average 2.74 letters shorter than the cells they name. A clustering could therefore separate them by detecting <b>which pipeline emitted the word</b>, and nothing about difficulty.</p>
    <p>Population B removes the difference: every state on both sides is a raw MS cell mapped through <code>aut_canon</code>, nothing else — 113 solved orbits against {TB['n_unsolved']} unsolved orbits.</p>
  </div>
  <div class="grid3" style="margin-top:18px">
    <div class="panel"><div class="phead"><h2>Population A</h2></div><div class="pbody">
      <div class="big">{TA['best']['ari']:.3f}</div><p style="margin:4px 0 0;font-size:13px">best ARI · null max {TA['null']['max']:.3f}</p></div></div>
    <div class="panel"><div class="phead"><h2>Population B</h2></div><div class="pbody">
      <div class="big">{TB['best']['ari']:.3f}</div><p style="margin:4px 0 0;font-size:13px">best ARI · null max {TB['null']['max']:.3f}</p></div></div>
    <div class="panel"><div class="phead"><h2>Conclusion</h2></div><div class="pbody">
      <div class="big" style="font-size:26px">SURVIVES</div>
      <p style="margin:4px 0 0;font-size:13px">Roughly <b>45% of the signal was provenance</b> (0.58 → 0.32), which is exactly why the control was worth running. What remains is still {TB['best']['ari']/TB['null']['max']:.1f}× the null maximum at p &lt; 0.001.</p></div></div>
  </div>
</section>

<section id="knots">
  <h2>The knot hypothesis</h2>
  <span class="tag w">hypothesis-driven — not part of the unbiased sweep</span>
  <p class="lede" style="margin-top:12px">A <b>knot</b> is a block of one generator squashed inside the other, counted around the ring. Cyclically a word alternates x-block, y-block, x-block, …, so the number of x-blocks always equals the number of y-blocks — "either of the indices" gives the same answer, and <code>knots = (number of runs) / 2</code>. The implementation reproduces both worked examples exactly:</p>
  <div class="grid3" style="margin-top:14px">
    <div class="panel"><div class="pbody"><code style="font-size:15px">yyyxxxyyyxxx</code>
      <p style="margin:8px 0 0;font-size:13px">→ <code>yyy|xxx|yyy|xxx</code> → 4 runs → <b>2 knots</b>. Few, long, even blocks.</p></div></div>
    <div class="panel"><div class="pbody"><code style="font-size:15px">yxxyxyxx</code>
      <p style="margin:8px 0 0;font-size:13px">→ <code>y|xx|y|x|y|xx</code> → 6 runs → <b>3 knots</b>. Many, short blocks.</p></div></div>
    <div class="panel"><div class="pbody"><h3 style="margin:0">Counted per relator</h3>
      <p style="margin:8px 0 0;font-size:13px">Taking the <b>max</b> over the two relators, not the sum — <code>max</code> and <code>min</code> are swap-invariant, the raw pair is not.</p></div></div>
  </div>

  <div class="panel" style="margin-top:18px"><div class="phead"><h2>Why "either index" is forced, not a convention</h2>
    <span class="tag a">proved &amp; machine-checked</span></div>
    <div class="pbody">
      <p style="margin:0"><b>Theorem.</b> If a cyclic word contains at least one x-type letter <i>and</i> at least one y-type letter, then #x-blocks = #y-blocks.</p>
      <p style="font-size:14px;color:var(--ink-2)"><b>Proof.</b> Maximal blocks partition the cycle <code>Z<sub>L</sub></code> into arcs <code>A₁…A<sub>m</sub></code> in cyclic order, and by maximality consecutive arcs carry different generators — so the labels alternate: <code>ℓⱼ = ℓ₁</code> for odd <code>j</code>, <code>ℓⱼ = ℓ₂ ≠ ℓ₁</code> for even <code>j</code>. Cyclicity requires <code>ℓ<sub>m</sub> ≠ ℓ₁</code>. Were <code>m</code> odd we would have <code>ℓ<sub>m</sub> = ℓ₁</code>, a contradiction. So <code>m</code> is even and exactly <code>m/2</code> arcs carry each generator. ∎</p>
      <p style="font-size:14px;color:var(--ink-2)">So counting on x or on y is not a choice — it is <b>forced</b> to agree, and <code>knots = max(#x-blocks, #y-blocks)</code> simply returns that common value. The definition needs no case split.</p>
      <p style="font-size:14px;color:var(--ink-2)"><b>The one exception is a pure power.</b> A word on a single generator (<code>X</code>, <code>yyy</code>) falls outside the hypothesis: it has one block of its own generator and none of the other, so the counts genuinely differ, 1 vs 0. This is not hypothetical — <code>sol_001</code> ships with <code>r₁ = X</code>. The <code>max</code> rule resolves it to 1.</p>
      <p style="font-size:14px;color:var(--ink-2)"><b>Machine-checked</b> (<code>tests/clustering/test_knots.py</code>, 8 passing): the balance holds for every cyclically reduced two-generator word up to length 9 — over 20,000 of them — and for every relator shipped in both tables; pure powers are confirmed as the <i>only</i> exception; and the count is invariant under rotation, relator inversion and the x↔y swap. Switching from the old "0 for a pure power" convention to <code>max</code> left every headline number unchanged.</p>
    </div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Max knots on one relator</h2><span class="tag b">population A</span>
      <p>Solved never exceeds 3. Unsolved reaches 5.</p></div>
      <div class="pbody">{knot_hist_svg(TA)}
      {LEG}</div></div>
    <div class="panel"><div class="phead"><h2>The threshold rule, swept</h2><span class="tag b">"some relator has &gt; t knots" ⇒ unsolved</span></div>
      <div class="xscroll"><table><thead><tr><th>rule</th><th>bal. acc</th><th>precision</th><th>recall</th><th>tp/fp/fn/tn</th></tr></thead>
      <tbody>{rule_rows(TA)}</tbody></table></div>
      <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)"><b>The threshold is &gt; 2, not &gt; 3.</b> At <code>&gt; 2</code> the rule reaches {TA['knots']['rule'][1]['bal_acc']:.3f} balanced accuracy. At <code>&gt; 3</code> it is <b>perfectly precise</b> — 14 hits, zero false positives, so ≥4 knots on a relator is a <i>sufficient</i> condition for unsolved in this data — but it catches only {TA['knots']['rule'][2]['recall']*100:.0f}% of them.</p></div></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead">
    <h2>max_knots = max(knots in r₁, knots in r₂) — the breakdown</h2><span class="tag b">the clearest single statistic</span>
    <p>Every state grouped by its max_knots value. The last two columns drill inside each group: what still differs between the solved and unsolved states that <i>share</i> a max_knots.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>max_knots</th><th>solved</th><th>unsolved</th><th>proportion (solved ▏unsolved)</th><th>% unsolved</th><th>unevenness s/u</th><th>length s/u</th></tr></thead>
      <tbody>{maxknot_rows(TA)}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)">
      <p style="margin:0 0 8px"><b>It is monotone, and it has a hard ceiling.</b> The share of unsolved climbs 18.5% → 87.9% → 100% → 100% as max_knots goes 2 → 5. <b>No solved presentation anywhere in the 113 has max_knots ≥ 4</b>, so all 14 states at 4 or 5 are unsolved. That is the perfect-precision regime — sufficient, but it only covers 11%.</p>
      <p style="margin:0 0 8px"><b>The bulk sits at 2 and 3, and there the split is nearly clean too</b>: max_knots = 2 is 82% solved, max_knots = 3 is 88% unsolved. A single integer read off the presentation gets {TA['knots']['rule'][1]['bal_acc']*100:.1f}% balanced accuracy.</p>
      <p style="margin:0"><b>Inside a group, unevenness takes over.</b> Among the 99 states with max_knots = 3, the solved ones average {TAB(TA,3)['unev_solved']:.2f} block unevenness against {TAB(TA,3)['unev_unsolved']:.2f} for the unsolved — and they are markedly shorter ({TAB(TA,3)['len_solved']:.1f} vs {TAB(TA,3)['len_unsolved']:.1f}). A solved presentation with three knots is <i>short and even</i>; an unsolved one with three knots is <i>long and lopsided</i>. The two statistics are complementary, not redundant.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>The same breakdown, provenance-matched</h2><span class="tag a">control</span>
    <p>Both sides produced identically. max_knots never reaches 4 here, which is itself informative: the ≥4 states in population A were <b>created by the upstream AC reduction</b>, not present in the raw Aut-minimal cells.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>max_knots</th><th>solved</th><th>unsolved</th><th>proportion (solved ▏unsolved)</th><th>% unsolved</th><th>unevenness s/u</th><th>length s/u</th></tr></thead>
      <tbody>{maxknot_rows(TB)}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">The gradient survives — max_knots = 3 is still {TAB(TB,3)['pct_unsolved']*100:.1f}% unsolved — but max_knots = 2 is now a coin flip ({TAB(TB,2)['pct_unsolved']*100:.1f}%), so the statistic separates the <i>upper</i> tail rather than the bulk. The within-group unevenness gap holds at {TAB(TB,3)['unev_solved']:.2f} vs {TAB(TB,3)['unev_unsolved']:.2f}.</p></div>
  </div>


  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Does knots = 0 occur? Yes — and only for a pure power</h2>
    <span class="tag a">correction</span>
    <p>Buckets are enumerated from 0, never only over observed values, so an empty bucket is visibly empty rather than silently absent.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>knots</th><th>relators</th><th>in solved</th><th>in unsolved</th><th></th></tr></thead>
      <tbody>{perrel_rows(TA)}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)">
      <p style="margin:0 0 8px"><b>7 of the 474 relators have 0 knots</b>, and every one of them is the bare relator <code>x&#772;</code>, in <code>sol_001</code>…<code>sol_007</code>. A pure power has one block of its own generator and none of the other, so nothing is squashed inside anything — the literal reading of the definition gives 0. A <code>max(#x,#y)</code> tie-break would have said 1, but that rule exists to reconcile the two counts when they disagree, and here there is no tie to break.</p>
      <p style="margin:0 0 8px">0 is also the <i>informative</i> value: a pure-power relator kills a generator outright — <code>sol_001</code> is ⟨x, y | x, y&#772;y&#772;x&#772;yx⟩, i.e. x = 1 — so a 0 flags a degenerate, trivially-collapsing presentation.</p>
      <p style="margin:0"><b>The choice moves nothing measurable.</b> No presentation's max_knots changes at all; only min_knots shifts from 1 to 0, for exactly those 7. Pinned by <code>test_pure_power_convention_does_not_move_max_knots</code>.</p></div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>min_knots — both relators at least this busy</h2></div>
      <div class="xscroll"><table><thead><tr><th>min_knots</th><th>solved</th><th>unsolved</th><th>% unsolved</th></tr></thead>
      <tbody>{minknot_rows(TA)}</tbody></table></div>
      <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">min_knots = 0 is a <b>pure solved</b> bucket, 7 for 7 — which is what you would expect, since those are the presentations that kill a generator. min_knots = 3 is pure the other way, 14 for 14. (The 1 bucket holds only 2 states; read nothing into it.)</p></div></div>
    <div class="panel"><div class="phead"><h2>Two sufficient conditions for unsolved</h2><span class="tag b">precision 1.000</span></div>
      <div class="xscroll"><table><thead><tr><th>rule</th><th>solved</th><th>unsolved</th><th>precision</th><th>recall</th></tr></thead>
      <tbody>{rules2_rows(TA)}</tbody></table></div>
      <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">Solved states occupy a tight box — <b>max_knots ≤ 3 and min_knots ≤ 2</b>. The two rules overlap on only 4 states, so together they certify <b>24 of the 124 unsolved with zero false positives</b>, nearly double either alone.</p></div></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Every block statistic, both populations</h2>
    <p>AUC 0.5 = no signal. "matched" = recomputed inside the overlapping length band {TA['matched_band'][0]}–{TA['matched_band'][1]}, which is the test of whether a statistic is length in disguise.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>statistic</th><th>solved</th><th>unsolved</th><th>AUC</th><th>AUC matched</th><th>Cohen's d</th></tr></thead>
      <tbody>{knot_rows(TA)}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)">
      <p style="margin:0 0 8px"><b>Where the hypothesis lands.</b> The direction is confirmed on the raw count — unsolved really do carry more knots (AUC {TA['knots']['features'][0]['auc']:.3f}). But that count is substantially <b>length</b>: unsolved words are longer, so they have more blocks, and the effect weakens from {TA['knots']['features'][2]['auc']:.3f} to {TB['knots']['features'][2]['auc']:.3f} once provenance is matched.</p>
      <p style="margin:0 0 8px"><b>Per unit length the sign flips.</b> Knot <i>density</i> gives AUC {TB['knots']['features'][6]['auc']:.3f} in the clean population — unsolved presentations have <b>fewer</b> knots per letter, and <b>longer</b> blocks (mean {TB['knots']['features'][3]['unsolved_mean']:.2f} vs {TB['knots']['features'][3]['solved_mean']:.2f}). That is the <code>yyyxxxyyyxxx</code> picture: few, long blocks.</p>
      <p style="margin:0"><b>The robust signal is unevenness, not count.</b> <code>max ÷ mean block</code> is scale-free by construction and scores AUC {TA['knots']['features'][8]['auc']:.3f} / {TB['knots']['features'][8]['auc']:.3f} across the two populations, holding at {TA['knots']['features'][8]['auc_matched']:.3f} / {TB['knots']['features'][8]['auc_matched']:.3f} inside the matched band. Unlike knot count it gets <i>stronger</i> under the provenance control. Unsolved presentations are not more finely knotted — they carry <b>one dominant long block among shorter ones</b>.</p></div>
  </div>
</section>


<section id="within">
  <h2>Inside a bucket: exponent signs and block sizes</h2>
  <span class="tag w">hypothesis-driven</span>
  <p class="lede" style="margin-top:12px">max_knots leaves two mixed buckets — 101 solved / 23 unsolved at max_knots = 2, and 12 / 87 at max_knots = 3. What separates states that share a max_knots? The two things the knot count throws away: the <b>exponent sign</b> (it lowercases, so x and x&#772; count alike) and the <b>block sizes</b> between knots.</p>

  <div class="callout w" style="margin-top:16px">
    <h3>The exponent ±1 carries nothing — and it cannot</h3>
    <p>All three "does the sign alternate inside a block" features measured <b>exactly 0.00</b> on all 237 presentations. That is not a quirk of this dataset, it is a theorem:</p>
    <p><b>In a freely reduced word, every maximal same-generator block is a pure power.</b> Two adjacent letters inside a block share a generator; if their signs differed the word would contain <code>xx&#772;</code> or <code>x&#772;x</code> and would not be reduced. So a block is always <code>x<sup>k</sup></code> or <code>x&#772;<sup>k</sup></code>, never mixed — there is no within-block exponent freedom to exploit. Verified over 50,000+ blocks in <code>tests/clustering/test_signed_knots.py</code>.</p>
    <p>The visible fingerprint: <b>mean |exponent| and mean block length have identical AUCs in both buckets</b> (0.769 / 0.769 and 0.989 / 0.989), because |exponent| = block length for every block. The only sign freedom left is one sign per block, and that tests at chance — AUC 0.515 and 0.522.</p>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>max_knots = 2 &nbsp;·&nbsp; 101 solved / 23 unsolved</h2>
    <span class="tag b">one feature separates almost perfectly</span>
    <p>Length alone scores AUC {WB["2"]["auc_length_alone"]:.3f} here, so every block feature is also scored with total length regressed out. Only one survives that.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>feature</th><th>solved</th><th>unsolved</th><th>AUC</th><th>AUC, length removed</th><th>verdict</th></tr></thead>
      <tbody>{wb_rows("2")}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)">
      <p style="margin:0 0 8px"><b>smaller mean block</b> — the mean run length of whichever generator runs <i>thinner</i> — reaches AUC <b>0.989</b>, and <b>0.981 with length removed</b>. It is the only feature in this bucket that beats length; every other block statistic collapses once length is taken out (max block length 0.743 → 0.500, unevenness 0.689 → 0.432). So the earlier "unevenness" story is a between-bucket effect, not a within-bucket one.</p>
      <p style="margin:0 0 8px"><b>The distributions barely touch.</b> Solved span 1.00–1.75 (median 1.25); unsolved span 1.50–1.75 (median 1.75). The rule <code>smaller mean block &gt; 1.25</code> flags <b>all 23 unsolved and only 6 of the 101 solved</b> — recall 1.000, balanced accuracy 0.970.</p>
      <p style="margin:0"><b>Read plainly:</b> in a solvable presentation the thin generator appears as <i>isolated single letters</i>; in an unsolvable one it starts clumping into runs of two or more. Best of |AUC−0.5| across all 14 features is 0.489 against a null 95th percentile of 0.161 and null max 0.298 over {WB["2"]["n_perm"]} permutations — p &lt; 0.001, so this is not the small bucket talking.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>max_knots = 3 &nbsp;·&nbsp; 12 solved / 87 unsolved</h2>
    <span class="tag w">length dominates here</span>
    <p>Total length alone reaches AUC {WB["3"]["auc_length_alone"]:.3f} in this bucket — the 12 solved states average {WB["3"]["len_solved"]:.1f} letters against {WB["3"]["len_unsolved"]:.1f}. Little room is left for anything else to prove itself.</p></div>
    <div class="xscroll"><table>
      <thead><tr><th>feature</th><th>solved</th><th>unsolved</th><th>AUC</th><th>AUC, length removed</th><th>verdict</th></tr></thead>
      <tbody>{wb_rows("3")}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">Mean block length still holds 0.885 after length is removed, but with only 12 solved states and length nearly separating on its own, treat this bucket as corroboration rather than independent evidence.</p></div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Block signatures · max_knots = 2</h2>
      <p>Literally "how many x&#8217;s and y&#8217;s sit between each knot", necklace-canonical so rotation cannot change it. Read <code>x1y7x1y8</code> as: x-block of 1, y-block of 7, x-block of 1, y-block of 8.</p></div>
      <div class="xscroll"><table><thead><tr><th>class</th><th>signature</th><th>count</th></tr></thead><tbody>{sig_rows("2")}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Block signatures · max_knots = 3</h2>
      <p>The same contrast, one knot up.</p></div>
      <div class="xscroll"><table><thead><tr><th>class</th><th>signature</th><th>count</th></tr></thead><tbody>{sig_rows("3")}</tbody></table></div></div>
  </div>
  <div class="note" style="margin-top:16px"><b>The signatures make it concrete.</b> Solved presentations are built from small numbers throughout — <code>x1y2x3y1</code>, <code>x1y1x1y2x1y2</code>. Unsolved ones carry a long single-generator run: <code>x1y7x1y8</code>, <code>x1y4x1y5</code>. Same knot count, very different interiors.</div>
</section>

<section id="diag">
  <h2>Diagnostics</h2>
  <p class="lede">Not results — instruments. A cross-validated classifier is <i>shown</i> the labels, so it is an <b>upper bound</b> on what any unsupervised method could recover. Its job here is to tell us whether the unsupervised numbers are plausible, and how much of the separability is size.</p>
  <div class="panel" style="margin-top:16px"><div class="phead"><h2>Supervised ceiling · balanced accuracy, 5-fold CV</h2><span class="tag w">diagnostic only</span>
    <p>0.5 is chance. The final column regresses total length out of every feature first.</p></div>
    <div class="xscroll" style="max-height:440px;overflow-y:auto"><table>
      <thead><tr><th>representation</th><th>kNN-5</th><th>kNN-15</th><th>logistic</th><th>logistic, length removed</th></tr></thead>
      <tbody>{ceiling_rows(TA)}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">Lengths alone reach {TA['ceiling'][0]['logreg']:.3f}, so size is genuinely informative — but the ring representations reach {max(c['logreg'] for c in TA['ceiling']):.3f}, and still {max(c['logreg_nolen'] for c in TA['ceiling']):.3f} after length is removed. Separability is therefore not reducible to length in population A.</p></div>
  </div>
</section>

<section id="caveats">
  <h2>What this does and does not show</h2>
  <div class="grid" style="margin-top:14px">
    <div class="callout"><h3>It does show</h3>
      <p>• Unsupervised clustering of minimal automorphic states recovers the solved / unsolved split far beyond what {TA['n_perm']} label permutations can produce from the same grid.<br>
      • The effect survives a provenance control that removes the manufacturing difference between the two sides.<br>
      • A single scale-free statistic — block unevenness — carries most of it, consistently across both populations and inside the matched length band.</p></div>
    <div class="callout w"><h3>It does not show</h3>
      <p>• <b>Not causation, and not a solvability test.</b> "Unsolved" means <i>not yet trivialised at the budgets tried</i>, so any structure found may describe what current search finds hard rather than what is AC-nontrivial.<br>
      • <b>Length is not fully removed.</b> Residualising on <i>total</i> length leaves the |r₁| vs |r₂| asymmetry; in population B no representation beat the shape control once total length was regressed out.<br>
      • <b>The two tables are quotients of different relations</b> — Aut(F₂) for the solved side, the coarser ACA for the unsolved — so population A mixes two granularities. Population B is the cleaner object.<br>
      • The knot section is <b>hypothesis-driven</b>: those features were chosen because of a conjecture about the label, so their AUCs are not protected by the permutation null that covers the sweep.</p></div>
  </div>
</section>

<section id="hyper">
  <h2>The hyperparameter search</h2>
  <p class="lede">A knot-based heap priority for the greedy substitution search — climb on structure while the presentation is long, with a length-16 phase boundary added only where the climb is lean enough to need one — tuned against the full 66-item benchmark and checked on an aut-disjoint held-out split it never trained on.</p>

  <div class="callout b" style="margin-top:16px"><h3>Held out, this time for real</h3>
    <div class="big b" style="font-size:52px">{hy_head['baseline']}<span style="font-size:22px"> of </span>{hy_head['n']}<span style="font-size:28px"> &#8594; </span>{hy_head['tuned']}<span style="font-size:22px"> of </span>{hy_head['n']}</div>
    <p>{hy_head_note}</p>
    <p style="margin-bottom:0">Every other denominator below — 24 rows, 19 distinct problems, the 45-row complementarity matrix further down — comes from a different experiment on a different slice. This is the framing that is genuinely leak-free (75 presentations no stage of this program ever read) and counted in problems rather than twin-inflated rows; treat it as the headline and the rest as detail.</p>
  </div>

  <div class="callout w" style="margin-top:20px"><h3>Correction <span class="pill pa">a retracted figure</span></h3>
    <p style="margin-top:0">{hy_corr_note}</p>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Can it be beaten?</h2>
    <span class="tag a">{hy_retune['configs']} fresh configs, refit from scratch</span></div>
    <div class="xscroll"><table><thead><tr><th></th><th>train ({hy_retune['tune_n']})</th>
    <th>eval ({hy_retune['eval_n']}, frozen before fitting)</th></tr></thead>
    <tbody>
      <tr><td>re-tuned challenger</td><td class="num">{hy_retune['winner_tune']}/{hy_retune['tune_n']}</td>
      <td class="num"><b>{hy_retune['winner_eval']}/{hy_retune['eval_n']}</b></td></tr>
      <tr class="win"><td>incumbent (this page's recommendation)</td>
      <td class="num"><b>{hy_retune['incumbent_tune']}/{hy_retune['tune_n']}</b></td>
      <td class="num"><b>{hy_retune['incumbent_eval']}/{hy_retune['eval_n']}</b></td></tr>
      <tr class="empty"><td>length baseline</td><td class="num">&#8212;</td>
      <td class="num">{hy_retune['baseline_eval']}/{hy_retune['eval_n']}</td></tr>
    </tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">{hy_retune['note']}</p></div>
  </div>

  <div class="grid3" style="margin-top:20px">
    <div class="callout"><h3>Budget 500 &middot; bins 4&#8211;7, the decidable band</h3>
      <div class="big">{hpair(hy_b47_500['baseline'])}<span style="font-size:20px"> &#8594; </span>{hpair(hy_b47_500['winner'])}</div>
      <p>Neither free (bins 0&#8211;3, already 24/24) nor unreachable (bins 8&#8211;9 + reach, 0 under every ordering) — the honest denominator. Full benchmark: {hpair(hy_full_500_base)} &#8594; {hpair(hy_full_500_win)}.</p></div>
    <div class="callout b"><h3>Budget 1000 &middot; bins 4&#8211;7, the decidable band</h3>
      <div class="big b">{hpair(hy_b47_1000['baseline'])}<span style="font-size:20px"> &#8594; </span>{hpair(hy_b47_1000['winner'])}</div>
      <p>Near-{hy_b47_1000['winner'][0]/hy_b47_1000['baseline'][0]:.0f}&times;. Full benchmark: {hpair(hy_full_1000_base)} &#8594; {hpair(hy_full_1000_win)}.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>The recommendation, by node budget</h2>
    <span class="tag a">500 needs the phase boundary &middot; 1000 does not</span></div>
    <div class="xscroll"><table><thead><tr><th>budget</th><th>ordering</th><th>full-bench (66)</th>
    <th>held out, 75 rows outside the benchmark</th></tr></thead>
    <tbody>{hyper_reco_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)">
      <p style="margin:0 0 8px;font-size:13px;color:var(--ink-2)">Budget 500 keeps the length-16 phase boundary — climb on structure while long, revert to pure length once short — because its climb is lean (knots and xy-imbalance only) and would wander without it near the trivial state. Budget 1000's richer climb already carries max-knots and smaller-block, both of which fall on their own as a pair approaches trivial, so it self-regulates: a <b>single weight vector</b>, applied at every length, with no phase boundary at all. See below.</p>
      <p style="margin:0;font-size:13px;color:var(--ink-2)"><b>It also wins on path length, not just solve count.</b> On the {hy_path['n']} rows both arms solve at budget 1000, the winner's mean path is <b>{hy_path['winner']:.1f}</b> moves against {hy_path['baseline']:.1f} for the baseline — fewer moves, not just more solves.</p>
    </div>
  </div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Budget 500 &middot; full 66</h2><span class="tag a">baseline + 4 orderings</span></div>
      <div class="xscroll"><table><thead><tr><th>ordering</th><th>total</th><th>bins 0&#8211;3</th><th>bin 4</th>
      <th>bin 5</th><th>bin 6</th><th>bin 7</th><th>bins 8&#8211;9</th><th>reach</th></tr></thead>
      <tbody>{hyper_fullbench_rows("500")}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Budget 1000 &middot; full 66</h2><span class="tag b">baseline + 4 orderings</span></div>
      <div class="xscroll"><table><thead><tr><th>ordering</th><th>total</th><th>bins 0&#8211;3</th><th>bin 4</th>
      <th>bin 5</th><th>bin 6</th><th>bin 7</th><th>bins 8&#8211;9</th><th>reach</th></tr></thead>
      <tbody>{hyper_fullbench_rows("1000")}</tbody></table></div></div>
  </div>
  <div class="note" style="margin-top:16px"><b>The gains land in bins 4&#8211;7.</b> Bins 0&#8211;3 (easy) are already saturated at 24/24 by the length baseline, and bins 8&#8211;9 plus the 6 reach rows stay at 0/12 and 0/6 under every ordering tried, at both budgets.</div>
  <div class="note" style="margin-top:10px"><b>That negative is not one family's blind spot.</b> {hy_hump2_note}</div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>It reorders difficulty</h2>
    <span class="tag a">largest single-presentation speedups measured</span></div>
    <div class="pbody" style="padding-bottom:4px"><div class="big">250&times;</div>
    <p style="margin:6px 0 0;font-size:14px;color:var(--ink-2)">The largest measured reduction in nodes-to-solve from switching only the heap priority — nothing else about the search changed.</p></div>
    <div class="xscroll"><table><thead><tr><th>presentation</th><th>baseline needs</th><th>knot ordering</th>
    <th>reduction</th></tr></thead>
    <tbody>{hyper_speedup_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">The three problems that resist cost the baseline only 13k&#8211;16k nodes — <i>less</i> than the two beaten 250&times; — so difficulty under length ordering does not predict difficulty under the knot ordering.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Counted as problems, not rows</h2>
    <span class="tag a">19 distinct automorphism classes, not 24 rows</span>
    <p>{e(HY['wave2']['distinct_problems']['note'])}.</p></div>
    <div class="xscroll"><table><thead><tr><th>budget</th><th>distinct problems solved (baseline &#8594; knot ordering)</th></tr></thead>
    <tbody>{hyper_distinct_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">Only <b>{HY['wave2']['distinct_problems']['resisting']}</b> problems resist at budget 1000. This follows the same discipline the equivalence-class work already established — quotient by every symmetry that preserves the question before counting.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>The knot intuition, tested directly</h2>
    <span class="tag b">a threshold, not a dial</span></div>
    <div class="xscroll"><table><thead><tr><th>stratum</th><th>n</th><th>k=0.5</th><th>k=1</th><th>k=2</th>
    <th>k=3</th><th>k=4</th><th>k=8</th><th>k=16</th></tr></thead>
    <tbody>{hyper_threshold_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">{e(HY['wave2']['knot_threshold']['verdict'].replace(" - ", " — "))}</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>What did not work</h2>
    <span class="tag w">measured negatives — kept the recommendation simple</span></div>
    <div class="pbody"><p style="margin:0">
      {hyper_negatives_list()}
    </p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Which ordering to run at Colab scale</h2>
    <span class="tag a">the most decision-relevant result on this page</span></div>
    <div class="xscroll"><table><thead><tr><th>ordering</th><th>gap @500</th><th>gap @1000</th>
    <th>tail</th></tr></thead>
    <tbody>{hyper_scaling_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">{hy_scaling_note}</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>The endgame phase is only needed by lean orderings</h2>
    <span class="tag a">what the phase boundary is worth, by climb</span></div>
    <div class="xscroll"><table><thead><tr><th>climb</th><th>terms</th><th>worth (500 / 1000)</th></tr></thead>
    <tbody>{hyper_phase_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">{hy_threshold_note}</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Depth beats breadth at a fixed budget</h2>
    <span class="tag w">a negative result — ruled out, not adopted</span></div>
    <div class="xscroll"><table><thead><tr><th>k</th><th>nodes each</th><th>richer</th><th>K8</th>
    <th>baseline</th></tr></thead>
    <tbody>{hyper_portfolio_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)">{hy_portfolio_note}</p></div>
  </div>

  <div class="callout" style="margin-top:20px"><h3>No single ordering is enough
    <span class="pill pa">19&#8594;23 is optimistic</span></h3>
    <div class="big">{hy_union['union']}<span style="font-size:20px"> of </span>{hy_union['n']}</div>
    <p>Best single ordering solves {hy_union['best_single']} of {hy_union['n']}; the union across every ordering tried in this program reaches {hy_union['union']}. Only <code>{e(hy_union['frontier'])}</code> (aut class 97) has resisted every configuration, across 607 recorded attempts. The same story the 250&times; speedup result already told: the heuristic <b>reorders</b> difficulty rather than uniformly improving it.</p>
    <p><b>But this 19&#8594;23 gap was selected on the rows it was scored on.</b> Cross-validated out of sample:</p>
    <div class="xscroll"><table><thead><tr><th>strategy</th><th>expected gain, out of sample</th></tr></thead>
    <tbody>
      <tr class="win"><td>pick a second ordering <i>for complementarity</i></td><td class="num"><b>+{hy_cv['complement']:.2f}</b></td></tr>
      <tr><td>pick the single strongest arm</td><td class="num">+{hy_cv['strength']:.2f}</td></tr>
      <tr class="empty"><td>pick a second ordering at random</td><td class="num">+{hy_cv['random']:.2f}</td></tr>
    </tbody></table></div>
    <p style="margin-top:10px;font-size:13px;color:var(--ink-2)">{hy_cv_note}</p>
    <p style="margin-bottom:0">Read 19&#8594;23 as the <b>demonstration</b>, not the estimate.</p>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Which feature carries the signal</h2>
    <span class="tag a">single-feature screen, train-500</span>
    <p>Best weight found per feature by a 1-D sweep against the length baseline; net = solved &minus; baseline.</p></div>
    <div class="xscroll"><table><thead><tr><th>feature</th><th>best weight</th><th>solved/40</th><th>net</th>
    <th>p</th></tr></thead>
    <tbody>{hyper_feature_rows()}</tbody></table></div>
    <div class="pbody" style="border-top:1px solid var(--line)"><p style="margin:0;font-size:13px;color:var(--ink-2)"><b>Knots win.</b> <code>nb</code> ties <code>K</code> exactly ({HY['feature_screen'][1]['solved']}/40, net {HY['feature_screen'][1]['net']:+d}, p={HY['feature_screen'][1]['p']:.3f}) because <code>nb = 2&middot;knots</code> by the balance theorem proved above — it is a consistency check on the same signal, not a second independent feature.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>A negative result, stated honestly</h2>
    <span class="tag b">knot progress &ne; a ranking signal</span></div>
    <div class="pbody">
      <p style="margin-top:0">Does reaching fewer knots by node 500 predict a solve, on the rows still open? Over {HY['knot_proxy']['n_windows']} windows: P(solve | dropped a knot by node 500) is <b>lower</b>, not higher, than P(solve | no drop).</p>
      <div class="big b">{HY['knot_proxy']['p_solve_given_drop']:.3f}<span style="font-size:20px"> vs </span>{HY['knot_proxy']['p_solve_given_no_drop']:.3f}</div>
      <p>So the knot <i>ordering</i> helps the search reach more presentations, but knot count <i>reached</i> is not itself a ranking signal for the unsolved rows still open at 500 — do not rank the second hump on it; use total length and real solves instead.</p>
    </div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>Caveats</h2></div>
    <div class="pbody"><p style="margin:0">
      &bull; The aut-disjoint split measures decidable&#8594;decidable transfer, not the decidable&#8594;second-hump gap — that gap is unmeasurable at &#8804;1,000 nodes.<br>
      &bull; The 75-row replication set and the retune's {hy_retune['eval_n']}-row frozen split are still modest samples, so each recommended <i>structure</i> (the 500 phase boundary, the 1000 single vector) is robust in aggregate, but the exact weights sit within selection noise.<br>
      &bull; {hy_u124_note}<br>
      &bull; {e(HY['leak_note'])}<br>
      &bull; {hy_tie}<br>
      &bull; <b>Scope:</b> {e(HY['harness_note'])}
    </p></div>
  </div>
</section>

<section id="search">
  <h2>From a classifier to a search heuristic</h2>
  <p class="lede">Everything above scores a presentation's <i>starting</i> shape. This part asks a different question: can the same block statistics <b>guide the search</b>? The baseline greedy orders its open set by total length alone — it always expands the shortest presentation it has seen. Replacing that one expression, and nothing else, is the whole experiment.</p>

  <div class="grid3" style="margin-top:16px">
    <div class="callout"><h3>Only the priority changes</h3>
      <div class="big">1</div>
      <p><code>HeuristicSolver</code> subclasses the baseline solver, so the move generator, free reduction, Booth canonicalisation, per-relator cap, visited set and the <code>(priority, depth, key)</code> tie-break are all inherited. <b>One expression differs.</b> Any gap between two arms is the ordering and nothing else.</p></div>
    <div class="callout b"><h3>The control is the baseline, pop for pop</h3>
      <div class="big b">=</div>
      <p>The <code>length</code> arm is asserted to reproduce <code>greedy_search</code> with the <i>same solved flag and the same nodes_explored</i> on every presentation, at every budget — before any comparison is read. Scoring the same is not being the same; a subclass that quietly changed the cap could still tie.</p></div>
    <div class="callout w"><h3>Budget is capped at 1,000</h3>
      <div class="big" style="color:var(--warn)">≤1k</div>
      <p>A search at budget <i>B</i> is exactly the first <i>B</i> pops of any longer search, so a bigger budget buys a slower repro, never different behaviour. Production budgets belong on Colab. Every number here is at 100–1,000 pops per presentation.</p></div>
  </div>

  <div class="callout" style="margin-top:20px">
    <h3>The benchmark, and what &#8220;held out&#8221; means here</h3>
    <p>The frozen subsets in <code>results/benchmark/subsets/</code> — 10 log-width difficulty bins, minimally automorphic, so the set is not 20 copies of the same easy problem. Tuning happens on <b>subset-20</b>. Two validation sets, because the first was compromised:</p>
    <p><b>exploratory (22)</b> — the members of subset-40 not in subset-20. These were inspected under a <i>buggy</i> tie-break (below), so they can no longer serve as a clean confirmation and are labelled accordingly rather than quietly reused. <b>confirm (34)</b> — the members of subset-60 in neither set above. Untouched.</p>
    <p style="margin-bottom:0"><b>The bug worth recording.</b> The first ranking compared arms by the raw <i>sum</i> of nodes over each arm's own both-solved set. Those sets differ in size, so 537 nodes over 8 presentations &#8220;beat&#8221; 582 over 9 — when the per-presentation means are 67.1 against 64.7, the opposite order. It pre-registered the wrong winner, and was caught only because the held-out numbers looked odd. Ranking now uses the mean.</p>
  </div>
</section>

<section id="arms">
  <h2>The 25 orderings</h2>
  <p class="lede">Three families, plus your endgame-switch idea at eight thresholds. <code>knots_first</code> is lexicographic — expand <i>any</i> state that reduced the knot count before any state that merely got shorter, because a knot reduction is rare. <code>@endgame&lt;T&gt;</code> reverts to pure length once the presentation is shorter than T, on the reasoning that near the trivial state the remaining work is cancellation, not restructuring.</p>

  <div class="panel" style="margin-top:16px"><div class="phead"><h2>Tuning set — benchmark subset 20</h2><span class="tag a">solve count at each budget</span></div>
    <div class="xscroll"><table><thead><tr><th>priority</th><th>@100</th><th>@200</th><th>@500</th><th>@500 paired</th></tr></thead>
    <tbody>{hs_arms_tune}</tbody></table></div></div>

  <div class="grid" style="margin-top:20px">
    <div class="panel"><div class="phead"><h2>Exploratory (already seen) — 22</h2><span class="tag w">not a clean check</span></div>
      <div class="xscroll"><table><thead><tr><th>priority</th><th>@100</th><th>@200</th><th>@500</th><th>paired</th></tr></thead>
      <tbody>{hs_arms_expl}</tbody></table></div></div>
    <div class="panel"><div class="phead"><h2>Confirmation — 34 untouched</h2><span class="tag b">never used for anything else</span></div>
      <div class="xscroll"><table><thead><tr><th>priority</th><th>@100</th><th>@200</th><th>@500</th><th>paired</th></tr></thead>
      <tbody>{hs_arms_conf}</tbody></table></div></div>
  </div>

  <div class="callout" style="margin-top:20px">
    <h3>At the 1,000-node ceiling — does the baseline catch up?</h3>
    <p>This is the point of running 1,000 at all. A search at budget <i>B</i> is the first <i>B</i> pops of any longer one, so an ordering that wins merely by <i>arriving sooner</i> will see the baseline close the gap as budget grows. One that wins by reaching states the length ordering never ranks highly will not. <b>The two look identical at 500 and have opposite consequences at 50k.</b></p>
    <div class="xscroll"><table><thead><tr><th>priority</th><th>@500</th><th>@1000</th><th>paired</th><th>nodes/search @1000</th></tr></thead>
    <tbody>{hs_t2}</tbody></table></div>
    <p style="margin-bottom:0">The knot arms <b>widen</b> (+2&#8594;+3, +2&#8594;+4). <code>length+4.0*smb</code> <b>flatlines</b> (+1&#8594;+0) — it only ever won by arriving sooner. Pooling the paired outcomes over the two validation sets only (56 presentations, tuning set excluded): <code>knots_first@endgame16</code> is <b>10W&#8211;2L, exact sign test p = 0.039</b>. Three arms were carried into validation, so Bonferroni puts that at p &#8776; 0.12.</p>
  </div>
</section>

<section id="tuned">
  <h2>Tuning all the weights at once</h2>
  <p class="lede">Rather than fixing one weight by hand, search them. The space below <b>subsumes</b> every arm above — large <code>a₁</code> is lexicographic knots-first, <code>a₁ = 4</code> with the rest zero is <code>length+4·knots</code>, and the all-zero vector with <code>T = 0</code> is exactly the baseline.</p>

  <div class="callout" style="margin-top:16px">
    <div class="xscroll"><p class="mono" style="font-size:14px;margin:0">priority(r₁, r₂) = (0, L)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; if L ≤ T<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(1, L + a₁·knots + a₂·max_knots + a₃·smb)&nbsp;&nbsp; otherwise</p></div>
    <p style="margin-bottom:0"><b>The zero vector stays in the candidate pool on purpose.</b> A search space that cannot express &#8220;no change&#8221; will always appear to beat the control — so the tuner is always free to return the baseline, and that it does not is the result. Asserted as a test.</p>
  </div>

  <div class="grid3" style="margin-top:20px">
    <div class="callout"><h3>Zero overfitting gap</h3>
      <div class="big">{tm_test:+.1f}</div>
      <p>Mean gain on the <b>held-out</b> half, against {tm_train:+.1f} on train — the tuner bought nothing it could not keep. Five splits stratified by difficulty bin; 200 random configs tuned per split, the winner scored once on the half it never saw.</p></div>
    <div class="callout b"><h3>Every split, no exceptions</h3>
      <div class="big b">5/5</div>
      <p>Splits where the tuned ordering beat the baseline on held-out data (sign p = 0.062). Per split it scores 15&#8211;16 of 30 against a baseline of 8&#8211;9.</p></div>
    <div class="callout w"><h3>Worth more than 10&times; the budget</h3>
      <div class="big" style="color:var(--ok)">30 &gt; 29</div>
      <p>The tuned ordering at <b>budget 100</b> (30/60) beats the baseline at <b>budget 1,000</b> (29/60). On this benchmark the priority is worth more than a tenfold node budget.</p></div>
  </div>

  <div class="panel" style="margin-top:20px"><div class="phead"><h2>The five splits</h2><span class="tag a">subset-60, budget 100</span>
  <p>Parameters are remarkably stable across splits — and <code>a_smb</code> (bold) is consistently the largest.</p></div>
    <div class="xscroll"><table><thead><tr><th>seed</th><th>T, a_knots, a_maxknots, <b>a_smb</b></th><th>train (30)</th><th>test (30, held out)</th><th>gain</th></tr></thead>
    <tbody>{hs_tm}</tbody></table></div></div>

  <div class="callout w" style="margin-top:20px">
    <h3>Two things this corrects</h3>
    <p><b><code>smaller mean block</code> carries the largest weight</b> — 7.8 to 9.3 across all five splits, against 5.4&#8211;7.4 for knots and 0.4&#8211;2.1 for max_knots. On its own it is the <i>weakest</i> family, flatlining to +0 at budget 1,000. In combination it is the biggest single term. <b>Testing features one at a time would have discarded it.</b></p>
    <p style="margin-bottom:0"><b>The endgame switch stops mattering.</b> Tuning drives T to 0 or 8, not 16. The <code>@endgame16</code> threshold is load-bearing for <i>pure lexicographic</i> <code>knots_first</code> — which scores 8/20, below baseline, without it — but a linear blend already degrades gracefully as L shrinks, so the explicit switch is redundant. The earlier claim that the threshold does real work holds only for the lexicographic arm.</p>
  </div>
</section>

<section id="cost">
  <h2>What it costs: nodes and path length</h2>
  <p class="lede">Solve rate alone cannot say an ordering is <i>better</i> — one that reaches more solutions by wandering into longer, costlier derivations has traded quality for coverage. Both remaining axes, on subset-60.</p>

  <div class="panel" style="margin-top:16px"><div class="phead"><h2>Tuned vs baseline</h2><span class="tag a">measured on the presentations BOTH arms solve</span></div>
    <div class="xscroll"><table><thead><tr><th>budget</th><th>solved</th><th>nodes (both-solved)</th><th>path (both-solved)</th><th>tuned, all its solves</th></tr></thead>
    <tbody>{hs_cp}</tbody></table></div></div>

  <div class="grid" style="margin-top:20px">
    <div class="callout"><h3>Path length is not being traded away</h3>
      <p>Marginally longer at budget 100&#8211;200 (+0.24, +0.80 moves), then <b>shorter</b> at 500&#8211;1,000 (&#8722;1.08, &#8722;1.83). Past a few hundred nodes the tuned ordering returns <i>better</i> derivations, not merely more of them. On the five held-out halves the mean path length is <b>identical to two decimals</b> — 11.43 against 11.43 — while nodes fall 26%.</p>
      <p style="margin-bottom:0">Neither arm claims a shortest path: best-first by length is not optimal for AC derivations. This is quality relative to the baseline, not distance from optimal.</p></div>
    <div class="callout w"><h3>Why &#8220;both-solved&#8221; is load-bearing</h3>
      <p>The last column is the tuned arm's path over <i>all</i> its solves — about 19 moves at budget 100, 30 at 1,000 — and it must <b>never</b> be read against the baseline's. The 13&#8211;14 extra presentations it solves are the hardest ones, with the longest derivations.</p>
      <p style="margin-bottom:0">Pooling them would make the tuned arm look <i>worse</i> on path length precisely <b>because it got further</b>. The column exists to make that confound visible rather than to hide it.</p></div>
  </div>

  <div class="callout b" style="margin-top:20px">
    <h3>The dissociation: what predicts difficulty is not what guides search</h3>
    <p><code>smaller mean block</code> is the <b>strongest classifier</b> on this page (AUC 0.912, 94.5% balanced accuracy) and the <b>weakest single search priority</b>. Knots are the reverse — demoted to chance level as a classifier once provenance is matched, yet the best single heuristic by a clear margin.</p>
    <p style="margin-bottom:0">These measure different things. A classifier is scored on the <b>start state</b>: does this presentation look hard? A heap priority is scored on its <b>gradient across the search</b>: does moving this way help? A statistic can rank starts well while being nearly flat over the states one move apart — which is what a bounded ratio like mean run length does. Knots are integer-valued and move rarely, so when one does move it is a strong, discrete signal.</p>
  </div>
</section>

<section id="tables">
  <h2>The two tables</h2>
  <div class="funnel" style="margin-top:14px">
    <div class="step"><span class="k">MS cells</span><span class="v">1190</span><span class="d">170 words × n∈1..7</span></div>
    <div class="step sa"><span class="k">Trivial</span><span class="v">640</span><span class="d">solved by the grid</span></div>
    <div class="step sa"><span class="k">Aut(F₂) orbits</span><span class="v">113</span><span class="d">5.7× redundancy removed</span></div>
    <div class="step sb"><span class="k">Unsolved</span><span class="v">550</span><span class="d">carrying 261 rep names</span></div>
    <div class="step sb"><span class="k">ACA classes</span><span class="v">124</span><span class="d">upper bound on distinct problems</span></div>
  </div>
  <div class="note" style="margin-top:16px"><b>0</b> Aut representatives are shared between the two tables — a shared orbit would mean an "unsolved" class is Aut-equivalent to a trivialized one, and therefore already solved. The 113-orbit partition is reproduced element-for-element by a second, independently written Whitehead implementation.</div>

  <div class="tools" style="margin-top:18px">
    <input type="search" id="q" placeholder="Filter both tables — id, relator, or member (e.g. YXXyx, 21_3, sol_00)" aria-label="Filter both tables">
    <span class="hits" id="hits">113 + 124 rows</span>
  </div>

  <div class="grid" style="margin-top:16px">
    <section class="panel"><div class="phead"><h2>Table A — Solved</h2><span class="tag a">113 Aut(F₂) orbits</span>
      <p>The 640 trivial cells, one row per distinct minimal automorphic state. No singletons: the smallest orbit holds 2 cells, the largest 16.</p></div>
      <div class="scroll"><table>
        <thead><tr><th>id</th><th>Aut-minimal representative</th><th>ℓ</th><th>cells</th><th>members (w@n)</th></tr></thead>
        <tbody id="tb-a">{rows_a}</tbody></table></div></section>
    <section class="panel"><div class="phead"><h2>Table B — Unsolved</h2><span class="tag b">124 ACA classes</span>
      <p>The 550 unsolved cells → 261 rep names → 124 classes. All 124 representatives are already Aut-minimal as written.</p></div>
      <div class="scroll"><table>
        <thead><tr><th>id</th><th>Class representative</th><th>ℓ</th><th>reps<br>cells</th><th>members (rep names)</th></tr></thead>
        <tbody id="tb-b">{rows_b}</tbody></table></div></section>
  </div>
</section>

<footer>Table A is quotiented by <b>Aut(F₂)</b> only — exact and decidable. Table B by <b>ACA</b> (AC moves <i>together with</i> change of variables), strictly coarser, so 124 is an upper bound, not a proven class count. No AC moves were run anywhere in the clustering: it is entirely about the initial minimal automorphic states as pairs of cyclic words. Sources <code>results/equivalence_classes/ms1190_tables/</code> and <code>results/clustering/</code>; code <code>experiments/clustering/</code>.</footer>
</div>

<script>
const q=document.getElementById("q"),hits=document.getElementById("hits");
const rowsA=[...document.querySelectorAll("#tb-a tr")],rowsB=[...document.querySelectorAll("#tb-b tr")];
function filter(){{const t=q.value.trim().toLowerCase();let a=0,b=0;
for(const r of rowsA){{const on=!t||r.dataset.q.includes(t);r.hidden=!on;if(on)a++;}}
for(const r of rowsB){{const on=!t||r.dataset.q.includes(t);r.hidden=!on;if(on)b++;}}
hits.textContent=`${{a}} + ${{b}} rows`;}}
q.addEventListener("input",filter);
document.addEventListener("click",e=>{{const btn=e.target.closest(".more");if(!btn)return;
const box=btn.nextElementSibling,open=btn.getAttribute("aria-expanded")==="true";
box.hidden=open;btn.setAttribute("aria-expanded",String(!open));
btn.textContent=open?"+"+box.children.length:"−";}});
</script>
"""

open(DEST, "w").write(page)
print("wrote", DEST, len(page), "bytes")
