"""Build G2v2 requests by changing only the Actor system prompt contract.

The old 120 G2 requests are the source of truth. User content, case/arm order,
model settings, and the already-produced G1 residuals are copied byte-for-byte.
No Goal Reviewer or Actor call is made here.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import TOP, digest, read, write


def build():
    old_path = TOP / "research_decision/REQUESTS.json"
    new_dir = TOP / "research_decision_v2"
    new_dir.mkdir(parents=True, exist_ok=True)
    old = read(old_path)
    if len(old) != 120:
        raise AssertionError("expected the frozen 120 G2 requests")

    prompt = (TOP / "prompts/research_actor_contract_v2.md").read_text()
    items = []
    for before in old:
        after = copy.deepcopy(before)
        messages = after["request"]["messages"]
        if len(messages) != 2 or messages[0].get("role") != "system" or messages[1].get("role") != "user":
            raise AssertionError("unexpected frozen request shape")
        messages[0]["content"] = prompt
        after["request_sha256"] = digest(after["request"])

        if before["case_id"] != after["case_id"] or before["qid"] != after["qid"]:
            raise AssertionError("case identity changed")
        if before["arm"] != after["arm"] or before["kind"] != after["kind"]:
            raise AssertionError("arm metadata changed")
        if before["request"]["model"] != after["request"]["model"]:
            raise AssertionError("model changed")
        if before["request"].get("stream") != after["request"].get("stream"):
            raise AssertionError("stream setting changed")
        if before["request"]["messages"][1] != after["request"]["messages"][1]:
            raise AssertionError("Actor user content changed")
        items.append(after)

    write(new_dir / "REQUESTS.json", items)
    print("built", len(items), "G2v2 requests; user payloads unchanged")


if __name__ == "__main__":
    build()
