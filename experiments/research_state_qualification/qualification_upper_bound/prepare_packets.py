"""Build R1 review packets from already frozen, prefix-only historical material."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.research_state_plan_handoff.plan_handoff_one_step.run import CASES, h0_request, plan

HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/model_backend_atria/PREFIX_ONLY_PACKETS.json"


def main():
    historical = {(x["qid"], x["seq"]): x for x in json.loads(SOURCE.read_text())["packets"]}
    selection = {"selection_rule": "all frozen DeepSeek P1 cases in historical order",
                 "cells": [{"qid": q, "seq": seq} for q, seq in CASES]}
    packets = []
    for q, seq in CASES:
        item = historical[(q, seq)]
        request = h0_request(q, seq)
        if request["messages"] != item["messages"]:
            raise ValueError(f"Historical prefix mismatch at {q}:{seq}")
        packets.append({"qid": q, "seq": seq, "original_question": item["question"],
                        "prefix_messages": item["messages"], "broad_plan": plan(q, seq),
                        "observed_documents": item["observed_documents"],
                        "last_visible_reasoning": item["last_visible_reasoning"]})
    (HERE / "SELECTION.json").write_text(json.dumps(selection, ensure_ascii=False, indent=2) + "\n")
    (HERE / "review_packets.json").write_text(json.dumps(packets, ensure_ascii=False, indent=2) + "\n")
    print(len(packets), "prefix-only packets")


if __name__ == "__main__":
    main()
