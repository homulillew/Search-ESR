"""Extract an immutable, already-visible E0 request without reading its future.

This module is deliberately independent of the Agent, retrieval stack, and SDK.
Reference ``path`` values are JSON pointers into a decoded tool message's
``content``; the question's empty path addresses its complete string content.
Hashes provide reproducibility/integrity checks, not signatures of provenance.
The preparation command separately verifies the source file against its pinned
Git blob before calling this extractor.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any


SCHEMA_VERSION = "need_review_checkpoint_v1"
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT = re.compile(r"[0-9a-f]{40}\Z")
_SENSITIVE_KEYS = {
    "api_key", "apikey", "authorization", "access_token", "refresh_token",
    "client_secret", "password", "cookie", "cookies", "headers",
    "extra_headers", "x_api_key", "proxy_authorization", "base_url",
    "api_base", "http_client", "client", "proxy", "proxies",
}


class CheckpointError(ValueError):
    """The selected source or prepared artifact violates the E0 contract."""


def canonical_json(value: Any) -> str:
    """Return the stable JSON representation used by all E0 content hashes."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CheckpointError("duplicate JSON object key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise CheckpointError("non-finite JSON number")


def _json(text: str) -> Any:
    try:
        return json.loads(text, object_pairs_hook=_object, parse_constant=_constant)
    except (TypeError, json.JSONDecodeError) as exc:
        raise CheckpointError("invalid JSON") from exc


def _positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise CheckpointError(f"{field} must be a positive integer")
    return value


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CheckpointError(f"{field} must be a nonempty string")
    return value


def _reject_sensitive_options(request: dict[str, Any]) -> None:
    # Message bodies and tool descriptions are task data, not SDK options.
    # Refuse credential/transport overrides instead of mutating the Actor input.
    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if str(key).lower().replace("-", "_") in _SENSITIVE_KEYS:
                    raise CheckpointError("request contains a credential or transport option")
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit({key: value for key, value in request.items()
           if key not in {"messages", "tools", "functions"}})


def _inspect_request(request: Any) -> tuple[int, list[dict[str, Any]]]:
    """Validate completed tool batches and return the actual tool observations."""
    if not isinstance(request, dict):
        raise CheckpointError("request must be an object")
    _reject_sensitive_options(request)
    _nonempty(request.get("model"), "model")
    if request.get("stream") is not False:
        raise CheckpointError("checkpoint request must explicitly have stream=false")
    messages = request.get("messages")
    if not isinstance(messages, list) or not messages:
        raise CheckpointError("request messages must be a nonempty list")

    question_index: int | None = None
    pending: dict[str, str] = {}
    seen_ids: set[str] = set()
    observations: list[dict[str, Any]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            raise CheckpointError("each message must be an object")
        role = message.get("role")
        if role not in {"system", "developer", "user", "assistant", "tool"}:
            raise CheckpointError("unsupported message role")
        if pending and role != "tool":
            raise CheckpointError("incomplete tool batch before the next message")
        if role == "user" and question_index is None:
            _nonempty(message.get("content"), "original question content")
            question_index = index
        if message.get("function_call") is not None:
            raise CheckpointError("legacy function_call messages are not supported")
        calls = message.get("tool_calls")
        if calls:
            if role != "assistant" or not isinstance(calls, list):
                raise CheckpointError("tool_calls must belong to an assistant message")
            if question_index is None:
                raise CheckpointError("tool calls precede the original question")
            for call in calls:
                if not isinstance(call, dict) or call.get("type") != "function":
                    raise CheckpointError("unsupported tool call shape")
                call_id = _nonempty(call.get("id"), "tool call id")
                function = call.get("function")
                if not isinstance(function, dict):
                    raise CheckpointError("tool call function must be an object")
                name = _nonempty(function.get("name"), "tool function name")
                if not isinstance(function.get("arguments"), str):
                    raise CheckpointError("tool function arguments must be a string")
                if call_id in seen_ids:
                    raise CheckpointError("duplicate tool call id")
                seen_ids.add(call_id)
                pending[call_id] = name
        elif calls is not None and not isinstance(calls, list):
            raise CheckpointError("tool_calls must be a list")
        if role == "tool":
            call_id = message.get("tool_call_id")
            if not isinstance(call_id, str) or call_id not in pending:
                raise CheckpointError("orphan or duplicate tool response")
            name = pending.pop(call_id)
            if message.get("name", name) != name:
                raise CheckpointError("tool response name differs from its call")
            content = message.get("content")
            if not isinstance(content, str):
                raise CheckpointError("tool response content must be a JSON string")
            observations.append({"message_index": index, "name": name,
                                 "result": _json(content)})
    if question_index is None:
        raise CheckpointError("original question is missing")
    if pending:
        raise CheckpointError("checkpoint ends with an incomplete tool batch")
    if not observations or messages[-1].get("role") != "tool":
        raise CheckpointError("E0 checkpoint must follow a completed tool batch")
    return question_index, observations


def _pointer(parent: str, key: str | int) -> str:
    return parent + "/" + str(key).replace("~", "~0").replace("/", "~1")


def _references(question_index: int, observations: list[dict[str, Any]],
                tool_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = [{"ref": "question", "message_index": question_index, "path": ""}]

    def walk(value: Any, path: str, message_index: int, seq: int) -> None:
        if isinstance(value, dict):
            # Read identifiers only from the actual returned document/window
            # object. Identifiers in assistant prose, parent_window_ref, logs'
            # hidden metadata, or a JSON-looking source string grant no access.
            if isinstance(value.get("text"), str):
                window_ref = value.get("window_ref")
                docid = value.get("docid")
                if isinstance(window_ref, str) and window_ref.strip():
                    ref = window_ref
                elif (isinstance(docid, (str, int)) and not isinstance(docid, bool)
                      and str(docid).strip()):
                    ref = f"event:{seq}:doc:{docid}"
                else:
                    ref = None
                if ref is not None:
                    references.append({"ref": ref, "message_index": message_index,
                                       "path": path})
            for key, child in value.items():
                walk(child, _pointer(path, key), message_index, seq)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, _pointer(path, index), message_index, seq)

    for observation, event in zip(observations, tool_events):
        walk(observation["result"], "", observation["message_index"], event["event_seq"])
    return references


def extract_checkpoint(events_path: Path, request_seq: int, *, checkpoint_id: str,
                       source_commit: str, tool_version: str,
                       parent_run: str | None = None) -> dict[str, Any]:
    """Read JSONL through one request and extract only that request's history.

    No event after the selected request is decoded or inspected here; the prefix
    hash ends at that request's line (a file buffer may read ahead internally).
    Prior tool_result records are used only to match the already-visible tool
    messages, by execution order, tool name, and exact decoded JSON content.
    """
    _positive_integer(request_seq, "request_seq")
    path = Path(events_path)
    prefix_hash = hashlib.sha256()
    prior_tool_results: list[dict[str, Any]] = []
    request: dict[str, Any] | None = None
    previous_seq = 0
    with path.open("rb") as stream:
        for line in stream:
            prefix_hash.update(line)
            try:
                event = _json(line.decode("utf-8"))
            except UnicodeDecodeError as exc:
                raise CheckpointError("source prefix is not UTF-8") from exc
            if not isinstance(event, dict):
                raise CheckpointError("event must be an object")
            seq = _positive_integer(event.get("seq"), "event seq")
            if seq != previous_seq + 1:
                raise CheckpointError("source event sequence must be contiguous from 1")
            previous_seq = seq
            if seq == request_seq:
                if event.get("kind") != "api_request":
                    raise CheckpointError("selected event is not an api_request")
                request = event.get("request")
                break
            if event.get("kind") == "tool_result":
                if "result" not in event:
                    raise CheckpointError("tool_result event has no result")
                prior_tool_results.append({"event_seq": seq, "name": event.get("name"),
                                           "result": event["result"]})
    if request is None:
        raise CheckpointError("selected api_request was not found or has no request")

    question_index, observations = _inspect_request(request)
    if len(observations) != len(prior_tool_results):
        raise CheckpointError("visible tool messages do not match recorded tool results")
    tool_events = []
    for observation, event in zip(observations, prior_tool_results):
        if (observation["name"] != event["name"]
                or canonical_json(observation["result"]) != canonical_json(event["result"])):
            raise CheckpointError("visible tool message differs from recorded result/order")
        tool_events.append({"message_index": observation["message_index"],
                            "event_seq": event["event_seq"], "name": event["name"],
                            "result_sha256": digest(observation["result"])})
    checkpoint = {
        "schema_version": SCHEMA_VERSION,
        "checkpoint_id": checkpoint_id,
        "source": {"events_path": str(path), "parent_run": parent_run,
                   "source_commit": source_commit, "tool_version": tool_version,
                   "request_seq": request_seq, "prefix_sha256": prefix_hash.hexdigest(),
                   "tool_events": tool_events},
        "request": deepcopy(request),
        "request_sha256": digest(request),
        "references": _references(question_index, observations, tool_events),
    }
    checkpoint["checkpoint_sha256"] = digest(checkpoint)
    return validate_checkpoint(checkpoint)


def validate_checkpoint(checkpoint: Any) -> dict[str, Any]:
    """Validate a self-contained prepared artifact and return an independent copy.

    This never reads the source trajectory. Event sequence provenance relies on
    extraction from the pinned source; reference membership is rebuilt from the
    exact request so an edited reference list cannot silently expand visibility.
    """
    if not isinstance(checkpoint, dict) or checkpoint.get("schema_version") != SCHEMA_VERSION:
        raise CheckpointError("unsupported checkpoint schema")
    _nonempty(checkpoint.get("checkpoint_id"), "checkpoint_id")
    expected = checkpoint.get("checkpoint_sha256")
    if not isinstance(expected, str) or not _SHA256.fullmatch(expected):
        raise CheckpointError("checkpoint_sha256 is missing or malformed")
    try:
        actual = digest({key: value for key, value in checkpoint.items()
                         if key != "checkpoint_sha256"})
    except (TypeError, ValueError, UnicodeError) as exc:
        raise CheckpointError("checkpoint is not canonical JSON data") from exc
    if actual != expected:
        raise CheckpointError("checkpoint_sha256 mismatch")

    source = checkpoint.get("source")
    if not isinstance(source, dict):
        raise CheckpointError("checkpoint source must be an object")
    _nonempty(source.get("events_path"), "source events_path")
    _nonempty(source.get("tool_version"), "tool_version")
    if source.get("parent_run") is not None:
        _nonempty(source["parent_run"], "parent_run")
    if not isinstance(source.get("source_commit"), str) or not _COMMIT.fullmatch(source["source_commit"]):
        raise CheckpointError("source_commit must be a full lowercase Git commit SHA")
    request_seq = _positive_integer(source.get("request_seq"), "request_seq")
    if not isinstance(source.get("prefix_sha256"), str) or not _SHA256.fullmatch(source["prefix_sha256"]):
        raise CheckpointError("prefix_sha256 is missing or malformed")
    request = checkpoint.get("request")
    question_index, observations = _inspect_request(request)
    if checkpoint.get("request_sha256") != digest(request):
        raise CheckpointError("request_sha256 mismatch")

    tool_events = source.get("tool_events")
    if not isinstance(tool_events, list) or len(tool_events) != len(observations):
        raise CheckpointError("source tool_events must cover exactly the visible tool messages")
    previous_seq = 0
    for observation, event in zip(observations, tool_events):
        if not isinstance(event, dict) or set(event) != {
                "message_index", "event_seq", "name", "result_sha256"}:
            raise CheckpointError("invalid tool event metadata")
        event_seq = _positive_integer(event["event_seq"], "tool event seq")
        if not previous_seq < event_seq < request_seq:
            raise CheckpointError("tool event is out of order or beyond the selected request")
        previous_seq = event_seq
        if (type(event["message_index"]) is not int
                or event["message_index"] != observation["message_index"]
                or event["name"] != observation["name"]
                or event["result_sha256"] != digest(observation["result"])):
            raise CheckpointError("tool event metadata differs from visible content")
    if checkpoint.get("references") != _references(question_index, observations, tool_events):
        raise CheckpointError("reference index differs from actual visible observations")
    return deepcopy(checkpoint)


def load_checkpoint(path: Path) -> dict[str, Any]:
    """Load a prepared JSON artifact; its original events file is unnecessary."""
    return validate_checkpoint(_json(Path(path).read_text(encoding="utf-8")))
