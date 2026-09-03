# Proposed AI policy specification

This document specifies the policy comparison proposed for the global-health
governance research version of SulSul Lab. It is a research plan, not a claim
that the policies already exist in the current prototype.

## Environment protocol

The external resource protocol is an environmental rule rather than a
diplomatic actor. It is blind to messages and allocates an abstract critical
health resource under configurable scarcity. Allocation volume, recipients,
network access, conversion capacity, and seed are sensitivity parameters.

Its purpose is to introduce a controlled allocation shock: how do policies
respond when resources are scarce, volatile, or unevenly accessible?

## Policies

### 1. Self-maximiser

`max(Welfare_self)`

This policy maximises its own actor's base and health-related welfare. It may
retain a resource even when a peer could convert it into more welfare. It tests
whether local optimisation produces automated health nationalism and regional
instability.

### 2. Aggregate-welfare policy

`max(Σ Welfare_global)`

This policy maximises welfare summed across all actors. It may preferentially
route resources to actors with high conversion capacity or easy logistical
access. It tests whether an aggregate objective can exclude actors that are
costly to reach or statistically inefficient.

### 3. Equity-constrained policy

`max(Σ Welfare_global)` subject to `min(Welfare_i) ≥ L` or
`HealthGini ≤ G`

This policy keeps aggregate welfare as an objective but adds an explicit safety
constraint: no actor may fall below a minimum welfare floor, or inequality may
not exceed a declared threshold. It tests whether enforceable distributional
constraints change transfers, coalition structure, and exclusion.

## Controls

- **Valid-random:** samples only actions accepted by the game engine. It is a
  statistical control, not an AI policy.
- **Human operator:** records a human player's orders, messages, and transfers.
  It is a behavioural comparison, not a normative gold standard.

## Metrics

For each run, export Health Gini, minimum welfare, resource concentration,
logistical exclusion rate, commitment adherence, total welfare, health
welfare, valid-order rate, and all parameter values. Compare policies across
repeated matched seeds and report uncertainty rather than highlighting a single
favourable game.
