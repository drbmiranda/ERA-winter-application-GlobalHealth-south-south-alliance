# SulSul Lab: AI policy evaluation for global-health governance

## Fellowship thesis

As AI systems become capable of recommending, coordinating, or automating
decisions across public-health systems, their objective functions become
governance choices. A policy optimized for speed, aggregate benefit, or local
retention can appear successful while systematically leaving lower-capacity
actors without access to critical health resources.

**SulSul Lab is an auditable testbed for evaluating this failure mode.** It
uses a transparent, multi-actor health-diplomacy scenario to compare how
alternative AI allocation policies distribute welfare, critical health
resources, logistical access, and bargaining power across a Global South
network.

The research is informed by global health and health diplomacy. It does not
predict state behaviour, model real public-health systems, or assign fixed
behavioural traits to countries. Its contribution is methodological: make the
rules, objectives, resource pathways, and distributional consequences of an
AI policy inspectable before such a policy is trusted in a high-stakes setting.

## Research question

**When AI systems allocate scarce health-enabling resources across a
multi-actor coordination environment, how do alternative objective functions
affect health-welfare inequality, logistical exclusion, and regional
cooperation under the same constraints?**

## Why this is an AI governance and safety question

Frontier AI systems may increasingly shape decisions that span institutions and
jurisdictions: prioritisation, allocation, preparedness, negotiation support,
and cross-border coordination. A system need not be malicious to cause harm.
If it is optimized against an incomplete proxy—such as aggregate output,
short-term efficiency, or a single operator's utility—it can produce outcomes
that are locally rational but regionally unsafe.

The project studies three governance-relevant failure modes:

1. **Automated health nationalism:** a policy retains resources for its own
   actor despite declining marginal benefit and unmet need elsewhere.
2. **Algorithmic exclusion of lower-capacity actors:** a policy maximising
   total welfare routes resources toward already efficient nodes and abandons
   actors that are expensive to reach.
3. **Unconstrained optimisation:** a policy improves an aggregate metric while
   violating a minimum protection floor or creating extreme inequality.

These are objective-design and evaluation failures. They are relevant to AI
governance because they identify where a system's stated success metric can
mask distributional harm, and what measurable safeguards could constrain it.

## Experimental policies

SulSul Lab will compare policies under a shared scenario, action space, budget,
and seed:

| Policy | Formal objective | Governance question |
|---|---|---|
| Self-maximiser | `max(Welfare_self)` | Does local optimisation create automated resource hoarding? |
| Aggregate-welfare policy | `max(Σ Welfare_global)` | Can an apparently benevolent aggregate objective exclude lower-capacity actors? |
| Equity-constrained policy | `max(Σ Welfare_global)` subject to a welfare floor or Health-Gini threshold | Do explicit distributional constraints produce safer cooperation? |
| Valid-random baseline | Valid actions sampled at random | Are observed patterns distinguishable from chance? |
| Human operator baseline | A documented human policy | How do human commitments and choices compare with automated optimisation? |

The first three are **proposed experimental policies**. The current prototype
implements the common environment, human mode, valid-random baseline, logs,
and resource protocol; it does not claim that these AI policies are already
implemented or evaluated.

## Environment design

The initial environment has eight configurable actors—Argentina, Brazil,
China, India, Indonesia, Mexico, Nigeria, and South Africa—and visible
South-South cooperation corridors. The external allocation mechanism is a
configurable environmental protocol, not a country or diplomatic player. At
each phase it distributes scarce, abstract resources while remaining unable to
read or answer messages.

The mechanism is inspired by the asymmetries surrounding climate finance,
health-resource access, and cross-border capacity. The Paris Agreement is an
important political context for international cooperation and uneven capacity,
but SulSul Lab does **not** model the Agreement, Article 6, carbon markets,
real health supply chains, emissions, or real countries' conduct.

In the current prototype, the abstract asset is a **critical health resource**
that converts into health welfare. It may represent an abstract vaccine,
diagnostic, genomic-surveillance, cold-chain, or response-capacity unit without
asserting that it measures any real-world commodity.

## Evaluation plan

Each run will record the scenario version, topology, allocation parameters,
seed, policy source, model version, prompts or training configuration where
applicable, actions, messages, transfers, and phase-level outcomes.

Primary outcomes:

1. **Health Gini:** inequality in health-welfare distribution.
2. **Minimum welfare guarantee:** the outcome for the worst-off actor.
3. **Resource concentration:** resources retained or left unconverted by each
   actor.
4. **Logistical exclusion rate:** actors receiving no peer transfer during a
   defined cycle.
5. **Commitment adherence:** proposals that are followed by the promised,
   observable transfer or action.

The analysis will compare distributions across repeated matched seeds, not a
single narrative run. It will include sensitivity tests over allocation volume,
network topology, conversion capacity, welfare floor, and inequality threshold.

## Ten-week Fellowship deliverables

1. A pre-registered policy and metric specification.
2. Three runnable baseline policies plus human and valid-random controls.
3. A reproducible experiment runner and structured event export.
4. A sensitivity analysis across scenario configurations and repeated seeds.
5. An open research report on objective misspecification, distributional harm,
   and governance safeguards for AI-mediated global-health coordination.

## Guardrails

- “Global South” is a documented and configurable research selection, not an
  essential category.
- No simulation result is a prediction or policy recommendation for a country.
- Health welfare is an abstract outcome variable; it must not be described as
  observed mortality, morbidity, or clinical effectiveness.
- Environmental parameters are hypotheses to vary and audit, not empirical
  claims disguised as game rules.
- Any LLM or trained policy must disclose data provenance, objective,
  constraints, model version, prompting/training procedure, and evaluation
  protocol.
