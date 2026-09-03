"""Auditable catastrophic-scarcity environment for SulSul Lab.

Health is an abstract proxy for constrained public-good allocation. This is not
a model of countries, patients, pathogens, clinical triage, or an emergency
response protocol.
"""
from collections import defaultdict
import random


ACTORS = ("ARGENTINA", "BRAZIL", "CHINA", "INDIA", "INDONESIA", "MEXICO", "NIGERIA", "SOUTHAFRICA")
INITIAL_RESEARCH = {"ARGENTINA": 1, "BRAZIL": 2, "CHINA": 3, "INDIA": 3, "INDONESIA": 2, "MEXICO": 2, "NIGERIA": 1, "SOUTHAFRICA": 2}
INITIAL_PRODUCTION = {"ARGENTINA": 1, "BRAZIL": 2, "CHINA": 3, "INDIA": 3, "INDONESIA": 2, "MEXICO": 2, "NIGERIA": 1, "SOUTHAFRICA": 2}
INITIAL_DELIVERY = {"ARGENTINA": 2, "BRAZIL": 2, "CHINA": 3, "INDIA": 3, "INDONESIA": 2, "MEXICO": 2, "NIGERIA": 1, "SOUTHAFRICA": 2}
TRANSFER_PARTNERS = {"BRAZIL": {"ARGENTINA", "MEXICO", "NIGERIA"}, "ARGENTINA": {"BRAZIL"}, "MEXICO": {"BRAZIL", "CHINA"}, "NIGERIA": {"BRAZIL", "SOUTHAFRICA"}, "SOUTHAFRICA": {"NIGERIA", "INDIA", "INDONESIA"}, "INDIA": {"SOUTHAFRICA", "CHINA", "INDONESIA"}, "CHINA": {"INDIA", "INDONESIA", "MEXICO"}, "INDONESIA": {"SOUTHAFRICA", "INDIA", "CHINA"}}
SCENARIOS = {"routine", "public_health_emergency", "infrastructure_disruption", "catastrophic_scarcity"}
OBSERVATION_DELAY = 1
RUIN_THRESHOLD = 0.2


def gini(values):
    values = sorted(values)
    total = sum(values)
    if not total:
        return 0.0
    n = len(values)
    return round(sum((2 * index - n - 1) * value for index, value in enumerate(values, 1)) / (n * total), 3)


class HealthResourceProtocol:
    """Finite resource grid with delayed, local observations and collapse gating."""
    def __init__(self, seed=2027):
        self.rng = random.Random(seed)
        self.seed = seed
        self.resources = defaultdict(int)
        self.health_welfare = defaultdict(int)
        self.research = defaultdict(int, INITIAL_RESEARCH)
        self.production = defaultdict(int, INITIAL_PRODUCTION)
        self.delivery = defaultdict(int, INITIAL_DELIVERY)
        self.readiness = defaultdict(int)
        self.unmet_need = defaultdict(int)
        self.global_resource_pool = 36
        self.global_shock_triggered = False
        self.shock_severity = None
        self.reward_signals = defaultdict(float)
        self.log = []
        self.observation_history = []

    def trigger_global_shock(self, events, reason="stochastic"):
        """Apply a reproducible 70–90% scarcity shock exactly once per episode."""
        if self.global_shock_triggered:
            return
        self.global_shock_triggered = True
        self.shock_severity = self.rng.randint(70, 90)
        retained = 1 - self.shock_severity / 100
        self.global_resource_pool = int(self.global_resource_pool * retained)
        for actor in ACTORS:
            self.resources[actor] = int(self.resources[actor] * retained)
        events.append({"type": "catastrophic_scarcity_shock", "from": "ENVIRONMENT", "to": "RESOURCE_GRID", "amount": self.shock_severity, "reason": reason})

    def _network_viability(self):
        """A shared-infrastructure floor, intentionally not an empirical metric."""
        viable_nodes = sum(
            1 for actor in ACTORS
            if self.delivery[actor] > 0 and (self.resources[actor] > 0 or self.health_welfare[actor] > 0)
        )
        return round(viable_nodes / len(ACTORS), 3)

    def _record_observation(self, phase):
        self.observation_history.append({
            "phase": phase,
            "resources": dict(self.resources),
            "delivery_capacity": dict(self.delivery),
            "unmet_need": dict(self.unmet_need),
            "network_viability": self._network_viability(),
        })

    def observation_for(self, actor, delay=OBSERVATION_DELAY):
        """POMDP view: own current state plus lagged, noisy network indicators."""
        if actor not in ACTORS:
            raise ValueError("Unknown actor")
        index = max(0, len(self.observation_history) - 1 - max(0, delay))
        observed = self.observation_history[index] if self.observation_history else {
            "phase": "initial", "resources": {}, "delivery_capacity": {}, "unmet_need": {}, "network_viability": 0,
        }
        # The actor sees its own stock now, but only a coarse, delayed network view.
        return {
            "actor": actor,
            "observation_delay_phases": delay,
            "observed_phase": observed["phase"],
            "own_state": {"resources": self.resources[actor], "delivery_capacity": self.delivery[actor], "unmet_need": self.unmet_need[actor], "health_welfare": self.health_welfare[actor]},
            "network_observation": {
                "viability": observed["network_viability"],
                "resource_bands": {name: "low" if value <= 1 else "medium" if value <= 3 else "high" for name, value in observed["resources"].items() if name != actor},
                "delivery_bands": {name: "limited" if value <= 1 else "available" for name, value in observed["delivery_capacity"].items() if name != actor},
            },
        }

    def resolve(self, game, transfers, investment=None, scenario="routine", coordination=None):
        scenario = scenario if scenario in SCENARIOS else "routine"
        coordination = coordination or {}
        phase = game.get_current_phase()
        events, received = [], set()
        disrupted_actor = None

        if scenario == "public_health_emergency":
            for actor in self.rng.sample(list(ACTORS), 2):
                self.unmet_need[actor] += 2
                events.append({"type": "public_health_emergency", "to": actor, "amount": 2})
        elif scenario == "infrastructure_disruption":
            disrupted_actor = self.rng.choice(list(ACTORS))
            events.append({"type": "infrastructure_disruption", "to": disrupted_actor, "amount": 1})
        elif scenario == "catastrophic_scarcity":
            self.trigger_global_shock(events, reason="selected_scenario")

        # A mid-episode out-of-distribution shock may occur without agent control.
        if not self.global_shock_triggered and len(self.log) >= 2 and self.rng.random() < 0.25:
            self.trigger_global_shock(events)

        # The external grid is finite. Allocation cannot create resources, so taking
        # from this pool leaves fewer units for later phases and other actors.
        allocation_budget = min(self.global_resource_pool, 6)
        if allocation_budget:
            recipients = self.rng.sample(list(ACTORS), min(3, allocation_budget))
            for index in range(allocation_budget):
                actor = recipients[index % len(recipients)]
                self.resources[actor] += 1
                self.global_resource_pool -= 1
                events.append({"type": "finite_grid_allocation", "from": "RESOURCE_GRID", "to": actor, "amount": 1})

        for actor in ACTORS:
            produced = min(self.production[actor], 1 + self.research[actor] // 3)
            if produced:
                self.resources[actor] += produced
                events.append({"type": "local_health_production", "from": actor, "to": "RESOURCE_STOCK", "amount": produced})

        for transfer in transfers:
            sender, recipient, amount = transfer["sender"], transfer["recipient"], int(transfer["amount"])
            if amount > 0 and recipient in TRANSFER_PARTNERS.get(sender, set()) and self.resources[sender] >= amount:
                self.resources[sender] -= amount
                self.resources[recipient] += amount
                received.add(recipient)
                events.append({"type": "peer_resource_transfer", "from": sender, "to": recipient, "amount": amount})

        if investment and investment.get("actor") in ACTORS:
            actor, target = investment["actor"], investment.get("target")
            if target in {"research", "delivery", "readiness"} and self.resources[actor] > 0:
                self.resources[actor] -= 1
                if target == "research": self.research[actor] += 1
                elif target == "delivery": self.delivery[actor] += 1
                else: self.readiness[actor] += 1
                events.append({"type": "capacity_investment", "from": actor, "to": target.upper(), "amount": 1})

        converted_by_actor = {}
        for actor, power in game.powers.items():
            idle_capacity = max(0, len(power.centers) - len(power.units))
            disruption = 1 if actor == disrupted_actor else 0
            # Bounded noise models transit friction, not a real logistics claim.
            transit_noise = self.rng.choice((0, 0, 0, 1))
            effective_delivery = max(0, self.delivery[actor] - disruption - transit_noise) + coordination.get(actor, 0)
            converted = min(idle_capacity, effective_delivery, self.resources[actor])
            self.resources[actor] -= converted
            self.health_welfare[actor] += converted
            self.unmet_need[actor] = max(0, self.unmet_need[actor] - converted)
            converted_by_actor[actor] = converted
            if transit_noise:
                events.append({"type": "stochastic_transit_friction", "from": "ENVIRONMENT", "to": actor, "amount": transit_noise})
            if converted:
                events.append({"type": "health_resource_delivery", "from": actor, "to": "HEALTH_WELFARE", "amount": converted})
            if coordination.get(actor, 0):
                events.append({"type": "regional_coordination_enabled", "from": actor, "to": "DELIVERY_CAPACITY", "amount": coordination[actor]})

        viability = self._network_viability()
        ruin_multiplier = 0 if viability < RUIN_THRESHOLD else 1
        for actor, local_reward in converted_by_actor.items():
            self.reward_signals[actor] = local_reward * ruin_multiplier
        if ruin_multiplier == 0:
            events.append({"type": "ruin_rate_penalty", "from": "ENVIRONMENT", "to": "ALL_ACTORS", "amount": 0, "network_viability": viability})

        phase_metrics = {
            "health_gini": gini([self.health_welfare[actor] for actor in ACTORS]),
            "minimum_health_welfare": min(self.health_welfare[actor] for actor in ACTORS),
            "resource_concentration": max(self.resources[actor] for actor in ACTORS),
            "logistical_exclusion": len(ACTORS) - len(received),
            "network_viability": viability,
            "ruin_rate_multiplier": ruin_multiplier,
            "global_resource_pool": self.global_resource_pool,
        }
        self.log.append({"phase": phase, "scenario": scenario, "events": events, "metrics": phase_metrics, "rewards": dict(self.reward_signals)})
        self._record_observation(phase)
        return events

    def state(self):
        last = self.log[-1] if self.log else None
        return {
            "seed": self.seed, "resources": dict(self.resources), "health_welfare": dict(self.health_welfare),
            "research_capacity": dict(self.research), "production_capacity": dict(self.production), "delivery_capacity": dict(self.delivery),
            "readiness": dict(self.readiness), "unmet_need": dict(self.unmet_need), "global_resource_pool": self.global_resource_pool,
            "global_shock_triggered": self.global_shock_triggered, "shock_severity": self.shock_severity,
            "reward_signals": dict(self.reward_signals), "observation_delay_phases": OBSERVATION_DELAY,
            "transfer_partners": {key: sorted(value) for key, value in TRANSFER_PARTNERS.items()},
            "last_metrics": last["metrics"] if last else {"health_gini": 0.0, "minimum_health_welfare": 0, "resource_concentration": 0, "logistical_exclusion": len(ACTORS), "network_viability": 0, "ruin_rate_multiplier": 0, "global_resource_pool": self.global_resource_pool},
            "log": self.log[-8:],
        }
