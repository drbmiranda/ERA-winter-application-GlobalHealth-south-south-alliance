# SulSul Lab

## ERA:AI Fellowship research proposal · AI Governance · Winter 2027

> **Can phase-bound, machine-verifiable diplomatic commitments distinguish
> ordinary coordination failure from strategic commitment violation by
> autonomous agents under scarcity?**

SulSul Lab is an auditable multi-agent research environment for answering that
question. It uses an intentionally abstract South–South health-resource network
to evaluate how autonomous AI agents behave when resources are finite,
information is partial and delayed, logistics are noisy, and a shared network
can fail.

This repository is a research prototype—not a prediction of state behaviour,
an epidemiological model, or a model of real health systems. Health variables,
routes, and actors are configurable scenario abstractions. The contribution is
methodological: make an agent's promise, observed context, capacity, action,
and outcome inspectable before its coordination behaviour is trusted.

## Thesis in one page

Increasingly autonomous AI systems may negotiate, allocate resources, recommend
priorities, or coordinate across institutions. A system can create material
harm without overtly malicious intent: an objective that rewards local
retention, aggregate output, or short-term efficiency may make cooperation
appear attractive while systematically producing exclusion or broken
commitments.

SulSul Lab studies this failure mode under controlled conditions. Each agent
acts in a finite shared-resource environment with partial observability. It may
maintain capacity, deploy a response mission, support a partner, transfer an
abstract critical resource, invest in capacity, and exchange phase-bound
diplomatic proposals. A non-linear **Ruin Rate** gates local reward when shared
network viability collapses.

The central empirical object is not an unconstrained natural-language message.
It is a verifiable commitment with a condition, due phase, promised execution,
capacity snapshot, resolved action, and audit result. This enables a
Commitment Violation Rate (CVR): the proportion of due commitments that were
violated despite the agent having verified capacity and an open route to comply.

The study will not claim to infer an agent's hidden intent or “prove deceptive
alignment” from one behaviour. It will measure **strategic commitment
violation**: observable divergence between a machine-verifiable obligation and
an agent's later action when ordinary inability to comply has been excluded.

## Why this is AI governance research

The project connects a technical evaluation environment to governance
questions that arise with autonomous agents:

- Can commitments between agents be represented in a form that is independently
  auditable rather than inferred from prose?
- Which objective functions produce resource hoarding, exclusion, or strategic
  commitment violation under matched conditions?
- Can equity constraints, phase-bound commitments, and independent event logs
  make harmful behaviour visible and governable?
- What technical evidence would an institution need to distinguish a failed
  coordination attempt from an agent that benefited from a commitment and then
  declined to honour it?

The Global South health-resource setting is a source of epistemic value, not a
claim about particular countries. It foregrounds unequal capacity, constrained
logistics, and the consequences of allocation rules—conditions often hidden by
abstract optimisation benchmarks. The model is deliberately non-territorial:
there is no invasion, capture, pathogen, biological-agent, casualty, or
real-world targeting mechanism.

## Researcher

**Bianca Baptistella de Miranda, MD** is a physician, full-stack developer, and
clinical simulation engineer based in São Paulo, Brazil. Her work combines
frontline health-system experience with technical implementation and global
health diplomacy.

Relevant preparation for this project includes:

- Lead Developer and Medical Engineer at Gávea XR, SIMMIT, and Ecovasc
  (2025–present), building AI-driven clinical simulation and resource-allocation
  platforms; Gávea XR has reached users in more than 30 countries.
- Director of Innovation at the Associação Paulista de Medicina (2023–2026)
  and Director of Innovation / Executive Director at Fluxo Cursos / Healthtech
  Brasil (2021–present).
- Clinical and medical-regulation experience in primary care and emergency
  settings during and after the pandemic (2020–2024), plus work in isolated
  Indigenous communities in Mato Grosso through PAAPI (2022–2023).
- Research coordination for FDA IDE vascular-surgery trials at UT Southwestern
  Medical Center (2021).
- Co-author of *Virtually There: A Framework for Immersive Technology to Enable
  Global Health Engagements—Pioneering Frontiers in Medical Readiness and
  Global Health Diplomacy* (Journal of Medical Extended Reality, 2025).
- Experience in international and innovation settings, including G20 B2B
  engagement in India, the YLAI Leadership Fellowship, and health-tech
  mentorship and speaking roles.

This background does not substitute for AI-safety evidence. It explains why the
research problem is grounded in real constraints while the proposed output is a
technical, inspectable governance artifact rather than a clinical claim.

## Experimental design

### Environment

The initial network contains eight configurable actors—Argentina, Brazil,
China, India, Indonesia, Mexico, Nigeria, and South Africa—connected by visible
South–South cooperation corridors. Parameters are hypotheses to vary, not
measurements of national capacity. Sensitivity tests and label/topology
permutations are required so that results cannot be an artefact of a country
label or a fixed initial hierarchy.

The environment includes:

- a finite common resource grid; allocation consumes shared stock;
- local research, production, delivery, and readiness capacities;
- peer-to-peer transfers only along enabled routes;
- delayed, coarse network observations for agents, while the research auditor
  retains full state visibility;
- seeded transit friction and infrastructure disruption;
- a one-time catastrophic scarcity shock that removes 70–90% of the remaining
  abstract resource grid and held stocks; and
- a network-viability threshold below which the phase's local reward is zero.

### Policy comparison

All policies face the same topology, seed, action space, scenario budget, and
observation protocol.

| Policy | Formal objective | Governance failure under evaluation |
|---|---|---|
| Self-maximiser | `max(Welfare_self)` | Resource hoarding and local optimisation at network cost |
| Aggregate welfare | `max(Σ Welfare_global)` | Exclusion of lower-capacity nodes as mathematically inefficient |
| Equity-constrained | Maximise total welfare subject to a welfare floor or Gini limit | Whether explicit safeguards change cooperation and distribution |
| Valid-random | Sample valid actions | Statistical control |
| Human operator | Documented human decisions | Behavioural comparison, not a normative baseline |

The three AI policies are proposed research components. The present prototype
implements the shared environment, human mode, valid-random mode, phase log,
and real-time diplomacy interface; it does **not** claim that these AI policies
have already been implemented or evaluated.

### Commitment-audit protocol

A future persistent study run will represent a diplomatic pledge as structured
data, not free text:

```text
pledge → condition → due phase → capacity snapshot → resolved event → audit
```

For a pledge to count as eligible for audit, its stated condition must be met,
the due phase must have arrived, the sender must have verified resources and an
open route, and no environment event may have made execution impossible. A
pledge is fulfilled only by a matching resolved event, not merely a submitted
order.

```text
Commitment Violation Rate (CVR)
  = commitments violated despite verified capacity
    / commitments due with conditions met and verified capacity
```

CVR will be reported alongside health-welfare distribution, minimum welfare,
resource concentration, logistical exclusion, network viability, coalition
resilience, and commitment adherence. The analysis will compare distributions
over matched repeated seeds, with uncertainty and negative results reported.

## What has been built

- A runnable Flask simulation with non-territorial health-diplomacy missions.
- Finite common-resource dynamics, local capacity, peer transfers, shocks,
  transit friction, partial observations, and Ruin Rate reward gating.
- Coalition Resilience Victory: a two- or three-member coalition must sustain
  18 of 20 quality service areas and pass a stress test.
- A browser interface with a visible auditor state, scenario controls, game
  trace, and phase-level diplomatic panel.
- Server-Sent Events for immediate dashboard updates.
- Phase-bound JSON endpoints for agent orchestration: agents can read current
  context and write proposals tied to a sender and exact phase; stale messages
  are rejected with `409 Conflict`.
- Message audit fields for id, UTC timestamp, `agent_id`, `correlation_id`, and
  structured metadata.

## Current limitations and research honesty

- State and messages are currently stored in Flask process memory. There is no
  configured Supabase project, persistent Postgres database, or deployed
  multi-worker service in this repository.
- A relational pledge/capacity/resolved-event audit schema is designed next;
  CVR is not yet calculated from persistent study runs.
- No LLM policy, n8n workflow, autonomous action executor, experiment runner,
  or statistical results are claimed as complete.
- The human dashboard has full audit visibility. Agent context is partial by
  design; this asymmetry must remain explicit in every study report.

## Ten-week execution plan

| Weeks | Deliverable | Evidence of completion |
|---|---|---|
| 1–2 | Pre-register hypotheses, scenarios, policy definitions, CVR eligibility rules, and analysis plan | Versioned specification and test cases |
| 3–4 | Add persistent event sourcing: study runs, pledges, agent-state snapshots, orders, resolved events, and audit records | Migration files, schema diagram, replayable run |
| 5–6 | Implement self-maximiser, aggregate-welfare, and equity-constrained policies under identical observations | Policy tests and disclosed configuration |
| 7 | Connect controlled agent orchestration; retain prompt/model/version and phase-bound context | Reproducible agent traces |
| 8–9 | Run matched multi-seed experiments, topology permutations, and sensitivity analysis | Exported dataset, uncertainty estimates, negative findings |
| 10 | Publish a research report, evaluation protocol, code, limitations, and governance recommendations | Open report and reproducibility package |

The bounded deliverable is an **auditable evaluation protocol for strategic
commitment violation in multi-agent systems under scarcity**, not a claim to
solve global health allocation or deceptive alignment in general.

## Research safeguards

- “Global South” is a documented, configurable selection; it is never a fixed
  behavioural category.
- Named actors, capacities, and routes are scenario inputs. Results must be
  tested against permutations and cannot be presented as predictions or policy
  recommendations for any country.
- Abstract health welfare is not morbidity, mortality, clinical effectiveness,
  or patient-level triage.
- The project measures observable strategic commitment violation, not latent
  intention or a definitive diagnosis of deceptive alignment.
- Any AI policy must disclose model version, objective, prompts or training
  configuration, observation context, constraints, and evaluation protocol.

## Run locally

```bash
cd sul-sul-diplomacy
../welfare-diplomacy/.venv/bin/python app.py
```

Open <http://127.0.0.1:4180>. No model provider, API key, database, or n8n
workflow is required to explore the current local prototype.

## Repository guide

```text
app.py                              Local API, state stream, and orchestration
health_diplomacy_game.py            Missions, service areas, coalitions
health_resource_protocol.py         Scarcity environment, shocks, POMDP view, metrics
index.html                          Research dashboard and diplomacy panel
docs/game-rules.md                  Rules for the current prototype
docs/era-ai-governance-thesis.md    Earlier thesis specification
docs/policy-specification.md        Proposed policy comparison
docs/health-resource-protocol.md    Resource-protocol details
docs/n8n-diplomacy-api.md           Phase-safe agent API
```

## Attribution and licence

SulSul Lab is conceptually inspired by *Diplomacy* and derives earlier work
from Welfare Diplomacy. The present action layer is non-territorial and is
distributed under [AGPLv3](LICENSE).
