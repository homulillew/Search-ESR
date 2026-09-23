"""Materialize S0 cards from frozen R1 one-step calls and current prefixes."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R1 = ROOT / "experiments/research_state_qualification/qualification_upper_bound"


def main():
    labels = {(x["qid"], x["seq"]): x for x in json.loads((R1 / "ANNOTATIONS.json").read_text())["rows"]}
    packets = {(x["qid"], x["seq"]): x for x in json.loads((R1 / "review_packets.json").read_text())}
    rows = json.loads((R1 / "mechanical_summary.json").read_text())["rows"]
    cards = []
    for row in rows:
        q, seq = row["qid"], row["seq"]
        label, packet = labels[(q, seq)], packets[(q, seq)]
        for index, call in enumerate(row["calls"], 1):
            cards.append({"cell": f"{q}:{seq}", "arm": row["arm"], "call_index": index,
                          "original_question": packet["original_question"],
                          "prefix_packet": f"{q}:{seq}", "current_need": label["current_need"],
                          "candidate_target": label["candidate_target"],
                          "status": label["status"],
                          "supported_part": label["supported_part"],
                          "missing_prerequisite": label["missing_prerequisite"],
                          "visible_support_refs": label["visible_support_refs"],
                          "tool_name": call["name"], "arguments": call["arguments"],
                          "inspected_doc_ref": call["doc_ref"],
                          "review_boundary": "Only R1 review packet, annotation, name and arguments; no tool result or future."})
    (HERE / "review_cards.json").write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n")
    print(len(cards), "S0 calls")


if __name__ == "__main__":
    main()
