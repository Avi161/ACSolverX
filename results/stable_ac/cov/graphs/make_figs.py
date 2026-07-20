"""Regenerate the CoV-vs-baseline figures. Run from ACSolverX/:
    .venv/bin/python3 results/stable_ac/cov/graphs/make_figs.py
Baseline = each presentation's control row (z_word is null, no CoV). "CoV" = every
transformed start (relabel + moved). Only budget-100 rows in the source file.
"""
import json, collections, statistics, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

F="results/stable_ac/cov/covsweep_100_66_subnc2pxysb_mrl24_cyc_s60r6_07_16_26.jsonl"
OUT="results/stable_ac/cov/graphs"; BUDGET=100
rows=[json.loads(l) for l in open(F)]
by=collections.defaultdict(lambda:{'ctrl':None,'cov':[]})
for r in rows:
    (by[r['pres_id']]['ctrl'].__setitem__ if False else None)
    if r.get('z_word') is None: by[r['pres_id']]['ctrl']=r
    else: by[r['pres_id']]['cov'].append(r)

C_FEWER="#2a9d8f"; C_EQUAL="#9aa0a6"; C_MORE="#e9a13b"; C_FAIL="#d1495b"; C_BASE="#1d3557"
plt.rcParams.update({'font.size':11,'axes.grid':True,'grid.alpha':0.25,'axes.axisbelow':True,
                     'figure.facecolor':'white','axes.edgecolor':'#888'})

def klass(d):
    if d['ctrl']['solved']: return 'baseline_solved'
    if any(r['solved'] for r in d['cov']): return 'flip'
    return 'never_solved'

per=[]
for p,d in by.items():
    base=d['ctrl']['nodes_explored']; cov=d['cov']; ncov=len(cov)
    solved=[r for r in cov if r['solved']]
    fewer=sum(1 for r in solved if r['nodes_explored']<base)
    equal=sum(1 for r in solved if r['nodes_explored']==base)
    more =sum(1 for r in solved if r['nodes_explored']>base)
    per.append(dict(pres=p,klass=klass(d),base=base,n_cov=ncov,fewer=fewer,equal=equal,
                    more=more,unsolved=ncov-len(solved),
                    best=min((r['nodes_explored'] for r in solved),default=None)))
bs=sorted([r for r in per if r['klass']=='baseline_solved'], key=lambda r:-r['base'])

def spearman(xs,ys):
    n=len(xs)
    def rk(v):
        o=sorted(range(n),key=lambda i:v[i]);rr=[0.0]*n;i=0
        while i<n:
            j=i
            while j+1<n and v[o[j+1]]==v[o[i]]:j+=1
            for k in range(i,j+1):rr[o[k]]=(i+j)/2
            i=j+1
        return rr
    rx,ry=rk(xs),rk(ys);mx=sum(rx)/n;my=sum(ry)/n
    return sum((rx[i]-mx)*(ry[i]-my) for i in range(n))/math.sqrt(
        sum((v-mx)**2 for v in rx)*sum((v-my)**2 for v in ry))

# ================= FIGURE 1 =================
fig=plt.figure(figsize=(15,9)); gs=fig.add_gridspec(2,2,height_ratios=[1,1.25],hspace=0.42,wspace=0.22)
axa=fig.add_subplot(gs[0,0])
c=collections.Counter(r['klass'] for r in per)
vals=[c['baseline_solved'],c['flip'],c['never_solved']]
axa.bar(['baseline\nsolved','flip: only CoV\nsolves','never solved\nby anything'],vals,
        color=[C_BASE,C_FEWER,'#bbbbbb'],edgecolor='white')
for i,v in enumerate(vals): axa.text(i,v+0.6,str(v),ha='center',weight='bold')
axa.set_ylim(0,36); axa.set_ylabel("# presentations")
axa.set_title("A.  Solve landscape — all 66 presentations @ budget 100",fontsize=11,weight='bold',loc='left')

axb=fig.add_subplot(gs[0,1])
tf=sum(r['fewer'] for r in bs);te=sum(r['equal'] for r in bs);tm=sum(r['more'] for r in bs);tu=sum(r['unsolved'] for r in bs)
tot=tf+te+tm+tu
w,_=axb.pie([tf,te,tm,tu],colors=[C_FEWER,C_EQUAL,C_MORE,C_FAIL],startangle=90,counterclock=False,
            wedgeprops=dict(width=0.42,edgecolor='white',linewidth=2))
axb.text(0,0.12,f"{tot}",ha='center',fontsize=20,weight='bold')
axb.text(0,-0.16,"CoV variants\n(17 solved-baseline pres)",ha='center',fontsize=8.5,color='#555')
axb.legend(w,[f"fewer nodes (better)\n{tf}  ({100*tf/tot:.0f}%)",f"equal\n{te} ({100*te/tot:.0f}%)",
              f"more nodes (worse)\n{tm} ({100*tm/tot:.0f}%)",f"did not solve\n{tu} ({100*tu/tot:.0f}%)"],
           loc='center left',bbox_to_anchor=(1.0,0.5),fontsize=9,frameon=False)
axb.set_title("B.  Does a change of variables reduce nodes?  Only 35% do.",fontsize=11,weight='bold',loc='left')

axc=fig.add_subplot(gs[1,:]); x=np.arange(len(bs))
ff=np.array([100*r['fewer']/r['n_cov'] for r in bs]); ee=np.array([100*r['equal']/r['n_cov'] for r in bs])
mm=np.array([100*r['more']/r['n_cov'] for r in bs]);  uu=np.array([100*r['unsolved']/r['n_cov'] for r in bs])
axc.bar(x,ff,color=C_FEWER,label='CoV solved, FEWER nodes than baseline (better)')
axc.bar(x,ee,bottom=ff,color=C_EQUAL,label='equal')
axc.bar(x,mm,bottom=ff+ee,color=C_MORE,label='CoV solved, MORE nodes (worse)')
axc.bar(x,uu,bottom=ff+ee+mm,color=C_FAIL,label=f'CoV did NOT solve within {BUDGET} nodes')
axc.set_xticks(x); axc.set_xticklabels([f"{r['pres']}\nbase={r['base']}\nn={r['n_cov']}" for r in bs],fontsize=8)
axc.set_ylabel("% of that presentation's CoV variants"); axc.set_ylim(0,100)
axc.set_title("C.  Per presentation: of all brute-force CoVs, how many beat vs. lose to the greedy baseline  (sorted by baseline difficulty →)",
              fontsize=11,weight='bold',loc='left')
axc.legend(loc='upper center',bbox_to_anchor=(0.5,-0.16),ncol=2,fontsize=9,frameon=False)
fig.suptitle("Change of variables vs. greedy baseline — node-explored comparison (66-presentation benchmark, budget 100)",
             fontsize=13,weight='bold',y=0.98)
fig.savefig(f"{OUT}/fig1_composition.png",dpi=140,bbox_inches='tight'); print("wrote fig1_composition.png")

# ================= FIGURE 2 =================
fig2=plt.figure(figsize=(16,6)); gs2=fig2.add_gridspec(1,3,wspace=0.28,width_ratios=[1.25,1,1])
rng=np.random.default_rng(0)

ax1=fig2.add_subplot(gs2[0,0])
for i,r in enumerate(bs):
    ys=[t['nodes_explored'] for t in by[r['pres']]['cov'] if t['solved']]
    xs=i+(rng.random(len(ys))-0.5)*0.55
    lo=[y<r['base'] for y in ys]
    ax1.scatter([a for a,b in zip(xs,lo) if b],[y for y,b in zip(ys,lo) if b],s=10,color=C_FEWER,alpha=0.55,lw=0)
    ax1.scatter([a for a,b in zip(xs,lo) if not b],[y for y,b in zip(ys,lo) if not b],s=10,color=C_MORE,alpha=0.55,lw=0)
    ax1.plot([i-0.4,i+0.4],[r['base'],r['base']],color=C_BASE,lw=2.4,solid_capstyle='round')
ax1.set_yscale('log'); ax1.set_ylim(1.7,120)
ax1.set_xticks(range(len(bs))); ax1.set_xticklabels([r['pres'] for r in bs],rotation=90,fontsize=7)
ax1.set_xlabel("presentation (sorted by baseline)"); ax1.set_ylabel("nodes explored (log)")
ax1.set_title("A.  Every solved CoV (dots) vs baseline (navy bar)",fontsize=10.5,weight='bold',loc='left')
ax1.legend(handles=[Patch(color=C_FEWER,label='CoV < baseline'),Patch(color=C_MORE,label='CoV ≥ baseline'),
                    plt.Line2D([0],[0],color=C_BASE,lw=2.4,label='baseline')],fontsize=8,frameon=False,loc='upper right')

ax2=fig2.add_subplot(gs2[0,1])
base_true=[];cov_n=[];base_jit=[];bx=[];byy=[]
for r in bs:
    for t in by[r['pres']]['cov']:
        if t['solved']:
            base_true.append(r['base']); cov_n.append(t['nodes_explored'])
            base_jit.append(r['base']*(1+rng.uniform(-0.06,0.06)))
    bx.append(r['base']); byy.append(r['best'])
base_true=np.array(base_true);cov_n=np.array(cov_n);base_jit=np.array(base_jit)
lo=cov_n<base_true                                   # color from TRUE baseline, jitter for display only
ax2.scatter(base_jit[lo],cov_n[lo],s=9,color=C_FEWER,alpha=0.4,lw=0,label='below y=x (CoV faster)')
ax2.scatter(base_jit[~lo],cov_n[~lo],s=9,color=C_MORE,alpha=0.4,lw=0,label='on/above y=x (CoV slower)')
ax2.scatter(bx,byy,s=70,marker='D',facecolor='none',edgecolor=C_BASE,linewidths=1.6,label='best CoV / presentation',zorder=5)
ax2.plot([2,110],[2,110],'k--',lw=1,alpha=0.7); ax2.text(58,64,"y = x",rotation=34,fontsize=9,alpha=0.7)
ax2.set_xscale('log');ax2.set_yscale('log');ax2.set_xlim(2.5,120);ax2.set_ylim(1.7,120)
ax2.set_xlabel("baseline nodes (greedy, no CoV)");ax2.set_ylabel("CoV nodes explored")
ax2.set_title("B.  CoV vs baseline — points straddle y=x",fontsize=10.5,weight='bold',loc='left')
ax2.legend(fontsize=7.5,frameon=False,loc='lower right')

ax3=fig2.add_subplot(gs2[0,2])
xb=[r['base'] for r in bs]; yf=[100*r['fewer']/r['n_cov'] for r in bs]
ax3.scatter(xb,yf,s=45,color=C_FEWER,edgecolor='white',zorder=3)
for r in bs: ax3.annotate(str(r['pres']),(r['base'],100*r['fewer']/r['n_cov']),fontsize=6.5,xytext=(3,2),textcoords='offset points',color='#555')
ax3.set_xscale('log');ax3.set_xlabel("baseline nodes (log)");ax3.set_ylabel("% of CoVs that reduce nodes")
ax3.set_title("C.  CoV can only help where the baseline is costly (node counts floor at ~2)",fontsize=9.8,weight='bold',loc='left')
ax3.text(0.05,0.06,f"Spearman ρ = {spearman(xb,yf):+.2f}",transform=ax3.transAxes,fontsize=9,style='italic')
fig2.suptitle("Distribution & correlation — is the node reduction consistent, or a difficulty-tracking lottery?",fontsize=13,weight='bold',y=1.02)
fig2.savefig(f"{OUT}/fig2_distribution_correlation.png",dpi=140,bbox_inches='tight'); print("wrote fig2_distribution_correlation.png")
