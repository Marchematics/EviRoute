
# EviRoute: Research Proposal

## Thesis
The Agentic Web turns search into decentralized coordination: website agents hide their corpora behind interfaces, while a user agent must decide where to spend a limited interaction budget. A relevance score answers "which site looks good alone?"; it does not answer "which site adds evidence I do not already have?"

EviRoute introduces a new pre-interaction object: a **query-conditioned coverage sketch**.

## Literature contradiction
AgentWebBench (ICML 2026) reports three facts at once: decentralized coordination can lag centralized retrieval, strong performance requires careful planning and enough interactions, and decentralized access concentrates traffic on a small set of sites. Meanwhile, recent tool-selection/search-agent work improves policies, often after observing richer retrieval outcomes or via learned rewards. The missing protocol primitive is a cheap way to estimate **cross-site complementarity before paying for full interaction**.

## Protocol
For query `q`, each site agent computes a compact sketch over its locally retrievable evidence fingerprints relevant to `q`. The sketch reveals coverage structure, not document text. The user agent maintains the union of already-covered sketch bins and routes next to the site with maximal estimated uncovered mass.

Possible implementations:
- hashed bitsets/Bloom-style coverage summaries;
- MinHash/HyperLogLog variants for cardinality and overlap;
- signed commitments if sites are untrusted.

## Objective
Let `E_i(q)` be the evidence atoms site `i` can support for query `q`. With budget `B`, maximize
`F(S)=| union_{i in S} E_i(q) |`
(or a weighted/quality-aware version).

With exact sets, this is monotone submodular coverage and greedy selection has the standard `(1-1/e)` guarantee. With approximate marginal estimates satisfying `|hatDelta-Delta| <= eps` at each selection, a standard greedy recurrence yields a bound of the form `(1-1/e)F(OPT)-O(B eps)`.

The paper should prove the exact constant for the chosen sketch and connect its collision rate to `eps`.

## Why this is not "information gain reward"
A learned search policy can reward information gain after retrieval. EviRoute changes the **Web coordination interface** so that marginal complementarity becomes observable *before* expensive content-agent calls. That is the intended paradigm contribution.

## CPU-first public-benchmark plan
1. Integrate into AgentWebBench's website-selection path.
2. Start with web search and web recommendation, where retrieval metrics avoid expensive answer-generation evaluation.
3. Cache per-site retrieved evidence and replay routing strategies on CPU.
4. Compare tool-embedding selection, prompt selection, independent relevance, MMR/diversification, random, set-level tool selection, and EviRoute.
5. Report NDCG/Recall, evidence coverage, interactions, latency, traffic Gini/top-share, and sketch bytes.
6. Stress-test sketch collisions, stale sketches, malicious sites, and query drift.

## Go / no-go gate
The real benchmark must show a Pareto improvement: materially higher task/evidence quality than independent relevance at the same interaction budget, while not worsening ecosystem concentration. A sketch that merely reproduces MMR is not enough.

## Current evidence
The included synthetic multi-query worlds show the desired qualitative effect: sketch-greedy routing approaches exact-set greedy coverage while reducing concentration relative to top-relevance routing. This justifies the AgentWebBench implementation, not a SOTA claim.

## Main risk
Sites may not want to reveal coverage fingerprints, and malicious sites may game sketches. A strong paper needs either privacy-preserving sketches, verifiable commitments, or an explicit honest-site threat model plus a companion strategic analysis.