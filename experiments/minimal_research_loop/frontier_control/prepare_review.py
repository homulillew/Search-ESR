"""Create post-call, answer-blind F1 one-action review packets."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = {x["case_id"]: x for x in json.loads((HERE / "BANK.json").read_text())}
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())


def main():
    target = HERE / "REVIEW_PACKETS.json"
    if target.exists():
        raise FileExistsError(target)
    packets = []
    for case in BANK.values():
        for arm in ("A0", "A1"):
            cell = case["case_id"] + ":" + arm
            outcome = OUTCOMES[cell]
            packets.append({"cell": cell, "qid": case["qid"],
                            "Question": case["raw_question"],
                            "Claims": case["committed_claims"],
                            "open_gaps": case["open_gaps"],
                            "initial_workspace": case["workspace"],
                            "selected_gap": outcome["selected_gap"],
                            "action": outcome["action"],
                            "tool_result": outcome["result"],
                            "observations": outcome["observations"],
                            "error": outcome["error"]})
    assert len(packets) == 48
    target.write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    print("review packets", len(packets))


if __name__ == "__main__":
    main()
