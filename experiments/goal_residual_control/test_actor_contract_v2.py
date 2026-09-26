import unittest

from actor_contract_v2 import validate_actor_output_v2

WORKSPACE = {
    "known_documents": [{"doc_ref": "D1"}],
    "observed_windows": [{"window_ref": "W1"}],
}


class ActorContractV2Tests(unittest.TestCase):
    def assert_valid(self, value):
        self.assertEqual(validate_actor_output_v2(value, WORKSPACE), value)

    def assert_invalid(self, value):
        with self.assertRaises(ValueError):
            validate_actor_output_v2(value, WORKSPACE)

    def test_valid_stop(self):
        self.assert_valid({"decision": "stop", "gap": "", "actions": []})

    def test_valid_search(self):
        self.assert_valid({
            "decision": "act",
            "gap": "identify source",
            "actions": [{"tool": "search", "query": "Oliver Mtukudzi Forbes Africa", "k": 5}],
        })

    def test_valid_find(self):
        self.assert_valid({
            "decision": "act",
            "gap": "locate exact passage",
            "actions": [{"tool": "find", "doc_ref": "D1", "query": "album count"}],
        })

    def test_valid_open(self):
        self.assert_valid({
            "decision": "act",
            "gap": "read adjacent context",
            "actions": [{"tool": "open", "window_ref": "W1", "direction": "around"}],
        })

    def test_valid_two_action_batch(self):
        self.assert_valid({
            "decision": "act",
            "gap": "test two independent retrieval formulations",
            "actions": [
                {"tool": "search", "query": "Oliver Mtukudzi Forbes Africa", "k": 5},
                {"tool": "search", "query": "Oliver Mtukudzi Forbes richest musicians", "k": 5},
            ],
        })

    def test_invalid_type_wrapper(self):
        self.assert_invalid({
            "decision": "act",
            "gap": "g",
            "actions": [{"type": "search", "query": "q", "k": 5}],
        })

    def test_invalid_name_arguments_wrapper(self):
        self.assert_invalid({
            "decision": "act",
            "gap": "g",
            "actions": [{"name": "search", "arguments": {"query": "q", "k": 5}}],
        })

    def test_invalid_missing_query(self):
        self.assert_invalid({
            "decision": "act",
            "gap": "g",
            "actions": [{"tool": "search", "k": 5}],
        })

    def test_invalid_tool(self):
        self.assert_invalid({
            "decision": "act",
            "gap": "g",
            "actions": [{"tool": "browse", "query": "q"}],
        })

    def test_invalid_dependent_batch(self):
        self.assert_invalid({
            "decision": "act",
            "gap": "g",
            "actions": [
                {"tool": "search", "query": "new document", "k": 5},
                {"tool": "find", "doc_ref": "D2", "query": "detail"},
            ],
        })


if __name__ == "__main__":
    unittest.main()
