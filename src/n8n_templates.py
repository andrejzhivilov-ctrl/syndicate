"""
n8n workflow templates for Floor 1 (all core nodes, FlowLint-compliant).

* sensory_switch  — Telegram trigger -> allow-list -> dedup -> Switch -> HTTP branches
* error_handler   — global Error Trigger -> /webhook/error (ErrorCollector)
* cron_briefing   — 07:30 morning briefing
* cron_evening    — 21:00 evening reflection

Secrets are never inlined: the Eva API key lives in an n8n credential ("Eva API", HTTP
Header Auth), never in a node. n8n 2.x blocks ``$env`` inside nodes, so the API base is a
fixed in-network URL.
"""

from __future__ import annotations

from typing import Any, Dict, List

ERROR_WORKFLOW_NAME = "syndicate_error_handler"
EVA_API_BASE = "http://eva-agent:8000"  # in-network; n8n 2.x blocks $env inside nodes
EVA_CREDENTIAL_NAME = "Eva API"  # n8n HTTP Header Auth credential holding X-API-Key
_HEADERS = {"parameters": [{"name": "Content-Type", "value": "application/json"}]}

_ALLOW_CODE = (
    "const allowed = ($env.ALLOWED_CHAT_IDS || '').split(',').map(s => s.trim()).filter(Boolean);\n"
    "const msg = $json.message || $json.edited_message || {};\n"
    "const chat = String((msg.chat || {}).id || '');\n"
    "if (!allowed.includes(chat)) { return []; }\n"
    "return [{ json: $json }];"
)
_DEDUP_CODE = (
    "const store = $getWorkflowStaticData('global');\n"
    "store.seen = store.seen || {};\n"
    "const id = String($json.update_id);\n"
    "if (store.seen[id]) { return []; }\n"
    "store.seen[id] = Date.now();\n"
    "const keys = Object.keys(store.seen);\n"
    "if (keys.length > 2000) { keys.sort((a,b)=>store.seen[a]-store.seen[b]).slice(0, 500).forEach(k => delete store.seen[k]); }\n"
    "return [{ json: $json }];"
)


def _node(name: str, ntype: str, version: float, pos: List[int], params: Dict[str, Any], **extra: Any) -> Dict[str, Any]:
    node = {"id": name.lower().replace(" ", "-"), "name": name, "type": ntype,
            "typeVersion": version, "position": pos, "parameters": params}
    node.update(extra)
    return node


def _http(name: str, path: str, pos: List[int], body: str = "={{ JSON.stringify($json) }}") -> Dict[str, Any]:
    return _node(
        name, "n8n-nodes-base.httpRequest", 4, pos,
        {
            "method": "POST",
            "url": f"{EVA_API_BASE}{path}",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True,
            "headerParameters": _HEADERS,
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": body,
            "options": {"timeout": 60000},
        },
        credentials={"httpHeaderAuth": {"name": EVA_CREDENTIAL_NAME}},
        continueOnFail=True,
        retryOnFail=True,
        maxTries=3,
    )


def bind_credential(workflow: Dict[str, Any], credential_id: str) -> Dict[str, Any]:
    """Point every Eva API node at the n8n credential created on the live instance."""
    for node in workflow["nodes"]:
        entry = (node.get("credentials") or {}).get("httpHeaderAuth")
        if entry is not None:
            entry["id"] = str(credential_id)
    return workflow


def build_sensory_switch() -> Dict[str, Any]:
    nodes = [
        _node("Telegram Trigger", "n8n-nodes-base.telegramTrigger", 1, [0, 300],
              {"updates": ["message", "edited_message"]}),
        _node("Allow List", "n8n-nodes-base.code", 2, [220, 300], {"jsCode": _ALLOW_CODE}),
        _node("Idempotency Guard", "n8n-nodes-base.code", 2, [440, 300], {"jsCode": _DEDUP_CODE}),
        _node("Sensory Switch", "n8n-nodes-base.switch", 3, [660, 300], {
            "rules": {"values": [
                {"outputKey": "voice", "conditions": {"conditions": [{"leftValue": "={{ $json.message.voice ? 'y' : '' }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "y"}]}},
                {"outputKey": "audio", "conditions": {"conditions": [{"leftValue": "={{ $json.message.audio ? 'y' : '' }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "y"}]}},
                {"outputKey": "photo", "conditions": {"conditions": [{"leftValue": "={{ $json.message.photo ? 'y' : '' }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "y"}]}},
                {"outputKey": "document", "conditions": {"conditions": [{"leftValue": "={{ $json.message.document ? 'y' : '' }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "y"}]}},
                {"outputKey": "text", "conditions": {"conditions": [{"leftValue": "={{ $json.message.text ? 'y' : '' }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "y"}]}},
            ]},
        }),
        _http("Voice -> STT", "/sensory/stt", [900, 100]),
        _http("Audio -> Split+STT", "/sensory/audio_split", [900, 220]),
        _http("Photo -> OCR", "/sensory/ocr", [900, 340]),
        _http("Document -> Extract", "/sensory/extract", [900, 460]),
        _http("Text -> Orchestrator", "/sensory/text", [900, 580]),
    ]
    names = [n["name"] for n in nodes]
    connections: Dict[str, Any] = {
        "Telegram Trigger": {"main": [[{"node": "Allow List", "type": "main", "index": 0}]]},
        "Allow List": {"main": [[{"node": "Idempotency Guard", "type": "main", "index": 0}]]},
        "Idempotency Guard": {"main": [[{"node": "Sensory Switch", "type": "main", "index": 0}]]},
        "Sensory Switch": {"main": [
            [{"node": "Voice -> STT", "type": "main", "index": 0}],
            [{"node": "Audio -> Split+STT", "type": "main", "index": 0}],
            [{"node": "Photo -> OCR", "type": "main", "index": 0}],
            [{"node": "Document -> Extract", "type": "main", "index": 0}],
            [{"node": "Text -> Orchestrator", "type": "main", "index": 0}],
        ]},
    }
    assert all(n in names for n in connections)
    return {
        "name": "syndicate_sensory_switch",
        "nodes": nodes,
        "connections": connections,
        "settings": {"errorWorkflow": ERROR_WORKFLOW_NAME, "executionOrder": "v1"},
        "active": False,
    }


def build_error_handler() -> Dict[str, Any]:
    nodes = [
        _node("Error Trigger", "n8n-nodes-base.errorTrigger", 1, [0, 200], {}),
        _node("Normalize", "n8n-nodes-base.code", 2, [220, 200], {"jsCode": (
            "const e = $json;\n"
            "return [{ json: { source: 'n8n', node: (e.execution||{}).lastNodeExecuted || '', "
            "error_message: ((e.execution||{}).error||{}).message || 'unknown', "
            "payload_sample: JSON.stringify(e.workflow||{}).slice(0, 300), severity: 'error' } }];"
        )}),
        _http("Report To Collector", "/webhook/error", [440, 200]),
    ]
    connections = {
        "Error Trigger": {"main": [[{"node": "Normalize", "type": "main", "index": 0}]]},
        "Normalize": {"main": [[{"node": "Report To Collector", "type": "main", "index": 0}]]},
    }
    return {"name": ERROR_WORKFLOW_NAME, "nodes": nodes, "connections": connections,
            "settings": {"executionOrder": "v1"}, "active": False}


def _cron(name: str, cron: str, task_path: str) -> Dict[str, Any]:
    nodes = [
        _node("Schedule", "n8n-nodes-base.scheduleTrigger", 1.2, [0, 200],
              {"rule": {"interval": [{"field": "cronExpression", "expression": cron}]}}),
        _http("Run Task", task_path, [260, 200], body="={{ JSON.stringify({ source: 'cron' }) }}"),
    ]
    return {
        "name": name,
        "nodes": nodes,
        "connections": {"Schedule": {"main": [[{"node": "Run Task", "type": "main", "index": 0}]]}},
        "settings": {"errorWorkflow": ERROR_WORKFLOW_NAME, "executionOrder": "v1", "timezone": "Europe/Kyiv"},
        "active": False,
    }


def build_cron_briefing() -> Dict[str, Any]:
    return _cron("syndicate_morning_briefing", "30 7 * * *", "/proactive/morning")


def build_cron_evening() -> Dict[str, Any]:
    return _cron("syndicate_evening_reflection", "0 21 * * *", "/proactive/evening")


def all_templates() -> Dict[str, Dict[str, Any]]:
    return {
        "sensory_switch": build_sensory_switch(),
        "error_handler": build_error_handler(),
        "cron_briefing": build_cron_briefing(),
        "cron_evening": build_cron_evening(),
    }


# Aliases
build_sensory_switch_workflow = build_sensory_switch
build_error_handler_workflow = build_error_handler
build_cron_briefing_workflow = build_cron_briefing
build_evening_reflection_workflow = build_cron_evening
