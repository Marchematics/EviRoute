
import numpy as np

def hashed_sketch(atoms, m=256):
    bits=np.zeros(m,dtype=bool)
    for a in atoms: bits[hash(int(a)) % m]=True
    return bits

def greedy_sketch_route(site_atoms, relevance, budget, m=256, relevance_tiebreak=1e-6):
    sketches=[hashed_sketch(a,m) for a in site_atoms]
    covered=np.zeros(m,dtype=bool); chosen=[]
    remaining=set(range(len(site_atoms)))
    for _ in range(min(budget,len(site_atoms))):
        best=None; best_val=-1
        for i in remaining:
            marginal=np.count_nonzero(sketches[i] & ~covered)
            val=marginal + relevance_tiebreak*float(relevance[i])
            if val>best_val: best_val=val; best=i
        chosen.append(best); covered |= sketches[best]; remaining.remove(best)
    return chosen

def top_relevance(relevance,budget):
    return np.argsort(-np.asarray(relevance))[:budget].tolist()

def mmr_route(site_atoms,relevance,budget,lam=0.65):
    chosen=[]; remaining=set(range(len(site_atoms)))
    while remaining and len(chosen)<budget:
        best=None; bestv=-1e18
        for i in remaining:
            if not chosen: redundancy=0.0
            else:
                A=site_atoms[i]
                redundancy=max(len(A&site_atoms[j])/max(1,len(A|site_atoms[j])) for j in chosen)
            v=lam*float(relevance[i])-(1-lam)*redundancy
            if v>bestv: bestv=v; best=i
        chosen.append(best); remaining.remove(best)
    return chosen