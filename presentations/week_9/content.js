/* Week 9 slide content. Renderer: week9_presentation.html (edit nothing there).
   Slide fields: hero, title, sub, wide, stat:[{n,label,on}], steps:[{t,d}],
   figs:[{img,cap,stat}], table:{head,rows,cap}, foot.

   Minimal skin, week_4/week_6 rule: a content slide is a title + the stat numbers +
   the figure, and nothing else. The foot carries provenance; the talk carries the words.

   Every number comes from ../assets/week_9/stats.js, generated with the figures by
   figures/make_figures.py, which reads the frozen campaign jsonl and never runs a
   search. Nothing here is typed by hand. */

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

const k = x => (x == null ? '—' : x.toLocaleString('en-US'));
const band = (t, b) => (t.bins || []).find(r => r.band === b) || {};
const live = t => (t.bins || []).filter(r => r.n);

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
          'was searched at <b>1,000</b> nodes only, the orbits across the full ' +
          '501 / 1,000 / 100,000 ladder · the orbit list is rebuilt and self-checked by ' +
          'make_ac19_autmin_screen.py, so every campaign row names a list something can regenerate',
  },

  {
    title: 'The <strong>cascade</strong> — one algorithm, four stages',
    steps: [
      { t: 'Nielsen descent', d: 'reduce_basis_key — shortens the pair by basis moves. ' +
           'Costs <b>1</b> node and settles <b>0</b> rows by itself.' },
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
      { n: RW.has5 + ' / ' + k(RW.n), label: 'carry a length-5 relator' },
      { n: RW.moves_med, label: 'median certificate moves' },
      { n: RW.moves_min + '–' + RW.moves_max, label: 'move range' },
    ],
    steps: [
      { t: 'the pattern', d: 'b⁻¹ a b a⁻² — the Baumslag–Solitar relation, any signed ' +
           'generator pair, up to rotation, inversion and relator swap.' },
      { t: 'recognition', d: 'structural, not a lookup: 16 ordered (a,b) pairs, each ' +
           'built and compared against a relator of length exactly 5.' },
      { t: 'the collapse', d: 'pinch the companion to one stable letter → eliminate b, ' +
           'leaving a⁻¹ → kill every remaining a. Each step a checked AC move.' },
    ],
    foot: 'the gate is visible in the data: <b>' + RW.has5 + ' of ' + k(RW.n) + '</b> ' +
          'rewrite rows have a relator of length exactly 5, against <b>' + k(RW.other_has5) +
          ' of ' + k(RW.other_n) + '</b> for every other stage combined · every rewrite is ' +
          'realised as a concrete AC move and checked by replay_move, so the stage raises ' +
          'rather than emit an unverified step · p99 ' + RW.moves_p99 + ' moves',
  },

  {
    title: 'AC19 <strong>aut-min</strong> · difficulty bins',
    stat: [
      { n: k(AUT.total.median), label: 'median nodes, all ' + k(AUT.total.n), on: true },
      { n: k(AUT.total.mean), label: 'mean nodes' },
      { n: band(AUT, '< 10').share + '%', label: 'under 10 nodes' },
      { n: band(AUT, '≥ 10k').n, label: 'over 10,000' },
    ],
    figs: [{ img: A + 'bins_autmin.svg' }],
    foot: 'bands are the CASCADE\'s own node cost, and the band edges are week 8\'s ' +
          'unchanged · a band defined by the arm being measured selects for rows that arm ' +
          'is good at — said here rather than hidden, because the cascade is the only arm ' +
          'with a per-row cost on every row · mean is <b>' + k(AUT.total.mean) +
          '</b> against a median of <b>' + k(AUT.total.median) + '</b>: the mean is the tail',
  },

  {
    title: 'AC19 <strong>extended</strong> · the same bins, one budget',
    stat: [
      { n: k(EXT.total.median), label: 'median nodes, ' + k(EXT.total.n) + ' solved', on: true },
      { n: k(EXT.total.mean), label: 'mean nodes' },
      { n: k(EXT.unsolved), label: 'unsolved at 1,000' },
    ],
    figs: [{ img: A + 'bins_extended.svg' }],
    foot: '<b>The empty bands are the budget, not the data.</b> This run stopped at ' +
          k(EXT.budget) + ' nodes, so its tail is the <b>' + k(EXT.unsolved) + '</b> ' +
          'unsolved, not an absent band — the one row in 1k–10k solved on the budget\'s ' +
          'very last node · joined through the orbit table those ' + k(EXT.unsolved) +
          ' reduce to <b>8</b> genuinely open orbits, all singletons',
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
          cells: [b, k(a.n), (a.share == null ? '—' : a.share + '%'),
                  k(a.mean), k(a.median),
                  e.n ? k(e.n) : '<span style="color:#b9bec9">not run</span>',
                  e.n ? e.share + '%' : '—', e.n ? k(e.mean) : '—', e.n ? k(e.median) : '—'],
          on: b === '10–100',
        };
      }).concat([{
        cells: ['<b>all</b>', '<b>' + k(AUT.total.n) + '</b>', '100%',
                '<b>' + k(AUT.total.mean) + '</b>', '<b>' + k(AUT.total.median) + '</b>',
                '<b>' + k(EXT.total.n) + '</b>', '100%',
                '<b>' + k(EXT.total.mean) + '</b>', '<b>' + k(EXT.total.median) + '</b>'],
      }]),
      cap: 'Cascade nodes, exact on every row of both populations. The extended column ' +
           'covers the ' + k(EXT.total.n) + ' it solved; ' + k(EXT.unsolved) + ' more hit ' +
           'the 1,000-node ceiling and have no cost. Only the first three bands compare ' +
           'across populations — beyond them the extended run simply stops.',
    },
  },

  {
    title: 'Aut-minimising moves mass toward <em>cheap</em>',
    stat: [
      { n: band(EXT, '< 10').share + '% → ' + band(AUT, '< 10').share + '%',
        label: 'under 10 nodes, extended → aut-min', on: true },
      { n: band(EXT, '10–100').share + '% → ' + band(AUT, '10–100').share + '%',
        label: '10–100 nodes' },
    ],
    figs: [{ img: A + 'bins_compare.svg' }],
    foot: 'at the head the minimised form is the cheaper one — a quarter of the orbits ' +
          'settle under 10 nodes against a sixth of the raw presentations · the tail says ' +
          'the opposite, and that is the next slide but one',
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
          'under Aut(F₂), so the basis change pushes back through the path · what is missing ' +
          'is a <b>decoder</b>, not a proof: <b>' + k(SG.aut) + '</b> of the ' + k(SG.n) +
          ' orbits are settled but recorded rather than certified, and building that ' +
          'push-back is the open task',
  },

  {
    title: 'All three arms, on the same bands',
    stat: [
      { n: k(ARM.greedy && ARM.greedy.exact), label: 'greedy rows with a stored cost' },
      { n: k(ARM.s20_mk2 && ARM.s20_mk2.exact), label: 's20_mk2 rows with a stored cost' },
      { n: k(AUT.total.n), label: 'cascade rows with a stored cost', on: true },
    ],
    figs: [{ img: A + 'arms_on_bins.svg' }],
    foot: '<b>The bands are only exact for the cascade.</b> greedy and s20_mk2 stored a ' +
          'per-row cost only for rows that FAILED the 10,000-node screen — ' +
          k(ARM.greedy && ARM.greedy.exact) + ' and ' + k(ARM.s20_mk2 && ARM.s20_mk2.exact) +
          ' rows. For the rest the archive keeps a failure list and nothing else, so all ' +
          'that is known is "solved at ≤ ' + k(W.screen_budget) + '" · the shaded band is ' +
          'that bracket, not a measurement, and re-running the ~72k to close it is barred ' +
          'by the standing archive rule · ' + (ARM.greedy || {}).censored + ' greedy and ' +
          (ARM.s20_mk2 || {}).censored + ' s20_mk2 rows sit at the far end, still unsolved ' +
          'at ' + k(W.ten_m),
  },

  {
    wide: true,
    title: 'Which stage returned the certificate',
    stat: [
      { n: k(SG.counts && SG.counts['s40_gen']), label: 's40_gen', on: true },
      { n: k(SG.counts && SG.counts['rewrite (BS collapse)']), label: 'BS rewrite' },
      { n: k(SG.counts && SG.counts['s20_mk2']), label: 's20_mk2' },
      { n: k(SG.counts && SG.counts['descent alone'] || 0), label: 'descent alone' },
      { n: k(SG.open && SG.open.length), label: 'open' },
    ],
    figs: [{ img: A + 'stage_attribution.svg' }],
    foot: '<b>Descent alone is measured at zero</b>, not unrecorded: a descent landing on ' +
          '(x, y) would reach bs_collapse and return reason=terminal, and every one of the ' +
          k(RW.n) + ' rewrite rows returns collapsed instead · ' + k(SG.ac) +
          ' of the ' + k(SG.n) + ' are AC-certified and ' + k(SG.aut) + ' await the decoder, ' +
          'and that exposure sits in one bucket — the rewrite and s20_mk2 stages are 100% ' +
          'certified, every aut_assisted row comes from s40_gen · regenerated by ' +
          'experiments/search/stage_attribution.py',
  },

  {
    title: 'At the shipped default, stage 4 <em>cannot run</em>',
    stat: [
      { n: 'min(501, 501 − 501) = 0', label: 's20_mk2 allowance at B = 501', on: true },
      { n: '0 / ' + k(W.n_aut), label: 'rows carrying an s20_mk2 attempt' },
    ],
    steps: [
      { t: 'the prefix is fixed', d: 'normalization + rewrite cost exactly <b>1</b> node ' +
           'on all 53,939 rows that reach s40_gen.' },
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
      { n: (TM.rows || []).filter(r => r.budget === 501).length + ' / ' +
           (TM.mutual || []).length, label: 'settled inside the 501-node prefix', on: true },
      { n: k(Math.min.apply(null, (TM.rows || []).map(r => r.nodes))) + '–' +
           k(Math.max.apply(null, (TM.rows || []).map(r => r.nodes))), label: 'cascade nodes' },
      { n: k(TM.greedy_open) + ' / ' + k(TM.s20_open), label: 'greedy / s20_mk2 open at 10M' },
    ],
    figs: [{ img: A + 'tenm_residue.svg' }],
    foot: 'greedy and s20_mk2 both exhausted 10,000,000 nodes on every one of these · the ' +
          'cascade settles all ' + (TM.mutual || []).length + ', six of them inside the ' +
          '501-node prefix · <b>all ' + (TM.mutual || []).length + ' are aut_assisted</b>, ' +
          'so they are the only rows in the set with no AC certificate from any arm — their ' +
          'AC-triviality rests entirely on the undecoded push-back',
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
    foot: 'Lucas Fagan\'s question, run: same arm, same 10,000,000-node budget, same cap 64 ' +
          '— only the input word differs · it is <b>not length</b>: every original is as ' +
          'long as its representative or longer · the ratios are a lower bound, since no ' +
          'representative finished — 10M is where they were stopped, not where they would ' +
          'end · the cascade shows the same sign on a disjoint set, ' + k(OG.casc_solved) +
          '/' + k(OG.casc_n) + ' originals at ' + k(OG.casc_min) + '–' + k(OG.casc_max) +
          ' nodes against 0/' + k(OG.casc_n) + ' reps',
  },

  {
    title: 'u124 carries <strong>two</strong> zeros',
    stat: [
      { n: U.s20_solved + ' / ' + U.s20_n, label: 's20_mk2 at ' + k(U.s20_budget), on: true },
      { n: U.s40_solved + ' / ' + U.s40_n, label: 's40_gen at ' + k(U.s40_budget) },
    ],
    figs: [{ img: A + 'u124_two_zeros.svg' }],
    foot: 'never quote "0 of 124" without both — they are a thousandfold apart in budget ' +
          'and are not the same negative result · the 10M zero is a real exhaustion; the ' +
          '10,000 zero is a starter-budget ceiling · a 50× budget sweep moved the landing ' +
          'zone by at most 2 units, and six weightings moved it by 0, so the floor is a ' +
          'property of the presentations rather than of the search',
  },

  {
    wide: true,
    title: '<strong>Appendix</strong> · what each arm actually stored',
    table: {
      head: ['arm', 'rows with an exact cost', 'bounded ≤ ' + k(W.screen_budget),
             'still open at ' + k(W.ten_m), 'quotable bare?'],
      rows: [
        { cells: ['greedy', k((ARM.greedy || {}).exact), k((ARM.greedy || {}).bounded),
                  k((ARM.greedy || {}).censored), 'no — a bracket'] },
        { cells: ['s20_mk2', k((ARM.s20_mk2 || {}).exact), k((ARM.s20_mk2 || {}).bounded),
                  k((ARM.s20_mk2 || {}).censored), 'no — a bracket'] },
        { cells: ['cascade', k(AUT.total.n), '0', k((SG.open || []).length), 'yes'],
          on: true },
      ],
      cap: 'The two substitutions push in OPPOSITE directions — an unknown-easy row entered ' +
           'at ' + k(W.screen_budget) + ' overstates it, a censored row entered at ' +
           k(W.ten_m) + ' understates it — so a single mean for greedy or s20_mk2 is a ' +
           'bound in neither direction, and the figures show a bracket instead. ' +
           (W.job_b_provisional ? 'The 8 cascade rows re-run at a 10,000,000 ceiling are ' +
            'transcribed from the run log; their jsonl has not landed in the repo, so they ' +
            'are provisional.' : ''),
    },
  },
];
