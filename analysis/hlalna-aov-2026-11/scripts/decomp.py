import pandas as pd, numpy as np
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
df=pd.read_pickle('orders_enriched.pkl'); q=df[df.qualified].copy()
L=q[(q.day>='2026-11-02')&(q.day<='2026-11-08')]; P=q[(q.day>='2026-10-26')&(q.day<='2026-11-01')]; E=q[(q.day>='2026-10-10')&(q.day<='2026-11-01')]
def decomp(a,b,col,name):
    g0=a.groupby(col).total.agg(['count','mean']); g1=b.groupby(col).total.agg(['count','mean'])
    t=g0.join(g1,lsuffix='_0',rsuffix='_1',how='outer')
    t[['count_0','count_1']]=t[['count_0','count_1']].fillna(0)
    t['s0']=t.count_0/t.count_0.sum(); t['s1']=t.count_1/t.count_1.sum()
    a0=t.mean_0.fillna(t.mean_1); a1=t.mean_1.fillna(t.mean_0)
    t['mix']=(t.s1-t.s0)*(a0+a1)/2 - (t.s1-t.s0)*0  # adjust below relative to overall
    # center mix on overall mean to make category contributions interpretable
    A0=a.total.mean(); A1=b.total.mean(); Abar=(A0+A1)/2
    t['mix_effect']=(t.s1-t.s0)*((a0+a1)/2-Abar)
    t['rate_effect']=(t.s0+t.s1)/2*(a1-a0)
    t=t.drop(columns='mix')
    print(f'\n=== {name}: base {A0:.1f} -> {A1:.1f}  Δ={A1-A0:.1f} | mix={t.mix_effect.sum():.1f} rate={t.rate_effect.sum():.1f}')
    print(t.round(2).to_string()); return t
if __name__=='__main__':
    for col in ['primary_cat','channel','payment_method','returning']:
        decomp(P,L,col,f'P7→L7 by {col}')
    q['band']=pd.cut(q.total,[-1,500,700,900,1200,1e9],right=False,labels=['<500','500-699','700-899','900-1199','1200+'])
    L=q.loc[L.index]; P=q.loc[P.index]; E=q.loc[E.index]
    decomp(P,L,'band','P7→L7 by band')
    decomp(E,L,'primary_cat','Prior23→L7 by primary_cat')
    # bootstrap
    rng=np.random.default_rng(7); d=[rng.choice(L.total,len(L)).mean()-rng.choice(P.total,len(P)).mean() for _ in range(5000)]
    print('\nBootstrap Δ L7-P7 CI95',np.percentile(d,[2.5,97.5]).round(1))
    d=[rng.choice(L.total,len(L)).mean()-rng.choice(E.total,len(E)).mean() for _ in range(5000)]
    print('Bootstrap Δ L7-Prior23 CI95',np.percentile(d,[2.5,97.5]).round(1))
    from scipy import stats
    print(stats.mannwhitneyu(L.total,P.total))
