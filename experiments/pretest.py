
from pathlib import Path
import sys,json
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src'))
from eviroute import greedy_sketch_route, top_relevance, mmr_route

def make_world(rng,W=100,E=500,hubs=15):
    common=set(rng.choice(E,size=90,replace=False).tolist())
    sites=[]
    for i in range(W):
        if i<hubs:
            base=set(rng.choice(list(common),size=65,replace=False).tolist())
            extra=set(rng.choice(E,size=35,replace=False).tolist())
            sites.append(base|extra)
        else:
            sites.append(set(rng.choice(E,size=42,replace=False).tolist()))
    return sites,common

def one_query(rng,sites,common,budget=8,m=256):
    E=500
    q_common=set(rng.choice(list(common),size=18,replace=False).tolist())
    remaining=list(set(range(E))-q_common)
    q=q_common|set(rng.choice(remaining,size=18,replace=False).tolist())
    rel=np.array([len(s&q)+0.03*rng.normal() for s in sites])
    methods={
      'TopRel':top_relevance(rel,budget),
      'MMR':mmr_route(sites,rel,budget),
      'EviRoute':greedy_sketch_route([s&q for s in sites],rel,budget,m=m),
    }
    # exact-set greedy coverage baseline
    chosen=[]; covered=set(); remaining_sites=set(range(len(sites)))
    for _ in range(budget):
        i=max(remaining_sites,key=lambda j:len((sites[j]&q)-covered))
        chosen.append(i); covered |= sites[i]&q; remaining_sites.remove(i)
    methods['ExactGreedy']=chosen
    out={}
    for name,ids in methods.items():
        cov=set()
        for i in ids: cov |= sites[i]&q
        out[name+'_recall']=len(cov)/len(q)
        out[name+'_hubshare']=np.mean(np.asarray(ids)<15)
    return out,methods

def gini(x):
    x=np.asarray(x,float)
    if x.sum()==0:return 0.0
    d=np.abs(x[:,None]-x[None,:]).sum()
    return d/(2*len(x)*x.sum())

def main():
    rows=[]
    for m in [32,64,128,256,512]:
        vals=[]
        for seed in range(40):
            rng=np.random.default_rng(seed); sites,common=make_world(rng)
            out,_=one_query(rng,sites,common,budget=8,m=m); vals.append(out)
        df=pd.DataFrame(vals)
        rows.append({'sketch_bits':m, **{c:df[c].mean() for c in df.columns}})
    pd.DataFrame(rows).to_csv(ROOT/'results'/'sketch_sweep.csv',index=False)

    world_rows=[]
    for world_seed in range(4):
        rng=np.random.default_rng(10_000+world_seed); sites,common=make_world(rng)
        counts={m:np.zeros(len(sites),int) for m in ['TopRel','MMR','EviRoute','ExactGreedy']}
        rec={m:[] for m in counts}
        for _ in range(60):
            out,methods=one_query(rng,sites,common,budget=8,m=256)
            for name,ids in methods.items():
                rec[name].append(out[name+'_recall'])
                counts[name][ids]+=1
        for name in counts:
            c=counts[name]
            world_rows.append({'world':world_seed,'method':name,'evidence_recall':np.mean(rec[name]),
                               'traffic_gini':gini(c),'top10_traffic_share':np.sort(c)[-10:].sum()/c.sum(),
                               'sites_visited':int(np.count_nonzero(c))})
    wdf=pd.DataFrame(world_rows); wdf.to_csv(ROOT/'results'/'multiquery_worlds.csv',index=False)
    summary={'experiment':'synthetic decentralized evidence-routing stress test',
             'claim_scope':'mechanism-only; not AgentWebBench SOTA',
             'multiquery_mean':wdf.groupby('method').mean(numeric_only=True).round(6).to_dict(orient='index')}
    (ROOT/'results'/'summary.json').write_text(json.dumps(summary,indent=2))
    print(wdf.groupby('method').mean(numeric_only=True).to_string())
if __name__=='__main__':main()