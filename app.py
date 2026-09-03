"""Local, auditable health-diplomacy simulation API for SulSul Lab.

The API deliberately keeps the simulation local for the prototype. It exposes
an SSE state stream and phase-bound JSON resources so a human UI and an agent
orchestrator can observe the same phase without relying on browser refreshes.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading

from flask import Flask, Response, jsonify, request, send_from_directory, stream_with_context

from health_diplomacy_game import HealthDiplomacyGame
from health_resource_protocol import HealthResourceProtocol


ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT))
game = HealthDiplomacyGame()
health = HealthResourceProtocol()
messages = []
message_sequence = 0
state_version = 0
state_lock = threading.RLock()
state_changed = threading.Condition(state_lock)


def _publish():
    """Notify every connected dashboard after one atomic state change."""
    global state_version
    state_version += 1
    state_changed.notify_all()


def _snapshot_unlocked():
    return {
        "version": state_version,
        "phase": game.get_current_phase(),
        "powers": [{
            "name": name, "health_system_nodes": len(power.centers),
            "response_capacity": len(power.units), "response_location": power.response_location,
            "welfare": power.welfare_points, "health_welfare": health.health_welfare[name],
            "health_resources": health.resources[name], "research_capacity": health.research[name],
            "production_capacity": health.production[name], "delivery_capacity": health.delivery[name],
            "unmet_need": health.unmet_need[name],
        } for name, power in game.powers.items()],
        "messages": messages[-80:],
        "health_protocol": health.state(),
        "mission_events": game.last_events,
        "mission_history": game.event_history[-40:],
        "network": game.network_state(health),
    }


def snapshot():
    with state_lock:
        return _snapshot_unlocked()


def _require_agent_key():
    """Optional server-to-server guard; leave unset only for local prototype work."""
    expected = os.environ.get("SULSUL_API_KEY")
    if expected and request.headers.get("X-API-Key") != expected:
        return jsonify({"error": "Invalid or missing X-API-Key."}), 401
    return None


def _phase_mismatch(expected_phase):
    current = game.get_current_phase()
    if expected_phase != current:
        return jsonify({
            "error": "Stale phase. Reload the current diplomatic context before writing.",
            "current_phase": current,
            "expected_phase": expected_phase,
        }), 409
    return None


@app.after_request
def no_store_api(response):
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")


@app.get("/visual/<path:filename>")
def visual(filename):
    return send_from_directory(ROOT / "visual", filename)


@app.get("/api/state")
def state():
    return jsonify(snapshot())


@app.get("/api/stream")
def stream():
    """Server-Sent Events: lightweight real-time delivery for every dashboard."""
    try:
        observed_version = int(request.args.get("since", "0"))
    except ValueError:
        observed_version = 0

    @stream_with_context
    def events():
        nonlocal observed_version
        yield "retry: 2000\n\n"
        while True:
            with state_changed:
                state_changed.wait_for(lambda: state_version != observed_version, timeout=20)
                observed_version = state_version
                payload = {"version": state_version, "phase": game.get_current_phase()}
            yield f"event: state\ndata: {json.dumps(payload)}\n\n"

    return Response(events(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    })


@app.get("/api/actions/<actor>")
def actions(actor):
    with state_lock:
        if actor not in game.powers:
            return jsonify({"error": "Unknown actor"}), 404
        return jsonify({"actor": actor, "phase": game.get_current_phase(), "actions": game.actions_for(actor)})


@app.get("/api/messages")
def get_messages():
    """Read phase-scoped diplomatic history; designed for n8n agent context."""
    denied = _require_agent_key()
    if denied:
        return denied
    phase_filter = request.args.get("phase")
    recipient_filter = request.args.get("recipient")
    try:
        since = int(request.args.get("since", "0"))
    except ValueError:
        return jsonify({"error": "since must be an integer."}), 400
    with state_lock:
        selected = [item for item in messages if item["id"] > since]
        if phase_filter:
            selected = [item for item in selected if item["phase"] == phase_filter]
        if recipient_filter:
            selected = [item for item in selected if item["recipient"] in (recipient_filter, "GLOBAL") or item["sender"] == recipient_filter]
        return jsonify({"version": state_version, "phase": game.get_current_phase(), "messages": selected})


@app.get("/api/diplomacy/context/<actor>")
def diplomacy_context(actor):
    """One-call context for an LLM: phase, relevant proposals and valid actions."""
    denied = _require_agent_key()
    if denied:
        return denied
    with state_lock:
        if actor not in game.powers:
            return jsonify({"error": "Unknown actor"}), 404
        current_phase = game.get_current_phase()
        relevant = [item for item in messages if item["phase"] == current_phase and (item["sender"] == actor or item["recipient"] in (actor, "GLOBAL"))]
        return jsonify({
            "version": state_version,
            "actor": actor,
            "phase": current_phase,
            "messages": relevant,
            "actions": game.actions_for(actor),
            "observation": health.observation_for(actor),
            "network": game.network_state(health),
        })


def validated_transfers(raw):
    transfers = []
    for transfer in raw if isinstance(raw, list) else []:
        if not isinstance(transfer, dict):
            continue
        try:
            amount = int(transfer.get("amount", 0))
        except (TypeError, ValueError):
            continue
        sender, recipient = transfer.get("sender"), transfer.get("recipient")
        if sender in game.powers and recipient in game.powers and amount > 0:
            transfers.append({"sender": sender, "recipient": recipient, "amount": amount})
    return transfers


@app.post("/api/advance-human")
def advance_human():
    data = request.get_json(silent=True) or {}
    with state_changed:
        policy = data.get("_co_player_policy", "maintain")
        actor = data.get("_actor")
        action = data.get("_action", "maintain")
        if actor not in game.powers:
            return jsonify({"error": "Choose a valid actor."}), 400
        coordination = game.process({actor: action}, "random" if policy == "random" else "maintain")
        game.propose_coalition(actor, data.get("_coalition_partner"))
        investment = {"actor": actor, "target": data.get("_health_investment")} if data.get("_health_investment") else None
        scenario = data.get("_health_scenario", "routine")
        health_events = health.resolve(game, validated_transfers(data.get("_health_transfers", [])), investment=investment, scenario=scenario, coordination=coordination)
        game.record_health_delivery(health_events, scenario)
        game.record_phase_events()
        _publish()
        return jsonify(_snapshot_unlocked())


def _record_message(data):
    global message_sequence
    sender, recipient = data.get("sender"), data.get("recipient")
    text = (data.get("message") or "").strip()
    expected_phase = data.get("phase")
    if sender not in game.powers or (recipient not in game.powers and recipient != "GLOBAL") or not text:
        return None, (jsonify({"error": "Provide a valid sender, recipient, and message."}), 400)
    if not isinstance(expected_phase, str) or not expected_phase:
        return None, (jsonify({"error": "phase is required so proposals cannot be written into the wrong round."}), 400)
    mismatch = _phase_mismatch(expected_phase)
    if mismatch:
        return None, mismatch
    if len(text) > 4000:
        return None, (jsonify({"error": "message may not exceed 4000 characters."}), 400)
    message_sequence += 1
    item = {
        "id": message_sequence,
        "sender": sender, "recipient": recipient, "message": text, "phase": expected_phase,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "agent_id": data.get("agent_id"), "correlation_id": data.get("correlation_id"),
        "metadata": data.get("metadata") if isinstance(data.get("metadata"), dict) else {},
    }
    messages.append(item)
    return item, None


@app.post("/api/messages")
@app.post("/api/agents/messages")
def send_message():
    denied = _require_agent_key()
    if denied:
        return denied
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "JSON object body required."}), 400
    with state_changed:
        item, error = _record_message(data)
        if error:
            return error
        _publish()
        return jsonify({"message": item, "version": state_version, "phase": game.get_current_phase()}), 201


@app.post("/api/advance-random")
def advance_random():
    with state_changed:
        coordination = game.process({}, "random")
        health_events = health.resolve(game, [], scenario="routine", coordination=coordination)
        game.record_health_delivery(health_events, "routine")
        game.record_phase_events()
        _publish()
        return jsonify(_snapshot_unlocked())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4180, debug=False, threaded=True)
