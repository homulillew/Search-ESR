"""Offline integration tests for E0 scheduling, failure accounting and provenance."""

import builtins
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from experiments.research_state.need_review import run
from experiments.research_state.need_review.checkpoint import digest


ROOT = Path(__file__).resolve().parents[1]


def completion(content=None, *, calls=None, usage=None):
    message = {"role": "assistant", "content": content}
    if calls is not None:
        message["tool_calls"] = calls
    return {
        "id": "offline-response",
        "choices": [{"index": 0, "finish_reason": "tool_calls" if calls else "stop",
                     "message": message}],
        "usage": usage or {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def proposed_batch():
    return completion(calls=[
        {"id": "next-search", "type": "function",
         "function": {"name": "search", "arguments": '{"query":"independent relationship"}'}},
        {"id": "next-open", "type": "function",
         "function": {"name": "get_document", "arguments": '{"docid":"visible-doc"}'}},
    ], usage={"prompt_tokens": 20, "completion_tokens": 7, "total_tokens": 27})


def successful_response(request):
    if "tools" in request:
        return proposed_batch()
    if "current_assumption" in request["messages"][0]["content"]:
        return completion(json.dumps({
            "current_assumption": None,
            "next_need": "Which visible relationship distinguishes the candidate?",
            "decision_effect": "A documented mismatch would reopen the candidate search.",
            "basis_refs": ["question"],
        }))
    return completion("The visible evidence leaves the relationship unresolved. Basis: question.")


class FakeClient:
    """Only completion requests are provided; no tool runtime exists in this fake."""

    def __init__(self, handler=successful_response, *, mutate_input=False):
        self.requests = []
        self.handler = handler
        self.mutate_input = mutate_input
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **request):
        self.requests.append(deepcopy(request))
        response = self.handler(request)
        if self.mutate_input:
            request["messages"].append({"role": "user", "content": "SDK mutation sentinel"})
        return response


class NeedReviewRunTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source_root = self.root / "source"
        self.source_root.mkdir()
        self.settings = run.settings_dict()

    def prepare_cases(self, identifiers=("case_546", "case_776", "case_517"), *, options=None):
        selection = {
            "schema_version": "need_review_selection_v1",
            "source_commit": "a" * 40,
            "checkpoints": [],
        }
        captured = {}
        for identifier in identifiers:
            observation = [{"docid": "visible-doc", "url": "https://example.invalid/source",
                            "text": f"Only the already returned text for {identifier}."}]
            call = {"id": "past-search", "type": "function",
                    "function": {"name": "search", "arguments": '{"query":"initial clues"}'}}
            request = {
                "model": "captured-model",
                "messages": [
                    {"role": "system", "content": "Research and cite observed sources."},
                    {"role": "user", "content": f"Identify the entity for {identifier}."},
                    {"role": "assistant", "content": None, "tool_calls": [call]},
                    {"role": "tool", "tool_call_id": "past-search", "name": "search",
                     "content": json.dumps(observation)},
                ],
                "tools": [
                    {"type": "function", "function": {"name": "search", "parameters": {
                        "type": "object", "properties": {"query": {"type": "string"}},
                        "required": ["query"], "additionalProperties": False}}},
                    {"type": "function", "function": {"name": "get_document", "parameters": {
                        "type": "object", "properties": {"docid": {"type": "string"}},
                        "required": ["docid"], "additionalProperties": False}}},
                ],
                "tool_choice": "auto", "stream": False, "temperature": 0.2,
                "max_tokens": 2048, "extra_body": {"enable_thinking": False},
            }
            request.update(deepcopy(options or {}))
            captured[identifier] = deepcopy(request)
            initial_request = deepcopy(request)
            initial_request["messages"] = initial_request["messages"][:2]
            events = [
                {"seq": 1, "kind": "api_request", "request": initial_request},
                {"seq": 2, "kind": "api_response", "response": completion(calls=[call])},
                {"seq": 3, "kind": "tool_start", "name": "search",
                 "arguments": {"query": "initial clues"}},
                {"seq": 4, "kind": "tool_result", "name": "search", "result": observation},
                {"seq": 5, "kind": "api_request", "request": request},
                {"seq": 6, "kind": "api_response", "response": completion("SECRET_FUTURE_ANSWER")},
            ]
            relative = f"runs/{identifier}/events.jsonl"
            path = self.source_root / relative
            path.parent.mkdir(parents=True)
            path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            selection["checkpoints"].append({
                "checkpoint_id": identifier, "events_path": relative,
                "events_blob_sha": run.git_blob_sha(path), "request_seq": 5,
                "tool_version": "synthetic-v000-search-get_document",
            })
        selection_path = self.root / "selection.json"
        run.write_json(selection_path, selection)
        prepared = self.root / "prepared"
        run.prepare(selection_path, self.source_root, prepared)
        return prepared, selection_path, captured

    def execute(self, prepared, client, *, settings=None):
        output = self.root / "run"
        with redirect_stdout(io.StringIO()):
            summary = run.execute(prepared, output, client=client, settings=settings or self.settings)
        return output, summary

    def test_exact_prefix_eighteen_actor_twelve_review_calls_and_batches_are_preserved(self):
        prepared, _, captured = self.prepare_cases()
        before = {path: path.read_bytes() for path in prepared.rglob("*.json")}
        # E0 must run from prepared data alone, even when the source is unavailable.
        for path in self.source_root.rglob("events.jsonl"):
            path.unlink()
        client = FakeClient(mutate_input=True)
        output, summary = self.execute(prepared, client)
        plan = run.read_json(output / "manifest.json")
        self.assertEqual(plan["scheduled_actor_requests"], 18)
        self.assertEqual(plan["scheduled_review_requests"], 12)
        self.assertEqual(plan["scheduled_logical_requests"], 30)
        self.assertEqual(len(client.requests), 30)
        self.assertEqual(summary["logical_requests_attempted"], 30)
        self.assertEqual(summary["branch_statuses"], {"completed": 18})
        self.assertEqual(summary["tool_executions"], 0)
        self.assertEqual(summary["reported_usage_by_stage"]["review"]["total_tokens"], 180)
        self.assertEqual(summary["reported_usage_by_stage"]["actor"]["total_tokens"], 486)
        self.assertEqual(len({item["sample_id"] for item in plan["schedule"]}), 18)
        for identifier in captured:
            for repeat in (1, 2):
                self.assertEqual({item["arm"] for item in plan["schedule"]
                                  if item["checkpoint_id"] == identifier and item["repeat_id"] == repeat},
                                 {"A", "B", "C"})
        for item in plan["schedule"]:
            result = run.read_json(output / "branches" / item["sample_id"] / "result.json")
            actor = result["actor"]
            original = captured[item["checkpoint_id"]]
            self.assertEqual(actor["classification"]["response_kind"], "tool_calls")
            self.assertTrue(actor["classification"]["protocol_compatible"])
            self.assertEqual(actor["classification"]["tool_calls"], proposed_batch()["choices"][0]["message"]["tool_calls"])
            self.assertEqual(actor["response"], proposed_batch())
            if item["arm"] == "A":
                self.assertEqual(actor["request"], original)
                self.assertFalse(result["memo_injected"])
            else:
                self.assertEqual(actor["request"]["messages"][:-1], original["messages"])
                self.assertEqual({key: value for key, value in actor["request"].items() if key != "messages"},
                                 {key: value for key, value in original.items() if key != "messages"})
                self.assertTrue(result["memo_injected"])
                review_request = result["review"]["request"]
                self.assertNotIn("tools", review_request)
                self.assertNotIn("tool_choice", review_request)
                self.assertEqual(review_request["max_tokens"], 512)
                self.assertEqual(review_request["extra_body"], original["extra_body"])
                payload = json.loads(review_request["messages"][1]["content"])
                self.assertEqual(payload["messages"], original["messages"])
                self.assertEqual(set(payload), {"messages", "references"})
        serialized = json.dumps(client.requests)
        self.assertNotIn("SECRET_FUTURE_ANSWER", serialized)
        self.assertNotIn("SDK mutation sentinel", serialized)
        self.assertEqual(before, {path: path.read_bytes() for path in prepared.rglob("*.json")})

    def test_invalid_need_review_falls_back_to_exact_request_and_retains_review_cost(self):
        prepared, _, captured = self.prepare_cases(("case_one",))
        _, checkpoints = run.load_prepared(prepared)
        invalid = completion(json.dumps({
            "current_assumption": None, "next_need": "A plausible need",
            "decision_effect": "A possible effect", "basis_refs": ["unseen-future-document"],
        }))
        client = FakeClient(lambda request: proposed_batch() if "tools" in request else invalid)
        item = {"sample_id": "case_one__C__r1", "checkpoint_id": "case_one", "arm": "C", "repeat_id": 1}
        output = self.root / "run"
        result = run.run_branch(checkpoints["case_one"], item, client,
                                output / "branches" / item["sample_id"], self.settings, run.load_prompts())
        self.assertEqual(len(client.requests), 2)
        self.assertEqual(result["review"]["status"], "node_invalid")
        self.assertEqual(result["review"]["response"], invalid)
        self.assertFalse(result["memo_injected"])
        self.assertEqual(result["actor"]["request"], captured["case_one"])
        summary = run.summarize(output, [item])
        self.assertEqual(summary["review_statuses"], {"node_invalid": 1})
        self.assertEqual(summary["reported_usage_by_stage"]["review"]["total_tokens"], 15)
        self.assertEqual(summary["logical_requests_attempted"], 2)

    def test_reviewer_api_error_falls_back_without_logging_exception_secrets(self):
        prepared, _, captured = self.prepare_cases(("case_one",))
        _, checkpoints = run.load_prepared(prepared)

        def fail_review(request):
            if "tools" not in request:
                raise RuntimeError("Authorization: bearer NEVER_LOG_THIS_SECRET")
            return proposed_batch()

        output = self.root / "run"
        items = []
        for arm in ("B", "C"):
            with self.subTest(arm=arm):
                item = {"sample_id": f"case_one__{arm}__r1", "checkpoint_id": "case_one", "arm": arm, "repeat_id": 1}
                items.append(item)
                client = FakeClient(fail_review)
                result = run.run_branch(checkpoints["case_one"], item, client,
                                        output / "branches" / item["sample_id"], self.settings, run.load_prompts())
                self.assertEqual(result["review"]["status"], "api_error")
                self.assertEqual(result["review"]["error_type"], "RuntimeError")
                self.assertEqual(result["actor"]["request"], captured["case_one"])
                self.assertEqual(result["status"], "completed")
                self.assertFalse(result["memo_injected"])
        summary = run.summarize(output, items)
        self.assertEqual(summary["failed_requests_with_unknown_cost"], 2)
        self.assertEqual(summary["logical_requests_attempted"], 4)
        self.assertEqual(summary["responses_received"], 2)
        for path in output.rglob("*.json*"):
            self.assertNotIn("NEVER_LOG_THIS_SECRET", path.read_text(encoding="utf-8"))

    def test_actor_errors_retain_all_branches_and_full_scheduled_denominator(self):
        prepared, _, _ = self.prepare_cases()

        def fail_actor(request):
            if "tools" in request:
                raise TimeoutError("transport detail must not be logged")
            return successful_response(request)

        client = FakeClient(fail_actor)
        output, summary = self.execute(prepared, client)
        self.assertEqual(summary["scheduled_branches"], 18)
        self.assertEqual(summary["branch_statuses"], {"actor_error": 18})
        self.assertEqual(summary["logical_requests_attempted"], 30)
        self.assertEqual(summary["failed_requests_with_unknown_cost"], 18)
        self.assertEqual(summary["responses_received"], 12)
        self.assertEqual(len(list((output / "branches").glob("*/result.json"))), 18)
        self.assertEqual(summary["actor_response_kinds"], {"not_observed": 18})

    def test_keyboard_interrupt_persists_partial_branch_and_not_run_denominator(self):
        prepared, _, _ = self.prepare_cases()

        def interrupt_actor(request):
            if "tools" in request:
                raise KeyboardInterrupt()
            return successful_response(request)

        client = FakeClient(interrupt_actor)
        output = self.root / "run"
        with redirect_stdout(io.StringIO()), self.assertRaises(KeyboardInterrupt):
            run.execute(prepared, output, client=client, settings=self.settings)
        manifest = run.read_json(output / "manifest.json")
        first = manifest["schedule"][0]
        partial = run.read_json(output / "branches" / first["sample_id"] / "result.json")
        summary = run.read_json(output / "summary.json")
        self.assertEqual(partial["status"], "interrupted")
        self.assertIsNone(partial["actor"])
        self.assertEqual(summary["scheduled_branches"], 18)
        self.assertEqual(summary["branch_statuses"], {"interrupted": 1, "not_run": 17})
        self.assertEqual(summary["failed_requests_with_unknown_cost"], 1)
        self.assertEqual(summary["logical_requests_attempted"], len(client.requests))
        events = [json.loads(line) for line in (output / "branches" / first["sample_id"] / "events.jsonl").read_text().splitlines()]
        self.assertEqual(events[-1]["error_type"], "KeyboardInterrupt")
        self.assertEqual(events[-1]["stage"], "actor")

    def test_prepare_refuses_changed_source_blob_before_creating_output(self):
        _, selection_path, _ = self.prepare_cases(("case_one",))
        source = self.source_root / "runs/case_one/events.jsonl"
        with source.open("a", encoding="utf-8") as stream:
            stream.write('{"seq":7,"kind":"later"}\n')
        output = self.root / "tampered-prepared"
        with self.assertRaisesRegex(ValueError, "Source blob differs"):
            run.prepare(selection_path, self.source_root, output)
        self.assertFalse(output.exists())

    def test_prepared_selection_hash_detects_edited_frozen_selection(self):
        prepared, _, _ = self.prepare_cases(("case_one",))
        manifest = run.read_json(prepared / "manifest.json")
        manifest["selection"]["checkpoints"][0]["request_seq"] += 1
        run.write_json(prepared / "manifest.json", manifest)
        with self.assertRaisesRegex(ValueError, "Selection hash mismatch"):
            run.load_prepared(prepared)

    def test_self_consistent_checkpoint_still_must_match_frozen_source_selection(self):
        prepared, _, _ = self.prepare_cases(("case_one",))
        manifest = run.read_json(prepared / "manifest.json")
        item = manifest["checkpoints"][0]
        checkpoint = run.read_json(prepared / item["file"])
        checkpoint["source"]["source_commit"] = "b" * 40
        checkpoint["checkpoint_sha256"] = digest({key: value for key, value in checkpoint.items()
                                                 if key != "checkpoint_sha256"})
        item["checkpoint_sha256"] = checkpoint["checkpoint_sha256"]
        run.write_json(prepared / item["file"], checkpoint)
        run.write_json(prepared / "manifest.json", manifest)
        with self.assertRaises(ValueError):
            run.load_prepared(prepared)

    def test_preflight_rejects_ambiguous_options_before_any_request_or_client_import(self):
        prepared, _, _ = self.prepare_cases(("case_one",), options={"extra_body": {"tools": []}})
        client = FakeClient()
        output = self.root / "run"
        with self.assertRaisesRegex(ValueError, "extra_body"):
            run.execute(prepared, output, client=client, settings=self.settings)
        self.assertEqual(client.requests, [])
        self.assertFalse(output.exists())
        real_import = builtins.__import__

        def prohibit_credentials(name, *args, **kwargs):
            if name in {"openai", "dotenv", "llm_chat.client"}:
                raise AssertionError("Offline preflight imported a credential or API dependency")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=prohibit_credentials):
            with self.assertRaisesRegex(ValueError, "extra_body"):
                run.main(["execute", "--prepared", str(prepared), "--output", str(output)])

    def test_offline_plan_imports_neither_sdk_credentials_nor_retrieval_runtime(self):
        prepared, _, _ = self.prepare_cases(("case_one",))
        script = """
import builtins
import sys
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.split('.')[0] in {'openai', 'dotenv', 'torch', 'llm_chat'}:
        raise AssertionError('Unexpected offline dependency: ' + name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
from experiments.research_state.need_review.run import main
main(['plan', '--prepared', sys.argv[1]])
"""
        process = subprocess.run([sys.executable, "-c", script, str(prepared)], cwd=ROOT,
                                 text=True, capture_output=True, check=False)
        self.assertEqual(process.returncode, 0, process.stderr)
        plan = json.loads(process.stdout)
        self.assertEqual(plan["scheduled_logical_requests"], 10)
        self.assertEqual(plan["tool_executions"], 0)

    def test_existing_output_is_rejected_before_calls_and_existing_data_survives(self):
        prepared, selection_path, _ = self.prepare_cases(("case_one",))
        with self.assertRaises(FileExistsError):
            run.prepare(selection_path, self.source_root, prepared)
        output = self.root / "run"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("already recorded", encoding="utf-8")
        client = FakeClient()
        with self.assertRaises(FileExistsError):
            run.execute(prepared, output, client=client, settings=self.settings)
        self.assertEqual(client.requests, [])
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "already recorded")

    def test_explicit_model_override_applies_to_both_stages_and_is_recorded(self):
        prepared, _, captured = self.prepare_cases(("case_one",))
        settings = run.settings_dict(repeats=1, model="explicit-model")
        client = FakeClient()
        output, summary = self.execute(prepared, client, settings=settings)
        self.assertEqual(len(client.requests), 5)
        self.assertEqual({request["model"] for request in client.requests}, {"explicit-model"})
        manifest = run.read_json(output / "manifest.json")
        self.assertEqual(manifest["settings"]["model_override"], "explicit-model")
        self.assertEqual(manifest["checkpoints"][0]["captured_model"], "captured-model")
        self.assertEqual(manifest["checkpoints"][0]["effective_model"], "explicit-model")
        _, checkpoint = run.load_prepared(prepared)
        self.assertEqual(checkpoint["case_one"]["request"], captured["case_one"])
        self.assertEqual(summary["tool_executions"], 0)


if __name__ == "__main__":
    unittest.main()
