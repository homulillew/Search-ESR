"""Append-only Research Actor contract for G2v2.

This module never changes or calls the frozen G2 parser. It reuses the historical
tool argument schemas but makes the surrounding flat action wrapper explicit and
checks that Find/Open references exist before a two-action batch is executed.
"""
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    CONFIG,
    ROOT,
    SCHEMAS,
    TOP,
    client,
    digest,
    extract,
    now,
    read,
    write,
)


def _action_schemas():
    out = []
    for tool, args in SCHEMAS.items():
        out.append(
            {
                "type": "object",
                "properties": {"tool": {"const": tool}, **args["properties"]},
                "required": ["tool", *args.get("required", [])],
                "additionalProperties": False,
            }
        )
    return out


ACTOR_SCHEMA_V2 = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "decision": {"enum": ["stop", "act"]},
        "gap": {"type": "string"},
        "actions": {
            "type": "array",
            "maxItems": 2,
            "items": {"oneOf": _action_schemas()},
        },
    },
    "required": ["decision", "gap", "actions"],
    "additionalProperties": False,
    "allOf": [
        {
            "if": {"properties": {"decision": {"const": "stop"}}},
            "then": {
                "properties": {
                    "gap": {"const": ""},
                    "actions": {"maxItems": 0},
                }
            },
            "else": {
                "properties": {
                    "gap": {"minLength": 1},
                    "actions": {"minItems": 1},
                }
            },
        }
    ],
}
VALIDATOR_V2 = Draft202012Validator(ACTOR_SCHEMA_V2)


def _workspace_refs(workspace):
    docs = {
        x["doc_ref"]
        for x in workspace.get("known_documents", [])
        if isinstance(x, dict) and isinstance(x.get("doc_ref"), str)
    }
    windows = {
        x["window_ref"]
        for x in workspace.get("observed_windows", [])
        if isinstance(x, dict) and isinstance(x.get("window_ref"), str)
    }
    return docs, windows


def validate_actor_output_v2(value, workspace):
    errors = sorted(
        VALIDATOR_V2.iter_errors(value),
        key=lambda e: (list(e.absolute_path), e.message),
    )
    if errors:
        first = errors[0]
        path = ".".join(str(x) for x in first.absolute_path) or "<root>"
        raise ValueError(f"actor_contract_v2:{path}:{first.message}")

    if value["decision"] == "act":
        docs, windows = _workspace_refs(workspace)
        for action in value["actions"]:
            if action["tool"] == "find" and action["doc_ref"] not in docs:
                raise ValueError("actor_contract_v2:dependent_or_unknown_prebatch_document")
            if action["tool"] == "open" and action["window_ref"] not in windows:
                raise ValueError("actor_contract_v2:dependent_or_unknown_prebatch_window")
    return value


def request_workspace(item):
    messages = item["request"]["messages"]
    if len(messages) != 2 or messages[0].get("role") != "system" or messages[1].get("role") != "user":
        raise ValueError("actor_contract_v2:unexpected_request_messages")
    view = json.loads(messages[1]["content"])
    workspace = view.get("Available Workspace")
    if not isinstance(workspace, dict):
        raise ValueError("actor_contract_v2:missing_workspace")
    return workspace


def parse_actor_response_v2(raw, workspace):
    if raw["choices"][0]["finish_reason"] != "stop":
        raise ValueError("abnormal_finish")
    value = json.loads(raw["choices"][0]["message"]["content"])
    return validate_actor_output_v2(value, workspace)


def call_actor_v2(c, item):
    start = time.monotonic()
    event = {**item, "started_utc": now()}
    output = None
    error = None
    try:
        raw = c.chat.completions.create(**item["request"]).model_dump(mode="json")
        event["response"] = raw
        event["cache_usage"] = extract(raw)
        output = parse_actor_response_v2(raw, request_workspace(item))
    except Exception as exc:
        error = {
            "type": type(exc).__name__,
            "status": getattr(exc, "status_code", None),
            "message": str(exc)[:500],
        }
        event["error"] = error
    event["elapsed_seconds"] = time.monotonic() - start
    result = {k: item[k] for k in ("case_id", "qid", "arm", "kind", "request_sha256")}
    result.update(
        output=output,
        error=error,
        cache_usage=event.get("cache_usage"),
        usage=event.get("response", {}).get("usage"),
    )
    return event, result


def git_blob(path):
    return subprocess.check_output(
        ["git", "hash-object", str(path)],
        cwd=ROOT,
        text=True,
    ).strip()


def _assert_reuse_invariants(items):
    old = read(TOP / "research_decision/REQUESTS.json")
    if len(items) != len(old) or len(items) != 120:
        raise AssertionError("G2v2 must keep the frozen 120-cell denominator")
    new_prompt = (TOP / "prompts/research_actor_contract_v2.md").read_text()
    for before, after in zip(old, items):
        for key in ("case_id", "qid", "arm", "kind"):
            if before[key] != after[key]:
                raise AssertionError(f"G2v2 changed {key}")
        b_req, a_req = before["request"], after["request"]
        if b_req["model"] != a_req["model"] or b_req.get("stream") != a_req.get("stream"):
            raise AssertionError("G2v2 changed provider request settings")
        if b_req["messages"][1] != a_req["messages"][1]:
            raise AssertionError("G2v2 changed Actor user content")
        if a_req["messages"][0] != {"role": "system", "content": new_prompt}:
            raise AssertionError("G2v2 did not use the frozen v2 contract prompt")
        if digest(a_req) != after["request_sha256"]:
            raise AssertionError("G2v2 request hash mismatch")


def run_stage_v2(base=None):
    base = Path(base or (TOP / "research_decision_v2"))
    freeze = read(base / "freeze.json")
    items = read(base / "REQUESTS.json")
    _assert_reuse_invariants(items)

    if freeze["requests_blob_sha"] != git_blob(base / "REQUESTS.json"):
        raise AssertionError("G2v2 requests blob changed after freeze")
    for rel, expected in freeze["files_blob_sha"].items():
        path = ROOT / rel
        if git_blob(path) != expected:
            raise AssertionError(f"frozen file changed: {rel}")
    if freeze["tool_schema_sha256"] != read(TOP / "research_decision/freeze.json")["tool_schema_sha256"]:
        raise AssertionError("tool schema hash differs from frozen G2")

    events = base / "events.jsonl"
    outputs = base / "outputs.json"
    if events.exists() or outputs.exists():
        raise AssertionError("G2v2 is append-only and cannot be rerun in place")

    complete = {}
    with client() as c, events.open("w") as log:
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {}
            for item in items:
                log.write(
                    json.dumps(
                        {
                            "kind": "request_started",
                            "time": now(),
                            "case_id": item["case_id"],
                            "arm": item["arm"],
                            "request_sha256": item["request_sha256"],
                        }
                    )
                    + "\n"
                )
                log.flush()
                futures[pool.submit(call_actor_v2, c, item)] = item
            for future in as_completed(futures):
                event, result = future.result()
                complete[(result["case_id"], result["arm"])] = result
                log.write(
                    json.dumps(
                        {"kind": "completed", "event": event, "result": result},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                log.flush()
                print(
                    result["case_id"],
                    result["arm"],
                    "ok" if result["output"] is not None else result["error"]["type"],
                    flush=True,
                )

    ordered = [complete[(x["case_id"], x["arm"])] for x in items]
    write(outputs, ordered)
    valid = sum(x["output"] is not None for x in ordered)
    write(
        base / "CONTRACT_VALIDITY.json",
        {
            "planned": len(ordered),
            "valid": valid,
            "valid_rate": valid / len(ordered),
            "execution_integrity_gate": 0.80,
            "gate_pass": valid / len(ordered) >= 0.80,
            "old_g2_valid": 75,
            "old_g2_planned": 120,
        },
    )
    print("complete", len(ordered), "valid", valid, "gate", valid >= 96, flush=True)


if __name__ == "__main__":
    run_stage_v2(sys.argv[1] if len(sys.argv) > 1 else None)
