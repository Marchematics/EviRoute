#!/usr/bin/env python3
"""AgentWebBench compositional routing gate for EviRoute.

Builds controlled two-facet tasks by pairing real distinct-source web-search
queries, then compares joint relevance, facet-wise marginal evidence, and
distinct-facet assignment using AgentWebBench's canonical site descriptions.

No model API or GPU is required.
"""
from __future__ import annotations
import ast, json, math, random, re, urllib.request
from collections import Counter
from pathlib import Path

DATA_URL="https://raw.githubusercontent.com/cxcscmu/AgentWebBench/main/data/web_search/test_354.json"
DESC_URL="https://raw.githubusercontent.com/cxcscmu/AgentWebBench/main/awbench/prompts/website_descriptions.py"
STOP=set("the a an and or of to in for on with is are be from by at how what why who when where which best meaning up give giving does do can i my you your it this that welcome world largest online platform users user provides providing".split())

def fetch(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8")

def toks(s):
    return [x for x in re.sub(r"[^a-z0-9\s]"," ",s.lower()).split() if len(x)>1 and x not in STOP]

def cosine(a,b):
    return sum(w*b.get(t,0.0) for t,w in a.items())

def normalize(v):
    z=math.sqrt(sum(x*x for x in v.values())) or 1.0
    return {k:x/z for k,x in v.items()}

def gini(vals):
    a=sorted(vals); n=len(a); s=sum(a)
    if not s: return 0.0
    return sum((2*(i+1)-n-1)*x for i,x in enumerate(a))/(n*s)

def main():
    data=json.loads(fetch(DATA_URL))
    src=fetch(DESC_URL)
    m=re.search(r"WEBSITE_DESCRIPTIONS\s*=\s*({[\s\S]*?})\s*\n",src)
    descriptions=ast.literal_eval(m.group(1))
    sites=list(descriptions)

    docs=[toks(descriptions[s]+" "+s.replace("."," ")) for s in sites]
    df=Counter()
    for d in docs: df.update(set(d))
    idf={t:math.log((len(sites)+1)/(n+1))+1 for t,n in df.items()}

    site_vec={}
    for s,d in zip(sites,docs):
        c=Counter(d)
        site_vec[s]=normalize({t:(1+math.log(n))*idf.get(t,1.0) for t,n in c.items()})

    def qvec(q):
        c=Counter(toks(q))
        return normalize({t:(1+math.log(n))*idf.get(t,5.0) for t,n in c.items()})

    def make_pairs(seed):
        a=data[:]
        random.Random(seed).shuffle(a)
        used=set(); out=[]
        for i,x in enumerate(a):
            if x["id"] in used: continue
            j=i+1
            while j<len(a) and (a[j]["id"] in used or a[j]["source"][0]==x["source"][0]):
                j+=1
            if j==len(a): continue
            y=a[j]; used|={x["id"],y["id"]}
            out.append({"facets":[x["question"],y["question"]],"gold":[x["source"][0],y["source"][0]]})
        return out

    def route(task,B,mode):
        facet=[qvec(q) for q in task["facets"]]
        M={s:[cosine(v,site_vec[s]) for v in facet] for s in sites}
        if mode=="joint":
            jq=qvec(" ".join(task["facets"]))
            return sorted(sites,key=lambda s:cosine(jq,site_vec[s]),reverse=True)[:B]
        if mode=="facet_greedy":
            selected=[]; best=[0.0]*len(facet)
            while len(selected)<B:
                cand=max(
                    (s for s in sites if s not in selected),
                    key=lambda s:sum(max(best[j],M[s][j])-best[j] for j in range(len(facet)))
                )
                selected.append(cand)
                best=[max(best[j],M[cand][j]) for j in range(len(facet))]
            return selected
        # best distinct assignment to the two facets, then joint-relevance fill
        best_pair=max(
            ((a,b) for a in sites for b in sites if a!=b),
            key=lambda p:M[p[0]][0]+M[p[1]][1]
        )
        selected=list(best_pair)[:B]
        jq=qvec(" ".join(task["facets"]))
        for s in sorted(sites,key=lambda s:cosine(jq,site_vec[s]),reverse=True):
            if s not in selected: selected.append(s)
            if len(selected)==B: break
        return selected

    rows=[]
    for seed in range(20):
        tasks=make_pairs(seed)
        for B in (2,3,5):
            for mode in ("joint","facet_greedy","facet_assign"):
                traffic=Counter(); recall=full=0.0
                for t in tasks:
                    sel=route(t,B,mode)
                    traffic.update(sel)
                    h=sum(g in sel for g in t["gold"])
                    recall+=h/2
                    full+=h==2
                rows.append({
                    "seed":seed,"B":B,"mode":mode,"pairs":len(tasks),
                    "source_recall":recall/len(tasks),
                    "full_coverage":full/len(tasks),
                    "traffic_gini":gini([traffic[s] for s in sites]),
                })

    agg=[]
    for B in (2,3,5):
        for mode in ("joint","facet_greedy","facet_assign"):
            a=[r for r in rows if r["B"]==B and r["mode"]==mode]
            agg.append({
                "B":B,"mode":mode,
                "source_recall":sum(x["source_recall"] for x in a)/len(a),
                "full_coverage":sum(x["full_coverage"] for x in a)/len(a),
                "traffic_gini":sum(x["traffic_gini"] for x in a)/len(a),
            })

    payload={
        "benchmark":"AgentWebBench web_search",
        "protocol":"20 seeded pairings of distinct-source real queries",
        "aggregate":agg,
        "rows":rows,
    }
    out=Path("results/agentwebbench_real_gate_repro.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload["aggregate"],indent=2))

if __name__=="__main__":
    main()
