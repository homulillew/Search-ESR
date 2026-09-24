"""Materialize the V1-preselected V2 bank without selecting on V1 outcomes."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
SELECTION = json.loads((HERE / "V2_SELECTION.json").read_text())
V1_CASES = {c["case_id"]: c for c in json.loads((STUDY / "test_representation/CASES.json").read_text())}
EVENTS = [json.loads(s) for s in (STUDY / "test_representation/events.jsonl").read_text().splitlines()]
OUTCOMES = {e["cell"]: e["items"] for e in EVENTS if e["kind"] == "arm_outcome"}
ERRORS = {e["cell"]: e["error_type"] for e in EVENTS if e["kind"] == "arm_error"}
SELECTED = json.loads((STUDY / "test_representation/results.json").read_text())["summary"]["selected_TestCard_arm"]

EXPECTED_SOURCE_TYPE = {
    "1034": "biography or contemporary profile documenting university study and child birthplace",
    "517": "2005 film cast/character credit and director biography",
    "580": "season-one episode guide or synopsis with the reconciliation scene",
    "546": "dated round-by-round 2023 snooker tournament results and opponent career record",
    "387": "game intro/end animation credits and animator interview about paper method",
    "435": "specified May Forbes Africa feature plus dated first-album discography",
    "177": "league final standings table with season, points tie, position and goal difference",
    "1094": "club histories for the two sides of the 95th-minute free-kick fixture",
}


def materialize():
    assert SELECTED in ("C1", "C2")
    assert len(SELECTION["case_ids"]) == 16
    assert len({V1_CASES[c]["qid"] for c in SELECTION["case_ids"]}) == 8
    result = []
    for cid in SELECTION["case_ids"]:
        c = V1_CASES[cid]
        c0 = cid + ":C0"
        test = cid + ":" + SELECTED
        assert c0 in OUTCOMES or c0 in ERRORS
        assert test in OUTCOMES or test in ERRORS
        result.append({
            "case_id": cid, "qid": c["qid"], "checkpoint": c["checkpoint"],
            "raw_question": c["raw_question"], "question_anchors": c["question_anchors"],
            "visible_evidence": c["visible_evidence"],
            "working_hypothesis": c["working_hypothesis"], "semantic_gap": c["semantic_gap"],
            "expected_source_type": EXPECTED_SOURCE_TYPE[c["qid"]],
            "concrete_claim_state": OUTCOMES.get(c0, []), "claim_state_error": ERRORS.get(c0),
            "test_card_state": OUTCOMES.get(test, []), "test_state_error": ERRORS.get(test),
        })
    output = HERE / "V2_CASES.json"
    if output.exists():
        raise FileExistsError(output)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    materialize()
