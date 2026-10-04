# Status

## Real-data gate: FAILED for the original formulation
- AgentWebBench compositional stress test completed using 354 real web-search queries and 20 deterministic pairings.
- B=5 joint-relevance baseline: source recall 0.3444, both-source coverage 0.1136, traffic Gini 0.6167.
- Marginal-evidence greedy: source recall **0.3907**, both-source coverage **0.1452**, but traffic Gini worsens to **0.8575**.
- Direct traffic penalties and near-tie load balancing reduce concentration only by sacrificing substantial routing quality.
- The original claim that marginal evidence alone yields a quality/ecosystem Pareto improvement is falsified.

## What survives
- Marginal evidence is a real routing signal: +13.5% relative source recall and +27.9% relative full coverage in the controlled two-facet stress test.
- The unresolved contradiction is now explicit: local coverage maximization creates a rich-get-richer exposure externality.

## Next-generation requirement
- Replace per-query greedy routing with a globally capacity-aware allocation mechanism.
- The new method must dominate joint relevance on quality while keeping traffic Gini at or below the joint baseline.
- It must remain Web-native and CPU-reproducible.

**Current stage:** original EviRoute rejected; redesign in progress around global exposure-constrained evidence allocation.
