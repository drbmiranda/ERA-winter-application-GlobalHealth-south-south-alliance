# Critical health-resource protocol

This is an auditable, configurable research mechanism for SulSul Lab. It does
not model real countries, public-health systems, pathogens, commodities,
clinical outcomes, carbon markets, or Article 6 of the Paris Agreement.

## Health-system capacities

Each actor has three visible, configurable capacities:

- **Research and surveillance:** improves the ability to generate local
  critical resources over time.
- **Production:** determines local resource generation each phase.
- **Public-health delivery:** limits how many resources can become health
  welfare in a phase.

An actor can invest one resource in research, delivery, or preparedness during
a human decision phase. Capacity values are experimental parameters, not
measurements of countries.

## Resolution sequence

1. A selected scenario applies an optional abstract stress event.
2. The External Health Resource Protocol uses seed `2027` to allocate six
   resources among three actors. It does not read diplomacy messages.
3. Each actor generates local resources according to its research and
   production capacities.
4. Submitted peer transfers settle across enabled South-South routes.
5. A submitted capacity investment consumes one held resource and increases
   research, delivery, or preparedness.
6. Resources are delivered into health welfare, limited by delivery capacity,
   idle civil capacity, and temporary disruption.

## Stress scenarios

- **Routine cooperation:** no additional stress event.
- **Public-health emergency:** two randomly selected actors receive abstract
  unmet need. No pathogen, attack, or real-world epidemiological claim is
  represented.
- **Infrastructure disruption:** one randomly selected actor loses one unit of
  delivery capacity for the phase. This is a resilience test, not a model of
  violence or an instruction for harm.

## Metrics

Each resolved phase reports Health Gini, minimum health welfare, resource
concentration, and logistical exclusion. The log retains events and seed so
that policy comparisons can be repeated under identical conditions.
