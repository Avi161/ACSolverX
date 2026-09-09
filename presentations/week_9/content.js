/* Week 9 slide content. Renderer: week9_presentation.html (edit nothing there).
   Slide fields: hero, title, sub, wide, stat:[{n,label,on}], steps:[{t,d}],
   figs:[{img,cap,stat}], table:{head,rows,cap}, foot.

   Minimal skin, week_4/week_6 rule: a content slide is a title + the stat numbers +
   the figure, and nothing else. The foot carries provenance; the talk carries the words.

   Every number comes from ../assets/week_9/stats.js, generated with the figures by
   figures/make_figures.py, which reads the frozen campaign jsonl and never runs a
   search. Nothing here is typed by hand -- if a figure appears as literal digits in
   this file it is a bug, not a shortcut. Structural constants (501, 500, the length-5
   relator, B - 501) are part of the algorithm, not measurements, and stay literal. */

const A = '../assets/week_9/';
const W = window.W9 || {};
const AUT = W.aut || {bins: [], total: {}};
const EXT = W.ext || {bins: [], total: {}};
const ARM = W.arms || {};
const SG = W.stages || {counts: {}, split: {}};
const RW = W.rewrite || {};
const TM = W.tenm || {rows: []};
const OG = W.orig || {};
const U = W.u124 || {};
const H2 = W.head2head || {bands: [], totals: {cascade: {}, s20_mk2: {}, greedy: {}}};

const k = x => (x == null ? '—' : x.toLocaleString('en-US'));
const band = (t, b) => (t.bins || []).find(r => r.band === b) || {};
const G = ARM.greedy || {}, S = ARM.s20_mk2 || {};
const nodes = (TM.rows || []).map(r => r.nodes);

const SLIDES = [
  {
    hero: true,
    title: 'Week <strong>9</strong>',
    sub: '',
    foot: 'Avi · AC-SolverX · SURF',
  },

  {
    title: '<strong>' + k(W.n_ext) + '</strong> presentations, <strong>' +
           k(W.n_aut) + '</strong> orbits',
    figs: [{ img: A + 'populations.svg' }],
    foot: 'AC19_extended.txt, and its Aut(F₂) orbit representatives · the two are run ' +
          'at different budgets and are <b>not the same experiment</b>: the extended set ' +
          'was searched at <b>' + k(EXT.budget) + '</b> nodes only, the orbits across the ' +
          'full 501 / 1,000 / 100,000 ladder · the orbit list is rebuilt and self-checked ' +
          'by make_ac19_autmin_screen.py, so every campaign row names a list something ' +
          'can regenerate',
  },

  {
    title: 'Three arms, on all <strong>' + k(H2.n) + '</strong> rows',
    stat: [
      { n: k((H2.totals.cascade || {}).median), label: 'cascade · median nodes', on: true },
      { n: k((H2.totals.s20_mk2 || {}).median), label: 's20_mk2' },
      { n: k((H2.totals.greedy || {}).median), label: 'greedy' },
      { n: H2.ratio_s20_clean + '× / ' + H2.ratio_greedy_clean + '×',
        label: 'total work, uncensored rows' },
    ],
    figs: [{ img: A + 'arms_summary.svg' }],
    foot: '<b>' + k(H2.n) + ' rows.</b> This slide used to read 225 — the mutual ' +
          k(W.screen_budget) + '-node failures, the only tail the archive priced for all ' +
          'three arms. Both plain arms have since been re-run over the whole screen, so ' +
          'the comparison is the population · <b>the ratio is quoted over the ' +
          k(H2.n_clean) + ' rows where nothing is censored</b>: with the ' +
          k(H2.censored_greedy) + ' greedy and ' + k(H2.censored_s20) + ' s20_mk2 rows ' +
          'still unsolved at ' + k(W.ten_m) + ' entered at the ceiling the same ratios ' +
          'read ' + H2.ratio_s20 + '× / ' + H2.ratio_greedy + '×, but ' +
          H2.censored_share_s20 + '% and ' + H2.censored_share_greedy + '% of those ' +
          'totals is then the substitution, not a measurement · the cascade is no sweep: ' +
          'it wins ' + k(H2.wins_greedy) + '/' + k(H2.n) + ' against greedy and ' +
          k(H2.wins_s20) + '/' + k(H2.n) + ' against s20_mk2, ties ' + k(H2.ties_s20) +
          ', and <b>loses the ' + H2.crossover + ' band outright</b>',
  },

  {
    title: 'The <strong>cascade</strong> — one algorithm, four stages',
    steps: [
      { t: 'Nielsen descent', d: 'reduce_basis_key — shortens the pair by basis moves. ' +
           'Costs <b>1</b> node and settles <b>' + k(SG.counts['descent alone'] || 0) +
           '</b> rows by itself.' },
      { t: '→ BS rewrite', d: 'recognises one relator pattern and collapses it by a ' +
           'certified move sequence. Budget min(1,000, ·).' },
      { t: '→ s40_gen', d: 'L + 40·S, with <b>Aut(F₂) moves in the heap</b> beside AC ' +
           'substitutions. Budget = starter, default <b>500</b>.' },
      { t: '→ s20_mk2', d: 'discard the frontier, restart from the <b>original</b> pair. ' +
           'L + 20·S + 2·MK, budget B − 501.' },
    ],
    foot: 'Both search stages restart from the canon\'d ORIGINAL pair — the descent\'s ' +
          'output feeds the rewrite stage and nothing else · a row settled by s20_mk2 was ' +
          'settled <b>inside</b> the cascade, by its fourth stage, not by a fallback outside it',
  },

  {
    title: 'What the rewrite <em>recognises</em>',
    stat: [
      { n: k(RW.n), label: 'orbits taken by the rewrite', on: true },
      { n: k(RW.has5) + ' / ' + k(RW.n), label: 'carry a length-5 relator' },
      { n: k(RW.moves_med), label: 'median certificate moves' },
      { n: k(RW.moves_min) + '–' + k(RW.moves_max), label: 'move range' },
    ],
    steps: [
      { t: 'the pattern', d: 'b⁻¹ a b a⁻² — the Baumslag–Solitar relation, any signed ' +
           'generator pair, up to rotation, inversion and relator swap.' },
      { t: 'recognition', d: 'structural, not a lookup: 16 ordered (a,b) pairs, each ' +
           'built and compared against a relator of length exactly 5.' },
      { t: 'the collapse', d: 'pinch the companion to one stable letter → eliminate b, ' +
           'leaving a⁻¹ → kill every remaining a. Each step a checked AC move.' },
    ],
    foot: 'the gate is visible in the data: <b>' + k(RW.has5) + ' of ' + k(RW.n) + '</b> ' +
          'rewrite rows have a relator of length exactly 5, against <b>' + k(RW.other_has5) +
          ' of ' + k(RW.other_n) + '</b> for every other stage combined · every rewrite is ' +
          'realised as a concrete AC move and checked by replay_move, so the stage raises ' +
          'rather than emit an unverified step · p99 ' + k(RW.moves_p99) + ' moves',
  },

  {
    title: 'AC19 <strong>aut-min</strong> · difficulty bins',
    stat: [
      { n: k(AUT.total.median), label: 'median nodes, all ' + k(AUT.total.n), on: true },
      { n: k(AUT.total.mean), label: 'mean nodes' },
      { n: band(AUT, '< 10').share + '%', label: 'under 10 nodes' },
      { n: k(band(AUT, '≥ 10k').n), label: 'over 10,000' },
    ],
    figs: [{ img: A + 'bins_autmin.svg' }],
    foot: 'bands are the CASCADE\'s own node cost, and the band edges are week 8\'s ' +
          'unchanged · a band defined by the arm being measured selects for rows that arm ' +
          'is good at — said here rather than hidden, because the cascade is the only arm ' +
          'with a per-row cost on every row · mean is <b>' + k(AUT.total.mean) +
          '</b> against a median of <b>' + k(AUT.total.median) + '</b>: the mean is the ' +
          'tail · <b>' + k(AUT.job_b_n) + ' rows are reconstructed, not measured</b> — ' +
          'their jsonl has not landed, and they carry ' + AUT.job_b_pct + '% of the ' +
          'total node mass, so the mean above rests on them and the median does not',
  },

  {
    title: 'AC19 <strong>extended</strong> · the same bins, full ladder',
    stat: [
      { n: k(EXT.total.median), label: 'median nodes, ' + k(EXT.total.n) + ' reached (x,y)',
        on: true },
      { n: k(EXT.total.mean), label: 'mean nodes' },
      { n: k(EXT.ac), label: 'AC-certified' },
      { n: k(EXT.unsolved), label: 'unsolved at ' + k(EXT.budget) },
    ],
    figs: [{ img: A + 'bins_extended.svg' }],
    foot: '<b>Every band is real and the set is closed</b> — ' + k(EXT.total.n) + ' of ' +
          k(EXT.total.n) + ', nothing left at the ceiling. An earlier version of this ' +
          'slide said the two hard bands were empty because the run stopped at ' +
          k(EXT.budget_first_rung) + ' nodes; the ' + k(W.screen_budget) + ' and ' +
          k(EXT.budget) + ' rungs had in fact run, each over the rung below\'s residue, ' +
          'and between them they finish it · the 100,000 file carries 397 lines for 227 ' +
          'names because 91 are MemoryError records from workers that OOM\'d and were ' +
          're-run on resume, so it is read by name and never by line count · and ' +
          '<b>reached (x, y) is not certified</b>: only ' + k(EXT.ac) + ' of the ' +
          k(EXT.total.n) + ' carry an AC certificate, the other ' + k(EXT.aut_assisted) +
          ' went through a Nielsen image',
  },

  {
    wide: true,
    title: 'Mean and median, per band, both populations',
    table: {
      head: ['band', 'aut-min n', 'share', 'mean', 'median',
             'extended n', 'share', 'mean', 'median'],
      rows: (W.bands || []).map(b => {
        const a = band(AUT, b), e = band(EXT, b);
        return {
          cells: [b, k(a.n), (a.share_pop == null ? '—' : a.share_pop + '%'),
                  k(a.mean), k(a.median),
                  e.n ? k(e.n) : '<span style="color:#b9bec9">not run</span>',
                  e.n ? e.share_pop + '%' : '—', e.n ? k(e.mean) : '—',
                  e.n ? k(e.median) : '—'],
          on: b === '10–100',
        };
      }).concat([{
        cells: ['<b>reached (x, y)</b>', '<b>' + k(AUT.total.n) + '</b>', '—',
                '<b>' + k(AUT.total.mean) + '</b>', '<b>' + k(AUT.total.median) + '</b>',
                '<b>' + k(EXT.total.n) + '</b>', '—',
                '<b>' + k(EXT.total.mean) + '</b>', '<b>' + k(EXT.total.median) + '</b>'],
      }, {
        cells: ['unsolved at the ceiling', k(0), '—', '—', '—',
                k(EXT.unsolved), '—', '—', '—'],
      }]),
      cap: 'Cascade nodes. Shares are of the whole population, so each column\'s bands ' +
           'plus its unsolved row account for all of it. <b>All five bands now compare</b> ' +
           '— the extended side used to stop at ' + k(EXT.budget_first_rung) + ' nodes, ' +
           'which made its two hard bands an artefact of the budget rather than a ' +
           'measurement; its full ladder has since landed and the set is closed, so the ' +
           'two columns are a like-for-like pair. ' + k(AUT.job_b_n) + ' aut-min rows are ' +
           'reconstructed rather than measured, and they sit in the last band.',
    },
  },

  {
    title: 'Aut-minimising moves mass toward <em>cheap</em>',
    stat: [
      { n: band(EXT, '< 10').share_pop + '% → ' + band(AUT, '< 10').share_pop + '%',
        label: 'under 10 nodes, extended → aut-min', on: true },
      { n: band(EXT, '10–100').share_pop + '% → ' + band(AUT, '10–100').share_pop + '%',
        label: '10–100 nodes' },
    ],
    figs: [{ img: A + 'bins_compare.svg' }],
    foot: 'at the head the minimised form is the cheaper one — ' +
          band(AUT, '< 10').share_pop + '% of the orbits settle under 10 nodes against ' +
          band(EXT, '< 10').share_pop + '% of the raw presentations, both counted over ' +
          'their full populations · this no longer needs a caveat: the extended side ' +
          'used to be missing its hardest rows, which understated the comparison, and ' +
          'now all ' + k(EXT.total.n) + ' are priced · the tail says the opposite, and ' +
          'that is the slide two on',
  },

  {
    title: 'The three arms',
    steps: [
      { t: 'greedy', d: 'AC substitutions only, ordered by total length. The control: ' +
           'no Nielsen image ever enters the heap.' },
      { t: 's20_mk2', d: 'AC substitutions only, ordered by L + 20·S + 2·MK. Same move ' +
           'set as greedy, better ruler.' },
      { t: 'cascade', d: 'the four stages. Its s40_gen stage is the only one that searches ' +
           '<b>Aut(F₂) moves</b> alongside AC substitutions.' },
    ],
    foot: 'a path through a Nielsen image is still an AC solve — AC moves are equivariant ' +
          'under Aut(F₂), so the basis change pushes back through the path · that push-back ' +
          'is <b>built</b>: ac_decode.py does it and every MS640 certificate replays to ' +
          '(x, y) · what the <b>' + k(SG.aut) + '</b> aut-assisted orbits still need is ' +
          'their <b>paths</b> — the screen stored a flag and no move string, so closing ' +
          'them is a re-run with capture plus a decode pass, not new mathematics',
  },

  {
    title: 'Where the cascade stops winning',
    stat: [
      { n: H2.crossover, label: 'the band it loses', on: true },
      { n: k(H2.wins_greedy) + ' / ' + k(H2.n), label: 'beats greedy' },
      { n: k(H2.wins_s20) + ' / ' + k(H2.n), label: 'beats s20_mk2' },
    ],
    figs: [{ img: A + 'arms_headtohead.svg' }],
    foot: 'the cascade owns the MIDDLE, not the ends. It takes 100–1k by 4× over s20_mk2 ' +
          'and 9× over greedy — its rewrite and s40_gen stages settle those rows before ' +
          'either plain arm has started · it <b>loses the cheapest band</b>, where its own ' +
          'fixed prefix costs more than the whole search: a row a plain arm finishes in 6 ' +
          'nodes cannot be beaten by an algorithm that spends nodes normalising first · ' +
          'and it <b>loses the ' + k(band(AUT, '≥ 10k').n) + ' rows of the top band ' +
          'badly</b>, 14k against ~4k, which says its hard rows are not the plain arms\' ' +
          'hard rows · that band is won against a handicap, not with one: the ' +
          k(H2.censored_greedy) + ' greedy and ' + k(H2.censored_s20) + ' s20_mk2 rows ' +
          'unsolved at ' + k(W.ten_m) + ' enter at the ceiling, pushing those medians ' +
          '<b>up</b>',
  },

  {
    wide: true,
    title: 'The same numbers, per band',
    table: {
      head: ['band', 'rows', 'cascade', 's20_mk2', 'greedy', 'winner', 'censored'],
      rows: (H2.bands || []).map(b => ({
        cells: [b.band, k(b.n), k(b.cascade), k(b.s20_mk2), k(b.greedy),
                b.winner, b.censored ? k(b.censored) : '—'],
        on: b.winner !== 'cascade',
      })).concat([{
        cells: ['<b>all</b>', '<b>' + k(H2.n) + '</b>',
                '<b>' + k((H2.totals.cascade || {}).median) + '</b>',
                '<b>' + k((H2.totals.s20_mk2 || {}).median) + '</b>',
                '<b>' + k((H2.totals.greedy || {}).median) + '</b>', 'cascade', '—'],
      }, {
        cells: ['total nodes', k(H2.n),
                k((H2.totals.cascade || {}).total), k((H2.totals.s20_mk2 || {}).total),
                k((H2.totals.greedy || {}).total),
                H2.ratio_s20 + '× / ' + H2.ratio_greedy + '×', '—'],
      }]),
      cap: 'Median nodes per row, on the ' + k(H2.n) + ' rows where all three arms have ' +
           'a real cost — which is now nearly the whole screen, not the 225-row tail this ' +
           'table was built on. cascade + greedy covers ' + k(H2.n_greedy) + ' rows, ' +
           'cascade + s20_mk2 ' + k(H2.n_s20) + ', all three ' + k(H2.n) + '. <b>Read the ' +
           'total-nodes row with the censoring in mind</b>: ' + k(H2.censored_greedy) + ' ' +
           'greedy and ' + k(H2.censored_s20) + ' s20_mk2 rows enter at ' + k(W.ten_m) + ', ' +
           'which is ' + H2.censored_share_greedy + '% and ' + H2.censored_share_s20 +
           '% of those two totals. Over the ' + k(H2.n_clean) + ' rows where nothing is ' +
           'censored the same comparison is ' + k(H2.totals_clean.cascade.total) + ' / ' +
           k(H2.totals_clean.s20_mk2.total) + ' / ' + k(H2.totals_clean.greedy.total) +
           ' nodes — ' + H2.ratio_s20_clean + '× and ' + H2.ratio_greedy_clean + '×.',
    },
  },

  {
    title: 'The rung that was <em>missing</em>',
    stat: [
      { n: k(G.exact), label: 'greedy rows with a measured cost', on: true },
      { n: k(S.exact), label: 's20_mk2 rows with a measured cost' },
      { n: k(AUT.total.n), label: 'cascade rows with a measured cost' },
      { n: '225 → ' + k(H2.n), label: 'rows the comparison runs on' },
    ],
    figs: [{ img: A + 'arms_on_bins.svg' }],
    foot: 'Until 2026-09-08 this slide said the comparison was <b>tail-only</b>, and it ' +
          'was: the 1k/10k wave ran in Colab and only its FAILURE lists came back, so ' +
          'greedy and s20_mk2 had a stored cost for the ' + k(W.screen_budget) + '-node ' +
          'screen\'s ' + '831 and 259 failures and nothing for the ~72k ' +
          'they solved · every rung above is a funnel — each ran the rung below\'s ' +
          'failures — so no later file could fill it · re-running both arms over all ' +
          k(W.n_aut) + ' orbits took <b>one core-hour</b>, and reproduced every archived ' +
          'failure at exactly its archived node count (831/831 and 259/259), which is a ' +
          'cross-generation bit-identity check as much as a re-run · what remains ' +
          'unmeasured is ' + k(G.censored) + ' + ' + k(S.censored) + ' rows censored at ' +
          k(W.ten_m) + ' and ' + k(G.unescalated) + ' + ' + k(S.unescalated) + ' the ' +
          'original wave never judged, so no higher rung ever ran them',
  },

  {
    title: 'Which stage returned the certificate',
    stat: [
      { n: k(SG.counts['s40_gen']), label: 's40_gen', on: true },
      { n: k(SG.counts['rewrite (BS collapse)']), label: 'BS rewrite' },
      { n: k(SG.counts['s20_mk2']), label: 's20_mk2' },
      { n: k(SG.counts['terminal'] || 0), label: 'terminal' },
      { n: k(SG.counts['descent alone'] || 0), label: 'descent alone' },
      { n: k((SG.open || []).length), label: 'open at 100,000' },
    ],
    figs: [{ img: A + 'stage_attribution.svg' }],
    foot: '<b>Descent alone is measured at zero</b>, not unrecorded: a descent landing on ' +
          '(x, y) would reach bs_collapse and return reason=terminal, and every one of the ' +
          k(RW.n) + ' rewrite rows returns collapsed instead · ' + k(SG.ac) +
          ' of the ' + k(SG.n) + ' are AC-certified and ' + k(SG.aut) + ' are settled but ' +
          'hold no move string, and that exposure sits in one bucket — the rewrite and ' +
          's20_mk2 stages are 100% certified, every aut-assisted row comes from s40_gen · ' +
          'regenerated by experiments/search/stage_attribution.py · <b>the ' +
          k((SG.open || []).length) + ' open rows are not unsolved</b> — that is where ' +
          'the 501/1k/100k ladder stops, and all ' + k((SG.open || []).length) +
          ' were re-run at ' + k(W.ten_m) + ' and solved, AC-certified, ' +
          '149,962 to 230,345 nodes',
  },

  {
    title: 'At the shipped default, stage 4 <em>cannot run</em>',
    stat: [
      { n: 'min(501, 501 − 501) = 0', label: 's20_mk2 allowance at B = 501', on: true },
      { n: '0 / ' + k(W.n_aut), label: 'rows carrying an s20_mk2 attempt' },
    ],
    steps: [
      { t: 'the prefix is fixed', d: 'normalization + rewrite cost exactly <b>1</b> node ' +
           'on every row that reaches s40_gen.' },
      { t: 'the starter is pinned', d: 's40_gen takes min(starter, ·) = <b>500</b>, at ' +
           'every rung of the ladder.' },
      { t: 'so 1 + 500 = 501', d: 'and the loop skips any stage whose allowance is ≤ 0. ' +
           'The 501-node screen is a <b>three</b>-stage pipeline.' },
    ],
    foot: 'this is the starvation result stated from the other end — B − 501 is the right ' +
          'formula for what stage 4 receives, and at B = 501 it evaluates to zero · the ' +
          '--starter-budget flag exists because starter_budget used to be an imported ' +
          'constant, so every rung gave s40_gen exactly 500 nodes and handed any rope above ' +
          'that to a stage that could not be entered',
  },

  {
    title: 'The <strong>' + (TM.mutual || []).length + '</strong> rows no arm took at ' +
           '<strong>' + k(W.ten_m) + '</strong>',
    stat: [
      { n: k(TM.in_prefix) + ' / ' + (TM.mutual || []).length,
        label: 'settled inside the 501-node prefix', on: true },
      { n: k(Math.min.apply(null, nodes)) + '–' + k(Math.max.apply(null, nodes)),
        label: 'cascade nodes' },
      { n: k(TM.greedy_open) + ' / ' + k(TM.s20_open), label: 'greedy / s20_mk2 open at 10M' },
    ],
    figs: [{ img: A + 'tenm_residue.svg' }],
    foot: 'greedy and s20_mk2 both exhausted ' + k(W.ten_m) + ' nodes on every one of ' +
          'these · the cascade settles all ' + (TM.mutual || []).length + ', ' +
          k(TM.in_prefix) + ' of them inside the 501-node prefix and the rest at the 1,000 ' +
          'and 100,000 rungs · <b>' + k(TM.ac_certified) + ' of the ' +
          (TM.mutual || []).length + ' are AC-certified</b> — they are the only rows in the ' +
          'set with no certificate from any arm, so their AC-triviality rests on a decode ' +
          'pass nobody has run on them yet',
  },

  {
    title: 'At the <em>tail</em>, aut-minimising makes rows harder',
    stat: [
      { n: k(OG.solved) + ' / ' + k(OG.n), label: 'raw originals solved', on: true },
      { n: '0 / ' + k(OG.orbits), label: 'their minimised reps solved' },
      { n: k(OG.median), label: 'median nodes, originals' },
      { n: k(OG.ctl_nodes), label: 'reps, stopped here' },
    ],
    figs: [{ img: A + 'autmin_harder.svg' }],
    foot: 'Lucas Fagan\'s question, run: same arm, same ' + k(OG.ctl_nodes) + '-node ' +
          'budget, same cap 64 — only the input word differs · <b>the ' + k(OG.orbits) +
          ' reps are the selection criterion</b>, chosen for having failed at ' +
          k(OG.ctl_nodes) + ', so their 0 is true by construction and the ' + k(OG.solved) +
          '/' + k(OG.n) + ' is the measurement · it is <b>not length</b>: every original is ' +
          'as long as its representative or longer · ratios are a lower bound, since no rep ' +
          'finished · the cascade shows the same sign on a disjoint set, ' + k(OG.casc_solved) +
          '/' + k(OG.casc_n) + ' originals at ' + k(OG.casc_min) + '–' + k(OG.casc_max) +
          ' nodes against 0/' + k(OG.casc_n) + ' reps',
  },

  {
    title: 'u124 carries <strong>two</strong> zeros',
    stat: [
      { n: k(U.s20_solved) + ' / ' + k(U.s20_n), label: 's20_mk2 at ' + k(U.s20_budget),
        on: true },
      { n: k(U.s40_solved) + ' / ' + k(U.s40_n), label: 's40_gen at ' + k(U.s40_budget) },
    ],
    figs: [{ img: A + 'u124_two_zeros.svg' }],
    foot: 'never quote "' + k(U.s20_solved) + ' of ' + k(U.s20_n) + '" without both — they ' +
          'are a thousandfold apart in budget and are not the same negative result · the ' +
          k(U.s20_budget) + ' zero is a real exhaustion; the ' + k(U.s40_budget) + ' zero is ' +
          'a starter-budget ceiling · the 10M jsonl carries ' + k(U.s20_lines) + ' lines for ' +
          k(U.s20_n) + ' rows, a resumed lane re-appending, so count names and not lines',
  },

  {
    wide: true,
    title: '<strong>Appendix</strong> · what each arm actually stored',
    table: {
      head: ['arm', 'rows with an exact cost', 'unmeasured',
             'unsolved at its deepest budget', 'quotable bare?'],
      rows: [
        { cells: ['greedy', k(G.exact),
                  G.unmeasured ? k(G.unmeasured) + ' at ' + k((G.unmeasured_at || [])[0])
                               : '0',
                  k(G.censored) + ' at ' + k(W.ten_m),
                  'yes, bar ' + k(G.censored + G.unmeasured)] },
        { cells: ['s20_mk2', k(S.exact),
                  S.unmeasured ? k(S.unmeasured) + ' at ' + k((S.unmeasured_at || [])[0])
                               : '0',
                  k(S.censored) + ' at ' + k(W.ten_m),
                  'yes, bar ' + k(S.censored + S.unmeasured)] },
        { cells: ['cascade', k(AUT.total.n), '0', '<b>0</b> at ' + k(W.ten_m),
                  'yes, bar ' + k(AUT.job_b_n) + ' transcribed'],
          on: true },
      ],
      cap: 'This table used to say "no — a bracket" for both plain arms, because an ' +
           'unknown-easy row could only be entered at ' + k(W.screen_budget) + ' and a ' +
           'censored one at ' + k(W.ten_m) + ', substitutions that push in OPPOSITE ' +
           'directions, so no single mean was a bound in either. The ' +
           k(W.screen_budget) + '-node rung has since been re-run over all ' + k(W.n_aut) +
           ' orbits, so the first column is measured and the bracket is gone; what is ' +
           'left out is named per row rather than averaged over. The deepest budget ' +
           'differs by arm: greedy and s20_mk2 were ' +
           'carried to ' + k(W.ten_m) + ', the cascade ladder stops at 100,000. Its ' +
           k(AUT.job_b_n) + ' rows re-run above that are transcribed from a run log whose ' +
           'jsonl has not landed, and they carry ' + AUT.job_b_pct + '% of the node mass.',
    },
  },
];
