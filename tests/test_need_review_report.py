"""Offline contracts for retained samples and human-only E0 annotations."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from experiments.research_state.need_review.report import export_review
from experiments.research_state.need_review.node import classify_actor_response
from experiments.research_state.need_review.checkpoint import SCHEMA_VERSION, digest


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def response(content=None, tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {
        "id": "hidden-response-id", "model": "hidden-model-name", "created": 123,
        "choices": [{"index": 0, "finish_reason": "tool_calls" if tool_calls else "stop", "message": message}],
        "usage": {"total_tokens": 77},
    }


class ExportReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run_dir = self.root / "run"
        self.schedule = [
            {"sample_id": f"case_secret__{arm}__r1", "checkpoint_id": "case_secret", "arm": arm, "repeat_id": 1}
            for arm in ("A", "B", "C")
        ]
        self.history = [
            {"role": "system", "content": "Keep original question constraints."},
            {"role": "user", "content": "Which person satisfies both constraints?"},
            {"role": "assistant", "content": None, "tool_calls": [{
                "id": "old-call", "type": "function", "function": {"name": "search", "arguments": '{"query":"first constraint"}'}
            }]},
            {"role": "tool", "tool_call_id": "old-call", "content": '[{"docid":"D1","text":"Visible evidence only."}]'},
        ]
        self.checkpoint = {
            "schema_version": SCHEMA_VERSION,
            "checkpoint_id": "case_secret",
            "request": {"messages": self.history, "model": "hidden-model-name", "stream": False},
            "references": [
                {"ref": "question", "message_index": 1, "path": ""},
                {"ref": "event:1:doc:D1", "message_index": 3, "path": "/0"},
            ],
            "source": {
                "events_path": "/does/not/exist/future_events.jsonl", "qid": 999,
                "source_commit": "a" * 40, "tool_version": "v000", "request_seq": 2,
                "prefix_sha256": "0" * 64,
                "tool_events": [{"message_index": 3, "event_seq": 1, "name": "search",
                                 "result_sha256": digest(json.loads(self.history[3]["content"]))}],
            },
            "gold_answer": "NEVER_EXPORT_GOLD",
            "purpose": "NEVER_EXPORT_PURPOSE",
        }
        self.checkpoint["request_sha256"] = digest(self.checkpoint["request"])
        self.checkpoint["checkpoint_sha256"] = digest(self.checkpoint)
        write_json(self.run_dir / "checkpoints" / "case_secret.json", self.checkpoint)
        prepared_manifest = {
            "schema_version": "need_review_prepared_v1",
            "checkpoints": [{"checkpoint_id": "case_secret", "checkpoint_sha256": self.checkpoint["checkpoint_sha256"]}],
        }
        self.manifest = {
            "schema_version": "need_review_run_v1", "settings": {"seed": 12}, "schedule": self.schedule,
            "checkpoints": [{"checkpoint_id": "case_secret", "request_sha256": self.checkpoint["request_sha256"]}],
            "prepared_manifest": prepared_manifest, "prepared_manifest_sha256": digest(prepared_manifest),
        }
        write_json(self.run_dir / "manifest.json", self.manifest)

    def write_result(self, arm, **fields):
        sample = next(sample for sample in self.schedule if sample["arm"] == arm)
        result = {**sample, "status": "completed", "review": None, "actor": None, "logical_requests": 1}
        result.update(fields)
        write_json(self.run_dir / "branches" / sample["sample_id"] / "result.json", result)

    def exported(self, output):
        cards = [json.loads(line) for line in (output / "cards.jsonl").read_text().splitlines()]
        private = json.loads((output / "private_key.json").read_text())
        by_arm = {entry["arm"]: next(card for card in cards if card["card_id"] == entry["card_id"]) for entry in private["cards"]}
        return cards, private, by_arm

    def test_retains_failures_and_pending_without_semantic_labels_or_metadata(self):
        calls = [
            {"id": "one", "type": "function", "function": {"name": "search", "arguments": '{"query":"other constraint"}'}},
            {"id": "two", "type": "function", "function": {"name": "get_document", "arguments": '{"docid":"D1"}'}},
        ]
        actor_response = response(tool_calls=calls)
        self.write_result("A", actor={"response": actor_response, "classification": {"response_kind": "tool_calls"}})
        self.write_result("B", status="actor_error", review={"status": "ok", "raw_text": "Check the second constraint."}, logical_requests=2)
        output = self.root / "review"
        summary = export_review(self.run_dir, output)
        cards, private, by_arm = self.exported(output)
        self.assertEqual(summary["scheduled"], 3)
        self.assertEqual(summary["cards"], 3)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["status_counts"], {"actor_error": 1, "completed": 1, "not_run": 1})
        self.assertEqual(by_arm["A"]["actor_response"]["choices"][0]["message"]["tool_calls"], calls)
        self.assertEqual(by_arm["B"]["review_output"], "Check the second constraint.")
        self.assertIsNone(by_arm["B"]["actor_response"])
        self.assertIsNone(by_arm["C"]["actor_response"])
        for card in cards:
            self.assertEqual(card["visible_history"], self.history)
            self.assertEqual(card["reference_index"], self.checkpoint["references"])
            self.assertTrue(all(value is None for value in card["labels"].values()))
        exported_text = (output / "cards.jsonl").read_text()
        for excluded in ("case_secret", "hidden-model-name", "hidden-response-id", "NEVER_EXPORT_GOLD", "NEVER_EXPORT_PURPOSE", "future_events.jsonl"):
            self.assertNotIn(excluded, exported_text)
        self.assertEqual({entry["sample_id"] for entry in private["cards"]}, {entry["sample_id"] for entry in self.schedule})

    def test_partial_events_and_truncated_tail_remain_unvalidated(self):
        sample = self.schedule[2]
        directory = self.run_dir / "branches" / sample["sample_id"]
        directory.mkdir(parents=True)
        events = [
            {"kind": "request", "stage": "review", "request": {"messages": []}},
            {"kind": "response", "stage": "review", "response": response('{"next_need":"A question?"}')},
            {"kind": "request", "stage": "actor", "request": {"messages": []}},
            {"kind": "response", "stage": "actor", "response": response("I cannot establish the answer.")},
        ]
        (directory / "events.jsonl").write_text("\n".join(json.dumps(event) for event in events) + '\n{"kind":', encoding="utf-8")
        output = self.root / "review"
        summary = export_review(self.run_dir, output)
        _, private, by_arm = self.exported(output)
        card = by_arm["C"]
        self.assertEqual(card["execution_status"]["branch_status"], "uncompleted")
        self.assertEqual(card["execution_status"]["review_status"], "unvalidated_partial")
        self.assertIsNone(card["execution_status"]["memo_injected"])
        self.assertIn("invalid_event_line_5", card["execution_status"]["export_errors"])
        self.assertEqual(card["review_output"], '{"next_need":"A question?"}')
        self.assertEqual(card["actor_response"]["choices"][0]["message"]["content"], "I cannot establish the answer.")
        self.assertIsNone(card["labels"]["answer_vs_abstention"])
        self.assertEqual(summary["cards_with_export_errors"], 1)
        self.assertEqual(next(entry for entry in private["cards"] if entry["arm"] == "C")["logical_requests"], 2)

    def test_invalid_review_fallback_is_not_hidden_or_judged_as_no_review(self):
        self.write_result(
            "C", review={"status": "node_invalid", "raw_text": "bad JSON", "errors": ["invalid_json"]},
            actor={"response": response("A tentative answer."), "classification": {"response_kind": "final_text"}},
            logical_requests=2, memo_injected=False,
        )
        output = self.root / "review"
        export_review(self.run_dir, output)
        _, private, by_arm = self.exported(output)
        self.assertEqual(by_arm["C"]["execution_status"]["review_status"], "node_invalid")
        self.assertEqual(by_arm["C"]["review_output"], "bad JSON")
        self.assertFalse(by_arm["C"]["execution_status"]["memo_injected"])
        self.assertIsNone(by_arm["C"]["labels"]["answer_vs_abstention"])
        self.assertEqual(next(entry for entry in private["cards"] if entry["arm"] == "C")["review_validation_errors"], ["invalid_json"])

    def test_complete_tool_proposal_with_stop_preserves_protocol_rejection(self):
        calls = [{"id": "one", "type": "function", "function": {
            "name": "search", "arguments": '{"query":"second constraint"}'
        }}]
        actor_response = response(tool_calls=calls)
        actor_response["choices"][0]["finish_reason"] = "stop"
        request = {
            "tool_choice": "auto",
            "tools": [{"type": "function", "function": {
                "name": "search", "parameters": {
                    "type": "object", "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            }}],
        }
        classification = classify_actor_response(actor_response, request)
        self.write_result("A", actor={"response": actor_response, "classification": classification})
        output = self.root / "review"
        export_review(self.run_dir, output)
        _, private, by_arm = self.exported(output)
        card = by_arm["A"]
        mechanical = card["execution_status"]["actor_classification"]
        self.assertEqual(mechanical["response_kind"], "tool_calls")
        self.assertTrue(mechanical["syntactic_complete"])
        self.assertFalse(mechanical["protocol_compatible"])
        self.assertEqual(mechanical["finish_reason"], "stop")
        self.assertIn("tool_calls_with_stop", mechanical["compatibility_markers"])
        self.assertTrue(mechanical["errors"])
        self.assertNotIn("raw_response", mechanical)
        self.assertNotIn("tool_calls", mechanical)
        self.assertEqual(card["actor_response"]["choices"][0]["message"]["tool_calls"], calls)
        self.assertEqual(next(entry for entry in private["cards"] if entry["arm"] == "A")["actor_classification"], mechanical)
        self.assertIsNone(card["labels"]["action_acceptable"])

    def test_missing_checkpoint_and_wrong_result_still_have_scheduled_cards(self):
        (self.run_dir / "checkpoints" / "case_secret.json").unlink()
        self.write_result("B", sample_id="different_sample", actor={"response": response("Wrong branch must not appear")})
        output = self.root / "review"
        summary = export_review(self.run_dir, output)
        cards, _, by_arm = self.exported(output)
        self.assertEqual(summary["cards"], 3)
        self.assertTrue(all(card["visible_history"] == [] for card in cards))
        self.assertTrue(all("checkpoint_missing" in card["execution_status"]["export_errors"] for card in cards))
        self.assertIn("result_metadata_mismatch", by_arm["B"]["execution_status"]["export_errors"])
        self.assertIsNone(by_arm["B"]["actor_response"])

    def test_swapped_and_tampered_checkpoints_never_present_an_authoritative_prefix(self):
        self.write_result("A", actor={"response": response("Recorded actor output.")})
        for change in ("swapped", "tampered", "rehashed_request", "rehashed_source", "rehashed_references"):
            with self.subTest(change=change):
                checkpoint = deepcopy(self.checkpoint)
                if change == "swapped":
                    checkpoint["checkpoint_id"] = "different_case"
                elif change in {"tampered", "rehashed_request"}:
                    checkpoint["request"]["messages"][1]["content"] = "A different question."
                    if change == "rehashed_request":
                        checkpoint["request_sha256"] = digest(checkpoint["request"])
                elif change == "rehashed_source":
                    checkpoint["source"]["source_commit"] = "b" * 40
                else:
                    checkpoint["references"].append({"ref": "hidden", "message_index": 1, "path": ""})
                if change != "tampered":
                    checkpoint["checkpoint_sha256"] = digest({key: value for key, value in checkpoint.items() if key != "checkpoint_sha256"})
                write_json(self.run_dir / "checkpoints" / "case_secret.json", checkpoint)
                output = self.root / change
                summary = export_review(self.run_dir, output)
                cards, _, by_arm = self.exported(output)
                self.assertEqual(summary["scheduled"], 3)
                self.assertEqual(summary["cards"], 3)
                self.assertEqual(summary["cards_with_export_errors"], 3)
                for card in cards:
                    self.assertEqual(card["visible_history"], [])
                    self.assertEqual(card["reference_index"], [])
                    self.assertTrue(card["execution_status"]["export_errors"])
                self.assertEqual(by_arm["A"]["actor_response"]["choices"][0]["message"]["content"], "Recorded actor output.")

    def test_prepared_manifest_tampering_is_explicit_and_retains_denominator(self):
        self.manifest["prepared_manifest"]["checkpoints"][0]["checkpoint_sha256"] = "f" * 64
        write_json(self.run_dir / "manifest.json", self.manifest)
        output = self.root / "review"
        summary = export_review(self.run_dir, output)
        cards, _, _ = self.exported(output)
        self.assertEqual(summary["cards"], 3)
        self.assertTrue(all("prepared_manifest_hash_mismatch" in card["execution_status"]["export_errors"] for card in cards))
        self.assertTrue(all(card["visible_history"] == [] for card in cards))

    def test_export_is_deterministic_does_not_mutate_input_or_replace_annotations(self):
        original_manifest = (self.run_dir / "manifest.json").read_bytes()
        original_checkpoint = (self.run_dir / "checkpoints" / "case_secret.json").read_bytes()
        first, second = self.root / "review1", self.root / "review2"
        export_review(self.run_dir, first)
        export_review(self.run_dir, second)
        for filename in ("cards.jsonl", "rubric.json", "private_key.json"):
            self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())
        (first / "cards.jsonl").write_text("human annotation", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            export_review(self.run_dir, first)
        self.assertEqual((first / "cards.jsonl").read_text(), "human annotation")
        self.assertEqual((self.run_dir / "manifest.json").read_bytes(), original_manifest)
        self.assertEqual((self.run_dir / "checkpoints" / "case_secret.json").read_bytes(), original_checkpoint)

    def test_invalid_manifest_fails_before_writing_output(self):
        for change in ("duplicate", "unsafe_path", "bad_repeat", "bad_schema"):
            with self.subTest(change=change):
                manifest = deepcopy(self.manifest)
                if change == "duplicate":
                    manifest["schedule"].append(deepcopy(manifest["schedule"][0]))
                elif change == "unsafe_path":
                    manifest["schedule"][0]["checkpoint_id"] = "../../original-future-events"
                elif change == "bad_repeat":
                    manifest["schedule"][0]["repeat_id"] = True
                else:
                    manifest["schema_version"] = "unknown"
                write_json(self.run_dir / "manifest.json", manifest)
                output = self.root / change
                with self.assertRaises(ValueError):
                    export_review(self.run_dir, output)
                self.assertFalse(output.exists())

    def test_rubric_distinguishes_mechanical_completion_from_semantic_judgment(self):
        output = self.root / "review"
        export_review(self.run_dir, output)
        rubric = json.loads((output / "rubric.json").read_text())
        self.assertEqual(
            rubric["labels"]["answer_vs_abstention"]["allowed_values"],
            ["answer", "abstention", "mixed", "no_final_text", "unknown", "not_applicable"],
        )
        for item in rubric["labels"].values():
            self.assertIn("unknown", item["allowed_values"])
            self.assertIn("not_applicable", item["allowed_values"])
        self.assertTrue(any("not guaranteed blinding" in limit for limit in rubric["limits"]))
        self.assertIn("memo_injected is false", rubric["labels"]["action_responds_to_need"]["description"])


if __name__ == "__main__":
    unittest.main()
