# AgentWebBench real-data gate

This experiment tests the central EviRoute claim on public AgentWebBench data.

## Why a compositional stress test is needed

The `web_search` split contains 354 real queries, but each query has one gold source domain. Marginal evidence coverage is a set-selection claim: it becomes identifiable when a task needs complementary evidence from more than one source. We therefore pair two real, distinct-source AgentWebBench queries under 20 deterministic random seeds. Each paired task has two facets and two gold source domains. The route budget is five sites.

Site-side pre-routing information uses the benchmark's canonical website descriptions. This keeps the experiment CPU-only and reproducible.

## Result

| router | source recall | both gold sources covered | traffic Gini |
|---|---:|---:|---:|
| joint relevance | 0.3444 | 0.1136 | **0.6167** |
| marginal-evidence greedy | **0.3907** | **0.1452** | 0.8575 |
| facet assignment | 0.3501 | 0.1172 | 0.6400 |

Marginal evidence is useful: recall rises by about 13.5% relative and full two-source coverage by about 27.9% relative. The same policy makes traffic substantially more concentrated.

## Falsified variants

We also tested:
- direct congestion penalties;
- least-loaded choice among near ties;
- evidence-first selection followed by balanced filling.

The aggressive penalties can reduce Gini to very small values, but source recall collapses. The hybrid settings produce a quality/concentration trade-off and do not dominate the joint-relevance baseline.

## Consequence

The original paper claim is too strong. A local marginal-evidence objective is not enough to improve both answer coverage and Web ecosystem concentration. The next method must treat **global exposure capacity as part of the routing problem**, rather than appending a local fairness penalty.

This negative result is retained because it defines the next scientific problem precisely.
