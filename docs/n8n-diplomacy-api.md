# Real-time diplomacy API

This local prototype serves a phase-bound JSON API for the SulSul Lab
diplomacy panel. It is intended as an integration surface for agent workflows,
including n8n, while preserving an auditable record of what an agent saw and
when it answered.

## Read the current context

`GET /api/diplomacy/context/{ACTOR}` returns the current phase, proposals that
the actor sent or can receive, valid missions, its delayed partial observation,
and the coalition network. It deliberately does not return the full resource
state available to the research auditor dashboard. Use it immediately before
every LLM invocation.

```text
GET /api/diplomacy/context/BRAZIL
```

For a broader history, use:

```text
GET /api/messages?phase=Health%20coordination%20phase%203&recipient=BRAZIL&since=0
```

`since` is an exclusive message id cursor. The response always includes the
server `version` and current `phase`.

## Write an agent proposal

`POST /api/agents/messages` (or `POST /api/messages`) accepts JSON:

```json
{
  "sender": "BRAZIL",
  "recipient": "INDIA",
  "message": "Brazil can share a cold-chain protocol if India coordinates an Indian Ocean delivery.",
  "phase": "Health coordination phase 3",
  "agent_id": "n8n-brazil-equity-policy-v1",
  "correlation_id": "run-2026-09-03-brazil-p3",
  "metadata": {
    "policy": "equity_constrained",
    "model": "example-model"
  }
}
```

The `phase` field is mandatory. A response arriving after resolution receives
`409 Conflict`, with the current phase in the body; n8n must discard it, fetch
fresh context and make a new decision. This prevents a delayed LLM response
from being recorded as if it were made in the next round.

Successful writes return `201 Created` with a monotonically increasing message
id and UTC timestamp. If `SULSUL_API_KEY` is set on the Flask process, provide
the same value in `X-API-Key` on all agent API calls.

## Live dashboard updates

`GET /api/stream` is a Server-Sent Events endpoint. Every message or resolved
phase increments the server version and broadcasts a `state` event. The web
dashboard reconnects automatically and refreshes `/api/state` without caching.

## Current prototype boundary

Messages and simulation state are intentionally process-memory only at this
stage. The SSE flow is correct for one local Flask process, but it is not a
durable research data store and cannot be shared across multiple workers. No
Supabase project, database credentials, Postgres trigger, or Supabase Realtime
subscription exists in this repository.

Before a hosted multi-agent study, persist `simulation_runs`,
`diplomatic_messages`, and `mission_events` in Postgres/Supabase; insert only
through a server-side service key; enable Realtime for the message/event tables;
and retain `phase`, `agent_id`, `correlation_id`, `metadata`, timestamp and
server version as audit fields. Do not expose a Supabase service key to the
browser.
