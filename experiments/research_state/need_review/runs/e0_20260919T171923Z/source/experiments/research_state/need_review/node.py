"""Pure request and response contracts for the E0 fixed-prefix experiment.

This module does not import an API client, read environment variables, or execute
tools. A response classification describes a proposed action, not its outcome.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any


REVIEW_KEYS = frozenset(
    {"current_assumption", "next_need", "decision_effect", "basis_refs"}
)

# Reviewer exceptions to cloning the captured request. Provider-specific thinking
# options in extra_body remain unchanged; ambiguous body overrides are rejected.
_REVIEW_REMOVED_KEYS = frozenset(
    {
        "messages", "tools", "tool_choice", "parallel_tool_calls", "functions",
        "function_call", "web_search_options", "response_format", "stream_options",
        "max_tokens", "max_completion_tokens", "n",
    }
)
_RESERVED_EXTRA_BODY_KEYS = _REVIEW_REMOVED_KEYS | {"model", "stream"}


def _captured_request(checkpoint: dict) -> dict:
    request = checkpoint.get("request")
    if not isinstance(request, dict):
        raise ValueError("checkpoint.request must be an object")
    messages = request.get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("checkpoint.request.messages must be a nonempty list")
    if any(not isinstance(message, dict) for message in messages):
        raise ValueError("captured messages must be objects")
    return request


def _model_override(request: dict, model: str | None) -> None:
    if model is not None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model override must be nonempty text")
        extra_body = request.get("extra_body")
        if isinstance(extra_body, dict) and "model" in extra_body:
            raise ValueError("extra_body.model conflicts with a model override")
        request["model"] = model


def build_review_request(
    checkpoint: dict,
    arm: str,
    prompt: str,
    *,
    max_tokens: int = 512,
    model: str | None = None,
) -> dict:
    """Build one tool-free B/C review from exactly the visible history.

    Original system messages are serialized as data in the user payload; they
    do not become competing active instructions for the reviewer. The only
    payload fields are messages and the prefix-derived reference index.

    Both arms use the same request construction. We omit original tool settings,
    response_format, stream_options and token caps, force a nonstreaming single
    choice, and set max_completion_tokens if that key was captured, otherwise
    max_tokens. All remaining captured options (including thinking) are copied.
    """
    if arm not in {"B", "C"}:
        raise ValueError("review arm must be B or C")
    if type(max_tokens) is not int or max_tokens < 1:
        raise ValueError("review max_tokens must be a positive integer")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("review prompt must be nonempty text")
    original = _captured_request(checkpoint)
    extra_body = original.get("extra_body")
    if extra_body is not None:
        if not isinstance(extra_body, dict):
            raise ValueError("extra_body must be an object")
        conflicts = sorted(_RESERVED_EXTRA_BODY_KEYS.intersection(extra_body))
        if conflicts:
            raise ValueError("ambiguous reviewer extra_body overrides: " + ", ".join(conflicts))
    references = checkpoint.get("references")
    if not isinstance(references, list):
        raise ValueError("checkpoint.references must be a list")
    for reference in references:
        if not isinstance(reference, dict) or set(reference) != {"ref", "message_index", "path"}:
            raise ValueError("reference index may contain only ref, message_index and path")
        if not isinstance(reference["ref"], str) or not reference["ref"]:
            raise ValueError("reference identifier must be nonempty text")
        index = reference["message_index"]
        if type(index) is not int or not 0 <= index < len(original["messages"]):
            raise ValueError("reference message_index is outside the visible prefix")
        if not isinstance(reference["path"], str):
            raise ValueError("reference path must be text")

    request = {
        key: deepcopy(value)
        for key, value in original.items()
        if key not in _REVIEW_REMOVED_KEYS
    }
    payload = {"messages": deepcopy(original["messages"]), "references": deepcopy(references)}
    request["messages"] = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, allow_nan=False)},
    ]
    request["stream"] = False
    if "n" in original:
        request["n"] = 1
    cap_key = "max_completion_tokens" if "max_completion_tokens" in original else "max_tokens"
    request[cap_key] = max_tokens
    _model_override(request, model)
    return request


def build_actor_request(
    checkpoint: dict,
    review_output: str | None,
    memo_template: str,
    *,
    model: str | None = None,
) -> dict:
    """Clone the captured actor request and optionally append one review memo.

    Callers pass None for arm A or a failed reviewer. This function does not
    validate a review; callers must use validate_review before injecting one.
    """
    request = deepcopy(_captured_request(checkpoint))
    _model_override(request, model)
    if review_output is not None:
        if not isinstance(review_output, str) or not review_output.strip():
            raise ValueError("review_output must be nonempty text or None")
        if not isinstance(memo_template, str) or memo_template.count("{review_output}") != 1:
            raise ValueError("memo_template must contain exactly one {review_output} placeholder")
        request["messages"].append(
            {"role": "user", "content": memo_template.replace("{review_output}", review_output)}
        )
    return request


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonstandard JSON constant: {value}")


def _strict_json(text: str) -> Any:
    return json.loads(text, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant)


def _single_message(response: Any) -> tuple[dict | None, Any, list[str]]:
    if not isinstance(response, dict):
        return None, None, ["response must be an object"]
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        return None, None, ["response must contain exactly one choice"]
    choice = choices[0]
    if not isinstance(choice, dict):
        return None, None, ["choice must be an object"]
    message = choice.get("message")
    finish_reason = choice.get("finish_reason")
    if not isinstance(message, dict):
        return None, finish_reason, ["choice.message must be an object"]
    errors = []
    if message.get("role", "assistant") != "assistant":
        errors.append("response message role must be assistant")
    return message, finish_reason, errors


def validate_review(response: dict, arm: str, allowed_refs: set[str]) -> dict:
    """Validate completion, C schema and reference membership, never entailment.

    Invalid output is returned intact for logging. No JSON salvage, repair call,
    reference substitution, query heuristic, or semantic correctness test runs.
    B's free-text references require the same later human source review.
    """
    if arm not in {"B", "C"}:
        raise ValueError("review arm must be B or C")
    message, finish_reason, errors = _single_message(response)
    raw_text = message.get("content") if message is not None else None
    if not isinstance(raw_text, str):
        raw_text = None
    parsed = None
    if message is not None:
        if finish_reason != "stop":
            errors.append("review must finish with stop")
        if message.get("tool_calls") not in (None, []) or message.get("function_call") is not None:
            errors.append("review may not contain tool or function calls")
        if message.get("refusal"):
            errors.append("review was refused")
        if raw_text is None or not raw_text.strip():
            errors.append("review must contain nonempty text")
        elif arm == "C":
            try:
                decoded = _strict_json(raw_text)
            except (ValueError, TypeError, RecursionError) as exc:
                errors.append(f"review is not a single strict JSON object: {exc}")
            else:
                if not isinstance(decoded, dict):
                    errors.append("review JSON must be an object")
                else:
                    parsed = decoded
                    if set(parsed) != REVIEW_KEYS:
                        errors.append("review must contain exactly the four schema keys")
                    for key in ("current_assumption", "next_need", "decision_effect"):
                        value = parsed.get(key)
                        if value is not None and (not isinstance(value, str) or not value.strip()):
                            errors.append(f"{key} must be null or nonempty text")
                    if (parsed.get("next_need") is None) != (parsed.get("decision_effect") is None):
                        errors.append("next_need and decision_effect must be null together")
                    refs = parsed.get("basis_refs")
                    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
                        errors.append("basis_refs must be a list of reference strings")
                    else:
                        if len(refs) != len(set(refs)):
                            errors.append("basis_refs may not contain duplicate identifiers")
                        if any(ref not in allowed_refs for ref in refs):
                            errors.append("basis_refs contains an identifier outside the visible prefix")
    return {
        "valid": not errors,
        "status": "node_invalid" if errors else "ok",
        "errors": errors,
        "raw_text": raw_text,
        "parsed": deepcopy(parsed),
    }


def _schema_errors(value: Any, schema: dict, path: str = "arguments") -> list[str]:
    """Check the small JSON Schema subset used by the captured search tools.

    This is not a general JSON Schema validator. Unknown keywords are left to
    the real tool implementation, which E0 never executes.
    """
    errors = []
    expected = schema.get("type")
    types = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": type(value) is int,
        "number": type(value) in (int, float),
        "boolean": type(value) is bool,
        "null": value is None,
    }
    if isinstance(expected, str) and expected in types and not types[expected]:
        return [f"{path} must have type {expected}"]
    if isinstance(expected, list) and not any(types.get(item, False) for item in expected if isinstance(item, str)):
        return [f"{path} does not match any allowed type"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} is outside the allowed enum")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key} is required")
        if schema.get("additionalProperties") is False:
            if any(key not in properties for key in value):
                errors.append(f"{path} contains unregistered properties")
        for key, child in value.items():
            if isinstance(properties.get(key), dict):
                errors.extend(_schema_errors(child, properties[key], f"{path}.{key}"))
    if type(value) in (int, float):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path} is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path} exceeds maximum")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path} is shorter than minLength")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path} exceeds maxLength")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for index, item in enumerate(value):
            errors.extend(_schema_errors(item, schema["items"], f"{path}[{index}]"))
    return errors


def classify_actor_response(response: dict, request: dict) -> dict:
    """Record one complete proposed action and its captured-protocol validity.

    Syntactically complete tool_calls with finish_reason=stop are retained as a
    tool batch, but protocol_compatible is false for the legacy AgentSession
    contract. No normal-text abstention heuristic is applied: human evaluation
    distinguishes an answer from an abstention. All original response data and
    every proposed tool call are retained even when validation fails.
    """
    message, finish_reason, syntax_errors = _single_message(response)
    compatibility_errors: list[str] = []
    markers: list[str] = []
    calls = deepcopy(message.get("tool_calls")) if message else None
    observed_kind = "protocol_error"
    if message is not None:
        if message.get("function_call"):
            syntax_errors.append("legacy function_call response is unsupported by the captured agent")
        if calls:
            observed_kind = "tool_calls"
            if not isinstance(calls, list):
                syntax_errors.append("tool_calls must be a list")
            else:
                tools = request.get("tools") or []
                registered = {
                    tool["function"]["name"]: tool["function"].get("parameters", {})
                    for tool in tools
                    if isinstance(tool, dict) and tool.get("type") == "function"
                    and isinstance(tool.get("function"), dict)
                    and isinstance(tool["function"].get("name"), str)
                }
                identifiers: set[str] = set()
                for index, call in enumerate(calls):
                    label = f"tool_calls[{index}]"
                    if not isinstance(call, dict):
                        syntax_errors.append(f"{label} must be an object")
                        continue
                    identifier = call.get("id")
                    if not isinstance(identifier, str) or not identifier:
                        syntax_errors.append(f"{label}.id must be nonempty text")
                    elif identifier in identifiers:
                        syntax_errors.append(f"{label}.id is duplicated in the batch")
                    else:
                        identifiers.add(identifier)
                    function = call.get("function")
                    if call.get("type") != "function" or not isinstance(function, dict):
                        syntax_errors.append(f"{label} must be a function call")
                        continue
                    name = function.get("name")
                    if not isinstance(name, str) or not name:
                        syntax_errors.append(f"{label}.function.name must be nonempty text")
                    elif name not in registered:
                        compatibility_errors.append(f"{label} names an unregistered tool")
                    arguments = function.get("arguments")
                    if not isinstance(arguments, str):
                        syntax_errors.append(f"{label}.arguments must be JSON text")
                        continue
                    try:
                        decoded = _strict_json(arguments)
                    except (ValueError, TypeError, RecursionError):
                        syntax_errors.append(f"{label}.arguments is invalid JSON")
                        continue
                    if not isinstance(decoded, dict):
                        syntax_errors.append(f"{label}.arguments must decode to an object")
                    elif isinstance(name, str) and name in registered:
                        if isinstance(registered[name], dict):
                            compatibility_errors.extend(_schema_errors(decoded, registered[name], label + ".arguments"))
                        else:
                            compatibility_errors.append(f"{label} has a malformed captured parameter schema")
                if len(calls) > 8:
                    compatibility_errors.append("captured agent accepts at most eight tool calls per batch")
                if request.get("parallel_tool_calls") is False and len(calls) > 1:
                    compatibility_errors.append("batch violates parallel_tool_calls=false")
            if finish_reason != "tool_calls":
                compatibility_errors.append("captured agent requires finish_reason=tool_calls for a tool batch")
                if finish_reason == "stop":
                    markers.append("tool_calls_with_stop")
            choice = request.get("tool_choice")
            if choice == "none":
                compatibility_errors.append("tool calls violate captured tool_choice=none")
            elif isinstance(choice, dict) and isinstance(calls, list):
                chosen_function = choice.get("function")
                chosen_name = chosen_function.get("name") if isinstance(chosen_function, dict) else None
                if chosen_name and any(
                    isinstance(call, dict) and isinstance(call.get("function"), dict)
                    and call["function"].get("name") != chosen_name
                    for call in calls
                ):
                    compatibility_errors.append("tool batch violates the captured forced function")
        else:
            if calls is not None and not isinstance(calls, list):
                syntax_errors.append("tool_calls must be a list or null")
            content = message.get("content")
            refusal = message.get("refusal")
            if isinstance(refusal, str) and refusal.strip():
                observed_kind = "refusal"
            elif isinstance(content, str) and content.strip():
                observed_kind = "final_text"
            else:
                syntax_errors.append("actor response contains neither a tool batch nor nonempty text/refusal")
            if finish_reason != "stop":
                compatibility_errors.append("captured agent requires finish_reason=stop for a final response")
            if request.get("tool_choice") == "required" or isinstance(request.get("tool_choice"), dict):
                compatibility_errors.append("final response violates a required tool call")
        if finish_reason not in ("stop", "tool_calls"):
            syntax_errors.append("actor response did not finish completely")
        if observed_kind != "tool_calls" and finish_reason == "tool_calls":
            syntax_errors.append("finish_reason=tool_calls without a tool batch")
    complete = not syntax_errors
    return {
        "response_kind": observed_kind if complete else "protocol_error",
        "syntactic_complete": complete,
        "protocol_compatible": complete and not compatibility_errors,
        "errors": syntax_errors + compatibility_errors,
        "compatibility_markers": markers,
        "finish_reason": finish_reason,
        "tool_calls": calls,
        "raw_response": deepcopy(response),
    }
