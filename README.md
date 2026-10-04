
# EviRoute

**Marginal-Evidence Routing with Coverage Sketches for the Agentic Web**

AgentWebBench exposes a new routing problem: a user agent must choose which website-specific content agents to query before seeing their hidden evidence. Selecting sites independently by relevance creates redundant interactions and can concentrate traffic.

EviRoute asks content agents to expose a compact **query-conditioned evidence coverage sketch** before expensive retrieval. The user agent greedily selects the site with the largest estimated *uncovered* evidence gain.

Run `python experiments/pretest.py`. The included results are synthetic mechanism tests; the decisive experiment is an AgentWebBench integration.