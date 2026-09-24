"""Human-readable action/W digest for the answer-blind reviewer."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = {x["case_id"]: x for x in json.loads((HERE / "BANK.json").read_text())}
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())

lines = ["# F1 action and returned-window digest", "", "This convenience view omits gold answers and future trajectory. Full W text remains in `REVIEW_PACKETS.json`.", ""]
for case in BANK.values():
    lines += [f"## {case['case_id']} — qid {case['qid']}", "",
              "Initial source: " + case["workspace"]["known_documents"][0]["title"],
              "Claims: " + " | ".join(x["statement"] for x in case["committed_claims"]),
              "Open Gaps: " + " | ".join(x["gap_id"] + " " + x["question"] for x in case["open_gaps"]), ""]
    for arm in ("A0", "A1"):
        value = OUTCOMES[case["case_id"] + ":" + arm]
        lines += [f"### {arm} — selected {value['selected_gap']}", "",
                  "Action: " + json.dumps(value["action"], ensure_ascii=False),
                  "Error: " + str(value["error"]), ""]
        for w in value["observations"]:
            lines += [f"- {w['window_ref']} {w['doc_ref']} {w.get('title', '')}",
                      "  " + w["text"][:1000].replace("\n", " "), ""]
(HERE / "REVIEW_DIGEST.md").write_text("\n".join(lines) + "\n")
print("digest lines", len(lines))
