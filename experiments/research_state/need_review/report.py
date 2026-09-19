"""Export human review cards from an E0 run without invoking a model or tool.

Only the run's copied checkpoints, manifest and branch records are read.  The
original trajectory files (which also contain future observations) are never
opened.  Mechanical run status is reported separately from human judgments.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from .checkpoint import CheckpointError, digest, load_checkpoint
from .integrity import HARNESS_REVISION, read_events, strict_json, verify_plan
from .audit import recover_record, verify_branch_requests


_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_COMMON_VALUES = ["yes", "no", "unknown", "not_applicable"]
_LABEL_DESCRIPTIONS = {
    "review_source_attribution_correct": (
        "Does the review distinguish actual question/tool evidence from earlier assistant hypotheses? "
        "A relevant document title or valid reference alone is not entailment. Use not_applicable for no review."
    ),
    "tool_action_direction_acceptable": (
        "Is the entire proposed tool batch a reasonable information-gathering direction, independently "
        "of accompanying prose? This supplementary axis is not retrieval success or a replacement "
        "for action_acceptable. Use not_applicable for final text with no tools."
    ),
    "assistant_assertions_supported": (
        "Are factual assertions in the actor content supported by visible evidence or clearly marked "
        "as unestablished hypotheses? Do not penalize merely considering a candidate. Do not treat "
        "a tentative final Query as repairing unsupported confident prose."
    ),
    "final_answer_supported": (
        "For an actual final answer, does the visible prefix support the decisive original constraints? "
        "Do not infer correctness from finish_reason, gold knowledge or next_need=null. "
        "Use not_applicable for a tool decision or no final answer."
    ),
    "assumption_grounded": (
        "Does the review identify a consequential, still unestablished premise "
        "that is supported as a description of the current route? Do not mark "
        "a premise false merely because evidence for it is missing."
    ),
    "need_unresolved": "Is the proposed information need unresolved in this exact visible history?",
    "need_decision_relevant": (
        "Could resolving the proposed need change the next action or the answer "
        "under an original question constraint? A new topic alone is insufficient."
    ),
    "need_already_answered": (
        "Is the proposed need already answered by a specific visible observation? "
        "This is a separate reading-failure label, not an automatic inverse of need_unresolved."
    ),
    "decision_effect_balanced": (
        "Does the proposed decision effect allow evidence to retain or revise "
        "the current judgment, rather than requiring confirmation or a candidate switch?"
    ),
    "action_responds_to_need": (
        "Does the actor's next response address the proposed need in meaning? "
        "A lexically different query alone is not evidence. Use not_applicable "
        "when there is no identifiable review need or memo_injected is false; "
        "a rejected review was not shown to the actor. Use unknown when a partial "
        "record does not establish whether the memo was injected."
    ),
    "original_constraint_preserved": (
        "Does the next response preserve the relevant constraints of the "
        "original question, without silently replacing the task?"
    ),
    "action_acceptable": (
        "Is this next response a reasonable action given only the visible prefix? "
        "Consider every proposed tool call. No tool result has been executed in E0."
    ),
    "regression": (
        "After completing independent card judgments, is this branch worse than "
        "the matched baseline at the same checkpoint? Requires comparison; "
        "leave unknown until then. A different candidate is not by itself a regression."
    ),
    "new_errors": (
        "Does the review or next response introduce a specific new unsupported "
        "claim, ignored constraint, or other error relative to the visible prefix?"
    ),
    "answer_vs_abstention": (
        "Human classification of the actor's final text: an answer, abstention, "
        "a mix of both, or no final text. Do not infer this from finish_reason "
        "or the mere absence of tool calls. This is not answer correctness."
    ),
}


def _rubric() -> dict[str, Any]:
    labels = {}
    for name, description in _LABEL_DESCRIPTIONS.items():
        allowed = list(_COMMON_VALUES)
        if name == "answer_vs_abstention":
            allowed = [
                "answer", "abstention", "mixed", "no_final_text", "unknown", "not_applicable"
            ]
        labels[name] = {"description": description, "allowed_values": allowed}
    return {
        "schema_version": "need_review_rubric_v1",
        "workflow": [
            "Read visible_history and reference_index first, before the branch outputs. "
            "Write permitted_next_actions_before_branch and the relevant original constraints.",
            "Read review_output and actor_response, then label them against that same prefix. "
            "All tool calls in the response belong to this single next decision.",
            "For each judgment, give label_evidence notes and visible supporting_refs. "
            "Use unknown when the prefix is insufficient and not_applicable when a field "
            "has no object to assess; null means not annotated yet.",
            "Only after independent judgments, use private_key.json to compare matched "
            "branches and fill regression. Keep private_key.json away from the initial reviewer.",
        ],
        "limits": [
            "Cards hide checkpoint identifiers, arm labels, model names and cost metadata. "
            "Review output format and the absence of a review can still reveal an arm; "
            "this is metadata masking, not guaranteed blinding.",
            "No gold answers, future observations or new tool results are added. "
            "The exact captured history may itself mention entities or source identifiers.",
            "Completed is an execution status. It does not establish acceptable behavior, "
            "correctness, evidence sufficiency, successful submission or causal benefit.",
            "Partial and failed branches remain in the export. A recovered review response "
            "without a completed result is unvalidated, even if it looks like valid JSON.",
            "The two repetitions are diagnostic. Do not treat card counts as independent "
            "tasks or claim a population accuracy gain from this small checkpoint set.",
        ],
        "labels": labels,
    }


def _read_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = strict_json(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except (OSError, UnicodeError, ValueError):
        return None, "unreadable_or_invalid_json"
    if not isinstance(value, dict):
        return None, "not_an_object"
    return value, None


def _safe_component(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _SAFE_COMPONENT.fullmatch(value):
        raise ValueError(f"{field} must be a nonempty filename component")
    return value


def _load_schedule(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    if manifest.get("schema_version") != "need_review_run_v1":
        raise ValueError("Unsupported or missing manifest schema_version")
    if manifest.get("harness_revision") not in (None, HARNESS_REVISION):
        raise ValueError("Unsupported harness revision")
    schedule = manifest.get("schedule")
    if not isinstance(schedule, list):
        raise ValueError("manifest.schedule must be a list")
    seen = set()
    for item in schedule:
        if not isinstance(item, dict):
            raise ValueError("Every schedule entry must be an object")
        sample_id = _safe_component(item.get("sample_id"), "sample_id")
        _safe_component(item.get("checkpoint_id"), "checkpoint_id")
        if sample_id in seen:
            raise ValueError(f"Duplicate sample_id in manifest: {sample_id}")
        seen.add(sample_id)
        if item.get("arm") not in {"A", "B", "C"}:
            raise ValueError("Every schedule entry must have arm A, B or C")
        repeat_id = item.get("repeat_id")
        if not isinstance(repeat_id, int) or isinstance(repeat_id, bool) or repeat_id < 1:
            raise ValueError("Every repeat_id must be a positive integer")
    return schedule


def _read_events(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    return read_events(path)


def _partial_record(events: list[dict[str, Any]]) -> dict[str, Any]:
    review_response = None
    actor_response = None
    requests = 0
    for event in events:
        if event.get("kind") == "request":
            requests += 1
        if event.get("kind") != "response":
            continue
        if event.get("stage") == "review":
            review_response = event.get("response")
        elif event.get("stage") == "actor":
            actor_response = event.get("response")
    raw_text = _response_text(review_response)
    return {
        "status": "uncompleted",
        "review": {
            "status": "unvalidated_partial" if review_response is not None else "uncompleted",
            "raw_text": raw_text,
        },
        "actor": {"response": actor_response} if actor_response is not None else None,
        "logical_requests": requests,
    }


def _response_text(response: Any) -> str | None:
    if not isinstance(response, dict):
        return None
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    message = first.get("message") if isinstance(first, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    return content if isinstance(content, str) else None


def _visible_response(response: Any) -> dict[str, Any] | None:
    """Retain all response choices and tool calls, omitting API metadata."""
    if response is None:
        return None
    if not isinstance(response, dict) or not isinstance(response.get("choices"), list):
        return {"choices": [], "export_error": "invalid_actor_response_shape"}
    choices = []
    for choice in response["choices"]:
        if not isinstance(choice, dict):
            choices.append({"export_error": "invalid_actor_choice_shape"})
            continue
        choices.append({
            key: deepcopy(choice[key])
            for key in ("index", "finish_reason", "message")
            if key in choice
        })
    return {"choices": choices}


def _read_checkpoint(
    run_dir: Path, checkpoint_id: str, manifest: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    try:
        checkpoint = load_checkpoint(run_dir / "checkpoints" / f"{checkpoint_id}.json")
    except FileNotFoundError:
        return {}, ["checkpoint_missing"]
    except CheckpointError as exc:
        return {}, [f"checkpoint_validation_failed: {exc}"]
    except (OSError, UnicodeError):
        return {}, ["checkpoint_unreadable"]
    errors = []
    if checkpoint["checkpoint_id"] != checkpoint_id:
        errors.append("checkpoint_id_mismatch")
    entries = manifest.get("checkpoints")
    matching = [item for item in entries if isinstance(item, dict) and item.get("checkpoint_id") == checkpoint_id] if isinstance(entries, list) else []
    if len(matching) != 1:
        errors.append("checkpoint_run_manifest_entry_missing_or_duplicate")
    elif matching[0].get("request_sha256") != checkpoint["request_sha256"]:
        errors.append("checkpoint_run_manifest_request_hash_mismatch")
    if "prepared_manifest" in manifest or "prepared_manifest_sha256" in manifest:
        prepared = manifest.get("prepared_manifest")
        try:
            prepared_valid = isinstance(prepared, dict) and digest(prepared) == manifest.get("prepared_manifest_sha256")
        except (TypeError, ValueError, UnicodeError):
            prepared_valid = False
        if not prepared_valid:
            errors.append("prepared_manifest_hash_mismatch")
        else:
            prepared_entries = prepared.get("checkpoints")
            matching_prepared = [item for item in prepared_entries if isinstance(item, dict) and item.get("checkpoint_id") == checkpoint_id] if isinstance(prepared_entries, list) else []
            if len(matching_prepared) != 1:
                errors.append("checkpoint_prepared_manifest_entry_missing_or_duplicate")
            elif matching_prepared[0].get("checkpoint_sha256") != checkpoint["checkpoint_sha256"]:
                errors.append("checkpoint_prepared_manifest_hash_mismatch")
    return ({}, errors) if errors else (checkpoint, [])


def _read_branch(
    run_dir: Path, sample: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    branch_dir = run_dir / "branches" / sample["sample_id"]
    result, error = _read_object(branch_dir / "result.json")
    errors = []
    if result is not None:
        if all(result.get(key) == sample[key] for key in ("sample_id", "checkpoint_id", "arm", "repeat_id")):
            events, issues = _read_events(branch_dir / "events.jsonl")
            recovered, recovered_stages = recover_record(result, events)
            issues.extend("recovered_unvalidated_" + stage for stage in recovered_stages)
            return recovered, issues
        errors.append("result_metadata_mismatch")
    elif error != "missing":
        errors.append(f"result_{error}")
    events, event_errors = _read_events(branch_dir / "events.jsonl")
    errors.extend(event_errors)
    if events or errors:
        return _partial_record(events), errors
    return {"status": "not_run", "review": None, "actor": None, "logical_requests": 0}, []


def export_review(run_dir: Path, output: Path) -> dict[str, Any]:
    """Write fresh review cards, rubric and private key; return mechanical counts.

    ``output`` must not already exist, so annotations from an earlier export are
    never replaced.  Missing, interrupted and malformed branch records retain
    their scheduled row.  Invalid manifests fail before creating any output.
    """
    run_dir, output = Path(run_dir), Path(output)
    manifest, error = _read_object(run_dir / "manifest.json")
    if error:
        raise ValueError(f"Cannot read run manifest: {error}")
    assert manifest is not None
    schedule = _load_schedule(manifest)
    prompts, prompt_errors = {}, []
    if manifest.get("harness_revision") == HARNESS_REVISION:
        if manifest.get("plan_approved") is not True:
            prompt_errors.append("run_plan_not_approved")
        else:
            try:
                approved = manifest["approved_plan"]
                if not isinstance(approved, dict):
                    raise ValueError("Missing approved plan")
                # The run envelope intentionally has a different schema tag.
                actual_plan = {key: manifest.get(key) for key in approved}
                actual_plan['schema_version'] = 'need_review_plan_v1'
                verify_plan(approved, actual_plan)
            except (ValueError, KeyError, TypeError):
                prompt_errors.append("run_manifest_differs_from_approved_plan")
        for name, expected in manifest.get("prompt_sha256", {}).items():
            try:
                _safe_component(name, "prompt name")
                raw = (run_dir / "prompts" / f"{name}.txt").read_bytes()
                if hashlib.sha256(raw).hexdigest() != expected:
                    raise ValueError("Prompt hash mismatch")
                prompts[name] = raw.decode("utf-8")
            except (ValueError, OSError, UnicodeError):
                prompt_errors.append("frozen_prompt_missing_or_changed")
    settings = manifest.get("settings", {})
    seed = settings.get("seed", 0) if isinstance(settings, dict) else 0
    # Stable masking does not alter the execution schedule or use a process-random hash.
    ordered = sorted(
        schedule,
        key=lambda sample: hashlib.sha256(
            f"{seed}\0{sample['sample_id']}".encode("utf-8")
        ).hexdigest(),
    )
    cards = []
    prefix_cards = []
    private_entries = []
    checkpoints = {}
    status_counts: Counter[str] = Counter()
    for ordinal, sample in enumerate(ordered, 1):
        checkpoint_id = sample["checkpoint_id"]
        if checkpoint_id not in checkpoints:
            checkpoints[checkpoint_id] = _read_checkpoint(run_dir, checkpoint_id, manifest)
        checkpoint, checkpoint_errors = checkpoints[checkpoint_id]
        result, branch_errors = _read_branch(run_dir, sample)
        errors = list(checkpoint_errors) + branch_errors + prompt_errors
        if manifest.get("harness_revision") == HARNESS_REVISION and checkpoint and not prompt_errors:
            events, _ = _read_events(run_dir / "branches" / sample["sample_id"] / "events.jsonl")
            if events or result.get("status") != "not_run":
                try:
                    errors.extend(verify_branch_requests(checkpoint, result, sample,
                                                        settings, prompts, events))
                except (ValueError, KeyError, TypeError):
                    errors.append("branch_request_audit_failed")
        status = result.get("status", "invalid_result")
        if not isinstance(status, str):
            status = "invalid_result"
            errors.append("branch_status_invalid")
        status_counts[status] += 1
        review = result.get("review")
        review = review if isinstance(review, dict) else {}
        actor = result.get("actor")
        actor = actor if isinstance(actor, dict) else {}
        classification = actor.get("classification")
        classification = classification if isinstance(classification, dict) else {}
        mechanical_classification = {
            key: deepcopy(classification[key])
            for key in (
                "response_kind", "syntactic_complete", "protocol_compatible",
                "errors", "compatibility_markers", "finish_reason",
            )
            if key in classification
        } or None
        card_id = f"card_{ordinal:04d}"
        raw_text = review.get("raw_text")
        if raw_text is None:
            raw_text = _response_text(review.get("response"))
        review_status = review.get("status")
        if sample["arm"] == "A" and review_status in {None, "uncompleted"}:
            review_status = "not_applicable"
        prefix_cards.append({
            "card_id": card_id,
            "visible_history": deepcopy(checkpoint.get("request", {}).get("messages", [])),
            "reference_index": deepcopy(checkpoint.get("references", [])),
            "permitted_next_actions_before_branch": None,
            "original_constraints_before_branch": None,
        })
        cards.append({
            "card_id": card_id,
            "visible_history": deepcopy(checkpoint.get("request", {}).get("messages", [])),
            "reference_index": deepcopy(checkpoint.get("references", [])),
            "permitted_next_actions_before_branch": None,
            "original_constraints_before_branch": None,
            "review_output": raw_text,
            "actor_response": _visible_response(actor.get("response")),
            "execution_status": {
                "branch_status": status,
                "review_status": review_status,
                "memo_injected": result.get("memo_injected", False if sample["arm"] == "A" else None),
                "actor_response_kind": classification.get("response_kind"),
                "actor_classification": mechanical_classification,
                "export_errors": errors,
            },
            "labels": {name: None for name in _LABEL_DESCRIPTIONS},
            "label_evidence": {
                name: {"supporting_refs": [], "notes": ""} for name in _LABEL_DESCRIPTIONS
            },
        })
        private_entries.append({
            "card_id": card_id,
            "sample_id": sample["sample_id"],
            "checkpoint_id": checkpoint_id,
            "arm": sample["arm"],
            "repeat_id": sample["repeat_id"],
            "review_contract": sample.get("review_contract", settings.get("review_contract", "baseline")),
            "execution_status": status,
            "actor_classification": deepcopy(mechanical_classification),
            "source": deepcopy(checkpoint.get("source")),
            "logical_requests": result.get("logical_requests"),
            "review_validation_errors": deepcopy(review.get("errors")),
            "review_usage": deepcopy(review.get("usage")),
            "actor_usage": deepcopy(actor.get("usage")),
            "review_elapsed_seconds": review.get("elapsed_seconds"),
            "actor_elapsed_seconds": actor.get("elapsed_seconds"),
            "export_errors": errors,
        })
    summary = {
        "scheduled": len(schedule),
        "cards": len(cards),
        "completed": status_counts.get("completed", 0),
        "status_counts": dict(sorted(status_counts.items())),
        "cards_with_export_errors": sum(bool(card["execution_status"]["export_errors"]) for card in cards),
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output / "prefix_cards.jsonl").open("w", encoding="utf-8") as handle:
        for card in prefix_cards:
            handle.write(json.dumps(card, ensure_ascii=False) + "\n")
    with (output / "cards.jsonl").open("w", encoding="utf-8") as handle:
        for card in cards:
            handle.write(json.dumps(card, ensure_ascii=False) + "\n")
    (output / "rubric.json").write_text(
        json.dumps(_rubric(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "private_key.json").write_text(
        json.dumps({
            "schema_version": "need_review_private_key_v1",
            "summary": summary,
            "cards": private_entries,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New directory; existing annotations are never replaced")
    args = parser.parse_args(argv)
    try:
        summary = export_review(args.run_dir, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 2 if summary['cards_with_export_errors'] else 0


if __name__ == "__main__":
    raise SystemExit(main())
