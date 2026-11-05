import csv, collections, math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','benchmark')+'/'
allr=list(csv.DictReader(open(B+'difficulty_bins.csv')))
sub=list(csv.DictReader(open(B+'subsets/benchmark_subset_60.csv')))
rank={int(r['pres_id']):int(r['difficulty_rank']) for r in allr}
cnt=collections.Counter(s['aut_class'] for s in sub)
edges=sorted({int(r['bin_lo_nodes']) for r in allr}|{int(r['bin_hi_nodes']) for r in allr})
INK='#0b0b0b'; INK2='#52514e'; GRID='#e4e3df'; GREY='#bdbcb6'; BLUE='#2a78d6'; ORANGE='#eb6834'; BAND='#f3f2ee'
plt.rcParams.update({'font.size':8,'font.family':'serif','axes.edgecolor':INK2,'axes.labelcolor':INK,
  'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False})
uniq=[s for s in sub if cnt[s['aut_class']]==1]; rep=[s for s in sub if cnt[s['aut_class']]>1]
def picks(ax,fx,fy):
    ax.scatter([fx(s) for s in uniq],[fy(s) for s in uniq],s=26,c=BLUE,edgecolors='white',linewidths=0.8,zorder=3,label=f'bench60, orbit once ({len(uniq)})')
    ax.scatter([fx(s) for s in rep],[fy(s) for s in rep],s=30,marker='D',c=ORANGE,edgecolors='white',linewidths=0.8,zorder=3,label=f'bench60, orbit repeated ({len(rep)})')
def legend(ax,loc):
    ax.legend(loc=loc,frameon=True,framealpha=0.95,edgecolor=GRID,fontsize=7,handletextpad=0.3,borderpad=0.4,markerscale=0.9)
W,H=3.4,2.9
# left: g against rank, horizontal bands = difficulty classes
f,ax=plt.subplots(figsize=(W,H))
for i in range(10):
    if i%2==0: ax.axhspan(edges[i],edges[i+1],color=BAND,zorder=0,lw=0)
    ax.text(668,math.sqrt(edges[i]*edges[i+1]),str(i),va='center',ha='left',fontsize=7,color=INK2,clip_on=False)
ax.text(668,2.2e6,'class',ha='left',fontsize=7,color=INK2,clip_on=False)
ax.scatter([int(r['difficulty_rank']) for r in allr],[int(r['nodes_explored']) for r in allr],s=4,c=GREY,lw=0,zorder=2,label='MS640 (640)')
picks(ax,lambda s:rank[int(s['pres_id'])],lambda s:int(s['nodes_1M']))
ax.set_yscale('log'); ax.set_ylim(2,1.1e6); ax.set_xlim(-12,655)
ax.set_xlabel('MS640 rows, easiest to hardest'); ax.set_ylabel('$g$ (expansions, log scale)')
legend(ax,'upper left'); f.tight_layout(); f.savefig('bench60_g.png',dpi=300); plt.close(f)
# right: path length against g, vertical bands = difficulty classes
f,ax=plt.subplots(figsize=(W,H))
for i in range(10):
    if i%2==0: ax.axvspan(edges[i],edges[i+1],color=BAND,zorder=0,lw=0)
    ax.text(math.sqrt(edges[i]*edges[i+1]),1250,str(i),ha='center',va='bottom',fontsize=7,color=INK2,clip_on=False)
ax.scatter([int(r['nodes_explored']) for r in allr],[int(r['path_length']) for r in allr],s=4,c=GREY,lw=0,zorder=2,label='MS640 (640)')
picks(ax,lambda s:int(s['nodes_1M']),lambda s:int(s['path_1M']))
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlim(2,1.1e6); ax.set_ylim(1.5,1100)
ax.set_xlabel('$g$ (expansions, log scale)\nbands: difficulty classes 0–9'); ax.set_ylabel('Path length (S-moves, log scale)')
legend(ax,'lower right'); f.tight_layout(); f.savefig('bench60_path.png',dpi=300); plt.close(f)
print(edges)
