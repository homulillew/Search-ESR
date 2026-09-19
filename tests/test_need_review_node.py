"""Offline contract tests: no API client, corpus, or model credentials needed."""

from copy import deepcopy
import json
import unittest

from experiments.research_state.need_review.node import (
    build_actor_request,
    build_review_request,
    classify_actor_response,
    validate_review,
)


MEMO = "This review may be wrong and is not source evidence.\n<review>\n{review_output}\n</review>"


def checkpoint():
    return {
        "checkpoint_id": "synthetic",
        "purpose": "EVALUATION_METADATA_MUST_NOT_REACH_THE_MODEL",
        "gold": "GOLD_MUST_NOT_REACH_THE_MODEL",
        "request": {
            "model": "captured-model",
            "messages": [
                {"role": "system", "content": "Original actor instruction; keep exactly."},
                {"role": "user", "content": "Which person satisfies the 1980–1990 clues?"},
                {"role": "assistant", "content": "Candidate A is a hypothesis.",
                 "tool_calls": [tool_call("call_1")]},
                {"role": "tool", "tool_call_id": "call_1",
                 "content": '[{"docid":"d1","text":"Some visible evidence."}]'},
            ],
            "tools": [
                {"type": "function", "function": {
                    "name": "search",
                    "parameters": {
                        "type": "object", "properties": {
                            "query": {"type": "string"},
                            "k": {"type": "integer", "minimum": 1, "maximum": 10},
                        }, "required": ["query"], "additionalProperties": False,
                    },
                }},
                {"type": "function", "function": {
                    "name": "open",
                    "parameters": {
                        "type": "object", "properties": {
                            "window_ref": {"type": "string"},
                            "direction": {"type": "string", "enum": ["before", "after", "around"]},
                        }, "required": ["window_ref", "direction"], "additionalProperties": False,
                    },
                }},
            ],
            "tool_choice": "auto", "stream": False, "temperature": 0.7,
            "max_tokens": 8000, "extra_body": {"enable_thinking": False},
        },
        "references": [
            {"ref": "question", "message_index": 1, "path": ""},
            {"ref": "event_4:docid:d1", "message_index": 3, "path": "/0"},
        ],
    }


def tool_call(identifier="call_2", name="search", arguments=None):
    if arguments is None:
        arguments = {"query": "relationship from original clues"}
    return {"id": identifier, "type": "function", "function": {
        "name": name, "arguments": json.dumps(arguments, ensure_ascii=False),
    }}


def response(content=None, *, finish="stop", calls=None, refusal=None):
    return {"id": "synthetic-response", "choices": [{
        "index": 0, "finish_reason": finish,
        "message": {"role": "assistant", "content": content,
                    "tool_calls": calls, "refusal": refusal},
    }], "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}


def need_review(**updates):
    value = {"current_assumption": None,
             "next_need": "Does the visible relationship include the original time range?",
             "decision_effect": "An explicit date could support or revise the proposed relationship.",
             "basis_refs": ["question", "event_4:docid:d1"]}
    value.update(updates)
    return value


class RequestContractTests(unittest.TestCase):
    def test_baseline_exact_copy_and_no_mutation_when_actor_changes(self):
        original = checkpoint()
        before = deepcopy(original)
        actual = build_actor_request(original, None, MEMO)
        self.assertEqual(actual, original["request"])
        actual["messages"][0]["content"] = "changed"
        actual["extra_body"]["enable_thinking"] = True
        actual["tools"][0]["function"]["name"] = "changed"
        self.assertEqual(original, before)

    def test_review_b_and_c_have_identical_inputs_and_matched_configuration(self):
        original = checkpoint()
        before = deepcopy(original)
        b = build_review_request(original, "B", "generic prompt")
        c = build_review_request(original, "C", "need prompt")
        self.assertEqual(b["messages"][1], c["messages"][1])
        self.assertEqual({k: v for k, v in b.items() if k != "messages"},
                         {k: v for k, v in c.items() if k != "messages"})
        payload = json.loads(c["messages"][1]["content"])
        self.assertEqual(payload, {"messages": original["request"]["messages"],
                                   "references": original["references"]})
        self.assertEqual(c["messages"][0], {"role": "system", "content": "need prompt"})
        serialized = json.dumps(c)
        self.assertNotIn("EVALUATION_METADATA_MUST_NOT", serialized)
        self.assertNotIn("GOLD_MUST_NOT", serialized)
        self.assertEqual(c["extra_body"], {"enable_thinking": False})
        self.assertEqual(c["max_tokens"], 512)
        self.assertEqual(c["temperature"], 0.7)
        self.assertEqual(original, before)
        c["extra_body"]["enable_thinking"] = True
        self.assertEqual(original, before)

    def test_reviewer_has_no_tools_or_carried_output_schema(self):
        original = checkpoint()
        original["request"].update({
            "functions": [{"name": "old-tool"}], "function_call": "auto",
            "parallel_tool_calls": True, "web_search_options": {},
            "response_format": {"type": "json_object"},
            "stream_options": {"include_usage": True}, "n": 4,
            "max_completion_tokens": 7000,
        })
        review = build_review_request(original, "B", "review", max_tokens=256)
        for key in ("tools", "tool_choice", "functions", "function_call",
                    "parallel_tool_calls", "web_search_options", "response_format",
                    "stream_options", "max_tokens"):
            self.assertNotIn(key, review)
        self.assertEqual(review["n"], 1)
        self.assertEqual(review["max_completion_tokens"], 256)
        self.assertFalse(review["stream"])

    def test_reviewer_cannot_regain_tools_or_override_matched_budget_via_extra_body(self):
        for key, value in (("tools", []), ("max_tokens", 9000), ("messages", []),
                           ("stream", True), ("response_format", {}), ("n", 2)):
            with self.subTest(key=key):
                original = checkpoint()
                original["request"]["extra_body"][key] = value
                with self.assertRaises(ValueError):
                    build_review_request(original, "C", "review")

    def test_reviewer_rejects_metadata_in_reference_index(self):
        original = checkpoint()
        original["references"][0]["case_purpose"] = "hidden evaluation annotation"
        with self.assertRaises(ValueError):
            build_review_request(original, "C", "review")
        for bad_index in (-1, 4, True):
            original = checkpoint()
            original["references"][0]["message_index"] = bad_index
            with self.assertRaises(ValueError):
                build_review_request(original, "C", "review")

    def test_actor_injects_exactly_one_user_memo_without_resetting_history(self):
        original = checkpoint()
        text = json.dumps(need_review(), ensure_ascii=False)
        actual = build_actor_request(original, text, MEMO)
        self.assertEqual(actual["messages"][:-1], original["request"]["messages"])
        self.assertEqual(actual["messages"][-1], {
            "role": "user", "content": MEMO.replace("{review_output}", text),
        })
        self.assertEqual({k: v for k, v in actual.items() if k != "messages"},
                         {k: v for k, v in original["request"].items() if k != "messages"})
        self.assertEqual(len(original["request"]["messages"]), 4)

    def test_model_override_is_explicit_in_both_requests_and_source_unchanged(self):
        original = checkpoint()
        actor = build_actor_request(original, None, MEMO, model="explicit-replacement")
        review = build_review_request(original, "C", "review", model="explicit-replacement")
        self.assertEqual(actor["model"], "explicit-replacement")
        self.assertEqual(review["model"], actor["model"])
        self.assertEqual(original["request"]["model"], "captured-model")

    def test_empty_review_and_ambiguous_memo_are_rejected(self):
        with self.assertRaises(ValueError):
            build_actor_request(checkpoint(), "  ", MEMO)
        for template in ("no placeholder", "{review_output} and {review_output}"):
            with self.assertRaises(ValueError):
                build_actor_request(checkpoint(), "review", template)
        for cap in (0, -1, True, 2.5):
            with self.assertRaises(ValueError):
                build_review_request(checkpoint(), "C", "review", max_tokens=cap)


class ReviewValidationTests(unittest.TestCase):
    def setUp(self):
        self.refs = {"question", "event_4:docid:d1"}

    def test_valid_c_keeps_exact_raw_text_and_accepts_no_unestablished_premise(self):
        value = need_review()
        text = "\n" + json.dumps(value) + "\n"
        result = validate_review(response(text), "C", self.refs)
        self.assertTrue(result["valid"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["raw_text"], text)
        self.assertEqual(result["parsed"], value)

    def test_all_nulls_does_not_force_search_or_claim_readiness(self):
        value = need_review(current_assumption=None, next_need=None, decision_effect=None, basis_refs=[])
        result = validate_review(response(json.dumps(value)), "C", self.refs)
        self.assertTrue(result["valid"])
        self.assertNotIn("ready", result)
        self.assertNotIn("stop", result)

    def test_no_json_salvage_duplicate_keys_or_nonstandard_constants(self):
        valid = json.dumps(need_review())
        bad_values = [
            "```json\n" + valid + "\n```", "Here is the review: " + valid,
            valid + valid, "[]", "null", valid[:-1],
            valid[:-1] + ', "current_assumption": "duplicate"}',
            valid.replace('"current_assumption": null', '"current_assumption": NaN'),
        ]
        for text in bad_values:
            with self.subTest(text=text):
                result = validate_review(response(text), "C", self.refs)
                self.assertFalse(result["valid"])
                self.assertEqual(result["raw_text"], text)
                self.assertEqual(result["status"], "node_invalid")

    def test_schema_refs_and_paired_null_contract(self):
        variants = [
            need_review(extra="new field"), need_review(current_assumption=3),
            need_review(next_need=" "), need_review(next_need=None),
            need_review(decision_effect=None), need_review(basis_refs="question"),
            need_review(basis_refs=["question", "question"]),
            need_review(basis_refs=["future_event:docid:d2"]), need_review(basis_refs=[1]),
        ]
        missing = need_review()
        del missing["current_assumption"]
        variants.append(missing)
        for value in variants:
            with self.subTest(value=value):
                self.assertFalse(validate_review(response(json.dumps(value)), "C", self.refs)["valid"])

    def test_truncated_tool_refusal_empty_and_multiple_choice_reviews_invalid(self):
        valid_text = json.dumps(need_review())
        variants = [response(valid_text, finish="length"), response(valid_text, calls=[tool_call()]),
                    response(valid_text, calls={}),
                    response(valid_text, refusal="cannot do so"), response(" "), response(None),
                    {"choices": []}, {"choices": [response(valid_text)["choices"][0]] * 2}]
        for value in variants:
            with self.subTest(value=value):
                self.assertFalse(validate_review(value, "C", self.refs)["valid"])

    def test_b_remains_plain_text_without_semantic_or_reference_regex_gate(self):
        result = validate_review(response("Progress is uncertain; see question and the first visible source."), "B", self.refs)
        self.assertTrue(result["valid"])
        self.assertIsNone(result["parsed"])
        self.assertFalse(validate_review(response("text", finish="length"), "B", self.refs)["valid"])


class ActorClassificationTests(unittest.TestCase):
    def setUp(self):
        self.request = checkpoint()["request"]

    def test_whole_tool_batch_preserved_without_execution(self):
        calls = [tool_call("a"), tool_call("b", "open", {"window_ref": "visible", "direction": "after"})]
        original = response("A proposed batch", finish="tool_calls", calls=calls)
        actual = classify_actor_response(original, self.request)
        self.assertEqual(actual["response_kind"], "tool_calls")
        self.assertTrue(actual["syntactic_complete"])
        self.assertTrue(actual["protocol_compatible"])
        self.assertEqual(actual["tool_calls"], calls)
        self.assertEqual(actual["raw_response"], original)
        actual["tool_calls"][0]["id"] = "changed"
        actual["raw_response"]["choices"][0]["message"]["content"] = "changed"
        self.assertEqual(original["choices"][0]["message"]["tool_calls"][0]["id"], "a")
        self.assertEqual(original["choices"][0]["message"]["content"], "A proposed batch")

    def test_stop_with_tools_retained_but_marked_legacy_incompatible(self):
        actual = classify_actor_response(response(calls=[tool_call()], finish="stop"), self.request)
        self.assertEqual(actual["response_kind"], "tool_calls")
        self.assertTrue(actual["syntactic_complete"])
        self.assertFalse(actual["protocol_compatible"])
        self.assertIn("tool_calls_with_stop", actual["compatibility_markers"])
        self.assertEqual(len(actual["tool_calls"]), 1)

    def test_final_text_abstention_and_refusal_remain_distinct_from_tool_errors(self):
        for content in ("The person is B.", "The corpus does not establish an answer."):
            actual = classify_actor_response(response(content), self.request)
            self.assertEqual(actual["response_kind"], "final_text")
            self.assertTrue(actual["protocol_compatible"])
        actual = classify_actor_response(response(refusal="I cannot answer this request."), self.request)
        self.assertEqual(actual["response_kind"], "refusal")
        self.assertTrue(actual["protocol_compatible"])

    def test_length_limit_keeps_batch_for_audit_but_not_as_complete_action(self):
        calls = [tool_call()]
        actual = classify_actor_response(response(finish="length", calls=calls), self.request)
        self.assertEqual(actual["response_kind"], "protocol_error")
        self.assertFalse(actual["syntactic_complete"])
        self.assertFalse(actual["protocol_compatible"])
        self.assertEqual(actual["tool_calls"], calls)

    def test_duplicate_ids_invalid_json_and_missing_object_arguments(self):
        malformed = tool_call()
        malformed["function"]["arguments"] = '{"query":'
        not_object = tool_call(arguments=["query"])
        duplicate_argument = tool_call()
        duplicate_argument["function"]["arguments"] = '{"query":"x", "query":"y"}'
        batches = [[tool_call("same"), tool_call("same")], [malformed], [not_object], [duplicate_argument]]
        for calls in batches:
            with self.subTest(calls=calls):
                actual = classify_actor_response(response(finish="tool_calls", calls=calls), self.request)
                self.assertFalse(actual["protocol_compatible"])
                self.assertEqual(actual["response_kind"], "protocol_error")
                self.assertEqual(actual["tool_calls"], calls)

    def test_registered_schema_catches_wrong_tool_missing_keys_bounds_and_enum(self):
        invalid = [tool_call(name="get_document"), tool_call(arguments={}),
                   tool_call(arguments={"query": "x", "k": True}),
                   tool_call(arguments={"query": "x", "k": 11}),
                   tool_call(arguments={"query": "x", "invented": "y"}),
                   tool_call(name="open", arguments={"window_ref": "x", "direction": "sideways"})]
        for call in invalid:
            with self.subTest(call=call):
                actual = classify_actor_response(response(finish="tool_calls", calls=[call]), self.request)
                self.assertTrue(actual["syntactic_complete"])
                self.assertFalse(actual["protocol_compatible"])
                self.assertTrue(actual["errors"])

    def test_tool_choice_and_batch_limit_are_not_silently_relaxed(self):
        none = deepcopy(self.request)
        none["tool_choice"] = "none"
        self.assertFalse(classify_actor_response(response(finish="tool_calls", calls=[tool_call()]), none)["protocol_compatible"])
        required = deepcopy(self.request)
        required["tool_choice"] = "required"
        self.assertFalse(classify_actor_response(response("Answer"), required)["protocol_compatible"])
        forced = deepcopy(self.request)
        forced["tool_choice"] = {"type": "function", "function": {"name": "open"}}
        self.assertFalse(classify_actor_response(response(finish="tool_calls", calls=[tool_call()]), forced)["protocol_compatible"])
        large = [tool_call(f"id_{i}") for i in range(9)]
        actual = classify_actor_response(response(finish="tool_calls", calls=large), self.request)
        self.assertFalse(actual["protocol_compatible"])
        self.assertEqual(len(actual["tool_calls"]), 9)

    def test_missing_empty_or_multiple_choices_never_become_answers(self):
        variants = [{}, {"choices": []}, response(None), response("  "),
                    response("partial", finish="length"),
                    {"choices": [response("one")["choices"][0], response("two")["choices"][0]]}]
        for value in variants:
            with self.subTest(value=value):
                actual = classify_actor_response(value, self.request)
                self.assertFalse(actual["protocol_compatible"])
                self.assertEqual(actual["response_kind"], "protocol_error")

    def test_malformed_call_under_forced_function_is_logged_without_crashing(self):
        forced = deepcopy(self.request)
        forced["tool_choice"] = {"type": "function", "function": {"name": "open"}}
        calls = [{"id": "broken", "type": "function", "function": None}]
        actual = classify_actor_response(response(finish="tool_calls", calls=calls), forced)
        self.assertEqual(actual["response_kind"], "protocol_error")
        self.assertEqual(actual["tool_calls"], calls)
        self.assertFalse(actual["protocol_compatible"])


if __name__ == "__main__":
    unittest.main()
