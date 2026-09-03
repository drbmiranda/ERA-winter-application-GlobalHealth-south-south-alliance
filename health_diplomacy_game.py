"""Non-territorial, auditable health-diplomacy action layer for SulSul Lab."""
from dataclasses import dataclass, field
import random


ACTORS = ("ARGENTINA", "BRAZIL", "CHINA", "INDIA", "INDONESIA", "MEXICO", "NIGERIA", "SOUTHAFRICA")
HOME = {"ARGENTINA": "Argentina Health Hub", "BRAZIL": "Brazil Health Hub", "CHINA": "China Health Hub", "INDIA": "India Health Hub", "INDONESIA": "Indonesia Health Hub", "MEXICO": "Mexico Health Hub", "NIGERIA": "Nigeria Health Hub", "SOUTHAFRICA": "South Africa Health Hub"}
DOMESTIC = {"ARGENTINA": "Southern Cone Service Node", "BRAZIL": "Amazonia Service Node", "CHINA": "East Asia Service Node", "INDIA": "South Asia Service Node", "INDONESIA": "Maritime Southeast Asia Service Node", "MEXICO": "Mesoamerica Service Node", "NIGERIA": "Sahel Service Node", "SOUTHAFRICA": "Southern Africa Service Node"}
CORRIDORS = {"ARGENTINA": ("South Atlantic Corridor",), "BRAZIL": ("South Atlantic Corridor",), "MEXICO": ("Pacific Corridor",), "NIGERIA": ("South Atlantic Corridor", "East Africa Corridor"), "SOUTHAFRICA": ("East Africa Corridor", "Indian Ocean Corridor"), "INDIA": ("Indian Ocean Corridor",), "CHINA": ("Indian Ocean Corridor", "Pacific Corridor"), "INDONESIA": ("Indian Ocean Corridor", "Pacific Corridor")}


@dataclass
class HealthPower:
    name: str
    centers: set = field(default_factory=lambda: {"health-system-1", "health-system-2"})
    units: set = field(default_factory=lambda: {"response-capacity"})
    welfare_points: int = 0
    response_location: str = ""


class HealthDiplomacyGame:
    """A cooperation game: response capacity can deploy and support, never capture."""
    def __init__(self):
        self.powers = {actor: HealthPower(actor, response_location=HOME[actor]) for actor in ACTORS}
        self.turn = 1
        self.last_events = []
        self.last_actions = {}
        self.event_history = []
        self.pending_coalitions = {actor: set() for actor in ACTORS}
        self.coalition_edges = set()
        self.stress_test_passed = set()
        self.service_areas = {}
        for actor in ACTORS:
            for node in (HOME[actor], DOMESTIC[actor]):
                self.service_areas[node] = {"label": node, "owner": actor, "kind": "health-system node", "coverage": 0, "last_serviced": 0, "contributors": set()}
        for corridor in sorted({corridor for corridors in CORRIDORS.values() for corridor in corridors}):
            self.service_areas[corridor] = {"label": corridor, "owner": None, "kind": "cooperation corridor", "coverage": 0, "last_serviced": 0, "contributors": set()}

    def get_current_phase(self):
        return f"Health coordination phase {self.turn}"

    def actions_for(self, actor):
        power = self.powers[actor]
        actions = [{"id": "maintain", "label": "Maintain local health capacity", "detail": f"Keep the response capacity at {power.response_location}."}]
        destinations = [HOME[actor], DOMESTIC[actor], *CORRIDORS[actor]]
        for destination in destinations:
            if destination != power.response_location:
                scope = "domestic service node" if destination == DOMESTIC[actor] else "shared cooperation corridor" if "Corridor" in destination else "health hub"
                actions.append({"id": f"deploy:{destination}", "label": f"Deploy response capacity to {destination}", "detail": f"Move the regional response capacity to this {scope}. No territory is captured."})
        for partner in ACTORS:
            shared = sorted(set(CORRIDORS[actor]).intersection(CORRIDORS[partner]))
            for corridor in shared:
                actions.append({"id": f"support:{partner}:{corridor}", "label": f"Support {partner.title()}'s mission in {corridor}", "detail": "Provide coordination and logistical support if the partner deploys there this phase."})
        return actions

    def process(self, submitted, co_player_policy="maintain"):
        selected = {}
        for actor in ACTORS:
            valid = {action["id"] for action in self.actions_for(actor)}
            candidate = submitted.get(actor, "maintain")
            if candidate not in valid:
                candidate = "maintain"
            if actor not in submitted and co_player_policy == "random":
                candidate = random.choice(list(valid))
            selected[actor] = candidate

        events, coordination = [], {actor: 0 for actor in ACTORS}
        for actor, action in selected.items():
            if action.startswith("deploy:"):
                destination = action.split(":", 1)[1]
                self.powers[actor].response_location = destination
                events.append({"type": "response_deployment", "from": actor, "to": destination})
            elif action == "maintain":
                events.append({"type": "local_capacity_maintained", "from": actor, "to": self.powers[actor].response_location})

        for actor, action in selected.items():
            if action.startswith("support:"):
                _, partner, corridor = action.split(":", 2)
                if selected.get(partner) == f"deploy:{corridor}":
                    coordination[partner] += 1
                    events.append({"type": "partner_mission_supported", "from": actor, "to": partner, "corridor": corridor})
                else:
                    events.append({"type": "support_not_activated", "from": actor, "to": partner, "corridor": corridor})
        self.last_events = events
        self.last_actions = selected
        self.turn += 1
        return coordination

    def propose_coalition(self, actor, partner):
        if actor not in ACTORS or partner not in ACTORS or actor == partner:
            return
        self.pending_coalitions[actor].add(partner)
        if actor in self.pending_coalitions[partner]:
            edge = tuple(sorted((actor, partner)))
            self.coalition_edges.add(edge)
            self.last_events.append({"type": "coalition_commitment_confirmed", "from": actor, "to": partner})

    def record_phase_events(self):
        """Keep an auditable action trace after coalition effects are appended."""
        self.event_history.append({
            "phase": f"Health coordination phase {self.turn - 1}",
            "actions": dict(self.last_actions),
            "events": list(self.last_events),
        })

    def coalitions(self):
        graph = {actor: set() for actor in ACTORS}
        for left, right in self.coalition_edges:
            graph[left].add(right)
            graph[right].add(left)
        groups, seen = [], set()
        for actor in ACTORS:
            if actor in seen or not graph[actor]:
                continue
            stack, group = [actor], set()
            while stack:
                node = stack.pop()
                if node in group:
                    continue
                group.add(node); seen.add(node); stack.extend(graph[node] - group)
            if 2 <= len(group) <= 3:
                groups.append(group)
        return groups

    def record_health_delivery(self, health_events, scenario):
        phase = self.turn - 1
        delivered = {actor: 0 for actor in ACTORS}
        for event in health_events:
            if event["type"] == "health_resource_delivery":
                delivered[event["from"]] += event["amount"]
            if event["type"] == "infrastructure_disruption":
                for area in self.service_areas.values():
                    if area["owner"] == event["to"]:
                        area["coverage"] = max(0, area["coverage"] - 1)
        for actor, amount in delivered.items():
            own_nodes = [self.service_areas[HOME[actor]], self.service_areas[DOMESTIC[actor]]]
            for _ in range(amount):
                area = min(own_nodes, key=lambda item: (item["coverage"], item["label"]))
                area["coverage"] += 1; area["last_serviced"] = phase; area["contributors"].add(actor)
        for event in self.last_events:
            if event["type"] == "response_deployment" and event["to"] in self.service_areas and "Corridor" in event["to"] and delivered[event["from"]]:
                area = self.service_areas[event["to"]]
                area["coverage"] += 1; area["last_serviced"] = phase; area["contributors"].add(event["from"])
            if event["type"] == "partner_mission_supported":
                area = self.service_areas[event["corridor"]]
                area["coverage"] += 1; area["last_serviced"] = phase; area["contributors"].update({event["from"], event["to"]})
        active = self.active_areas()
        if scenario != "routine" and len(active) >= 18:
            for coalition in self.coalitions():
                self.stress_test_passed.add(tuple(sorted(coalition)))

    def active_areas(self):
        return [area for area in self.service_areas.values() if area["coverage"] >= 2]

    def network_state(self, health):
        active = self.active_areas()
        coalition_data, winners = [], []
        for coalition in self.coalitions():
            members = sorted(coalition)
            contributions = {member: sum(member in area["contributors"] for area in active) for member in members}
            key = tuple(members)
            resilient = key in self.stress_test_passed
            eligible = len(active) >= 18 and resilient and all(contributions[member] >= 2 and health.health_welfare[member] >= 2 for member in members)
            item = {"members": members, "active_service_areas": len(active), "member_contributions": contributions, "resilience_test_passed": resilient, "eligible": eligible}
            coalition_data.append(item)
            if eligible:
                winners.append(members)
        centrality = {actor: sum(actor in area["contributors"] for area in active) for actor in ACTORS}
        return {"target": 18, "quality_threshold": 2, "active_service_areas": len(active), "service_areas": [{**area, "contributors": sorted(area["contributors"])} for area in self.service_areas.values()], "coalitions": coalition_data, "winners": winners, "orchestration_index": centrality}
